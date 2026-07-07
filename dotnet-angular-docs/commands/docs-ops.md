---
description: Generate deployment & operations documentation (config, integrations, health checks, network)
argument-hint: "[component or scope, lang:xx — default: whole system]"
---

REQUIRED FIRST STEP: invoke the Skill tool with skill `ops-docs` and follow
its procedure and rules exactly.

Key contract (also stated in the skill): AS IS only — no recommendations or
suggestions; no YAML/JSON dumps — configuration via tables and prose;
secrets by name, never value; exact versions; health checks must state what
they actually verify; Mermaid diagrams (PlantUML only if the repo config
demands it). Deliverable is the file; final chat message 1–3 sentences.

Scope: $ARGUMENTS
