"""Git path bytes must survive the local overlap coverage inventory.

Object-only fixtures also exercise names that Windows cannot materialize.
Prepared for josecarlosgonzalezroque-design with OpenAI Codex assistance.
Retains the local coverage contract introduced by PR4419. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import find_overlap as overlap
sys.path.pop(0)


@unittest.skipUnless(shutil.which("git"), "Git is needed for object fixtures")
class GitPathCoverageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "repo"
        self.root.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")

    def git(self, *args, data=None):
        return subprocess.run(["git", *args], cwd=self.root, input=data,
                              capture_output=True, check=True, timeout=15).stdout

    def inventory(self, package_names):
        # Construct trees directly: no checkout or platform filename support
        # is needed to inspect the repository's NUL-delimited path inventory.
        blob = self.git("hash-object", "-w", "--stdin", data=b"needle\n").strip()
        note_tree = self.git("mktree", "-z", data=b"100644 blob " + blob + b"\tREADME.md\0").strip()
        entries = [b"040000 tree " + note_tree + b"\t" + name + b"\0"
                   for name in package_names]
        research = self.git("mktree", "-z", data=b"".join(entries)).strip()
        tree = self.git("mktree", "-z", data=b"040000 tree " + research + b"\tresearch\0").strip()
        head = self.git("-c", "commit.gpgsign=false", "commit-tree", tree.decode("ascii"),
                        data=b"path fixture\n").strip().decode("ascii")
        self.git("update-ref", "HEAD", head)
        return head, sorted((b"research/" + name + b"/README.md").decode("utf-8", "surrogateescape")
                            for name in package_names)

    def test_cr_lf_and_crlf_paths_remain_distinct(self):
        head, expected = self.inventory([b"line\rbreak", b"line\nbreak", b"line\r\nbreak"])
        coverage, warnings = overlap.local_coverage(self.root, [])
        self.assertEqual(coverage["head"], head)
        self.assertEqual(coverage["head_records"], 3)
        self.assertEqual(coverage["unsearched_head_paths"], expected)
        self.assertFalse(coverage["complete_head_inventory"])
        self.assertEqual(len(warnings), 1)
        self.assertIn("3 HEAD note paths were not searched", warnings[0])

    def test_lf_record_cannot_hide_unsearched_cr_paths(self):
        _, expected = self.inventory([b"line\rbreak", b"line\nbreak", b"line\r\nbreak"])
        # The input to local_coverage is the already searched note inventory.
        # A distinct LF note must not count as either omitted CR variant.
        searched = "research/line\nbreak/README.md"
        coverage, warnings = overlap.local_coverage(self.root, [{"path": searched}])
        self.assertFalse(coverage["complete_head_inventory"])
        self.assertEqual(coverage["head_records"], 3)
        self.assertEqual(coverage["unsearched_head_paths"], [p for p in expected if p != searched])
        self.assertIn("2 HEAD note paths were not searched", warnings[0])

    def test_exact_records_complete_the_inventory(self):
        _, expected = self.inventory([b"line\rbreak", b"line\nbreak", b"line\r\nbreak"])
        coverage, warnings = overlap.local_coverage(self.root, [{"path": p} for p in expected])
        self.assertEqual(coverage["head_records"], 3)
        self.assertTrue(coverage["complete_head_inventory"])
        self.assertEqual(coverage["unsearched_head_paths"], [])
        self.assertEqual(warnings, [])

    def test_tabs_unicode_and_non_utf8_bytes_are_preserved(self):
        _, expected = self.inventory([b"tab\tname", "unicode-κ".encode("utf-8"), b"raw-\xff"])
        coverage, warnings = overlap.local_coverage(self.root, [])
        self.assertEqual(coverage["unsearched_head_paths"], expected)
        self.assertEqual(coverage["head_records"], 3)
        self.assertEqual(json.loads(json.dumps(coverage)), coverage)
        self.assertEqual(len(warnings), 1)

    def test_cli_json_preserves_paths_and_search_results(self):
        head, expected = self.inventory([b"line\rbreak", b"line\nbreak", b"line\r\nbreak"])
        scripts = self.root / "scripts"
        scripts.mkdir()
        for name in ("find_overlap.py", "research_package.py"):
            shutil.copyfile(ROOT / "scripts" / name, scripts / name)
        note = self.root / "research/kept/README.md"
        note.parent.mkdir(parents=True)
        note.write_bytes(b"needle from the working tree\n")
        cache = self.root.parent / "cache.json"
        cache.write_text(json.dumps({"schema_version": 1, "repository": overlap.REPO,
                                     "sources": {}}), encoding="utf-8")
        original = cache.read_bytes()
        result = subprocess.run(
            [sys.executable, *(["-O"] if sys.flags.optimize else []), "-I", "-B",
             str(scripts / "find_overlap.py"), "needle", "--offline", "--json",
             "--limit", "1", "--cache", str(cache)], cwd=self.root,
            capture_output=True, check=True, timeout=15)
        report = json.loads(result.stdout)
        self.assertEqual(report["coverage"]["local"]["head"], head)
        self.assertEqual(report["coverage"]["local"]["head_records"], 3)
        self.assertEqual(report["coverage"]["local"]["unsearched_head_paths"], expected)
        self.assertFalse(report["coverage"]["local"]["complete_head_inventory"])
        self.assertEqual(report["matches_total"], 1)
        self.assertIn("needle from the working tree", report["matches"][0]["excerpt"])
        self.assertEqual(cache.read_bytes(), original)

    def test_unborn_head_keeps_coverage_unknown(self):
        coverage, warnings = overlap.local_coverage(self.root, [])
        self.assertIsNone(coverage["head"])
        self.assertIsNone(coverage["head_records"])
        self.assertIsNone(coverage["complete_head_inventory"])
        self.assertIsNone(coverage["unsearched_head_paths"])
        self.assertEqual(len(warnings), 1)
        self.assertIn("HEAD note inventory unavailable", warnings[0])

    def test_missing_git_keeps_coverage_unknown(self):
        with patch.object(overlap.subprocess, "run", side_effect=FileNotFoundError("missing git")):
            coverage, warnings = overlap.local_coverage(self.root, [])
        self.assertIsNone(coverage["complete_head_inventory"])
        self.assertEqual(len(warnings), 1)
        self.assertIn("missing git", warnings[0])


if __name__ == "__main__":
    unittest.main()
