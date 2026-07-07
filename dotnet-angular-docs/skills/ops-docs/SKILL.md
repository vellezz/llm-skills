---
name: ops-docs
description: >-
  Generate deployment and operations documentation for DevOps and system
  administrators: component inventory, runtime requirements, configuration
  reference, message-broker topology, external integrations, deployment
  (Docker/Kubernetes), health checks, and network requirements — everything
  needed to redeploy the application in a new environment. Use whenever the
  user asks for deployment/operations/technical docs, or mentions "ops docs",
  "deployment documentation", "dokumentacja wdrożeniowa", "dokumentacja
  techniczna", "dokumentacja operacyjna", "health checks", "wdrożenie".
---

# Operations Documentation Generator

Audience: DevOps, sysadmins, deployment teams. Scope: configuration,
integrations, communication — **not** code internals. Purpose: enough to
redeploy the app in a fresh environment.

## Procedure

1. **Check `docs/.docgen/config.yml`** — keys under `ops-docs`: `output`
   (default `docs/operations/technical-reference.md`), `diagrams`
   (`mermaid` default; `plantuml` only when explicitly configured),
   `sections` (whitelist). Ignore unknown keys; never fail on config.
2. **Inventory the system from code and config files** (never assume):
   components with ports and exact framework versions (from `.csproj` /
   `package.json`), databases, brokers, caches, external HTTP services,
   docker-compose / K8s manifests / CI files.
3. **Render `templates/technical-reference.md`** section by section. Every
   fact traces to a file; uncertain → `⚠ Unverified`.
4. **Health checks get special care:** for each probe document endpoint,
   delays/thresholds, and — critically — **what it actually verifies**
   (often nothing beyond process liveness). State that as plain fact.
5. Diagrams follow `../architecture-docs/references/mermaid-conventions.md`.

## Rules (non-negotiable)

- **AS IS only.** Describe the current state. NO recommendations,
  suggestions, improvement lists, or "should/consider" language — if a
  health check verifies nothing, write "verifies only that the process
  responds; no dependency checks" and stop there.
- **No config-file dumps.** Never paste YAML/JSON/XML content. Convey
  configuration through tables (parameter | section/key | required |
  default | purpose) and short prose. Individual keys and values go in
  backticks.
- **No code fragments or implementation internals** — how it deploys and
  communicates, not how it works inside.
- **Secrets: names and where they come from — never values.** CMDB/secret
  variables as a mapping table (app parameter | variable name | purpose).
- **Exact versions** ("8.0", not "8.x") taken from project files.
- Tables over paragraphs; numbered steps for flows; `⚠` for critical
  warnings (only that marker, no other emoji).
- Language rule and docgen markers apply as everywhere else.
- Deliverable is the file. Final chat message: 1–3 sentences.

## Before finishing, verify

1. Every component lists port, framework + exact version, and source path.
2. Every database has its connection-string **key** (not value) and purpose.
3. Every broker config, queue/topic, and consumer is listed.
4. Every health check states what it actually verifies.
5. Network table covers inbound and outbound per component.
6. No YAML/JSON blocks, no recommendations anywhere in the document.
