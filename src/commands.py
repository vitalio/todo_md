def cmd_check(base_dir: Path) -> int:
    errors, count = validate_all(base_dir)
    if errors:
        for e in errors:
            sys.stderr.write(f"ERROR: {e}\n")
        return 1
    sys.stdout.write(f"{prog_name()}: OK ({count} task(s) verified across TODO*.md)\n")
    return 0


def cmd_init(base_dir: Path, force: bool = False) -> int:
    today = date.today().isoformat()
    templates = {
        "TODO.md": "\n".join([
            "# Project — active tasks and operational state",
            "",
            "`README.md` documents usage; `AGENTS.md` sets the rules for an AI agent.",
            "Deferred tasks live in `TODO_PLAN.md`; completed and canceled records live in `TODO_ARCHIVE.md`.",
            "",
            "Task heading format: `### <emoji> [<STATUS>] <ID>: <title>`",
            "(`⚪ [NEW]`, `🔵 [WIP]`, `⏸️ [HOLD]`, `❓ [QUESTION]`, `✅ [DONE]`, `❌ [CANCELED]`).",
            "",
            "## Resume",
            "",
            f"Written {today}. Initialized TODO structure.",
            "",
            "## Tasks",
            "",
            "### ⚪ [NEW] F1: Initial task",
            "",
            "Describe the goal and acceptance criteria.",
            "",
        ]),
        "TODO_PLAN.md": "\n".join([
            "# Project — deferred tasks and future roadmap",
            "",
            "Active operational tasks live in `TODO.md`; completed and canceled records live in `TODO_ARCHIVE.md`.",
            "",
            "## Deferred Tasks",
            "",
        ]),
        "TODO_ARCHIVE.md": "\n".join([
            "# Project — archived tasks (DONE and CANCELED)",
            "",
            "Active operational tasks live in `TODO.md`; deferred tasks live in `TODO_PLAN.md`.",
            "",
            "## Archive",
            "",
        ]),
    }
    created: list[str] = []
    for fname, content in templates.items():
        p = base_dir / fname
        if p.exists() and not force:
            continue
        p.write_text(content, encoding="utf-8")
        created.append(fname)
    if not created:
        sys.stdout.write(f"{prog_name()}: TODO*.md files already exist in {base_dir} (use --force to overwrite)\n")
    else:
        sys.stdout.write(f"{prog_name()}: initialized {', '.join(created)} in {base_dir}\n")
    return 0


def agents_markdown(prog: str | None = None) -> str:
    cmd = prog or prog_name()
    lines = [
        f"## Task management (`{cmd}` v{VERSION}: `TODO.md`, `TODO_PLAN.md`, `TODO_ARCHIVE.md`)",
        "",
        "Task state is split across three files — modify them via the `" + cmd + "` CLI rather than manual file edits:",
        "- `TODO.md` — **only** `## Resume` (current operational state) and `## Tasks` (immediate active queue).",
        "- `TODO_PLAN.md` — **only** `## Deferred Tasks` (future roadmap and open design questions).",
        "- `TODO_ARCHIVE.md` — **only** `## Archive` (completed `✅ [DONE]` and dropped `❌ [CANCELED]` tasks).",
        "",
        "### 1. Session workflow (`Resume` & task lifecycle)",
        "",
        "- **Start of session:** Reconcile `Resume` in `TODO.md` with current Git state (`git status`, `git log`). **Git beats Resume:** if they diverge, report the mismatch first and update `Resume` (`" + cmd + " resume`).",
        "- **Repository scope only:** Record only tasks, commits, and `Resume` state belonging to the current repository — never mix in tasks or changes from other repositories worked on in the same chat session.",
        "- **6 task statuses** (`### <emoji> [<STATUS>] <ID>: <title> — *<optional note>*`):",
        "  - `⚪ [NEW]` — planned, ready to start (`TODO.md` or `TODO_PLAN.md`)",
        "  - `🔵 [WIP]` — actively in progress (`TODO.md`)",
        "  - `⏸️ [HOLD]` — paused on external dependency (`TODO.md` or `TODO_PLAN.md`, with reason)",
        "  - `❓ [QUESTION]` — blocked on human clarification (`TODO.md` or `TODO_PLAN.md`, with question)",
        "  - `✅ [DONE]` — completed and verified (`TODO_ARCHIVE.md` only, with commit SHA)",
        "  - `❌ [CANCELED]` — dropped (`TODO_ARCHIVE.md` only, with reason)",
        "- **Unique IDs (never split or reuse):** Every `<ID>` (e.g. `F1`) must appear in **at most one** file across `TODO*.md`. Never archive part of `<ID>` as `DONE` while keeping a remaining `<ID>` in `TODO.md` — either keep `<ID>` open until 100% done, or close `<ID>` and `" + cmd + " add` a new ID for follow-up work.",
        f"- **End of task / session:** Update task statuses (`{cmd} done` / `status`) and refresh `Resume` (`{cmd} resume`) with today's ISO date (`YYYY-MM-DD`), completed work (with commit SHAs), current state, and next tasks in queue.",
        "",
        f"### 2. `{cmd}` CLI commands",
        "",
        f"- **Inspect:**",
        f"  - `{cmd}` — print `TODO.md` summary, `IDs in use`, and plan/archive counts",
        f"  - `{cmd} <ID>` / `{cmd} list [active|plan|archive|all|<STATUS>]` — view task `<ID>` or compact table",
        f"  - `{cmd} plan` / `{cmd} archive` / `{cmd} ids` — view deferred tasks, archive, or next free IDs",
        "- **Create & edit tasks (body can be passed via `-b TEXT` or `stdin` heredoc):**",
        f'  - `{cmd} add [<ID|PREFIX>] "<title>" [--plan] [--status NEW|WIP|HOLD|QUESTION] [-m "<note>"] [-b "<body_md>"]`',
        f'  - `{cmd} edit <ID> [-t "<title>"] [-m "<note>"] [-b "<body_md>"]` — update title, note, or body of `<ID>`',
        f'  - `{cmd} append <ID> [-b "<text>"]` — append progress/notes to the end of task `<ID>` body',
        "- **Transitions:**",
        f'  - `{cmd} status <ID> <NEW|WIP|HOLD|QUESTION> [-m "<note>"]` — update status in place',
        f"  - `{cmd} activate <ID> [--wip]` / `{cmd} defer <ID>` — move task between `TODO_PLAN.md` and `TODO.md`",
        f'  - `{cmd} done <ID> [-m "<commit_sha>"]` / `{cmd} cancel <ID> [-m "<reason>"]` — close and move to `TODO_ARCHIVE.md`',
        "- **Update `Resume` & validate:**",
        f'  - `{cmd} resume [-b "<resume_md>"]` (or pipe/heredoc via `stdin`) — replace `## Resume` in `TODO.md`',
        f"  - `{cmd} check` — validate layout, headings, and unique IDs across `TODO*.md`",
    ]
    return "\n".join(lines)


def _extract_and_remove_task(text: str, target_id: str) -> tuple[dict[str, object] | None, str]:
    lines = text.splitlines()
    in_fence = False
    start_idx: int | None = None
    end_idx: int | None = None
    found_info: dict[str, object] | None = None
    for idx, line in enumerate(lines):
        if line.lstrip().startswith(FENCE):
            in_fence = not in_fence
        if not in_fence:
            if start_idx is not None and (line.startswith("### ") or line.startswith("## ")):
                end_idx = idx
                break
            if start_idx is None and line.startswith("### "):
                m = HEADING_RE.match(line)
                if m and m.group(3).upper() == target_id:
                    emoji, status, tid, title = m.groups()
                    start_idx = idx
                    found_info = {"id": tid, "status": status, "emoji": emoji, "title": title}
    if start_idx is None or found_info is None:
        return None, text
    if end_idx is None:
        end_idx = len(lines)
    section_lines = lines[start_idx:end_idx]
    while section_lines and not section_lines[-1].strip():
        section_lines.pop()
    found_info["lines"] = section_lines
    remaining = lines[:start_idx] + lines[end_idx:]
    new_text = re.sub(r"\n{3,}", "\n\n", "\n".join(remaining).rstrip()) + "\n"
    return found_info, new_text


def _strip_heading_note(title: str) -> tuple[str, str | None]:
    m = re.match(r"^(.*?)\s+—\s+\*(.*)\*\s*$", title.strip())
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return title.strip(), None


def _format_heading(status: str, tid: str, title: str, note: str | None = None) -> str:
    emoji = VALID_STATUSES[status]
    base_title, existing_note = _strip_heading_note(title)
    final_note = note.strip() if note is not None else existing_note
    if final_note:
        return f"### {emoji} [{status}] {tid}: {base_title} — *{final_note}*"
    return f"### {emoji} [{status}] {tid}: {base_title}"


def _append_task_section(file_path: Path, section_lines: list[str], default_header: str) -> None:
    if not file_path.is_file():
        file_path.write_text(default_header + "\n\n" + "\n".join(section_lines) + "\n", encoding="utf-8")
        return
    existing = file_path.read_text(encoding="utf-8").rstrip()
    file_path.write_text(existing + "\n\n" + "\n".join(section_lines) + "\n", encoding="utf-8")


def _parse_note_arg(rest: list[str]) -> tuple[list[str], str | None]:
    pos: list[str] = []
    note: str | None = None
    i = 0
    while i < len(rest):
        if rest[i] in ("-m", "--note", "--reason"):
            if i + 1 >= len(rest):
                raise SystemExit(f"{prog_name()}: {rest[i]} requires an argument")
            note = rest[i + 1]
            i += 2
        else:
            pos.append(rest[i])
            i += 1
    return pos, note


def cmd_archive_view(base_dir: Path) -> int:
    arch_path = base_dir / "TODO_ARCHIVE.md"
    if not arch_path.is_file():
        sys.stderr.write(f"{prog_name()}: no TODO_ARCHIVE.md found in {base_dir}\n")
        return 1
    sys.stdout.write(read_if_exists(arch_path).rstrip() + "\n")
    return 0


def cmd_transition(
    base_dir: Path,
    task_id: str,
    new_status: str | None = None,
    dest_file: str | None = None,
    note: str | None = None,
) -> int:
    target = task_id.strip().upper()
    if new_status and new_status not in VALID_STATUSES:
        raise SystemExit(f"{prog_name()}: invalid status {new_status!r}; expected one of {', '.join(VALID_STATUSES)}")
    source_file: str | None = None
    found: dict[str, object] | None = None
    updated_source_text = ""
    for fname in TASK_FILES:
        p = base_dir / fname
        if not p.is_file():
            continue
        info, rem = _extract_and_remove_task(read_if_exists(p), target)
        if info is not None:
            source_file = fname
            found = info
            updated_source_text = rem
            break
    if found is None or source_file is None:
        sys.stderr.write(f"{prog_name()}: task {target!r} not found in TODO*.md under {base_dir}\n")
        return 1

    final_status = new_status or str(found["status"])
    if dest_file is None:
        if final_status in ("DONE", "CANCELED"):
            dest_file = "TODO_ARCHIVE.md"
        else:
            dest_file = source_file

    sec_lines = list(found["lines"])  # type: ignore[arg-type]
    sec_lines[0] = _format_heading(final_status, str(found["id"]), str(found["title"]), note=note)

    if dest_file == source_file:
        src_path = base_dir / source_file
        orig_lines = read_if_exists(src_path).splitlines()
        in_fence = False
        for idx, line in enumerate(orig_lines):
            if line.lstrip().startswith(FENCE):
                in_fence = not in_fence
            if not in_fence and line.startswith("### "):
                m = HEADING_RE.match(line)
                if m and m.group(3).upper() == target:
                    orig_lines[idx] = sec_lines[0]
                    break
        src_path.write_text("\n".join(orig_lines) + "\n", encoding="utf-8")
        sys.stdout.write(f"{prog_name()}: updated {target} -> [{final_status}] in {source_file}\n")
        return 0

    (base_dir / source_file).write_text(updated_source_text, encoding="utf-8")
    default_hdrs = {
        "TODO.md": "# Project — active tasks and operational state\n\n## Resume\n\nInitialized.\n\n## Tasks",
        "TODO_PLAN.md": "# Project — deferred tasks and future roadmap\n\n## Deferred Tasks",
        "TODO_ARCHIVE.md": "# Project — archived tasks (DONE and CANCELED)\n\n## Archive",
    }
    _append_task_section(base_dir / dest_file, sec_lines, default_hdrs[dest_file])
    sys.stdout.write(f"{prog_name()}: moved {target} ([{final_status}]) from {source_file} -> {dest_file}\n")
    return 0


def cmd_add(base_dir: Path, argv: list[str]) -> int:
    prog = prog_name()
    plan = False
    status = "NEW"
    note: str | None = None
    body: str | None = None
    pos: list[str] = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--plan", "-p"):
            plan = True
            i += 1
        elif a in ("--status", "-s"):
            if i + 1 >= len(argv):
                raise SystemExit(f"{prog}: {a} requires an argument")
            status = argv[i + 1].upper()
            i += 2
        elif a in ("-m", "--note", "--reason"):
            if i + 1 >= len(argv):
                raise SystemExit(f"{prog}: {a} requires an argument")
            note = argv[i + 1]
            i += 2
        elif a in ("-b", "--body"):
            if i + 1 >= len(argv):
                raise SystemExit(f"{prog}: {a} requires an argument")
            body = argv[i + 1]
            i += 2
        elif a.startswith("-"):
            raise SystemExit(f"{prog}: unknown option for add: {a}")
        else:
            pos.append(a)
            i += 1

    if status not in ("NEW", "WIP", "HOLD", "QUESTION"):
        raise SystemExit(f"{prog}: add status must be NEW, WIP, HOLD, or QUESTION (got {status!r})")

    if len(pos) == 1:
        tid = next_free_id(base_dir, "F")
        title = pos[0].strip()
    elif len(pos) == 2:
        first, second = pos[0].strip(), pos[1].strip()
        if re.fullmatch(r"[A-Za-z]", first):
            tid = next_free_id(base_dir, first.upper())
            title = second
        elif re.fullmatch(r"[A-Za-z]\d+", first):
            tid = first.upper()
            title = second
        else:
            raise SystemExit(f"{prog}: invalid task ID or prefix {first!r}; expected e.g. F or F4")
    else:
        raise SystemExit(f"{prog}: usage: {prog} add [<ID|PREFIX>] <TITLE> [--plan] [--status STATUS] [-m NOTE] [-b BODY]")

    if not title:
        raise SystemExit(f"{prog}: task title cannot be empty")

    used = all_used_ids(base_dir)
    if tid in used:
        raise SystemExit(f"{prog}: task ID {tid} is already in use (next free for {tid[0]}: {next_free_id(base_dir, tid[0])})")

    if body is None:
        body = _read_stdin_if_piped()

    dest_file = "TODO_PLAN.md" if plan else "TODO.md"
    heading = _format_heading(status, tid, title, note=note)
    sec_lines = [heading]
    if body and body.strip():
        sec_lines.extend(["", body.strip()])

    default_hdrs = {
        "TODO.md": "# Project — active tasks and operational state\n\n## Resume\n\nInitialized.\n\n## Tasks",
        "TODO_PLAN.md": "# Project — deferred tasks and future roadmap\n\n## Deferred Tasks",
    }
    _append_task_section(base_dir / dest_file, sec_lines, default_hdrs[dest_file])
    errors, _ = validate_all(base_dir)
    if errors:
        for e in errors:
            sys.stderr.write(f"ERROR: {e}\n")
        return 1
    sys.stdout.write(f"{prog}: added {tid} ([{status}]) to {dest_file}\n")
    return 0


def cmd_edit(base_dir: Path, argv: list[str]) -> int:
    prog = prog_name()
    new_title: str | None = None
    note: str | None = None
    clear_note = False
    body: str | None = None
    pos: list[str] = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-t", "--title"):
            if i + 1 >= len(argv):
                raise SystemExit(f"{prog}: {a} requires an argument")
            new_title = argv[i + 1]
            i += 2
        elif a in ("-m", "--note", "--reason"):
            if i + 1 >= len(argv):
                raise SystemExit(f"{prog}: {a} requires an argument")
            note = argv[i + 1]
            if note == "":
                clear_note = True
            i += 2
        elif a in ("-b", "--body"):
            if i + 1 >= len(argv):
                raise SystemExit(f"{prog}: {a} requires an argument")
            body = argv[i + 1]
            i += 2
        elif a.startswith("-"):
            raise SystemExit(f"{prog}: unknown option for edit: {a}")
        else:
            pos.append(a)
            i += 1

    if len(pos) != 1:
        raise SystemExit(f"{prog}: usage: {prog} edit <ID> [-t TITLE] [-m NOTE] [-b BODY]")
    target = pos[0].strip().upper()
    if body is None:
        body = _read_stdin_if_piped()

    if new_title is None and note is None and body is None:
        raise SystemExit(f"{prog}: edit requires at least one of -t TITLE, -m NOTE, -b BODY, or stdin")

    for fname in TASK_FILES:
        p = base_dir / fname
        if not p.is_file():
            continue
        lines = read_if_exists(p).splitlines()
        in_fence = False
        start_idx: int | None = None
        end_idx: int | None = None
        matched_groups: tuple[str, str, str, str] | None = None
        for idx, line in enumerate(lines):
            if line.lstrip().startswith(FENCE):
                in_fence = not in_fence
            if not in_fence:
                if start_idx is not None and (line.startswith("### ") or line.startswith("## ")):
                    end_idx = idx
                    break
                if start_idx is None and line.startswith("### "):
                    m = HEADING_RE.match(line)
                    if m and m.group(3).upper() == target:
                        start_idx = idx
                        matched_groups = (m.group(1), m.group(2), m.group(3), m.group(4))
        if start_idx is None or matched_groups is None:
            continue
        if end_idx is None:
            end_idx = len(lines)
        _, status, tid, old_full_title = matched_groups
        base_title, old_note = _strip_heading_note(old_full_title)
        final_title = new_title.strip() if new_title is not None else base_title
        final_note = None if clear_note else (note if note is not None else old_note)
        heading = _format_heading(status, tid, final_title, note=final_note)

        if body is not None:
            new_sec = [heading]
            if body.strip():
                new_sec.extend(["", body.strip()])
            new_sec.append("")
        else:
            old_sec = lines[start_idx:end_idx]
            old_sec[0] = heading
            new_sec = old_sec

        updated_lines = lines[:start_idx] + new_sec + lines[end_idx:]
        new_text = re.sub(r"\n{3,}", "\n\n", "\n".join(updated_lines).rstrip()) + "\n"
        p.write_text(new_text, encoding="utf-8")
        errors, _ = validate_all(base_dir)
        if errors:
            for e in errors:
                sys.stderr.write(f"ERROR: {e}\n")
            return 1
        sys.stdout.write(f"{prog}: updated task {tid} in {fname}\n")
        return 0

    sys.stderr.write(f"{prog}: task {target!r} not found in TODO*.md under {base_dir}\n")
    return 1


def cmd_append(base_dir: Path, argv: list[str]) -> int:
    prog = prog_name()
    body: str | None = None
    pos: list[str] = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-b", "--body", "-m", "--note"):
            if i + 1 >= len(argv):
                raise SystemExit(f"{prog}: {a} requires an argument")
            body = argv[i + 1]
            i += 2
        elif a.startswith("-"):
            raise SystemExit(f"{prog}: unknown option for append: {a}")
        else:
            pos.append(a)
            i += 1

    if len(pos) != 1:
        raise SystemExit(f"{prog}: usage: {prog} append <ID> [-b TEXT]")
    target = pos[0].strip().upper()
    if body is None:
        body = _read_stdin_if_piped()
    if not body or not body.strip():
        raise SystemExit(f"{prog}: append requires non-empty text via -b TEXT or stdin")

    for fname in TASK_FILES:
        p = base_dir / fname
        if not p.is_file():
            continue
        lines = read_if_exists(p).splitlines()
        in_fence = False
        start_idx: int | None = None
        end_idx: int | None = None
        for idx, line in enumerate(lines):
            if line.lstrip().startswith(FENCE):
                in_fence = not in_fence
            if not in_fence:
                if start_idx is not None and (line.startswith("### ") or line.startswith("## ")):
                    end_idx = idx
                    break
                if start_idx is None and line.startswith("### "):
                    m = HEADING_RE.match(line)
                    if m and m.group(3).upper() == target:
                        start_idx = idx
        if start_idx is None:
            continue
        if end_idx is None:
            end_idx = len(lines)
        sec_lines = lines[start_idx:end_idx]
        while sec_lines and not sec_lines[-1].strip():
            sec_lines.pop()
        sec_lines.extend(["", body.strip(), ""])
        updated_lines = lines[:start_idx] + sec_lines + lines[end_idx:]
        new_text = re.sub(r"\n{3,}", "\n\n", "\n".join(updated_lines).rstrip()) + "\n"
        p.write_text(new_text, encoding="utf-8")
        errors, _ = validate_all(base_dir)
        if errors:
            for e in errors:
                sys.stderr.write(f"ERROR: {e}\n")
            return 1
        sys.stdout.write(f"{prog}: appended to {target} in {fname}\n")
        return 0

    sys.stderr.write(f"{prog}: task {target!r} not found in TODO*.md under {base_dir}\n")
    return 1


def cmd_resume(base_dir: Path, argv: list[str]) -> int:
    prog = prog_name()
    todo_path = base_dir / "TODO.md"
    if not todo_path.is_file():
        sys.stderr.write(f"{prog}: no TODO.md found in {base_dir} (run '{prog} init' to create one)\n")
        return 1
    body: str | None = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-b", "--body", "-m", "--note"):
            if i + 1 >= len(argv):
                raise SystemExit(f"{prog}: {a} requires an argument")
            body = argv[i + 1]
            i += 2
        else:
            raise SystemExit(f"{prog}: usage: {prog} resume [-b TEXT] (or pass text on stdin)")
    if body is None:
        body = _read_stdin_if_piped()
    if body is None or not body.strip():
        # If no body provided and stdin is a tty, print current Resume
        lines = read_if_exists(todo_path).splitlines()
        in_resume = False
        out: list[str] = []
        for line in lines:
            if line.startswith("## "):
                if line[3:].strip() == "Resume":
                    in_resume = True
                    continue
                elif in_resume:
                    break
            if in_resume:
                out.append(line)
        sys.stdout.write("\n".join(out).strip() + "\n")
        return 0

    lines = read_if_exists(todo_path).splitlines()
    in_fence = False
    res_start: int | None = None
    res_end: int | None = None
    for idx, line in enumerate(lines):
        if line.lstrip().startswith(FENCE):
            in_fence = not in_fence
        if not in_fence and line.startswith("## "):
            sec = line[3:].strip()
            if sec == "Resume" and res_start is None:
                res_start = idx
            elif res_start is not None and res_end is None:
                res_end = idx
                break
    if res_start is None:
        sys.stderr.write(f"{prog}: '## Resume' section not found in {todo_path}\n")
        return 1
    if res_end is None:
        res_end = len(lines)
    updated_lines = lines[: res_start + 1] + ["", body.strip(), ""] + lines[res_end:]
    new_text = re.sub(r"\n{3,}", "\n\n", "\n".join(updated_lines).rstrip()) + "\n"
    todo_path.write_text(new_text, encoding="utf-8")
    errors, _ = validate_all(base_dir)
    if errors:
        for e in errors:
            sys.stderr.write(f"ERROR: {e}\n")
        return 1
    sys.stdout.write(f"{prog}: updated ## Resume in {todo_path}\n")
    return 0
