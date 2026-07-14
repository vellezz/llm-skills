---
description: Generate architecture docs — ADR, C4 overview, or Mermaid diagrams
argument-hint: '[adr <decision> | c4 | deps | sequence <flow> — default: ask]'
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `architecture-docs` and follow its procedure and output contract
exactly. Do not document from this summary alone.

Key contract: Deliverables are files under docs/architecture/ or docs/adr/NNNN-title.md. Final chat message is 1–3 sentences, with no document pasted into chat.

Scope: $ARGUMENTS (if empty, use the skill's default
scope — ask first when the workspace contains more than ~20 projects).