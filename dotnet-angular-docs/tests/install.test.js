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
