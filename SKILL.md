---
name: ai-obsidian-encyclopedia
description: Scaffold an empty Obsidian vault into an agent-maintained LLM wiki, then install a load-vault skill that tells the agent where the vault is and what was last done.
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
wiki/log.md                audit trail with one setup entry
wiki/tasks.md              the shared queue
wiki/How this vault works.md
wiki/LLM Wiki pattern.md
```

No `README.md`, no `SKILL.md`, no `.git` — those belong to the seed repo, not to their vault.

## 6. Date the first log entry

`wiki/log.md` ships with one entry dated `YYYY-MM-DD`. Replace that placeholder with today's date, and change nothing else:

```bash
# replace the placeholder in the setup entry only
```

One line, one edit. Nothing else in the copied files is modified.

## 7. Install the `load-vault` skill

Setup itself created high friction: the user had to tell their agent where the vault is, what it is, and what happened last. This skill removes that permanently.

Write it into **your own runtime's skill mechanism** — a skills directory, a workshop proposal for the user to approve, a config entry, whatever your runtime uses. Do not invent a path, and do not assume another agent's layout. If your runtime has no skill system, put this spec in a file the user can paste into their agent's instructions yourself.

**The spec:**

```
Name: load-vault
Triggers: !load-vault, load-vault, /load-vault, "load my vault"

Vault: <absolute path, resolved in step 1>

On invocation:
1. If the vault path no longer exists, ask the user for the new path and
   update this skill. Do not search for it.
2. Read the last 5 entries of <vault>/wiki/log.md. Entries start with "## [",
   so take the last 5 blocks, not the last 20 lines — entries vary in height.
3. Report, in five lines or fewer:
   - vault path
   - the most recent entry: date, what was done
   - the project folder it names, and the newest progress file in it
   Do not open that progress file. Do not open the project index.
   Report only.
4. If the user asks to continue, then read, in this order:
   newest progress/NN_*.md -> that project's index.md -> AGENTS.md.
5. Never write to the vault while loading it.

This skill is the user's. They may change the triggers, the number of
entries, the report format, or delete it. It is a convenience, not
part of the vault contract.
```

Bake the real path in. A skill that has to ask where the vault is has not solved anything.

Then tell the user it exists and how to invoke it. If your runtime requires approval (a proposal, a diff to accept), say that it is waiting for them rather than pretending it is live.

## 8. Report and stop

Five lines:

- Vault path.
- Files created — the list above, once.
- Projects: none yet. That is correct for a fresh vault.
- Skill: installed, or waiting on their approval.
- Next move: put a source in `raw/`, then invoke `load-vault` and ask for an ingest.

## What setup must never do

- **Never edit a note.** Setup copies files and dates one line. That is all it writes.
- **Never add frontmatter to anything.** No note exists yet to add it to.
- **Never run on a vault with content.** No exceptions, no partial migration.
- **Never `git init` the vault.** If it is already a repo, leave committing to the user.
- **Never delete the clone while the user might want the repo.** Mention nothing; it is a temp directory and it will clean itself up.
- **Never copy the seed's `README.md` or `SKILL.md` into the vault.** The vault gets the schema and the wiki, not the marketing.

## After setup

Setup is over. From here the vault's own `AGENTS.md` is the contract: three layers, `raw/` immutable, indexes before search, one log line per write, `progress/` per session. Read it when the user asks you to do something with the vault — not before.
