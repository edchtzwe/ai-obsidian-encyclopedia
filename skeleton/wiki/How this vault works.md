---
type: concept
created: 2026-10-22
updated: 2026-10-22
tags: [vault, meta]
---

# How this vault works

The vault is the shared memory between you and every agent you run. The full machine-facing contract is `agents.md` at the vault root; this page is the human version.

## The idea

An agent reading a source, answering, and forgetting wastes the work. Instead, each source is compiled once into linked markdown, and kept current. The vault compounds. Chat history doesn't.

See [[LLM Wiki pattern]] for where this comes from.

## Where things go

```
raw/     Sources. Never edited. Delete nothing.
wiki/    The knowledge. Written by agents, read by you.
agents.md  The rules.
```

That's it. No folders for concepts, entities or sources — `index.md` groups pages by category instead. Structure gets added when page count demands it, not before.

## Three things agents do

**Ingest** a source from `raw/` — summarise it, update every page it touches, index it, log it.

**Query** — read `index.md`, open what it points to, answer with citations. Good answers get filed back as pages, so the next question starts ahead.

**Lint** — find contradictions, stale claims, orphans, gaps. Run on request.

## Two files worth understanding

[[index]] is a table of contents. Every page, one line each, grouped by kind. Agents read it first on any question. It works to roughly 100 sources; past that, search replaces it rather than a longer index.

[[log]] is append-only. `grep "^## \[" wiki/log.md | tail -5` tells any agent what happened recently, including what another agent just did.

[[tasks]] is the work queue. `#owner/any` is unclaimed, `#owner/clawz` is mine, `#owner/human` is yours. Completed tasks stay, dated.

## The rules that matter

- `raw/` is immutable. If a source is wrong, say so in `wiki/`, don't fix it in place.
- Read the index before searching the vault.
- Extend an existing page rather than making a near-duplicate.
- Never silently overwrite a contradiction — keep both claims and attribute them.
- Every write ends with a log line.

The rest is in `agents.md`.
