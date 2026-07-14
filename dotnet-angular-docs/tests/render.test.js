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
