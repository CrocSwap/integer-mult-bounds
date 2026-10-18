"""Task selection must be reproducible without promising exclusive ownership."""

import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("choose_research_task", ROOT / "scripts/choose_research_task.py")
assignment = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(assignment)
CATALOG = json.loads((ROOT / assignment.CATALOG).read_text(encoding="utf-8"))


class ResearchAssignmentTests(unittest.TestCase):
    def test_catalog_sources_and_weights(self):
        assignment.validate_catalog(CATALOG, ROOT)

    def test_documented_allocation_matches_catalog(self):
        guide = (ROOT / "docs/research/current-priorities.md").read_text(encoding="utf-8")
        rows = re.findall(r"^\| [^|\n]*\(`([a-z0-9-]+)`\) \| (\d+)% \|", guide, re.MULTILINE)
        self.assertEqual(len(rows), len(CATALOG["tracks"]))
        self.assertEqual(
            {ident: int(weight) for ident, weight in rows},
            {track["id"]: track["weight"] for track in CATALOG["tracks"]},
        )

    def test_reproducible_and_track_override(self):
        seed = "a1" * 16
        first = assignment.select(CATALOG, seed)
        self.assertEqual(first, assignment.select(CATALOG, seed.upper()))
        for track in CATALOG["tracks"]:
            result = assignment.select(CATALOG, seed, track["id"])
            self.assertEqual(result["track"], track["id"])
            self.assertEqual(len(result["suggestions"]), min(3, len(track["tasks"])))
            tasks = {t["id"]: t for t in track["tasks"]}
            for suggestion in result["suggestions"]:
                task = tasks[suggestion["task_id"]]
                self.assertIn(suggestion["method"], task["methods"])

    def test_nonce_does_not_make_same_scope_unique(self):
        seen = {}
        collision = False
        for nonce in range(40):
            result = assignment.select(CATALOG, f"{nonce:032x}", "complex-mechanisms")
            for card in result["suggestions"]:
                semantic = (card["task_id"], card["method"])
                if semantic in seen:
                    self.assertEqual(seen[semantic], card["scope_key"])
                    collision = True
                seen[semantic] = card["scope_key"]
        self.assertTrue(collision)

    def test_bad_seed_or_track_fails(self):
        for seed in ("", "1", "z" * 32, "0" * 33):
            with self.assertRaises(ValueError):
                assignment.select(CATALOG, seed)
        with self.assertRaises(ValueError):
            assignment.select(CATALOG, "0" * 32, "nonexistent")
        with self.assertRaises(ValueError):
            assignment.select(CATALOG, "0" * 32, "complex-mechanisms", "connector-alphabet-change")

    def test_specific_card_exposes_first_step_and_scope_changes(self):
        result = assignment.select(CATALOG, "0" * 32, task_id="connector-alphabet-change")
        self.assertEqual(len(result["suggestions"]), 1)
        card = result["suggestions"][0]
        self.assertIn("source count", card["scope_change_triggers"][0])
        self.assertIn("PASS_UNIVERSAL_CONNECTOR_BOUNDARY", card["first_step"]["expected"])
        self.assertTrue(card["first_experiment"])

    def test_broken_catalog_rejected(self):
        for mutation in ("weight", "duplicate", "missing-source", "empty-methods", "revision", "missing-log"):
            catalog = copy.deepcopy(CATALOG)
            track = catalog["tracks"][0]
            if mutation == "weight":
                track["weight"] += 1
            elif mutation == "duplicate":
                track["tasks"].append(copy.deepcopy(track["tasks"][0]))
            elif mutation == "missing-source":
                track["tasks"][0]["starting_points"] = ["does-not-exist"]
            elif mutation == "empty-methods":
                track["tasks"][0]["methods"] = []
            elif mutation == "revision":
                catalog["priority_revision"] = 0
            else:
                catalog["priority_log"] = "does-not-exist"
            with self.assertRaises(ValueError):
                assignment.validate_catalog(catalog, ROOT)

    def test_cli_dynamic_selected_record_and_receipt(self):
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts/choose_research_task.py"), "--seed", "0" * 32],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        receipt = json.loads(result.stdout)
        selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["selected"]["reproduce"], selected["reproduce"])
        self.assertEqual(receipt["selected"]["review"], selected["review"])
        self.assertEqual(receipt["status"], "SUGGESTIONS_ONLY_NOT_RESERVED")
        self.assertEqual(receipt["priority_revision"], CATALOG["priority_revision"])
        self.assertEqual(receipt["priority_log"], CATALOG["priority_log"])
        self.assertEqual(len(receipt["catalog_sha256"]), 64)


class SparseResearchAssignmentTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.catalog = copy.deepcopy(CATALOG)
        self.catalog["tracks"] = [self.catalog["tracks"][0]]
        self.catalog["tracks"][0]["weight"] = 100
        self.catalog["tracks"][0]["tasks"] = [self.catalog["tracks"][0]["tasks"][0]]
        self.catalog["priority_log"] = "priority.log"
        card = self.catalog["tracks"][0]["tasks"][0]
        card["first_step"]["command"] = ["python3", "-B", "programs/first.py"]
        card["starting_points"] = ["notes/entry.md"]
        for name, body in {
            "priority.log": "fixture log\n",
            "programs/first.py": "print('fixture')\n",
            "notes/entry.md": "fixture note\n",
            str(assignment.CATALOG): json.dumps(self.catalog),
            "certificates/selected-result.json": json.dumps({
                "kappa": "1/1000", "review": "review.md",
                "source_manifest": "source.json", "reproduce": "fixture-only",
            }),
            "scripts/choose_research_task.py": (ROOT / "scripts/choose_research_task.py").read_text(),
        }.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "core.hooksPath=/dev/null", "commit", "-qm", "fixture")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True).stdout

    def sparse(self):
        self.git("sparse-checkout", "init", "--no-cone")
        self.git("sparse-checkout", "set", "/scripts/", "/docs/", "/certificates/")

    def receipt(self):
        result = subprocess.run(
            [sys.executable, "-B", "scripts/choose_research_task.py", "--seed", "a1" * 16],
            cwd=self.root, capture_output=True, text=True, check=True,
        )
        return json.loads(result.stdout)

    def test_sparse_cli_preserves_assignment_and_reports_omitted_inputs(self):
        full = self.receipt()
        self.sparse()
        self.assertFalse((self.root / "programs/first.py").exists())
        sparse = self.receipt()
        self.assertEqual(sparse.pop("sparse_checkout")["omitted_catalogue_paths"],
                         ["notes/entry.md", "priority.log", "programs/first.py"])
        self.assertEqual(sparse, full)
        self.assertFalse((self.root / "programs/first.py").exists())

    def test_cone_sparse_index_also_validates_omitted_files(self):
        self.git("sparse-checkout", "init", "--cone", "--sparse-index")
        self.git("sparse-checkout", "set", "scripts", "docs", "certificates")
        self.assertEqual(assignment.validate_catalog(self.catalog, self.root),
                         ["notes/entry.md", "programs/first.py"])

    def test_ordinary_deletion_and_unknown_path_still_fail(self):
        (self.root / "notes/entry.md").unlink()
        with self.assertRaisesRegex(ValueError, "entry.md"):
            assignment.validate_catalog(self.catalog, self.root)
        self.sparse()
        self.catalog["tracks"][0]["tasks"][0]["starting_points"] = ["unknown.md"]
        with self.assertRaisesRegex(ValueError, "unknown.md"):
            assignment.validate_catalog(self.catalog, self.root)

    def test_staged_sparse_change_must_match_head(self):
        self.sparse()
        path = self.root / "notes/entry.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("staged replacement\n")
        self.git("add", "--sparse", "notes/entry.md")
        self.git("update-index", "--skip-worktree", "notes/entry.md")
        path.unlink()
        with self.assertRaisesRegex(ValueError, "entry.md"):
            assignment.validate_catalog(self.catalog, self.root)

    def test_staged_only_sparse_file_has_no_head_source(self):
        self.sparse()
        path = self.root / "new.md"
        path.write_text("new staged file\n")
        self.git("add", "--sparse", "new.md")
        self.git("update-index", "--skip-worktree", "new.md")
        path.unlink()
        self.catalog["tracks"][0]["tasks"][0]["starting_points"] = ["new.md"]
        with self.assertRaisesRegex(ValueError, "new.md"):
            assignment.validate_catalog(self.catalog, self.root)

    def test_missing_sparse_symlink_is_not_a_regular_source(self):
        path = self.root / "notes/entry.md"
        path.unlink()
        try:
            path.symlink_to("../priority.log")
        except OSError:
            self.skipTest("symlinks unavailable")
        self.git("add", "notes/entry.md")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "core.hooksPath=/dev/null", "commit", "-qm", "symlink fixture")
        self.sparse()
        with self.assertRaisesRegex(ValueError, "entry.md"):
            assignment.validate_catalog(self.catalog, self.root)

    def test_directory_and_external_alias_cannot_replace_omitted_file(self):
        self.sparse()
        path = self.root / "notes/entry.md"
        path.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "entry.md"):
            assignment.validate_catalog(self.catalog, self.root)
        path.rmdir()
        try:
            path.symlink_to(self.root.parent / "outside-missing-chooser-input")
        except OSError:
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(ValueError, "entry.md"):
            assignment.validate_catalog(self.catalog, self.root)

    def test_git_failure_does_not_accept_missing_files(self):
        self.sparse()
        with mock.patch.object(assignment.subprocess, "run",
                               side_effect=subprocess.CalledProcessError(1, "git")):
            with self.assertRaises(ValueError):
                assignment.validate_catalog(self.catalog, self.root)


if __name__ == "__main__":
    unittest.main()
