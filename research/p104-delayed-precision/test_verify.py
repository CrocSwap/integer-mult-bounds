#!/usr/bin/env python3
"""Behavior controls and separate Fraction checks for the completed-word bound."""
from fractions import Fraction as Q
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_delayed_precision", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = V
spec.loader.exec_module(V)
I = V.Instruction


class PrecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = V.load_word()
        cls.program = V.normalize(cls.word)
        cls.result = V.analyze(cls.program)

    def test_signed_cancellation_and_all_cut_coverage(self):
        program = [I("add", 0, 1, Q(1)), I("add", 0, 1, Q(-1))]
        result = V.analyze(program, roles=2)
        self.assertEqual([p[0] for p in result["peaks"]], [Q(2), Q(2), Q(4)])
        self.assertEqual(result["inputs"][0].coefficients(), {0: Q(1)})
        self.assertEqual(result["errors"][0].coefficients(), {0: Q(1), 1: Q(1)})
        V.check_peaks(program, result)

    def test_fraction_oracle_for_dyadic_row_updates(self):
        weights = (2, 3, 5)
        rows = [V.DyadicRow(weights, i) for i in range(3)]
        dense = [{i: Q(1)} for i in range(3)]
        operations = [(0, 1, Q(-1, 65536)), (0, 2, Q(3, 2)),
                      (2, 0, Q(65536)), (1, 2, Q(-8)), (0, 1, Q(1, 2)),
                      (0, 1, Q(-1, 2)), (2, 1, Q(1, 8))]
        # Initial input weights are intentionally nonzero in this arithmetic test.
        for i, row in enumerate(rows):
            row.weighted = weights[i]
        for dst, src, q in operations:
            rows[dst].add_scaled(rows[src], q)
            for j, value in tuple(dense[src].items()):
                dense[dst][j] = dense[dst].get(j, Q(0)) + q * value
                if not dense[dst][j]:
                    del dense[dst][j]
            self.assertEqual(rows[dst].coefficients(), dense[dst])
            self.assertEqual(Q(rows[dst].absolute, 1 << rows[dst].exponent),
                             sum(map(abs, dense[dst].values())))
            self.assertEqual(Q(rows[dst].weighted, 1 << rows[dst].exponent),
                             sum(abs(q) * weights[j] for j, q in dense[dst].items()))
        rows[0].scale(Q(-1, 65536))
        self.assertEqual(rows[0].coefficients(), {j: -q / 65536 for j, q in dense[0].items()})

    def test_reset_does_not_erase_propagated_private_error(self):
        program = [I("reset", 1), I("add", 1, 0, Q(1)),
                   I("add", 0, 1, Q(1)), I("reset", 1)]
        result = V.analyze(program, roles=2)
        self.assertEqual(result["errors"][1].coefficients(), {})
        self.assertEqual(result["errors"][0].coefficients(), {1: Q(1), 2: Q(1)})
        self.assertEqual(V.injected(program, 3, 0, defects={1: Q(1)}, roles=2), Q(1))

    def test_completed_word_sharp_peaks_and_endpoint_sensitivities(self):
        self.assertEqual([p[:3] for p in self.result["peaks"]],
                         [(Q(131072), 33373, 93), (Q(1394705), 33373, 93),
                          (Q(2134050), 33373, 93)])
        V.endpoint_check(self.result, self.word["live_ports"])
        V.check_peaks(self.program, self.result)
        for target in (93, 112, 86, 224, 712, 732, 704):
            inputs, errors = V.adjoint(self.program, len(self.program) - 1, target)
            self.assertEqual(inputs, self.result["inputs"][target].coefficients())
            self.assertEqual(errors, self.result["errors"][target].coefficients())
        self.assertEqual(V.injected(self.program, 33373, 93, defects={7691: Q(1)}), Q(-65536))
        self.assertEqual(V.injected(self.program, len(self.program)-1, 112,
                                    defects={22003: Q(1)}), Q(1))
        self.assertEqual(V.injected(self.program, len(self.program)-1, 704,
                                    defects={22003: Q(1)}), Q(0))

    def test_state_relative_guard_is_sufficient_not_a_precision_minimum(self):
        P, K = Q(131072), Q(2134050)
        self.assertEqual(V.guard_bits(P, K), 39)
        for bits in (0, 1, 32, 128, 1024):
            u = Q(1, 1 << (bits + 39))
            self.assertLess(K * u, 1)
            self.assertLessEqual(P * K * u / (1 - K * u), Q(1, 1 << bits))
            u = Q(1, 1 << (bits + 38))
            self.assertGreater(P * K * u / (1 - K * u), Q(1, 1 << bits))
        with self.assertRaisesRegex(ValueError, "positive feedback"):
            V.guard_bits(P, Q(0))
        with self.assertRaisesRegex(ValueError, "capacity exceeded"):
            V.guard_bits(Q(1 << 1024), Q(2))

    def test_semantic_faults_fail(self):
        bad = dict(self.word)
        bad["actions"] = [list(e) for e in self.word["actions"]]
        first = next(i for i, e in enumerate(bad["actions"]) if e[0] == "climb")
        bad["actions"][first][3] = 1
        with self.assertRaisesRegex(ValueError, "transport entry chart"):
            V.normalize(bad)
        # Suppress a real private clear without changing any instruction index.
        bad = list(self.program)
        index = next(i for i, e in enumerate(bad) if e.op == "reset")
        bad[index] = I("exact")
        with self.assertRaisesRegex(ValueError, "arbitrary-input endpoint"):
            V.endpoint_check(V.analyze(bad), self.word["live_ports"])
        # Initial compensation is part of the completed word, not free metadata.
        with self.assertRaisesRegex(ValueError, "arbitrary-input endpoint"):
            V.endpoint_check(V.analyze(self.program[7686:]), self.word["live_ports"])

    def test_read_only_export_and_fail_closed_receipts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("verify.py", "WORD.json.gz", "RESULT.json"):
                (root / name).write_bytes((HERE / name).read_bytes())
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            for flags in ([], ["-O"]):
                done = subprocess.run([sys.executable, "-I", "-B", *flags, str(root / "verify.py")],
                                      capture_output=True, text=True, timeout=60)
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertIn("input=131072 absolute=1394705 relative=2134050", done.stdout)
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})
            receipt = json.loads((root / "RESULT.json").read_text())
            receipt["uniform_relative_guard_bits"] = 38
            (root / "RESULT.json").write_text(json.dumps(receipt))
            failed = subprocess.run([sys.executable, "-I", "-B", str(root / "verify.py")],
                                    capture_output=True, text=True, timeout=60)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("complete canonical precision receipt", failed.stderr)
            raw = gzip.decompress((root / "WORD.json.gz").read_bytes())
            (root / "WORD.json.gz").write_bytes(gzip.compress(raw + b" ", mtime=0))
            failed = subprocess.run([sys.executable, "-I", "-B", str(root / "verify.py")],
                                    capture_output=True, text=True, timeout=60)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("literal stream authentication", failed.stderr)

    def test_changed_producer_is_rejected_before_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "export_word.py").write_bytes((HERE / "export_word.py").read_bytes())
            (root / "producer.py").write_text("raise RuntimeError('untrusted producer executed')\n")
            failed = subprocess.run([sys.executable, "-I", "-B", str(root / "export_word.py"),
                                     "--check"], capture_output=True, text=True, timeout=10)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("unchanged PR2139 producer authentication", failed.stderr)
            self.assertNotIn("untrusted producer executed", failed.stderr)

    def test_no_overwrite_and_coefficient_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "receipt.json"
            target.write_text("keep\n")
            failed = subprocess.run([sys.executable, "-I", "-B", str(HERE / "verify.py"),
                                     "--write", str(target)],
                                    capture_output=True, text=True, timeout=60)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("FileExistsError", failed.stderr)
            self.assertEqual(target.read_text(), "keep\n")
        with self.assertRaisesRegex(ValueError, "replay domain capacity"):
            V.analyze([I("exact")], roles=845)
        with self.assertRaisesRegex(ValueError, "replay domain capacity"):
            V.analyze([I("exact")] * 34334, roles=1)
        self.assertEqual(V.coefficient("-1/65536"), Q(-1, 65536))
        for value in ("0", "1/3", "65537", "1/131072"):
            with self.assertRaises(ValueError):
                V.coefficient(value)


if __name__ == "__main__":
    unittest.main()
