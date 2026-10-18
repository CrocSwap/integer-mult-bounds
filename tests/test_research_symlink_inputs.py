"""Filesystem aliases must not hide registered replay dependencies. Apache-2.0."""
import errno
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import research_package as runner
import new_research_package as scaffold
sys.path.pop(0)


class SymlinkInputTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.git("init", "-q")
        for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid"),
                           ("core.autocrlf", "false")):
            self.git("config", key, value)
        for name, text in {
            "src/dep.json": '{"proof":1}',
            "docs/research/agent-task-catalog.json": json.dumps({
                "priority_revision": 5,
                "tracks": [{"tasks": [{"id": "fixture", "question": "Audit dependency paths"}]}]}),
            "certificates/selected-result.json": "{}",
        }.items():
            self.write(name, text)
        self.write("scripts/research_package.py", (ROOT / "scripts/research_package.py").read_text())
        self.commit()
        self.target = scaffold.create(self.root, "alpha", "fixture", "Fixture")
        task_path = self.target / "TASK.json"
        task = json.loads(task_path.read_text())
        task.update(bottleneck_link="Replay dependency coverage", stop_rule="One path fixture",
                    outcome="completed", evidence="Actual Git and filesystem controls",
                    ai_assistance="Test fixture", open_questions=[],
                    no_open_questions_reason="Regression fixture only")
        task_path.write_text(json.dumps(task))
        self.manifest = json.loads((self.target / "VERIFY.json").read_text())
        self.manifest["status"] = "ready"
        self.manifest["commands"][0]["checks"] = "Dependency fixture"
        self.input("src/dep.json")

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root,
                                       stderr=subprocess.PIPE, timeout=30).decode().strip()

    def commit(self):
        self.git("add", "--all")
        self.git("-c", "maintenance.auto=false", "-c", "gc.auto=0", "commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD")

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def input(self, name):
        self.manifest["inputs"] = [name]
        (self.target / "VERIFY.json").write_text(json.dumps(self.manifest))

    def link(self, name, target, directory=False):
        try:
            (self.root / name).symlink_to(target, target_is_directory=directory)
        except OSError as exc:
            if os.name == "nt" and getattr(exc, "winerror", None) == 1314:
                self.skipTest("Windows symlink privilege is unavailable")
            raise

    def test_regular_dependency_validates_and_selects(self):
        runner.validate(self.root, "research/alpha")
        self.assertEqual(runner.relative_file(self.root, "src/dep.json").read_bytes(), b'{"proof":1}')
        self.assertEqual(runner.plan(self.root, ["src/dep.json"]), ["research/alpha"])
        self.assertEqual(runner.plan(self.root, ["unrelated.txt"]), [])

    def test_parent_alias_rejected_in_full_metadata_and_planning(self):
        self.link("alias", "src", directory=True)
        self.input("alias/dep.json")
        # This additional dependency is intentionally not a SOURCES input pin.
        # Such inputs are supported, so provenance checks cannot reject the alias.
        with self.assertRaisesRegex(ValueError, "symlink.*alias/dep.json"):
            runner.validate(self.root, "research/alpha")
        for changed in (["src/dep.json"], ["unrelated.txt"], ["scripts/research_package.py"]):
            with self.subTest(changed=changed), self.assertRaisesRegex(ValueError, "symlink"):
                runner.plan(self.root, changed)

    def test_leaf_alias_rejected_in_resolution_and_planning(self):
        self.link("leaf.json", "src/dep.json")
        self.input("leaf.json")
        with self.assertRaisesRegex(ValueError, "symlink"):
            runner.relative_file(self.root, "leaf.json")
        with self.assertRaisesRegex(ValueError, "symlink"):
            runner.plan(self.root, ["src/dep.json"])

    def test_broken_cyclic_external_and_nested_links_reject_before_following(self):
        with tempfile.TemporaryDirectory() as external:
            for name, target in (("broken", "absent"), ("cycle", "cycle"),
                                 ("external", external), ("src/nested", ".")):
                self.link(name, target, directory=True)
                dependency = name + "/absent.json"
                self.input(dependency)
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "symlink"):
                    runner.plan(self.root, ["unrelated.txt"])
                with self.assertRaisesRegex(ValueError, "symlink"):
                    runner.relative_file(self.root, dependency)

    def test_deleted_leaf_and_deleted_parent_still_select(self):
        (self.root / "src/dep.json").unlink()
        for remove_parent in (False, True):
            if remove_parent:
                (self.root / "src").rmdir()
            with self.subTest(remove_parent=remove_parent):
                self.assertEqual(runner.plan(self.root, ["src/dep.json"]), ["research/alpha"])
                with self.assertRaisesRegex(ValueError, "missing or external"):
                    runner.relative_file(self.root, "src/dep.json")

    def test_parent_replaced_by_file_retains_deletion_selection(self):
        (self.root / "src/dep.json").unlink()
        (self.root / "src").rmdir()
        self.write("src", "replacement")
        self.assertEqual(runner.plan(self.root, ["src/dep.json", "src"]), ["research/alpha"])
        with self.assertRaisesRegex(ValueError, "missing or external"):
            runner.relative_file(self.root, "src/dep.json")

    def test_component_io_errors_propagate(self):
        original = Path.lstat
        for component in ("src", "src/dep.json"):
            for code in (errno.EACCES, errno.EIO):
                def failed(path, *args, **kwargs):
                    if path == self.root / component:
                        raise OSError(code, "injected component failure")
                    return original(path, *args, **kwargs)
                with self.subTest(component=component, code=code), patch.object(Path, "lstat", failed):
                    with self.assertRaisesRegex(OSError, "injected component failure"):
                        runner.relative_file(self.root, "src/dep.json")
                    with self.assertRaisesRegex(OSError, "injected component failure"):
                        runner.plan(self.root, ["src/dep.json"])

    def test_actual_git_target_change_fails_cli_without_partial_matrix(self):
        self.link("alias", "src", directory=True)
        self.input("alias/dep.json")
        base = self.commit()
        self.write("src/dep.json", '{"proof":2}')
        self.commit()
        self.assertEqual(self.git("diff", "--name-only", base, "HEAD"), "src/dep.json")
        output = self.root / "github-output.txt"
        output.write_text("existing-output\n")
        result = self.cli(base, output)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("symlink", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(output.read_text(), "existing-output\n")
        self.input("src/dep.json")
        canonical_base = self.commit()
        self.write("src/dep.json", '{"proof":3}')
        self.commit()
        self.assertEqual(self.git("diff", "--name-only", canonical_base, "HEAD"), "src/dep.json")
        good = self.cli(canonical_base, output)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(good.stdout), {"include": [{"package": "research/alpha"}]})
        self.assertIn("count=1\n", output.read_text())

    @unittest.skipIf(os.name == "nt" or getattr(os, "geteuid", lambda: -1)() == 0,
                     "requires POSIX permissions without root bypass")
    def test_inaccessible_component_fails_cli_without_partial_matrix(self):
        base = self.commit()
        output = self.root / "github-output.txt"
        output.write_text("existing-output\n")
        blocked = self.root / "src"
        mode = blocked.stat().st_mode
        blocked.chmod(0)
        try:
            result = self.cli(base, output)
        finally:
            blocked.chmod(mode)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Permission denied", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(output.read_text(), "existing-output\n")

    def cli(self, base, output):
        return subprocess.run(
            [sys.executable, "-I", "-O", "-B", str(self.root / "scripts/research_package.py"),
             "--changed-since", base, "--github-output", str(output)],
            cwd=self.root, capture_output=True, text=True, timeout=30)


if __name__ == "__main__":
    unittest.main()
