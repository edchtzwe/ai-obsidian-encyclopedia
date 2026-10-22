# ai-obsidian-encyclopedia

A convention for Obsidian vaults that LLM agents maintain.

Point your agent at this repo. It sets the vault up, then keeps it current: ingesting sources, linking pages, flagging contradictions, and leaving a trail you can audit.

## The problem

Every agent runtime has its own memory, and none of them share one. Run several agents and you get several knowledge bases, each forgetting what the others learned.

And the default alternative — RAG over a pile of documents — re-derives knowledge on every question. Nothing compounds. Ask something that needs five sources and the agent reassembles the fragments from scratch, every time.

The fix isn't more tooling. It's **agreement on what a vault looks like**, so that the files themselves are the shared memory.

## What this gives you

A vault with three layers:

| Layer | Who owns it | Rule |
| :--- | :--- | :--- |
| `raw/` | You | Sources. Immutable. Never edited by an agent. |
| `wiki/` | The agent | Interlinked markdown, rewritten and extended as knowledge arrives. |
| `agents.md` | Both | The schema — what a page is, where things go, what the operations do. |

Plus two files that make the whole thing navigable:

- **`wiki/index.md`** — a table of contents. Every page, one line each, grouped by kind. Agents read it first instead of grepping. Scales to ~100 sources before anything fancier is warranted.
- **`wiki/log.md`** — append-only. A fixed prefix makes it greppable, so any agent can see what happened recently, including what another agent just did.

## Why prose instead of a program

Every modern agent already reads, writes, searches and edits files. A Python library wrapping those operations would be a worse version of native tools, and it would rot.

What agents *don't* share is judgement: when to extend a page instead of creating a near-duplicate, how to keep an index honest, what to do when a new source contradicts an old claim. That's prose, and prose doesn't break on a version bump.

The single exception is deterministic bookkeeping — broken wikilinks, malformed frontmatter, orphan pages, duplicate slugs. That earns its keep as a script, because doing it by reading burns a context window for no judgement.

## Layout

```
skeleton/
├── agents.md              The schema. The only file that really matters.
├── zeroclaw.md            Reference agent overlay — paths and tool names.
├── raw/assets/            Immutable sources and attachments.
└── wiki/
    ├── index.md           Table of contents.
    ├── log.md             Append-only activity record.
    ├── tasks.md           Shared work queue, #owner/ tags.
    └── How this vault works.md
```

## Install

Not yet automated. The setup skill (`SKILL.md`) is next.

For now, copy `skeleton/` into your vault and read `skeleton/agents.md`. It is written to be read by an agent, and it is the whole contract.

Your vault need not be empty. The skeleton coexists with existing notes — the agent works around what's there and migrates only when you ask.

To make your agent pick it up automatically, either rename `zeroclaw.md` to match your runtime, or copy the paths from it into your own overlay. Keep `agents.md` as the shared base so the rules stay in one place.

## Design principles

- **Three layers, no more.** Deeper structure is unearned until page count forces it.
- **`raw/` is immutable.** If a source is wrong, say so in `wiki/` — never fix it in place.
- **Index before search.** A table of contents is cheaper than a grep, and keeps the agent oriented.
- **Extend, don't duplicate.** Near-duplicate pages are the most common failure mode of agent-maintained wikis.
- **Contradictions are kept, not overwritten.** Both claims stay, each attributed. The conflict is the interesting part.
- **Completion is history.** Finished work is dated and left in place, never deleted.
- **No locks.** Log-first, last-write-wins, git when you need real isolation.

## Based on

Andrej Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — the pattern. This repo is one instantiation of it, deliberately opinionated about layout and operations, deliberately silent about tooling.

> "Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."

The gist text is not vendored here. Read it at the source; `wiki/LLM Wiki pattern.md` summarises it with the parts this project adopted and rejected.

## Status

Working vault convention, in use. Setup automation (`SKILL.md`) and a structural linter are next.

## License

MIT. See [LICENSE](LICENSE).
