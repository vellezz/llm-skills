"""Deterministic, property-based assertions over LLM-generated docs.

Each assert_* function returns a list of finding strings (empty = pass).
Findings prefixed "WARN:" are informational and do not fail the suite.
No AI involved: pure parsing and comparison.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# A method+route pair anywhere in the doc. The skill's layout is not stable:
# sometimes the header carries it (`### GET /api/orders`, `## **POST** `/x``),
# sometimes a prose title heads the section and the route sits on its own line
# (`POST /payments/intents`) or inside a fence. Matching the pair wherever it
# appears (not only in headers) makes the parser robust to that variance.
ENDPOINT_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b[\s*`:>|)\]-]*(/[^\s`)\]|>]*)")
# alias kept for the idempotency duplication heuristic and the selftest
ENDPOINT_HEADER = ENDPOINT_RE


def norm_route(route: str) -> str:
    """Normalize a route for comparison: drop any query/fragment, lowercase,
    leading slash, any {param} or {param:constraint} -> {}, no trailing slash
    or punctuation."""
    r = route.strip().split("?")[0].split("#")[0]
    r = r.rstrip("/").rstrip(".,;:").lower()
    if not r.startswith("/"):
        r = "/" + r
    return re.sub(r"\{[^}]*\}", "{}", r)


def docs_api_dirs(workdir: Path) -> list[Path]:
    """docs/api directories in the workdir — root-level (single repo) and
    one level down (multi-repo workspace-parent layout)."""
    dirs = [workdir / "docs" / "api"] + sorted(workdir.glob("*/docs/api"))
    return [d for d in dirs if d.is_dir()]


def parse_endpoints(docs_dir: Path) -> dict[tuple[str, str], list[str]]:
    """Scan all *.md under docs_dir; return {(METHOD, norm_route): [files]}."""
    found: dict[tuple[str, str], list[str]] = {}
    for md in sorted(docs_dir.rglob("*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        for m in ENDPOINT_RE.finditer(text):
            key = (m.group(1).upper(), norm_route(m.group(2)))
            found.setdefault(key, []).append(md.name)
    return found


def load_expected(expected_path: Path) -> dict:
    return json.loads(expected_path.read_text(encoding="utf-8"))


def _static_segments(route: str) -> list[str]:
    """Non-parameter path segments of a normalized route, e.g.
    /api/orders/{}/archive -> ['api', 'orders', 'archive']."""
    return [s for s in route.strip("/").split("/") if s and s != "{}"]


def _covers(documented: set[tuple[str, str]], method: str, route: str) -> bool:
    """True if the expected (method, route) is covered by a documented one,
    allowing a documented route to carry an unresolved prefix: its segments
    end with the expected route's segments."""
    if (method, route) in documented:
        return True
    exp_segs = _static_segments(route)
    if not exp_segs:
        return False
    for dm, dr in documented:
        if dm != method:
            continue
        doc_segs = _static_segments(dr)
        if len(doc_segs) >= len(exp_segs) and doc_segs[-len(exp_segs):] == exp_segs:
            return True
    return False


def assert_api_docs(
    workdir: Path,
    expected_endpoints: set[tuple[str, str]],
    optional_endpoints: set[tuple[str, str]] = frozenset(),
    sources: str | None = None,
    check_completeness: bool = True,
    completeness_severity: str = "fail",
) -> list[str]:
    """Grounding + completeness of docs/api against the known API surface.

    expected_endpoints/optional_endpoints hold (METHOD, norm_route) pairs.

    Grounding (always a hard failure): a documented endpoint absent from the
    expected set is INVENTED unless `sources` is given and all its static path
    segments appear there (then WARN — a construct the extractor can't resolve).

    Completeness: an expected endpoint not covered by any documented route.
    Severity is `completeness_severity` ("fail" for the controlled fixture,
    "warn" for arbitrary target apps where the extractor is only a lower bound).
    """
    findings: list[str] = []
    dirs = docs_api_dirs(workdir)
    if not dirs:
        return [f"no docs/api directory was created under {workdir}"]

    documented: dict[tuple[str, str], list[str]] = {}
    for d in dirs:
        for key, files in parse_endpoints(d).items():
            documented.setdefault(key, []).extend(files)
    if not documented:
        return ["docs/api exists but no endpoint headers were parsed from it"]

    exp_all = expected_endpoints | optional_endpoints
    src_lower = sources.lower() if sources else None

    for method, route in sorted(set(documented) - exp_all):
        where = documented[(method, route)]
        segs = _static_segments(route)
        if src_lower and segs and all(seg in src_lower for seg in segs):
            findings.append(
                f"WARN: documented endpoint not in extracted ground truth "
                f"(but its segments exist in sources): {method} {route} (in {where})"
            )
        else:
            findings.append(
                f"INVENTED endpoint documented but absent from sources: "
                f"{method} {route} (in {where})"
            )

    if check_completeness:
        doc_set = set(documented)
        prefix = "WARN: " if completeness_severity == "warn" else ""
        for method, route in sorted(expected_endpoints):
            if not _covers(doc_set, method, route):
                findings.append(
                    f"{prefix}undocumented endpoint present in sources: {method} {route}"
                )

    return findings


def assert_no_dev_speak(workdir: Path) -> list[str]:
    """User manual must contain no code identifiers or HTTP verbs."""
    findings: list[str] = []
    guide_dir = workdir / "docs" / "user-guide"
    if not guide_dir.is_dir():
        return [f"docs/user-guide was not created (looked in {guide_dir})"]
    forbidden = re.compile(
        r"HttpClient|FormGroup|ControllerBase|\b(GET|POST|PUT|DELETE)\s+/|\bclass\s+\w+"
    )
    for md in sorted(guide_dir.rglob("*.md")):
        for i, line in enumerate(md.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if forbidden.search(line):
                findings.append(f"dev-speak in user manual {md.name}:{i}: {line.strip()[:80]}")
    return findings


def assert_idempotency(workdir: Path, sentinel: str) -> list[str]:
    """After a second generation run: manual sentinel preserved, no duplicated sections."""
    findings: list[str] = []
    dirs = docs_api_dirs(workdir)
    if not dirs:
        return ["docs/api missing after second run"]
    all_md = [p for d in dirs for p in sorted(d.rglob("*.md"))]

    all_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in all_md)
    if sentinel not in all_text:
        findings.append(f"hand-written sentinel was clobbered by the second run: {sentinel!r}")

    for md in all_md:
        text = md.read_text(encoding="utf-8", errors="replace")
        counts: dict[tuple[str, str], int] = {}
        for m in ENDPOINT_RE.finditer(text):
            key = (m.group(1).upper(), norm_route(m.group(2)))
            counts[key] = counts.get(key, 0) + 1
        # a route may legitimately appear twice (table of contents + section);
        # 3+ signals the regeneration actually duplicated the endpoint block
        for (method, route), n in counts.items():
            if n > 2:
                findings.append(f"duplicated section in {md.name}: {method} {route} appears {n}x")
    return findings


SUMMARY_ROW = r"\|\s*{label}\s*\|\s*(\d+)\s*\|"


def assert_drift_report(
    workdir: Path, hints: dict[str, str], chat_fallback: str = ""
) -> list[str]:
    """The drift audit must detect every planted change.

    Detection is the substance of the test and is format-agnostic: each planted
    change carries a distinctive `hint` string (a fake policy name, a phantom
    route, a removed endpoint's segment) that a correct report must name.

    The report should be written to docs/drift-report.md. In headless/print
    mode the skill often returns it as chat text instead; we accept that text
    for the detection checks but flag the unwritten file as a WARN.
    """
    findings: list[str] = []
    report_path = workdir / "docs" / "drift-report.md"
    if not report_path.is_file():
        candidates = list(workdir.glob("docs/**/drift*.md")) + list(workdir.glob("*/docs/**/drift*.md"))
        report_path = candidates[0] if candidates else report_path

    if report_path.is_file():
        text = report_path.read_text(encoding="utf-8", errors="replace")
    elif chat_fallback.strip():
        text = chat_fallback
        findings.append(
            "WARN: drift report returned as chat text, not written to "
            "docs/drift-report.md (skill spec says write the file)"
        )
    else:
        return [f"drift report neither written to {report_path} nor returned as text"]

    low = text.lower()
    for cls, hint in hints.items():
        if hint and hint.lower() not in low:
            findings.append(f"{cls} drift not detected — report never mentions {hint!r}")

    drift_language = re.search(r"drift|orphan|missing|mismatch|inaccura|stale|⚠", low)
    if re.search(r"in sync|no drift found|✅ docs", low) and not drift_language:
        findings.append("verdict claims docs are in sync despite planted drift")

    return findings


def split_failures(findings: list[str]) -> tuple[list[str], list[str]]:
    """(hard failures, warnings)."""
    warns = [f for f in findings if f.startswith("WARN:")]
    fails = [f for f in findings if not f.startswith("WARN:")]
    return fails, warns


# --- self-test fixtures (no LLM, validates the parsers themselves) -----------

SELFTEST_API_DOC = """# Orders API
### GET /api/orders
ok
### **POST** `/api/orders`
ok
### DELETE /api/orders/{id:guid}
ok
"""

SELFTEST_DRIFT_DOC = """# Documentation drift report
## Summary
| Class | Count |
|---|---|
| STALE | 1 |
| ORPHANED | 2 |
| MISSING | 1 |
| UNVERIFIED | 0 |
**Verdict:** ⚠ Drift detected
## Findings
### STALE · POST route changed to /api/orders/create
### MISSING · POST /api/orders/{id}/archive is undocumented
"""


def selftest() -> list[str]:
    errors = []
    eps = {
        (m.group(1).upper(), norm_route(m.group(2)))
        for m in ENDPOINT_HEADER.finditer(SELFTEST_API_DOC)
    }
    want = {("GET", "/api/orders"), ("POST", "/api/orders"), ("DELETE", "/api/orders/{}")}
    if eps != want:
        errors.append(f"endpoint parser selftest failed: {eps} != {want}")

    for label, n_want in (("STALE", 1), ("ORPHANED", 2), ("MISSING", 1)):
        m = re.search(SUMMARY_ROW.format(label=label), SELFTEST_DRIFT_DOC)
        if not m or int(m.group(1)) != n_want:
            errors.append(f"summary parser selftest failed for {label}")

    if norm_route("api/Orders/{id:guid}/") != "/api/orders/{}":
        errors.append("norm_route selftest failed")

    if _static_segments("/api/orders/{}/archive") != ["api", "orders", "archive"]:
        errors.append("_static_segments selftest failed")
    return errors
