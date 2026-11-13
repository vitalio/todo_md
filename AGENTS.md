# `todo_md` — Project-Specific Agent Rules

Universal workflow, language, Git, SemVer, Python CLI, and single-file build rules are loaded via `.agents_bundle`.

## Architecture & Module Boundaries

- `src/header.py` — CLI usage docstring, standard library imports, version constants, and task heading regexes.
- `src/parser.py` — `TODO.md`, `TODO_PLAN.md`, and `TODO_ARCHIVE.md` task parser, ID sequence tracking, and structural validator (`todo_md check`).
- `src/commands.py` — task lifecycle subcommands (`add`, `edit`, `append`, `status`, `activate`, `defer`, `done`, `cancel`, `resume`, `list`, `plan`, `archive`, `ids`) and `todo_md --agents`.
- `src/cli.py` — CLI argument routing and self-update (`--update`, `--check-update`).
