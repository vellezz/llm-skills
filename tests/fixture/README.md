# Fixture Shop

Sample order-management app. Used as a test fixture for the
dotnet-angular-docs plugin — the content below is a known-good baseline.

## Tech stack

- Backend: .NET 8 / ASP.NET Core (controllers)
- Frontend: Angular 17 (standalone components)
- Database: PostgreSQL

## Getting started

```bash
docker compose up -d
cd src/Api
dotnet run
cd ../web
npm install
npm start
```
