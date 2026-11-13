# `todo_md` — Project-Specific Agent Rules

Universal workflow, language, Git, SemVer, and Python CLI rules are loaded via `agents_rules` in `.agents_bundle`.

## Release trigger & local reinstall

- Whenever `todo_md`, `install.sh`, or `install.ps1` is modified, bump `VERSION` and `VERSION = "..."` in `todo_md`, reinstall locally via `sh install.sh --yes >/dev/null`, commit, push to `origin main`, and push annotated tag `vX.Y.Z`.
