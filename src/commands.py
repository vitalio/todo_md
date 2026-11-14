def cmd_check(base_dir: Path) -> int:
    errors, count = validate_all(base_dir)
    if errors:
        for e in errors:
            sys.stderr.write(f"ERROR: {e}\n")
        return 1
    sys.stdout.write(f"{prog_name()}: OK ({count} task(s) verified across TODO*.md)\n")
    return 0


def _default_todo_header(base_dir: Path) -> str:
    return ""


def _default_archive_header(base_dir: Path) -> str:
    return ""


def cmd_init(base_dir: Path, argv: list[str] | None = None, force: bool = False) -> int:
    prog = prog_name()
    pos: list[str] = []
    for a in argv or []:
        if a == "--force":
            force = True
        elif a.startswith("-"):
            raise SystemExit(f"{prog}: unknown option for init: {a}")
        else:
            pos.append(a)
    idea_text = " ".join(pos).strip() if pos else (_read_stdin_if_piped() or "").strip()
    todo_content = ""
    if idea_text:
        todo_content = f"# 🎯 [NEXT] F1: Project concept and initial design\n\n{idea_text}\n"
    templates = {
        "TODO.md": todo_content,
        "TODO_ARCHIVE.md": "",
    }
    created: list[str] = []
    for fname, content in templates.items():
        p = base_dir / fname
        if p.exists() and not force:
            continue
        p.write_text(content, encoding="utf-8")
        created.append(fname)
    if not created:
        sys.stdout.write(f"{prog}: TODO*.md files already exist in {base_dir} (use --force to overwrite)\n")
    else:
        sys.stdout.write(f"{prog}: initialized {', '.join(created)} in {base_dir}\n")
    return 0


def agents_markdown(prog: str | None = None) -> str:
    cmd = prog or prog_name()
    lines = [
        f"## Task management (`{cmd}` v{VERSION}: `TODO.md`, `TODO_ARCHIVE.md`)",
        "",
        f"Task state lives in two files — modify them via the `{cmd}` CLI rather than manual file edits:",
        "- `TODO.md` — all open tasks (`# <emoji> [<STATUS>] <ID>: <title>`).",
        "- `TODO_ARCHIVE.md` — completed (`✅ [DONE]`) and dropped (`❌ [CANCELED]`) tasks.",
        "",
        "### 1. Task lifecycle & priority statuses",
        "",
        "- **Repository scope only:** Record only tasks belonging to the current repository — never mix in tasks from other repositories worked on in the same chat session.",
        "- **7 task statuses** (`# <emoji> [<STATUS>] <ID>: <title> — *<optional note>*`):",
        "  - `🔵 [WIP]` — actively in progress (`TODO.md`, shown in full by default)",
        "  - `🎯 [NEXT]` — high-priority queue ready to start next (`TODO.md`, shown in full by default)",
        "  - `⚪ [NEW]` — planned backlog item (`TODO.md`)",
        "  - `⏸️ [HOLD]` — paused on external dependency (`TODO.md`, with reason)",
        "  - `❓ [QUESTION]` — blocked on human clarification (`TODO.md`, with question)",
        "  - `✅ [DONE]` — completed and verified (`TODO_ARCHIVE.md` only, with date and commit SHA)",
        "  - `❌ [CANCELED]` — dropped (`TODO_ARCHIVE.md` only, with reason)",
        f"- **Auto-assigned unique IDs (never pass, split, or reuse numbers):** Every `<ID>` (e.g. `F1`, `B1`, `P1`) appears in **at most one** file across `TODO*.md`. When adding a task, pass only the title (or an optional single-letter prefix like `F`, `B`, `P`) — `{cmd} add` automatically assigns and prints the next free ID.",
        f'- **Bootstrap from idea:** Run `{cmd} init "<idea>"` (or pipe idea text on `stdin`) to initialize `TODO.md` with `# 🎯 [NEXT] F1: Project concept and initial design`.',
        "",
        f"### 2. `{cmd}` CLI commands",
        "",
        "- **Inspect:**",
        f"  - `{cmd} [--full]` — print `TODO.md` overview (full `WIP`/`NEXT` tasks + compact backlog) and `IDs in use`",
        f"  - `{cmd} <ID>` / `{cmd} list [active|archive|all|<STATUS>]` — view full task `<ID>` or compact table",
        f"  - `{cmd} archive` / `{cmd} ids` — view `TODO_ARCHIVE.md` or next free IDs",
        "- **Create & edit tasks (body can be passed via `-b TEXT` or `stdin` heredoc):**",
        f'  - `{cmd} add [<PREFIX>] "<title>" [-p <PREFIX>] [--next] [--status WIP|NEXT|NEW|HOLD|QUESTION] [-m "<note>"] [-b "<body_md>"]` — auto-assigns and prints the new `<ID>` (default prefix `F`; do not pass a number)',
        f'  - `{cmd} edit <ID> [-t "<title>"] [-m "<note>"] [-b "<body_md>"]` — update title, note, or body of `<ID>`',
        f'  - `{cmd} append <ID> [-b "<text>"]` — append progress/notes to the end of task `<ID>` body',
        "- **Transitions & validation:**",
        f'  - `{cmd} status <ID> <WIP|NEXT|NEW|HOLD|QUESTION> [-m "<note>"]` — update status in place',
        f'  - `{cmd} next <ID> [-m "<note>"]` — promote `<ID>` to `🎯 [NEXT]` at the top of `TODO.md`',
        f'  - `{cmd} done <ID> [-m "<commit_sha>"]` / `{cmd} cancel <ID> [-m "<reason>"]` — close and move to `TODO_ARCHIVE.md`',
        f"  - `{cmd} check` — validate layout, headings, and unique IDs across `TODO.md` and `TODO_ARCHIVE.md`",
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
        if not in_fence and line.startswith("# "):
            if start_idx is not None:
                end_idx = idx
                break
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
        return f"# {emoji} [{status}] {tid}: {base_title} — *{final_note}*"
    return f"# {emoji} [{status}] {tid}: {base_title}"


def _insert_task_section(file_path: Path, section_lines: list[str], default_header: str = "", prepend: bool = False) -> None:
    if not file_path.is_file() or not file_path.read_text(encoding="utf-8").strip():
        file_path.write_text("\n".join(section_lines) + "\n", encoding="utf-8")
        return
    existing = file_path.read_text(encoding="utf-8")
    if not prepend:
        file_path.write_text(existing.rstrip() + "\n\n" + "\n".join(section_lines) + "\n", encoding="utf-8")
        return
    lines = existing.splitlines()
    in_fence = False
    insert_idx: int | None = None
    for idx, line in enumerate(lines):
        if line.lstrip().startswith(FENCE):
            in_fence = not in_fence
        if not in_fence and line.startswith("# "):
            m = HEADING_RE.match(line)
            if m and m.group(2) == "WIP":
                continue
            insert_idx = idx
            break
    if insert_idx is None:
        file_path.write_text(existing.rstrip() + "\n\n" + "\n".join(section_lines) + "\n", encoding="utf-8")
        return
    updated = lines[:insert_idx] + section_lines + [""] + lines[insert_idx:]
    new_text = re.sub(r"\n{3,}", "\n\n", "\n".join(updated).rstrip()) + "\n"
    file_path.write_text(new_text, encoding="utf-8")


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
    promote_top: bool = False,
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
            dest_file = "TODO.md"

    today_iso = date.today().isoformat()
    effective_note = note
    if final_status == "DONE":
        if effective_note and today_iso not in effective_note:
            effective_note = f"{today_iso}, {effective_note}"
        elif effective_note is None:
            _, existing_n = _strip_heading_note(str(found["title"]))
            if not existing_n:
                effective_note = today_iso

    sec_lines = list(found["lines"])  # type: ignore[arg-type]
    sec_lines[0] = _format_heading(final_status, str(found["id"]), str(found["title"]), note=effective_note)

    if dest_file == source_file and not promote_top:
        src_path = base_dir / source_file
        orig_lines = read_if_exists(src_path).splitlines()
        in_fence = False
        for idx, line in enumerate(orig_lines):
            if line.lstrip().startswith(FENCE):
                in_fence = not in_fence
            if not in_fence and line.startswith("# "):
                m = HEADING_RE.match(line)
                if m and m.group(3).upper() == target:
                    orig_lines[idx] = sec_lines[0]
                    break
        src_path.write_text("\n".join(orig_lines) + "\n", encoding="utf-8")
        sys.stdout.write(f"{prog_name()}: updated {target} -> [{final_status}] in {source_file}\n")
        return 0

    (base_dir / source_file).write_text(updated_source_text, encoding="utf-8")
    default_hdrs = {
        "TODO.md": _default_todo_header(base_dir),
        "TODO_ARCHIVE.md": _default_archive_header(base_dir),
    }
    _insert_task_section(
        base_dir / dest_file,
        sec_lines,
        default_hdrs[dest_file],
        prepend=(promote_top and dest_file == "TODO.md"),
    )
    if dest_file == source_file:
        sys.stdout.write(f"{prog_name()}: promoted {target} ([{final_status}]) to top of {dest_file}\n")
    else:
        sys.stdout.write(f"{prog_name()}: moved {target} ([{final_status}]) from {source_file} -> {dest_file}\n")
    return 0


def cmd_add(base_dir: Path, argv: list[str]) -> int:
    prog = prog_name()
    status = "NEW"
    prepend = False
    prefix: str | None = None
    note: str | None = None
    body: str | None = None
    pos: list[str] = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--next", "-n", "--top"):
            status = "NEXT"
            prepend = True
            i += 1
        elif a in ("-p", "--prefix"):
            if i + 1 >= len(argv):
                raise SystemExit(f"{prog}: {a} requires an argument")
            prefix = argv[i + 1].strip().upper()
            if not re.fullmatch(r"[A-Z]", prefix):
                raise SystemExit(f"{prog}: invalid ID prefix {argv[i + 1]!r}; expected a single letter A-Z")
            i += 2
        elif a in ("--status", "-s"):
            if i + 1 >= len(argv):
                raise SystemExit(f"{prog}: {a} requires an argument")
            status = argv[i + 1].upper()
            if status in ("WIP", "NEXT"):
                prepend = True
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

    if status not in ("WIP", "NEXT", "NEW", "HOLD", "QUESTION"):
        raise SystemExit(f"{prog}: add status must be WIP, NEXT, NEW, HOLD, or QUESTION (got {status!r})")

    if len(pos) == 1:
        tid = next_free_id(base_dir, prefix or "F")
        title = pos[0].strip()
    elif len(pos) == 2 and prefix is None:
        first, second = pos[0].strip(), pos[1].strip()
        if re.fullmatch(r"[A-Za-z]", first):
            tid = next_free_id(base_dir, first.upper())
            title = second
        elif re.fullmatch(r"[A-Za-z]\d+", first):
            tid = next_free_id(base_dir, first[0].upper())
            title = second
            if first.upper() != tid:
                sys.stderr.write(
                    f"{prog}: note: ignoring explicit ID {first.upper()}; auto-assigned {tid}\n"
                )
        else:
            raise SystemExit(f"{prog}: invalid ID prefix {first!r}; expected a single letter A-Z (e.g. F, B, P)")
    else:
        raise SystemExit(
            f"{prog}: usage: {prog} add [<PREFIX>] <TITLE> [-p PREFIX] [--next] [--status STATUS] [-m NOTE] [-b BODY]"
        )

    if not title:
        raise SystemExit(f"{prog}: task title cannot be empty")

    if body is None:
        body = _read_stdin_if_piped()

    heading = _format_heading(status, tid, title, note=note)
    sec_lines = [heading]
    if body and body.strip():
        sec_lines.extend(["", body.strip()])

    _insert_task_section(base_dir / "TODO.md", sec_lines, _default_todo_header(base_dir), prepend=prepend)
    errors, _ = validate_all(base_dir)
    if errors:
        for e in errors:
            sys.stderr.write(f"ERROR: {e}\n")
        return 1
    sys.stdout.write(f"{prog}: added {tid} ([{status}]) to TODO.md\n")
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
            if not in_fence and line.startswith("# "):
                if start_idx is not None:
                    end_idx = idx
                    break
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
            if not in_fence and line.startswith("# "):
                if start_idx is not None:
                    end_idx = idx
                    break
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
