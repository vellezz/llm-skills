---
name: project-readme
description: >-
  Generate or refresh README files and developer onboarding guides for
  .NET and Angular repositories: setup instructions, prerequisites,
  how to run/test/build, project structure overview. Use whenever the user
  asks for a README, onboarding doc, "getting started" guide, contributor
  guide, or says a new developer needs to understand the repo — including
  phrases like "readme", "onboarding", "jak uruchomić projekt",
  "dokumentacja dla nowego developera".
---

# README & Onboarding Generator

## Procedure

1. **Extract facts — never assume:**
   - .NET: target framework from `.csproj` (`<TargetFramework>`), required
     SDK from `global.json` if present, startup project(s), `launchSettings.json`
     ports/profiles, EF Core migrations (does `dotnet ef database update` apply?),
     required services from `docker-compose.yml` / connection strings /
     `appsettings.Development.json`.
   - Angular: Node version (`engines` in `package.json`, `.nvmrc`), package
     manager (lockfile: npm/yarn/pnpm), real scripts from `package.json`
     (`start`, `build`, `test`, `lint`), proxy config (`proxy.conf.json`),
     environment files.
   - Both: CI workflow files reveal the authoritative build/test commands —
     read `.github/workflows/*` and mirror what CI actually runs.
2. **Verify commands when possible.** If you have shell access, dry-check
   commands exist (`dotnet --list-sdks`, script names in package.json).
   A README with a broken `npm start` is worse than no README.
3. **Render from `templates/readme.md`.** Cut sections that don't apply —
   an empty "Deployment" heading is noise.
4. **When updating an existing README:** preserve badges, license, and any
   hand-written prose; refresh only factual sections (setup, commands,
   structure) and say what you changed.

## Multi-repo workspaces

When the target directory is a workspace parent holding several repositories,
generate a **workspace README** instead: one short paragraph per repo (what it
is + link to its own README), the cross-repo run order (what must be running
first), and shared prerequisites. Do not duplicate per-repo setup steps.

## Rules

- Every command in the README must be copy-pasteable and in the right order
  (clone → prerequisites → restore → configure → run).
- Document secrets by *name and where to get them*, never by value.
- Project structure section: max 15 lines of tree, annotate only
  non-obvious directories.
- Keep it under ~150 lines; link out to `docs/` for depth.
- Deliverable is the `README.md` file. Final chat message: 1–3 sentences on
  what was written or changed — never paste the README into chat.
- **Language:** honor an explicit language request in the arguments
  (`lang:pl`, "po polsku", …); when refreshing an existing README, keep its
  current language unless asked otherwise. Shell commands, paths, and config
  keys are never translated.
