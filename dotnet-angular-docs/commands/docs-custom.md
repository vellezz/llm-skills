---
description: Generate project-specific documents from specs in docs/.docgen/custom/
argument-hint: "[spec name(s) — default: all specs in docs/.docgen/custom/]"
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `custom-docs` and follow
its procedure exactly.

Key contract (also stated in the skill): each spec's frontmatter names the
output file; the brief controls content but never overrides grounding —
every fact traces to code/config, secret values are never documented.
Deliverables are files; final chat message 1–3 sentences.

Specs: $ARGUMENTS
