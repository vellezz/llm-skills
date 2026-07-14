#!/usr/bin/env node
// Regenerate the committed Claude plugin files (agents/, commands/) from core/.
// Run this whenever core/ changes; tests/sync.test.js enforces they stay in sync.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadCore, loadAdapter, render } from './render.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const files = render(ROOT, loadCore(ROOT), loadAdapter(ROOT, 'claude'));
for (const f of files) {
  if (f.path.startsWith('skills/')) continue; // skills are source, not generated
  const abs = path.join(ROOT, f.path);
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  fs.writeFileSync(abs, f.content);
  console.log(`wrote ${f.path}`);
}
