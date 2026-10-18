#!/usr/bin/env python3
"""Independent matrix oracle and package rejection tests. Apache-2.0.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
Matrix entries are bits. Payload entries are bitsets of ALL input basis
coordinates, so each replay evaluates every dirty basis input simultaneously.
This oracle imports the emitted word, not the symbolic interpreter semantics.
Finite matrix checks support the implementation; they are not the universal
free-algebra argument or a six-source optimality proof.
"""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("connector_verifier", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def xor_vectors(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def dense_initial(rows, dimension):
    return {row: tuple(1 << (index * dimension + k) for k in range(dimension))
            for index, row in enumerate(rows)}


def apply_matrix(matrix, vector):
    out = []
    for coefficients in matrix:
        entry = 0
        for column, value in enumerate(vector):
            if coefficients & (1 << column):
                entry ^= value
        out.append(entry)
    return tuple(out)


def dense_program(program, rows, matrices, dimension):
    state = dense_initial(rows, dimension)
    for symbol, source, target in program:
        state[target] = xor_vectors(state[target], apply_matrix(matrices[symbol], state[source]))
    return state


def dense_expected(rows, factors, matrices, dimension):
    state = dense_initial(rows, dimension)
    for mask in range(1, 64):
        for source in range(6):
            if mask & (1 << source):
                value = state[f"x{source}"]
                for symbol in factors[f"B{source}"] + factors[f"A{mask}"]:
                    value = apply_matrix(matrices[symbol], value)
                state[f"y{mask}"] = xor_vectors(state[f"y{mask}"], value)
    return state


def substitute_polynomials(polynomials, rows, matrices, dimension):
    basis = dense_initial(rows, dimension)
    state = {}
    for row, terms in polynomials.items():
        total = (0,) * dimension
        for term in terms:
            value = basis[term[-1][1:]]
            for symbol in reversed(term[:-1]):
                value = apply_matrix(matrices[symbol], value)
            total = xor_vectors(total, value)
        state[row] = total
    return state


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = v.load_fixture(HERE)
        cls.factors = v.factor_bank(cls.fixture)
        cls.chunks = v.lower_batch(cls.fixture["root_ops"], cls.factors)
        cls.program = [g for chunk in cls.chunks for g in chunk]

    def test_dense_all_dirty_basis_inputs(self):
        rows = v.DATA_ROWS + v.SCRATCH
        rng = random.Random(79)
        symbols = sorted({g[0] for g in self.program})
        for dimension in (2, 3, 7):
            with self.subTest(dimension=dimension):
                matrices = {symbol: tuple(rng.randrange(1 << dimension) for _ in range(dimension))
                            for symbol in symbols}
                # Explicit singular/noncommuting operators as well as the seeded bank.
                matrices["B0.f0"] = tuple(1 << ((i + 1) % dimension) for i in range(dimension))
                matrices["B0.f7"] = (1,) + (0,) * (dimension - 1)
                wanted = dense_expected(rows, self.factors, matrices, dimension)
                for program in (self.program, self.program[::-1]):
                    actual = dense_program(program, rows, matrices, dimension)
                    self.assertEqual(actual, wanted)
                    symbolic = v.run(program, rows)
                    self.assertEqual(actual, substitute_polynomials(symbolic, rows, matrices, dimension))

    def test_free_words_do_not_commute(self):
        rows = ("x", "w", "y")
        word = [("B", "x", "w"), ("A", "w", "y")]
        polynomial = v.run(word, rows)
        self.assertIn(("A", "B", "@x"), polynomial["y"])
        self.assertNotIn(("B", "A", "@x"), polynomial["y"])
        matrices = {"A": (2, 1), "B": (1, 0)}
        actual = dense_program(word, rows, matrices, 2)
        self.assertEqual(actual, substitute_polynomials(polynomial, rows, matrices, 2))
        bad = deepcopy(polynomial)
        bad["y"].remove(("A", "B", "@x"))
        bad["y"].add(("B", "A", "@x"))
        self.assertNotEqual(actual, substitute_polynomials(bad, rows, matrices, 2))

    def test_output_only_checks_miss_two_restoration_faults(self):
        controls = v.negative_controls(self.fixture["root_ops"], self.factors, self.chunks)
        self.assertEqual(controls["omit_final_source_restoration"]["wrong_rows"], ["z"])
        self.assertEqual(controls["omit_recursive_cleanup_leaf"]["wrong_rows"], ["s2"])
        self.assertEqual(len(controls), 10)

    def test_source_and_fixture_corruption_rejected(self):
        mutations = [
            ("reference bytes", "references/PR1185-verify.py", None),
            ("source head", "SOURCES.json", lambda j: j["references"][0].update(commit="0" * 40)),
            ("missing reference", "SOURCES.json", lambda j: j["references"].pop()),
            ("changed root", "FIXTURE.json", lambda j: j["root_ops"][0].__setitem__(1, 1)),
            ("omitted query", "FIXTURE.json", lambda j: j["root_ops"].pop()),
            ("collapsed source product", "FIXTURE.json", lambda j: j["source_factor_lengths"].__setitem__(0, 1)),
            ("collapsed output product", "FIXTURE.json", lambda j: j["output_factor_lengths"].__setitem__(0, 1)),
            ("boolean operator index", "FIXTURE.json", lambda j: j["root_ops"][0].__setitem__(1, False)),
        ]
        for name, relative, mutate in mutations:
            with self.subTest(control=name), tempfile.TemporaryDirectory() as temporary:
                package = Path(temporary) / "copy"
                shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
                path = package / relative
                if mutate is None:
                    path.write_bytes(path.read_bytes() + b"\n# corruption\n")
                else:
                    data = json.loads(path.read_text())
                    mutate(data)
                    path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    v.compute(package)

    def test_relocated_optimized_replay_and_expected_corruption(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / "arbitrary location"
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
            good = subprocess.run(command, cwd=temporary, capture_output=True, text=True, timeout=30)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertIn("queries=142 leaves=3832 rows=73 boundaries=284 controls=10", good.stdout)
            receipt = json.loads((package / "EXPECTED.json").read_text())
            receipt["expanded"]["primitive_calls"] -= 1
            (package / "EXPECTED.json").write_text(json.dumps(receipt))
            bad = subprocess.run(command, cwd=temporary, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("EXPECTED.json differs", bad.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
