"""Decisive finite controls for the reversible coset interface. Apache-2.0."""

import itertools
from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


def load(path):
    namespace = {"__file__": str(path), "__name__": path.stem}
    exec(compile(path.read_bytes(), str(path), "exec"), namespace)
    return namespace


VERIFY = load(ROOT / "verify.py")
Reducer = load(ROOT / "reducer.py")["Reducer"]


class Controls(unittest.TestCase):
    def test_all_small_triangular_cases(self):
        matrices = vectors = 0
        for q, d in itertools.product((2, 4), range(1, 4)):
            diagonals = [1 << k for k in range(q.bit_length())]
            slots = [(i, j) for i in range(d) for j in range(i+1, d)]
            for diagonal in itertools.product(diagonals, repeat=d):
                ranges = [range(diagonal[i]) for i, _ in slots]
                for coefficients in itertools.product(*ranges):
                    rows = [[diagonal[i]*int(i == j) for j in range(d)] for i in range(d)]
                    for (i, j), c in zip(slots, coefficients, strict=True):
                        rows[i][j] = c
                    try:
                        r = Reducer(rows, q)
                    except ValueError as error:
                        self.assertIn("qZ^d", str(error))
                        continue
                    matrices += 1
                    for value in itertools.product(range(q), repeat=d):
                        vectors += 1
                        state = r.apply(list(value))
                        self.assertEqual(r.residues(state), r.ordinary(value))
                        bit_state = r.apply_bits(list(value))
                        self.assertEqual(bit_state, state)
                        self.assertEqual(r.apply(state, inverse=True), list(value))
                        self.assertEqual(r.apply_bits(bit_state, inverse=True), list(value))
        self.assertEqual((matrices, vectors), (170, 8660))

    def test_missing_period_containment(self):
        with self.assertRaisesRegex(ValueError, "qZ"):
            Reducer([[2, 1, 0], [0, 2, 1], [0, 0, 1]], 2)
        # Bypassing only containment gives s=(0,1,0). H z=t-s has nonintegral z0.
        z2 = 1
        z1 = Fraction(-1-z2, 2)
        z0 = Fraction(-z1, 2)
        self.assertEqual((z0, z1, z2), (Fraction(1, 2), -1, 1))

    def test_elementary_adders(self):
        pairs = 0
        for width in range(1, 5):
            q = 1 << width
            r = Reducer([[q, 1], [0, 1]], q)
            for target, source in itertools.product(range(q), repeat=2):
                pairs += 1
                state = r.apply_bits([target, source])
                self.assertEqual(state, [(target-source) % q, source])
                self.assertEqual(r.apply_bits(state, inverse=True), [target, source])
        self.assertEqual(pairs, 340)
        # Exercise the reference's larger clean conjunction chains as well.
        for width in range(5, 9):
            q = 1 << width
            r = Reducer([[q, 1], [0, 1]], q)
            for target, source in ((q-1, q-1), (0, q-1), (q//2, q//2+1)):
                self.assertEqual(r.apply_bits([target, source]), [(target-source) % q, source])

    def test_quotient_erasure_and_inverse_order(self):
        r = Reducer([[1]], 2)
        states = [r.apply([x]) for x in (0, 1)]
        self.assertNotEqual(states[0], states[1])
        self.assertEqual(r.residues(states[0]), r.residues(states[1]))
        r = Reducer([[2, 1, 0], [0, 2, 1], [0, 0, 1]], 4)
        state = r.apply([0, 0, 1])
        broken = list(state)
        for source, target, shift, exponent in r.ops:  # Wrong chronology.
            broken[target] = (broken[target] + ((broken[source] >> exponent) << shift)) % 4
        self.assertNotEqual(broken, [0, 0, 1])
        self.assertEqual(r.apply(state, inverse=True), [0, 0, 1])

    def test_rank_seven_literal_gates_and_dirty_target(self):
        rows, _ = VERIFY["sources"]()
        r = Reducer(rows, 16)
        for value in ([15]*256, [i % 16 for i in range(256)], [-i*i for i in range(256)]):
            original = list(value)
            target = (1 << 343)-1
            work = [0]*256
            a = r.oracle(value, target, work)
            b = r.oracle(value, target, work, bit_gates=True)
            self.assertEqual(a, b)
            self.assertEqual(r.oracle(value, b, work, bit_gates=True), target)
            self.assertEqual(value, original)
            self.assertEqual(work, [0]*256)
        state = r.apply([15]*256)
        broken = Reducer(rows, 16)
        broken.ops = broken.ops[1:]
        self.assertNotEqual(broken.apply_bits([15]*256), state)

    def test_clean_workspace_and_invalid_model(self):
        r = Reducer([[1]], 2)
        with self.assertRaisesRegex(ValueError, "clean work"):
            r.oracle([1], 0, [1])
        with self.assertRaisesRegex(ValueError, "alias"):
            value = [0]
            r.oracle(value, 0, value)
        for rows, q in (([[1]], 3), ([[2]], 1), ([[1, 0], [1, 1]], 2)):
            with self.assertRaises(ValueError):
                Reducer(rows, q)

    def test_source_and_typed_receipt_controls(self):
        with tempfile.TemporaryDirectory(prefix="p104-modular-controls-") as tmp:
            copy = Path(tmp)/"package"
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns("__pycache__"))
            source = copy/"vendor"/"lattice.py"
            source.write_bytes(source.read_bytes()+b"\n# changed\n")
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(copy/"verify.py")],
                                    capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("predecessor bytes", result.stderr)
            shutil.copyfile(ROOT/"vendor"/"lattice.py", source)
            receipt = copy/"RESULT.json"
            data = json.loads(receipt.read_text())
            data["no_new_kappa"] = 1  # Equality alone confuses bool and int.
            receipt.write_text(json.dumps(data))
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(copy/"verify.py")],
                                    capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("typed exact receipt", result.stderr)

    def test_read_only_git_free_export(self):
        with tempfile.TemporaryDirectory(prefix="p104-modular-export-") as tmp:
            copy = Path(tmp)/"package"
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns("__pycache__"))
            paths = list(copy.rglob("*"))
            try:
                for path in paths:
                    path.chmod(0o555 if path.is_dir() else 0o444)
                copy.chmod(0o555)
                result = subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B",
                                         str(copy/"verify.py")], cwd=tmp,
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("PASS_P104_MODULAR_RESIDUE_REDUCER", result.stdout)
            finally:
                copy.chmod(0o755)
                for path in paths:
                    path.chmod(0o755 if path.is_dir() else 0o644)


if __name__ == "__main__":
    unittest.main()
