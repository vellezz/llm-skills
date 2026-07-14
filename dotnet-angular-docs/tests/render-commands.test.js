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
