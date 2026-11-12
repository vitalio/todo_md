# todo_md — active tasks and operational state

[README.md](README.md) documents installation and CLI usage; [AGENTS.md](AGENTS.md)
defines the rules and workflow for an AI agent. Deferred tasks live in
[TODO_PLAN.md](TODO_PLAN.md); completed and canceled records live in
[TODO_ARCHIVE.md](TODO_ARCHIVE.md).

Task heading format: `### <emoji> [<STATUS>] <ID>: <title>`
(`⚪ [NEW]`, `🔵 [WIP]`, `⏸️ [HOLD]`, `❓ [QUESTION]`, `✅ [DONE]`, `❌ [CANCELED]`).

## Resume

Written 2026-11-12. Initial release `todo_md` `v0.1.0`:
- Standalone zero-dependency Python 3 CLI (`todo_md`) with `install.sh` and `install.ps1`.
- Subcommands: `todo_md` (operational summary), `todo_md plan`, `todo_md <ID>` / `todo_md show <ID>`, `todo_md list`, `todo_md ids`, `todo_md check`, `todo_md init`, and `todo_md agents`.
- Seamless integration with `run_block --start` via `.run_block.start` (`$ todo_md agents`, `$ todo_md`).

## Tasks
