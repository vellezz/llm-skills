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
