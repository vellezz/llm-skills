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
