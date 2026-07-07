---
name: user-manual
description: >-
  Generate end-user documentation (user manuals, feature guides, how-to
  instructions) for Angular applications by analyzing routes, components,
  forms, and guards. Use whenever the user asks for a user manual, help
  content, feature description for non-technical readers, instructions for
  end users, or mentions "manual", "instrukcja", "podręcznik użytkownika",
  "dokumentacja dla użytkownika", "help page" — the audience is NOT developers.
---

# User Manual Generator

Audience: end users. No code, no class names, no HTTP verbs in the output.

## Procedure

1. **Map user-facing features from the Angular app:**
   - Routes (`app.routes.ts` / routing modules) → the app's screens.
     Route guards (`canActivate`) → who can access what (roles/permissions).
   - Per screen: page title, forms (`FormGroup`/`FormControl` names +
     validators → required fields and their constraints in human terms),
     primary actions (buttons calling service methods), tables/lists and
     their filters.
   - i18n files (`assets/i18n/*.json`, `$localize`) are the authoritative
     source for UI wording — use the exact labels users see on screen.
2. **Translate validation to user language.** `Validators.required` →
   "This field is required." `maxLength(50)` → "Maximum 50 characters."
   Custom validators: read their implementation and describe the rule,
   not the code.
3. **Structure with `templates/feature-guide.md`** — one file per feature
   area (usually per top-level route), plus an index/table of contents.
4. **Flag what you can't know from code:** business context, screenshots,
   and "why" explanations need human input — insert
   `<!-- TODO: add screenshot of {screen} -->` placeholders rather than
   inventing descriptions.

## Repo configuration (`docs/.docgen/`)

Optional `config.yml` keys under `user-manual`: `locales` (which i18n locales
to generate manuals for). `docs/.docgen/templates/feature-guide.md` replaces
the plugin template. Ignore unknown keys; never fail on config.

## Rules

- Write in second person, imperative: "Click **Save**", "Enter the order number".
- Bold exact UI labels as they appear (from templates/i18n), in the app's language.
- Describe error states users can actually hit (validation messages,
  guard redirects), not internal exceptions.
- Steps must follow the real screen flow — verify navigation order against
  router calls (`router.navigate`) before writing "Next, go to…".
- Output path: `docs/user-guide/<feature>.md`. Deliverables are the files.
  Final chat message: 1–3 sentences listing the files written — never paste
  the guides into chat.
- **Language:** the manual's language must match the locale whose i18n labels
  it quotes. If the app ships multiple locales (`assets/i18n/*.json`) and the
  arguments name one (`lang:pl`), use that locale's file for every quoted
  label; if none is named, use the app's default locale and say which one
  you chose.
