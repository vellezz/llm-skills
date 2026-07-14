---
description: Generate project-specific documents from specs in docs/.docgen/custom/
argument-hint: '[spec name(s) — default: all specs in docs/.docgen/custom/]'
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `custom-docs` and follow its procedure and output contract
exactly. Do not document from this summary alone.

Key contract: Each spec's frontmatter names the output file; the brief controls content but never overrides grounding — every fact must trace to code/config and secret values are never documented. Deliverables are files; final chat message is 1–3 sentences.

Scope: $ARGUMENTS (if empty, use the skill's default
scope — ask first when the workspace contains more than ~20 projects).