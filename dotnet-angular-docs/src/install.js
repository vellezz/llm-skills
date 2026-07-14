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

export function writeFile(abs, content, force) {
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  const isInstructions = abs.endsWith('copilot-instructions.md');
  if (fs.existsSync(abs) && !force && !isInstructions) {
    return fs.readFileSync(abs, 'utf8') === content ? 'skip' : 'differs';
  }
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
      const rel = path.relative(targetRoot, f.abs);
      if (action === 'differs') console.warn(`differs (kept; re-run that single platform with --force to overwrite): ${rel}`);
      else console.log(`${action}: ${rel}`);
    }
  }
}

function isMainModule() {
  if (!process.argv[1]) return false;
  try {
    return fs.realpathSync(process.argv[1]) === fileURLToPath(import.meta.url);
  } catch {
    return false;
  }
}

if (isMainModule()) {
  main();
}
