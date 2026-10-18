#!/usr/bin/env python3
"""Failure-sensitive controls for the scoped mathematical and source checks."""
import contextlib
import copy
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import algebra
import runtime_check
verify = runtime_check.load_source("_weighted_contract_driver", PACKAGE / "verify.py")


class ContractControls(unittest.TestCase):
    def test_original_source_and_nontrivial_positive(self):
        self.assertEqual(runtime_check.authenticate(), 12)
        self.assertEqual(len(algebra.controls()["controls"]), 6)

    def test_omitted_first_subtraction_rejects(self):
        def omitted(h, d, p, pinv, q, qinv, add, sub):
            h, d = p[d], pinv[h]
            d = add[d][h]
            h, d = q[d], qinv[h]
            return h, sub[h][d]
        with patch.object(algebra, "word", omitted):
            with self.assertRaisesRegex(ValueError, "two-callee iff criterion"):
                algebra.automorphism_census(3, 1)

    def test_ignoring_second_callee_rejects(self):
        original = algebra.word
        def ignored(h, d, p, pinv, q, qinv, add, sub):
            return original(h, d, p, pinv, p, pinv, add, sub)
        with patch.object(algebra, "word", ignored):
            with self.assertRaisesRegex(ValueError, "two-callee iff criterion"):
                algebra.automorphism_census(2, 2)

    def test_wrong_inverse_in_literal_callee_rejects(self):
        def wrong(address, modulus, weights, gap, suffix):
            self.assertEqual(len(weights), 1)
            pref, h, middle, d, tail = runtime_check.unpack(address, modulus, gap, suffix)
            return runtime_check.pack(pref, weights[0]*d % modulus, middle,
                                      weights[0]*h % modulus, tail, modulus, gap, suffix)
        with runtime_check.installed() as outer:
            with patch.object(runtime_check, "weighted_destination", wrong):
                with self.assertRaisesRegex(ValueError, "literal source origin oracle"):
                    runtime_check.literal_case(outer, q=3, w=2, first=(4,), second=(4,))

    def test_source_byte_corruption_rejects(self):
        manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for item in manifest["files"]:
                if item.get("usage") == "input":
                    target = root / item["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(runtime_check.ROOT / item["path"], target)
            self.assertEqual(runtime_check.authenticate(root), 12)
            target = root / "research/selected-outer-borrowing-wrapper/outer.py"
            target.write_bytes(target.read_bytes() + b"\n# source control\n")
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                runtime_check.authenticate(root)

    def test_typed_and_incomplete_receipts_reject(self):
        original = json.loads((PACKAGE / "RESULT.json").read_text())
        mutations = [copy.deepcopy(original) for _ in range(3)]
        mutations[0]["schema_version"] = True
        del mutations[1]["literal_source"]
        mutations[2]["literal_source"][1]["agreeing_addresses"] += 1
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for changed in mutations:
                (root / "RESULT.json").write_text(json.dumps(changed))
                with patch.object(verify, "PACKAGE", root), patch.object(verify, "run", return_value=original):
                    with patch.object(sys, "argv", ["verify.py"]):
                        with self.assertRaisesRegex(ValueError, "complete typed receipt"):
                            verify.main()

    def test_emission_is_external_and_exclusive(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "receipt.json"
            with patch.object(verify, "run", return_value={"control": 1}):
                with patch.object(sys, "argv", ["verify.py", "--emit-to", str(target)]):
                    with contextlib.redirect_stdout(io.StringIO()):
                        verify.main()
                    with self.assertRaises(FileExistsError):
                        verify.main()
                with patch.object(sys, "argv", ["verify.py", "--emit-to", str(PACKAGE / "never-write.json")]):
                    with self.assertRaisesRegex(ValueError, "emit outside package"):
                        verify.main()

    def test_private_source_namespace_restores_after_error(self):
        before = set(sys.modules)
        with self.assertRaisesRegex(RuntimeError, "injected control"):
            with runtime_check.installed():
                raise RuntimeError("injected control")
        for name in ("_weighted_audit_predecessor", "_weighted_audit_outer", "padding", "source", "words"):
            if name not in before:
                self.assertNotIn(name, sys.modules)


if __name__ == "__main__":
    unittest.main(verbosity=2)
