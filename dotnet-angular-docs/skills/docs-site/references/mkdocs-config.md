# MkDocs configuration rules

## Required blocks
- Theme: `material`; set `theme.language` from the resolved output language.
- Mermaid — this exact superfences block, otherwise diagrams render as code:

  ```yaml
  markdown_extensions:
    - admonition
    - tables
    - pymdownx.superfences:
        custom_fences:
          - name: mermaid
            class: mermaid
            format: !!python/name:pymdownx.superfences.fence_code_format
  ```

- Plugins: `search` always. `mike` version provider only when versioning:

  ```yaml
  extra:
    version:
      provider: mike
  ```

## Nav construction
- One nav section per top-level `docs/` subfolder (api, architecture,
  user-guide…), files in alphabetical order, `index.md` first.
- Section titles: humanize folder names ("api" → "API",
  "user-guide" → "User guide"); do not rename files.
- Exclude `drift-report.md` unless explicitly requested.

## Build hygiene
- Local builds run `mkdocs build --strict` first — it fails on broken links,
  which is the point: fix or report link errors before publishing.
- `gh-pages` is a generated branch — never hand-edit it; `mkdocs gh-deploy`
  and `mike` own it.
