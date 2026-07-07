---
description: Generate changelog / release notes from git history with breaking-change detection
argument-hint: "[range or version, e.g. v1.2.0..HEAD — default: last tag → HEAD]"
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `changelog` and follow
its procedure exactly.

Key contract: classify into Keep a Changelog categories with breaking changes
on top; insert the new section idempotently into `CHANGELOG.md` — never
rewrite prior entries. Final chat message: 1–3 sentences (version, counts).

Range/version: $ARGUMENTS (default: last tag → HEAD; confirm with the user
if no tags exist).
