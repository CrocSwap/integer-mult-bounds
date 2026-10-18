#!/usr/bin/env python3
"""Semantic and rejection tests; the registered verifier owns the full census."""
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
spec = importlib.util.spec_from_file_location("gl3_verify", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class SemanticChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.words = v.direct_census()
        cls.formal = v.Formal(cls.words)
        cls.witness = tuple((*v.PAIRS[gi], u, u) for u in (1, 2) for gi in cls.words[v.H])

    def test_every_generator_and_pair_commutes_with_natural_map(self):
        for first in v.GENERATORS:
            expected_first = v.natural_step(v.I6, first)
            self.assertEqual(self.formal.natural(self.formal.word([first])), expected_first)
            self.assertEqual(v.natural_step(expected_first, first), v.I6)
            for second in v.GENERATORS:
                self.assertEqual(self.formal.natural(self.formal.word([first, second])),
                                 v.natural_step(expected_first, second))

    def test_scalar_conjugation_preserves_complete_alphabet(self):
        independent = v.load_independent()
        scalars = [(a, b) for a in range(4) for b in range(4) if v.rank((a, b)) == 2]
        projectors = {tuple(vv if u >> i & 1 else 0 for i in range(2))
                      for u, vv in v.IDEMPOTENTS}
        self.assertEqual(projectors, set(independent.scalar_projectors()))
        self.assertEqual(len(projectors), 6)
        for b in scalars:
            inverse = independent.inverse(b)
            for n in projectors:
                conjugate = v.multiply_rows(b, v.multiply_rows(n, inverse))
                self.assertIn(conjugate, projectors)

    def test_nonfaithful_alias_is_rejected_formally(self):
        target = self.formal.target()
        powers = [v.I3]
        for _ in range(3):
            powers.append(v.multiply_rows(v.H, powers[-1]))
        alias = list(target)
        alias[1] = sum(1 << self.formal.index[g] for g in powers)
        self.assertNotEqual(tuple(alias), target)
        self.assertEqual(self.formal.natural(tuple(alias)), self.formal.natural(target))
        self.assertEqual(alias[1].bit_count() % 2, 0)  # augmentation does not detect it

    def test_regular_engine_rejects_wrong_chronology(self):
        independent = v.load_independent()
        self.assertEqual(independent.check_regular(self.witness, v.H), 336)
        with self.assertRaisesRegex(ValueError, "regular column"):
            independent.check_regular(tuple(reversed(self.witness)), v.H)

    def test_receipt_corruption_fails(self):
        receipt = json.loads((HERE / "EXPECTED.json").read_text())
        for field in ("radius_three_four_target_meets", "paid_generator_count", "target_order"):
            changed = copy.deepcopy(receipt)
            changed[field] += 1
            with self.assertRaisesRegex(ValueError, "receipt mismatch"):
                v.compare_receipt(receipt, changed)

    def test_source_corruption_fails(self):
        with tempfile.TemporaryDirectory(dir=HERE.parent) as tmp:
            root = Path(tmp)
            package = root / "research" / "gl3-order4-register-census"
            package.mkdir(parents=True)
            shutil.copy(HERE / "SOURCES.json", package)
            pins = json.loads((package / "SOURCES.json").read_text())
            for entry in pins["files"]:
                if entry["usage"] == "input":
                    target = root / entry["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text("incorrect source bytes\n")
            with self.assertRaisesRegex(ValueError, "source SHA256 mismatch"):
                v.source_checks(package)

    def test_optimized_cli_rejects_corrupt_receipt(self):
        with tempfile.TemporaryDirectory(dir=HERE.parent) as tmp:
            path = Path(tmp) / "wrong.json"
            receipt = json.loads((HERE / "EXPECTED.json").read_text())
            receipt["claim"] = "FALSE_CLAIM"
            path.write_text(json.dumps(receipt))
            run = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"),
                                  "--expected", str(path)], capture_output=True, text=True,
                                 timeout=90)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("expected receipt mismatch", run.stderr)


if __name__ == "__main__":
    unittest.main()
