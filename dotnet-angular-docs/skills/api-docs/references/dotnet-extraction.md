# .NET API extraction rules

## Route resolution
- Effective route = `[Route]` on class (replace `[controller]` token with class
  name minus "Controller") + method-level template.
- `[ApiVersion]` / `Asp.Versioning`: include version segment; document each
  version separately if behavior differs.
- Minimal APIs: resolve `MapGroup` prefixes recursively; follow extension
  methods (`app.MapUserEndpoints()`) into their definitions.

## Parameter binding
| Source | How to detect | Document as |
|---|---|---|
| Route | `{id}` in template, `[FromRoute]` | Path parameter |
| Query | Simple types without attribute, `[FromQuery]` | Query parameter |
| Body | Complex types, `[FromBody]` | Request body (JSON) |
| Header | `[FromHeader]` | Header |
| Form | `[FromForm]`, `IFormFile` | multipart/form-data |

## Type mapping (C# → JSON)
`int/long` → integer · `decimal/double` → number · `bool` → boolean ·
`string/Guid/DateTime/DateOnly` → string (note format: `uuid`, `date-time`, `date`) ·
`IEnumerable<T>/List<T>/T[]` → array · nullable (`?`) → optional/nullable ·
`enum` → string, list allowed values (check `JsonStringEnumConverter`).

Respect `System.Text.Json` naming policy from `Program.cs`
(default camelCase in ASP.NET Core) and `[JsonPropertyName]` overrides.

## Status codes
- Prefer `[ProducesResponseType]` attributes.
- Otherwise infer: `Ok(...)` → 200, `Created/CreatedAtAction` → 201,
  `NoContent()` → 204, `BadRequest` → 400, `NotFound` → 404,
  `Unauthorized` → 401, `Forbid` → 403, `Conflict` → 409,
  `ValidationProblem` → 400 (ProblemDetails).
- Check global exception middleware / `ProblemDetails` configuration and
  document the error response shape once, in the index file, not per endpoint.

## Auth
- Class-level `[Authorize]` applies to all actions unless `[AllowAnonymous]`.
- Document policy names and roles; look up policy definitions in
  `AddAuthorization(...)` to describe what they actually require.
