# todo_md — active tasks and operational state

[README.md](README.md) documents installation and CLI usage; [AGENTS.md](AGENTS.md)
defines the rules and workflow for an AI agent. Deferred tasks live in
[TODO_PLAN.md](TODO_PLAN.md); completed and canceled records live in
[TODO_ARCHIVE.md](TODO_ARCHIVE.md).

Task heading format: `### <emoji> [<STATUS>] <ID>: <title>`
(`⚪ [NEW]`, `🔵 [WIP]`, `⏸️ [HOLD]`, `❓ [QUESTION]`, `✅ [DONE]`, `❌ [CANCELED]`).

## Resume

Written 2026-11-13. Released `todo_md` `v0.1.2`:
- `todo_md init` now automatically installs `$ todo_md --agents` and `$ todo_md` into `.run_block.start` if it exists in the target directory (replacing plain `TODO.md` file entries).
- Placed `$ run_block --agents` first in `.run_block.start` and `README.md`, and added explicit versioning/tag rules in `AGENTS.md`.
- Enforced strict H2 section layout (`Resume` + `Tasks` in `TODO.md`, `Deferred Tasks` in `TODO_PLAN.md`, `Archive` in `TODO_ARCHIVE.md`) and orphan/truncated heading validation in `todo_md check`.

## Tasks
