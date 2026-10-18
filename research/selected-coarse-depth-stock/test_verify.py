"""Independent boundary/proof and fail-closed checks; Apache-2.0."""
import importlib.util
from fractions import Fraction as Q
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("depth_audit", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class ProofChecks(unittest.TestCase):
    def test_complete_small_branch_trees(self):
        # Enumerate all rank choices, rather than selecting the rank-48 child.
        ranks = (1, 2, 3, 4, 5, 7, 8, 48)
        def leaves(n, d):
            if n < 73:
                return [d]
            result = []
            for r in ranks:
                result.extend(leaves(r*(n//73), d + 1))
            return result
        for n in (0, 72, 73, 74, 145, 146, 218, 219, 291, 292, 510, 511, 802, 803, 1898):
            self.assertEqual(max(leaves(n, 0)), v.depth(n))

    def test_threshold_interval_implication(self):
        bs = v.thresholds(2**256)
        for d, b in enumerate(bs, 1):
            self.assertEqual(v.depth(b - 1), d - 1)
            self.assertEqual(v.depth(b), d)
            self.assertEqual(v.depth(b + 1), d)
            if d > 1:
                previous = bs[d - 2]
                self.assertLess(48*((b - 1)//73), previous)
                self.assertGreaterEqual(48*(b//73), previous)

    def test_all_size_threshold_enclosures(self):
        a = Q(73, 48)
        for d, b in enumerate(v.thresholds(2**256), 1):
            self.assertGreaterEqual(b, 73*a**(d - 1))
            self.assertLessEqual(b, Q(5329,25)*a**(d - 1)-Q(3504,25))

    def test_strict_block_and_minimal_domain(self):
        result, count, passed = v.blocks()
        self.assertEqual((result, count, passed), ((43,26),2080,1227))
        self.assertEqual(result, v.independent_block())
        self.assertGreater(73**43, 2**26*48**43)
        # Every strictly better ratio in the declared domain is ruled out.
        for p in range(1,65):
            for q in range(1,p+1):
                if Q(p,q) < Q(43,26):
                    self.assertLessEqual(73**p, 2**q*48**p)

    def test_rounding_and_unpaid_width_controls(self):
        self.assertEqual(v.depth(73),1)
        self.assertGreater(48*((74+72)//73),74)
        self.assertGreater(48*(219//73),219//2)
        self.assertEqual((43*2642+25)//26,4370)
        self.assertLess(4369*26,43*2642)
        for invalid in (True,-1,1.0):
            with self.assertRaises(ValueError):
                v.depth(invalid)

    def test_typed_receipt_and_duplicate_keys(self):
        self.assertFalse(v.same_receipt({"adoption":False},{"adoption":0}))
        self.assertFalse(v.same_receipt({"depth":1},{"depth":1.0}))
        self.assertTrue(v.same_receipt({"a":1,"b":False},{"b":False,"a":1}))
        with self.assertRaises(ValueError):
            v.parse('{"adoption":false,"adoption":true}')

    def test_actual_source_mutation_rejected(self):
        manifest = v.parse((HERE / "SOURCES.json").read_bytes())
        first = next(row for row in manifest["files"] if row["usage"] == "input")
        original = (v.ROOT / first["path"]).read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            destination = root / first["path"]
            destination.parent.mkdir(parents=True)
            destination.write_bytes(original + b" ")
            with patch.object(v, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "source pin"):
                    v.sources()

    def test_receipt_matches_full_replay(self):
        actual = v.run()
        self.assertTrue(v.same_receipt(actual, v.parse((HERE / "RESULT.json").read_bytes())))
        self.assertFalse(actual["conditional_depth_component"]["adoption_claimed"])
        self.assertFalse(actual["stage_parameter_comparison"]["complete_stock_coefficient_known"])
        self.assertFalse(actual["producer_boundary"]["complex_depth_is_ordinary_bootstrap_depth"])


if __name__ == "__main__":
    unittest.main()
