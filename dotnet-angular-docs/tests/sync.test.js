import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadCore, loadAdapter, render } from '../src/render.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const norm = (s) => s.replace(/\r\n/g, '\n');

test('committed Claude files match render(core, claude)', () => {
  const files = render(ROOT, loadCore(ROOT), loadAdapter(ROOT, 'claude'));
  for (const f of files) {
    if (f.path.startsWith('skills/')) continue; // skills are the source, not rendered artifacts
    const onDisk = fs.readFileSync(path.join(ROOT, f.path), 'utf8');
    assert.equal(norm(onDisk), norm(f.content), `${f.path} is out of sync with core — run: npm run build`);
  }
});
