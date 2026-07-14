# Documentation grounding rules

These rules apply to all documentation work in this repository.

- Ground every statement in the actual source code. Never document an
  endpoint, component, config value, or behavior you have not located in
  the source; mark anything unverifiable as `> ⚠ Unverified`.
- Output is Markdown; diagrams are Mermaid (never ASCII art or image links).
- Preserve hand-written sections. Only regenerate content between
  `<!-- docgen:begin:<section> -->` / `<!-- docgen:end:<section> -->` markers.
- Never invent endpoints, commands, or behavior. Never print secret values.
