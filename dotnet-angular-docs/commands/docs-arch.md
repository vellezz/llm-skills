---
description: Generate architecture docs — ADR, C4 overview, or Mermaid diagrams
argument-hint: "[adr <decision> | c4 | deps | sequence <flow> — default: ask]"
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `architecture-docs` and
follow its decision table, procedure, Mermaid conventions, and templates
exactly.

Key contract: deliverables are files under `docs/architecture/` or
`docs/adr/NNNN-title.md`. Final chat message: 1–3 sentences, no document
pasted into chat.

Requested: $ARGUMENTS (if empty or ambiguous, ask one short question to pick
the document type instead of guessing).
