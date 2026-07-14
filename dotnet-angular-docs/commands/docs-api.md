---
description: Generate REST API documentation from ASP.NET controllers / minimal APIs
argument-hint: '[feature, controller, or path — default: whole API surface]'
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `api-docs` and follow its procedure and output contract
exactly. Do not document from this summary alone.

Key contract: Write files to docs/api/ (one per feature group + index.md); every endpoint section header is exactly `### METHOD /route`; wrap generated sections in <!-- docgen:begin:endpoints --> / <!-- docgen:end:endpoints --> markers. Never invent endpoints — verify each in code.

Scope: $ARGUMENTS (if empty, use the skill's default
scope — ask first when the workspace contains more than ~20 projects).