# {Project name}

{One–two sentences: what it is and who it's for.}

## Tech stack

- Backend: .NET {ver} / ASP.NET Core {style}
- Frontend: Angular {ver} ({standalone components / NgModules})
- Database: {…}
- {other verified infrastructure}

## Prerequisites

- .NET SDK {ver} — pinned in `global.json` *(if applicable)*
- Node.js {ver} + {npm/yarn/pnpm}
- {Docker, if compose is required}

## Getting started

```bash
# 1. Clone
git clone {url}

# 2. Infrastructure (if applicable)
docker compose up -d

# 3. Backend
cd src/{Api}
dotnet restore
dotnet ef database update        # only if migrations exist
dotnet run                       # → https://localhost:{port from launchSettings}

# 4. Frontend
cd src/{web}
{npm|pnpm|yarn} install
{npm|pnpm|yarn} start            # → http://localhost:4200
```

## Configuration

| Setting | Where | Notes |
|---|---|---|
| `ConnectionStrings:Default` | user-secrets / env | {…} |

## Testing

```bash
dotnet test
{npm} test
```

## Project structure

```
src/
├── {Api}/          # {…}
├── {Domain}/       # {…}
└── {web}/          # Angular app
```

## Further documentation

- [API docs](docs/api/index.md)
- [Architecture](docs/architecture/)
- [ADRs](docs/adr/)
