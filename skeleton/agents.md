# Vault Schema

The contract for any agent working in this vault. Read this, then work. Based on Andrej Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern.

## What this is

A knowledge base that **compounds**. Instead of re-reading raw documents on every question (RAG), each new source is compiled into an interlinked markdown wiki once, and kept current. The wiki is the artifact; chat history is not.

The human curates sources, directs the work and asks the questions. The agent does the bookkeeping.

## Layout

```
raw/           Immutable source material. Read only.
raw/assets/    Images and attachments.
wiki/          Agent-owned markdown. index.md and log.md live here.
agents.md      This file — the universal schema.
zeroclaw.md    Agent-specific overlay, if one exists.
```

Three layers only: **raw** (source of truth, never modified), **wiki** (agent owns it entirely), **schema** (this file).

Deeper structure is deliberately absent. Add a folder only when page count forces it, and record the reason in the log.

## Hard rules

1. **Never modify `raw/`.** No edits, renames or deletions. If a source is wrong, say so on a wiki page.
2. **Read `wiki/index.md` first** on any query, then open the pages it names. Do not grep the whole vault before trying the index.
3. **Every write ends in a log entry.** One line, at the time of the write.
4. **Extend, don't create.** Search the index and existing pages before making a new one. Near-duplicate pages are the most common failure mode.
5. **Rewrite summaries, don't append to them.** Appending turns a summary into an incoherent changelog.
6. **Never silently overwrite.** If new information contradicts a page, keep both claims, attribute each to its source, and flag the conflict.
7. **Cite raw sources.** Any claim traceable to a source names that source.
8. **Say so when you don't know.** A gap documented as a gap is useful; an invented bridge is not.

## Operations

### ingest

Process one source from `raw/` into the wiki.

1. Read the source. If the takeaways are unclear, discuss them before writing.
2. Search `wiki/` for existing pages this touches — usually more than you expect.
3. Write or update a summary page in `wiki/`, `type: source`.
4. Update the entity and concept pages it changes. One source commonly touches 5–15 pages.
5. Note contradictions with existing claims explicitly.
6. Add one line to the Sources section of `index.md`.
7. Append a log entry.

Ingest one source at a time where possible. Batch only for bulk imports.

### query

Answer from the wiki.

1. Read `index.md`. Identify candidate pages.
2. Open them. Follow `[[wikilinks]]` outward as far as the question needs.
3. Answer with citations to the pages used.
4. **File good answers back.** A comparison, an analysis, a discovered connection is knowledge — write it to `wiki/` as `type: synthesis`, index it, log it. Do not let it die in chat.

If the wiki cannot answer, say what is missing and what source would fill it. That is a useful output.

### lint

Health-check the wiki. Run on request, not on every session.

Look for: contradictions between pages · stale claims superseded by newer sources · orphan pages with no inbound wikilinks · concepts mentioned repeatedly but lacking a page · missing cross-references · gaps worth filling with a web search.

Report findings. Fix the mechanical ones (broken links, orphans); propose the judgement calls rather than making them silently.

## Page format

YAML frontmatter, then a title, then content:

```yaml
---
type: entity | concept | source | synthesis | note
created: 2026-10-21
updated: 2026-10-21
sources: ["raw/articles/example.md"]
tags: [topic]
---
```

`type` is required. `created` and `updated` are required on creation and update respectively. `sources` and `tags` are optional. No other keys are mandatory — do not invent a schema for the sake of it.

- Cross-reference with `[[Page Name]]`. Link generously; Obsidian's graph view is the health check.
- Filenames are `Title Case With Spaces.md`, matching the page title.
- Avoid `[ ] { } | # ^` in filenames — they break wikilinks and aliasing.
- Frontmatter must be valid YAML or Dataview queries silently fail.

## index.md

A **table of contents**, not a database. For each page: a link, a one-line summary, grouped under a category heading (Entities, Concepts, Sources, Synthesis, Working notes). Categories in the index are sections — they are not directories.

The index is the retrieval mechanism until the vault reaches roughly 100 sources or several hundred pages. Past that, add search (see Scale) instead of making the index longer.

## log.md

Append-only, newest at the bottom.

```
## [2026-10-21] ingest | Article Title
- one or two lines on what changed
```

Verbs: `ingest`, `query`, `lint`, `update`, `decision`, `setup`.

A consistent prefix keeps the log parseable with plain unix tools:

```bash
grep "^## \[" wiki/log.md | tail -5
```

## tasks.md

`wiki/tasks.md` is the shared work queue between the human and every agent. It is the one place actionable work lives, so that nothing is duplicated or silently dropped.

It is **state**, not a view: one checkbox line per task, each self-describing.

```
- [ ] Short imperative #owner/x ➕ 2026-10-21 📅 2026-10-28 [[Related Page]]
- [x] Finished thing #owner/clawz ➕ 2026-10-20 ✅ 2026-10-21
```

Rules:

- **Claim before starting.** Replace `#owner/any` with `#owner/<you>` in a single edit, then work.
- **Never touch `#owner/human`.** Surface it; do not do it unasked.
- **Never delete a task line.** Complete it in place (`[x]` plus `✅ date`) or move it to Dropped. Completion is history, not cleanup.
- **Append, don't rewrite.** Add lines at the bottom of Open; replace one line to claim or complete. Whole-file rewrites race with other agents.
- **One task per line, no nesting.** Nested checklists cannot be claimed unambiguously.
- **Link the page a task concerns** once that page exists. A task floating free of the graph is a task nobody can act on later.

Tasks do not belong in a second freeform document. A prose todo list has no owner, no claim state and no completion history, and it loses entries to whichever agent wrote last.

Task completion is not a log entry on its own — the `✅` date is the record. Log it only when completing tasks was part of a larger operation.

## Concurrency

Several agents may share this vault. There are no locks and no coordinator.

- Check `tail` of `log.md` before editing a shared page, to see who touched it last.
- Keep writes small and attributable. Prefer editing one page over rewriting five.
- Log-first, last-write-wins. If you and another agent both edited a page, the log tells you what happened — reconcile from there.
- The vault is a git repo. Commit or branch if you need real isolation.

## Scale

The index works well to ~100 sources. Beyond that, add real search rather than piling onto the index — a local markdown search tool, or a small script. Do not build it before the pain is felt.

## Maintenance tooling

One piece of code is planned, and only when the need is felt: a linter for the mechanical checks that burn context when done by reading — broken wikilinks, malformed frontmatter, orphans, duplicate slugs. Structure checks are deterministic and belong in a script. Contradiction and staleness checks are judgement and do not.
