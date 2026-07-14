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
