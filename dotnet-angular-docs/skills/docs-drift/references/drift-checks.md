# Drift checks by document type

Run only the sections for doc types that actually exist in the repo.

## API docs (`docs/api/*.md`)
- Every documented endpoint (METHOD + route) still resolves to a controller
  action or `Map*` call. Gone → ORPHANED.
- Route, verb, parameters, request/response types, and status codes match
  a fresh extraction (per `api-docs` rules). Mismatch → STALE.
- Endpoints found in code but absent from docs → MISSING.
- Auth: documented policy/roles vs current `[Authorize]` attributes.
- "Consumed by" lines: the Angular service method still exists and still
  calls that URL. If the frontend lives in a repo outside the workspace,
  classify these as UNVERIFIED (reason: repo not available), not as drift.

## README (`README.md`)
- Tech-stack versions vs `<TargetFramework>` in `.csproj` and
  `@angular/core` in `package.json`.
- Every shell command is still valid: npm scripts exist in `package.json`,
  `dotnet ef` steps only if migrations exist, ports match
  `launchSettings.json`, package manager matches the lockfile.
- Prerequisites vs `global.json`, `engines`, Docker compose files.
- Paths shown in the project-structure tree still exist on disk.

## User manual (`docs/user-guide/*.md`)
- Documented screens ↔ routes in `app.routes.ts` / routing modules.
- Bolded UI labels still exist verbatim in i18n files / templates.
- Field tables vs current `FormGroup` controls and validators.
- "Who can use it" claims vs current route guards.

## Architecture docs (`docs/architecture/`, `docs/adr/`)
- Diagram nodes ↔ projects in `.sln` / `angular.json`; edges ↔
  `ProjectReference` entries and HTTP/messaging registrations.
- External dependencies (DB, brokers, third-party APIs) still present in
  configuration / DI setup.
- ADRs are immutable — never flag their content as STALE. Flag only when
  current code contradicts an **Accepted** ADR, and suggest a superseding
  ADR instead of an edit.

## Changelog (`CHANGELOG.md`)
- Version headers ↔ git tags (missing tag or missing entry → finding).
- Commits since the last tag with no `[Unreleased]` coverage → MISSING
  (only user-visible changes; skip pure-internal commits).
