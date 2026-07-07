# {Feature name} API

> Source: `{path/to/Controller.cs}` · Auth: {default auth requirement}

{One-paragraph summary of what this API group does.}

## Endpoints

<!-- docgen:begin:endpoints -->
<!-- Endpoint headers are a parsing contract: exactly `### METHOD /route`
     (uppercase method, one space, literal route). Keep this format. -->

### {METHOD} {/route/path}

{One–two sentence description (from XML docs if present).}

**Auth:** {policy/roles or "Anonymous"}

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| {id} | path | string (uuid) | yes | {…} |

**Request body** *(if applicable)*

```json
{ "example": "derived from DTO" }
```

**Responses**

| Status | Body | When |
|---|---|---|
| 200 | `{DtoName}` | {…} |
| 404 | `ProblemDetails` | {…} |

**Consumed by:** `{AngularService.method()}` *(if Angular cross-ref enabled)*

---

<!-- docgen:end:endpoints -->
