---
description: Generate the complete documentation set via parallel docs-writer subagents
argument-hint: "[scope, repos:..., lang:xx — default: whole workspace]"
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `docs-suite` and follow
its procedure exactly.

Key contract (also stated in the skill): inventory the workspace, then fan out
parallel `docs-writer` subagents (~4 at a time) — one per service/area, each
told to load exactly one skill and given exact scope + output paths + language.
Keep the architecture overview and the final `docs/index.md` synthesis at the
orchestrator level. Deliverables are files; final chat message is a short
report (3–6 sentences).

Scope: $ARGUMENTS (default: the whole workspace; honors `repos:` for sibling
repositories and `lang:` for output language).
