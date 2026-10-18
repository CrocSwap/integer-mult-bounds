#!/usr/bin/env python3
"""Behavioral controls for the scoped fallback certificate. Apache-2.0."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import fallback as F
import oracle as O
import verify as V


class FallbackControls(unittest.TestCase):
    def test_semantic_controls(self):
        self.assertEqual(len(V.semantic_controls()), 12)

    def test_complete_coefficient_guard_is_sensitive(self):
        matrix = [[1, 3], [0, 1]]
        plan = F.compile_fallback(matrix, 3, 2)
        plan["operations"] = [op for op in plan["operations"]
                              if not (op[0] == "add" and op[3] == 3)]
        with self.assertRaisesRegex(O.OracleError, "compiled operator coefficient"):
            O.audit_plan(matrix, plan)
        # The same mutant is accepted if the named complete-coefficient guard
        # is actually removed. This prevents a vacuous negative control.
        with patch.object(O, "_assert_operator", return_value=None):
            O.audit_plan(matrix, plan)

    def test_independent_template_guard(self):
        plan = F.compile_fallback(F.identity(2), 3, 2)
        plan["reductions"] = []
        O.audit_plan(F.identity(2), plan)
        with self.assertRaisesRegex(O.OracleError, "complete shear slots"):
            O.audit_template(plan)
        with self.assertRaisesRegex(F.ContractError, "fixed shear skeleton"):
            V.audit_template(plan)

    def test_weighted_target_is_not_trusted(self):
        matrix = [[3, 1], [8, 0]]
        weights = [[2, 4], [4, 8], [8, 7]]
        block = F.compile_weighted_block(matrix, weights, 3, 2)
        O.audit_weighted_block(matrix, weights, block)
        block["matrices_by_atom"][0][0][0] ^= 1
        with self.assertRaisesRegex(O.OracleError, "target binding"):
            O.audit_weighted_block(matrix, weights, block)

    def test_arbitrary_spectator_defect(self):
        matrix = [[0, 1], [1, 0]]
        word = [["weighted_swap", 0, 1, 1]]
        O.audit_fields(matrix, word, 9, atoms=3, spectator_fields=3,
                       field_positions=[1, 3])
        original = O.execute_fields

        def erase_spectator(*args, **kwargs):
            state = original(*args, **kwargs)
            state[0] = 0
            return state

        with patch.object(O, "execute_fields", side_effect=erase_spectator):
            with self.assertRaisesRegex(O.OracleError, "operator coefficient"):
                O.audit_fields(matrix, word, 9, atoms=3, spectator_fields=3,
                               field_positions=[1, 3])

    def test_mixed_orientation_descriptor_defect(self):
        weights = [2, 4, 5]
        targets = [[[0, a], [pow(a, -1, 9), 0]] for a in weights]
        word = [["weighted_swap", 0, 1, weights]]
        O.audit_fields(targets[0], word, 9, atoms=3, matrices_by_atom=targets,
                       orientations=[-1, 1])
        original = O._reversed_call

        def wrong_descriptor(state, first, second, descriptor, modulus):
            return original(state, first, second, descriptor[::-1], modulus)

        with patch.object(O, "_reversed_call", side_effect=wrong_descriptor):
            with self.assertRaisesRegex(O.OracleError, "operator coefficient"):
                O.audit_fields(targets[0], word, 9, atoms=3, matrices_by_atom=targets,
                               orientations=[-1, 1])

    def test_equivalent_factor_presentation(self):
        matrix = [[2, 1], [3, 2]]
        plan = F.compile_fallback(matrix, 3, 2)
        plan["operations"] += [["add", 1, 0, 4], ["add", 1, 0, 5]]
        # The operator consumer admits harmless cancelling factors. The
        # separate skeleton contract need not admit alternate compilers.
        O.audit_plan(matrix, plan)

    def test_full_high_lifts_need_zero_slots(self):
        a = F.compile_fallback([[1, 0], [0, 1]], 3, 2)
        b = F.compile_fallback([[1, 3], [0, 1]], 3, 2)
        self.assertEqual(V.topology(a["operations"]), V.topology(b["operations"]))
        self.assertNotEqual(a["reductions"], b["reductions"])
        sparse = lambda p: [op for op in p["reductions"] if op[0] != "add" or op[3]]
        self.assertNotEqual(V.topology(sparse(a)), V.topology(sparse(b)))

    def test_source_corruption_and_pin_omission(self):
        with tempfile.TemporaryDirectory(prefix="fallback-source-") as tmp:
            root = Path(tmp)
            for path in V.INPUTS:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(V.ROOT / path, dest)
            V.bind_sources(root)
            target = root / V.INPUTS[1]
            target.write_bytes(target.read_bytes() + b" ")
            with self.assertRaisesRegex(F.ContractError, "source SHA256"):
                V.bind_sources(root)
            manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
            manifest["files"] = [x for x in manifest["files"] if x["path"] != V.INPUTS[1]]
            path = root / "omit-pin.json"
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(F.ContractError, "complete external-input set"):
                V.bind_sources(root, path)

    def test_archive_member_binding_is_checked(self):
        with patch.object(V, "MEMBER_SHA", "0" * 64):
            with self.assertRaisesRegex(F.ContractError, "assembler member SHA256"):
                V.bind_sources()

    def test_fixed_receipt_missing_corrupt_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="fallback-receipt-") as tmp:
            root = Path(tmp)
            missing = root / "missing.json"
            cmd = [sys.executable, "-I", "-O", "-B", str(PACKAGE / "verify.py")]
            result = subprocess.run(cmd + ["--result", str(missing)], text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("fixed receipt is missing", result.stderr)
            self.assertFalse(missing.exists())
            supplied = root / "receipt.json"
            supplied.write_text('{"wrong": true}\n')
            original = supplied.read_bytes()
            with self.assertRaisesRegex(F.ContractError, "fixed result receipt differs"):
                V.check_receipt(supplied, {"wrong": False})
            result = subprocess.run(cmd + ["--write-result", str(supplied)], text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must not exist", result.stderr)
            self.assertEqual(supplied.read_bytes(), original)

    def test_read_only_relocated_replay(self):
        with tempfile.TemporaryDirectory(prefix="fallback-relocated-") as tmp:
            root = Path(tmp)
            relocated = root / "research" / PACKAGE.name
            shutil.copytree(PACKAGE, relocated, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            for path in V.INPUTS:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(V.ROOT / path, dest)
            files = [p for p in root.rglob("*") if p.is_file()]
            before = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            directories = [p for p in root.rglob("*") if p.is_dir()]
            try:
                for p in files:
                    p.chmod(0o444)
                for p in directories:
                    p.chmod(0o555)
                cmd = [sys.executable, "-I", "-B"]
                if not __debug__:
                    cmd.append("-O")
                result = subprocess.run(cmd + [str(relocated / "verify.py")],
                                        cwd=root, text=True, capture_output=True, timeout=180)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("PASS_SELECTED_BIT_BAD_CLASS_FALLBACK", result.stdout)
                after = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in root.rglob("*") if p.is_file()}
                self.assertEqual(before, after)
            finally:
                for p in directories:
                    p.chmod(0o755)
                for p in files:
                    p.chmod(0o644)


if __name__ == "__main__":
    unittest.main()
