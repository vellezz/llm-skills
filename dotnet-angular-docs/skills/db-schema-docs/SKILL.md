---
name: db-schema-docs
description: >-
  Document the database schema and data model of .NET projects using EF Core:
  entities, relationships, keys, indexes, Mermaid ER diagrams, and migration
  history. Use whenever the user asks to document the database, data model,
  entities, tables, or schema, or mentions "ER diagram", "schemat bazy",
  "model danych", "encje", "migracje", "database schema", "DbContext".
---

# Database Schema Documentation Generator

## Procedure

1. **Locate the model.** `DbContext` subclasses → `DbSet<T>` properties;
   `OnModelCreating` and `IEntityTypeConfiguration<T>` implementations
   (follow `ApplyConfigurationsFromAssembly`); data annotations on entities.
   Note the provider from `UseSqlServer`/`UseNpgsql`/`UseSqlite` registration.
2. **Read `references/efcore-extraction.md`** for how to derive tables,
   columns, keys, relationships, and constraints. Precedence: Fluent API
   wins over annotations, annotations win over conventions.
3. **Extract per entity:** table/schema name, primary key, columns with
   CLR → SQL types, required/nullable, max lengths, defaults, indexes,
   relationships with cardinality and delete behavior, owned types,
   enum storage (string vs int).
4. **Migration history (if a `Migrations/` folder exists):** chronological
   table of migrations with their schema impact — new tables, breaking
   column changes. Read names and key operations only; never reproduce
   migration code.
5. **Render `templates/data-model.md`** with a Mermaid `erDiagram`. Follow
   the general rules in `../architecture-docs/references/mermaid-conventions.md`
   (quoting, no custom colors, size limits).

## Rules

- Never invent columns or relations — verify each in configuration or
  annotations. Facts derived purely from EF conventions are marked
  `⚠ Convention`.
- Diagrams: max ~15 entities. Larger models split by aggregate/bounded
  context into separate files, linked from an index.
- Always document delete behaviors — `Cascade` vs `Restrict` is the kind
  of fact that bites in production.
- Output: `docs/architecture/data-model.md`
  (or `docs/architecture/data/<context>.md` when split).
- Deliverables are the files. Final chat message: 1–3 sentences (entity count,
  files written) — never paste the document into chat.
- **Language:** honor an explicit language request in the arguments
  (`lang:pl`, …). Localize prose and "Notes" columns; entity, table, and
  column names, SQL types, and erDiagram identifiers stay untouched.
