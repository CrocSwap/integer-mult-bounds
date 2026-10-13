#!/usr/bin/env python3
"""Failure-mode and independent-completeness controls; Apache-2.0."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import oracle
import verify


class ResidualAuditTests(unittest.TestCase):
    def test_independent_powerset_census(self):
        # Different enumeration: inspect every subset of the 15 nonzero vectors.
        # Direct XOR closure identifies all subspaces, without the extension tree.
        brute = set()
        for mask in range(1 << 15):
            space = frozenset([0] + [i + 1 for i in range(15) if mask >> i & 1])
            if all(a ^ b in space for a in space for b in space):
                brute.add(space)
        self.assertEqual(brute, set(oracle.list_subspaces(4)))
        self.assertEqual(len(brute), 67)

    def test_direct_projection_and_characteristic(self):
        plane = oracle.span((3, 5), 3)
        full = oracle.span((1, 2, 4), 3)
        self.assertEqual(oracle.characteristic(plane, 3), 0)
        self.assertEqual(oracle.characteristic(full, 3), 7)
        self.assertEqual(oracle.residual(plane, full, 3), oracle.span((7,), 3))
        for x in range(8):
            projected = oracle.project(plane, x, 3)
            self.assertIn(projected, plane)
            self.assertTrue(all(oracle.dot(projected ^ x, y, 3) == 0 for y in plane))
        # Isotropic characteristic != alternating form.
        f2 = oracle.span((1, 2), 2)
        self.assertEqual(oracle.characteristic(f2, 2), 3)
        self.assertFalse(oracle.classify(f2, 2)["alternating"])

    def test_invalid_domains(self):
        for n in (-1, True, 1.5, 7):
            with self.assertRaises(ValueError):
                oracle.list_subspaces(n)
        for vector in (-1, 8, True):
            with self.assertRaises(ValueError):
                oracle.dot(vector, 1, 3)
        for space in ((1,), (0, 1, 2), None):
            with self.assertRaises(ValueError):
                oracle.classify(space, 3)
        with verify.subjects() as (frames, parity):
            for cap in (-1, True, 1.5, 7):
                with self.assertRaises(ValueError):
                    verify.audit(frames, parity, cap)

    def test_predecessor_assertions_and_boundary_controls(self):
        with verify.subjects() as (frames, parity):
            self.assertEqual(len(verify.controls(frames, parity)), 10)
            # This must fail under -O too: source is compiled with optimize=0.
            with self.assertRaises(AssertionError):
                frames.orthonormal_basis((3, 5))
            result = verify.audit(frames, parity, cap=3)
            self.assertEqual(result["coverage"][-1]["nested_pairs"], 33)
            self.assertEqual(result["coverage"][-1]["nonzero_alternating_pairs"], 2)

    def test_faulty_subjects_detected(self):
        with verify.subjects() as (frames, parity):
            real_classify = frames.classify
            def wrong_classify(rows):
                result = real_classify(rows)
                result["nonalternating"] = not result["nonalternating"]
                return result
            with patch.object(frames, "classify", wrong_classify):
                with self.assertRaisesRegex(ValueError, "Classification mismatch"):
                    verify.audit(frames, parity, cap=1)
            with patch.object(parity, "characteristic", lambda rows: 0):
                with self.assertRaisesRegex(ValueError, "Characteristic mismatch"):
                    verify.audit(frames, parity, cap=1)
            with patch.object(frames, "residual", lambda lower, upper: ()):
                with self.assertRaisesRegex(ValueError, "Residual set mismatch"):
                    verify.audit(frames, parity, cap=1)
            real_basis = frames.orthonormal_basis
            def wrong_basis(rows):
                result = real_basis(rows)
                return (1, 2, 7) if len(result) == 3 else result
            with patch.object(frames, "orthonormal_basis", wrong_basis):
                with self.assertRaisesRegex(ValueError, "Nonorthonormal output"):
                    verify.audit(frames, parity, cap=3)

    def test_pins_and_typed_receipt_controls(self):
        manifest = json.loads((HERE / "SOURCES.json").read_text())
        verify.check_sources()
        missing = json.loads(json.dumps(manifest))
        missing["files"].pop(verify.SOURCE_PATHS[0])
        with self.assertRaisesRegex(ValueError, "Incomplete source inventory"):
            verify.check_sources(manifest=missing)
        for key in ("sha256", "git_blob"):
            bad = json.loads(json.dumps(manifest))
            bad["files"][verify.SOURCE_PATHS[0]][key] = "0" * len(bad["files"][verify.SOURCE_PATHS[0]][key])
            with self.assertRaisesRegex(ValueError, "mismatch"):
                verify.check_sources(manifest=bad)
        expected = json.loads((HERE / "EXPECTED.json").read_text())
        for replacement in (True, 1.0, 2):
            bad = json.loads(json.dumps(expected))
            bad["coverage"][0]["subspaces"] = replacement
            self.assertFalse(verify.same_typed(expected, bad))
            with patch.object(verify, "audit", return_value=expected):
                with self.assertRaisesRegex(ValueError, "Exact typed receipt mismatch"):
                    verify.run(expected=bad)
        with verify.subjects() as (frames, parity):
            small = verify.audit(frames, parity, cap=1)
        with patch.object(verify, "audit", return_value=small):
            with self.assertRaisesRegex(ValueError, "Exact typed receipt mismatch"):
                verify.run(expected={})
        real_spaces = oracle.list_subspaces
        with verify.subjects() as (frames, parity):
            with patch.object(oracle, "list_subspaces", lambda n: real_spaces(n)[:-1]):
                with self.assertRaisesRegex(ValueError, "Incomplete all-subspace census"):
                    verify.audit(frames, parity, cap=1)

    def test_minimal_relocation_and_output_preservation(self):
        with tempfile.TemporaryDirectory(prefix="binary audit with spaces ") as tmp:
            root = Path(tmp)
            package = root / "research/binary-residual-exhaustive"
            package.mkdir(parents=True)
            for relative in verify.SOURCE_PATHS:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(verify.ROOT / relative, destination)
            for name in ("verify.py", "oracle.py", "SOURCES.json", "EXPECTED.json"):
                shutil.copy2(HERE / name, package / name)
            cmd = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
            # Minimal source closure: no .git, predecessor tests are pinned context,
            # and no repository module beyond the three declared subjects is loaded.
            result = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True, check=True)
            self.assertIn("PASS_BINARY_RESIDUAL_EXHAUSTIVE", result.stdout)
            output = root / "keep.json"
            output.write_text("preserve me\n")
            (root / verify.SOURCE_PATHS[0]).write_text("corrupt source\n")
            failure = subprocess.run(cmd + ["--output", str(output)], cwd=tmp,
                                     capture_output=True, text=True)
            self.assertNotEqual(failure.returncode, 0)
            self.assertIn("Source SHA256 mismatch", failure.stderr)
            self.assertEqual(output.read_text(), "preserve me\n")
            (root / verify.SOURCE_PATHS[0]).unlink()
            with self.assertRaisesRegex(ValueError, "Missing/escaping source"):
                verify.check_sources(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
