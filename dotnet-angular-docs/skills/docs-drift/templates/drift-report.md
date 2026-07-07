# Documentation drift report

> Generated {YYYY-MM-DD} against `{branch}@{short-sha}`. Code is the source
> of truth. This report is a snapshot — regenerate rather than edit.

## Summary

| Class | Count |
|---|---|
| STALE | {n} |
| ORPHANED | {n} |
| MISSING | {n} |
| UNVERIFIED | {n} |

**Verdict:** {✅ Docs in sync | ⚠ Drift detected}

## Findings

### {CLASS} · {short title}

- **Doc:** {quote or claim} — `{docs/api/orders.md}` ({section/line})
- **Code:** {current fact} — `{src/Api/OrdersController.cs:57}`
- **Fix:** {regenerate `docgen:<section>` via `{skill}` | manual edit | add missing doc}

---

## Suggested actions

**Auto-fixable** (inside `docgen` markers — say "fix drift" to apply):
1. {…}

**Manual follow-ups** (hand-written sections — needs a human decision):
1. {…}
