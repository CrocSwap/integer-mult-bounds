"""Meaningful corrupted-input, domain, arithmetic and replay failure controls."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify
import independent


class ReconciliationControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = verify.read_json((HERE / "SOURCE-PINS.json").read_bytes())
        cls.blobs, cls.reference = verify.validate_inputs(verify.ROOT, cls.manifest)
        cls.arithmetic = independent.exclusion()

    def test_source_and_input_corruption(self):
        # The historical serializer, upstream selector, original source,
        # reference output and written tail hypothesis must all be bound.
        for path in ("scripts/prepare_layers.py", "upstream/manifest.json",
                     "scripts/experiments/core_limits.py", verify.REFERENCE,
                     "docs/research/core-limits.md"):
            with self.subTest(path=path), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                for relative, data in self.blobs.items():
                    target = root / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                (root / path).write_bytes(self.blobs[path] + b"\nchanged\n")
                with self.assertRaisesRegex(ValueError, "Source hash mismatch"):
                    verify.validate_inputs(root, self.manifest)

    def test_missing_local_pin(self):
        manifest = deepcopy(self.manifest)
        del manifest["files"]["scripts/prepare_layers.py"]
        with self.assertRaisesRegex(ValueError, "Unpinned local"):
            verify.validate_inputs(verify.ROOT, manifest)

    def test_domain_and_arithmetic_corruptions(self):
        def drop(row):
            row["envelope"]["cases"].pop()

        def duplicate(row):
            row["envelope"]["cases"].append(deepcopy(row["envelope"]["cases"][0]))

        def composite(row):
            row["envelope"]["cases"][0]["q"] = 6

        def negative_sign(row):
            row["envelope"]["cases"][0]["positive_deficit"] = True

        def eta(row):
            positive = next(x for x in row["envelope"]["cases"] if x["positive_deficit"])
            positive["eta_upper"] = str(Fraction(positive["eta_upper"]) + 1)

        def floor(row):
            positive = next(x for x in row["envelope"]["cases"] if x["positive_deficit"])
            positive["side_role_floor"] -= 1

        def assembly(row):
            positive = next(x for x in row["envelope"]["cases"] if x["positive_deficit"])
            positive["bit_saving_upper"] = positive["kappa_upper"]

        def target(row):
            row["envelope"]["target"] = "1/33554432"

        def tail(row):
            row["envelope"]["tail_dimension_exclusion"]["W_over_N_lower"] = 8

        def conclusion(row):
            row["envelope"]["all_prime_powers_and_ground_sizes_excluded"] = 1

        def best(row):
            row["envelope"]["best_finite_upper"]["h"] = 30

        for mutation in (drop, duplicate, composite, negative_sign, eta, floor,
                         assembly, target, tail, conclusion, best):
            with self.subTest(mutation=mutation.__name__):
                changed = deepcopy(self.reference)
                mutation(changed)
                with self.assertRaises(ValueError):
                    independent.check_historical(changed, self.arithmetic)

    def test_no_stale_output_false_success(self):
        # A producer that prints a success marker but writes nothing cannot
        # inherit the reference certificate from the staging directory.
        changed = dict(self.blobs)
        changed[verify.ENTRY] = b"print('PASS common-subset prime-power family')\n"
        with self.assertRaises(FileNotFoundError):
            verify.replay(changed)

    def test_duplicate_json_and_type_sensitive_receipts(self):
        with self.assertRaisesRegex(ValueError, "Duplicate JSON"):
            verify.read_json(b'{"claim":true,"claim":false}')
        self.assertNotEqual(verify.canonical({"claim": 1}),
                            verify.canonical({"claim": True}))
        manifest = (HERE / "SOURCE-PINS.json").read_bytes()
        self.assertEqual(verify.canonical(verify.read_json(manifest)),
                         verify.canonical(verify.read_json(manifest.replace(b"\n", b"\r\n"))))

    def test_independent_prime_catalogue_and_tail_boundary(self):
        powers = independent.prime_powers(34)
        self.assertEqual(set(powers), {2, 3, 4, 5, 7, 8, 9, 11, 13, 16,
                                      17, 19, 23, 25, 27, 29, 31, 32})
        self.assertEqual(powers[27], 3)
        self.assertEqual(self.arithmetic["tail_start"], 67)
        self.assertGreater(Fraction(self.arithmetic["previous_tail_kappa_upper"]),
                           independent.TARGET)
        self.assertLess(Fraction(self.arithmetic["tail_kappa_upper"]),
                        independent.TARGET)


if __name__ == "__main__":
    unittest.main(verbosity=2)
