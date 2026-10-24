---
name: ai-obsidian-encyclopedia
description: Scaffold an empty Obsidian vault into an agent-maintained LLM wiki, then write the vault's path and contract into the agent's always-loaded memory so every future session starts oriented.
---

# Set up an agent-maintained Obsidian vault

You are being asked to scaffold a vault from a seed repo. This file is the only thing you need to read. `AGENTS.md` in the seed is for **using** the vault afterwards, not for setting it up — do not read it during setup.

**This works on empty vaults only.** If the vault already has notes, stop. There is no safe migration: an agent reformatting someone's notes will damage them eventually, and no script can do it without judgement. A refusal costs one message; a bad migration costs their work.

---

## 1. Get the vault path

Ask the user for the absolute path to their Obsidian vault. Do not guess, do not search their disk, do not use the current directory.

```bash
cd "<vault>" && pwd -P
```

Then confirm it is an Obsidian vault:

```bash
test -d "<vault>/.obsidian" && echo vault || echo not-a-vault
```

Not a vault → stop and say: *"That folder isn't an Obsidian vault. Open Obsidian → Create new vault, point it at where you want it (or open an existing empty one), then tell me the path again."* Setting up Obsidian is their job, not yours.

## 2. Gate 1 — is it already set up?

```bash
ls "<vault>/AGENTS.md" "<vault>/wiki/index.md" "<vault>/wiki/log.md" 2>/dev/null
```

Anything found → stop. It is already seeded; run setup twice and you will overwrite the schema someone has since edited.

## 3. Gate 2 — is it empty?

List everything that is not configuration, trash, version control, or OS noise:

```bash
find "<vault>" -type f \
  -not -path '*/.obsidian/*' -not -path '*/.trash/*' -not -path '*/.git/*' \
  -not -name '.DS_Store' -not -name 'Thumbs.db' -not -name 'desktop.ini'
```

- **No output** → empty. Continue.
- **Any output** → stop.

The refusal, in full:

> This vault already has notes in it. I only set up empty vaults — migrating an existing one means reformatting your notes, and that risks permanent damage I can't undo for you. I won't touch it.

Do not offer to try anyway, do not offer to migrate "just this once", do not propose archiving and reformatting. If they want this structure, the honest options are a new empty vault, or doing the migration by hand with their own agent.

Empty folders are fine. A vault with only `.obsidian/` is a fresh vault.

## 4. Clone the seed to a temporary directory

Clone outside the vault. Never clone inside it.

```bash
tmp="$(mktemp -d)/ai-obsidian-encyclopedia"
git clone --depth 1 https://github.com/edchtzwe/ai-obsidian-encyclopedia.git "$tmp"
```

HTTPS, not SSH. You are a stranger to this repo and it is public; no key, no push rights, no PRs. If the clone fails for network reasons, say so — do not reconstruct the files by hand from memory.

## 5. Copy the seed in

Copy the **contents** of `skeleton/`, not the folder, and not the repo:

```bash
cp -R "$tmp/skeleton/." "<vault>/"
```

Windows (PowerShell):

```powershell
Copy-Item -Path "$tmp\skeleton\*" -Destination "<vault>" -Recurse
```

That is the whole installation. What arrives:

```
AGENTS.md                  the schema
raw/assets/                empty, ready for sources
wiki/index.md              root catalog, no projects yet
wiki/log.md                audit trail, empty until step 6
wiki/tasks.md              the shared queue
wiki/How this vault works.md
wiki/LLM Wiki pattern.md
```

No `README.md`, no `SKILL.md`, no `.git` — those belong to the seed repo, not to their vault.

## 6. Write the first log entry

`wiki/log.md` ships empty. Append the setup entry, dated today:

```bash
printf '%s\n' '' "## [$(date +%F)] setup | vault initialised from ai-obsidian-encyclopedia" \
  '- Structure created: `raw/`, `wiki/`, `AGENTS.md`. Nothing ingested yet, no projects yet' \
  '' '---' '' >> "<vault>/wiki/log.md"
```

That is the only write setup makes inside an existing file, and the only content it authors. Everything else was copied byte-for-byte.

Do not invent entries, do not backfill, do not describe what you are about to do. One line about what happened.

## 7. Bake the vault into the agent's memory

Setup created the friction: every fresh session had to be told where the vault is, what it is, and what happened last. An installed skill only fixes that if the user remembers to invoke it. Memory does not need invoking.

Find the file **your runtime loads into every session** as long-term memory — `MEMORY.md`, `CLAUDE.md`, `.cursorrules`, a standing-instructions block, whatever it is. Do not invent a path, and do not assume another agent's layout. If your runtime has no such file, put the block in the agent's system prompt or persistent instructions. If there is nowhere it will actually be loaded, say so instead of writing a file that does nothing.

**Append** the block. Do not rewrite the file, do not reorder what is already there, do not delete anything the user wrote.

```
## Obsidian vault

Path: <absolute path, resolved in step 1>

Before reading or writing in it, read <absolute path>/AGENTS.md — that is the contract.

"Update my vault", "what did I last work on", "add this to my vault": that vault.

If the path does not resolve, ask for a new one. Never search the disk.
```

That is the whole mechanism. The path means no hunting; the `AGENTS.md` line means the conventions load themselves; the trigger list means the user does not have to learn a command. `AGENTS.md` carries the read order, so nothing else needs stating here.

Five lines is deliberate. This block is paid for in every session, forever.

## 8. Report and stop

Five lines:

- Vault path.
- Files created — the list above, once.
- Projects: none yet. That is correct for a fresh vault.
- Memory: the file you appended to, and the vault path in it — or why you could not.
- Next move: put a source in `raw/`, then say "update my vault" and ask for an ingest.

## What setup must never do

- **Never edit a note.** Setup copies files and appends one log line. That is all it writes.
- **Never add frontmatter to anything.** No note exists yet to add it to.
- **Never run on a vault with content.** No exceptions, no partial migration.
- **Never `git init` the vault.** If it is already a repo, leave committing to the user.
- **Never mention the temp clone.** It is a cache, not their data; it cleans itself up. Saying "you can delete this" invites a question about something that does not matter.
- **Never copy the seed's `README.md` or `SKILL.md` into the vault.** The vault gets the schema and the wiki, not the marketing.
- **Never rewrite the memory file.** Append the block and leave the user's existing memory alone.

## After setup

Setup is over. From here the vault's own `AGENTS.md` is the contract: three layers, `raw/` write-once, indexes before search, one log line per write, `progress/` per session. Read it when the user asks you to do something with the vault — not before.
