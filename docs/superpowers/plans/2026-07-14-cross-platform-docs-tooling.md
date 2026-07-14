# Cross-platform Documentation Tooling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate the `dotnet-angular-docs` persona and commands for Claude Code, GitHub Copilot, and VS Code agent mode from one source, and install them into any repo via `npx`.

**Architecture:** A single source of truth (`core/` + the unchanged `skills/`) is transformed by a small Node renderer using per-platform data manifests (`adapters/*.yml`). A pure `render(core, adapter)` function emits persona + command files; skills are copied verbatim. An `install.js` CLI (the `npx` bin) writes the rendered files into a target repository. The Claude Code plugin's own files (`agents/`, `commands/`) become committed rendered artifacts guarded by a sync test.

**Tech Stack:** Node.js (ESM), `js-yaml` (only runtime dependency), Node built-in test runner (`node:test` + `node:assert`).

## Global Constraints

- **Node >= 20** (uses `node:test`, `node:util.parseArgs`, `import.meta.url`).
- **Exactly one runtime dependency:** `js-yaml`. Do not add test frameworks or other libs.
- **ESM only:** `package.json` has `"type": "module"`; use `import`, not `require`.
- **Repo is English-only.** All code comments, file content, and commit messages in English.
- **Commit convention:** conventional commits (`feat:`, `test:`, `docs:`, `chore:`); **no Claude attribution / no Co-Authored-By footer.**
- **Skills are never re-rendered**, only copied verbatim.
- **Rendered Claude files** (`agents/docs-writer.md`, `commands/docs-*.md`) are committed and must stay byte-identical to `render(core, claude)` (enforced by the sync test).
- **Command names must never equal skill names** (a command shadows a same-named skill) — enforced as a build-time invariant.
- Package/bin name: `dotnet-angular-docs-init`.

---

### Task 1: Package scaffold + frontmatter helper

**Files:**
- Create: `package.json`
- Create: `src/frontmatter.js`
- Test: `tests/frontmatter.test.js`

**Interfaces:**
- Produces: `splitFrontmatter(text: string) -> { data: object, body: string }`; `stringify({ data: object, body: string }) -> string`.

- [ ] **Step 1: Create `package.json`**

```json
{
  "name": "dotnet-angular-docs-init",
  "version": "0.1.0",
  "description": "Install the dotnet-angular-docs documentation tooling into a repo for Claude Code, GitHub Copilot, or VS Code agent mode.",
  "type": "module",
  "bin": { "dotnet-angular-docs-init": "src/install.js" },
  "files": ["src", "core", "adapters", "skills"],
  "scripts": { "test": "node --test" },
  "engines": { "node": ">=20" },
  "dependencies": { "js-yaml": "^4.1.0" },
  "license": "MIT"
}
```

- [ ] **Step 2: Install the dependency**

Run: `npm install`
Expected: creates `node_modules/` and `package-lock.json`; `js-yaml` present.

- [ ] **Step 3: Write the failing test**

```js
// tests/frontmatter.test.js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { splitFrontmatter, stringify } from '../src/frontmatter.js';

test('splitFrontmatter parses data and body', () => {
  const { data, body } = splitFrontmatter('---\nname: x\n---\nHello world');
  assert.equal(data.name, 'x');
  assert.equal(body.trim(), 'Hello world');
});

test('splitFrontmatter returns empty data when no frontmatter', () => {
  const { data, body } = splitFrontmatter('Just body');
  assert.deepEqual(data, {});
  assert.equal(body, 'Just body');
});

test('stringify round-trips through splitFrontmatter', () => {
  const out = stringify({ data: { name: 'x', tools: ['a', 'b'] }, body: 'Body here' });
  const { data, body } = splitFrontmatter(out);
  assert.equal(data.name, 'x');
  assert.deepEqual(data.tools, ['a', 'b']);
  assert.equal(body.trim(), 'Body here');
});
```

- [ ] **Step 4: Run test to verify it fails**

Run: `node --test tests/frontmatter.test.js`
Expected: FAIL — `Cannot find module '../src/frontmatter.js'`.

- [ ] **Step 5: Write minimal implementation**

```js
// src/frontmatter.js
import yaml from 'js-yaml';

const FM_RE = /^---\n([\s\S]*?)\n---\n?([\s\S]*)$/;

export function splitFrontmatter(text) {
  const m = FM_RE.exec(text);
  if (!m) return { data: {}, body: text };
  return { data: yaml.load(m[1]) || {}, body: m[2] };
}

export function stringify({ data, body }) {
  const fm = yaml.dump(data, { lineWidth: -1 }).trimEnd();
  return `---\n${fm}\n---\n\n${body.replace(/^\n+/, '')}`;
}
```

- [ ] **Step 6: Run test to verify it passes**

Run: `node --test tests/frontmatter.test.js`
Expected: PASS (3 tests).

- [ ] **Step 7: Commit**

```bash
git add package.json package-lock.json src/frontmatter.js tests/frontmatter.test.js
git commit -m "feat: add node package scaffold and frontmatter helper"
```

---

### Task 2: Extract the single source (`core/`)

**Files:**
- Create: `core/persona.md`
- Create: `core/commands.yml`
- Create: `core/instructions.md`
- Test: `tests/core.test.js`

**Interfaces:**
- Produces: `core/persona.md` (frontmatter `name`, `description`; body contains the token `{{skill_invocation}}`), `core/commands.yml` (list of `{ name, skill, description, argument-hint, contract-summary }`), `core/instructions.md` (plain Markdown grounding rules).

- [ ] **Step 1: Create `core/persona.md`**

Copy the body of the existing `agents/docs-writer.md` verbatim, with two changes: (a) drop the platform-specific frontmatter (`tools`, `model`) — keep only `name` and `description`; (b) in rule 3, replace the phrase `loading it with the Skill tool` with `{{skill_invocation}}`. Result:

```markdown
---
name: docs-writer
description: >-
  Technical documentation specialist for .NET and Angular codebases.
  Use this agent when the goal is to create or update documentation
  rather than write feature code.
---

You are a technical writer embedded in a .NET + Angular engineering team.
Your job is to produce documentation that is accurate, grounded in the
actual source code, and maintainable.

## Operating rules

1. **Ground everything in code.** Never document an endpoint, component,
   config value, or behavior you have not located in the source. If you
   cannot verify something, mark it explicitly as `> ⚠ Unverified` rather
   than guessing.
2. **Detect the stack first.** Before writing, identify:
   - .NET: solution/project files (`*.sln`, `*.csproj`), target framework,
     ASP.NET style (controllers vs minimal APIs), presence of Swashbuckle/NSwag.
   - Angular: `angular.json`, Angular version from `package.json`,
     standalone components vs NgModules, state management (NgRx/signals/services).
3. **Use the matching skill.** For API docs, architecture docs, README,
   user manuals, or changelogs, follow the procedure in the corresponding
   skill — do not improvise a different structure. When your task names a
   skill, your first action is {{skill_invocation}}.
4. **One document, one purpose.** Do not mix audiences (developer vs
   end-user) in a single file.
5. **Output is always Markdown** unless the user asks otherwise. Diagrams
   are always Mermaid (renderable on GitHub), never ASCII art or image links.
6. **Idempotent updates.** When updating existing docs, preserve manually
   written sections. Only regenerate sections delimited by
   `<!-- docgen:begin:<section> -->` / `<!-- docgen:end:<section> -->`
   markers, or clearly outdated content the user asked to refresh.
7. **Ask before large scans.** If the workspace contains more than ~20
   projects, confirm scope with the user before analyzing everything.
8. **Deliverables go to files, not chat.** When a skill defines an output
   contract (file paths, header formats, markers), follow it exactly. Write
   the file first, then reply with a short summary (1–3 sentences). Never
   substitute a chat message for a required file.
9. **Output language.** Resolve in this order: an explicit language request
   in the arguments (e.g. `lang:pl`, "po polsku", "in German") → the language
   of existing docs when updating them → the language the user wrote their
   request in → English. Never translate code identifiers, routes, shell
   commands, or format-contract labels that tools parse.
10. **Token economy.** Spend tokens on the documentation files, not around
    them: no step-by-step narration of what you are about to do, no pasting
    file contents into chat after writing them, no restating the docs in your
    reply. When invoked as a subagent, reply only with the files written
    (paths) and a one-line status per file. This never shortens the
    documentation itself — depth and completeness of the deliverable always
    win over brevity.
```

- [ ] **Step 2: Create `core/commands.yml`**

Enumerate all 10 commands. For each, pull `description` and `argument-hint` from the frontmatter of the matching `commands/docs-*.md`, and condense its "Key contract" paragraph into `contract-summary`. The command→skill mapping is fixed:

| command | skill |
|---|---|
| docs-api | api-docs |
| docs-arch | architecture-docs |
| docs-readme | project-readme |
| docs-manual | user-manual |
| docs-changelog | changelog |
| docs-schema | db-schema-docs |
| docs-custom | custom-docs |
| docs-all | docs-suite |
| docs-pages | docs-site |
| docs-ops | ops-docs |

Worked example for the first entry (extracted from the existing `commands/docs-api.md`):

```yaml
- name: docs-api
  skill: api-docs
  description: Generate REST API documentation from ASP.NET controllers / minimal APIs
  argument-hint: "[feature, controller, or path — default: whole API surface]"
  contract-summary: >-
    Write files to docs/api/ (one per feature group + index.md); every endpoint
    section header is exactly `### METHOD /route`; wrap generated sections in
    <!-- docgen:begin:endpoints --> / <!-- docgen:end:endpoints --> markers.
    Never invent endpoints — verify each in code.
# ...repeat the same four fields for the remaining 9 commands, pulling
# description/argument-hint from each commands/docs-*.md frontmatter and the
# contract-summary from that file's "Key contract" paragraph.
```

- [ ] **Step 3: Create `core/instructions.md`**

A short, platform-neutral grounding file used to render the root instructions on Copilot/VS Code:

```markdown
# Documentation grounding rules

These rules apply to all documentation work in this repository.

- Ground every statement in the actual source code. Never document an
  endpoint, component, config value, or behavior you have not located in
  the source; mark anything unverifiable as `> ⚠ Unverified`.
- Output is Markdown; diagrams are Mermaid (never ASCII art or image links).
- Preserve hand-written sections. Only regenerate content between
  `<!-- docgen:begin:<section> -->` / `<!-- docgen:end:<section> -->` markers.
- Never invent endpoints, commands, or behavior. Never print secret values.
```

- [ ] **Step 4: Write the test**

```js
// tests/core.test.js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import yaml from 'js-yaml';
import { splitFrontmatter } from '../src/frontmatter.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

test('persona has name/description and the skill_invocation token', () => {
  const { data, body } = splitFrontmatter(fs.readFileSync(path.join(ROOT, 'core/persona.md'), 'utf8'));
  assert.equal(data.name, 'docs-writer');
  assert.ok(data.description);
  assert.ok(body.includes('{{skill_invocation}}'));
});

test('commands.yml lists 10 well-formed entries', () => {
  const cmds = yaml.load(fs.readFileSync(path.join(ROOT, 'core/commands.yml'), 'utf8'));
  assert.equal(cmds.length, 10);
  for (const c of cmds) {
    for (const key of ['name', 'skill', 'description', 'argument-hint', 'contract-summary']) {
      assert.ok(c[key], `command ${c.name} missing ${key}`);
    }
  }
});
```

- [ ] **Step 5: Run test to verify it passes**

Run: `node --test tests/core.test.js`
Expected: PASS (2 tests).

- [ ] **Step 6: Commit**

```bash
git add core/ tests/core.test.js
git commit -m "feat: extract single-source core (persona, commands, instructions)"
```

---

### Task 3: Adapter manifests + loader

**Files:**
- Create: `adapters/claude.yml`, `adapters/copilot.yml`, `adapters/vscode.yml`
- Create: `src/render.js` (loaders only in this task)
- Test: `tests/adapters.test.js`

**Interfaces:**
- Produces: `loadCore(root) -> { persona: {data, body}, commands: [...], instructions: string }`; `loadAdapter(root, name) -> object`; `skillNames(root) -> string[]`.

- [ ] **Step 1: Create `adapters/claude.yml`**

```yaml
platform: claude
persona:
  path: agents/docs-writer.md
  frontmatter:
    tools: Skill, Read, Write, Edit, Bash, Glob, Grep
    model: inherit
  skill_invocation: loading it with the Skill tool
  command_skill_ref: "invoke the Skill tool with skill `{skill}`"
commands:
  dir: commands
  ext: .md
  arg_token: $ARGUMENTS
  frontmatter: {}
skills:
  copy_to: skills
instructions:
  path: null
```

- [ ] **Step 2: Create `adapters/copilot.yml`**

```yaml
platform: copilot
persona:
  path: .github/agents/docs-writer.agent.md
  frontmatter:
    tools: ["search/codebase", "githubRepo", "edit", "view", "bash"]
  skill_invocation: opening and following the corresponding skill file
  command_skill_ref: "follow the procedure in the `{skill}` skill file"
commands:
  dir: .github/prompts
  ext: .prompt.md
  arg_token: ${input}
  frontmatter:
    mode: agent
skills:
  copy_to: .github/skills
instructions:
  path: .github/copilot-instructions.md
```

- [ ] **Step 3: Create `adapters/vscode.yml`**

```yaml
platform: vscode
persona:
  path: .github/chatmodes/docs-writer.chatmode.md
  frontmatter:
    tools: [codebase, search, editFiles, runCommands, fetch]
  skill_invocation: opening and following the corresponding skill file
  command_skill_ref: "follow the procedure in the `{skill}` skill file"
commands:
  dir: .github/prompts
  ext: .prompt.md
  arg_token: ${input}
  frontmatter:
    mode: docs-writer
skills:
  copy_to: .github/instructions
instructions:
  path: .github/copilot-instructions.md
```

- [ ] **Step 4: Write the failing test**

```js
// tests/adapters.test.js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadCore, loadAdapter, skillNames } from '../src/render.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

test('loadCore returns persona, commands, instructions', () => {
  const core = loadCore(ROOT);
  assert.equal(core.persona.data.name, 'docs-writer');
  assert.equal(core.commands.length, 10);
  assert.ok(core.instructions.length > 0);
});

test('each adapter has the required keys', () => {
  for (const name of ['claude', 'copilot', 'vscode']) {
    const a = loadAdapter(ROOT, name);
    assert.equal(a.platform, name);
    assert.ok(a.persona.path);
    assert.ok(a.persona.skill_invocation);
    assert.ok(a.persona.command_skill_ref);
    assert.ok(a.commands.dir);
    assert.ok(a.commands.ext);
    assert.ok(a.commands.arg_token);
    assert.ok(a.skills.copy_to);
  }
});

test('skillNames finds the known skills', () => {
  const names = skillNames(ROOT);
  assert.ok(names.includes('api-docs'));
  assert.ok(names.includes('docs-suite'));
});
```

- [ ] **Step 5: Run test to verify it fails**

Run: `node --test tests/adapters.test.js`
Expected: FAIL — `render.js` has no `loadCore` export.

- [ ] **Step 6: Write minimal implementation (loaders)**

```js
// src/render.js
import fs from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';
import { splitFrontmatter, stringify } from './frontmatter.js';

export function loadCore(root) {
  const persona = splitFrontmatter(fs.readFileSync(path.join(root, 'core/persona.md'), 'utf8'));
  const commands = yaml.load(fs.readFileSync(path.join(root, 'core/commands.yml'), 'utf8'));
  const instructions = fs.readFileSync(path.join(root, 'core/instructions.md'), 'utf8');
  return { persona, commands, instructions };
}

export function loadAdapter(root, name) {
  return yaml.load(fs.readFileSync(path.join(root, `adapters/${name}.yml`), 'utf8'));
}

export function skillNames(root) {
  const dir = path.join(root, 'skills');
  return fs.readdirSync(dir, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name);
}
```

- [ ] **Step 7: Run test to verify it passes**

Run: `node --test tests/adapters.test.js`
Expected: PASS (3 tests).

- [ ] **Step 8: Commit**

```bash
git add adapters/ src/render.js tests/adapters.test.js
git commit -m "feat: add platform adapter manifests and core/adapter loaders"
```

---

### Task 4: Render the persona

**Files:**
- Modify: `src/render.js`
- Test: `tests/render-persona.test.js`

**Interfaces:**
- Consumes: `loadCore`, `loadAdapter`.
- Produces: `renderPersona(core, adapter) -> { path: string, content: string }`. Output frontmatter = core persona `name`/`description` merged with `adapter.persona.frontmatter`; every `{{skill_invocation}}` in the body replaced by `adapter.persona.skill_invocation`.

- [ ] **Step 1: Write the failing test**

```js
// tests/render-persona.test.js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadCore, loadAdapter, renderPersona } from '../src/render.js';
import { splitFrontmatter } from '../src/frontmatter.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

test('claude persona has Skill tools and resolved invocation, at the claude path', () => {
  const core = loadCore(ROOT);
  const out = renderPersona(core, loadAdapter(ROOT, 'claude'));
  assert.equal(out.path, 'agents/docs-writer.md');
  const { data, body } = splitFrontmatter(out.content);
  assert.equal(data.name, 'docs-writer');
  assert.equal(data.tools, 'Skill, Read, Write, Edit, Bash, Glob, Grep');
  assert.equal(data.model, 'inherit');
  assert.ok(body.includes('loading it with the Skill tool'));
  assert.ok(!body.includes('{{skill_invocation}}'));
});

test('vscode persona is a chatmode with array tools', () => {
  const core = loadCore(ROOT);
  const out = renderPersona(core, loadAdapter(ROOT, 'vscode'));
  assert.equal(out.path, '.github/chatmodes/docs-writer.chatmode.md');
  const { data, body } = splitFrontmatter(out.content);
  assert.deepEqual(data.tools, ['codebase', 'search', 'editFiles', 'runCommands', 'fetch']);
  assert.ok(body.includes('opening and following the corresponding skill file'));
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/render-persona.test.js`
Expected: FAIL — `renderPersona` is not a function.

- [ ] **Step 3: Add `renderPersona` to `src/render.js`**

```js
export function renderPersona(core, adapter) {
  const body = core.persona.body.replaceAll('{{skill_invocation}}', adapter.persona.skill_invocation);
  const data = { ...core.persona.data, ...adapter.persona.frontmatter };
  return { path: adapter.persona.path, content: stringify({ data, body }) };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/render-persona.test.js`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/render.js tests/render-persona.test.js
git commit -m "feat: render docs-writer persona per platform"
```

---

### Task 5: Render the commands

**Files:**
- Modify: `src/render.js`
- Test: `tests/render-commands.test.js`

**Interfaces:**
- Produces: `renderCommands(core, adapter) -> Array<{ path, content }>`, one per command. Body uses `adapter.persona.command_skill_ref` (with `{skill}` substituted) and `adapter.commands.arg_token`. Frontmatter = `{ description, 'argument-hint', ...adapter.commands.frontmatter }`.

- [ ] **Step 1: Write the failing test**

```js
// tests/render-commands.test.js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadCore, loadAdapter, renderCommands } from '../src/render.js';
import { splitFrontmatter } from '../src/frontmatter.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

test('claude renders one .md per command with $ARGUMENTS and Skill-tool ref', () => {
  const core = loadCore(ROOT);
  const outs = renderCommands(core, loadAdapter(ROOT, 'claude'));
  assert.equal(outs.length, 10);
  const api = outs.find((o) => o.path === 'commands/docs-api.md');
  assert.ok(api, 'docs-api.md present');
  assert.ok(api.content.includes('invoke the Skill tool with skill `api-docs`'));
  assert.ok(api.content.includes('$ARGUMENTS'));
});

test('vscode renders prompt files with ${input} and mode frontmatter', () => {
  const core = loadCore(ROOT);
  const outs = renderCommands(core, loadAdapter(ROOT, 'vscode'));
  const api = outs.find((o) => o.path === '.github/prompts/docs-api.prompt.md');
  assert.ok(api, 'docs-api.prompt.md present');
  const { data, body } = splitFrontmatter(api.content);
  assert.equal(data.mode, 'docs-writer');
  assert.ok(body.includes('${input}'));
  assert.ok(body.includes('follow the procedure in the `api-docs` skill file'));
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/render-commands.test.js`
Expected: FAIL — `renderCommands` is not a function.

- [ ] **Step 3: Add `renderCommands` to `src/render.js`**

```js
export function renderCommands(core, adapter) {
  return core.commands.map((c) => {
    const ref = adapter.persona.command_skill_ref.replace('{skill}', c.skill);
    const data = {
      description: c.description,
      'argument-hint': c['argument-hint'],
      ...adapter.commands.frontmatter,
    };
    const body = [
      `REQUIRED FIRST STEP: ${ref} and follow its procedure and output contract`,
      `exactly. Do not document from this summary alone.`,
      ``,
      `Key contract: ${c['contract-summary']}`,
      ``,
      `Scope: ${adapter.commands.arg_token} (if empty, use the skill's default`,
      `scope — ask first when the workspace contains more than ~20 projects).`,
    ].join('\n');
    return { path: `${adapter.commands.dir}/${c.name}${adapter.commands.ext}`, content: stringify({ data, body }) };
  });
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/render-commands.test.js`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/render.js tests/render-commands.test.js
git commit -m "feat: render slash commands / prompt files per platform"
```

---

### Task 6: Skills copy plan, invariants, and top-level `render()`

**Files:**
- Modify: `src/render.js`
- Test: `tests/render.test.js`

**Interfaces:**
- Produces:
  - `renderSkills(root, adapter) -> Array<{ path, content }>` — every file under `skills/**` re-homed under `adapter.skills.copy_to`, content unchanged.
  - `checkInvariants(core, names)` — throws `Error` if a command name equals a skill name, or a command targets a missing skill.
  - `renderInstructions(core, adapter) -> { path, content } | null`.
  - `render(root, core, adapter) -> Array<{ path, content }>` — persona + commands + skills + instructions, after `checkInvariants`.

- [ ] **Step 1: Write the failing test**

```js
// tests/render.test.js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadCore, loadAdapter, skillNames, render, checkInvariants } from '../src/render.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

test('checkInvariants throws when a command name equals a skill name', () => {
  const core = { commands: [{ name: 'api-docs', skill: 'api-docs' }] };
  assert.throws(() => checkInvariants(core, ['api-docs']), /shadow/);
});

test('checkInvariants throws when a command targets a missing skill', () => {
  const core = { commands: [{ name: 'docs-x', skill: 'nope' }] };
  assert.throws(() => checkInvariants(core, ['api-docs']), /missing skill/);
});

test('render(vscode) includes persona, prompts, copied skills, and instructions', () => {
  const core = loadCore(ROOT);
  const files = render(ROOT, core, loadAdapter(ROOT, 'vscode'));
  const paths = files.map((f) => f.path);
  assert.ok(paths.includes('.github/chatmodes/docs-writer.chatmode.md'));
  assert.ok(paths.includes('.github/prompts/docs-api.prompt.md'));
  assert.ok(paths.includes('.github/copilot-instructions.md'));
  assert.ok(paths.some((p) => p.startsWith('.github/instructions/api-docs/')));
});

test('render(claude) has no instructions file (path is null)', () => {
  const core = loadCore(ROOT);
  const files = render(ROOT, core, loadAdapter(ROOT, 'claude'));
  assert.ok(!files.some((f) => f.path.endsWith('copilot-instructions.md')));
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/render.test.js`
Expected: FAIL — `render` / `checkInvariants` not exported.

- [ ] **Step 3: Add the remaining functions to `src/render.js`**

```js
function walk(dir) {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...walk(full));
    else out.push(full);
  }
  return out;
}

export function renderSkills(root, adapter) {
  const skillsRoot = path.join(root, 'skills');
  return walk(skillsRoot).map((full) => {
    const rel = path.relative(skillsRoot, full).split(path.sep).join('/');
    return { path: `${adapter.skills.copy_to}/${rel}`, content: fs.readFileSync(full, 'utf8') };
  });
}

export function checkInvariants(core, names) {
  const skills = new Set(names);
  for (const c of core.commands) {
    if (skills.has(c.name)) throw new Error(`command "${c.name}" would shadow the same-named skill`);
    if (!skills.has(c.skill)) throw new Error(`command "${c.name}" targets missing skill "${c.skill}"`);
  }
}

export function renderInstructions(core, adapter) {
  if (!adapter.instructions || !adapter.instructions.path) return null;
  const content = `<!-- docgen:begin:instructions -->\n${core.instructions.trim()}\n<!-- docgen:end:instructions -->\n`;
  return { path: adapter.instructions.path, content };
}

export function render(root, core, adapter) {
  checkInvariants(core, skillNames(root));
  const files = [renderPersona(core, adapter), ...renderCommands(core, adapter), ...renderSkills(root, adapter)];
  const instr = renderInstructions(core, adapter);
  if (instr) files.push(instr);
  return files;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/render.test.js`
Expected: PASS (4 tests).

- [ ] **Step 5: Run the whole suite**

Run: `npm test`
Expected: PASS (all tests from Tasks 1–6).

- [ ] **Step 6: Commit**

```bash
git add src/render.js tests/render.test.js
git commit -m "feat: add skills copy, build invariants, and top-level render"
```

---

### Task 7: Installer CLI (`npx` entrypoint)

**Files:**
- Create: `src/install.js`
- Test: `tests/install.test.js`

**Interfaces:**
- Consumes: `loadCore`, `loadAdapter`, `render`.
- Produces: `planFor(root, platform, targetRoot) -> Array<{ abs, content }>`; a `main()` that parses `--platform`, `--target`, `--dry-run`, `--force`. Files that exist are skipped unless `--force`, except the instructions file whose `docgen:instructions` region is always replaced in place.

- [ ] **Step 1: Write the failing test**

```js
// tests/install.test.js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { planFor } from '../src/install.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

test('planFor(vscode) produces absolute paths under the target', () => {
  const target = fs.mkdtempSync(path.join(os.tmpdir(), 'dad-'));
  const plan = planFor(ROOT, 'vscode', target);
  const chat = plan.find((f) => f.abs.endsWith(path.join('.github', 'chatmodes', 'docs-writer.chatmode.md')));
  assert.ok(chat, 'chatmode planned');
  assert.ok(chat.abs.startsWith(target));
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/install.test.js`
Expected: FAIL — `planFor` not found.

- [ ] **Step 3: Write `src/install.js`**

```js
#!/usr/bin/env node
import { parseArgs } from 'node:util';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadCore, loadAdapter, render } from './render.js';

const PKG_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PLATFORMS = ['claude', 'copilot', 'vscode'];

export function planFor(root, platform, targetRoot) {
  const files = render(root, loadCore(root), loadAdapter(root, platform));
  return files.map((f) => ({ abs: path.join(targetRoot, f.path), content: f.content }));
}

function writeFile(abs, content, force) {
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  const isInstructions = abs.endsWith('copilot-instructions.md');
  if (fs.existsSync(abs) && !force && !isInstructions) return 'skip';
  if (isInstructions && fs.existsSync(abs)) {
    const existing = fs.readFileSync(abs, 'utf8');
    const re = /<!-- docgen:begin:instructions -->[\s\S]*?<!-- docgen:end:instructions -->\n?/;
    const merged = re.test(existing) ? existing.replace(re, content) : existing.trimEnd() + '\n\n' + content;
    fs.writeFileSync(abs, merged);
    return 'merge';
  }
  fs.writeFileSync(abs, content);
  return 'write';
}

function main() {
  const { values } = parseArgs({ options: {
    platform: { type: 'string' },
    target: { type: 'string', default: '.' },
    'dry-run': { type: 'boolean', default: false },
    force: { type: 'boolean', default: false },
  } });
  const chosen = values.platform === 'all' ? PLATFORMS : [values.platform];
  if (!values.platform || chosen.some((p) => !PLATFORMS.includes(p))) {
    console.error(`Usage: dotnet-angular-docs-init --platform ${PLATFORMS.join('|')}|all [--target DIR] [--dry-run] [--force]`);
    process.exit(1);
  }
  const targetRoot = path.resolve(values.target);
  for (const platform of chosen) {
    for (const f of planFor(PKG_ROOT, platform, targetRoot)) {
      if (values['dry-run']) { console.log(`[dry-run] ${path.relative(targetRoot, f.abs)}`); continue; }
      const action = writeFile(f.abs, f.content, values.force);
      console.log(`${action}: ${path.relative(targetRoot, f.abs)}`);
    }
  }
}

if (import.meta.url === `file://${process.argv[1]}` || process.argv[1] === fileURLToPath(import.meta.url)) {
  main();
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/install.test.js`
Expected: PASS.

- [ ] **Step 5: Manual smoke test into a temp dir**

Run (bash):
```bash
TMP=$(mktemp -d) && node src/install.js --platform vscode --target "$TMP" && find "$TMP/.github" -type f | sort
```
Expected: prints `write: ...` lines and lists `.github/chatmodes/docs-writer.chatmode.md`, `.github/prompts/docs-*.prompt.md`, `.github/instructions/...`, `.github/copilot-instructions.md`.

- [ ] **Step 6: Commit**

```bash
git add src/install.js tests/install.test.js
git commit -m "feat: add npx installer CLI"
```

---

### Task 8: Migrate committed Claude files to rendered output + sync guard

**Files:**
- Modify: `agents/docs-writer.md`, `commands/docs-*.md` (regenerate from core)
- Delete: `copilot/agents/docs-writer.agent.md` (now generated on demand; no longer hand-maintained)
- Modify: `README.md` layout note referencing `copilot/` (remove the stale path)
- Test: `tests/sync.test.js`

**Interfaces:**
- Consumes: `render`, `loadCore`, `loadAdapter`.

- [ ] **Step 1: Write the failing sync test**

```js
// tests/sync.test.js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadCore, loadAdapter, render } from '../src/render.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

test('committed Claude files match render(core, claude)', () => {
  const files = render(ROOT, loadCore(ROOT), loadAdapter(ROOT, 'claude'));
  for (const f of files) {
    if (f.path.startsWith('skills/')) continue; // skills are the source, not rendered artifacts
    const onDisk = fs.readFileSync(path.join(ROOT, f.path), 'utf8');
    assert.equal(onDisk, f.content, `${f.path} is out of sync with core — re-run the generator`);
  }
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/sync.test.js`
Expected: FAIL — the existing hand-written `agents/docs-writer.md` / `commands/*.md` differ from the rendered output.

- [ ] **Step 3: Regenerate the committed Claude files**

Run (bash):
```bash
node -e "import('./src/render.js').then(async (m) => { \
  const fs = await import('node:fs'); const path = await import('node:path'); \
  const files = m.render('.', m.loadCore('.'), m.loadAdapter('.', 'claude')); \
  for (const f of files) { if (f.path.startsWith('skills/')) continue; \
    fs.mkdirSync(path.dirname(f.path), { recursive: true }); fs.writeFileSync(f.path, f.content); } \
})"
```
Expected: overwrites `agents/docs-writer.md` and `commands/docs-*.md` with rendered content.

- [ ] **Step 4: Remove the now-redundant hand-maintained Copilot agent**

Run: `git rm copilot/agents/docs-writer.agent.md` and remove the empty `copilot/` tree.

- [ ] **Step 5: Run test to verify it passes**

Run: `node --test tests/sync.test.js`
Expected: PASS.

- [ ] **Step 6: Run the existing plugin validator and full suite**

Run: `python scripts/validate.py && npm test`
Expected: validator exits 0 (plugin still structurally valid); all Node tests pass.

- [ ] **Step 7: Commit**

```bash
git add agents/ commands/ tests/sync.test.js
git rm -r copilot
git commit -m "refactor: generate Claude plugin files from core, drop hand-maintained copilot variant"
```

---

### Task 9: Documentation

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the README**

Replace the "GitHub Copilot — repo-level" manual-copy section with the `npx` flow, and add a "Single source" subsection. Required content:

```markdown
## Install into your repo

- **Claude Code:** install this plugin as usual (marketplace or plugin directory).
- **GitHub Copilot:** `npx dotnet-angular-docs-init --platform copilot` in your repo.
- **VS Code agent mode:** `npx dotnet-angular-docs-init --platform vscode` in your repo.
- **All at once:** `npx dotnet-angular-docs-init --platform all`.

Add `--dry-run` to preview writes, `--force` to overwrite existing files.

## Single source of truth

Persona, commands, and grounding rules live once in `core/`; per-platform
naming lives in `adapters/*.yml`. `src/render.js` turns them into each
platform's files; `skills/` is copied verbatim. The Claude plugin's own
`agents/` and `commands/` are generated and kept in sync by `tests/sync.test.js`.
```

Also delete the old lines referencing `copilot/agents/docs-writer.agent.md` and the `cp -r … .github/skills` instructions.

- [ ] **Step 2: Verify no stale references remain**

Run: `grep -rn "copilot/agents" README.md`
Expected: no matches.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: document npx install and single-source architecture"
```

---

## Self-Review Notes

- **Spec coverage:** single source (Tasks 2–3) ✓; Node tooling + one dep (Task 1) ✓; `npx` installer with `--platform`/`--dry-run`/`--force` (Task 7) ✓; skills copied verbatim (Task 6) ✓; three rendered layers — persona/commands/instructions (Tasks 4–6) ✓; Claude committed + sync guard (Task 8) ✓; platform outputs table realized in adapters (Task 3) ✓; command↔skill collision invariant (Task 6) ✓; docs-suite parallelism caveat is skill wording, tracked as a follow-up content edit (see below). VS Code `.vsix` is a documented non-goal — no task, correct.
- **Deferred from spec (intentional):** porting `validate.py` to Node — Task 8 keeps `validate.py` as-is and adds the sync guard as a Node test instead; the two coexist. The `docs-suite` sequential-fallback wording is a one-line edit to `skills/docs-suite/SKILL.md`; fold it into Task 9 if desired, or leave for a follow-up since it does not affect rendering.
- **Placeholder scan:** the only "extract from existing file" instruction (Task 2, commands.yml) enumerates all 10 commands, their fixed skill mapping, the exact fields to copy, and a full worked entry — concrete, not a placeholder.
- **Type consistency:** `loadCore`/`loadAdapter`/`skillNames`/`renderPersona`/`renderCommands`/`renderSkills`/`renderInstructions`/`checkInvariants`/`render`/`planFor` names are used identically across tasks and tests.
