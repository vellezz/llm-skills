---
description: Document the EF Core data model — entities, relations, ER diagram, migrations
argument-hint: "[DbContext name or bounded context — default: all DbContexts]"
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `db-schema-docs` and
follow its procedure and template exactly.

Key contract: precedence Fluent API > annotations > conventions
(convention-only facts marked `⚠ Convention`); deliverable is
`docs/architecture/data-model.md` with a Mermaid `erDiagram`. Final chat
message: 1–3 sentences (entity count, files written).

Scope: $ARGUMENTS (if empty, document every `DbContext` found; split by
bounded context when the model exceeds ~15 entities).
