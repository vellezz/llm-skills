import { test } from 'node:test';
import assert from 'node:assert/strict';
import { splitFrontmatter, stringify } from '../src/frontmatter.js';

test('splitFrontmatter parses data and body', () => {
  const { data, body } = splitFrontmatter('---\nname: x\n---\nHello world');
  assert.equal(data.name, 'x');
  assert.equal(body.trim(), 'Hello world');
});

test('splitFrontmatter returns empty data when no frontmatter', () => {
  const { data, body } = splitFrontmatter('Just body');
  assert.deepEqual(data, {});
  assert.equal(body, 'Just body');
});

test('stringify round-trips through splitFrontmatter', () => {
  const out = stringify({ data: { name: 'x', tools: ['a', 'b'] }, body: 'Body here' });
  const { data, body } = splitFrontmatter(out);
  assert.equal(data.name, 'x');
  assert.deepEqual(data.tools, ['a', 'b']);
  assert.equal(body.trim(), 'Body here');
});
