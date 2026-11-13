# todo_md — active tasks and operational state

`README.md` documents installation and CLI usage; `AGENTS.md`
defines the rules and workflow for an AI agent. Deferred tasks live in
`TODO_PLAN.md`; completed and canceled records live in
`TODO_ARCHIVE.md`.

Task heading format: `### <emoji> [<STATUS>] <ID>: <title>`
(`⚪ [NEW]`, `🔵 [WIP]`, `⏸️ [HOLD]`, `❓ [QUESTION]`, `✅ [DONE]`, `❌ [CANCELED]`).

## Resume

Written 2026-11-14. Released `todo_md` `v0.3.0` (`6f84ccf`):
- Modularized `todo_md` into `src/` (`header.py`, `parser.py`, `commands.py`, `cli.py`) with `build.py` (`--check`).
- Added repository-scope rule to `todo_md --agents` requiring `TODO*.md` and `Resume` to record only tasks and changes belonging to the current repository.
- Updated `.agents_bundle` to use `preset vitalio/agents_rules:default` and `rule vitalio/agents_rules:release/single-file-build`.

## Tasks
