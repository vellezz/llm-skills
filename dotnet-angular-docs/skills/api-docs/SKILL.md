---
name: api-docs
description: >-
  Generate REST API documentation from .NET source code (ASP.NET Core
  controllers, minimal APIs) and document Angular API client services.
  Use this skill whenever the user asks to document an API, endpoints,
  controllers, generate OpenAPI/Swagger descriptions, describe request/response
  contracts, or mentions "API docs", "dokumentacja API", "endpointy",
  "swagger", "kontrakt" — even if they don't say "documentation" explicitly.
---

# API Documentation Generator

Produce endpoint-level API documentation grounded in actual source code.

## Procedure

1. **Locate the API surface.**
   - Controllers: classes inheriting `ControllerBase`/`Controller`, attributes
     `[Route]`, `[HttpGet]`, `[HttpPost]`, etc.
   - Minimal APIs: `app.MapGet/MapPost/MapPut/MapDelete/MapGroup` calls in
     `Program.cs` or extension methods.
   - If Swashbuckle/NSwag config exists, read it — respect existing groupings,
     versioning (`Asp.Versioning`), and `[ProducesResponseType]` metadata.
2. **Read the extraction rules** in `references/dotnet-extraction.md` for how
   to derive routes, parameter binding, status codes, and auth requirements.
3. **For each endpoint, resolve the full contract:**
   - Route (including route prefixes and API versioning), HTTP method.
   - Request: route/query/body parameters with C# types mapped to JSON types.
     Expand DTOs one level deep; link nested types instead of inlining them.
   - Response: each documented status code with body type. If no
     `ProducesResponseType`, infer from return type and mark `> ⚠ Inferred`.
   - Auth: `[Authorize]` policies/roles, `[AllowAnonymous]`.
4. **Angular side (if requested or if an Angular app consumes this API):**
   read `references/angular-client.md` and cross-reference which Angular
   services call each endpoint — include a "Consumed by" line.
5. **Render using `templates/api-docs.md`.** One file per controller/feature
   group; an `index.md` with a table of all groups.

## Repo configuration (`docs/.docgen/`)

- `config.yml` keys under `api-docs`: `exclude-routes` (glob list — skip and
  note them in `index.md` as "Omitted routes"), `consumed-by` (bool),
  `examples` (bool), `output` (path). Top-level `lang` applies too.
- `docs/.docgen/templates/api-docs.md`, if present, replaces the plugin
  template.
- Config is always optional and adjusts scope/shape only — it can never
  disable grounding or the endpoint-header/marker contracts. Never fail on a
  missing or partially unknown config; ignore unknown keys.

## Multi-repo workspaces

- The Angular client may live in a sibling repository. Accept a `repos:`
  argument (e.g. `repos:../shop-frontend,../shop-admin`) or repo paths named
  in the request, and read those trees for the cross-reference step.
- If the frontend repository is NOT available in the workspace, still document
  the API fully, but mark the cross-ref explicitly:
  `**Consumed by:** ⚠ Unverified — frontend repository not in workspace`.
  Never guess consumers.

## Output contract (strict — tools parse this format)

- Files: `docs/api/<feature>.md`, one per controller/feature group, plus
  `docs/api/index.md` with a table of all groups.
- Every endpoint section starts with a header in EXACTLY this form:

  ```
  ### METHOD /route/path
  ```

  Uppercase method, single space, literal route with `{param}` placeholders.
  No backticks, bold, or words in that header line. Do not use prose titles
  (`#### Create Payment`) with the route on a separate line.
- Wrap the generated endpoint sections in idempotency markers:
  `<!-- docgen:begin:endpoints -->` … `<!-- docgen:end:endpoints -->`.
  When updating an existing file, regenerate only inside the markers and
  preserve everything outside them byte-for-byte.
- Final chat message: one short paragraph — which files were written and how
  many endpoints documented. Never paste the docs into chat.

## Rules

- Never invent endpoints, parameters, or status codes. Verify each in code.
- Use realistic example payloads derived from the DTO property types and
  validation attributes (`[Required]`, `[MaxLength]`, `[Range]`).
- Keep descriptions one to two sentences per endpoint; contracts carry the detail.
- If XML doc comments (`///<summary>`) exist, use them as the description source.
- **Language:** honor an explicit language request in the arguments
  (`lang:pl`, "po polsku", …); default per the docs-writer language rule.
  Localize prose and table descriptions only — endpoint headers
  (`### METHOD /route`), JSON examples, type names, and docgen markers stay
  untouched.

## Before finishing, verify

1. Every documented route exists in code (grep it).
2. Every endpoint header matches `### METHOD /route` exactly.
3. `docs/api/index.md` lists every generated file.
4. Markers are present and balanced in every file.
