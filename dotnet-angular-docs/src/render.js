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

function walk(dir) {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...walk(full));
    else out.push(full);
  }
  return out;
}

export function renderSkills(root, adapter) {
  const skillsRoot = path.join(root, 'skills');
  return walk(skillsRoot).map((full) => {
    const rel = path.relative(skillsRoot, full).split(path.sep).join('/');
    return { path: `${adapter.skills.copy_to}/${rel}`, content: fs.readFileSync(full, 'utf8') };
  });
}

export function checkInvariants(core, names) {
  const skills = new Set(names);
  for (const c of core.commands) {
    if (skills.has(c.name)) throw new Error(`command "${c.name}" would shadow the same-named skill`);
    if (!skills.has(c.skill)) throw new Error(`command "${c.name}" targets missing skill "${c.skill}"`);
  }
}

export function renderInstructions(core, adapter) {
  if (!adapter.instructions || !adapter.instructions.path) return null;
  const content = `<!-- docgen:begin:instructions -->\n${core.instructions.trim()}\n<!-- docgen:end:instructions -->\n`;
  return { path: adapter.instructions.path, content };
}

export function render(root, core, adapter) {
  checkInvariants(core, skillNames(root));
  const files = [renderPersona(core, adapter), ...renderCommands(core, adapter), ...renderSkills(root, adapter)];
  const instr = renderInstructions(core, adapter);
  if (instr) files.push(instr);
  return files;
}
