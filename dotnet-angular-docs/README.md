# dotnet-angular-docs

Documentation generator for .NET + Angular projects. It ships **seven narrow
skills**, **slash commands**, and a **docs-writer agent** for producing API
docs, architecture docs (ADR / C4 / Mermaid), README & onboarding guides, user
manuals, changelogs, EF Core data-model docs — and for auditing existing docs
against the code (drift detection). All output is grounded in actual
source-code analysis; the skills forbid inventing endpoints, commands, or
behavior.

It is **portable**: install it as a Claude Code plugin, or drop the skills into
a repository so GitHub Copilot (VS Code + coding agent) picks them up.

## What's inside

| Component | Purpose | Trigger words |
|---|---|---|
| `skills/api-docs` | REST API docs from ASP.NET controllers / minimal APIs, Angular client cross-ref, contract-drift detection | "API docs", "endpoints", "swagger", "dokumentacja API" |
| `skills/architecture-docs` | ADR, C4 overview, Mermaid dependency & sequence diagrams | "architecture", "ADR", "diagram", "data flow" |
| `skills/project-readme` | README / onboarding with verified, copy-pasteable commands | "readme", "onboarding", "getting started" |
| `skills/user-manual` | End-user manuals from Angular routes, forms, guards, i18n labels | "user manual", "instrukcja", "help content" |
| `skills/changelog` | Changelog / release notes from git history with breaking-change detection | "changelog", "release notes", "what changed" |
| `skills/docs-drift` | Audit existing docs against code: stale endpoints, broken README commands, outdated diagrams | "docs drift", "stale docs", "audyt dokumentacji" |
| `skills/db-schema-docs` | EF Core data model docs: entities, relations, Mermaid ER diagram, migration history | "data model", "ER diagram", "schemat bazy", "encje" |
| `skills/docs-suite` | **Multi-agent orchestrator**: full documentation set via parallel docs-writer subagents (one per service/area) + index synthesis | "document everything", "pełna dokumentacja", `/docs-all` |
| `commands/docs-*` | Slash commands (Claude Code only) — deterministic invocation of each skill | `/docs-api`, `/docs-drift`, `/docs-schema`, … |
| `agents/docs-writer.md` | Claude Code subagent enforcing grounding, idempotent updates, Markdown+Mermaid output | invoked via the Agent tool |
| `copilot/agents/docs-writer.agent.md` | Same agent, adapted for GitHub Copilot (Copilot tool names) | selected manually in chat |

## Layout

```
dotnet-angular-docs/
├── .claude-plugin/plugin.json         # Claude Code manifest
├── agents/docs-writer.md              # agent — Claude Code tool names
├── commands/                          # slash commands — Claude Code only
│   ├── docs-api.md … docs-changelog.md
│   ├── docs-drift.md
│   └── docs-schema.md
├── skills/                            # shared skills (used by both platforms)
│   ├── api-docs/ …
│   ├── architecture-docs/ …
│   ├── project-readme/ …
│   ├── user-manual/ …
│   ├── changelog/ …
│   ├── docs-drift/ …
│   └── db-schema-docs/ …
├── copilot/agents/docs-writer.agent.md   # agent — Copilot tool names
└── README.md
```

The `skills/` folder is shared and platform-neutral. Only the **agent** differs
between platforms (tool names and file extension), so it is kept in two places.

## Installation

### Claude Code (as a plugin)

The manifest lives in `.claude-plugin/plugin.json`, so Claude Code discovers the
plugin from the `dotnet-angular-docs/` directory. Add it via your plugin
marketplace, or point Claude Code at this directory. Verify with `/plugin` —
the seven skills, the `docs-*` commands, and the `docs-writer` agent should
appear.

Slash commands map 1:1 to skills for deterministic invocation:

| Command | Skill |
|---|---|
| `/docs-api [scope]` | api-docs |
| `/docs-arch [type]` | architecture-docs |
| `/docs-readme` | project-readme |
| `/docs-manual [feature]` | user-manual |
| `/docs-changelog [range]` | changelog |
| `/dotnet-angular-docs:docs-drift [area]` | docs-drift (skill invoked directly — see note) |
| `/docs-schema [context]` | db-schema-docs |

> **Naming note:** a command must never share its name with a skill — both
> register as `/plugin:name` and the command shadows the skill, so the skill's
> procedure never loads. That is why `docs-drift` has no wrapper command.

### GitHub Copilot — repo-level (VS Code + coding agent)

Copy the shared skills and the **Copilot** agent variant into the repository:

```bash
cp -r dotnet-angular-docs/skills/*            <your-repo>/.github/skills/
cp    dotnet-angular-docs/copilot/agents/docs-writer.agent.md \
                                              <your-repo>/.github/agents/
```

Use the **`copilot/agents/`** variant (not `agents/docs-writer.md`) — it uses
Copilot's tool names (`search/codebase`, `githubRepo`, `edit`, `view`, `bash`).
Commit — everyone on the team gets the skills automatically. Verify in VS Code
Copilot Chat with `/skills`.

> The `commands/` folder is Claude Code-specific — skip it for Copilot; the
> skills' trigger words cover the same functionality there.

## Design notes (why it's structured this way)

- **Seven narrow skills instead of one big one** — only skill frontmatter is
  loaded up front; the full body loads when your prompt matches. One monolithic
  "docs" skill would burn context on API-extraction rules when you just wanted a
  changelog.
- **Stack-specific extraction rules live in `references/`** — loaded on demand,
  keeping each SKILL.md body small.
- **Templates in separate files** — the agent reads them when rendering, and you
  can edit a template without touching skill logic.
- **Descriptions include Polish + English trigger words** — matching works on
  your team's actual prompts.
- **Idempotency markers** (`<!-- docgen:begin -->`) let skills refresh generated
  sections without clobbering hand-written docs.
- **One agent, two frontmatters** — the body is identical; only the `tools`
  declaration and file extension differ, because Claude Code and Copilot name
  their tools differently.

## Multi-repo systems

Skills work per-repo out of the box (README, changelog, schema, manuals).
Cross-repo features — Angular↔API cross-referencing, contract-drift detection,
and the whole-system C4 overview — need all repos visible at once. Two ways:

1. **Workspace-parent** (recommended): clone the repos side by side and run
   Claude Code from the parent folder.
2. **Extra dirs**: `claude --add-dir ../shop-frontend`, or pass
   `repos:../shop-frontend,../shop-admin` in a command's arguments.

When a counterpart repo is not available, skills mark the affected sections
`⚠ Unverified` / `⚠ not in workspace` instead of guessing. `changelog`
aggregates multi-repo release notes into one platform-level file when given
`repos:` (per-component sections, shared breaking-changes block).

## Multi-agent generation (`/docs-all`)

For large solutions (10+ projects) or whole workspaces, the `docs-suite` skill
fans the work out to parallel `docs-writer` subagents — one per service/area,
each loading exactly one skill with a narrow scope and a small context, ~4 at
a time. The orchestrator keeps whole-system reasoning (architecture overview,
`docs/index.md` synthesis, contract spot-checks) to itself and respawns a
failed item once. Small per-agent contexts also make output quality hold up
on smaller models.

**Model tiering (quality-first):** when the platform allows a model per agent
(Claude Code: `model` in the agent definition or per Agent/Task call; Copilot:
`model` pinned in the agent file), narrow generation items may run on a
smaller/faster model, while the architecture overview, synthesis, and all
contract spot-checks stay on the strongest one. The quality floor is
enforced, not assumed: any item failing its contract spot-check is redone
once on the strongest model. Model names are user configuration — the skills
never hardcode them.

**Token economy:** agents spend tokens on documentation files, not around
them — no narration, no pasting docs into chat, terse subagent returns
(file list + status). This never shortens the documentation itself.

## Customization

- **Output language:** pass it in the arguments — `lang:pl`, "po polsku",
  "in German", e.g. `/docs-api lang:pl` or
  `/dotnet-angular-docs:project-readme wygeneruj po polsku`. Resolution order
  (defined in the docs-writer agent): explicit request → language of the
  existing doc being updated → language you asked in → English. Code
  identifiers, routes, shell commands, and parsed labels (endpoint headers,
  drift Summary/verdict, Keep a Changelog categories) are never translated.
  `user-manual` additionally binds the text language to the i18n locale it
  quotes labels from.
- Change output paths in each SKILL.md ("Rules" section).
- Edit templates freely — structure is contract, wording is yours.
- Add company standards via a repo-level instructions file (Claude Code:
  `CLAUDE.md`; Copilot: `.github/copilot-instructions.md`); skills compose with
  instructions, they don't replace them.
