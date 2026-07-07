#!/usr/bin/env python3
"""Behavioral test harness for the dotnet-angular-docs plugin.

Runs the plugin's skills headlessly (claude -p) against application sources
and applies deterministic assertions to the generated docs. Ground truth is
computed at runtime by extract.py, so any real app can be the test subject.

Usage:
  python tests/run.py --target C:/path/to/app      # test against real sources
  python tests/run.py --target ./app --only drift  # single test
  python tests/run.py --target ./app --scope "src/MyService"  # limit skill scope
  python tests/run.py                              # built-in fixture (smoke)
  python tests/run.py --setup-only                 # materialize only, no LLM
  python tests/run.py --selftest                   # parsers + extractor, free
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asserts  # noqa: E402
import extract  # noqa: E402

ROOT = Path(__file__).resolve().parent            # tests/
PROJECT = ROOT.parent                             # docs_plugin/
PLUGIN = PROJECT / "dotnet-angular-docs"
FIXTURE = ROOT / "fixture"
WORK = ROOT / ".work"

CLAUDE = shutil.which("claude") or "claude"
GIT = shutil.which("git") or "git"

# Read-only shell verbs the skills lean on for exploration, plus git for
# baseline commits. Denying these just makes skills waste turns on large repos.
ALLOWED_TOOLS = (
    "Skill,Task,Agent,Read,Glob,Grep,Write,Edit,"
    "Bash(git:*),Bash(grep:*),Bash(cat:*),Bash(ls:*),Bash(wc:*),"
    "Bash(head:*),Bash(tail:*),Bash(find:*),Bash(rg:*)"
)

SENTINEL = "MANUAL-SENTINEL-7F3A — ręczna notatka zespołu, nie usuwać."

PHANTOM_SECTION = """

### GET /api/phantom-widgets

Returns phantom widgets. This endpoint exists only in the documentation —
it was planted by the drift test harness and has no counterpart in code.

**Responses**

| Status | Body | When |
|---|---|---|
| 200 | `PhantomWidgetDto[]` | always |
"""


def sh(args: list[str], cwd: Path, timeout: int | None = None,
       env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, cwd=str(cwd), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout, env=env,
    )


def claude_env() -> dict[str, str]:
    """Env for the headless claude subprocess. Strips session markers so the
    harness also works when launched from inside a Claude Code session
    (the nested-session guard checks CLAUDECODE)."""
    env = dict(os.environ)
    env.pop("CLAUDECODE", None)
    env.pop("CLAUDE_CODE_ENTRYPOINT", None)
    return env


def git(workdir: Path, *args: str) -> None:
    r = sh([GIT, "-c", "user.email=fixture@test.local", "-c", "user.name=harness", *args], workdir)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{r.stderr}")


def rmtree_force(path: Path) -> None:
    """rmtree that clears the read-only bit git sets on .git/objects (Windows)."""
    def _retry(func, p, _exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_retry)
    else:
        shutil.rmtree(path, onerror=_retry)


class Config:
    """Resolved run configuration (target vs fixture)."""

    def __init__(self, targets: list[Path] | None, scope: str, timeout: int,
                 completeness: str = "auto", model: str = ""):
        self.targets = list(targets or [])
        self.scope = scope
        self.timeout = timeout
        self.model = model
        self.mode = "target" if self.targets else "fixture"
        # auto: completeness on, unless a scope hint restricts generation
        self.check_completeness = (
            completeness == "on" or (completeness == "auto" and not scope)
        )

    @property
    def source_roots(self) -> list[Path]:
        return self.targets or [FIXTURE]


COPY_IGNORE = shutil.ignore_patterns(
    # 'nul'/'aux'/'con': reserved Windows device names — uncopyable junk.
    # '.claude': the app's own agent config (CLAUDE.md etc.) would be
    # loaded by the headless runs and could steer skill behavior — tests
    # must measure the plugin, not the target app's prompts.
    *extract.EXCLUDED_DIRS, "nul", "aux", "con", ".claude",
)


def setup_workdir(cfg: Config, name: str) -> Path:
    """Copy the sources (never touching the originals) into an isolated
    workdir with a fresh git history. Multiple targets are laid out
    side by side (workspace-parent), each with its own git history."""
    dst = WORK / f"{cfg.mode}-{name}"
    if dst.exists():
        rmtree_force(dst)
    roots = cfg.source_roots
    if len(roots) == 1:
        shutil.copytree(roots[0], dst, ignore=COPY_IGNORE)
        repos = [dst]
    else:
        dst.mkdir(parents=True)
        repos = []
        for root in roots:
            repo_dst = dst / root.name
            shutil.copytree(root, repo_dst, ignore=COPY_IGNORE)
            repos.append(repo_dst)
    for repo in repos:
        # Clean-room the docs tree: real apps ship their own docs/ which would
        # confound the audit and pollute the endpoint parse. Tests assert only
        # on docs the plugin generates in this run.
        existing_docs = repo / "docs"
        if existing_docs.is_dir():
            rmtree_force(existing_docs)
            print(f"  [setup] cleared pre-existing docs/ in {repo.name or 'workdir'}")
        git(repo, "init", "-q")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "chore: import sources for docs testing")
        git(repo, "tag", "v1.0.0")
    print(f"  [setup] sources materialized at {dst} ({len(repos)} repo(s))")
    return dst


def ground_truth(cfg: Config) -> tuple[set, set, str]:
    """(required endpoints, optional endpoints, concatenated sources)."""
    sources = "\n".join(extract.sources_blob(r) for r in cfg.source_roots)
    if cfg.mode == "fixture":
        exp = asserts.load_expected(ROOT / "expected.json")
        required = {
            (e["method"], asserts.norm_route(e["route"]))
            for e in exp["endpoints"] if not e.get("optional")
        }
        optional = {
            (e["method"], asserts.norm_route(e["route"]))
            for e in exp["endpoints"] if e.get("optional")
        }
        return required, optional, sources
    extracted: set[tuple[str, str]] = set()
    for root in cfg.source_roots:
        extracted |= {
            (m, asserts.norm_route(r)) for m, r in extract.extract_endpoints(root)
        }
    if not extracted:
        raise RuntimeError(f"extractor found no endpoints under {cfg.source_roots}")
    print(f"  [extract] ground truth: {len(extracted)} endpoints")
    return extracted, set(), sources


def run_claude(cfg: Config, prompt: str, workdir: Path, log_name: str) -> str:
    """Invoke a plugin skill headlessly inside the workdir. Returns the FULL
    assistant transcript (every text block across all turns), so detection
    checks don't depend on how the model structures its final message — a
    skill that writes a long report across turns then ends with a terse
    summary would lose that content under --output-format json's `result`.
    """
    cmd = [
        CLAUDE, "-p", prompt,
        "--plugin-dir", str(PLUGIN),
        "--allowedTools", ALLOWED_TOOLS,
        "--output-format", "stream-json", "--verbose",
    ]
    if cfg.model:
        cmd += ["--model", cfg.model]
    print(f"  [claude] {prompt}")
    r = sh(cmd, workdir, timeout=cfg.timeout, env=claude_env())
    log = WORK / f"{cfg.mode}-{log_name}.log"
    log.write_text(
        f"$ {' '.join(cmd)}\n\n--- stdout ---\n{r.stdout}\n--- stderr ---\n{r.stderr}\n",
        encoding="utf-8",
    )
    if r.returncode != 0:
        raise RuntimeError(f"claude exited {r.returncode}; see {log}")

    texts: list[str] = []
    is_error = False
    saw_result = False
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        etype = ev.get("type")
        if etype == "assistant":
            for block in ev.get("message", {}).get("content", []):
                if block.get("type") == "text" and block.get("text"):
                    texts.append(block["text"])
        elif etype == "result":
            saw_result = True
            is_error = bool(ev.get("is_error"))
            if ev.get("result"):
                texts.append(ev["result"])
    if saw_result and is_error:
        raise RuntimeError(f"claude reported an error; see {log}")
    return "\n".join(texts)


def api_prompt(cfg: Config) -> str:
    # invoke the SKILL directly (not the docs-api wrapper command): this
    # guarantees SKILL.md lands in context — weaker models skip the wrapper's
    # "use the X skill" indirection and improvise from the summary otherwise
    return f"/dotnet-angular-docs:api-docs {cfg.scope}".strip()


# --- docs-side drift planting (generic: works on any app's generated docs) ----


def plant_docs_drift(workdir: Path) -> dict[str, str]:
    """Plant one drift finding of each class by mutating the generated DOCS
    (code stays untouched, so the mutations are app-agnostic):
      STALE    — a documented status code contradicts the code
      ORPHANED — a documented endpoint has no counterpart in code
      MISSING  — an endpoint in code loses its documentation
    Returns {class: text the report must mention}.
    """
    files = [
        p for d in asserts.docs_api_dirs(workdir) for p in sorted(d.rglob("*.md"))
        if "index" not in p.name.lower()
    ]
    if not files:
        raise RuntimeError("no generated docs to plant drift into")

    target = max(
        files, key=lambda p: len(asserts.ENDPOINT_RE.findall(p.read_text(encoding="utf-8")))
    )
    text = target.read_text(encoding="utf-8")
    matches = list(asserts.ENDPOINT_RE.finditer(text))
    if not matches:
        raise RuntimeError(f"no endpoint routes found in {target.name}")
    hints: dict[str, str] = {}

    # MISSING: undocument a real endpoint by deleting every line that mentions
    # its route (header, route line, TOC alike). Pick the most-specific route
    # (most segments) so the substring match can't clip a shorter sibling.
    def _specificity(m: re.Match) -> int:
        return len(asserts._static_segments(asserts.norm_route(m.group(2))))

    victim = max(matches, key=_specificity)
    route_raw = victim.group(2).split("?")[0].split("#")[0].rstrip("/.,;:")
    removed_norm = asserts.norm_route(route_raw)
    segs = asserts._static_segments(removed_norm)
    hints["MISSING"] = segs[-1] if segs else removed_norm
    lines = text.splitlines(keepends=True)
    kept = [ln for ln in lines if route_raw not in ln]
    text = "".join(kept)
    print(f"  [plant] MISSING: undocumented {victim.group(1)} {route_raw} "
          f"(removed {len(lines) - len(kept)} line(s))")

    # STALE: make a documented fact contradict the code. Real skill output
    # varies from the template (auth/status live in different shapes), so try
    # several patterns, most-detectable first — first hit wins. Auth is
    # preferred: a fake policy name is checkable against Policies(...) in code
    # and quoted verbatim in the report, making the assertion robust.
    stale_strategies = [
        # auth value in a table row: | **Auth** | `Authenticated` | -> PhantomAdmin
        (r"(\|\s*\*\*Auth\*\*\s*\|\s*)([^|\n]+?)(\s*\|)",
         r"\g<1>`PhantomAdmin` role required\g<3>", "phantomadmin", "auth -> PhantomAdmin"),
        # auth blockquote/line (fixture/summary format)
        (r"(?m)^(>?\s*\*\*Auth:?\*\*).*$",
         r"\g<1> Requires the `PhantomAdmin` role", "phantomadmin", "auth -> PhantomAdmin"),
        # backtick-wrapped status in an inline responses cell: `200` -> `418`
        (r"`(200|201)`", "`418`", "418", "status -> 418"),
        # bare status cell in a responses table (template format): | 200 | -> | 418 |
        (r"(?m)^(\|\s*)(200|201)(\s*\|)", r"\g<1>418\g<3>", "418", "status -> 418"),
    ]
    for pattern, repl, hint, desc in stale_strategies:
        new_text, n = re.subn(pattern, repl, text, count=1)
        if n:
            text, hints["STALE"] = new_text, hint
            print(f"  [plant] STALE: {desc}")
            break
    else:
        raise RuntimeError(f"could not plant STALE drift in {target.name}")

    # ORPHANED: append a fabricated endpoint section
    text += PHANTOM_SECTION
    hints["ORPHANED"] = "phantom-widgets"
    print("  [plant] ORPHANED: added fake GET /api/phantom-widgets")

    target.write_text(text, encoding="utf-8")
    return hints


# --- tests --------------------------------------------------------------------


def test_api(cfg: Config, llm: bool = True) -> list[str]:
    wd = setup_workdir(cfg, "api")
    if not llm:
        return []
    required, optional, sources = ground_truth(cfg)
    run_claude(cfg, api_prompt(cfg), wd, "api-run1")
    return asserts.assert_api_docs(
        wd, required, optional,
        sources=sources if cfg.mode == "target" else None,
        check_completeness=cfg.check_completeness,
        # extractor is exact on the fixture, best-effort lower bound on real apps
        completeness_severity="fail" if cfg.mode == "fixture" else "warn",
    )


def test_idempotency(cfg: Config, llm: bool = True) -> list[str]:
    wd = setup_workdir(cfg, "idempotency")
    if not llm:
        return []
    run_claude(cfg, api_prompt(cfg), wd, "idem-run1")

    docs = [p for d in asserts.docs_api_dirs(wd) for p in sorted(d.rglob("*.md"))]
    if not docs:
        return ["first run produced no docs/api/*.md — cannot test idempotency"]
    target = next((p for p in docs if "index" not in p.name.lower()), docs[0])
    target.write_text(
        target.read_text(encoding="utf-8") + f"\n## Team notes\n\n{SENTINEL}\n",
        encoding="utf-8",
    )
    print(f"  [inject] sentinel into {target.name}")

    run_claude(cfg, api_prompt(cfg), wd, "idem-run2")
    return asserts.assert_idempotency(wd, SENTINEL)


def test_drift(cfg: Config, llm: bool = True) -> list[str]:
    wd = setup_workdir(cfg, "drift")
    if not llm:
        return []
    # baseline docs generated from the untouched sources
    run_claude(cfg, api_prompt(cfg), wd, "drift-baseline")
    for repo in ([wd] if (wd / ".git").exists() else [d for d in wd.iterdir() if (d / ".git").is_dir()]):
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "--allow-empty", "-m", "docs: baseline API docs")

    hints = plant_docs_drift(wd)

    # the docs-drift SKILL directly — the wrapper command was removed because
    # its identical name shadowed the skill, so SKILL.md never loaded
    report_text = run_claude(cfg, "/dotnet-angular-docs:docs-drift docs/api", wd, "drift-audit")
    return asserts.assert_drift_report(wd, hints, chat_fallback=report_text)


TESTS = {"api": test_api, "idempotency": test_idempotency, "drift": test_drift}


def selftest() -> int:
    errs = asserts.selftest()
    # cross-validate the extractor against the fixture's hand-written truth
    exp = asserts.load_expected(ROOT / "expected.json")
    want = {(e["method"], asserts.norm_route(e["route"])) for e in exp["endpoints"]}
    got = {(m, asserts.norm_route(r)) for m, r in extract.extract_endpoints(FIXTURE)}
    if got != want:
        errs.append(
            f"extractor mismatch on fixture: extra={sorted(got - want)} missing={sorted(want - got)}"
        )
    for e in errs:
        print(f"  FAIL {e}")
    print("selftest:", "PASS" if not errs else "FAIL")
    return 0 if not errs else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", type=Path, action="append",
                    help="path to real application sources; repeat for multi-repo "
                         "(repos are laid out side by side in the workdir)")
    ap.add_argument("--scope", default="", help="scope hint passed to the docs-api command")
    ap.add_argument("--completeness", choices=["auto", "on", "off"], default="auto",
                    help="completeness check: auto = on unless --scope is set")
    ap.add_argument("--model", default="",
                    help="model for headless runs (e.g. sonnet, haiku) — default: account default")
    ap.add_argument("--timeout", type=int, default=1800, help="seconds per skill invocation")
    ap.add_argument("--only", choices=sorted(TESTS), help="run a single test")
    ap.add_argument("--setup-only", action="store_true", help="materialize sources, skip LLM calls")
    ap.add_argument("--selftest", action="store_true", help="validate parsers + extractor, no LLM")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    for t in args.target or []:
        if not t.is_dir():
            print(f"--target does not exist or is not a directory: {t}")
            return 2

    cfg = Config([t.resolve() for t in args.target] if args.target else None,
                 args.scope, args.timeout, args.completeness, args.model)
    WORK.mkdir(exist_ok=True)
    selected = {args.only: TESTS[args.only]} if args.only else TESTS

    results: dict[str, tuple[list[str], list[str]]] = {}
    for name, fn in selected.items():
        print(f"\n=== {name} ({cfg.mode}) ===")
        try:
            findings = fn(cfg, llm=not args.setup_only)
        except Exception as exc:  # noqa: BLE001 — raportujemy i jedziemy dalej
            findings = [f"harness error: {exc}"]
        results[name] = asserts.split_failures(findings)

    print("\n" + "=" * 50)
    failed = False
    for name, (fails, warns) in results.items():
        status = "PASS" if not fails else "FAIL"
        if fails:
            failed = True
        print(f"{status}  {name}" + (f"  ({len(warns)} warning(s))" if warns else ""))
        for e in fails:
            print(f"      - {e}")
        for w in warns:
            print(f"      ~ {w}")
    print(f"\nartifacts kept in {WORK}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
