---
type: source
created: 2026-10-22
updated: 2026-10-22
sources: ["https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f"]
tags: [llm-wiki, knowledge-management, karpathy]
---

# LLM Wiki pattern

Summary of Karpathy's "LLM Wiki" idea file. Full text: <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f> — not vendored here, read it at the source.

## The argument

RAG re-derives knowledge on every question. You upload documents, the model retrieves chunks, answers, and forgets. Ask something requiring five documents and it reassembles the fragments from scratch every time. Nothing accumulates.

The alternative: compile sources into a **persistent interlinked wiki** once, and keep it current. Each new source updates entity pages, revises summaries, and flags contradictions with what came before. The wiki is the artifact, not the chat log.

> "Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."

The human curates sources, directs analysis, and asks the questions. The LLM does the bookkeeping — and bookkeeping is precisely why human-maintained wikis rot.

## Three layers

| Layer | Owner | Rule |
| :--- | :--- | :--- |
| Raw sources | Human | Immutable. Read, never modify. Source of truth. |
| Wiki | LLM | Created and maintained entirely by the agent. |
| Schema | Both | The contract that makes the agent a disciplined maintainer rather than a chatbot. |

## Three operations

- **Ingest** — process one source into the wiki. Commonly touches 10–15 pages.
- **Query** — answer from the wiki with citations. Good answers get filed back as pages.
- **Lint** — find contradictions, stale claims, orphans, missing pages, broken cross-references.

## The two special files

`index.md` is a **table of contents**: link, one-line summary, grouped by category, updated on every ingest, read first on any query. Explicitly noted as sufficient to ~100 sources and hundreds of pages without any embedding infrastructure.

`log.md` is **chronological and append-only**. A fixed prefix (`## [2026-04-02] ingest | Title`) makes it greppable, which is the whole point.

## What this vault took

The three layers, the three operations, the index-as-catalog, the append-only log, and the rule that raw is immutable.

One adaptation: the catalog is split in two. `wiki/index.md` lists projects only, and each `wiki/<project>/index.md` lists that project's pages. Same idea, so the file read first stays small no matter how much is written.

## What this vault rejected

- **The prescribed directory structure** — there isn't one. The gist says explicitly that structure, conventions and tooling are domain-specific and "optional and modular." Our earlier 27-folder tree was invention, not pattern.
- **Tooling up front** — search engines and scripted helpers are explicitly optional and should arrive when the index stops scaling.
- **The plugin stack** — Marp, Dataview and web clipper are all optional conveniences. Deferred.
