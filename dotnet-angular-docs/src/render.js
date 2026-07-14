import fs from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';
import { splitFrontmatter, stringify } from './frontmatter.js';

export function loadCore(root) {
  const persona = splitFrontmatter(fs.readFileSync(path.join(root, 'core/persona.md'), 'utf8'));
  const commands = yaml.load(fs.readFileSync(path.join(root, 'core/commands.yml'), 'utf8'));
  const instructions = fs.readFileSync(path.join(root, 'core/instructions.md'), 'utf8');
  return { persona, commands, instructions };
}

export function loadAdapter(root, name) {
  return yaml.load(fs.readFileSync(path.join(root, `adapters/${name}.yml`), 'utf8'));
}

export function skillNames(root) {
  const dir = path.join(root, 'skills');
  return fs.readdirSync(dir, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name);
}

export function renderPersona(core, adapter) {
  const body = core.persona.body.replaceAll('{{skill_invocation}}', adapter.persona.skill_invocation);
  const data = { ...core.persona.data, ...adapter.persona.frontmatter };
  return { path: adapter.persona.path, content: stringify({ data, body }) };
}
