"""The sparse preflight names omitted selected inputs instead of failing opaquely."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import research_baseline_sparse as sparse
sys.path.pop(0)

RECORD = {
    "certificate": "research/audit/ASSEMBLY.json", "source_manifest": "research/audit/SOURCE.json",
    "proof": "research/pkg-a/PROOF.md", "review": "docs/review.md",
    "validation": "docs/validation.md",
    "proof_supplements": {"research/pkg-b/NOTE.md": "0", "scripts/helper.py": "0"},
}


class SparseBaselineTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        files = {
            "certificates/selected-result.json": json.dumps(RECORD),
            "docs/review.md": "review\n", "docs/validation.md": "validation\n",
            "scripts/helper.py": "pass\n", "research/pkg-a/PROOF.md": "proof\n",
            "research/pkg-a/data/x.json": "[]\n", "research/pkg-b/NOTE.md": "note\n",
            "research/audit/ASSEMBLY.json": "{}\n",
            "research/audit/SOURCE.json": json.dumps({
                "format": "repository-packages-sha256-v1", "package_roots": ["research/pkg-a"],
                "files": {"research/pkg-a/PROOF.md": "0", "research/pkg-a/data/x.json": "0"}}),
        }
        for name, body in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        self.record = RECORD
        self.git("init", "-q")
        self.git("add", ".")
        self.commit("fixture")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True,
                              text=True, encoding="utf-8").stdout

    def commit(self, message, *extra):
        # Detached maintenance can recreate .git/objects during temp cleanup.
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "maintenance.auto=false", "-c", "gc.auto=0",
                 "-c", "core.hooksPath=/dev/null", "commit", "-q", *extra, "-m", message)

    def run_main(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = sparse.main(["--root", str(self.root)])
        return code, json.loads(out.getvalue())

    def productive_certificate(self):
        (self.root / self.record["certificate"]).write_text(json.dumps({
            "schema": "proposed-conditional-integer-multiplication-claim/1",
        }), encoding="utf-8")

    def explicit_manifest(self):
        self.record = {**RECORD, "source_manifest": "certificates/source.json"}
        (self.root / sparse.SELECTED).write_text(json.dumps(self.record), encoding="utf-8")
        (self.root / "LICENSE").write_text("fixture license\n", encoding="utf-8")
        (self.root / self.record["source_manifest"]).write_text(json.dumps({
            "format": "repository-files-sha256-v1",
            "files": {"LICENSE": "0", "research/pkg-a/data/x.json": "0"},
        }), encoding="utf-8")
        self.productive_certificate()
        self.git("add", ".")
        self.commit("explicit repository inventory")

    def test_full_checkout_reports_nothing(self):
        self.assertEqual(sparse.sparse_omissions(self.record, self.root), [])
        code, result = self.run_main()
        self.assertEqual((code, result["status"]), (0, "NO_SPARSE_SELECTED_OMISSIONS"))
        self.assertEqual(result["next"], ["python3", "-B", "scripts/research_baseline.py"])

    def test_fixture_commit_never_starts_background_maintenance(self):
        # Force automatic work even in this tiny repo. Keep the positive
        # control synchronous so its own maintenance cannot race cleanup.
        for key, value in {
            "maintenance.auto": "true", "maintenance.autoDetach": "false",
            "gc.autoDetach": "false", "maintenance.commit-graph.enabled": "true",
            "maintenance.commit-graph.auto": "-1", "gc.auto": "1",
        }.items():
            self.git("config", key, value)
        with tempfile.TemporaryDirectory() as directory:
            trace = Path(directory) / "git-trace.jsonl"

            def maintenance_children():
                return [event for line in trace.read_text(encoding="utf-8").splitlines()
                        if (event := json.loads(line)).get("event") == "child_start"
                        and any(arg in {"maintenance", "gc"}
                                for arg in event.get("argv", []))]

            with mock.patch.dict(os.environ, {"GIT_TRACE2_EVENT": str(trace)}):
                self.commit("guarded fixture", "--allow-empty")
            self.assertEqual(maintenance_children(), [])

            trace.unlink()
            with mock.patch.dict(os.environ, {"GIT_TRACE2_EVENT": str(trace)}):
                self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                         "-c", "core.hooksPath=/dev/null", "commit", "-q", "--allow-empty",
                         "-m", "unguarded positive control")
            self.assertTrue(maintenance_children(), "positive control must start maintenance")

    def test_full_explicit_inventory_keeps_repository_relative_paths(self):
        self.explicit_manifest()
        code, result = self.run_main()
        self.assertEqual((code, result["status"]), (0, "NO_SPARSE_SELECTED_OMISSIONS"))
        self.assertEqual(result["next"], ["python3", "-B", "scripts/research_selected_baseline.py"])

    def test_sparse_explicit_inventory_and_certificate_read_from_head(self):
        self.explicit_manifest()
        self.git("sparse-checkout", "set", "--no-cone", "/*", "!/*/", "/scripts/", "/docs/",
                 "/certificates/selected-result.json")
        self.assertFalse((self.root / self.record["source_manifest"]).exists())
        self.assertFalse((self.root / self.record["certificate"]).exists())
        self.assertTrue((self.root / "LICENSE").is_file())
        omitted = sparse.sparse_omissions(self.record, self.root)
        self.assertEqual(omitted, ["certificates/source.json", "research/audit/ASSEMBLY.json",
                                   "research/pkg-a/PROOF.md", "research/pkg-a/data/x.json",
                                   "research/pkg-b/NOTE.md"])
        code, result = self.run_main()
        self.assertEqual((code, result["status"], result["omitted_files"]),
                         (2, "SPARSE_SELECTED_INPUTS_ABSENT", 5))
        self.assertEqual(result["next"], ["python3", "-B", "scripts/research_selected_baseline.py"])
        self.git(*result["materialize"][1:])
        self.assertEqual(sparse.sparse_omissions(self.record, self.root), [])
        self.assertEqual(self.run_main()[0], 0)

    def test_productive_schema_routes_package_inventory_to_selected_baseline(self):
        self.productive_certificate()
        self.commit("productive certificate", "-a")
        self.git("sparse-checkout", "set", "--cone", "scripts", "docs", "certificates")
        code, result = self.run_main()
        self.assertEqual(code, 2)
        self.assertEqual(result["next"], ["python3", "-B", "scripts/research_selected_baseline.py"])

    def test_cone_sparse_names_packages_and_reads_manifest_from_head(self):
        self.git("sparse-checkout", "set", "--cone", "scripts", "docs", "certificates")
        self.assertFalse((self.root / "research/audit/SOURCE.json").exists())
        omitted = sparse.sparse_omissions(self.record, self.root)
        self.assertEqual(omitted, ["research/audit/ASSEMBLY.json", "research/audit/SOURCE.json",
                                   "research/pkg-a/PROOF.md", "research/pkg-a/data/x.json",
                                   "research/pkg-b/NOTE.md"])
        code, result = self.run_main()
        self.assertEqual((code, result["status"], result["omitted_files"]),
                         (2, "SPARSE_SELECTED_INPUTS_ABSENT", 5))
        command = result["materialize"]
        self.assertEqual(command, sparse.materialize_command(omitted))
        self.assertEqual(command[3:], ["research/audit", "research/pkg-a", "research/pkg-b"])
        self.git(*command[1:])
        self.assertEqual(sparse.sparse_omissions(self.record, self.root), [])
        self.assertEqual(self.run_main()[0], 0)

    def test_non_cone_sparse_and_legacy_package_relative_manifest(self):
        legacy = self.root / "research/audit/SOURCE.json"
        legacy.write_text(json.dumps({"files": {"ASSEMBLY.json": "0"}}), encoding="utf-8")
        self.commit("legacy", "-a")
        self.git("sparse-checkout", "set", "--no-cone", "/scripts/", "/docs/", "/certificates/",
                 "/research/pkg-a/", "/research/pkg-b/")
        self.assertEqual(sparse.sparse_omissions(self.record, self.root),
                         ["research/audit/ASSEMBLY.json", "research/audit/SOURCE.json"])

    def test_ordinary_deletion_is_not_reported_as_sparse(self):
        (self.root / "research/pkg-a/data/x.json").unlink()
        with self.assertRaisesRegex(ValueError, "Invalid selected file: research/pkg-a/data/x.json"):
            sparse.sparse_omissions(self.record, self.root)
        self.git("checkout", "--", "research/pkg-a/data/x.json")
        self.git("sparse-checkout", "set", "--cone", "scripts", "docs", "certificates", "research/audit")
        (self.root / "research/audit/SOURCE.json").unlink()
        with self.assertRaisesRegex(ValueError, "Invalid selected file: research/audit/SOURCE.json"):
            sparse.sparse_omissions(self.record, self.root)

    def test_staged_change_to_omitted_entry_is_not_sparse(self):
        self.git("sparse-checkout", "set", "--cone", "scripts", "docs", "certificates",
                 "research/audit", "research/pkg-a")
        changed = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=self.root, input="other\n",
                                 check=True, capture_output=True, text=True).stdout.strip()
        self.git("update-index", "--cacheinfo", "100644," + changed + ",research/pkg-b/NOTE.md")
        self.git("update-index", "--skip-worktree", "research/pkg-b/NOTE.md")
        with self.assertRaisesRegex(ValueError, "Invalid selected file: research/pkg-b/NOTE.md"):
            sparse.sparse_omissions(self.record, self.root)


if __name__ == "__main__":
    unittest.main()
