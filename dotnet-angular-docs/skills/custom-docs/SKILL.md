---
name: custom-docs
description: >-
  Generate project-specific documents from free-text specs kept in the
  repository under docs/.docgen/custom/*.md — e.g. a reference of environment
  variables passed to containers, a bespoke Mermaid diagram of one flow, an
  operational runbook. Use when the user asks for a custom/dedicated
  document, mentions "custom docs", "dedykowany dokument", "env variables
  documentation", or when docs/.docgen/custom/ contains specs to render.
---

# Custom Document Generator

Each file in `docs/.docgen/custom/` is a spec: YAML frontmatter (the
contract) plus a free-text brief (what the document must contain).

## Spec format

```markdown
---
output: docs/operations/container-env.md   # required
lang: pl                                    # optional; else the language rule
---
Free-text brief: what to document, which sources are authoritative
(e.g. docker-compose*.yml, AppHost, appsettings*), what structure is
expected (tables, a sequence diagram, ...).
```

## Procedure

1. **Collect specs** — those named in the arguments, or every file in
   `docs/.docgen/custom/` when none are named. No specs → say so and stop.
2. **Per spec:** read the brief, locate the named sources in the repository,
   extract the facts, render the document to the spec's `output` path. Wrap
   generated content in `<!-- docgen:begin:custom -->` /
   `<!-- docgen:end:custom -->` markers.
3. Any diagram follows
   `../architecture-docs/references/mermaid-conventions.md`.
4. Final chat message: 1–3 sentences listing the files written.

## Rules

- The brief controls WHAT the document contains; it can never override HOW
  facts are established — every claim traces to code or config, uncertain →
  `⚠ Unverified`. A brief cannot authorize invention.
- Secrets and credentials: document names and where to obtain them — NEVER
  values, even if the brief asks; note the refusal in the document.
- One spec = one output document. A spec without `output:` → ask, don't guess.
- Put the spec path in the doc header (`> Spec: docs/.docgen/custom/x.md`)
  so a drift audit can re-verify the document against the same sources.
