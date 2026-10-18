#!/usr/bin/env python3
"""Independent envelope probes and public CLI controls. Apache-2.0."""

import importlib.util
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location("entry_contract", HERE / "verify.py")
V = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = V
SPEC.loader.exec_module(V)


def scalar_producer(r, x, y, routed):
    """Integer common grid 1/64; independent equations, not Envelope arithmetic."""
    owners = len(x[0])

    def route(row, stage, port):
        if not routed or stage == 0:
            return row[:]
        permutation = list(range(owners))
        first = port % owners
        second = (first + stage) % owners
        permutation[first], permutation[second] = permutation[second], permutation[first]
        return [row[j] for j in permutation]

    def q(bank, subset, stage):
        return [[sum(int(r[j][p]) * route(bank[p], stage, p)[o] for p in subset)
                 for o in range(owners)] for j in range(8)]

    def inj(query, subset, stage):
        output = [[0] * owners for _ in range(112)]
        for p in subset:
            numerator = [sum(int(r[j][p]) * query[j][o] for j in range(8))
                         for o in range(owners)]
            if any(value % 4 for value in numerator):
                raise ValueError("inexact oracle quarter")
            output[p] = route([value // 4 for value in numerator], stage, p)
        return output

    f = q(x, range(112), 0)
    old = inj(q(x, V.T, 0), V.A, 0)
    kf = inj(f, V.U + V.T, 0)
    x1 = [[x[p][o] - kf[p][o] if p in V.U else old[p][o] if p in V.A
           else kf[p][o] for o in range(owners)] for p in range(112)]
    y1 = [[y[p][o] + x1[p][o] if p in V.U else x[p][o] + y[p][o] - x1[p][o]
           for o in range(owners)] for p in range(112)]
    future = inj(q(y1, V.U + V.T, 2), V.A, 2)
    u = [[y1[p][o] + future[p][o] for o in range(owners)] for p in range(112)]
    a, b = q(x1, V.T, 1), q(u, range(112), 1)
    ia, ib = inj(a, V.U + V.T, 1), inj(b, V.T, 1)
    y2 = [[y1[p][o] + ia[p][o] if p in V.U else u[p][o] if p in V.A
           else u[p][o] - ib[p][o] - 11 * ia[p][o] for o in range(owners)]
          for p in range(112)]
    x2 = [[x1[p][o] - y1[p][o] if p in V.U
           else x1[p][o] + y1[p][o] - y2[p][o] for o in range(owners)]
          for p in range(112)]
    return {"x1": x1, "y1": y1, "u": u, "a": a, "b": b, "x2": x2, "y2": y2}


class EntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r, cls.k = V.geometry(V.sources())
        cls.envelopes = V.producer(cls.r, cls.k)

    def check_fixture(self, x, y, routed, height):
        actual = scalar_producer(self.r, x, y, routed)
        for name, rows in actual.items():
            for values, bound in zip(rows, self.envelopes[name], strict=True):
                for value in values:
                    self.assertLessEqual(abs(value), 64 * height * bound.norm)
                    self.assertEqual(value % (1 << (6 - bound.debt)), 0)
        for p in V.U:
            self.assertEqual(actual["x2"][p], [-value for value in y[p]])
        for p in V.A + V.T:
            for o in range(len(x[0])):
                self.assertEqual(actual["x2"][p][o] + actual["y2"][p][o], x[p][o] + y[p][o])

    def test_basis_and_noncommuting_owner_fixtures(self):
        for source in range(224):
            fields = [[0] for _ in range(224)]
            fields[source][0] = 64
            self.check_fixture(fields[:112], fields[112:], False, 1)
        rng = random.Random(19692707)
        for _ in range(16):
            fields = [[64 * rng.randrange(-3, 4) for _ in range(4)] for _ in range(224)]
            self.check_fixture(fields[:112], fields[112:], True, 3)

    def test_gaussian_product_denominators(self):
        # Each kernel coefficient is a product of (1+i)/2 or (1-i)/2.
        for length in range(73):
            worst = 0
            for negatives in range(length + 1):
                real, imag = 1, 0
                for j in range(length):
                    sign = -1 if j < negatives else 1
                    real, imag = real - sign * imag, imag + sign * real
                for numerator in (real, imag):
                    value = Fraction(numerator, 1 << length)
                    worst = max(worst, value.denominator.bit_length() - 1)
            self.assertEqual(worst, (length + 1) // 2)

    def test_format_and_error_conversion(self):
        self.assertEqual(V.format_parameters(1, 64, 0, 64),
                         {"Q0": 80, "B_over_H": 17628, "decoder_b": 79,
                          "E": 15, "k": 137, "Qmax": 497, "W": 532})
        self.assertLess(Fraction(17628, 1 << 15), 1)
        self.assertGreater(Fraction(17628, 1 << 14), 1)
        for arguments in ((0, 0, 0, 0), (True, 0, 0, 0), (1, -1, 0, 0),
                          (4097, 0, 0, 0), (1, 0, 0, 1.5)):
            with self.assertRaisesRegex(ValueError, "domain|positive"):
                V.format_parameters(*arguments)
        self.assertEqual(V.mix((Fraction(1, 4), -11),
                               (V.Envelope(Fraction(3), 4), V.Envelope(Fraction(2), 0))),
                         V.Envelope(Fraction(91, 4), 6))
        quarter_fixture = Fraction(3, 64) + 22
        self.assertEqual((quarter_fixture * 64).denominator, 1)
        self.assertEqual((quarter_fixture * 32).denominator, 2)
        with self.assertRaisesRegex(ValueError, "non-dyadic"):
            V.mix((Fraction(1, 3),), (V.Envelope(Fraction(1), 0),))
        packet = V.sources()
        packet["R_rows"][0]["0"] = "2"
        with self.assertRaisesRegex(ValueError, "R alphabet"):
            V.geometry(packet)

    def run_cli(self, root, *arguments):
        package = root / "research/qq16-producer-entry-contract"
        environment = dict(os.environ, PYTHONPYCACHEPREFIX=str(root / ".cache"))
        return subprocess.run([sys.executable, "-Werror", "-I", "-O", "-B",
                               str(package / "verify.py"), *arguments], cwd=root,
                              env=environment, capture_output=True, text=True, timeout=60)

    def test_export_source_receipt_and_cli_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "research/qq16-producer-entry-contract"
            package.mkdir(parents=True)
            for name in ("verify.py", "SOURCES.json", "RESULT.json"):
                shutil.copyfile(HERE / name, package / name)
            for name in V.INPUTS:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            outcome = self.run_cli(root)
            self.assertEqual(outcome.returncode, 0, outcome.stderr)
            self.assertIn("PASS_QQ16_PRODUCER_ENTRY_CONTRACT", outcome.stdout)
            original = (package / "RESULT.json").read_bytes()
            boolean_receipt = json.loads(original)
            boolean_receipt["rows"]["x2"][V.U[0]]["fractional_debt"] = False
            for replacement in (json.dumps(boolean_receipt).encode(),
                                b'{"status":true}', b'{"x":1,"x":2}', b" " * 131073):
                (package / "RESULT.json").write_bytes(replacement)
                outcome = self.run_cli(root)
                self.assertNotEqual(outcome.returncode, 0)
                self.assertIn("FAIL_QQ16_PRODUCER_ENTRY_CONTRACT", outcome.stderr)
            (package / "RESULT.json").write_bytes(original)
            for arguments in (("--write",), ("--unknown",)):
                self.assertNotEqual(self.run_cli(root, *arguments).returncode, 0)
            source = root / V.INPUTS[0]
            source.write_bytes(source.read_bytes() + b"drift")
            outcome = self.run_cli(root)
            self.assertNotEqual(outcome.returncode, 0)
            self.assertIn("source hash", outcome.stderr)

    def test_exclusive_recreation_is_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "research/qq16-producer-entry-contract"
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__", "RESULT.json"))
            for name in V.INPUTS:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            outcome = self.run_cli(root, "--write")
            self.assertEqual(outcome.returncode, 0, outcome.stderr)
            self.assertEqual((package / "RESULT.json").read_bytes(), (HERE / "RESULT.json").read_bytes())
            self.assertEqual(self.run_cli(root).returncode, 0)


if __name__ == "__main__":
    unittest.main()
