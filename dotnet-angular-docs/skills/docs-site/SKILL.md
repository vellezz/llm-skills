---
name: docs-site
description: >-
  Publish the generated documentation as a GitHub Pages site (MkDocs
  Material + Mermaid), either by building and pushing locally or by
  scaffolding a manually-triggered release workflow. Use whenever the user
  asks to publish docs, set up GitHub Pages, build a docs site, or mentions
  "pages", "docs site", "opublikuj dokumentację", "strona z dokumentacją",
  "mkdocs".
---

# Documentation Site Publisher

Turn the `docs/` tree produced by the other skills into a browsable site.
Two modes — pick from the arguments (`local` | `workflow`); if unspecified,
ask one short question.

## Procedure

1. **Inventory `docs/`.** The nav must mirror files that actually exist.
   If `docs/` is empty, stop and tell the user to generate docs first
   (`api-docs`, `docs-suite`); do not scaffold a site over nothing.
2. **Render `templates/mkdocs.yml`** following `references/mkdocs-config.md`:
   site name from the repository, `nav` built from the real `docs/` tree
   (inside `# docgen:begin:nav` / `# docgen:end:nav` markers), Mermaid via
   superfences, theme language per the language rule.
3. **Mode `local` — build and publish now:**
   - no version requested → `mkdocs gh-deploy --force` (builds and pushes
     the `gh-pages` branch in one step);
   - a release tag given (e.g. `v1.3.0`) → `mike deploy --push
     --update-aliases <major.minor> latest` (versioned site with a switcher).
   - Pushing `gh-pages` publishes content — if the user has not already
     asked to publish in this conversation, confirm before the push.
4. **Mode `workflow` — scaffold manual release publishing:** write
   `templates/docs-release.yml` to `.github/workflows/docs-release.yml`.
   It is triggered manually (`workflow_dispatch`) with a required `tag`
   input: checks out the repo, takes `docs/` content **as of that tag**,
   and publishes it with `mike` as version `major.minor` + alias `latest`.
5. **Finish.** Remind about the one-time setting: repository Settings →
   Pages → source **Deploy from a branch** → branch `gh-pages` (both modes
   publish via that branch). Offer the equivalent
   `gh api repos/{owner}/{repo}/pages` command instead of clicking.

## Rules

- The nav mirrors `docs/` — never invent entries; regenerate only inside the
  docgen markers and preserve manual edits outside them.
- `drift-report.md` stays OUT of the nav by default — it is a QA artifact,
  not reader content. Include it only on explicit request or when
  `docs/.docgen/config.yml` sets `docs-site.include-drift-report: true`;
  `docs-site.site-name` overrides the derived site name.
- `docs/index.md` is the homepage; if missing, create a minimal one linking
  the top-level sections (grounded in existing files only).
- Deliverables: `mkdocs.yml` (+ workflow file in `workflow` mode). Final chat
  message: 1–3 sentences — what was written/published and the site URL
  (`https://<owner>.github.io/<repo>/`).
- Versioning maps a git tag `vX.Y.Z` to docs version `X.Y`; patch releases
  overwrite their `X.Y`. No tags in the repo → no versioning, plain deploy.
