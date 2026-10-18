#!/usr/bin/env python3
"""Behavioral controls for source binding and the public audit command. Apache-2.0."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("entrance_audit", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class BindingControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, (cls.A, cls.B) = V.load_inputs()
        cls.rows, cls.records = V.check_binding(cls.data["base"], cls.A)

    def test_missing_provider_rejected(self):
        with self.assertRaisesRegex(V.Reject, "both fixed providers"):
            V.verify({"base": self.data["base"]}, self.A, self.B, controls=False)

    def test_extra_provider_is_actually_checked(self):
        bad = copy.deepcopy(self.data)
        r = bad["extra"]["canon"]["start"][V.ORIGINS[-1]]
        bad["extra"]["adapters"]["recipes"][str(r)]["rank"] = 8
        with self.assertRaisesRegex(V.Reject, "rank-seven recipe"):
            V.verify(bad, self.A, self.B, controls=False)

    def test_marker_only_misplacement_rejected(self):
        bad = copy.deepcopy(self.data["base"])
        events = bad["programs"]["backward"]
        i = events.index(["phase", "full_frame_cleanup"])
        marker = events.pop(i)
        post = next(i for i, e in enumerate(events) if e[:3] == ["residual_adapter", "post", 474])
        events.insert(post + 1, marker)
        with self.assertRaisesRegex(V.Reject, "wrapper phase placement"):
            V.check_binding(bad, self.A)

    def test_each_kernel_control_detects_an_accept_all_fault(self):
        # Fault-sensitive harness: independently suppress each operator decision.
        for function in ("exact_a", "exact_b"):
            with self.subTest(function=function), patch.object(V, function, return_value=True):
                with self.assertRaisesRegex(V.Reject, "rejects global_phase"):
                    V.semantic_controls(self.data["base"], self.A, self.B, self.records[:1])

    def test_fixed_inputs_fail_before_decode_or_import(self):
        with tempfile.TemporaryDirectory(prefix="entrance-input-fault-") as d:
            p = Path(d) / "package"; shutil.copytree(HERE, p)
            manifest = json.loads((p / "INPUTS.json").read_text())
            # Retain14 rows but omit a kernel from the authenticated inventory.
            row = next(x for x in manifest["files"] if x["path"] == "vendor/clifford.py")
            row["path"] = "unused.py"; (p / "unused.py").write_text("raise RuntimeError('not imported')\n")
            (p / "INPUTS.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(V.Reject, "complete distinct fixed inputs"):
                V.load_inputs(p)
            shutil.copyfile(HERE / "INPUTS.json", p / "INPUTS.json")
            kernel = p / "vendor/clifford.py"
            kernel.write_text("raise RuntimeError('must reject hash before import')\n")
            with self.assertRaisesRegex(V.Reject, "immutable input hash"):
                V.load_inputs(p)

    def test_public_cli_missing_evidence_fails_optimized(self):
        with tempfile.TemporaryDirectory(prefix="entrance-cli-fault-") as d:
            p = Path(d) / "package"; shutil.copytree(HERE, p)
            (p / "inputs/extra-RESIDUAL-ADAPTERS.json").unlink()
            proc = subprocess.run([sys.executable, "-I", "-O", "-B", str(p / "verify.py")],
                                  cwd=d, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("FAIL_T74_RAISED_ENTRANCE_WRAPPERS", proc.stderr)
            self.assertNotIn("PASS_T74_RAISED_ENTRANCE_WRAPPERS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
