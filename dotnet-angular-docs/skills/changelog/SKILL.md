---
name: changelog
description: >-
  Generate or update CHANGELOG entries and release notes from git history,
  merged PRs, and code diffs for .NET and Angular projects. Use whenever the
  user asks to summarize changes, prepare release notes, update the changelog,
  describe what changed between versions/tags/branches, or mentions
  "changelog", "release notes", "co się zmieniło", "lista zmian".
---

# Changelog & Release Notes Generator

## Procedure

1. **Determine the range.** Last tag → HEAD by default
   (`git describe --tags --abbrev=0`). Confirm with the user if no tags exist.
2. **Collect:** `git log --oneline <range>`, merged PR titles if available,
   and for user-visible impact, diff the public surface: controller routes,
   DTOs, Angular routes, and `package.json`/`.csproj` dependency bumps.
3. **Classify** each change (Keep a Changelog categories):
   Added / Changed / Deprecated / Removed / Fixed / Security.
   Detect breaking changes explicitly: removed/renamed endpoints, changed
   DTO fields, changed route paths, major dependency bumps — put them in a
   **⚠ Breaking changes** section at the top.
4. **Write for the changelog's audience:** describe the effect
   ("Order search now filters by status"), not the mechanics
   ("refactored OrderQueryHandler"). Skip pure-internal commits (formatting,
   test-only, CI) unless the user wants a full log.
5. **Insert idempotently:** new version section at the top of
   `CHANGELOG.md` under `## [Unreleased]` or as `## [x.y.z] - YYYY-MM-DD`;
   never rewrite prior entries.

## Multi-repo release notes

When the arguments list several repositories (`repos:../backend,../frontend`),
produce ONE platform-level changelog: resolve each repo's range independently
(its own last tag → HEAD), classify per repo, then merge into a single version
section grouped by component (`### backend`, `### frontend`), noting each
component's tag next to its heading. Breaking changes from all components go
into one shared **⚠ Breaking changes** block on top. Write the file in the
repository you were invoked in.

## Rules

- One line per change, sentence case, no trailing period, link PR/issue
  numbers when identifiable from commit messages (`#123`).
- Uncertain classification → put it under Changed and move on.
- Version number: take from the user, or suggest based on semver
  (breaking → major, Added → minor, only Fixed → patch) and ask.
- Deliverable is the edited `CHANGELOG.md`. Final chat message: 1–3 sentences
  (version, counts per category) — never paste the entries into chat.
- **Language:** entries follow an explicit language request or the existing
  changelog's language. Keep a Changelog category headers (Added / Changed /
  Deprecated / Removed / Fixed / Security) stay canonical English.
