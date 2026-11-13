# `todo_md` — Engineering Rules

- **Zero external dependencies:** Python 3.9+ standard library only (`from __future__ import annotations` at top of Python files for macOS system Python 3.9 compatibility).
- **Pre-commit checks:**
  - `bash -n install.sh && shellcheck -S warning install.sh`
  - `python3 -W error -c 'from pathlib import Path; import ast; ast.parse(Path("todo_md").read_text())'`
  - `python3 tests/test_todo_md.py -v`
  - `./todo_md check`
- **Release rule on CLI/installer changes:** Whenever `todo_md`, `install.sh`, or `install.ps1` is modified:
  1. Bump `VERSION` and `VERSION = "..."` inside `todo_md` (PATCH `0.Y.Z+1` for bugfixes, UI/box tweaks, and `--agents`/`--help` updates; MINOR `0.Y+1.0` for new CLI commands/flags or config options; MAJOR `X+1.0.0` only when explicitly requested).
  2. Reinstall locally: `sh install.sh --yes >/dev/null`
  3. Commit, push to `origin main`, and push an annotated release tag (`git tag -a vX.Y.Z -m "Release vX.Y.Z" && git push origin vX.Y.Z`).
