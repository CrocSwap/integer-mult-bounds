"""Git input spelling is exact, independent of filesystem alias resolution."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GitInputSpellingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "repo"
        self.root.mkdir()
        self.output = Path(temporary.name) / "github-output"
        self.git("init", "-q")
        for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid"),
                           ("core.autocrlf", "false"), ("core.precomposeunicode", "false")):
            self.git("config", key, value)
        self.write("scripts/research_package.py", (ROOT / "scripts/research_package.py").read_bytes())
        self.write("src/dep.json", b"original\n")
        self.write("other.json", b"other\n")
        self.manifest("alpha", ["src/dep.json"])
        self.manifest("beta", ["other.json"])
        self.commit()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, stderr=subprocess.PIPE, timeout=15)

    def write(self, name, raw):
        target = self.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    def manifest(self, slug, inputs):
        self.write(f"research/{slug}/VERIFY.json", json.dumps({"inputs": inputs}).encode())

    def commit(self):
        self.git("add", "--all")
        self.git("-c", "maintenance.auto=false", "-c", "gc.auto=0", "commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD").decode().strip()

    def cli(self, base):
        self.output.write_text("existing-output\n", encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-B", str(self.root / "scripts/research_package.py"),
             "--changed-since", base, "--github-output", str(self.output)],
            cwd=self.root, capture_output=True, text=True, encoding="utf-8", timeout=15, check=False)

    def selected(self, base):
        result = self.cli(base)
        self.assertEqual(result.returncode, 0, result.stderr)
        matrix = json.loads(result.stdout)
        self.assertIn("matrix=" + json.dumps(matrix), self.output.read_text(encoding="utf-8"))
        return [entry["package"] for entry in matrix["include"]]

    def rejected(self, base, name):
        result = self.cli(base)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("exact Git-tracked input", result.stderr)
        self.assertIn(name, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(self.output.read_text(encoding="utf-8"), "existing-output\n")

    def test_case_aliases_reject_a_target_only_git_diff(self):
        for alias in ("SRC/dep.json", "src/DEP.json", "SRC/DEP.json"):
            with self.subTest(alias=alias):
                self.manifest("alpha", [alias])
                base = self.commit()
                self.write("src/dep.json", (alias + "\n").encode())
                self.commit()
                self.assertEqual(self.git("diff", "--name-only", "-z", base, "HEAD"), b"src/dep.json\0")
                self.rejected(base, alias)
                self.manifest("alpha", ["src/dep.json"])
                # Only the declaration changes; the same target-only Git delta is used.
                self.assertEqual(self.selected(base), ["research/alpha"])

    def test_canonical_deleted_parent_and_unrelated_changes(self):
        base = self.git("rev-parse", "HEAD").decode().strip()
        self.write("src/dep.json", b"changed\n")
        self.commit()
        self.assertEqual(self.selected(base), ["research/alpha"])
        base = self.git("rev-parse", "HEAD").decode().strip()
        self.write("other.json", b"unrelated to alpha\n")
        self.commit()
        self.assertEqual(self.selected(base), ["research/beta"])
        base = self.git("rev-parse", "HEAD").decode().strip()
        self.git("rm", "-qr", "src")
        self.commit()
        self.assertFalse((self.root / "src").exists())
        self.assertEqual(self.selected(base), ["research/alpha"])
        # A stale declaration cannot become a silently ignored input on a later delta.
        base = self.git("rev-parse", "HEAD").decode().strip()
        self.write("other.json", b"changed other\n")
        self.commit()
        self.rejected(base, "src/dep.json")

    def test_case_only_rename_selects_both_exact_consumers(self):
        self.manifest("beta", ["SRC/dep.json"])
        base = self.commit()
        self.git("mv", "src", "temporary-name")
        self.git("mv", "temporary-name", "SRC")
        self.commit()
        self.assertEqual(set(self.git("diff", "--no-renames", "--name-only", "-z", base, "HEAD").split(b"\0")),
                         {b"src/dep.json", b"SRC/dep.json", b""})
        self.assertEqual(self.selected(base), ["research/alpha", "research/beta"])

    def test_unicode_spelling_is_not_normalized(self):
        spellings = ("src/caf\u00e9.json", "src/cafe\u0301.json")
        self.write(spellings[0], b"original unicode\n")
        self.commit()
        # Some filesystems store the decomposed spelling. The tree, not the
        # requested filesystem spelling, defines the accepted declaration.
        stored = self.git("ls-tree", "-r", "--name-only", "-z", "HEAD").decode().split("\0")
        exact = next(name for name in stored if name in spellings)
        alias = next(name for name in spellings if name != exact)
        self.manifest("alpha", [alias])
        base = self.commit()
        self.write(exact, b"changed unicode\n")
        self.commit()
        self.assertIn(exact.encode() + b"\0", self.git("diff", "--name-only", "-z", base, "HEAD"))
        self.rejected(base, alias)
        self.manifest("alpha", [exact])
        self.assertEqual(self.selected(base), ["research/alpha"])

    @unittest.skipIf(sys.platform == "win32", "Windows forbids control characters in filenames")
    def test_nul_framing_preserves_spaces_tabs_and_newlines(self):
        names = ["src/space name.json", "src/tab\tname.json", "src/line\nname.json", "src/cr\rname.json"]
        for name in names:
            self.write(name, b"original\n")
        self.manifest("alpha", names)
        base = self.commit()
        for name in names:
            self.write(name, b"changed\n")
        self.commit()
        self.assertEqual(self.selected(base), ["research/alpha"])

    def test_untracked_and_staged_only_inputs_reject_until_committed(self):
        base = self.git("rev-parse", "HEAD").decode().strip()
        self.write("src/new.json", b"new\n")
        self.manifest("alpha", ["src/new.json"])
        self.rejected(base, "src/new.json")
        self.git("add", "src/new.json")
        self.rejected(base, "src/new.json")
        self.commit()
        self.assertEqual(self.selected(base), ["research/alpha"])

    def test_git_failure_cannot_publish_a_partial_matrix(self):
        (self.root / ".git").rename(self.root / "saved-git")
        result = self.cli("0")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("git", result.stderr.lower())
        self.assertEqual(result.stdout, "")
        self.assertEqual(self.output.read_text(encoding="utf-8"), "existing-output\n")

    def test_missing_head_cannot_publish_a_partial_matrix(self):
        # ls-files still succeeds, so this reaches the new ls-tree boundary.
        self.git("checkout", "--orphan", "unborn")
        self.assertIn(b"src/dep.json\0", self.git("ls-files", "-z"))
        result = self.cli("0")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("ls-tree", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(self.output.read_text(encoding="utf-8"), "existing-output\n")

    def test_metadata_uses_the_same_exact_head_inventory(self):
        # Complete, source-pinned fixture. The added VERIFY dependency is unpinned,
        # which is permitted, so provenance lookup cannot mask this boundary.
        from test_research_onboarding import PackageTests
        fixture = PackageTests("runTest")
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.ready()
        path = fixture.target / "VERIFY.json"
        manifest = json.loads(path.read_bytes())
        spec = importlib.util.spec_from_file_location("git_spelling_metadata", ROOT / "scripts/research_package.py")
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        runner.validate(fixture.root, "research/fixture")
        for name in ("INPUT.txt", "untracked.txt"):
            with self.subTest(name=name):
                if name == "untracked.txt":
                    (fixture.root / name).write_text("not committed\n", encoding="utf-8")
                manifest["inputs"] = ["input.txt", name]
                path.write_text(json.dumps(manifest), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "exact Git-tracked input"):
                    runner.validate(fixture.root, "research/fixture")
        manifest["inputs"] = ["input.txt"]
        path.write_text(json.dumps(manifest), encoding="utf-8")
        runner.validate(fixture.root, "research/fixture")


if __name__ == "__main__":
    unittest.main()
