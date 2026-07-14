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

export function renderCommands(core, adapter) {
  return core.commands.map((c) => {
    const ref = adapter.persona.command_skill_ref.replace('{skill}', c.skill);
    const data = {
      description: c.description,
      'argument-hint': c['argument-hint'],
      ...adapter.commands.frontmatter,
    };
    const body = [
      `REQUIRED FIRST STEP: ${ref} and follow its procedure and output contract`,
      `exactly. Do not document from this summary alone.`,
      ``,
      `Key contract: ${c['contract-summary']}`,
      ``,
      `Scope: ${adapter.commands.arg_token} (if empty, use the skill's default`,
      `scope — ask first when the workspace contains more than ~20 projects).`,
    ].join('\n');
    return { path: `${adapter.commands.dir}/${c.name}${adapter.commands.ext}`, content: stringify({ data, body }) };
  });
}
