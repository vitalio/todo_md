#!/usr/bin/env python3
"""Tests for todo_md and install.sh."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "todo_md"
INSTALL_SH = ROOT / "install.sh"


class TestTodoMd(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="todo_md_test_"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_help_version_and_agents(self):
        rh = subprocess.run([str(SCRIPT), "-h"], capture_output=True, text=True, check=False)
        self.assertEqual(rh.returncode, 0)
        self.assertIn("Usage:", rh.stdout)

        rv = subprocess.run([str(SCRIPT), "--version"], capture_output=True, text=True, check=False)
        self.assertEqual(rv.returncode, 0)
        ver = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(rv.stdout.strip(), f"todo_md {ver}")

        ra = subprocess.run([str(SCRIPT), "agents"], capture_output=True, text=True, check=False)
        self.assertEqual(ra.returncode, 0)
        self.assertIn("Git beats Resume", ra.stdout)
        self.assertIn("TODO_ARCHIVE.md", ra.stdout)

    def test_init_summary_list_show_ids_and_check(self):
        r_init = subprocess.run([str(SCRIPT), "init"], cwd=str(self.tmp), capture_output=True, text=True, check=False)
        self.assertEqual(r_init.returncode, 0)
        self.assertTrue((self.tmp / "TODO.md").is_file())
        self.assertTrue((self.tmp / "TODO_PLAN.md").is_file())
        self.assertTrue((self.tmp / "TODO_ARCHIVE.md").is_file())

        (self.tmp / "TODO_PLAN.md").write_text("# Plan\n\n## Deferred Tasks\n\n### ⚪ [NEW] P2: Planned item\nDetails here.\n", encoding="utf-8")
        (self.tmp / "TODO_ARCHIVE.md").write_text("# Archive\n\n## Archive\n\n### ✅ [DONE] A5: Old item\nDone.\n", encoding="utf-8")

        r_sum = subprocess.run([str(SCRIPT)], cwd=str(self.tmp), capture_output=True, text=True, check=False)
        self.assertEqual(r_sum.returncode, 0)
        self.assertIn("IDs in use: A:5 F:1 P:2  (next free: A6, F2, P3)", r_sum.stdout)

        r_show = subprocess.run([str(SCRIPT), "P2"], cwd=str(self.tmp), capture_output=True, text=True, check=False)
        self.assertEqual(r_show.returncode, 0)
        self.assertIn("TODO_PLAN.md:5", r_show.stdout)
        self.assertIn("Planned item", r_show.stdout)

        r_list = subprocess.run([str(SCRIPT), "list", "all"], cwd=str(self.tmp), capture_output=True, text=True, check=False)
        self.assertEqual(r_list.returncode, 0)
        self.assertIn("F1", r_list.stdout)
        self.assertIn("P2", r_list.stdout)
        self.assertIn("A5", r_list.stdout)

        r_chk = subprocess.run([str(SCRIPT), "check"], cwd=str(self.tmp), capture_output=True, text=True, check=False)
        self.assertEqual(r_chk.returncode, 0, r_chk.stderr)

        # Test status, activate, defer, done, cancel, archive
        r_st = subprocess.run([str(SCRIPT), "status", "F1", "WIP", "-m", "in progress"], cwd=str(self.tmp), capture_output=True, text=True, check=False)
        self.assertEqual(r_st.returncode, 0, r_st.stderr)
        self.assertIn("### 🔵 [WIP] F1: Initial task — *in progress*", (self.tmp / "TODO.md").read_text(encoding="utf-8"))

        r_act = subprocess.run([str(SCRIPT), "activate", "P2", "--wip"], cwd=str(self.tmp), capture_output=True, text=True, check=False)
        self.assertEqual(r_act.returncode, 0, r_act.stderr)
        self.assertIn("### 🔵 [WIP] P2: Planned item", (self.tmp / "TODO.md").read_text(encoding="utf-8"))
        self.assertNotIn("P2", (self.tmp / "TODO_PLAN.md").read_text(encoding="utf-8"))

        r_def = subprocess.run([str(SCRIPT), "defer", "P2"], cwd=str(self.tmp), capture_output=True, text=True, check=False)
        self.assertEqual(r_def.returncode, 0, r_def.stderr)
        self.assertIn("### ⚪ [NEW] P2: Planned item", (self.tmp / "TODO_PLAN.md").read_text(encoding="utf-8"))

        r_done = subprocess.run([str(SCRIPT), "done", "F1", "-m", "commit 1234567"], cwd=str(self.tmp), capture_output=True, text=True, check=False)
        self.assertEqual(r_done.returncode, 0, r_done.stderr)
        self.assertNotIn("F1:", (self.tmp / "TODO.md").read_text(encoding="utf-8"))
        arch_out = subprocess.run([str(SCRIPT), "archive"], cwd=str(self.tmp), capture_output=True, text=True, check=False)
        self.assertEqual(arch_out.returncode, 0)
        self.assertIn("### ✅ [DONE] F1: Initial task — *commit 1234567*", arch_out.stdout)

        r_can = subprocess.run([str(SCRIPT), "cancel", "P2", "-m", "not needed"], cwd=str(self.tmp), capture_output=True, text=True, check=False)
        self.assertEqual(r_can.returncode, 0, r_can.stderr)
        self.assertIn("### ❌ [CANCELED] P2: Planned item — *not needed*", (self.tmp / "TODO_ARCHIVE.md").read_text(encoding="utf-8"))

        # Duplicate ID should fail check
        (self.tmp / "TODO_PLAN.md").write_text("# Plan\n\n## Deferred Tasks\n\n### ⚪ [NEW] F1: Dup ID\n", encoding="utf-8")
        r_bad = subprocess.run([str(SCRIPT), "check"], cwd=str(self.tmp), capture_output=True, text=True, check=False)
        self.assertNotEqual(r_bad.returncode, 0)
        self.assertIn("duplicate task ID F1", r_bad.stderr)

    def test_install_sh(self):
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        env = {**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"}
        r = subprocess.run(["sh", str(INSTALL_SH), "--dir", str(bin_dir), "--yes"], capture_output=True, text=True, env=env, check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((bin_dir / "todo_md").is_file())


if __name__ == "__main__":
    unittest.main()
