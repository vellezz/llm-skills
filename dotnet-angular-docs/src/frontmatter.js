import yaml from 'js-yaml';

const FM_RE = /^---\n([\s\S]*?)\n---\n?([\s\S]*)$/;

export function splitFrontmatter(text) {
  const normalized = text.replace(/\r\n/g, '\n');
  const m = FM_RE.exec(normalized);
  if (!m) return { data: {}, body: normalized };
  return { data: yaml.load(m[1]) || {}, body: m[2] };
}

export function stringify({ data, body }) {
  const fm = yaml.dump(data, { lineWidth: -1 }).trimEnd();
  return `---\n${fm}\n---\n\n${body.replace(/^\n+/, '')}`;
}
