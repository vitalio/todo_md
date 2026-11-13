# todo_md — active tasks and operational state

`README.md` documents installation and CLI usage; `AGENTS.md`
defines the rules and workflow for an AI agent. Deferred tasks live in
`TODO_PLAN.md`; completed and canceled records live in
`TODO_ARCHIVE.md`.

Task heading format: `### <emoji> [<STATUS>] <ID>: <title>`
(`⚪ [NEW]`, `🔵 [WIP]`, `⏸️ [HOLD]`, `❓ [QUESTION]`, `✅ [DONE]`, `❌ [CANCELED]`).

## Resume

Written 2026-11-13. Released `todo_md` `v0.2.0`:
- Added full task & resume mutation CLI (`todo_md add`, `todo_md edit`, `todo_md append`, `todo_md resume`) supporting both flags (`-t`, `-m`, `-b`) and `stdin` heredocs so AI agents can perform 100% of `TODO*.md` updates via CLI.
- Redesigned `todo_md --agents` to be concise, removed self-referential ``TODO.md`` links, and documented the complete CLI workflow.
- Decoupled `todo_md` and `run_block` completely (removed `install_into_run_block_start` and cross-references from `todo_md`, `README.md`, and `AGENTS.md`).
- Slimmed `AGENTS.md` to contain only non-computable engineering and release rules.
- Next in queue: `F1` (`todo_md stats`), `F2` (`--json` output).

## Tasks
