#!/usr/bin/env python3
# todo_md-repo: vitalio/todo_md
"""Usage:
  {prog} [dir]                               Print summary (TODO.md + IDs in use + plan/archive counts)
  {prog} <ID> | show <ID>                    Show full section for task <ID> across TODO*.md
  {prog} list [filter]                       Compact task table (active | plan | archive | all | <STATUS>)
  {prog} plan                                Print summary plus full TODO_PLAN.md
  {prog} archive [<ID>] [-m NOTE]            Print TODO_ARCHIVE.md, or archive task <ID>
  {prog} add [<ID|PREFIX>] <TITLE> [opts]    Add a new task (reads body from -b TEXT or stdin)
                                             Opts: --plan, --status STATUS, -m NOTE, -b BODY
  {prog} edit <ID> [opts]                    Update task title, note, or body (-t TITLE, -m NOTE, -b BODY or stdin)
  {prog} append <ID> [-b TEXT]               Append text to task <ID> body (from -b TEXT or stdin)
  {prog} status <ID> <STATUS> [-m NOTE]      Update status of <ID> (NEW|WIP|HOLD|QUESTION|DONE|CANCELED)
  {prog} activate <ID> [--wip]               Move task <ID> from TODO_PLAN.md into active TODO.md
  {prog} defer <ID>                          Move task <ID> from active TODO.md into TODO_PLAN.md
  {prog} done <ID> [-m SHA_OR_NOTE]          Mark task <ID> as DONE and move it to TODO_ARCHIVE.md
  {prog} cancel <ID> [-m REASON]             Mark task <ID> as CANCELED and move it to TODO_ARCHIVE.md
  {prog} resume [-b TEXT]                    Replace ## Resume section in TODO.md (from -b TEXT or stdin)
  {prog} ids                                 Print highest task IDs in use and next available ID per prefix
  {prog} check                               Validate layout, headings, status badges, and unique IDs
  {prog} init [--force]                      Create starter TODO.md, TODO_PLAN.md, and TODO_ARCHIVE.md
  {prog} --agents | agents                   Print Markdown instructions for AI agents
  {prog} update [--force]                    Self-update {prog} from GitHub (vitalio/todo_md)
  {prog} check-update                        Check if a newer version is available on GitHub
  {prog} -V | --version                      Print version and exit 0
  {prog} -h | --help                         Print this usage and exit 0

Manages structured Markdown task files in a repository:
  - TODO.md          Operational state (Resume) and immediate/active tasks
  - TODO_PLAN.md     Deferred/future tasks and open design questions
  - TODO_ARCHIVE.md  Completed (DONE) and dropped (CANCELED) tasks and historical snapshots

Environment variables:
  TODO_MD_CWD          Override target directory (default: current directory or Git root)
  TODO_MD_UPDATE_URL   Override raw script URL for update / check-update
"""
from __future__ import annotations

if __doc__ is None:
    raise SystemExit("missing usage documentation")

import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from datetime import date
from pathlib import Path

VERSION = "0.3.1"
REPO_MARKER = "todo_md-repo: vitalio/todo_md"
DEFAULT_UPDATE_URL = "https://raw.githubusercontent.com/vitalio/todo_md/main/todo_md"
FENCE = chr(96) * 3

VALID_STATUSES: dict[str, str] = {
    "NEW": "⚪",
    "WIP": "🔵",
    "HOLD": "⏸️",
    "QUESTION": "❓",
    "DONE": "✅",
    "CANCELED": "❌",
}

TASK_FILES = ("TODO.md", "TODO_PLAN.md", "TODO_ARCHIVE.md")

HEADING_RE = re.compile(
    r"^###\s+(⚪|🔵|⏸️?|❓|✅|❌)\s+`?\[(NEW|WIP|HOLD|QUESTION|DONE|CANCELED)\]`?\s+([A-Z]\d+)\s*:\s*(.+?)\s*$"
)
STATUS_TOKEN_PAT = r"(?:(?:⚪|🔵|⏸️?|❓|✅|❌)\s+)?`?\[(?:NEW|WIP|HOLD|QUESTION|DONE|CANCELED)\]`?"
ANY_ID_RE = re.compile(
    rf"^(?:###\s+(?:{STATUS_TOKEN_PAT}\s+|[-*o?+c]\s+)?|(?:- \[[ xX~]\]\s+(?:{STATUS_TOKEN_PAT}\s+)?|- |[*o?+c] ))([A-Z]\d+)\b"
)


def prog_name() -> str:
    raw = Path(sys.argv[0]).name if sys.argv and sys.argv[0] else "todo_md"
    for suf in (".py", ".cmd", ".bat", ".exe"):
        if raw.lower().endswith(suf) and len(raw) > len(suf):
            raw = raw[:-len(suf)]
            break
    return raw or "todo_md"


def usage_text() -> str:
    return (__doc__ or "").format(prog=prog_name())
