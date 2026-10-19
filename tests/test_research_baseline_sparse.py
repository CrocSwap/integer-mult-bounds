"""The sparse preflight names omitted selected inputs instead of failing opaquely."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

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
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "core.hooksPath=/dev/null", "commit", "-q", *extra, "-m", message)

    def run_main(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = sparse.main(["--root", str(self.root)])
        return code, json.loads(out.getvalue())

    def test_full_checkout_reports_nothing(self):
        self.assertEqual(sparse.sparse_omissions(self.record, self.root), [])
        code, result = self.run_main()
        self.assertEqual((code, result["status"]), (0, "NO_SPARSE_SELECTED_OMISSIONS"))

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
