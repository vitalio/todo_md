# todo_md — active tasks and operational state

`README.md` documents installation and CLI usage; `AGENTS.md`
defines the rules and workflow for an AI agent. Deferred tasks live in
`TODO_PLAN.md`; completed and canceled records live in
`TODO_ARCHIVE.md`.

Task heading format: `### <emoji> [<STATUS>] <ID>: <title>`
(`⚪ [NEW]`, `🔵 [WIP]`, `⏸️ [HOLD]`, `❓ [QUESTION]`, `✅ [DONE]`, `❌ [CANCELED]`).

## Resume

Written 2026-11-13. Released `todo_md` `v0.2.1` (`84bd75a`):
- When `TODO.md` has 0 active tasks and `TODO_PLAN.md` has deferred tasks, `todo_md` summary automatically displays the deferred tasks with a hint to run `todo_md activate <ID>`.
- Replaced `.run_block.start` with `.agents_bundle`.

## Tasks
