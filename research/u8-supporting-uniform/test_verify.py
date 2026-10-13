"""Mathematical corruption controls and source-model binding checks."""
import ast
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import verify as V


class SupportingCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = V.build_certificate()

    def test_committed_certificate_and_source_pins(self):
        V.source_pins()
        candidate = json.loads((V.HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
        V.check_certificate(candidate, self.expected)

    def test_model_matches_pinned_predecessor_literals(self):
        # Parse literal data only. Never execute the predecessor's code.
        path = V.ROOT / "research/complex-t37-owners/independent/all_t_bound.py"
        literals = {}
        names = {"WIDTHS", "PRICES", "CAPACITIES", "INVENTORY"}
        for node in ast.parse(path.read_text(encoding="utf-8")).body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name) and target.id in names:
                    literals[target.id] = ast.literal_eval(node.value)
        self.assertEqual(literals, {
            "WIDTHS": V.WIDTHS, "PRICES": V.PRICES,
            "CAPACITIES": V.CAPACITIES,
            "INVENTORY": dict(zip(V.WIDTHS, V.HELPERS)),
        })

    def test_cube_floor_across_exact_cube_boundaries(self):
        for k in (0, 1, 2, 3, 10, 48, 10**12, 3634241185664):
            for n in (k**3, k**3 + 1, (k + 1)**3 - 1):
                result = V.cube_floor(n)
                self.assertLessEqual(result**3, n)
                self.assertLess(n, (result + 1)**3)
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            V.cube_floor(-1)

    def test_equality_profile_requires_replicas_divisible_by_37(self):
        # Modular arithmetic proves the all-T statement; these check boundaries
        # and the explicit representative without asserting a finite search proof.
        from fractions import Fraction
        self.assertEqual(Fraction(150, 925), Fraction(6, 37))
        self.assertEqual(48 * 11086 + 6, 14382 * 37)
        self.assertEqual(19 * 6 - 13 * 11086, -3892 * 37)
        for replicas in (1, 8, 21, 36, 37, 38, 74, 10**6):
            self.assertEqual((6 * replicas) % 37 == 0, replicas % 37 == 0)

    def test_false_broadening_to_b_equal_one(self):
        # At b=1, the *unstrengthened* supporting inequality already fails.
        from fractions import Fraction
        rank = 32
        v = next(r["credit"] for r in self.expected["rows"] if r["rank"] == rank)
        self.assertEqual(Fraction(925 * (48 - rank), 47) - v, Fraction(-22800, 47))

    def test_source_mutation_is_rejected(self):
        pins = V.source_pins()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in pins["files"]:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((V.ROOT / relative).read_bytes())
            V.source_pins(root)
            target = root / "research/complex-t21-owner-bound/PROOF.md"
            target.write_bytes(target.read_bytes() + b"\nchanged source\n")
            with self.assertRaisesRegex(ValueError, "source drift"):
                V.source_pins(root)

    def test_mathematical_certificate_mutations(self):
        def row(data, rank):
            return next(item for item in data["rows"] if item["rank"] == rank)

        def omit(data, rank):
            data["rows"] = [item for item in data["rows"] if item["rank"] != rank]

        changes = {
            "wrong_rank_one_price": lambda d: row(d, 1).__setitem__("upper_price", 18),
            "wrong_signed_credit": lambda d: row(d, 38).__setitem__("credit", 2050),
            "omit_worst_rank": lambda d: omit(d, 44),
            "omit_negative_credit_rank": lambda d: omit(d, 38),
            "false_cube_lower": lambda d: row(d, 2)["cube_root_numerators"].__setitem__(
                0, row(d, 2)["cube_root_numerators"][0] + 1),
            "false_denominator_upper": lambda d: d["cube_root_48_numerators"].__setitem__(
                1, d["cube_root_48_numerators"][0]),
            "inflated_margin": lambda d: row(d, 44).__setitem__("scaled_margin_lower", "1000"),
            "wrong_equality_mass": lambda d: d["equality_profile"].__setitem__("rank_48", 11087),
            "unproved_exponent_interval": lambda d: d.__setitem__("exponent_interval", "0 < b <= 1"),
        }
        reasons = {
            "wrong_rank_one_price": "independent price and credit at rank 1",
            "wrong_signed_credit": "independent price and credit at rank 38",
            "omit_worst_rank": "complete ordered unique rows",
            "omit_negative_credit_rank": "complete ordered unique rows",
            "false_cube_lower": "consecutive integer root endpoints",
            "false_denominator_upper": "consecutive integer root endpoints",
            "inflated_margin": "certificate's exact margin at rank 44",
            "wrong_equality_mass": "integer equality profile",
            "unproved_exponent_interval": "exponent scope",
        }
        independent = V.HERE / "independent_check.py"
        self.assertTrue(independent.is_file(), "independent implementation must be present")
        with tempfile.TemporaryDirectory() as directory:
            for name, change in changes.items():
                with self.subTest(control=name):
                    candidate = copy.deepcopy(self.expected)
                    change(candidate)
                    with self.assertRaisesRegex(ValueError, "certificate differs"):
                        V.check_certificate(candidate, self.expected)
                    path = Path(directory) / (name + ".json")
                    path.write_text(json.dumps(candidate), encoding="utf-8")
                    process = subprocess.run(
                        [sys.executable, "-O", "-S", "-B", str(independent),
                         "--certificate", str(path)], capture_output=True, text=True)
                    self.assertNotEqual(process.returncode, 0, name)
                    self.assertIn("ValueError: " + reasons[name], process.stderr, process.stderr)

    def test_optimized_standalone_runs(self):
        for filename in ("verify.py", "independent_check.py"):
            result = subprocess.run(
                [sys.executable, "-O", "-S", "-B", str(V.HERE / filename)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_U8_SUPPORTING_", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
