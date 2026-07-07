---
description: Generate or refresh the README / onboarding guide with verified commands
argument-hint: "[optional: path to the README to refresh — default: ./README.md]"
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `project-readme` and
follow its procedure and template exactly. Extract facts from the repository
— never assume; verify commands where possible.

Key contract: the deliverable is the `README.md` file; when refreshing,
preserve hand-written prose and badges. Final chat message: 1–3 sentences on
what changed, no README pasted into chat.

Target: $ARGUMENTS (default `README.md` in the repository root).
