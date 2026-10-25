---
type: schema
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [schema, meta]
---

# AGENTS.md

The contract for any agent working in this vault. Based on Andrej Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern, adapted for several agents sharing one vault across many projects.

## Start here

The folder holding this file is the vault root.

1. `wiki/index.md` — one line per project, each pointing at that project's index.
2. `wiki/<project>/index.md` — that project's pages. Every wiki subfolder has one.
3. `wiki/<project>/progress/` — one file per session. The highest number is the current state; read it to continue that work.
4. `wiki/log.md` — what happened, oldest first. Last five entries:

   ```bash
   grep '^## \[' wiki/log.md | tail -5
   ```

   The projects in those five entries, newest first, each with its latest progress file:

   ```bash
   awk '/^## \[/{if(h!=""){n++;H[n]=h;P[n]=p}h=$0;p="";next} /^- Progress: /{p=$0} END{if(h!=""){n++;H[n]=h;P[n]=p} for(i=n;i>=((n>5)?n-4:1);i--){if(P[i]=="")continue; s=H[i]; k=match(s,/wiki\/[^\/]+\//)?substr(s,RSTART,RLENGTH):s; if(k in seen)continue; seen[k]=1; print H[i]; print P[i]}}' wiki/log.md
   ```

   Two lines per project: its most recent entry, and that session's progress file. Five entries, one line per project, so three sessions on one project cost one line. This surfaces where each thing stopped; it opens nothing. Continuing is the user's call — not the agent's.
5. `wiki/tasks.md` — the shared queue.

Follow the indexes; never crawl directories. If the session matches no project, ask before creating one. If the vault path in your memory does not resolve, ask for it — do not search the disk.

Everything below is the rules. Nothing here is optional.

## What this vault is

Compiled knowledge, not chat history. A source is read once and written up as linked markdown; the wiki is the artifact. Nothing is re-derived from raw documents on every question, and nothing learned dies in a chat window.

## Three layers

| Layer | Owner | Rule |
| :--- | :--- | :--- |
| `raw/` | Both | Write-once. Anyone may add a source; no one edits, moves or deletes one. |
| `wiki/` | Agents | Written by agents, read by humans. |
| `AGENTS.md` | Both | The rules that keep the other two honest. |

No fourth layer. A folder is added when page count forces it, not because a category exists.

## Layout

```
raw/                          sources — the provenance for every claim
raw/assets/                   images and attachments
wiki/index.md                 root catalog: one pointer per project
wiki/log.md                   audit trail of operations on the vault
wiki/tasks.md                 shared work queue
wiki/<project>/index.md       that project's catalog
wiki/<project>/progress/      numbered session records, newest = current state
wiki/<project>/*.md           the project's pages
wiki/*.md                     cross-cutting pages that belong to no project
lint.py                       the health check — the one script
AGENTS.md                     this file
```

`<project>` is the project's machine name in kebab-case. Pages inside keep human titles.

A fresh vault has no project folders, and that is correct — `wiki/<project>/` is created with that project's first page, not before. Do not create empty project scaffolding.

## Hard rules

1. **`raw/` is immutable.** If a source is wrong, say so on a wiki page. Never fix it in place.
2. **Adding is not editing.** Any agent may land a source in `raw/` — a PDF, a document, an export. Once there, it is frozen. Record its path in the page's `sources:` and cite it.
3. **Read the indexes first.** Root index → project index → the page. Only search the vault if the index fails you.
4. **Every write ends in one log line.** One line, at the time of the write, naming the project folder it touched.
5. **Extend, don't duplicate.** Look for the page that already covers it. Near-duplicates are the most common failure mode.
6. **Rewrite summaries; never append to them.** An appended summary is a changelog wearing a summary's clothes.
7. **Never silently overwrite a contradiction.** Keep both claims, attribute each, flag the conflict.
8. **Cite `raw/` sources.** A claim traceable to a source names it. Cite the original document, not a text extraction of it — an extraction is derived, lossy and re-derivable, and is never itself the source.
9. **Say when you don't know.** A documented gap is useful; an invented bridge is not.
10. **Never rewrite history.** `log.md`, `progress/` and completed tasks are records. They are appended to, not edited.

## Operations

### ingest

One source from `raw/` into the wiki. If it is not in `raw/` yet, land it there first — rule 2 — and leave it untouched afterwards.

1. Read the source. If the takeaways are unclear, ask before writing.
2. Find every existing page it touches — usually more than expected.
3. Write or update a `type: source` summary page in the project's folder.
4. Update the entity, concept and synthesis pages it changes.
5. Note contradictions explicitly.
6. Add the page to the project index.
7. Log one line.

One source at a time, except for bulk imports.

### query

1. Root `wiki/index.md` → the project's `index.md` → the page.
2. Follow `[[wikilinks]]` as far as the question needs.
3. Answer with citations to the pages used.
4. **File good answers back.** A comparison, an analysis, a connection found — that is knowledge. Write it as a page, index it, log it.

If the vault can't answer, say what's missing and which source would fill it. That is a useful answer.

### lint

Health check. On request, not every session. Broken `[[wikilinks]]`, malformed frontmatter, orphan pages, pages missing from their project index, contradictions, stale claims, concepts mentioned repeatedly with no page. Fix the mechanical ones; propose the judgement calls.

## Page format

```markdown
---
type: entity | concept | source | synthesis | note
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: ["raw/Source.md"]
tags: [topic]
---

# Title

One paragraph: what this page says, in the wiki's own words. Not a table of contents.

## Key points

## Connections

- [[Other Page]] — how they relate

## Sources
```

`type`, `created` and `updated` are required. `sources` and `tags` are optional. Invent no other keys. **Bump `updated` on every edit.**

A source page summarises its source; it never pastes it. The `raw/` file is the provenance, not the page.

If a source contradicts a claim already in the wiki, add the section; if nothing conflicts, omit it:

```markdown
## Contradictions

- <claim A> — [[Page]] — <source>
- <claim B> — [[Page]] — <source>
```

Keep both. Attribute both. Never silently overwrite.

- `# Title` matches the filename exactly. The page opens with prose, not a second heading.
- Cross-reference with `[[Page Name]]`. Link generously — the graph view is the health check.
- Filenames are `Title Case With Spaces.md`, matching the title.
- No `[ ] { } | # ^` in filenames. They break wikilinks.
- Frontmatter must be valid YAML or Dataview silently fails.

## Indexes

Two levels, both generated by hand and kept tiny.

**`wiki/index.md` — root.** One line per project, each pointing at that project's index, plus cross-cutting pages and system files. It grows with project count, never with page count. Roughly: twenty projects is forty lines, so reading it is free forever.

- **Append-only, with two exceptions.** Add a line when a project is created. Do not reorder or reword lines.
- Two edits are permitted: **repair** a pointer whose target was renamed, or **delete** a line whose project folder no longer exists. Log the deletion by name — the log is what survives.
- Never list a project's pages here. That is what the project index is for.

**`wiki/<project>/index.md` — project.** Every page in that project: a `[[link]]`, an em dash, a one-line summary. Factual and specific — "decisions, open questions and rationale", not "notes". If the title and summary don't tell an agent whether to open it, the line is useless.

- Update on every write inside the project.
- Session records are not listed here. `progress/` is numbered, so the newest one is always the highest number; `wiki/log.md` names every session as it happened.

Neither index holds content. Both are pointers.

### Removing a project

Deleting `wiki/<project>/` deletes its `progress/` with it — the only record of that work — and
nothing brings it back. Say so plainly, say it cannot be undone, and get explicit confirmation
before removing anything. Then delete the folder, delete the root index line, and log the removal
by name. The log line is the only trace left.

If the folder disappears out of band, its index line is now a dead pointer. Repair it: delete the
line and log it. A user may always delete what is theirs from a terminal. The contract governs the
agent, not them.

## progress/

One numbered file per work session: `progress/01_slug.md`, `02_slug.md`, …

- The folder is created with the project's first page. An empty vault has no project folders, and that is correct.
- `NN` is the highest existing number plus one. Check the directory with `ls` before writing.
- **Written once, at the end of the session. Never edited afterwards.** It is a record of that session, not a live status board.
- The highest number **is** the current state. There is no separate status document, and nothing is rewritten to stay current — so nothing can go stale.
- To find it: `ls wiki/<project>/progress/ | sort | tail -1`. The zero-padded prefix means sort order is chronological order.
- The H1 is `NN — <slug>` and does not match the filename. Progress files are exempt from the title rule.

Template:

```markdown
---
type: progress
date: YYYY-MM-DD
agent: <name>
status: done | wip | blocked
---

# NN — <slug>

## What was done

Concrete actions, past tense: what you wrote, changed, decided. Not what you plan to do.

## Files touched

Every path created, modified or deleted, one bullet each, with a short why. A path the next session cannot find is a path you did not record.

## Decisions

Choices the next session must honour, and the reason. Not a narrative of the discussion.

## Blockers

Hard stops, missing inputs, unanswered questions. `none` if none.

## Next steps

Ordered. The first step must be runnable immediately, by someone holding only this file.
```

## log.md

One line per operation **on the vault** — what was written, where. Not what the work accomplished, and never the content itself.

```markdown
## [2026-10-22] update | wiki/<project>/ — <what changed>
- <what changed, one bullet>
- Progress: wiki/<project>/progress/03_slug.md
```

Verbs: `ingest`, `create`, `update`, `move`, `delete`, `query`, `lint`, `setup`, `decision`.

The description **names the project folder** it touched (`create | wiki/<project>/page`), or the page itself when it belongs to no project (`create | wiki/<page>`). That is what makes it possible to answer "where was I?" from the last few entries alone.

An entry that records a session's writes **in a project** carries a `Progress:` bullet naming that session's file. Audit-only entries — `setup`, a push, a standalone `decision` — carry none, and neither does a write to a cross-cutting page that belongs to no project; there the entry itself is the record.

"What did I last work on" is answered from the log alone: the last five entries, deduplicated by project, newest first. That is a report, not a resume. Open a progress file only when the user asks to continue that project.

Three reasons the log carries no content:

- **Drift.** Duplicated content is a second copy of the wiki, and the copy always goes stale.
- **Size.** It is append-only forever. Content makes it unreadable within months.
- **Audit.** An audit trail answers "who changed what, when". The narrative lives in `progress/`.

Keep the prefix fixed so unix tools can parse it:

```bash
grep "^## \[" wiki/log.md | tail -5
```

## tasks.md

The shared queue for the human and every agent. The one place actionable work lives.

```
- [ ] Short imperative #owner/x ➕ 2026-10-21 📅 2026-10-28 [[Related Page]]
- [x] Finished thing #owner/clawz ➕ 2026-10-20 ✅ 2026-10-21
```

- **Claim before starting:** `#owner/any` → `#owner/<you>`, one edit, before the work.
- **Never touch `#owner/human`.** Surface it.
- **Never delete a line.** Complete in place with `✅ date`, or move it to Dropped with a reason.
- **Append, don't rewrite.** Whole-file rewrites race between agents.
- **One task per line.** Nested checklists can't be claimed unambiguously.
- **Link the page** once it exists.

`progress/` records what a session did. `tasks.md` records what remains. Do not keep a second backlog in prose.

## Concurrency

Several agents share this vault. No locks, no coordinator.

- `tail` the log before editing a shared page, to see who touched it last.
- Keep writes small and attributable. One page beat five.
- Projects are the isolation boundary: two agents on different projects never collide. Two agents on the same project collide in `progress/` only by taking the same `NN` — check, then increment.
- Log-first, last-write-wins. The vault is a git repo if you made it one; branch if you need real isolation.

## Tooling

Exactly one script: **a linter**, no LLM in the loop. Broken wikilinks, malformed frontmatter, orphan pages, pages missing from their project index, duplicate slugs.

Implemented in this package: `lint.py` at the vault root. Stdlib Python 3, no dependencies,
no config, no `--fix`. `python3 lint.py` prints `path:line: CODE: message`, exits 0 when clean
and 1 on findings. It reports; repairing is a separate decision — the agent and the user.

Nothing else. No index generator — indexes are pointers and small enough to maintain by hand, and a generator implies the index holds content it doesn't. No read/write/query layer — every agent already has file tools.

The linter must skip fenced code blocks and frontmatter. This file and `tasks.md` contain `[[wikilinks]]` as syntax examples; treating those as links reports failures that don't exist.

Deterministic checks belong in code. Contradiction and staleness checks are judgement and do not.

**The linter runs on request only.** Never run it automatically, and never as part of setup or a
routine write. The user or their agent decides a vault might be broken, then runs it to find out.

## Scale

The index works to roughly 100 sources and a few hundred pages. Past that, add search rather than a longer index. Build it when the pain arrives, not before.
