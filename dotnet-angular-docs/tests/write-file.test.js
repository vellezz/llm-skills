import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { writeFile } from '../src/install.js';

function tmpfile() {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'dad-wf-'));
  return path.join(d, 'sub', 'f.md');
}

test('writeFile writes when absent, skips identical, flags differing, overwrites with force', () => {
  const f = tmpfile();
  assert.equal(writeFile(f, 'A', false), 'write');
  assert.equal(fs.readFileSync(f, 'utf8'), 'A');
  assert.equal(writeFile(f, 'A', false), 'skip');
  assert.equal(writeFile(f, 'B', false), 'differs');
  assert.equal(fs.readFileSync(f, 'utf8'), 'A', 'differing content is NOT written without force');
  assert.equal(writeFile(f, 'B', true), 'write');
  assert.equal(fs.readFileSync(f, 'utf8'), 'B');
});
