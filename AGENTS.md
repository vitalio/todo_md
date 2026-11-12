# todo_md: rules and workflow for an AI agent

Operational contract for an AI agent working on `todo_md`.
[README.md](README.md) documents features, installation, and CLI reference;
[TODO.md](TODO.md) holds the current state (`Resume`) and active tasks.

## Project architecture and files

- `todo_md` — standalone executable Python 3 CLI (zero external dependencies; supports Python 3.9+ on Linux, macOS, and Windows).
- `.run_block.start` — declarative bundle specification for `run_block --start`.
- `VERSION` — single-line semantic version string (`0.1.0`), must match `VERSION` inside `todo_md`.
- `install.sh` — POSIX shell installer for Linux and macOS.
- `install.ps1` — PowerShell 7+ installer for Windows.
- `tests/test_todo_md.py` — unit test suite (`unittest`, no network required).
- `.github/workflows/ci.yml` — GitHub Actions CI and automatic GitHub Release on `v*` tags.

## Engineering rules and local checks

- **Zero external dependencies:** Use only the Python 3 standard library (`from __future__ import annotations`).
- **Syntax and lint checks before committing:**
  ```bash
  bash -n install.sh
  shellcheck -S warning install.sh
  python3 -W error -c 'from pathlib import Path; import ast; ast.parse(Path("todo_md").read_text())'
  python3 tests/test_todo_md.py -v
  ./todo_md check
  ```
- **Keep local binary in sync:** Whenever `todo_md` or `VERSION` changes, run:
  ```bash
  sh install.sh --yes >/dev/null
  ```
- **Git identity and releases:** Commits use `Vitaly <2vitalio@gmail.com>` and push to `origin main` (`git@github.com-2vitalio:vitalio/todo_md.git`).
