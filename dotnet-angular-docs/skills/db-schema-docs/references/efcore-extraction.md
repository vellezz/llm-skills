# EF Core schema extraction rules

## Precedence
Fluent API (`IEntityTypeConfiguration<T>` / `OnModelCreating`) → data
annotations → conventions. Convention-only facts are marked `⚠ Convention`.

## Tables & columns
- Table: `ToTable("Name", "schema")` | `[Table]` | `DbSet` property name (convention).
- Column type: `HasColumnType`, else the provider default for the CLR type —
  name the provider (SQL Server / PostgreSQL / SQLite) so types are concrete.
- Required: `IsRequired()` | `[Required]` | non-nullable CLR type.
- Length: `HasMaxLength` | `[MaxLength]` / `[StringLength]`.
- Defaults: `HasDefaultValue` / `HasDefaultValueSql` (quote the SQL).
- Conversions: `HasConversion` — document the *stored* type, note the CLR type.
- Enums: stored as int by default; string only with a conversion — check.
- Owned types: `OwnsOne` → inlined columns (prefix), `OwnsMany` → own table.

## Keys & indexes
- PK: `HasKey` | `[Key]` | `Id` / `<Entity>Id` convention.
- Alternate keys: `HasAlternateKey`.
- Indexes: `HasIndex` (+ `IsUnique`) | `[Index]` attribute.

## Relationships
| Fluent pattern | Cardinality | erDiagram edge |
|---|---|---|
| `HasOne().WithMany()` | many-to-one | `A }o--|| B` |
| `HasMany().WithOne()` | one-to-many | `A ||--o{ B` |
| `HasOne().WithOne()` | one-to-one | `A ||--|| B` |
| skip navigations / `UsingEntity` | many-to-many | `A }o--o{ B` (name the join table) |

- FK: `HasForeignKey`; nullability of the FK property → optional vs required.
- Delete behavior: `OnDelete(DeleteBehavior.X)`; unspecified → EF default
  (Cascade for required, ClientSetNull for optional) — mark `⚠ Convention`.

## Mermaid erDiagram specifics
- Entity attributes: `type name PK|FK "constraint note"` — keep notes short.
- Label every relationship edge with a verb (`contains`, `places`, `owns`).
- Same quoting rules as other diagrams; no styling.

## Migrations
- `Migrations/` files are timestamp-prefixed — sort chronologically.
- Impact summary from `Up()` method operation names only
  (`CreateTable`, `AddColumn`, `DropColumn`, `AlterColumn`, `CreateIndex`).
- Flag destructive operations (`DropTable`, `DropColumn`) explicitly.
