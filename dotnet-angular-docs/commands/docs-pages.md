---
description: Publish generated docs as a GitHub Pages site (MkDocs Material + Mermaid)
argument-hint: "[local | workflow] [vX.Y.Z] [lang:xx] — default: ask which mode"
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `docs-site` and follow
its procedure exactly.

Key contract (also stated in the skill): the nav in `mkdocs.yml` mirrors the
real `docs/` tree (docgen markers, no invented entries, drift-report
excluded). Mode `local` builds and pushes `gh-pages` now (`mkdocs gh-deploy`,
or `mike` when a release tag is given); mode `workflow` scaffolds
`.github/workflows/docs-release.yml` — a manually-triggered publisher for a
specific release tag. Remind about the one-time Pages setting
(branch `gh-pages`).

Arguments: $ARGUMENTS
