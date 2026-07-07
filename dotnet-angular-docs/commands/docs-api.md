---
description: Generate REST API documentation from ASP.NET controllers / minimal APIs
argument-hint: "[feature, controller, or path — default: whole API surface]"
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `api-docs` and follow
its procedure and output contract exactly. Do not document from this summary
alone.

Key contract (also stated in the skill): write files to `docs/api/` (one per
feature group + `index.md`); every endpoint section header is exactly
`### METHOD /route`; wrap generated sections in
`<!-- docgen:begin:endpoints -->` / `<!-- docgen:end:endpoints -->` markers.
Never invent endpoints — verify each in code. Final chat message: one short
paragraph, no docs pasted into chat.

Scope: $ARGUMENTS (if empty, document the whole API surface — but ask first
when the workspace contains more than ~20 projects).
