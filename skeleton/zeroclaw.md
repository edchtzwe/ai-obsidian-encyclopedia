# zeroclaw — Vault Overlay

Agent-specific notes on top of [agents.md](agents.md). This file is an **overlay**, not a copy — read `agents.md` for the actual rules, then apply the deltas here.

## This instance

- Agent: clawz (zeroclaw runtime)
- Vault: `/zeroclaw-data/.zeroclaw/agents/clawz/workspace/obsidian-vault`
- Workspace root: `/zeroclaw-data/.zeroclaw/agents/clawz/workspace`

Paths above are absolute because `file_read` / `file_write` resolve relative paths from the workspace root, while `shell` may run elsewhere. Pass absolute paths to file tools and relative paths to shell, or `cd` first.

## How work enters this vault

Through the `!vault` skill in `skills-chest/`, loaded on demand. The schema is **not** injected into the system prompt — that would cost context on every session whether or not the vault is in play.

If the skill is absent or the task arrived without it: read `agents.md` and `wiki/index.md` before touching anything. Two reads, not a directory crawl.

## Standard moves

```bash
V=/zeroclaw-data/.zeroclaw/agents/clawz/workspace/obsidian-vault

# Last five log entries
grep "^## \[" "$V/wiki/log.md" | tail -5

# Every page
find "$V/wiki" -name "*.md" -type f

# Append a log entry (newest at bottom)
printf '## [%s] ingest | %s\n- %s\n\n' "$(date +%F)" "$TITLE" "$NOTE" >> "$V/wiki/log.md"
```

Native tools cover everything else. There is no read/write API to call — this agent writes markdown directly, `file_write` / `file_edit`, same as any other file.

## Deltas from the base schema

- **Do not rename existing user files.** `{{Big Brother}}.md` and `{{Big Brother}} System Instructions.md` violate the filename rule in `agents.md` (braces). They are the user's; leave them until the user asks. Wikilinks resolve to them today.
- **`raw/` is empty.** Nothing has been ingested yet. Do not invent sources or backfill from memory — a source page without a raw file is unverifiable.
- **No linter yet.** Planned, not written. Do the mechanical checks by reading until it exists.

## Open cleanup

- Write the linter (`tools/lint.py`) once the vault is big enough that reading it costs real context.
- `wiki/tasks.md` dashboards need the Obsidian **Tasks** community plugin. Not installed. The queue works without it; only the query views are dead until it is.
