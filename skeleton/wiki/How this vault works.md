---
type: concept
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [vault, meta]
---

# How this vault works

The vault is shared memory between you and every agent you run. The machine-facing contract is `AGENTS.md` at the vault root; this page is the human version.

## The idea

An agent that reads a source, answers, and forgets wastes the work. Instead each source is compiled once into linked markdown and kept current. The vault compounds. Chat history doesn't.

See [[LLM Wiki pattern]] for where this comes from.

## Where things go

```
raw/                          sources. Never edited.
wiki/index.md                 one line per project, pointing at its index
wiki/<project>/index.md       that project's pages
wiki/<project>/progress/      01_, 02_, 03_ ... one file per session
wiki/<project>/*.md           the project's pages
AGENTS.md                     the rules
```

Two index levels, because one index shared by everything is either enormous or ambiguous. Root stays small forever — it only learns about new projects.

Folders appear when work does. An empty vault with no project folders is a vault that hasn't been used yet, not one that is missing something.

## Three things agents do

**Ingest** a source from `raw/` — write it up, update every page it touches, add it to the project index, log one line.

**Query** — root index, project index, the page. Answer with citations. Good answers get filed back as pages, so the next question starts ahead.

**Lint** — broken links, bad frontmatter, orphans, pages missing from an index. A script, not a reading exercise.

## The files worth understanding

[[index]] lists projects. It is append-only and a pointer list; if it ever gets long, something is being filed in the wrong place.

`wiki/<project>/index.md` lists that project's pages. Titles and summaries have to be factual — "decisions and open questions", not "notes" — or an agent can't tell whether to open them.

`progress/` holds one file per session, numbered, never edited afterwards. Reading the highest number tells you where the work is. There is no status doc to keep current, which is why it can't go stale.

[[log]] is an audit trail: what was written, where. It never holds the content itself — a second copy of the wiki would drift from the first.

[[tasks]] is the queue. `#owner/any` is unclaimed, `#owner/<agent>` is that agent's, `#owner/human` is yours. Completed tasks stay, dated.

## The rules that matter

- `raw/` is immutable. If a source is wrong, say so in `wiki/`.
- Read the indexes before searching the vault.
- Extend a page rather than making a near-duplicate.
- Never silently overwrite a contradiction — keep both claims, attribute them.
- Every write ends with a log line.
- Records are appended to, never rewritten. That covers the log, `progress/` and completed tasks.

The rest is in `AGENTS.md`.
