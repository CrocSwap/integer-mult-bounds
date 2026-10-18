"""Exercise witness failures and rank controls with optimization enabled."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import independent
import verify


class WitnessTests(unittest.TestCase):
    def setUp(self):
        self.witness = verify.read_json(verify.PACKAGE / "WITNESS.json")

    def test_literal_witness(self):
        result = verify.check_witness(self.witness)
        self.assertEqual(result["intersection_dimension"], 5)
        self.assertEqual(result["small_supports"], [18, 20, 20, 19, 13])

    def test_separate_geometry(self):
        self.assertEqual(verify.geometry(), independent.lattice_points())

    def test_modular_lower_and_rational_upper_bound(self):
        result = independent.check(self.witness)
        self.assertEqual(result["rational_combined_upper_bound"], 14)
        self.assertEqual(result["small_support_label_ranks"], [8, 8, 8, 9, 7])
        self.assertEqual(result["endpoint_support_label_ranks"], [8, 9, 8, 8, 9, 8])

    def test_changed_endpoint_value(self):
        changed = copy.deepcopy(self.witness)
        changed["endpoints_sparse"][0][0][1] *= -1
        with self.assertRaisesRegex(ValueError, "reconstruction"):
            verify.check_witness(changed)
        with self.assertRaisesRegex(ValueError, "inclusion"):
            independent.check(changed)

    def test_duplicated_endpoint(self):
        changed = copy.deepcopy(self.witness)
        changed["endpoints_sparse"][1] = changed["endpoints_sparse"][0]
        with self.assertRaises(ValueError):
            verify.check_witness(changed)
        with self.assertRaises(ValueError):
            independent.check(changed)

    def test_duplicate_coordinate(self):
        changed = copy.deepcopy(self.witness)
        changed["endpoints_sparse"][0][1] = changed["endpoints_sparse"][0][0]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            verify.check_witness(changed)

    def test_thirty_is_not_this_witness(self):
        changed = copy.deepcopy(self.witness)
        changed["cuts"].pop()
        with self.assertRaisesRegex(ValueError, "cut inventory"):
            verify.check_witness(changed)
        with self.assertRaisesRegex(ValueError, "31 distinct cuts"):
            independent.check(changed)

    def test_cut_replacement_breaks_construction(self):
        changed = copy.deepcopy(self.witness)
        changed["cuts"] = sorted(set(changed["cuts"][1:]) | {1})
        with self.assertRaises(ValueError):
            verify.check_witness(changed)
        with self.assertRaises(ValueError):
            independent.check(changed)

    def test_dependent_directions(self):
        changed = copy.deepcopy(self.witness)
        changed["directions_doubled"][1] = changed["directions_doubled"][0]
        with self.assertRaisesRegex(ValueError, "Gram"):
            verify.check_witness(changed)
        with self.assertRaises(ValueError):
            independent.check(changed)

    def test_rank_exact_and_modular(self):
        rows = ((1, 0, 1), (0, 1, 1), (1, 1, 2))
        self.assertEqual(len(verify.rank_pivots(rows)), 2)
        self.assertEqual(independent.modular_rank(rows), 2)
        self.assertEqual(len(verify.rank_pivots(((101, 0), (0, 1)))), 2)
        self.assertEqual(independent.modular_rank(((101, 0), (0, 1))), 1)

    def test_invalid_integer_boundary(self):
        changed = copy.deepcopy(self.witness)
        changed["endpoints_sparse"][0][0][0] = True
        with self.assertRaisesRegex(ValueError, "entries"):
            verify.check_witness(changed)

    def test_receipt_matches(self):
        actual = json.loads(json.dumps(verify.check_witness(self.witness)))
        self.assertEqual(actual, verify.read_json(verify.PACKAGE / "RESULT.json"))

    def test_source_hash_rejects_tampering(self):
        relative = Path("research/p112-six-vertex-budget/vendor/geometry.py")
        with tempfile.TemporaryDirectory(prefix="support31-source-") as folder:
            path = Path(folder) / relative
            path.parent.mkdir(parents=True)
            path.write_bytes((verify.REPO / relative).read_bytes() + b"\n# changed\n")
            with patch.object(verify, "REPO", Path(folder)):
                with self.assertRaisesRegex(ValueError, "source hash"):
                    verify.bind_sources()

    def test_cli_external_receipt_and_no_overwrite(self):
        command = [
            sys.executable,
            "-S",
            "-W",
            "error",
            "-B",
            str(verify.PACKAGE / "verify.py"),
        ]
        with tempfile.TemporaryDirectory(prefix="support31-cli-") as folder:
            output = Path(folder) / "result.json"
            first = subprocess.run(
                [*command, "--output", str(output)],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            original = output.read_bytes()
            self.assertEqual(
                json.loads(original), verify.read_json(verify.PACKAGE / "RESULT.json")
            )
            second = subprocess.run(
                [*command, "--output", str(output)],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(output.read_bytes(), original)
            inside = verify.PACKAGE / "forbidden-output.json"
            refused = subprocess.run(
                [*command, "--output", str(inside)],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertFalse(inside.exists())


if __name__ == "__main__":
    unittest.main()
