---
description: Document the EF Core data model — entities, relations, ER diagram, migrations
argument-hint: '[DbContext name or bounded context — default: all DbContexts]'
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `db-schema-docs` and follow its procedure and output contract
exactly. Do not document from this summary alone.

Key contract: Precedence is Fluent API > annotations > conventions, with convention-only facts marked ⚠ Convention. Deliverable is docs/architecture/data-model.md with a Mermaid erDiagram; final chat message is 1–3 sentences (entity count, files written).

Scope: $ARGUMENTS (if empty, use the skill's default
scope — ask first when the workspace contains more than ~20 projects).