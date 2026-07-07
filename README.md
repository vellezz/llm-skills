# llm-skills

A collection of LLM agent skills and plugins. Each top-level directory is a
self-contained project: the skill/plugin itself plus its own tests and tooling.

| Project | What it does |
|---|---|
| [`dotnet-angular-docs/`](dotnet-angular-docs/) | Documentation generator for .NET + Angular projects: API docs, architecture (C4/Mermaid), README, user manuals, changelog, EF Core data model, drift audit, custom documents from free-text specs, multi-agent suite orchestration, and GitHub Pages publishing. Per-repo customization via `docs/.docgen/` (config, template overrides, custom specs). Multi-repo aware. Includes a behavioral test harness with a deterministic API-surface extractor. |

## Layout convention

```
<project>/
├── skills/ commands/ agents/ …   # the plugin/skill content
├── tests/                        # its behavioral test harness
└── scripts/                      # its validation tooling
```

CI workflows live in `.github/workflows/` prefixed with the project name and
scoped to its paths.
