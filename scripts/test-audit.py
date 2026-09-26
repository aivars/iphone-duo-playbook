#!/usr/bin/env python3
"""Exercise the audit as a CLI with disposable source fixtures."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parent / "duo-audit.sh"


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="duo-audit-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "App With Spaces"
        self.root.mkdir()

    def run_audit(self, *args, env=None):
        return subprocess.run(["/bin/bash", str(SCRIPT), str(self.root), *args],
                              capture_output=True, text=True, env=env)

    def test_empty_folder_succeeds(self):
        result = self.run_audit()
        self.assertEqual(result.returncode, 0, result.stderr)
        counts = re.findall(r"^[-A-Za-z/ ]+: (\d+)$", result.stdout, re.MULTILINE)
        self.assertEqual(counts, ["0"] * 9)

    def test_occurrences_details_and_exclusions(self):
        (self.root / "View.swift").write_text(
            'let screens = [UIScreen.main, UIScreen.current]\n'
            'Text("x").frame(width: 340).frame(height: 260)\n'
            'Button("Done") {}\n'
            'view.sheet(isPresented: $show) {}\n', encoding="utf-8")
        for directory in ["build", ".git", ".build", "DerivedData", "Pods", ".worktrees"]:
            (self.root / directory).mkdir()
            (self.root / directory / "Ignore.swift").write_text("UIScreen.main\n")
        (self.root / "Ignore.txt").write_text("UIScreen.main\n")
        result = self.run_audit("--details")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r"screen-based layout\s*: 2")
        self.assertRegex(result.stdout, r"fixed widths\s*: 1")
        self.assertRegex(result.stdout, r"fixed heights\s*: 1")
        self.assertRegex(result.stdout, r"sheets/covers\s*: 1")
        self.assertIn("View.swift:1:", result.stdout)
        self.assertNotIn("Ignore.swift:", result.stdout)

    def test_project_without_matching_settings_succeeds(self):
        project = self.root / "App.xcodeproj"
        project.mkdir()
        (project / "project.pbxproj").write_text("// no matching keys\n")
        self.assertEqual(self.run_audit().returncode, 0)

    def test_project_settings(self):
        project = self.root / "App.xcodeproj"
        project.mkdir()
        (project / "project.pbxproj").write_text("\tIPHONEOS_DEPLOYMENT_TARGET = 17.0;\n")
        result = self.run_audit()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("IPHONEOS_DEPLOYMENT_TARGET = 17.0;", result.stdout)

    def test_bad_arguments_fail(self):
        self.assertEqual(self.run_audit("--unknown").returncode, 2)
        self.root.rmdir()
        self.assertNotEqual(self.run_audit().returncode, 0)

    def test_read_error_is_not_reported_as_zero(self):
        # A controlled grep error also works when tests run with elevated privileges.
        tools = Path(self.temp.name) / "tools"
        tools.mkdir()
        grep = tools / "grep"
        grep.write_text('#!/bin/sh\necho "fixture read error" >&2\nexit 2\n')
        grep.chmod(0o755)
        env = dict(os.environ, PATH=f"{tools}:{os.environ['PATH']}")
        result = self.run_audit(env=env)
        self.assertEqual(result.returncode, 2)
        self.assertIn("counts are incomplete", result.stderr)


if __name__ == "__main__":
    unittest.main()
