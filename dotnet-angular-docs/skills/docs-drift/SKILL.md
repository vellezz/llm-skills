---
name: docs-drift
description: >-
  Audit existing documentation against the current .NET and Angular source
  code and report drift: stale endpoints, broken README commands, removed
  routes, renamed DTOs, outdated diagrams. Use whenever the user asks to
  verify docs, check whether documentation is up to date, find stale or
  outdated docs, or mentions "docs drift", "stale docs", "audyt dokumentacji",
  "czy dokumentacja jest aktualna", "zweryfikuj dokumentację".
---

# Documentation Drift Auditor

Verify docs against code — never the other way around. Code is the source of
truth. The deliverable of this skill is ONE FILE: `docs/drift-report.md`.
The audit never edits the documentation it examines.

## Procedure

1. **Create the report file FIRST.** Before auditing anything, copy
   `templates/drift-report.md` to `docs/drift-report.md` (overwrite any
   previous report — it is a snapshot, not history). You will fill it in as
   you go. This is the required first action of every run.
2. **Inventory the docs.** Find what exists: `README.md`, `docs/api/*.md`,
   `docs/architecture/`, `docs/adr/`, `docs/user-guide/`, `CHANGELOG.md`.
   Note which sections carry `<!-- docgen:begin/end -->` markers (safe to
   regenerate later) vs hand-written prose (report only, never touch).
3. **Re-extract the current state from code** using the sibling skills' rules:
   API surface per `api-docs`, commands/versions per `project-readme`,
   routes and labels per `user-manual`, project graph per `architecture-docs`.
4. **Run the checks in `references/drift-checks.md`** for every doc found.
   After checking each doc, write its findings into the report file
   immediately — do not hold findings in your head until the end.
5. **Classify each finding:**

   | Class | Meaning |
   |---|---|
   | STALE | doc says X, code says Y |
   | ORPHANED | documented, but no longer exists in code |
   | MISSING | exists in code, but is undocumented |
   | UNVERIFIED | doc claim that cannot be traced to code at all |

6. **Finish the file.** Fill in the Summary table counts (integers) and the
   verdict (`✅ Docs in sync` when nothing drifted / `⚠ Drift detected`).
7. **Fix only on request.** If the user asks to fix findings, regenerate only
   sections inside docgen markers by following the matching skill; list
   everything outside markers as manual follow-ups.

## Output contract (strict)

- A run that ends without `docs/drift-report.md` on disk is a FAILED run,
  even if findings were reported in chat. "Report only" means "do not edit
  the audited docs" — it never means "do not write the report file".
- Final chat message: at most 3 sentences — verdict, counts per class, and
  the report path. The findings live in the file, not in chat.

## Rules

- Every finding needs evidence on both sides: doc file + location, and
  code file + symbol/line.
- **Repo configuration:** read `docs/.docgen/config.yml` if present — routes
  in `api-docs.exclude-routes` are intentionally undocumented: never flag
  them as MISSING. Custom documents carry a `> Spec:` header — re-audit them
  against the sources their spec names.
- **Multi-repo:** cross-repo contract checks ("Consumed by" lines, Angular
  client drift) require the counterpart repository in the workspace (or via
  `repos:…`). When it is absent, record those checks as UNVERIFIED with the
  reason — never silently skip them and never fail them.
- Drift is factual disagreement only — never flag style, wording, or tone.
- Keep the Summary table labels exactly as in the template
  (STALE / ORPHANED / MISSING / UNVERIFIED) — tools parse them.
- **Language:** finding narratives may follow an explicit language request
  (`lang:pl`, …), but the Summary labels above, the verdict markers
  (`✅` / `⚠ Drift detected`), and quoted evidence stay untouched — they are
  a parsing contract.
