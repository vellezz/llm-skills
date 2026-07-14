# Cross-platform documentation tooling — Design

**Date:** 2026-07-14
**Status:** Design approved; implementation plan pending
**Scope:** Deliver the `dotnet-angular-docs` functionality on Claude Code, GitHub
Copilot, and VS Code agent mode from a single repository, with automated install.

## Problem

`dotnet-angular-docs` currently ships as a Claude Code plugin: 11 platform-neutral
skills, slash commands, and a `docs-writer` agent. The same functionality should be
usable from three platforms — Claude Code, GitHub Copilot, and VS Code agent mode —
maintained from **one** source, with an automated way to install it into a target
project. Today the only cross-platform asset is a hand-maintained Copilot variant of
the agent, which drifts from the Claude one by hand.

## Goals

- **One source of truth** for all documentation logic — no hand-duplicated per-platform copies.
- **One-command installation** into a user's repository for Copilot and VS Code.
- **Claude Code keeps its native plugin distribution** unchanged.
- **No runtime dependency the audience lacks.** The audience (.NET + Angular teams)
  has `dotnet` and `node`, not necessarily Python.

## Non-goals (YAGNI for the first version)

- A compiled VS Code `.vsix` Marketplace extension. The architecture must not preclude
  it later, but it is out of scope now. VS Code is delivered file-based
  (`.chatmode.md`, auto-discovered by VS Code).
- Parallel multi-agent fan-out on Copilot / VS Code — those platforms do not spawn
  parallel sub-agents; `docs-suite` degrades to sequential there.

## Key decisions

1. **Single source of truth.** Documentation logic lives once; platform files are
   generated from it.
2. **Tooling in Node/JavaScript.** Both the author-side renderer and the user-facing
   installer are one Node package. Rationale: the Angular half of the audience already
   has Node; `npx` needs no global install; avoids imposing Python on users.
3. **Installation via `npx`.** `npx dotnet-angular-docs-init --platform copilot|vscode|claude|all`
   renders and writes files into the target repo. Claude Code additionally keeps its
   native plugin/marketplace install.
4. **Skills are copied verbatim.** The 11 skills are already platform-neutral Markdown;
   never re-rendered per platform, only copied. This protects them from drift.
5. **Only three thin layers are rendered:** the persona (agent / chatmode), the command
   wrappers (slash commands / prompt files), and the optional root instructions file.
6. **VS Code delivery is file-based now, `.vsix` later.** A `.chatmode.md` placed in
   `.github/chatmodes/` is auto-discovered by VS Code and appears in the agent-mode
   picker — no extension required. A future `.vsix` can bundle the same `core/` unchanged.
7. **Platform knowledge lives in data, not code.** Per-platform tool names, file paths,
   and extensions live in `adapters/*.yml`. When Copilot / VS Code conventions change,
   only the data file changes.

## Architecture

Single repo, single Node package. The repo root **remains a valid Claude Code plugin**
(skills stay in place). We add `core/`, `adapters/`, a renderer, and an installer.

```
dotnet-angular-docs/
├── core/                       # SINGLE SOURCE OF TRUTH (new)
│   ├── persona.md              #   docs-writer body (10 rules) + 1–2 platform placeholders
│   ├── commands.yml            #   command list: name, skill, description, argument-hint, contract-summary
│   └── instructions.md         #   shared grounding rules (optional root-instructions body)
├── adapters/                   # platform manifests — pure data (new)
│   ├── claude.yml
│   ├── copilot.yml
│   └── vscode.yml
├── src/                        # Node tooling (new)
│   ├── render.js               #   pure function: (core, adapter) -> { path: content }
│   └── install.js              #   npx entrypoint: pick target + platform, write files
├── package.json                # npm package, bin = install.js (new)
├── skills/                     # 11 skills — UNCHANGED, copied 1:1 to other platforms
├── agents/docs-writer.md       # RENDERED from core, committed (Claude marketplace reads it directly)
├── commands/docs-*.md          # RENDERED from core, committed
├── .claude-plugin/plugin.json  # unchanged
├── scripts/validate.py         # extended with a core↔rendered sync guard (or ported to Node — deferred)
├── tests/                      # + a render test
└── README.md
```

### Source of truth (`core/` + `skills/`)

- `skills/` — the 11 skills, unchanged; copied 1:1 to other platforms.
- `core/persona.md` — the docs-writer body (the 10 operating rules) with 1–2 placeholders
  for platform-specific phrasing (e.g. `{{skill_invocation}}`: Claude → "load it with the
  Skill tool"; Copilot / VS Code → "follow the procedure in the referenced skill file").
- `core/commands.yml` — one entry per command: `name`, target `skill`, `description`,
  `argument-hint`, `contract-summary`.
- `core/instructions.md` — shared grounding rules for the optional root instructions file.

### Adapter manifests (`adapters/*.yml`)

Pure data per platform: persona output path + frontmatter (tool names, extension, model),
command output dir/extension + argument token, where skills are copied, root-instructions
path. Example shape (`vscode.yml`):

```yaml
platform: vscode
persona:
  path: ".github/chatmodes/docs-writer.chatmode.md"
  frontmatter: { tools: [codebase, search, editFiles, runCommands, fetch] }
  skill_invocation: "follow the procedure in the referenced skill file"
commands:
  dir: ".github/prompts"
  ext: ".prompt.md"
  arg_token: "${input}"
  frontmatter: { mode: "docs-writer" }
skills:
  copy_to: ".github/instructions"
instructions:
  path: ".github/copilot-instructions.md"
```

### Renderer (`src/render.js`, runs author-side and at install time)

Pure function `(core, adapter) -> { relativePath: content }`. Three transformations:

1. **Persona** = manifest frontmatter (tool names + extension + model) **+** `core/persona.md`
   body with placeholders resolved from the manifest.
2. **Commands** = for each `commands.yml` entry: frontmatter + a "load the skill first" body
   + `contract-summary` + the manifest's argument token (`$ARGUMENTS` vs `${input}`).
3. **Skills** = copied unchanged to the manifest's skills location.

**Build-time invariants (fail fast, not at runtime):**
- No command name equals a skill name (a command shadows a same-named skill — established rule).
- Every command references an existing skill.
- Every skill named in the persona exists.

### Installer (`src/install.js`, `npx` entrypoint)

`npx dotnet-angular-docs-init --platform <p> [--target <dir>] [--dry-run] [--force]`.
Detects the target repo root, runs the renderer for the chosen platform(s), writes files.
Generated regions carry markers so re-running updates cleanly without clobbering user edits
(same idempotency philosophy as the docgen markers the skills already emit). `--dry-run`
lists planned writes without touching disk.

### Platform outputs

| | Claude Code | GitHub Copilot | VS Code agent mode |
|---|---|---|---|
| Persona | `agents/docs-writer.md` | `.github/agents/docs-writer.agent.md` | `.github/chatmodes/docs-writer.chatmode.md` |
| Skill invocation | `Skill` tool | by path / trigger | by path / trigger |
| Commands | `commands/docs-*.md` | `.github/prompts/*.prompt.md` | `.github/prompts/*.prompt.md` |
| Skills location | `skills/` (native) | `.github/skills/` | `.github/instructions/` (pending verification) |
| Root instructions | persona covers it | `.github/copilot-instructions.md` | `.github/copilot-instructions.md` |
| Install | native plugin / marketplace | `npx … --platform copilot` | `npx … --platform vscode` |

### Claude Code specifics

The repo root stays a valid plugin. Its rendered files (`agents/docs-writer.md`,
`commands/docs-*.md`) are **committed** so marketplace install works directly; a sync check
guards them against manual edits diverging from `core/`.

## Validation & testing

- **Sync guard:** re-render from `core/` and diff against committed Claude files; fail CI on
  drift, so nobody edits a rendered file instead of the source. Extends `scripts/validate.py`
  (or ported to Node — see open decisions).
- **Render test:** for each platform, assert expected files exist, frontmatter is valid, and
  tool names are mapped per the manifest.
- **Behavioral harness:** the existing `tests/` (headless on the fixture app) keeps validating
  skill behavior, unchanged.

## Known caveats / risks

1. **`docs-suite` parallelism** is Claude-Code-only; degrades to sequential on Copilot / VS Code.
   The skill wording states this generically — no per-platform rendering of the skill body.
2. **Convention drift / knowledge cutoff.** Exact Copilot / VS Code file conventions and tool
   names change quickly and are past the assistant's Jan-2026 knowledge cutoff. They must be
   verified against current docs before release. Because they live in `adapters/*.yml`, updates
   are data edits, not code changes.
3. **Idempotent re-install** relies on marker regions, consistent with the docgen markers the
   skills already use.

## Open decisions (low-priority, resolve during implementation)

- Whether to port `validate.py` to Node so the repo has a single tooling runtime.
- Exact skills location for VS Code agent mode (`.github/instructions/` vs `.github/skills/`),
  pending convention verification.
