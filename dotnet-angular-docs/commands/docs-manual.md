---
description: Generate an end-user manual from Angular routes, forms, and i18n labels
argument-hint: "[feature or route — default: all top-level routes]"
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `user-manual` and follow
its procedure and template exactly.

Key contract: audience is end users — no code, no class names, no HTTP verbs
in the output; use exact UI labels from i18n files. Deliverables are files
under `docs/user-guide/`. Final chat message: 1–3 sentences listing the files.

Scope: $ARGUMENTS (if empty, one guide per top-level route plus an index).
