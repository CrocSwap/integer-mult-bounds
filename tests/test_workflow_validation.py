"""Regression tests use the real pinned actionlint; never skip if it is missing."""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_workflows as guard
import install_actionlint as installer

VALID = '''name: P112 regression control
on:
  workflow_dispatch:
jobs:
  exact-slice:
    runs-on: ubuntu-24.04
    steps:
      - name: Initialise P112 work directory
        run: echo "TMPDIR=$RUNNER_TEMP/p112-common-slice" >> "$GITHUB_ENV"
      - run: echo "$TMPDIR"
'''
INVALID_CONTEXT = VALID.replace(
    '    steps:\n',
    '    env:\n      TMPDIR: ${{ runner.temp }}/p112-common-slice\n    steps:\n',
).replace('      - name: Initialise P112 work directory\n'
          '        run: echo "TMPDIR=$RUNNER_TEMP/p112-common-slice" >> "$GITHUB_ENV"\n', '')
ZERO = "0" * 40


class GuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binary = guard.actionlint_binary("actionlint")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_CONFIG_NOSYSTEM": "1"}
        self.git("init", "-q")
        self.workflow = self.repo / ".github/workflows/check.yml"
        self.workflow.parent.mkdir(parents=True)
        self.workflow.write_text(VALID)
        self.valid = self.commit()

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-C", str(self.repo), "-c", "user.name=Workflow test",
             "-c", "user.email=workflow-test@example.invalid",
             "-c", "commit.gpgsign=false", *args], env=self.env,
            stderr=subprocess.STDOUT).decode().strip()

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "test workflow snapshot")
        return self.git("rev-parse", "HEAD")

    def run_guard(self, *args, stdin=None):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts/check_workflows.py"),
             "--repo", str(self.repo), "--actionlint", self.binary, *args],
            input=stdin, text=True, capture_output=True, env=self.env)

    def test_valid_runner_environment_initialization(self):
        result = self.run_guard("--ref", self.valid)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(self.valid, result.stdout)

    def test_original_job_env_runner_context_is_rejected(self):
        self.workflow.write_text(INVALID_CONTEXT)
        result = self.run_guard()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('context "runner" is not allowed here', result.stdout)
        self.assertIn('[expression]', result.stdout)

    def test_invalid_yaml_is_rejected(self):
        self.workflow.write_text("name: [broken\n")
        self.assertNotEqual(self.run_guard().returncode, 0)

    def test_other_expression_errors_are_not_suppressed(self):
        self.workflow.write_text(VALID.replace('echo "$TMPDIR"',
                                               'echo "${{ missing.foo }}"'))
        result = self.run_guard()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('[expression]', result.stdout)

    def test_uncommitted_fix_cannot_hide_bad_committed_head(self):
        self.workflow.write_text(INVALID_CONTEXT)
        bad = self.commit()
        self.workflow.write_text(VALID)
        self.assertEqual(self.run_guard().returncode, 0)
        self.assertNotEqual(self.run_guard("--ref", bad).returncode, 0)

    def test_pre_push_checks_non_checked_out_branch_without_mutation(self):
        self.workflow.write_text(INVALID_CONTEXT)
        bad = self.commit()
        self.git("branch", "bad", bad)
        self.git("checkout", "-q", "--detach", self.valid)
        before = self.git("status", "--porcelain")
        result = self.run_guard("--pre-push", stdin=f"refs/heads/bad {bad} refs/heads/bad {ZERO}\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(bad, result.stdout)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.valid)
        self.assertEqual(self.git("status", "--porcelain"), before)
        self.assertEqual(self.workflow.read_text(), VALID)

    def test_pre_push_checks_all_refs_even_after_failure(self):
        self.workflow.write_text(INVALID_CONTEXT)
        bad = self.commit()
        stdin = (f"refs/heads/bad {bad} refs/heads/bad {ZERO}\n"
                 f"refs/heads/good {self.valid} refs/heads/good {ZERO}\n")
        result = self.run_guard("--pre-push", stdin=stdin)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(bad, result.stdout)
        self.assertIn(self.valid, result.stdout)

    def test_pre_push_uses_good_ref_even_if_checkout_is_bad(self):
        self.workflow.write_text(INVALID_CONTEXT)
        self.commit()
        result = self.run_guard("--pre-push", stdin=
                               f"refs/heads/good {self.valid} refs/heads/good {ZERO}\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_deletion_only_needs_no_linter(self):
        result = self.run_guard("--pre-push", "--actionlint", "absent-actionlint",
                               stdin=f"(delete) {ZERO} refs/heads/old {self.valid}\n")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_malformed_pre_push_input_fails_closed(self):
        for stdin in ("bad\n", f"refs/heads/a nope refs/heads/a {ZERO}\n"):
            self.assertNotEqual(self.run_guard("--pre-push", stdin=stdin).returncode, 0)

    def test_annotated_tag_validates_its_commit(self):
        self.git("tag", "-a", "safe", "-m", "test tag", self.valid)
        tag = self.git("rev-parse", "safe")
        result = self.run_guard("--pre-push", stdin=
                               f"refs/tags/safe {tag} refs/tags/safe {ZERO}\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(self.valid, result.stdout)

    def test_missing_workflows_is_not_an_empty_success(self):
        self.workflow.unlink()
        empty = self.commit()
        result = self.run_guard("--ref", empty)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing an empty pass", result.stderr)

    def test_yaml_extension_and_disabled_jobs_are_still_linted(self):
        self.workflow.with_suffix(".yaml").write_text(INVALID_CONTEXT.replace(
            "    runs-on:", "    if: false\n    runs-on:"))
        self.assertNotEqual(self.run_guard().returncode, 0)

    def test_symlinked_workflow_is_rejected(self):
        self.workflow.unlink()
        self.workflow.symlink_to(self.repo / "outside.yml")
        (self.repo / "outside.yml").write_text(VALID)
        result = self.run_guard()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stderr)
        oid = self.commit()
        self.assertNotEqual(self.run_guard("--ref", oid).returncode, 0)

    def test_local_action_directory_symlink_fails_closed(self):
        action = self.repo / "local-action"
        action.mkdir()
        (action / "action.yml").write_text("""name: Alias control
description: A valid action must still not be imported through a symlink
runs:
  using: composite
  steps:
    - run: echo okay
      shell: bash
""")
        (self.repo / "alias").symlink_to("local-action", target_is_directory=True)
        self.workflow.write_text(VALID + "      - uses: ./alias\n")
        result = self.run_guard()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stderr)
        bad = self.commit()
        self.assertNotEqual(self.run_guard("--ref", bad).returncode, 0)

    def test_linked_worktree_git_file_is_not_a_resource(self):
        action = self.repo / "local-action"
        action.mkdir()
        (action / "action.yml").write_text("""name: Local control
description: Linked worktree fixture
runs:
  using: composite
  steps:
    - run: echo okay
      shell: bash
""")
        self.workflow.write_text(VALID + "      - uses: ./local-action\n")
        good = self.commit()
        linked = self.repo / "linked"
        self.git("worktree", "add", "--detach", str(linked), good)
        result = self.run_guard("--repo", str(linked))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_repository_ignore_configuration_cannot_suppress_errors(self):
        self.workflow.write_text(INVALID_CONTEXT)
        (self.repo / ".github/actionlint.yaml").write_text("paths:\n  '**/*.yml':\n    ignore:\n      - '.*'\n")
        self.assertNotEqual(self.run_guard().returncode, 0)

    def test_local_reusable_workflow_inputs_are_checked(self):
        callee = self.workflow.parent / "reusable.yml"
        callee.write_text("""name: Reusable control
on:
  workflow_call:
    inputs:
      required_input:
        required: true
        type: string
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - run: echo okay
""")
        self.workflow.write_text("""name: Caller control
on: push
jobs:
  call:
    uses: ./.github/workflows/reusable.yml
    with:
      wrong_input: value
""")
        result = self.run_guard()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[workflow-call]", result.stdout)
        self.assertIn("required_input", result.stdout)
        self.assertIn("wrong_input", result.stdout)
        oid = self.commit()
        self.assertNotEqual(self.run_guard("--ref", oid).returncode, 0)
        self.workflow.write_text(self.workflow.read_text().replace(
            "wrong_input: value", "required_input: value"))
        self.assertEqual(self.run_guard().returncode, 0)

    def test_local_action_inputs_and_resources_use_exact_tree(self):
        action = self.repo / "my-action"
        action.mkdir()
        (action / "action.yaml").write_text("""name: Local action control
description: Metadata validation fixture
inputs:
  known:
    description: Declared input
runs:
  using: node24
  main: ../shared/index.js
""")
        shared = self.repo / "shared"
        shared.mkdir()
        (shared / "index.js").write_text("throw new Error('must never execute');")
        self.workflow.write_text(VALID + """      - uses: ./my-action
        with:
          wrong: value
""")
        result = self.run_guard()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[action]", result.stdout)
        self.assertIn("wrong", result.stdout)
        bad = self.commit()
        self.workflow.write_text(self.workflow.read_text().replace("wrong:", "known:"))
        result = self.run_guard()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotEqual(self.run_guard("--ref", bad).returncode, 0)
        good = self.commit()
        self.assertEqual(self.run_guard("--ref", good).returncode, 0)
        (shared / "index.js").unlink()
        result = self.run_guard()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("index.js", result.stdout)
        # An uncommitted missing resource cannot corrupt an exact good commit.
        self.assertEqual(self.run_guard("--ref", good).returncode, 0)

    def test_git_replacement_refs_cannot_hide_bad_object(self):
        self.workflow.write_text(INVALID_CONTEXT)
        bad = self.commit()
        self.git("replace", bad, self.valid)
        result = self.run_guard("--ref", bad)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(bad, result.stdout)
        self.assertIn('context "runner"', result.stdout)
        result = self.run_guard("--pre-push", stdin=
                               f"refs/heads/bad {bad} refs/heads/bad {ZERO}\n")
        self.assertNotEqual(result.returncode, 0)

    def test_missing_and_wrong_version_fail_closed(self):
        result = self.run_guard("--actionlint", "absent-actionlint")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing", result.stderr)
        with mock.patch.object(guard.subprocess, "run", return_value=
                               subprocess.CompletedProcess([], 0, "0.0.0\n", "")):
            with self.assertRaisesRegex(guard.ValidationError, "required"):
                guard.actionlint_binary(self.binary)

    def test_hook_preserves_stdin_and_uses_current_repository(self):
        self.workflow.write_text(INVALID_CONTEXT)
        bad = self.commit()
        self.git("checkout", "-q", "--detach", self.valid)
        result = subprocess.run([str(ROOT / ".githooks/pre-push"), "origin", "unused"],
                                cwd=self.repo, env=self.env, text=True, capture_output=True,
                                input=f"refs/heads/bad {bad} refs/heads/bad {ZERO}\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(bad, result.stdout)
        self.assertIn('context "runner"', result.stdout)


class InstallerTests(unittest.TestCase):
    def test_checksum_failure_never_writes_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "bin"
            with mock.patch.object(installer.platform, "system", return_value="Linux"), \
                 mock.patch.object(installer.platform, "machine", return_value="x86_64"), \
                 mock.patch.object(installer.urllib.request, "urlopen", return_value=io.BytesIO(b"tampered")):
                with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                    installer.install(destination)
            self.assertFalse(destination.exists())

    def test_valid_archive_installs_only_expected_binary(self):
        archive = io.BytesIO()
        with tarfile.open(fileobj=archive, mode="w:gz") as tar:
            for name, data in (("actionlint", b"test binary"), ("../escape", b"not extracted")):
                member = tarfile.TarInfo(name)
                member.size = len(data)
                tar.addfile(member, io.BytesIO(data))
        payload = archive.getvalue()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"version": "1.7.12", "sha256": {
                "linux_amd64": hashlib.sha256(payload).hexdigest()}}))
            with mock.patch.object(installer, "MANIFEST", manifest), \
                 mock.patch.object(installer.platform, "system", return_value="Linux"), \
                 mock.patch.object(installer.platform, "machine", return_value="x86_64"), \
                 mock.patch.object(installer.urllib.request, "urlopen", return_value=io.BytesIO(payload)):
                binary = installer.install(root / "bin")
            self.assertEqual(binary.read_bytes(), b"test binary")
            self.assertTrue(os.access(binary, os.X_OK))
            self.assertFalse((root / "escape").exists())


if __name__ == "__main__":
    unittest.main()
