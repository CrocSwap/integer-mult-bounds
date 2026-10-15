#!/usr/bin/env python3
"""Artifact corruption controls, including an actual copied-source CLI failure."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("binding_verifier", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class Integrity(unittest.TestCase):
    def test_every_source_and_blob(self):
        manifest = json.loads((HERE / "SOURCES.json").read_text())
        records = [(verify.ROOT / r["path"], r) for r in manifest["files"] if r["usage"] == "input"]
        records += [(HERE / r["path"], r) for r in manifest["vendored"]]
        for path, record in records:
            with self.subTest(path=record["path"]):
                data = path.read_bytes()
                verify.authenticate(data, record)
                with self.assertRaisesRegex(ValueError, "source SHA256"):
                    verify.authenticate(data + b"\n", record)
                with self.assertRaisesRegex(ValueError, "source Git blob"):
                    verify.authenticate(data, dict(record, git_blob="0" * 40))

    def test_complete_typed_receipt(self):
        result = json.loads((HERE / "RESULT.json").read_text())
        verify.compare_receipt(result, copy.deepcopy(result))
        mutations = []
        changed = copy.deepcopy(result)
        changed["width_one_root"] = 1  # Python's raw dict equality accepts True == 1.
        self.assertEqual(changed, result)
        mutations.append(changed)
        changed = copy.deepcopy(result)
        changed["fixtures"][0]["values"][0][1] += 1
        mutations.append(changed)
        changed = copy.deepcopy(result)
        changed["fixtures"][0]["global_slots_read"] = []
        mutations.append(changed)
        changed = copy.deepcopy(result)
        del changed["independent_local_oracles"]
        mutations.append(changed)
        for changed in mutations:
            with self.assertRaisesRegex(ValueError, "typed receipt"):
                verify.compare_receipt(result, changed)

    def test_modified_vendor_rejected_before_import(self):
        # The temporary directory is explicitly under the invoking workspace's
        # TMPDIR when set, and no source checkout file is changed.
        with tempfile.TemporaryDirectory(prefix="control-binding-") as temporary:
            copied = Path(temporary) / "package"
            shutil.copytree(HERE, copied, ignore=shutil.ignore_patterns("__pycache__"))
            target = copied / "sources/pr2310/control.py"
            target.write_text(target.read_text() + "\nraise RuntimeError('must not execute')\n")
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(copied / "verify.py"),
                                     "--repository", str(verify.ROOT)],
                                    text=True, capture_output=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source SHA256: sources/pr2310/control.py", result.stderr)
            self.assertNotIn("RuntimeError", result.stderr)


if __name__ == "__main__":
    unittest.main()
