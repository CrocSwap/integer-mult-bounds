"""Behavioral controls for stock policy, binding and the typed replay boundary."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify
from arithmetic import depth, guard_chain


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.namespace = verify.activate()

    @classmethod
    def tearDownClass(cls):
        cls.namespace.cleanup()

    def test_source_corruption(self):
        original = Path.read_bytes
        target = verify.ROOT / "research/physical-ordinary-interchange/encoded.py"
        def read(path):
            data = original(path)
            return data + b"# changed\n" if path == target else data
        with patch.object(Path, "read_bytes", read), self.assertRaisesRegex(ValueError, "source pin"):
            verify.authenticate()

    def test_proof_corruption(self):
        original = Path.read_bytes
        def read(path):
            return original(path) + (b"changed" if path.name == "pr3246-README.md" else b"")
        with patch.object(Path, "read_bytes", read), self.assertRaisesRegex(ValueError, "PR3246 proof"):
            verify.authenticate()

    def test_invalid_compiled_contracts(self):
        import encoded
        from cardinal_counts import Count
        from selector import select_guard_stock
        original = Count.literal(32)
        try:
            for radix, profile, q in ((1, encoded.Profile(), 2),
                                       (2, encoded.Profile(), 0),
                                       (2, encoded.Profile(dimension=2, child_rank=2), 2),
                                       (2, encoded.Profile(denominator=0), 2),
                                       (2, encoded.Profile(numerator=2, denominator=1), 2),
                                       (2, encoded.Profile(row_factor=0), 2)):
                with self.subTest(radix=radix, profile=profile, q=q), self.assertRaises(ValueError):
                    select_guard_stock(original, radix, profile, q)
        finally:
            original.close()

    def test_complete_vs_first_guard(self):
        self.assertTrue(guard_chain(36, 6, 2, 1))
        self.assertFalse(guard_chain(36, 6, 2, 2))
        self.assertTrue(guard_chain(72, 6, 2, 2))
        self.assertNotEqual(72 % 144, 0)

    def test_body_depth_is_not_root_depth(self):
        self.assertGreater(depth(32, 2, 1), depth(18, 2, 1))

    def test_typed_receipt_controls(self):
        # Use the actual CLI receipt comparator, but a tiny injected setup so
        # this boundary test doesn't repeat the costly encoded census.
        expected = json.loads((HERE / "RESULT.json").read_text())["setup"]
        for key, value in (("peak_setup_roles", True), ("selections", [])):
            bad = dict(expected)
            bad[key] = value
            with self.subTest(key=key), patch.object(sys, "argv", ["verify", "--suite", "setup"]), \
                    patch.object(verify, "activate", return_value=__import__('contextlib').nullcontext()), \
                    patch.object(verify, "setup", return_value=bad), \
                    self.assertRaisesRegex(ValueError, "complete typed receipt"):
                verify.main()

    def test_original_failure_controls(self):
        import check_controls
        result = check_controls.run()
        self.assertEqual(result["count"], 12)
        self.assertIn("equal-valued wrong origin", result["controls"])
        self.assertIn("explicit final lease release", result["controls"])

    def test_existing_output_refused(self):
        with patch.object(sys, "argv", ["verify", "--suite", "setup", "--emit-to", str(HERE/"RESULT.json")]), \
                patch.object(verify, "activate", return_value=__import__('contextlib').nullcontext()), \
                patch.object(verify, "setup", return_value={}), self.assertRaises(FileExistsError):
            verify.main()


if __name__ == "__main__":
    unittest.main(verbosity=2)
