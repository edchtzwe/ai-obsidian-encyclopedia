---
type: note
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tasks, queue]
---

# Tasks

Shared work queue for the human and any agent working in this vault.

One line per task. Completed tasks are **never deleted** — they are checked off and dated, then left in place as a record.

## Syntax

```
- [ ] Short imperative description #owner/x ➕ YYYY-MM-DD 📅 YYYY-MM-DD [[Related Page]]
- [x] Finished thing #owner/clawz ➕ 2026-10-20 ✅ 2026-10-21
```

| Field | Meaning |
| :--- | :--- |
| `#owner/any` | Unclaimed. First agent to start it replaces the tag with its own. |
| `#owner/human` | The human's. Agents do not touch these unless explicitly asked. |
| `#owner/<agent>` | Claimed. If you are not that agent, leave it alone. |
| `➕ date` | Added. Set on creation, never changed. |
| `📅 date` | Due. Optional. Only when there is a real deadline. |
| `✅ date` | Completed. Appended at the moment of completion. |
| `[[Page]]` | The knowledge this task concerns. Add once the page exists. |

Priority markers are optional and sparing: `⏫` high, `🔼` medium, `🔽` low.

## Rules for agents

1. **Append, don't rewrite.** Add new lines at the bottom of the Open section, or replace a single line. Never rewrite the file wholesale.
2. **Claim before you start.** `#owner/any` → `#owner/<you>`. One edit, immediately, before doing the work.
3. **Complete in place.** `[ ]` → `[x]`, append `✅ <today>`. Keep the line and its owner tag.
4. **Never delete a task line** — not yours, not anyone's. If a task is obsolete, complete it and let the log say why, or move it to Dropped.
5. **Do not touch `#owner/human`.** Surface it instead of doing it.
6. **One task per line.** No nested checklists — they are ambiguous to parse and impossible to claim.

## Open

Starter tasks. Delete them as you make the vault yours.

- [ ] Read `AGENTS.md` and `wiki/index.md`, then create the first project folder `wiki/<project>/` #owner/any ➕ YYYY-MM-DD
- [ ] Drop a source into `raw/` and ask your agent to ingest it #owner/any ➕ YYYY-MM-DD
- [ ] End the session with a `progress/01_slug.md` and a log entry that links it #owner/any ➕ YYYY-MM-DD

## Done

## Dropped

Abandoned or superseded. Kept for the record; say why in the log.
