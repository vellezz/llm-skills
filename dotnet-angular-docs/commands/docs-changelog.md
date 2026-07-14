---
description: Generate changelog / release notes from git history with breaking-change detection
argument-hint: '[range or version, e.g. v1.2.0..HEAD — default: last tag → HEAD]'
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `changelog` and follow its procedure and output contract
exactly. Do not document from this summary alone.

Key contract: Classify entries into Keep a Changelog categories with breaking changes on top, and insert the new section idempotently into CHANGELOG.md without rewriting prior entries. Final chat message is 1–3 sentences (version, counts).

Scope: $ARGUMENTS (if empty, use the skill's default
scope — ask first when the workspace contains more than ~20 projects).