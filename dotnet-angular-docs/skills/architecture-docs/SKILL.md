---
name: architecture-docs
description: >-
  Generate architecture documentation for .NET and Angular projects:
  ADRs (Architecture Decision Records), C4 diagrams (context, container,
  component), dependency and sequence diagrams in Mermaid, and high-level
  architecture overviews. Use whenever the user asks about documenting
  architecture, system design, project structure, dependencies between
  modules/services, data flow, or mentions "ADR", "C4", "diagram",
  "architektura", "przepływ danych" — even without the word "documentation".
---

# Architecture Documentation Generator

## Choosing the document type

| User intent | Produce |
|---|---|
| Record a decision ("why did/should we choose X") | ADR → `templates/adr.md` |
| Explain the system to newcomers/stakeholders | C4 overview → `templates/c4-overview.md` |
| Show how modules/services relate | Mermaid dependency diagram |
| Explain a runtime flow ("how does login work") | Mermaid sequence diagram |

If ambiguous, ask one short question instead of guessing.

## Procedure

1. **Map the solution.** .NET: parse `.sln` + `ProjectReference` entries in
   `.csproj` files → project dependency graph. Angular: `angular.json`
   projects, plus feature boundaries (routes in `app.routes.ts`/routing
   modules, Nx project graph if `nx.json` exists).
2. **Identify external dependencies:** databases (connection strings, EF Core
   `DbContext`), message brokers, caches, third-party APIs (HttpClient
   registrations, `AddHttpClient` named clients), identity providers.
3. **Read `references/mermaid-conventions.md`** before drawing any diagram
   and follow it exactly — consistent diagrams matter more than clever ones.
4. **Write the document from the matching template.** Every architectural
   claim must trace to something you found in code or config; mark
   assumptions explicitly.

## Multi-repo workspaces

- Best run from a workspace parent containing all the system's repositories
  side by side (or with extra repos added as additional working directories);
  map each repo as its own container group in C4 L2.
- Accept a `repos:` argument listing sibling repo paths.
- System parts whose repository is NOT in the workspace must appear as
  external containers marked `⚠ not in workspace` — never invent their
  internals, endpoints, or dependencies.

## Rules

- C4: go top-down. Never produce a Component diagram without at least a brief
  Container context above it.
- Keep diagrams under ~15 nodes. If bigger, split by bounded context and link.
- ADRs are immutable once accepted — for changed decisions, write a new ADR
  that supersedes the old one (link both ways).
- Output paths: `docs/architecture/` for overviews and diagrams,
  `docs/adr/NNNN-title.md` for ADRs (zero-padded sequence, find the next number).
- Deliverables are the files. Final chat message: 1–3 sentences on what was
  written — never paste the document into chat.
- **Language:** honor an explicit language request in the arguments
  (`lang:pl`, "po polsku", …). Localize prose and Mermaid node labels;
  node IDs stay short ASCII, technology names stay as-is.
