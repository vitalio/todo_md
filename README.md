# todo_md

**Structured Markdown task management (`TODO.md`, `TODO_ARCHIVE.md`) for humans and AI coding agents.**

`todo_md` is a zero-dependency Python 3 CLI that keeps your repository's open tasks
(`TODO.md`) and completed/canceled history (`TODO_ARCHIVE.md`) clean, validated, and easy
to manage from the terminal.

## Quick Installation

### Linux & macOS

```bash
curl -fsSL https://raw.githubusercontent.com/vitalio/todo_md/main/install.sh | sh
```

### Windows (PowerShell 7+)

```powershell
irm https://raw.githubusercontent.com/vitalio/todo_md/main/install.ps1 | iex
```

## Quick Start

Initialize `TODO.md` and `TODO_ARCHIVE.md` in your repository:

```bash
todo_md init
todo_md
```

Create, update, transition, and validate tasks via the CLI:

```bash
todo_md add F "Implement feature X" --next -b "Goal and acceptance criteria."
todo_md status F1 WIP -m "started implementation"
todo_md append F1 -b "- [x] Unit tests added"
todo_md done F1 -m "a1b2c3d"
todo_md check
```

## CLI Reference

| Command | Description |
| :--- | :--- |
| `todo_md [--full]` | Print `TODO.md` overview (full `WIP`/`NEXT` tasks + compact backlog + `IDs in use`) |
| `todo_md <ID>` / `todo_md show <ID>` | Show full Markdown section for task `<ID>` across `TODO*.md` |
| `todo_md list [filter]` | List tasks (`active`, `archive`, `all`, or status like `WIP`, `NEXT`, `HOLD`) |
| `todo_md archive [<ID>] [-m NOTE]` | Print `TODO_ARCHIVE.md`, or archive task `<ID>` to `TODO_ARCHIVE.md` |
| `todo_md add [<ID\|PREFIX>] <TITLE> [opts]` | Add a new task (`--next`, `--status STATUS`, `-m NOTE`, `-b BODY` or `stdin`) |
| `todo_md edit <ID> [opts]` | Update task title, note, or body (`-t TITLE`, `-m NOTE`, `-b BODY` or `stdin`) |
| `todo_md append <ID> [-b TEXT]` | Append progress/notes to task `<ID>` body (`-b TEXT` or `stdin`) |
| `todo_md status <ID> <STATUS> [-m N]` | Update task status (`WIP`, `NEXT`, `NEW`, `HOLD`, `QUESTION`, `DONE`, `CANCELED`) |
| `todo_md next <ID> [-m NOTE]` | Promote task `<ID>` to `🎯 [NEXT]` priority at the top of `TODO.md` |
| `todo_md done <ID> [-m NOTE]` | Mark task `<ID>` as `✅ [DONE]` and move it to `TODO_ARCHIVE.md` |
| `todo_md cancel <ID> [-m REASON]` | Mark task `<ID>` as `❌ [CANCELED]` and move it to `TODO_ARCHIVE.md` |
| `todo_md ids` | Print highest task IDs in use and next free ID per letter prefix |
| `todo_md check` | Validate task headings, status badges, and unique IDs across `TODO*.md` |
| `todo_md init [TEXT] [--force]` | Create starter `TODO.md` (with optional project idea from `TEXT` or `stdin`) and `TODO_ARCHIVE.md` |
| `todo_md --agents` | Print Markdown instructions for AI agents |
| `todo_md update [--force]` | Self-update `todo_md` from GitHub (`vitalio/todo_md`) |
| `todo_md check-update` | Check GitHub for a newer version |
| `todo_md -V`, `--version` | Print version and exit `0` |
| `todo_md -h`, `--help` | Print usage help and exit `0` |

## License

MIT © 2026 vitalio
