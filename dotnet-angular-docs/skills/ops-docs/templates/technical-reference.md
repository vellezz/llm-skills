# {System name} — Technical Reference (Deployment & Operations)

> Generated from source analysis on {date}. Facts marked ⚠ are unverified.
> Audience: DevOps / administrators. Content describes the system AS IS.

<!-- docgen:begin:ops -->

## 1. System overview

**{Name}** — {1–2 sentences}.

| Component | Port | Framework (exact version) | API type | Source |
|---|---|---|---|---|
| **{Component}** | {port} | {framework x.y} | {REST/gRPC/—} | `{path}` |

## 2. Technical requirements

- Runtime: {framework + exact version per component}
- Databases: {type + version, per component}
- Broker/cache: {if used}
- Optional dependencies: {name — when needed}

## 3. Architecture

{Mermaid component diagram: components, databases, brokers, external
services, arrows labeled with protocol. Then one numbered Mermaid flow
per main path (sync request, async event).}

## 4. Data sources

| Component | Database | Connection-string key | Purpose |
|---|---|---|---|
| **{Component}** | `{db_name}` | `{Config:Key}` | {…} |

{Access patterns (ORM/queries), file-path resources, caching — described
verbally with the config keys involved.}

## 5. Communication and integrations

**API groups** (detail lives in `docs/api/`):

| Group | Path | Methods | Purpose |
|---|---|---|---|

**Health checks:**

| Endpoint | Component | Actually verifies |
|---|---|---|
| `{/health}` | {…} | {e.g. "process liveness only; no dependency checks"} |

**Message broker** *(if used)*:

| Config name | Section/key | Virtual host | Purpose |
|---|---|---|---|

Consumed queues/topics: `{queue}` — {what it processes}.

**External HTTP services:** {service — config key for its address, endpoints
used, requirements}.

## 6. Configuration

{Per environment: how configuration is loaded, as a numbered order of
sources (e.g. 1. appsettings, 2. env vars, 3. secrets) — words, not file
dumps.}

| Parameter | Section/key | Required | Default | Purpose |
|---|---|---|---|---|

**Secrets / CMDB variables:**

| App parameter | Variable name | Purpose |
|---|---|---|

Logging: {sinks, levels, where configured — verbally}.

## 7. Deployment

{Containers: image, build context, dependencies — described verbally.}

| Env variable | Purpose | Example shape |
|---|---|---|

**Kubernetes probes** *(if applicable)*: per component — endpoint, port,
initial delay, period, failure threshold, and what it actually verifies.

**Resources:** requests/limits per component (memory, CPU) — as configured.

**Network:**

| Component | Inbound | Outbound |
|---|---|---|

**Security:** {encryption requirements, secret management — AS IS}.

**Build/CI:** {how artifacts are built and shipped — as found in workflows}.

<!-- docgen:end:ops -->
