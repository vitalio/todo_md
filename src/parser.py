def resolve_target_dir(explicit: str | None = None) -> Path:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if not p.is_dir():
            raise SystemExit(f"{prog_name()}: directory not found: {explicit}")
        return p
    env_cwd = os.environ.get("TODO_MD_CWD", "").strip()
    if env_cwd:
        return Path(env_cwd).expanduser().resolve()
    cwd = Path.cwd().resolve()
    if (cwd / "TODO.md").is_file():
        return cwd
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
        if r.returncode == 0 and r.stdout.strip():
            groot = Path(r.stdout.strip()).resolve()
            if (groot / "TODO.md").is_file():
                return groot
    except OSError:
        pass
    return cwd


def read_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def _read_stdin_if_piped() -> str | None:
    try:
        if not sys.stdin.isatty():
            data = sys.stdin.read()
            return data if data.strip() else None
    except Exception:
        pass
    return None


def parse_tasks_in_text(text: str, filename: str) -> list[dict[str, object]]:
    tasks: list[dict[str, object]] = []
    in_fence = False
    current: dict[str, object] | None = None
    body_lines: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith(FENCE):
            in_fence = not in_fence
        if not in_fence and line.startswith("# "):
            if current is not None:
                current["section"] = "\n".join(body_lines).rstrip()
                tasks.append(current)
                current = None
                body_lines = []
            m = HEADING_RE.match(line)
            if m:
                emoji, status, tid, title = m.groups()
                current = {
                    "id": tid,
                    "status": status,
                    "emoji": emoji,
                    "title": title,
                    "file": filename,
                    "line": lineno,
                    "heading": line,
                }
                body_lines = [line]
                continue
        if current is not None:
            body_lines.append(line)
    if current is not None:
        current["section"] = "\n".join(body_lines).rstrip()
        tasks.append(current)
    return tasks


def collect_all_tasks(base_dir: Path) -> list[dict[str, object]]:
    all_tasks: list[dict[str, object]] = []
    for fname in TASK_FILES:
        p = base_dir / fname
        if p.is_file():
            all_tasks.extend(parse_tasks_in_text(read_if_exists(p), fname))
    return all_tasks


def highest_ids_in_use(base_dir: Path) -> dict[str, int]:
    top: dict[str, int] = {}
    for fname in TASK_FILES:
        text = read_if_exists(base_dir / fname)
        if not text:
            continue
        in_fence = False
        for line in text.splitlines():
            if line.lstrip().startswith(FENCE):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = ANY_ID_RE.match(line)
            if m:
                ident = m.group(1)
                prefix, num = ident[0], int(ident[1:])
                top[prefix] = max(top.get(prefix, 0), num)
    return top


def all_used_ids(base_dir: Path) -> set[str]:
    used: set[str] = set()
    for fname in TASK_FILES:
        text = read_if_exists(base_dir / fname)
        if not text:
            continue
        in_fence = False
        for line in text.splitlines():
            if line.lstrip().startswith(FENCE):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = ANY_ID_RE.match(line)
            if m:
                used.add(m.group(1).upper())
    return used


def next_free_id(base_dir: Path, prefix: str = "F") -> str:
    p = prefix.upper()
    if not re.fullmatch(r"[A-Za-z]", p):
        raise SystemExit(f"{prog_name()}: invalid ID prefix {prefix!r}; expected a single letter A-Z")
    top = highest_ids_in_use(base_dir)
    return f"{p}{top.get(p, 0) + 1}"


def format_ids_summary(top: dict[str, int]) -> str:
    if not top:
        return "[none]"
    used = " ".join(f"{k}:{v}" for k, v in sorted(top.items()))
    nxt = ", ".join(f"{k}{v + 1}" for k, v in sorted(top.items()))
    return f"{used}  (next free: {nxt})"


def _format_task_for_summary(task: dict[str, object], full: bool = False) -> str:
    sec = str(task["section"]).rstrip()
    status = str(task["status"])
    if full or status in ("WIP", "NEXT"):
        return sec
    lines = sec.splitlines()
    heading = lines[0]
    body_non_empty = [l for l in lines[1:] if l.strip()]
    if len(body_non_empty) <= 2:
        return sec
    tid = str(task["id"])
    extra = len(body_non_empty) - 1
    return f"{heading}\n\n{body_non_empty[0]}\n*(+{extra} more line{'s' if extra != 1 else ''} — run `{prog_name()} {tid}` to view full task)*"


def cmd_summary(base_dir: Path, full: bool = False) -> int:
    todo_path = base_dir / "TODO.md"
    if not todo_path.is_file():
        sys.stderr.write(f"{prog_name()}: no TODO.md found in {base_dir} (run '{prog_name()} init' to create one)\n")
        return 1
    todo_text = read_if_exists(todo_path).rstrip()
    active_tasks = parse_tasks_in_text(todo_text, "TODO.md")
    arch_tasks = parse_tasks_in_text(read_if_exists(base_dir / "TODO_ARCHIVE.md"), "TODO_ARCHIVE.md")
    top = highest_ids_in_use(base_dir)

    if active_tasks:
        if full or len(active_tasks) <= 5:
            sys.stdout.write(todo_text + "\n\n")
        else:
            rendered = [_format_task_for_summary(t, full=False) for t in active_tasks]
            sys.stdout.write("\n\n".join(rendered) + "\n\n")

    if not active_tasks:
        sys.stdout.write("*(No open tasks in TODO.md)*\n\n")
    sys.stdout.write("---\n")
    sys.stdout.write(f"IDs in use: {format_ids_summary(top)}\n")
    sys.stdout.write(f"Open in TODO.md: {len(active_tasks)} task(s) | Archived in TODO_ARCHIVE.md: {len(arch_tasks)} task(s)\n")
    return 0


def cmd_ids(base_dir: Path) -> int:
    top = highest_ids_in_use(base_dir)
    sys.stdout.write(f"IDs in use: {format_ids_summary(top)}\n")
    return 0


def cmd_show(base_dir: Path, task_id: str) -> int:
    target = task_id.strip().upper()
    top = highest_ids_in_use(base_dir)
    for t in collect_all_tasks(base_dir):
        if str(t["id"]).upper() == target:
            sys.stdout.write(f"# {t['file']}:{t['line']}\n{t['section']}\n\n---\nIDs in use: {format_ids_summary(top)}\n")
            return 0
    sys.stderr.write(f"{prog_name()}: task {target!r} not found in TODO*.md under {base_dir}\n")
    return 1


def cmd_list(base_dir: Path, filt: str | None = None) -> int:
    mode = (filt or "active").strip().lower()
    tasks = collect_all_tasks(base_dir)
    if mode in ("active", "open"):
        shown = [t for t in tasks if t["file"] == "TODO.md"]
    elif mode == "archive":
        shown = [t for t in tasks if t["file"] == "TODO_ARCHIVE.md"]
    elif mode == "all":
        shown = tasks
    elif mode.upper() in VALID_STATUSES:
        shown = [t for t in tasks if t["status"] == mode.upper()]
    else:
        raise SystemExit(f"{prog_name()}: unknown list filter {filt!r}; expected active, archive, all, or a status name")

    if not shown:
        sys.stdout.write(f"No matching tasks ({mode}) in {base_dir}\n")
    else:
        for t in shown:
            badge = f"{t['emoji']} [{t['status']}]"
            loc = str(t["file"])
            sys.stdout.write(f"  {str(t['id']):<6}  {badge:<14}  {loc:<16}  {t['title']}\n")
    top = highest_ids_in_use(base_dir)
    sys.stdout.write(f"\nIDs in use: {format_ids_summary(top)}\n")
    return 0


def validate_all(base_dir: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    seen_ids: dict[str, str] = {}
    has_archive = (base_dir / "TODO_ARCHIVE.md").is_file()
    if (base_dir / "TODO_PLAN.md").is_file():
        errors.append("TODO_PLAN.md: deprecated file exists (merge deferred tasks into TODO.md)")
    for fname in TASK_FILES:
        p = base_dir / fname
        if not p.is_file():
            continue
        text = read_if_exists(p)
        in_fence = False
        for lineno, line in enumerate(text.splitlines(), start=1):
            if line.lstrip().startswith(FENCE):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if line.startswith("# "):
                m = HEADING_RE.match(line)
                if not m:
                    errors.append(f"{fname}:{lineno}: invalid task heading format: {line}")
                    continue
                emoji, status, tid, title = m.groups()
                norm_emoji = "⏸️" if emoji.startswith("⏸") else emoji
                if VALID_STATUSES.get(status) != norm_emoji:
                    errors.append(f"{fname}:{lineno}: mismatched emoji {emoji} for status [{status}]")
                if title.endswith(",") or title.count("(") != title.count(")"):
                    errors.append(f"{fname}:{lineno}: truncated/malformed task heading title: {title!r}")
                loc = f"{fname}:{lineno}"
                if tid in seen_ids:
                    errors.append(f"{loc}: duplicate task ID {tid} (first seen at {seen_ids[tid]})")
                else:
                    seen_ids[tid] = loc
                if fname == "TODO.md" and has_archive and status in ("DONE", "CANCELED"):
                    errors.append(f"{loc}: {status} task {tid} should be moved to TODO_ARCHIVE.md")
                if fname == "TODO_ARCHIVE.md" and status not in ("DONE", "CANCELED"):
                    errors.append(f"{loc}: non-archived status [{status}] on task {tid} in TODO_ARCHIVE.md")

    return errors, len(seen_ids)
