"""Hand-derived controls for the independent valuation engine."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "newton_verify", Path(__file__).with_name("verify.py")
)
ENGINE = importlib.util.module_from_spec(SPEC)
if SPEC.loader is not None and Path(SPEC.origin).exists():
    SPEC.loader.exec_module(ENGINE)


class ValuationTests(unittest.TestCase):
    def test_radix_four_integer_coefficients(self):
        # Dropping a tail factor, rotating in the wrong direction, or reducing
        # x^2 as +1 instead of -1 breaks this hand-calculated fixture.
        self.assertTrue(hasattr(ENGINE, "tail_coefficients"), "engine not implemented")
        self.assertEqual(
            ENGINE.tail_coefficients(4, 1),
            [(4, 0), (2, 2), (1, 1), (1, 0)],
        )

    def test_ramified_weights_include_integer_prime_factors(self):
        # v(2)=2 and v(1-i)=1 in Q_2(i); a plain mod-2 residue is insufficient.
        self.assertTrue(hasattr(ENGINE, "coefficient_valuation"), "engine not implemented")
        self.assertEqual(
            [ENGINE.coefficient_valuation(c, 2, 2)
             for c in [(4, 0), (2, 2), (1, 1), (1, 0)]],
            [4, 3, 1, 0],
        )

    def test_polygon_excludes_points_above_its_edges(self):
        self.assertTrue(hasattr(ENGINE, "lower_hull"), "engine not implemented")
        self.assertEqual(
            ENGINE.lower_hull([12, 11, 9, 8, 4, 3, 1, 0]),
            [(0, 12), (4, 4), (6, 1), (7, 0)],
        )
        self.assertEqual(
            ENGINE.lower_hull([12, 11, 10, 7, 6, 5, 2, 1, 0]),
            [(0, 12), (6, 2), (8, 0)],
        )

    def test_rejects_nonprimitive_and_non_prime_power_inputs(self):
        self.assertTrue(hasattr(ENGINE, "tail_coefficients"), "engine not implemented")
        for radix, power in [(4, 2), (9, 3), (12, 1), (1, 1)]:
            with self.subTest(radix=radix, power=power):
                with self.assertRaises(ValueError):
                    ENGINE.tail_coefficients(radix, power)

    def test_mod_ideal_preserving_tamper_is_rejected(self):
        self.assertTrue(hasattr(ENGINE, "check_coefficients"), "engine not implemented")
        # Both 2+2i and 4+4i vanish modulo (1-i), but their valuations differ.
        coefficients = [(4, 0), (4, 4), (1, 1), (1, 0)]
        with self.assertRaises(ValueError):
            ENGINE.check_coefficients(4, coefficients)

    def test_shifted_cyclotomic_is_eisenstein(self):
        # A dropped geometric-sum term or wrong binomial sign breaks these.
        self.assertTrue(hasattr(ENGINE, "shifted_cyclotomic"), "not implemented")
        self.assertEqual(ENGINE.shifted_cyclotomic(4), [2, -2, 1])
        self.assertEqual(ENGINE.shifted_cyclotomic(9), [3, -9, 18, -21, 15, -6, 1])

    def test_repeated_integral_division_counts_uniformizer_factors(self):
        # The second engine must divide by 1-i, not by the rational prime 2.
        self.assertTrue(hasattr(ENGINE, "division_valuation"), "not implemented")
        self.assertEqual(
            [ENGINE.division_valuation(c, 4)
             for c in [(4, 0), (2, 2), (1, 1), (1, 0), (1, -1)]],
            [4, 3, 1, 0, 1],
        )
        with self.assertRaises(ValueError):
            ENGINE.division_valuation((0, 0), 4)

    def test_checker_rejects_changed_receipt(self):
        # Success cannot be reported from an unchecked stored status string.
        self.assertTrue(hasattr(ENGINE, "replay"), "replay not implemented")
        receipt = ENGINE.replay()
        self.assertEqual(receipt["embedding_count"], 214)
        self.assertEqual(receipt["coefficient_count"], 10268)
        receipt["embedding_count"] = 213
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tampered.json"
            path.write_text(json.dumps(receipt), encoding="utf-8")
            process = subprocess.run(
                [sys.executable, "-B", "-I", "-O", SPEC.origin, "--check", str(path)],
                capture_output=True, text=True,
            )
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("receipt mismatch", process.stderr)

    def test_source_pin_rejects_changed_predecessor(self):
        self.assertTrue(hasattr(ENGINE, "check_sources"), "pin check not implemented")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "research/prime-power-cyclic-inverse/PROOF.md"
            path.parent.mkdir(parents=True)
            path.write_text("altered kernel\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source pin mismatch"):
                ENGINE.check_sources(root)


if __name__ == "__main__":
    unittest.main()
