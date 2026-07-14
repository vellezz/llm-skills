import yaml from 'js-yaml';

const FM_RE = /^---\n([\s\S]*?)\n---\n?([\s\S]*)$/;

export function splitFrontmatter(text) {
  const m = FM_RE.exec(text);
  if (!m) return { data: {}, body: text };
  return { data: yaml.load(m[1]) || {}, body: m[2] };
}

export function stringify({ data, body }) {
  const fm = yaml.dump(data, { lineWidth: -1 }).trimEnd();
  return `---\n${fm}\n---\n\n${body.replace(/^\n+/, '')}`;
}
