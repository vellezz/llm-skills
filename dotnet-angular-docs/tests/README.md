# Tests for the dotnet-angular-docs plugin

## Layers

| Layer | Command | Cost | When |
|---|---|---|---|
| Static | `python dotnet-angular-docs/scripts/validate.py` | free | every commit (CI) |
| Official validator | `claude plugin validate ./dotnet-angular-docs` | free | every commit (CI) |
| Parser + extractor selftest | `python dotnet-angular-docs/tests/run.py --selftest` | free | every commit (CI) |
| Behavioral | `python dotnet-angular-docs/tests/run.py --target <app>` | API tokens | on-demand / nightly |

## Behavioral tests — against YOUR sources

You name the target at run time — the harness tests the plugin on a **real
application**, not a synthetic sample:

```bash
python dotnet-angular-docs/tests/run.py --target C:/path/to/app
python dotnet-angular-docs/tests/run.py --target ../app --only drift
python dotnet-angular-docs/tests/run.py --target ../app --scope "src/OrdersService"  # big repo
python dotnet-angular-docs/tests/run.py --target ../app --timeout 2700               # default 1800 s
python dotnet-angular-docs/tests/run.py --target ../backend --target ../frontend     # multi-repo
python dotnet-angular-docs/tests/run.py --target ../app --model sonnet               # another model
```

Multi-repo: each `--target` is a separate repository — copies are laid out
side by side in one workdir (workspace-parent pattern), each with its own git
history; the extractor computes ground truth from the union of all trees, and
assertions look for `docs/api` both at the root and per repo.

Safety: sources are **copied** into `tests/.work/` (without `node_modules`,
`bin`, `obj`, `.git`, `.claude`…) and get a fresh git history — the original
repository is never touched. Pre-existing `docs/` is cleared in the copy for
a clean-room baseline.

### Where ground truth comes from on an arbitrary app

`extract.py` is a deterministic (regex, no AI) API-surface extractor:
attribute-routed controllers (`[Route]` + `[HttpGet]`, `[controller]` token),
minimal APIs (`app.MapGet`, one level of `MapGroup` prefixes), and
**FastEndpoints** (`Get(...)`/`Post(...)` inside `Configure()`, including a
route held in a class const, e.g. `Get(Route)`). The computed set is the
baseline for assertions.

The extractor is a **best-effort lower bound** of the API surface, not a 1:1
oracle. Known limits: no nested `MapGroup` chains, no FastEndpoints `Group<T>`
prefixes, no `[ApiVersion]`, no routes built by concatenation/interpolation.
Hence two tolerance mechanisms:

- **Grounding (hard fail)** — a documented endpoint whose path segments do
  NOT exist anywhere in the sources is a fabrication → FAIL. If the segments
  exist but the extractor could not resolve the exact route → `WARN`.
- **Completeness** — in `fixture` mode (controlled, extractor is exact) an
  undocumented endpoint = FAIL; in `target` mode (arbitrary app) = `WARN`.
  Matching tolerates unresolved prefixes: a documented route "covers" an
  expected one when its segments end with the expected segments
  (`/admin/blog/posts` covers `/blog/posts`).

Real-run example (a large e-commerce app: 76 projects, FastEndpoints): the
extractor found 378 endpoints, the skill documented 374 of them (98%) with
**zero fabrications** — the 4 completeness WARNs were upload/stats endpoints
worth a manual look.

The extractor itself is tested for free: `--selftest` compares its output on
`tests/fixture/` against the hand-written `tests/expected.json`.

### The tests

| Test | Scenario | Assertions |
|---|---|---|
| `api` | `/docs-api` on clean sources | zero invented endpoints; extractor set fully documented (completeness off with `--scope`) |
| `idempotency` | generate → hand-written note → regenerate | sentinel survived; no duplicated sections |
| `drift` | generate → 3 planted mutations **in the docs** → `/docs-drift` | the report detects every planted change (hint-centric) |

Drift mutations act on the generated Markdown (not on C#), so they are
app-agnostic: STALE = auth rewritten to a fake `PhantomAdmin` policy
(fallback: status → 418), ORPHANED = a fabricated `GET /api/phantom-widgets`
section, MISSING = every line mentioning a real endpoint's route removed.
Each mutation carries a **distinctive hint** (`phantomadmin`,
`phantom-widgets`, a route segment) that a correct report must name — that is
the hard detection gate, robust to report formatting.

**Format robustness.** The skill's layout is non-deterministic — sometimes
`### GET /route` headers, sometimes prose titles with the route on its own
line, sometimes `**POST** \`/route\``. The parser (`ENDPOINT_RE`) matches the
method+route pair wherever it appears, tolerating Markdown in between.

**Capture.** The harness uses `--output-format stream-json` and collects the
FULL transcript (every assistant turn), not just the final message — a report
written across intermediate turns and ended with a terse summary would
otherwise be lost.

Artifacts of every run (generated docs, `claude` transcripts) stay in
`tests/.work/` — start with the `*.log` files when something fails.

## Interpreting results

- `PASS … (N warning(s))` — warnings (`~`) describe extractor limits, not
  regressions.
- A single `FAIL` — inspect the artifacts first; LLM output is
  non-deterministic. A repeatable failure of the same assertion after a
  change in `skills/` = a real skill regression.
- Known weak spot: `idempotency` may expose a gap — if it fails because
  hand-written sections were clobbered, fix the skill/template (docgen
  markers), not the test.

## Findings from real-app runs (microservices e-commerce, 76 projects)

- **`docs-api` — strong.** FastEndpoints solution: **0 fabrications**,
  374/378 endpoints (98%) documented; it even caught a real route-prefix bug
  (docs prefixed routes with `/api/`, the code registers them without it).
- **`idempotency` — PASS** on one service: a hand-written note survived
  regeneration.
- **`drift` — PASS.** The auditor detected all planted changes plus the real
  prefix bug.
- **The "report never lands in a file" mystery — SOLVED.** The cause was not
  headless mode but a **name collision**: a `docs-drift` command and the
  `docs-drift` skill both registered as `/plugin:docs-drift`; the command
  shadowed the skill, so SKILL.md never reached the model. After removing the
  wrapper the report file is written exactly per template.
  **Rule:** a command name must never equal a skill name.
  **Diagnostic:** grep the stream-json transcript for unique SKILL.md
  phrases — zero hits = the skill never loaded.

## Optimization for smaller models (Sonnet) — measured

A `drift` run with `--model sonnet` on the same app: PASS **with no
warnings** — report file written, template reproduced 1:1, all plants
detected plus extra real drift. The `api-docs` baseline under Sonnet: 100% of
headers in the strict `### METHOD /route` format, balanced `docgen` markers
in every file. The changes that made it work:

1. **Output contracts in the skills** — explicit file paths, pinned header
   format, markers, capped chat replies, "before finishing" checklists.
2. **File-first** in `docs-drift` — the deliverable exists before the audit.
3. **Wrapper commands force-load the skill** ("REQUIRED FIRST STEP: invoke
   the Skill tool…") and carry the critical contract inline.
4. **The harness invokes skills directly** (`/plugin:api-docs`), and
   `--model sonnet|haiku` measures the plugin on any tier.

## Fixture

`tests/fixture/` (mini .NET 8 + Angular 17 + EF Core) exists to
cross-validate the extractor for free and as a no-`--target` smoke; use real
applications via `--target` to judge skill quality.

## CI

- `dotnet-angular-docs-validate.yml` — free layers, every push/PR touching
  this project.
- `dotnet-angular-docs-behavioral.yml` — nightly + `workflow_dispatch`
  (input `only`), runs on the fixture (CI has no access to private apps).
  Requires the `ANTHROPIC_API_KEY` secret.
