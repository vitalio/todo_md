# `todo_md` — Project-Specific Agent Rules

## Architecture & Module Boundaries

- `src/header.py` — CLI usage docstring (`-h`/`--help`), standard library imports, version placeholder (`__VERSION__`, injected from `VERSION` by `build.py`), and task heading regexes.
- `src/parser.py` — `TODO.md` and `TODO_ARCHIVE.md` task parser, ID sequence tracking, and structural validator (`todo_md check`).
- `src/commands.py` — task lifecycle subcommands (`init`, `add`, `edit`, `append`, `status`, `next`, `done`, `cancel`, `list`, `archive`, `ids`, `check`) and `todo_md --agents`. Keep `agents_markdown()`, `-h`/`--help`, and `README.md` in sync in the same commit whenever commands or flags change.
- `src/cli.py` — CLI argument routing and self-update (`update`, `check-update`).
