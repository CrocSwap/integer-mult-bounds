"""Synthetic Git controls for explicit historical-only receipt adaptation.

No network, original evidence rewriting, or mathematical suite is required.
"""
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import replay_historical_receipt as historical
import research_package as replay

PACKAGE = "research/pr1-retention-receipt"
INPUT = "docs/input.txt"
CATALOG = "docs/research/agent-task-catalog.json"


class HistoricalReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="test-historical-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "--quiet", "--template=")
        self.git("config", "user.name", "Historical fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.put(INPUT, b"original input\n")
        card = {"id": "receipt", "question": "historical source check"}
        self.put(CATALOG, json.dumps({"tracks": [{"tasks": [card]}]}))
        self.put(historical.ADAPTER, b"# fixture adapter input\n")
        self.put(historical.REGRESSION, b"# fixture regression input\n")
        self.base = self.commit()
        self.sources = {"schema_version": 1, "base_commit": self.base, "files": [
            self.source_row(INPUT, "input"), self.source_row(CATALOG, "provenance")]}
        self.manifest = {"schema_version": 1, "status": "ready", "python": "3.12",
                         "requirements": [], "inputs": [INPUT], "commands": [{
                             "argv": ["{python}", "-B", "{package}/verify.py"],
                             "timeout_seconds": 10, "checks": "Original input and assertion control"}]}
        task = {"schema_version": 1, "base_commit": self.base, "task_id": "receipt",
                "original_card": card, "scope_status": "refined", "scope_change_reason": "fixture",
                "actual_scope": "historical receipt fixture", "outcome": "completed",
                "bottleneck_link": "fixture", "stop_rule": "one check", "evidence": "verifier",
                "author": "fixture", "ai_assistance": "fixture", "open_questions": [],
                "no_open_questions_reason": "bounded fixture"}
        self.put(PACKAGE + "/TASK.json", json.dumps(task))
        self.original_readme = "## Open next questions\nBounded fixture\n"
        self.put(PACKAGE + "/README.md", self.original_readme)
        self.put(PACKAGE + "/verify.py", "from pathlib import Path\n"
                 "assert __debug__, 'assertions were disabled'\n"
                 "assert Path('docs/input.txt').read_bytes() == b'original input\\n'\n"
                 "print('PASS_ORIGINAL_CONTROL')\n")
        self.freeze()
        self.put(INPUT, b"current input with later credit\n")
        self.commit()
        self.patch = mock.patch.dict(historical.POLICY, {PACKAGE: self.policy}, clear=True)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    def put(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value.encode() if isinstance(value, str) else value)

    def commit(self):
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "fixture")
        return self.git("rev-parse", "HEAD").decode().strip()

    def source_row(self, name, usage):
        return {"path": name, "usage": usage,
                "git_blob": self.git("rev-parse", self.base + ":" + name).decode().strip(),
                "sha256": hashlib.sha256((self.root / name).read_bytes()).hexdigest()}

    def freeze(self):
        self.put(PACKAGE + "/README.md", self.original_readme)
        self.put(PACKAGE + "/SOURCES.json", json.dumps(self.sources))
        self.put(PACKAGE + "/VERIFY.json", json.dumps(self.manifest))
        commit = self.commit()
        self.policy = {"package_commit": commit,
                       "package_tree": self.git("rev-parse", commit + ":" + PACKAGE).decode().strip(),
                       "base_commit": self.base, "inputs": (INPUT,), "git_inputs": (),
                       "manifest_sha256": {name: hashlib.sha256((self.root / PACKAGE / name).read_bytes()).hexdigest()
                                           for name in ("SOURCES.json", "VERIFY.json")}}
        original = {PACKAGE + "/" + name: ("100644", (self.root / PACKAGE / name).read_bytes())
                    for name in ("SOURCES.json", "VERIFY.json", "README.md")}
        for name, (_, raw) in historical.wrapper_files(original, PACKAGE).items():
            self.put(name, raw)
        if hasattr(self, "patch"):
            historical.POLICY[PACKAGE] = self.policy

    def run_receipt(self, check_only=False):
        with contextlib.redirect_stdout(io.StringIO()) as text:
            historical.run(self.root, PACKAGE, check_only=check_only)
        return text.getvalue()

    def test_positive_historical_replay_keeps_live_bytes_and_git_unchanged(self):
        before = historical.package_snapshot(self.root, PACKAGE)
        live = (self.root / INPUT).read_bytes()
        git_before = {p.relative_to(self.root).as_posix(): p.read_bytes()
                      for p in (self.root / ".git").rglob("*") if p.is_file()}
        result = self.run_receipt()
        self.assertIn("PASS_HISTORICAL_RECEIPT_ONLY", result)
        self.assertIn("live_inputs_validated=false", result)
        self.assertEqual((self.root / INPUT).read_bytes(), live)
        self.assertEqual(historical.package_snapshot(self.root, PACKAGE), before)
        git_after = {p.relative_to(self.root).as_posix(): p.read_bytes()
                     for p in (self.root / ".git").rglob("*") if p.is_file()}
        self.assertEqual(git_before, git_after)

    def test_default_live_validation_still_fails(self):
        for _ in range(2):
            wrapped = {name: (self.root / PACKAGE / name).read_bytes()
                       for name in ("SOURCES.json", "VERIFY.json")}
            try:
                for name in wrapped:
                    self.put(PACKAGE + "/" + name, self.git("show", self.policy["package_commit"] + ":" + PACKAGE + "/" + name))
                with self.assertRaisesRegex(ValueError, "working source drift"):
                    replay.validate(self.root, PACKAGE)
            finally:
                for name, raw in wrapped.items():
                    self.put(PACKAGE + "/" + name, raw)
            self.run_receipt(check_only=True)

    def test_arbitrary_wrapper_metadata_drift_rejected(self):
        for name in ("SOURCES.json", "VERIFY.json", "README.md"):
            with self.subTest(name=name):
                path = self.root / PACKAGE / name
                original = path.read_bytes()
                try:
                    path.write_bytes(original + b" ")
                    with self.assertRaisesRegex(ValueError, "live package drift"):
                        self.run_receipt()
                finally:
                    path.write_bytes(original)

    def test_original_manifest_digest_mismatch_rejected(self):
        historical.POLICY[PACKAGE]["manifest_sha256"]["VERIFY.json"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "original manifest digest mismatch"):
            self.run_receipt()

    def test_metadata_only_is_not_labelled_receipt_success(self):
        result = self.run_receipt(check_only=True)
        self.assertIn("PASS_HISTORICAL_METADATA_ONLY", result)
        self.assertNotIn("PASS_HISTORICAL_RECEIPT_ONLY", result)

    def test_unknown_package_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "not approved"):
            historical.run(self.root, "research/other")

    def test_wrong_frozen_commit_rejected(self):
        historical.POLICY[PACKAGE]["package_commit"] = "0" * 40
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_receipt()

    def test_wrong_frozen_package_tree_rejected(self):
        historical.POLICY[PACKAGE]["package_tree"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "package tree mismatch"):
            self.run_receipt()

    def test_wrong_history_base_rejected(self):
        historical.POLICY[PACKAGE]["base_commit"] = historical.POLICY[PACKAGE]["package_commit"]
        with self.assertRaisesRegex(ValueError, "base differs"):
            self.run_receipt()

    def test_wrong_blob_pin_rejected(self):
        self.sources["files"][0]["git_blob"] = "0" * 40
        self.freeze()
        with self.assertRaisesRegex(ValueError, "Git blob mismatch"):
            self.run_receipt()

    def test_wrong_sha256_pin_rejected(self):
        self.sources["files"][0]["sha256"] = "0" * 64
        self.freeze()
        with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
            self.run_receipt()

    def test_foreign_head_pin_rejected(self):
        self.sources["files"][0]["pin"] = "head:" + self.base + ":" + INPUT
        self.freeze()
        # The supported general resolver yields the same base expression. A
        # genuinely different commit is what must not replace the approved base.
        self.sources["files"][0]["pin"] = "head:" + "f" * 40 + ":" + INPUT
        self.freeze()
        with self.assertRaisesRegex(ValueError, "base-commit source pins"):
            self.run_receipt()

    def test_undeclared_input_rejected(self):
        self.manifest["inputs"] = []
        self.freeze()
        with self.assertRaisesRegex(ValueError, "input list differs"):
            self.run_receipt()

    def test_missing_historical_input_rejected(self):
        self.sources["files"][0]["path"] = "docs/missing.txt"
        self.freeze()
        with self.assertRaisesRegex(ValueError, "missing exact historical input"):
            self.run_receipt()

    def test_duplicate_pin_rejected(self):
        self.sources["files"].append(copy.deepcopy(self.sources["files"][0]))
        self.freeze()
        with self.assertRaisesRegex(ValueError, "duplicate or overlapping"):
            self.run_receipt()

    def test_malicious_paths_rejected(self):
        for name in ("../escape", "/escape", "docs/../input.txt", "docs//input.txt",
                     "./docs/input.txt", "docs\\input.txt", ".git/config", "docs/.GiT/config",
                     "docs/input\n.txt", "docs/input\x00.txt", ":(glob)*"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    historical.safe_path(name)

    def test_traversal_in_authenticated_sources_rejected(self):
        self.sources["files"][0]["path"] = "../escape"
        self.freeze()
        with self.assertRaisesRegex(ValueError, "canonical"):
            self.run_receipt()

    def test_live_package_drift_rejected(self):
        self.put(PACKAGE + "/verify.py", "print('fake success')\n")
        with self.assertRaisesRegex(ValueError, "live package drift"):
            self.run_receipt()

    def test_extra_live_package_file_rejected(self):
        self.put(PACKAGE + "/extra.py", "print('untracked')\n")
        with self.assertRaisesRegex(ValueError, "inventory differs"):
            self.run_receipt()

    def test_live_package_symlink_rejected(self):
        (self.root / PACKAGE / "link").symlink_to(self.root / INPUT)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.run_receipt()

    def test_frozen_package_symlink_rejected(self):
        (self.root / PACKAGE / "link").symlink_to(self.root / INPUT)
        self.freeze()
        with self.assertRaisesRegex(ValueError, "non-regular frozen package"):
            self.run_receipt()

    def test_live_input_symlink_rejected(self):
        (self.root / INPUT).unlink()
        (self.root / INPUT).symlink_to(self.root / CATALOG)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.run_receipt()

    def test_missing_live_input_rejected(self):
        (self.root / INPUT).unlink()
        with self.assertRaisesRegex(ValueError, "missing or external"):
            self.run_receipt()

    def test_materialized_source_mutation_fails_final_gate(self):
        def corrupt(root, package):
            (root / INPUT).write_text("bad mutation")
        with mock.patch.object(replay, "run_package", side_effect=corrupt):
            with self.assertRaisesRegex(ValueError, "changed its materialized"):
                self.run_receipt()

    def test_materialized_extra_package_file_fails_final_gate(self):
        def corrupt(root, package):
            (root / package / "extra").write_text("bad mutation")
        with mock.patch.object(replay, "run_package", side_effect=corrupt):
            with self.assertRaisesRegex(ValueError, "changed its materialized"):
                self.run_receipt()

    def test_live_mutation_during_replay_fails_final_gate(self):
        def corrupt(root, package):
            (self.root / INPUT).write_text("bad live mutation")
        with mock.patch.object(replay, "run_package", side_effect=corrupt):
            with self.assertRaisesRegex(ValueError, "live package or inputs changed"):
                self.run_receipt()

    def test_failure_propagates_and_temporary_directory_is_removed(self):
        paths = []
        def fail(root, package):
            paths.append(root)
            raise ValueError("original verifier rejected")
        with mock.patch.object(replay, "run_package", side_effect=fail):
            with self.assertRaisesRegex(ValueError, "original verifier rejected"):
                self.run_receipt()
        self.assertTrue(paths)
        self.assertTrue(all(not path.exists() for path in paths))

    def test_original_assertions_run_despite_inherited_optimization(self):
        with mock.patch.dict(os.environ, {"PYTHONOPTIMIZE": "2"}):
            self.run_receipt()
            self.assertEqual(os.environ["PYTHONOPTIMIZE"], "2")

    def test_replacement_cannot_substitute_wrong_history(self):
        self.put(INPUT, b"replacement bytes\n")
        replacement = self.commit()
        self.git("replace", self.base, replacement)
        self.run_receipt()

    def test_inherited_git_directory_cannot_redirect_authentication(self):
        with mock.patch.dict(os.environ, {"GIT_DIR": str(self.root / "absent"),
                                         "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.bare",
                                         "GIT_CONFIG_VALUE_0": "true"}):
            self.run_receipt()

    def test_historical_symlink_input_rejected(self):
        (self.root / "docs/link.txt").symlink_to("input.txt")
        commit = self.commit()
        with self.assertRaisesRegex(ValueError, "non-regular historical input"):
            historical.pinned_file(self.root, commit, "docs/link.txt")

    def test_original_timeout_is_enforced(self):
        self.manifest["commands"][0]["timeout_seconds"] = 1
        self.put(PACKAGE + "/verify.py", "import time; time.sleep(10)\n")
        self.freeze()
        with self.assertRaisesRegex(ValueError, "verification timed out"):
            self.run_receipt()

    def test_original_nonzero_exit_is_not_success(self):
        self.put(PACKAGE + "/verify.py", "raise SystemExit(7)\n")
        self.freeze()
        with self.assertRaisesRegex(ValueError, "verification command exited 7"):
            self.run_receipt()

    def test_adapter_input_mutation_fails_final_gate(self):
        def corrupt(root, package):
            (self.root / historical.ADAPTER).write_text("bad mutation")
        with mock.patch.object(replay, "run_package", side_effect=corrupt):
            with self.assertRaisesRegex(ValueError, "live package or inputs changed"):
                self.run_receipt()

    def test_legacy_grafts_rejected(self):
        self.put(".git/info/grafts", self.base + "\n")
        with self.assertRaisesRegex(ValueError, "legacy Git grafts"):
            self.run_receipt()

    def test_isolated_git_has_no_alternates_or_live_config(self):
        def inspect(root, package):
            self.assertFalse((root / ".git/objects/info/alternates").exists())
            self.assertNotIn(str(self.root), (root / ".git/config").read_text())
            self.assertEqual(historical.output(root, "show", self.base + ":" + INPUT), b"original input\n")
            self.assertIn(INPUT.encode(), historical.output(root, "ls-tree", "-r", self.base))
        with mock.patch.object(replay, "run_package", side_effect=inspect):
            self.run_receipt()


if __name__ == "__main__":
    unittest.main()
