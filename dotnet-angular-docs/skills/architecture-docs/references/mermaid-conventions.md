# Mermaid conventions

## General
- Always use fenced blocks with the `mermaid` language tag (GitHub renders these).
- Direction: `graph TD` for dependency/structure, `sequenceDiagram` for flows,
  `C4Context`/`C4Container` blocks only if the team's renderer supports them —
  otherwise emulate C4 with `graph TD` + subgraphs (safer default).
- Node IDs: short alphanumeric (`api`, `db`, `authSvc`); labels carry the
  human-readable name: `api["Orders API (ASP.NET Core)"]`.
- Quote every label containing spaces, parentheses, or special characters —
  unquoted parentheses are the #1 cause of broken Mermaid on GitHub.

## Dependency diagrams
- Solid arrow `-->` = compile-time reference (ProjectReference, TS import).
- Dashed arrow `-.->` = runtime call (HTTP, message queue). Label it:
  `web -.->|HTTPS/JSON| api`.
- Group by layer or bounded context with `subgraph`.

## Sequence diagrams
- Participants left-to-right in call order: user/browser → Angular → API →
  domain/services → infrastructure (DB, broker).
- Show only the happy path plus at most one significant failure branch (`alt`).
- Use `activate`/`deactivate` sparingly — only when lifetimes matter.

## Styling
- No custom colors or themes — they render inconsistently across GitHub,
  VS Code, and doc portals. Structure over decoration.
