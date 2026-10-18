#!/usr/bin/env python3
"""independent dual-coordinate, determinant, and failure-detection tests.

gojo (@6ojo), with substantial openai codex assistance; apache-2.0.
"""

from copy import deepcopy
import gzip
import importlib.util
from itertools import combinations, permutations, product
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("parity_verifier", HERE / "verify.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)
with gzip.open(ROOT / verifier.WORD, "rt", encoding="utf-8") as source:
    WORD = json.load(source)
EXPECTED = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))


def determinant(matrix):
    result = 0
    for permutation in permutations(range(len(matrix))):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(len(matrix)) for j in range(i + 1, len(matrix)))
        term = -1 if inversions % 2 else 1
        for i, j in enumerate(permutation):
            term *= matrix[i][j]
        result += term
    return result


def binary_basis(rows):
    basis = []
    for row in rows:
        for pivot, previous in basis:
            if row & (1 << pivot):
                row ^= previous
        if row:
            basis.append((row.bit_length() - 1, row))
            basis.sort(reverse=True)
    return basis


def binary_member(row, basis):
    for pivot, previous in basis:
        if row & (1 << pivot):
            row ^= previous
    return row == 0


class ParityTests(unittest.TestCase):
    def test_exterior_coefficients_against_permutations(self):
        vectors = list(product((0, 1), repeat=4))
        matrices = minors = 0
        for degree in range(4):
            for rows in product(vectors, repeat=degree):
                blade = {0: 1}
                for row in rows:
                    blade = verifier.wedge(blade, row)
                for columns in combinations(range(4), degree):
                    mask = sum(1 << j for j in columns)
                    self.assertEqual(blade.get(mask, 0), determinant(
                        [[row[j] for j in columns] for row in rows]))
                    minors += 1
                matrices += 1
        self.assertEqual((matrices, minors), (4369, 17985))
        rng = random.Random(76)
        for degree in range(9):
            rows = [[rng.randrange(-2, 3) for _ in range(8)] for _ in range(degree)]
            blade = {0: 1}
            for row in rows:
                blade = verifier.wedge(blade, row)
            for columns in combinations(range(8), degree):
                self.assertEqual(blade.get(sum(1 << j for j in columns), 0), determinant(
                    [[row[j] for j in columns] for row in rows]))

    def test_dual_encoding_and_all_frame_closures(self):
        # encode a root by its eight integer pairings with the lattice basis.
        # this uses neither inverse coordinates nor exterior products.
        q = EXPECTED["quotient"]
        basis = [WORD["lines"][i] for i in q["basis_label_indices"]]
        dual = [sum(((sum(a * b for a, b in zip(root, row)) // 2) % 2) << j
                    for j, row in enumerate(basis)) for root in WORD["lines"]]
        conversion = {}
        for mask in range(256):
            image = sum((sum(q["gram"][i][j] for i in range(8) if mask & (1 << i)) % 2) << j
                        for j in range(8))
            conversion[image] = mask
        self.assertEqual(len(conversion), 256)
        self.assertEqual([conversion[value] for value in dual], q["root_classes"])
        for frame, expected in zip(WORD["frames"], EXPECTED["frames"]):
            reduced = binary_basis([dual[i] for i in frame])
            self.assertEqual(len(reduced), expected["parity_rank"])
            members = [i for i, value in enumerate(dual) if binary_member(value, reduced)]
            self.assertEqual(format(sum(1 << i for i in members), "030x"),
                             expected["parity_membership_mask_hex"])

    def test_all_480_lifts_in_original_coordinates(self):
        basis = [WORD["lines"][i] for i in EXPECTED["quotient"]["basis_label_indices"]]
        checked = 0
        for record in EXPECTED["frames"]:
            frame = WORD["frames"][record["frame"]]
            for extra in record["extra_roots"]:
                root = WORD["lines"][extra["label"]]
                original_difference = [sum(WORD["lines"][i][j] for i in extra["subset_labels"]) - root[j]
                                       for j in range(8)]
                lift = extra["half_difference_lattice_coordinates"]
                reconstructed = [2 * sum(lift[i] * basis[i][j] for i in range(8)) for j in range(8)]
                self.assertEqual(original_difference, reconstructed)
                # positivity plus orthogonality proves rational nonmembership,
                # independently of the verifier's augmented-minor witness.
                self.assertEqual(sum(x * x for x in root), 4)
                self.assertTrue(all(sum(a * b for a, b in zip(root, WORD["lines"][i])) == 0
                                    for i in frame))
                checked += 1
        self.assertEqual(checked, 480)

    def test_quadratic_form_and_alternate_lifts(self):
        q = EXPECTED["quotient"]
        basis = [WORD["lines"][i] for i in q["basis_label_indices"]]
        self.assertEqual(determinant(basis), -16)
        self.assertEqual(determinant(q["gram"]), 1)
        rng = random.Random(76)
        for mask in range(256):
            # a different representative of every class, including negatives.
            coordinates = [((mask >> i) & 1) + 2 * rng.randrange(-3, 4) for i in range(8)]
            root = [sum(coordinates[i] * basis[i][j] for i in range(8)) for j in range(8)]
            self.assertEqual(sum(x * x for x in root) % 4, 0)
            self.assertEqual((sum(x * x for x in root) // 4) % 2, q["quadratic_values"][mask])
        self.assertEqual(sum(1 if not x else -1 for x in q["quadratic_values"]), 16)
        self.assertEqual(len(set(verifier.residue(row) for row in WORD["lines"])), 15)
        self.assertEqual(len(set(q["root_classes"])), 120)
        self.assertTrue(all(verifier.residue([-x for x in row]) == verifier.residue(row)
                            for row in q["integral_root_coordinates"]))

    def test_coordinate_isometry_basis_guard_and_controls(self):
        changed = deepcopy(WORD)
        # preserve the pinned label order: the seed-nominated basis is checked
        # primitive for this instance, not asserted primitive for every order.
        changed["lines"] = [[-row[0]] + row[1:] for row in WORD["lines"]]
        result = verifier.analyze(changed)
        self.assertEqual(result["frame_census"], EXPECTED["frame_census"])
        self.assertEqual(result["extra_memberships"], 480)
        reordered = deepcopy(WORD)
        reordered["lines"] = list(reversed(WORD["lines"]))
        reordered["frames"] = [sorted(119 - i for i in frame) for frame in WORD["frames"]]
        with self.assertRaisesRegex(verifier.Reject, "root basis has index sixteen"):
            verifier.analyze(reordered)
        result = verifier.analyze(WORD)
        result["negative_controls"] = verifier.rejection_controls(WORD, result)
        self.assertEqual(result, EXPECTED)

    def test_optimized_cli_and_failure_detection(self):
        pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(prefix="r420-parity-test-", dir=ROOT.parent) as temporary:
            root = Path(temporary)
            sources = root / "source with spaces"
            package = root / "standalone package"
            package.mkdir()
            for name in ("verify.py", "SOURCES.json", "EXPECTED.json"):
                shutil.copyfile(HERE / name, package / name)
            for relative in pins["files_sha256"]:
                target = sources / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, target)

            def run(*args):
                return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"),
                                       "--source-root", str(sources), *map(str, args)],
                                      cwd=root, capture_output=True, text=True, timeout=60)

            good = run()
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertIn("480 extra memberships; 11 rejected controls", good.stdout)
            output = root / "fresh.json"
            self.assertEqual(run("--write", output).returncode, 0)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), EXPECTED)
            saved = output.read_bytes()
            self.assertNotEqual(run("--write", output).returncode, 0)
            self.assertEqual(output.read_bytes(), saved)
            bad = deepcopy(EXPECTED)
            bad["frames"][362]["extra_roots"][0]["half_difference_lattice_coordinates"][0] += 1
            output.write_text(json.dumps(bad), encoding="utf-8")
            rejected = run("--expected", output)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("certificate differs", rejected.stderr)
            word_path = sources / verifier.WORD
            word_path.write_bytes(word_path.read_bytes() + b"corruption")
            rejected = run()
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("changed pinned source", rejected.stderr)
            word_path.unlink()
            self.assertIn("missing pinned source", run().stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
