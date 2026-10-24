"""Local overlap coverage must expose notes omitted from a Git checkout."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("git"), "Git is needed for checkout fixtures")
class LocalOverlapCoverageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "repo"
        self.root.mkdir()
        self.cache = Path(temporary.name) / "cache.json"
        sources = {name: {"fetched_at": datetime.now(timezone.utc).isoformat(),
                          "complete_pagination": True, "records": []}
                   for name in ("open_prs", "discussions")}
        self.cache.write_text(json.dumps({"schema_version": 1,
                                         "repository": "CrocSwap/integer-mult-bounds",
                                         "sources": sources}), encoding="utf-8")
        self.omitted = "research/omitted κ\npackage"
        for path, body in {
            "scripts/find_overlap.py": (ROOT / "scripts/find_overlap.py").read_text(encoding="utf-8"),
            "scripts/research_package.py": (ROOT / "scripts/research_package.py").read_text(encoding="utf-8"),
            "research/kept/README.md": "needle local note",
            "research/kept/TASK.json": '{"scope": "needle local task"}',
            f"{self.omitted}/README.md": "only-omitted needle",
            f"{self.omitted}/TASK.json": '{"scope": "only-omitted needle"}',
            "docs/research/pr-ledger.md": "ledger needle",
            "research/kept/vendor/README.md": "out-of-scope nested note",
            "research/kept/NOTES.md": "out-of-scope arbitrary note",
        }.items():
            self.write(path, body)
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                 "commit", "-qm", "overlap fixture")
        self.head = self.git("rev-parse", "HEAD").strip()

    def write(self, name, body):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, encoding="utf-8").stdout

    def report(self, *args, text=False, env=None):
        original = self.cache.read_bytes()
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(self.root / "scripts/find_overlap.py"),
             "--cache", str(self.cache), "--max-age", "3600",
             *([] if text else ["--json"]), *args],
            cwd=self.root, capture_output=True, encoding="utf-8", timeout=15, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.cache.read_bytes(), original)
        return result.stdout if text else json.loads(result.stdout)

    def sparse(self, cone=False):
        if cone:
            self.git("sparse-checkout", "init", "--cone", "--sparse-index")
            self.git("sparse-checkout", "set", "scripts", "research/kept")
        else:
            self.git("sparse-checkout", "init", "--no-cone")
            self.git("sparse-checkout", "set", "/scripts/", "/research/kept/")

    def test_full_checkout_uses_working_edits_and_untracked_notes(self):
        self.write("research/kept/README.md", "edited needle")
        self.write("research/untracked/README.md", "new needle")
        report = self.report("needle")
        self.assertEqual(report["local_records"], 6)
        self.assertEqual(report["coverage"]["local"], {
            "head": self.head, "records": 6, "head_records": 5,
            "complete_head_inventory": True, "unsearched_head_paths": []})
        self.assertEqual(report["warnings"], [])
        self.assertEqual({m["excerpt"] for m in report["matches"] if "README.md" in m["path"]},
                         {"edited needle", "new needle", "only-omitted needle"})

    def test_sparse_gaps_survive_no_hits_and_result_limits(self):
        expected = sorted(["docs/research/pr-ledger.md", f"{self.omitted}/README.md",
                           f"{self.omitted}/TASK.json"])
        for cone in (False, True):
            with self.subTest(cone=cone):
                self.sparse(cone)
                report = self.report("only-omitted", "--offline", "--limit", "1")
                self.assertEqual(report["matches_total"], 0)
                self.assertEqual(report["coverage"]["local"], {
                    "head": self.head, "records": 2, "head_records": 5,
                    "complete_head_inventory": False, "unsearched_head_paths": expected})
                self.assertTrue(any("local: 3 HEAD note paths were not searched" in warning
                                    for warning in report["warnings"]))
                limited = self.report("needle", "--limit", "1")
                self.assertEqual(limited["matches_total"], 2)
                self.assertEqual(len(limited["matches"]), 1)
                self.assertEqual(limited["coverage"]["local"], report["coverage"]["local"])
                output = self.report("only-omitted", text=True)
                self.assertIn('"complete_head_inventory": false', output)
                self.assertIn('"unsearched_head_paths_count": 3', output)
                self.assertNotIn('"unsearched_head_paths":', output)
                self.assertIn("WARNING: local: 3 HEAD note paths were not searched", output)
                self.assertFalse((self.root / self.omitted).exists())
                self.git("sparse-checkout", "disable")
                restored = self.report("only-omitted")
                self.assertTrue(restored["coverage"]["local"]["complete_head_inventory"])
                self.assertEqual(restored["matches_total"], 2)

    def test_ordinary_deleted_note_is_also_unsearched(self):
        (self.root / "research/kept/README.md").unlink()
        report = self.report("needle")
        self.assertEqual(report["coverage"]["local"]["unsearched_head_paths"],
                         ["research/kept/README.md"])
        self.assertFalse(report["coverage"]["local"]["complete_head_inventory"])

    def test_skipped_symlink_cannot_count_as_a_searched_head_note(self):
        note = self.root / "research/kept/README.md"
        note.unlink()
        try:
            note.symlink_to("TASK.json")
        except OSError:
            self.skipTest("symlinks unavailable")
        report = self.report("needle")
        self.assertEqual(report["coverage"]["local"]["unsearched_head_paths"],
                         ["research/kept/README.md"])
        self.assertEqual(report["local_records"], 4)

    def test_empty_head_note_inventory_is_complete(self):
        self.git("rm", "-qr", "research", "docs")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                 "commit", "-qm", "no notes")
        report = self.report("needle")
        self.assertEqual(report["coverage"]["local"]["head_records"], 0)
        self.assertTrue(report["coverage"]["local"]["complete_head_inventory"])
        self.assertEqual(report["warnings"], [])

    def test_missing_git_or_repository_keeps_search_but_marks_coverage_unknown(self):
        for mode in ("missing-git", "not-a-repository", "unborn-head"):
            with self.subTest(mode=mode):
                if mode == "not-a-repository":
                    shutil.rmtree(self.root / ".git")
                elif mode == "unborn-head":
                    self.git("init", "-q")
                env = {**os.environ, "PATH": ""} if mode == "missing-git" else None
                report = self.report("needle", env=env)
                coverage = report["coverage"]["local"]
                self.assertIsNone(coverage["complete_head_inventory"])
                self.assertIsNone(coverage["head_records"])
                self.assertIsNone(coverage["unsearched_head_paths"])
                self.assertEqual(report["matches_total"], 5)
                self.assertTrue(any(w.startswith("local: HEAD note inventory unavailable;")
                                    for w in report["warnings"]))


if __name__ == "__main__":
    unittest.main()
