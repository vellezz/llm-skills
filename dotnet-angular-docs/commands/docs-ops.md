---
description: Generate deployment & operations documentation (config, integrations, health checks, network)
argument-hint: '[component or scope, lang:xx — default: whole system]'
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `ops-docs` and follow its procedure and output contract
exactly. Do not document from this summary alone.

Key contract: AS IS only — no recommendations or suggestions; no YAML/JSON dumps, with configuration shown via tables and prose; secrets referenced by name never value; exact versions; health checks must state what they actually verify; diagrams are Mermaid (PlantUML only if the repo config demands it). Deliverable is the file; final chat message is 1–3 sentences.

Scope: $ARGUMENTS (if empty, use the skill's default
scope — ask first when the workspace contains more than ~20 projects).