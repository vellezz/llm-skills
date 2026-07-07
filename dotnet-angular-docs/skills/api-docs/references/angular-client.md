# Angular API client cross-referencing

## Locating API calls
- Services with `HttpClient` injected (`inject(HttpClient)` or constructor).
- Calls: `http.get/post/put/patch/delete<T>(url, ...)`.
- Resolve URL bases from: `environment.ts` (`apiUrl` etc.), interceptors that
  prepend base URLs, injection tokens, or generated clients (NSwag/openapi-generator
  output — if a generated client exists, document the generator source instead
  of hand-tracing calls).

## What to record per endpoint
- Service class + method name that calls it (e.g. `UserService.getById()`).
- The TypeScript interface used as the response type — flag mismatches with
  the C# DTO (missing/extra fields, nullability differences) in a
  "⚠ Contract drift" note. This is high-value output; check it carefully.

## Signals of consumption patterns worth documenting
- Interceptors adding auth headers → note in the Auth section of the index.
- Retry/error-handling operators (`retry`, `catchError`) that change
  effective behavior for consumers.
