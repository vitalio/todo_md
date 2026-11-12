# todo_md

**Structured Markdown task management (`TODO.md`, `TODO_PLAN.md`, `TODO_ARCHIVE.md`) for humans and AI coding agents.**

`todo_md` is a zero-dependency CLI companion to [`run_block`](https://github.com/vitalio/run_block).
It keeps your repository's operational context (`Resume`), active queue (`TODO.md`), deferred
roadmap (`TODO_PLAN.md`), and historical archive (`TODO_ARCHIVE.md`) clean, validated, and
ready to bundle into new AI chat sessions.

## Quick Installation

### Linux & macOS

```bash
curl -fsSL https://raw.githubusercontent.com/vitalio/todo_md/main/install.sh | sh
```

### Windows (PowerShell 7+)

```powershell
irm https://raw.githubusercontent.com/vitalio/todo_md/main/install.ps1 | iex
```

## Integration with `run_block --start`

Add `todo_md` to your project's `.run_block.start`:

```text
AGENTS.md

$ run_block --agents
$ todo_md --agents
$ todo_md
$ git status -sb
$ git branch -vv
$ git log --oneline -10
```

## CLI Reference

| Command | Description |
| :--- | :--- |
| `todo_md` | Print operational summary (`TODO.md` + `IDs in use` + plan/archive counts) |
| `todo_md <ID>` / `todo_md show <ID>` | Show full Markdown section for task `<ID>` across `TODO*.md` |
| `todo_md list [filter]` | List tasks (`active`, `plan`, `archive`, `all`, or status like `WIP`) |
| `todo_md plan` | Print operational summary plus full `TODO_PLAN.md` |
| `todo_md archive [<ID>] [-m NOTE]` | Print `TODO_ARCHIVE.md`, or archive task `<ID>` to `TODO_ARCHIVE.md` |
| `todo_md done <ID> [-m NOTE]` | Mark task `<ID>` as `✅ [DONE]` and move it to `TODO_ARCHIVE.md` |
| `todo_md cancel <ID> [-m REASON]` | Mark task `<ID>` as `❌ [CANCELED]` and move it to `TODO_ARCHIVE.md` |
| `todo_md status <ID> <STATUS> [-m N]` | Update task status (`NEW`, `WIP`, `HOLD`, `QUESTION`, `DONE`, `CANCELED`) |
| `todo_md activate <ID> [--wip]` | Move task `<ID>` from `TODO_PLAN.md` into active `TODO.md` |
| `todo_md defer <ID>` | Move task `<ID>` from `TODO.md` into `TODO_PLAN.md` |
| `todo_md ids` | Print highest task IDs in use and next free ID per letter prefix |
| `todo_md check` | Validate task headings, status badges, and unique IDs across `TODO*.md` |
| `todo_md init [--force]` | Create starter `TODO.md`, `TODO_PLAN.md`, and `TODO_ARCHIVE.md` |
| `todo_md --agents` | Print Markdown instructions for AI agents |
| `todo_md update [--force]` | Self-update `todo_md` from GitHub (`vitalio/todo_md`) |
| `todo_md check-update` | Check GitHub for a newer version |
| `todo_md -V`, `--version` | Print version and exit `0` |
| `todo_md -h`, `--help` | Print usage help and exit `0` |

## License

[MIT](LICENSE) © 2026 [vitalio](https://github.com/vitalio)
