#!/usr/bin/env python3
"""Behavioral controls for the fixed receipts and independent mathematics.

Apache-2.0; substantial OpenAI Codex assistance. Tests never rewrite evidence.
"""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


primary = load("qq16_primary", HERE / "verify.py")
oracle = load("qq16_oracle", HERE / "independent.py")


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = primary.build(REPO)
        cls.receipt = json.loads((HERE / "RESULT.json").read_text())

    def test_fixed_receipts_and_independent_source_derivation(self):
        primary.validate(self.receipt, self.actual)
        other = oracle.audit(REPO)
        expected = json.loads((HERE / "ORACLE.json").read_text())
        self.assertEqual(oracle.canonical(other), oracle.canonical(expected))
        first = self.actual["route_audit"]
        for key in ("R_dense_sha256", "routes_U96_stage_major_sha256"):
            self.assertEqual(first[key], other["reconstruction"][key])
        self.assertEqual(first["ordinary_gram"], other["same_stage_gram"])
        for key, pair in first["pairs"].items():
            self.assertEqual(pair["identity_coefficient"], other["stage_pairs"][key]["identity_coefficient"])
            self.assertEqual(pair["distinct_routes"], other["stage_pairs"][key]["distinct_relative_routes"])
        bounds = other["trace_coefficients_per_regular_cover_order"]
        self.assertEqual(first["trace_per_cover_owner"], bounds["stacked_Gram_trace"])
        self.assertEqual(first["square_trace_per_cover_owner"], bounds["stacked_Gram_square_trace"])
        self.assertEqual(first["stacked_rank_lower_per_cover_owner"], bounds["stacked_query_rank_lower_bound"])
        self.assertEqual(first["missing_A_dimension_lower_per_cover_owner"],
                         bounds["rank_B0_restricted_to_joint_kernel_B1_B2_lower_bound"])

    def test_complete_receipt_rejects_semantic_and_typed_corruption(self):
        mutants = []
        bad = deepcopy(self.receipt)
        bad["route_audit"]["missing_A_dimension_lower_per_cover_owner"] = "33/7"
        mutants.append(bad)
        bad = deepcopy(self.receipt)
        bad["route_audit"]["pairs"]["0,1"]["identity_coefficient"][0][0] -= 1
        bad["route_audit"]["pairs"]["0,1"]["identity_coefficient"][1][1] += 1
        mutants.append(bad)  # same trace, different matrix
        bad = deepcopy(self.receipt)
        del bad["tail"][2]
        mutants.append(bad)
        bad = deepcopy(self.receipt)
        bad["finite_fixture"]["after_B1_only_YU"] = 1
        mutants.append(bad)  # bool and integer must remain distinct
        bad = deepcopy(self.receipt)
        bad["unpriced_native_gain"] = True
        mutants.append(bad)
        for bad in mutants:
            with self.subTest(change=str(bad)[:60]):
                with self.assertRaisesRegex(primary.CheckError, "complete fixed receipt"):
                    primary.validate(bad, self.actual)
        # Formatting/key order is intentionally not a semantic difference.
        reformatted = json.loads(json.dumps(self.receipt, sort_keys=True, indent=4))
        primary.validate(reformatted, self.actual)

    def test_missing_receipts_and_no_overwrite(self):
        before = (HERE / "RESULT.json").read_bytes()
        with tempfile.TemporaryDirectory(prefix="qq16-receipts-") as tmp:
            missing = Path(tmp) / "missing.json"
            run = subprocess.run([sys.executable, "-I", "-B", str(HERE / "verify.py"),
                                  "--repo", str(REPO), "--certificate", str(missing)],
                                 text=True, capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("FileNotFoundError", run.stderr)
            self.assertFalse(missing.exists())
            run = subprocess.run([sys.executable, "-I", "-B", str(HERE / "verify.py"),
                                  "--repo", str(REPO), "--write", str(HERE / "RESULT.json")],
                                 text=True, capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("FileExistsError", run.stderr)
        self.assertEqual(before, (HERE / "RESULT.json").read_bytes())

    def test_live_source_drift(self):
        # A small shadow of live input paths tests byte drift without editing
        # frozen sources or making another Git checkout. Git reads use REPO.
        sources = json.loads((HERE / "SOURCES.json").read_text())["files"]
        with tempfile.TemporaryDirectory(prefix="qq16-source-") as tmp:
            root = Path(tmp)
            for item in sources:
                if item["usage"] != "input":
                    continue
                target = root / item["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(REPO / item["path"])
            name = "research/joint-query/evidence/JOINT-QUERY-TRANSFER.md"
            target = root / name
            target.unlink()
            target.write_bytes((REPO / name).read_bytes() + b"\nchanged source\n")
            command = primary.subprocess.check_output
            def git_read(args, **kwargs):
                kwargs["cwd"] = REPO
                return command(args, **kwargs)
            with patch.object(primary.subprocess, "check_output", side_effect=git_read):
                with self.assertRaisesRegex(primary.CheckError, "live source: " + name):
                    primary.authenticate(root)

    def test_independent_controls_fail_when_named_guards_are_removed(self):
        source = (HERE / "independent.py").read_text()
        guards = [
            'require(len(relative_routes) == len(set(relative_routes)) == 96,\n            "96 distinct relative routes")',
            'require(gram(columns) == scalar_identity(48), "ordinary column Gram")',
        ]
        for guard in guards:
            self.assertEqual(source.count(guard), 1)
            mutant = types.ModuleType("qq16_guard_removed")
            mutant.__file__ = str(HERE / "independent.py")
            exec(compile(source.replace(guard, "pass"), mutant.__file__, "exec"), mutant.__dict__)
            with self.assertRaisesRegex(mutant.AuditError, "negative control unexpectedly accepted"):
                mutant.audit(REPO)

    def test_normal_optimized_and_relocated_verification_preserve_artifacts(self):
        # Package relocation uses an explicitly supplied original Git repo.
        # This is not a source-export or full copied-repository cold replay.
        names = ["RESULT.json", "ORACLE.json", "SOURCES.json"]
        before = {name: (HERE / name).read_bytes() for name in names}
        with tempfile.TemporaryDirectory(prefix="qq16-relocated-") as tmp:
            moved = Path(tmp) / "package"
            shutil.copytree(HERE, moved, ignore=shutil.ignore_patterns("__pycache__"))
            outputs = []
            for optimize in ([], ["-O"]):
                run = subprocess.run([sys.executable, "-I", *optimize, "-B", str(moved / "verify.py"),
                                      "--repo", str(REPO)], cwd=tmp, text=True, capture_output=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                outputs.append(run.stdout)
            self.assertEqual(outputs[0], outputs[1])
            self.assertIn("PASS_QQ16_EXTRA_QUERY_RESIDUAL", outputs[0])
            for name in names:
                self.assertEqual((moved / name).read_bytes(), before[name])
        for name in names:
            self.assertEqual((HERE / name).read_bytes(), before[name])


if __name__ == "__main__":
    unittest.main(verbosity=2)
