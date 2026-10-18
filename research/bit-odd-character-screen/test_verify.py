"""Independent direct-character oracles and actual command-line failure controls."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from fractions import Fraction
from itertools import combinations_with_replacement, permutations, product
from pathlib import Path

import verify

HERE = Path(__file__).resolve().parent
ALPHABET = ((1, 0), (0, 1), (1, 1), (1, -1), (2, 0), (3, 0), (0, 3))
TARGETS = ((0, 0), (1, 0), (0, 1), (1, 1), (1, -1), (3, 0), (0, 3))


def direct_patterns(paid, targets, modulus):
    patterns = set()
    for character in product(range(modulus), repeat=2):
        values = tuple(sum(a * b for a, b in zip(character, row, strict=True)) % modulus
                       for row in paid + targets)
        patterns.add(tuple(value != 0 for value in values))
    return patterns


def direct_reject(paid, targets):
    patterns = direct_patterns(paid, targets, 45)
    return any(sum(pattern[:len(paid)]) < sum(pattern[len(paid):])
               for pattern in patterns)


def embedded(paid, targets):
    def matrix(row):
        return [list(row), [0, 0]]
    return {"address_dimension": 2, "paid_frames": [matrix(row) for row in paid],
            "target_frames": [matrix(row) for row in targets]}


def cli(root, *args, optimized=False):
    command = [sys.executable, "-I", "-B"]
    if optimized:
        command.append("-O")
    return subprocess.run([*command, str(root / "verify.py"), *map(str, args)],
                          capture_output=True, text=True, timeout=60, check=False)


def relocate(destination):
    root = destination / "research" / HERE.name
    shutil.copytree(HERE, root, ignore=shutil.ignore_patterns("__pycache__"))
    sources = json.loads((HERE / "SOURCES.json").read_text())
    repo = HERE.parent.parent
    for source in sources["files"]:
        if source["usage"] == "input":
            target = destination / source["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(repo / source["path"], target)
    return root


class ScreenTests(unittest.TestCase):
    def test_determinants_against_leibniz(self):
        for size in range(1, 7):
            for seed in range(24):
                rows = [[((seed + 3) * (i + 2) + (j + 5) ** (i + 1)) % 7 - 3
                         for j in range(size)] for i in range(size)]
                expected = 0
                for perm in permutations(range(size)):
                    inversions = sum(perm[i] > perm[j] for i in range(size)
                                     for j in range(i + 1, size))
                    term = -1 if inversions % 2 else 1
                    for i in range(size):
                        term *= rows[i][perm[i]]
                    expected += term
                self.assertEqual(verify.determinant(rows), expected)

    def test_all_odd_screen_against_direct_characters(self):
        cases = 0
        for extra in combinations_with_replacement(ALPHABET, 2):
            paid = ((1, 0), (0, 1), *extra)
            for targets in combinations_with_replacement(TARGETS, 2):
                result = verify.run_input(embedded(paid, targets))
                self.assertEqual(result["status"] == "REJECT_ODD_CHARACTER_CUT",
                                 direct_reject(paid, targets), (paid, targets, result))
                cases += 1
        self.assertEqual(cases, 784)

    def test_finite_quotient_densities_directly(self):
        cases = 0
        for base in combinations_with_replacement(ALPHABET, 2):
            a, b = base
            if a[0] * b[1] == a[1] * b[0]:
                continue
            for targets in combinations_with_replacement(TARGETS, 2):
                valid = total = 0
                for x, y in product(range(45), repeat=2):
                    if any((x * v[0] + y * v[1]) % 45 for v in base):
                        continue
                    total += 1
                    valid += all((x * v[0] + y * v[1]) % 45 for v in targets)
                self.assertEqual(verify.avoidance_density(base, targets),
                                 Fraction(valid, total), (base, targets))
                cases += 1
        self.assertEqual(cases, 476)

    def test_prime_orders_are_insufficient(self):
        data = verify.read_json(HERE / "EXAMPLE.json")
        paid, targets = verify.parse_frames(data)
        self.assertEqual(sum(row[0] for row in paid), sum(row[0] for row in targets))
        # At primes other than 3 and 5, both paid labels survive. At 3 or 5,
        # exactly one paid label and exactly one target survives.
        for modulus in (2, 3, 5, 7, 11, 13, 17):
            for value in range(modulus):
                self.assertGreaterEqual(sum(value * row[0] % modulus != 0 for row in paid),
                                        sum(value * row[0] % modulus != 0 for row in targets))
        self.assertEqual(verify.avoidance_density(((15,),), targets), Fraction(8, 15))
        self.assertEqual(verify.avoidance_density(((2,),), ((1,),)), 0)
        self.assertEqual(verify.avoidance_density(((6,),), ((1,),)), Fraction(2, 3))
        self.assertEqual(verify.avoidance_density((), ((1,),)), 1)
        self.assertEqual(verify.avoidance_density((), ((0,),)), 0)
        self.assertEqual(verify.finite_index(((2, 0),), ((0, 1),)), None)
        self.assertEqual(verify.avoidance_density(((3, 0), (0, 3)),
                         ((1, 0), (0, 1), (1, 1), (1, -1))), 0)
        impossible = {"address_dimension": 1, "paid_frames": [[[1]], [[1]]],
                      "target_frames": [[[3]]]}
        self.assertEqual(verify.run_input(impossible)["status"],
                         "PASS_ALL_ODD_CHARACTER_CUTS_ONLY")

    def test_membership_fractional_aliases_and_capacity(self):
        data = {"address_dimension": 1, "paid_frames": [[["1/2"]], [["3/2"]]],
                "target_frames": [[["1/2"]]]}
        self.assertEqual(verify.run_input(data)["status"], "PASS_ALL_ODD_CHARACTER_CUTS_ONLY")
        data["target_frames"] = [[["1/4"]]]
        self.assertEqual(verify.run_input(data)["status"],
                         "REJECT_TARGET_OUTSIDE_GENERATED_LATTICE")
        data["paid_frames"] = []
        data["target_frames"] = [[[0]]]
        self.assertEqual(verify.run_input(data)["status"], "PASS_ALL_ODD_CHARACTER_CUTS_ONLY")
        self.assertEqual(verify.run_input(verify.direct_fixture())["paid_subsets_checked"], 46)
        large = {"address_dimension": 1, "paid_frames": [[[65535]]] * 9,
                 "target_frames": [[[65535]]] * 3}
        self.assertEqual(verify.run_input(large)["status"], "PASS_ALL_ODD_CHARACTER_CUTS_ONLY")
        zeros = {"address_dimension": 3, "paid_frames": [],
                 "target_frames": [[[0] * 3 for _ in range(3)]] * 3}
        self.assertEqual(verify.run_input(zeros)["status"], "PASS_ALL_ODD_CHARACTER_CUTS_ONLY")

    def test_malformed_inputs(self):
        original = verify.read_json(HERE / "EXAMPLE.json")
        changes = [("address_dimension", True), ("address_dimension", 0),
                   ("address_dimension", 4), ("paid_frames", [ [[0]] ]),
                   ("paid_frames", [[[1.0]]]), ("paid_frames", [[[True]]]),
                   ("paid_frames", [[["1/0"]]]), ("paid_frames", [[["1e1"]]]),
                   ("paid_frames", [[["1/65536"]]]), ("paid_frames", [[[65536]]]),
                   ("paid_frames", [[[1]]] * 10), ("paid_frames", [[[1, 2]]]),
                   ("target_frames", []), ("target_frames", [[[1]]] * 4)]
        for key, value in changes:
            data = deepcopy(original)
            data[key] = value
            with self.assertRaises(ValueError, msg=str((key, value))):
                verify.run_input(data)
        with self.assertRaises(ValueError):
            verify.run_input(dict(original, extra=1))
        with self.assertRaises(ValueError):
            verify.run_input({"address_dimension": 2, "paid_frames": [[[1, 0], [0, 1]]],
                              "target_frames": [[[1, 0], [0, 1]]]})
        with self.assertRaises(ValueError):
            json.loads('{"a":1,"a":2}', object_pairs_hook=verify.unique_object)

    def test_real_cli_relocation_and_failures(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = relocate(Path(temporary))
            before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            for optimized in (False, True):
                result = cli(root, optimized=optimized)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("PASS_ODD_CHARACTER_SCREEN", result.stdout)
            self.assertEqual(before, {p: p.read_bytes() for p in root.rglob("*") if p.is_file()})
            result = cli(root, "--input", root / "EXAMPLE.json")
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(json.loads(result.stdout)["avoidance_density"], "8/15")
            positive = root / "positive.json"
            positive.write_text(json.dumps(verify.direct_fixture()))
            self.assertEqual(cli(root, "--input", positive).returncode, 0)
            self.assertEqual(cli(root, "--input", root / "missing").returncode, 2)
            positive.write_bytes(b"x" * 65537)
            self.assertEqual(cli(root, "--input", positive).returncode, 2)
            self.assertEqual(cli(root, "--input", positive, "--write").returncode, 2)
            receipt = root / "RESULT.json"
            receipt.write_text(receipt.read_text().replace('"8/15"', '"1/2"'))
            self.assertNotEqual(cli(root).returncode, 0)
            sources = json.loads((root / "SOURCES.json").read_text())
            live = next(row for row in sources["files"] if row["usage"] == "input")
            external = Path(temporary) / live["path"]
            external.write_bytes(external.read_bytes() + b"\ncorrupted\n")
            source_failure = cli(root)
            self.assertEqual(source_failure.returncode, 2)
            self.assertIn("source digest mismatch", source_failure.stderr)

    def test_actual_algorithm_mutants(self):
        mutants = (("return value // (value & -value)", "return value"),
                   ("if index is None:\n        return Fraction(0)",
                    "if index is None:\n        return Fraction(1)"),
                   ("sign = -1 if mask.bit_count() % 2 else 1", "sign = 1"),
                   ("if survivors >= len(targets):", "if True:"))
        for old, new in mutants:
            with tempfile.TemporaryDirectory() as temporary:
                root = relocate(Path(temporary))
                path = root / "verify.py"
                source = path.read_text()
                self.assertEqual(source.count(old), 1)
                path.write_text(source.replace(old, new))
                # Actual executable mutant, not a corrupted expected receipt.
                result = cli(root)
                self.assertNotEqual(result.returncode, 0, old)
                self.assertNotIn("result receipt mismatch", result.stderr, old)


if __name__ == "__main__":
    unittest.main()
