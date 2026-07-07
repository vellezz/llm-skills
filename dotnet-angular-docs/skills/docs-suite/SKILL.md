---
name: docs-suite
description: >-
  Generate a complete documentation set (API docs, architecture overview,
  README, data model, user manuals) for a whole solution or multi-repo
  workspace by fanning out parallel docs-writer subagents — one per
  service/area — and synthesizing an index. Use when the user asks to
  "document everything", "generate full docs", "udokumentuj cały projekt",
  "pełna dokumentacja", "kompletna dokumentacja", or when the solution is
  too large for a single pass (10+ projects or several repositories).
---

# Documentation Suite Orchestrator

Produce the full documentation set by splitting the work across parallel
subagents. Each subagent gets ONE narrow scope and a small context — that is
what makes the output reliable on large solutions.

## Procedure

1. **Inventory the workspace.**
   - Repositories: a single repo, or a workspace parent with repos side by side.
   - Per repo: services with an API surface (controllers / minimal APIs /
     FastEndpoints), `DbContext` owners, Angular apps.
   - Existing `docs/` content and docgen markers.
2. **Plan the fan-out.** One work item per:
   - service → `api-docs`
   - DbContext owner → `db-schema-docs`
   - Angular app → `user-manual` (only if end-user docs were requested)
   - repository → `project-readme`
   - custom spec in `docs/.docgen/custom/*.md` → `custom-docs` (one item
     per spec)
   - deployment/operations reference → `ops-docs` (when requested)
   The architecture overview (`architecture-docs`) is ONE item at workspace
   level — it needs the whole picture, so keep it for yourself or one agent
   given the full inventory.
3. **Spawn subagents in parallel** (about 4 at a time) using the Agent/Task
   tool with the `docs-writer` agent. Every prompt must contain:
   - the ONE skill to load: "First invoke the Skill tool with skill
     `<name>` and follow its procedure and output contract exactly."
   - the exact scope (service/repo path) and expected output file path(s),
   - the resolved output language (docs-writer rule 9),
   - the return format: "Reply only with the list of files you wrote and a
     one-line status per file — no document content, no narration."
4. **Synthesize.** When all items are done:
   - build `docs/index.md` linking every generated file, grouped by area,
   - spot-check each file against its contract (endpoint header format,
     balanced docgen markers, language),
   - respawn a failed or contract-violating item once — on the strongest
     available model; fix small gaps yourself.
5. **Report.** Final chat message: 3–6 sentences — item counts, files written,
   anything that failed twice.

## Model tiering (optional — never at the cost of quality)

If the platform supports choosing a model per agent (Claude Code: `model` on
the Agent/Task call or in the agent definition; Copilot: `model` pinned in the
agent file):

- Narrow generation items (one service's `api-docs`, one `db-schema-docs`,
  one `user-manual`) MAY run on a smaller/faster model — they are safe there
  precisely because their scope is tiny and the output contract is pinned.
- The architecture overview, cross-repo synthesis, the index, and all contract
  spot-checks stay on the strongest available model (or yourself).
- Quality floor: the spot-check in step 4 is what protects quality — any item
  whose output violates its contract is redone once on the strongest model.
  If you cannot verify, do not downgrade.
- No per-agent model selection on this platform, or in doubt → session model
  for everything. Never hardcode model names in prompts; they are platform
  configuration.

## Token economy

- Subagents return a terse status only: files written (paths), item counts,
  and contract deviations — never the document content, never a summary of it.
- Do not narrate progress between spawns; spend tokens on documentation files,
  not commentary. Your own report is capped by step 5.

## Rules

- One agent, one scope — never give a single agent two services.
- Never delegate whole-system reasoning (architecture overview, cross-repo
  synthesis, the index) to an agent that has seen only one service.
- Pass the language and multi-repo context (`repos:` paths) down to every
  subagent explicitly — subagents do not inherit your conversation.
- If the Agent/Task tool is unavailable, do the items sequentially yourself in
  the same order, same scopes, same contracts.
- Deliverables are files; keep chat output to the final report.
