#!/usr/bin/env python3
"""Exercise the two owner-verifier CLI workspace lifecycles. Apache-2.0."""
import contextlib
import io
import json
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = ("half-stage-evacuation", "source-partner-residual-exchanges")


def load_main(package):
    # Load the actual entry point but substitute only the expensive proof body.
    # The optional full mode below runs that body through the registered CLI.
    with mock.patch.object(sys, "path", sys.path.copy()):
        # run_path does not emulate the script-directory import path.
        sys.path.insert(0, str(ROOT / "research" / package))
        namespace = runpy.run_path(str(ROOT / "research" / package / "verify.py"))
    return namespace["main"]


class WorkspaceTests(unittest.TestCase):
    def test_default_repeated_success(self):
        for package in PACKAGES:
            with self.subTest(package=package):
                main = load_main(package)
                paths = []

                def verify(work, paths=paths):
                    self.assertFalse(work.exists())
                    work.mkdir()
                    (work / "RESULT.json").write_text("proof fixture", encoding="utf-8")
                    paths.append(work)

                with mock.patch.dict(main.__globals__, verify=verify):
                    main([])
                    main([])
                self.assertEqual(len(paths), 2)
                self.assertNotEqual(paths[0].parent, paths[1].parent)
                self.assertTrue(all(not path.parent.exists() for path in paths))

    def test_default_failure_cleans_and_propagates(self):
        for package in PACKAGES:
            with self.subTest(package=package):
                main = load_main(package)
                paths = []

                def verify(work, paths=paths):
                    work.mkdir()
                    (work / "partial").write_bytes(b"incomplete")
                    paths.append(work)
                    raise RuntimeError("proof failed")

                with (mock.patch.dict(main.__globals__, verify=verify),
                      self.assertRaisesRegex(RuntimeError, "proof failed")):
                    main([])
                self.assertEqual(len(paths), 1)
                self.assertFalse(paths[0].parent.exists())

    def test_default_interrupt_cleans_and_propagates(self):
        for package in PACKAGES:
            with self.subTest(package=package):
                main = load_main(package)
                paths = []

                def verify(work, paths=paths):
                    work.mkdir()
                    paths.append(work)
                    raise KeyboardInterrupt()

                with (mock.patch.dict(main.__globals__, verify=verify),
                      self.assertRaises(KeyboardInterrupt)):
                    main([])
                self.assertEqual(len(paths), 1)
                self.assertFalse(paths[0].parent.exists())

    def test_explicit_fresh_path_retains_result(self):
        for package in PACKAGES:
            with self.subTest(package=package), tempfile.TemporaryDirectory() as directory:
                main = load_main(package)
                work = Path(directory) / "saved"

                def verify(actual, expected=work):
                    self.assertEqual(actual, expected.resolve())
                    actual.mkdir()
                    (actual / "RESULT.json").write_bytes(b"saved evidence")

                with mock.patch.dict(main.__globals__, verify=verify):
                    main(["--work", str(work)])
                self.assertEqual((work / "RESULT.json").read_bytes(), b"saved evidence")

    def test_explicit_failure_retains_partial_diagnostics(self):
        for package in PACKAGES:
            with self.subTest(package=package), tempfile.TemporaryDirectory() as directory:
                main = load_main(package)
                work = Path(directory) / "failed"

                def verify(actual):
                    actual.mkdir()
                    (actual / "partial").write_bytes(b"diagnostic")
                    raise RuntimeError("proof failed")

                with (mock.patch.dict(main.__globals__, verify=verify),
                      self.assertRaisesRegex(RuntimeError, "proof failed")):
                    main(["--work", str(work)])
                self.assertEqual((work / "partial").read_bytes(), b"diagnostic")

    def test_existing_paths_refused_without_overwrite(self):
        for package in PACKAGES:
            for kind in ("directory", "file", "dangling-link"):
                with self.subTest(package=package, kind=kind):
                    self.check_existing_path(package, kind)

    def check_existing_path(self, package, kind):
        main = load_main(package)
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory) / "existing"
            if kind == "directory":
                work.mkdir()
                sentinel = work / "keep"
                sentinel.write_bytes(b"original")
            elif kind == "file":
                work.write_bytes(b"original")
                sentinel = work
            else:
                try:
                    work.symlink_to(Path(directory) / "absent", target_is_directory=True)
                except OSError as error:
                    self.skipTest("symlink unavailable: " + str(error))
                sentinel = None
            stderr = io.StringIO()
            with mock.patch.dict(main.__globals__, verify=mock.Mock()) as globals_:
                with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as exit_:
                    main(["--work", str(work)])
                self.assertEqual(exit_.exception.code, 2)
                globals_["verify"].assert_not_called()
            self.assertIn("fresh path", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())
            if sentinel is not None:
                self.assertEqual(sentinel.read_bytes(), b"original")
            else:
                self.assertTrue(work.is_symlink())
                self.assertFalse(work.exists())

    def test_registered_commands_use_default_workspace(self):
        for package in PACKAGES:
            with self.subTest(package=package):
                manifest = json.loads((ROOT / "research" / package / "VERIFY.json").read_text())
                self.assertEqual(manifest["commands"][0]["argv"],
                                 ["{python}", "-B", "{package}/verify.py"])


def full_replay():
    """Run real checks twice with an isolated temp root and a stale-work sentinel."""
    for package in PACKAGES:
        with tempfile.TemporaryDirectory(prefix="owner-replay-control-") as directory:
            parent = Path(directory)
            sentinel = parent / "previous-run"
            sentinel.write_bytes(b"do not delete")
            env = dict(os.environ, TMPDIR=directory, TEMP=directory, TMP=directory)
            command = [sys.executable, "-B", "scripts/research_package.py",
                       "--package", "research/" + package]
            outputs = []
            for _ in range(2):
                result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                                        text=True, timeout=310, check=False)
                if result.returncode != 0:
                    raise RuntimeError(result.stdout + result.stderr)
                expected = "PASS_REGISTERED_RESEARCH_PACKAGE research/" + package
                if expected not in result.stdout or "PASS_LITERAL_OWNERS_AND_EXACT_MOMENT" not in result.stdout:
                    raise RuntimeError("missing actual replay marker: " + result.stdout)
                if set(parent.iterdir()) != {sentinel} or sentinel.read_bytes() != b"do not delete":
                    raise RuntimeError("temporary replay leaked state or changed preexisting data")
                outputs.append(result.stdout)
            if outputs[0] != outputs[1]:
                raise RuntimeError("repeated replay stdout differs")
            print("PASS_REPEAT_REGISTERED_OWNER_REPLAY " + package, flush=True)


if __name__ == "__main__":
    full = sys.argv[1:] == ["--full"]
    if sys.argv[1:] not in ([], ["--full"]):
        raise SystemExit("usage: verify.py [--full]")
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(WorkspaceTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
    if full:
        full_replay()
    print("PASS_OWNER_REPLAY_WORKSPACE_CONTROLS", flush=True)
