"""Mathematical controls and portable package admission (stdlib unittest)."""
from collections import deque
from fractions import Fraction as Q
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import search
import verify


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.small = search.ball(2)

    def test_independent_dense_complete_gl2(self):
        # A separate flat-matrix implementation, no row lookup or generator list.
        identity = (1, 0, 0, 1)
        found, queue = {identity: 0}, deque([identity])
        while queue:
            state = queue.popleft()
            for t in (0, 1):
                for kind in ("neg", "plus", "minus"):
                    other = list(state)
                    for c in (0, 1):
                        a, b = state[2 * t + c], state[2 * (1 - t) + c]
                        other[2 * t + c] = (-a if kind == "neg" else a + b if kind == "plus" else a - b) % 3
                    other = tuple(other)
                    if other not in found:
                        found[other] = found[state] + 1
                        queue.append(other)
        decoded = {(m[0] % 3, m[0] // 3, m[1] % 3, m[1] // 3): d for m, d in self.small.items()}
        self.assertEqual(found, decoded)
        self.assertEqual(len(found), (9 - 1) * (9 - 3))

    def test_meeting_against_direct_distance_all_gl2(self):
        # Independent dense matrix products check every ordered ball pair.
        target = (0, 1, 1, 0)
        best = 100
        for a, da in self.small.items():
            for b, db in self.small.items():
                flat_a = [a[0] % 3, a[0] // 3, a[1] % 3, a[1] // 3]
                flat_b = [b[0] % 3, b[0] // 3, b[1] % 3, b[1] // 3]
                product = tuple(sum(flat_a[2 * r + k] * flat_b[2 * k + c] for k in (0, 1)) % 3
                                for r in (0, 1) for c in (0, 1))
                if product == target:
                    best = min(best, da + db)
        self.assertEqual(best, 4)
        self.assertEqual(search.meeting(self.small, (1, 0))[0], best)

    def test_all_generator_inverses_and_quotient_halving(self):
        for n in (2, 3, 5):
            self.assertEqual(len(set(search.generators(n))), n * (2 * n - 1))
            for t, s, sign in search.generators(n):
                if t != s:
                    self.assertIn((t, s, -sign), search.generators(n))
            plus, minus = search.row_tables(n)
            for row in range(3 ** n):
                self.assertEqual(plus[row][minus[0][row]], 0)
                self.assertEqual(minus[0][minus[0][row]], row)
        for numerator in range(-24, 25):
            for power in range(9):
                value = Q(numerator, 2 ** power)
                residue = (value.numerator * pow(value.denominator, -1, 3)) % 3
                half = value / 2
                self.assertEqual((half.numerator * pow(half.denominator, -1, 3)) % 3, 2 * residue % 3)
        with self.assertRaises(ValueError):
            pow(2, -1, 2)  # F2 cannot soundly admit the HALVE primitive.

    def test_omitted_generator_or_wrong_ball_depth(self):
        wrong = search.ball(2, ops=[op for op in search.generators(2) if op[0] != op[1]])
        self.assertNotEqual(search.ball_bytes(wrong), search.ball_bytes(self.small))
        self.assertEqual(len(wrong), 24)  # Determinant-one subgroup misses the swap.
        self.assertNotEqual(search.ball_bytes(search.ball(2, 3)), search.ball_bytes(self.small))
        changed = dict(self.small)
        changed[(1, 3)] = 1
        self.assertNotEqual(search.ball_bytes(changed), search.ball_bytes(self.small))

    def test_modular_existence_is_not_exact_existence(self):
        rows, _ = verify.exact_matrix(2, [("add", 0, 1)] * 3)
        self.assertNotEqual(rows, [[1, 0], [0, 1]])
        self.assertEqual([[int(x) % 3 for x in row] for row in rows], [[1, 0], [0, 1]])

    def test_exact_witnesses_and_all_primitive_omissions(self):
        result, count = verify.witnesses()
        self.assertEqual(count, 37)
        self.assertEqual([result[str(n)]["without_cost"] for n in (2, 3, 5)], [4, 6, 10])
        self.assertEqual([result[str(n)]["with_cost"] for n in (2, 3, 5)], [4, 5, 8])

    def test_permutation_direction_and_invalid_targets(self):
        matrix = (1, 3, 9)
        p = (1, 2, 0)
        self.assertEqual(search.right_permute(matrix, p), (3, 9, 1))
        self.assertEqual(search.right_permute(search.right_permute(matrix, p), (2, 0, 1)), matrix)
        with self.assertRaises(ValueError):
            search.right_permute(matrix, (0, 0, 2))
        for dimension in (0, 1, 4, 6):
            with self.assertRaises(ValueError):
                search.ball(dimension)
        with self.assertRaises(ValueError):
            search.ball(2, 5)

    def test_census_barriers_signs_and_omissions(self):
        a, b = ["L", 0], ["L", 1]
        ops = [["add", a, b, 1, 1], ["add", b, a, -1, 1],
               ["add", a, b, 1, 1], ["scale", b, -1, 1]]
        events = [["scalar", op, 24] for op in ops]
        self.assertEqual(len(verify.boundary_census(events)), 1)
        for position in range(4):
            self.assertEqual(verify.boundary_census(events[:position] + events[position + 1:]), [])
        frame_bad = json.loads(json.dumps(events)); frame_bad[2][2] = 25
        self.assertEqual(verify.boundary_census(frame_bad), [])
        sign_bad = json.loads(json.dumps(events)); sign_bad[1][1][3] = 1
        self.assertEqual(verify.boundary_census(sign_bad), [])
        for position in range(1, 4):
            self.assertEqual(verify.boundary_census(events[:position] + [["phase", "barrier"]] + events[position:]), [])

    def test_manifest_is_complete_and_sources_reject_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in verify.INPUTS:
                path = root / name; path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.ROOT / name, path)
            verify.admit_sources(root)
            for name in verify.INPUTS:
                path = root / name
                good = path.read_bytes()
                path.write_bytes(good + b"\n")
                with self.assertRaisesRegex(ValueError, "source SHA256"):
                    verify.admit_sources(root)
                path.write_bytes(good)

    def test_minimal_offline_relocation_and_receipt_corruption(self):
        with tempfile.TemporaryDirectory(prefix="boundary replay with spaces ") as directory:
            root = Path(directory)
            target = root / "research/complex-scratch-free-boundaries"
            shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__"))
            for name in verify.INPUTS:
                path = root / name; path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.ROOT / name, path)
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            command = [sys.executable, "-I", "-O", "-B", str(target / "verify.py")]
            passed = subprocess.run(command, cwd=directory, capture_output=True, text=True)
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
            self.assertIn("boundaries=168 states=509157", passed.stdout)
            self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()})
            receipt = target / "EXPECTED.json"
            broken = json.loads(receipt.read_text())
            broken["finite_search"]["5"]["lower_bound"] = 8
            receipt.write_text(json.dumps(broken))
            rejected = subprocess.run(command, cwd=directory, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("complete receipt mismatch", rejected.stderr)


if __name__ == "__main__":
    unittest.main()
