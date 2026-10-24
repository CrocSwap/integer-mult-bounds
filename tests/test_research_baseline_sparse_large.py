"""Large sparse inventories must fit Windows argv without weakening validation.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
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


class LargeSparseBaselineTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        # Spaces exercise Windows quoting; brackets exercise literal pathspecs;
        # the supplementary character occupies two UTF-16 code units.
        self.names = [f"research/omitted/{i:04d} [payload] " + "long-name-" * 7 + "\U0001f9ea.txt"
                      for i in range(600)]
        self.record = {
            "certificate": "certificates/claim.json",
            "source_manifest": "certificates/source.json",
            "proof": "docs/proof.md", "review": "docs/proof.md",
            "validation": "docs/proof.md", "proof_supplements": {},
        }
        files = {
            "certificates/selected-result.json": json.dumps(self.record),
            "certificates/claim.json": json.dumps({"schema": sparse.PRODUCTIVE_SCHEMA}),
            "certificates/source.json": json.dumps({
                "format": "repository-files-sha256-v1",
                "files": {name: "0" for name in self.names},
            }),
            "docs/proof.md": "fixture\n",
            **{name: "input\n" for name in self.names},
        }
        for name, content in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self.git("init", "-q")
        self.git("-c", "core.autocrlf=false", "add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "maintenance.auto=false", "-c", "gc.auto=0",
                 "-c", "core.hooksPath=/dev/null", "commit", "-qm", "fixture")
        self.git("sparse-checkout", "set", "--cone", "certificates", "docs")

    def git(self, *args, **kwargs):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, **kwargs).stdout

    def test_complete_inventory_with_windows_launch_limit(self):
        original_run = subprocess.run
        inventories = []

        def windows_limit(argv, **kwargs):
            if argv[:2] == ["git", "--literal-pathspecs"]:
                units = len(subprocess.list2cmdline(argv).encode("utf-16-le")) // 2
                if units >= 32767:
                    raise OSError(206, "simulated Windows command line limit")
                inventories.append((argv[2], argv[argv.index("--") + 1:]))
            return original_run(argv, **kwargs)

        unbatched = ["git", "--literal-pathspecs", "ls-files", "-t", "--stage", "-z",
                     "--", *self.names]
        self.assertGreater(len(subprocess.list2cmdline(unbatched)), 32767)
        with mock.patch.object(subprocess, "run", side_effect=windows_limit):
            omitted = sparse.sparse_omissions(self.record, self.root)
        self.assertEqual(omitted, self.names)
        for command in ("ls-files", "ls-tree"):
            batches = [paths for kind, paths in inventories if kind == command]
            self.assertGreater(len(batches), 1)
            self.assertEqual([name for paths in batches for name in paths], self.names)

    def test_real_cli_materializes_every_input(self):
        command = [sys.executable, "-B", str(ROOT / "scripts/research_baseline_sparse.py"),
                   "--root", str(self.root)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["omitted_files"], len(self.names))
        self.assertEqual(report["first_omitted"], self.names[:5])
        self.assertEqual(report["next"], ["python3", "-B", "scripts/research_selected_baseline.py"])
        self.git(*report["materialize"][1:])
        self.assertTrue(all((self.root / name).is_file() for name in self.names))
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "NO_SPARSE_SELECTED_OMISSIONS")

    def test_late_ordinary_deletion_rejected(self):
        name = self.names[-1]
        self.git("update-index", "--no-skip-worktree", "--", name)
        with self.assertRaises(ValueError) as failure:
            sparse.sparse_omissions(self.record, self.root)
        self.assertEqual(str(failure.exception), "Invalid selected file: " + name)

    def test_late_staged_blob_drift_rejected(self):
        name = self.names[-1]
        blob = self.git("hash-object", "-w", "--stdin", input=b"changed\n").decode().strip()
        self.git("update-index", "--cacheinfo", "100644," + blob + "," + name)
        self.git("update-index", "--skip-worktree", "--", name)
        with self.assertRaises(ValueError) as failure:
            sparse.sparse_omissions(self.record, self.root)
        self.assertEqual(str(failure.exception), "Invalid selected file: " + name)

    def test_late_git_failure_does_not_publish_partial_report(self):
        original_run = subprocess.run
        calls = 0

        def fail_second_inventory(argv, **kwargs):
            nonlocal calls
            if argv[:3] == ["git", "--literal-pathspecs", "ls-files"]:
                calls += 1
                if calls == 2:
                    raise subprocess.CalledProcessError(1, argv, stderr="injected failure")
            return original_run(argv, **kwargs)

        with mock.patch.object(subprocess, "run", side_effect=fail_second_inventory):
            with self.assertRaises(ValueError):
                sparse.report(self.record, self.root)
        self.assertEqual(calls, 2, "the control must reach a later inventory batch")


if __name__ == "__main__":
    unittest.main()
