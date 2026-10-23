# ai-obsidian-encyclopedia

A seed for Obsidian vaults that LLM agents maintain, based on Andrej Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Give your agent this URL. It reads `SKILL.md`, asks where your vault is, scaffolds it, and installs a `load-vault` skill so you never have to explain your own vault to it again.

**Empty vaults only.** If your vault already has notes, setup refuses. Migrating means reformatting notes an agent did not write, and no script does that safely — so this repo does not pretend to. Your options are a new empty vault, or a manual migration with your own agent.

## What you get

```
raw/                          sources. Immutable, never edited by an agent.
raw/assets/                   images and attachments
wiki/index.md                 root catalog: one line per project
wiki/<project>/index.md       that project's pages
wiki/<project>/progress/      01_, 02_ ... one file per session, never edited
wiki/*.md                     cross-cutting pages
wiki/log.md                   audit trail: what was written, where
wiki/tasks.md                 work queue with #owner/ tags
AGENTS.md                     the schema
```

Three layers — `raw/`, `wiki/`, `AGENTS.md` — and no more. Deeper structure is unearned until page count forces it.

The conventions are the point, so they are worth stating plainly:

- **`raw/` is immutable.** If a source is wrong, say so in `wiki/`.
- **Index before search.** Two levels: projects at the root, pages per project. Reading the first file costs nothing at any vault size.
- **Extend, don't duplicate.** Near-duplicate pages are the most common failure mode of agent-maintained wikis.
- **Contradictions are kept, not overwritten.** Both claims stay, each attributed.
- **`progress/` is immutable.** One numbered file per session; the highest number is the current state, so there is no status doc to go stale.
- **The log carries no content.** It is an audit trail, not a second wiki.
- **Completion is history.** Finished tasks are dated and left in place.

## The load-vault skill

The friction this solves: a fresh session has no idea where your vault is or what you were doing.

The skill bakes in the vault's real path, then on invocation reads the last five entries of `wiki/log.md` and reports where the vault is, what happened last, and which project it was. It does not open `progress/` — you ask, it reads. That keeps a load to a few hundred tokens instead of a directory crawl.

It is generated during setup into whatever skill mechanism your runtime uses. It is then yours: change the triggers, change the report, delete it. Nothing in the vault depends on it.

## Install

Point your agent at this file:

```
Set up my vault according to https://github.com/edchtzwe/ai-obsidian-encyclopedia/SKILL.md
```

It will ask for the vault path, check that it is an Obsidian vault and that it is empty, clone this repo to a temporary directory, copy `skeleton/` into the vault, date the setup entry in the log, and install `load-vault`.

If your vault is not empty it stops and says so. That is the whole safety story: this repo never edits a note that already exists.

## Why prose instead of a program

Every modern agent already reads, writes, searches and edits files. A Python wrapper around those operations would be a worse version of native tools, and it would rot.

What agents do not share is judgement: when to extend a page instead of creating a near-duplicate, how to keep an index honest, what to do when a new source contradicts an old claim. That is prose, and prose does not break on a version bump.

One script is on the roadmap and no more — a linter for broken wikilinks, malformed frontmatter, orphans and duplicate slugs. Deterministic, mechanical, and it should not burn a context window on every write. Contradiction and staleness checks are judgement, and stay out.

## Status

v0.1 — seed and setup skill. The linter is not written; `AGENTS.md` describes it as planned, and nothing else depends on it.

## Based on

Andrej Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — the pattern. This repo is one instantiation of it, deliberately opinionated about layout and operations, deliberately silent about tooling.

> "Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."

The gist text is not vendored here. Read it at the source; `skeleton/wiki/LLM Wiki pattern.md` summarises it and names what this project adopted and rejected.

## License

MIT. Fork it, change the conventions, publish your own — that is what it is for.
