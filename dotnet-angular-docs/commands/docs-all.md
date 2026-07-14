---
description: Generate the complete documentation set via parallel docs-writer subagents
argument-hint: '[scope, repos:..., lang:xx — default: whole workspace]'
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `docs-suite` and follow its procedure and output contract
exactly. Do not document from this summary alone.

Key contract: Inventory the workspace, then fan out parallel docs-writer subagents (~4 at a time), one per service/area, each loading exactly one skill with an exact scope, output paths, and language. The architecture overview and final docs/index.md synthesis stay at the orchestrator level; final chat message is a short report (3–6 sentences).

Scope: $ARGUMENTS (if empty, use the skill's default
scope — ask first when the workspace contains more than ~20 projects).