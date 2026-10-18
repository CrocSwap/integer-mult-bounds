#!/usr/bin/env python3
"""Independent scalar controls for the transpose/rank certificate (Apache-2.0)."""
import copy
import gzip
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
spec = importlib.util.spec_from_file_location("rank80", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def scalar(gates, initial):
    """Ordinary Boolean execution, independent of packed covector arithmetic."""
    state = initial[:]
    for dest, sources in gates:
        value = state[dest]
        for source in sources:
            value = value != state[source]
        state[dest] = value
    return state


def literal_scalar(word, sections, initial):
    """Read the source JSON directly, without the verifier's stream adapter."""
    state = initial[:]
    for section in sections:
        if section == "scatter":
            copied = [state[register] for register in word["ret"]]
            for target, row in enumerate(word["scatter"]):
                for index in row:
                    state[120 + target] = state[120 + target] != copied[index]
        else:
            for _, dest, sources in word[section]:
                for source in sources:
                    state[dest] = state[dest] != state[source]
    return state


class Evidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = v.load_word()
        cls.cert = json.loads((HERE / "EXPECTED.json").read_text())
        cls.cols = v.extract(cls.word)
        cls.pivots = [p - 240 for p in cls.cert["pivot_helpers_absolute"]]
        cls.inv = [int(r, 16) for r in cls.cert["minor_inverse_rows_hex"]]
        cls.free = [j for j in range(420) if j not in cls.pivots]
        cls.right = []
        for t in range(120):
            cls.right.append(sum(((r >> t) & 1) << p for p, r in zip(cls.pivots, cls.inv)))
        cls.kernel = []
        for f in cls.free:
            # Set symmetric difference implements linear combinations separately.
            support = {f}
            for t in range(120):
                if (cls.cols[f] >> t) & 1:
                    support.symmetric_difference_update(j for j in range(420) if (cls.right[t] >> j) & 1)
            cls.kernel.append(sum(1 << j for j in support))

    def test_literal_certificate_dense_inverse_products(self):
        # Check both products using lists of bits, no inverse/elimination routine.
        matrix = [[(self.cols[p] >> i) & 1 for p in self.pivots] for i in range(120)]
        inv = [[(row >> j) & 1 for j in range(120)] for row in self.inv]
        for a, b in ((matrix, inv), (inv, matrix)):
            for i in range(120):
                for j in range(120):
                    self.assertEqual(sum(a[i][k] * b[k][j] for k in range(120)) % 2, int(i == j))

    def test_all_dirty_witnesses_and_kernel_directions_by_scalar_execution(self):
        # 120 right-inverse + 300 kernel vectors form a basis of all helper dirt.
        for index, bits in enumerate(self.right + self.kernel):
            initial = [False] * 240 + [bool((bits >> j) & 1) for j in range(420)]
            out = literal_scalar(self.word, ("A", "scatter", "B"), initial)
            expected = [j == index for j in range(120)] if index < 120 else [False] * 120
            self.assertEqual(out[120:240], expected)
            self.assertEqual(literal_scalar(self.word, ("D", "A", "scatter", "B", "C"), initial), initial)

    def test_adjoint_identity_exhaustive_small_circuits(self):
        rng = random.Random(80)
        # Exhaust all 16 inputs x 16 observables for each of 40 tiny circuits.
        for _ in range(40):
            gates = []
            for _ in range(9):
                d = rng.randrange(4)
                gates.append((d, tuple(s for s in range(4) if s != d and rng.randrange(2))))
            back = v.pullback(gates, range(4))[:4]
            for x in range(16):
                out = scalar(gates, [bool((x >> i) & 1) for i in range(4)])
                for q in range(16):
                    lhs = sum(out[i] * ((q >> i) & 1) for i in range(4)) % 2
                    rhs = sum(((x >> i) & 1) * ((back[i] & q).bit_count() % 2) for i in range(4)) % 2
                    self.assertEqual(lhs, rhs)

    def test_all_minimum_weight_words_in_literal_circuit(self):
        supports = self.cert["kernel_distance"]["weight_four_supports_absolute"]
        self.assertEqual(len(supports), 18)
        for support in supports:
            for subset in range(1, 16):
                state = [False] * 660
                for i, register in enumerate(support):
                    state[register] = bool((subset >> i) & 1)
                error = literal_scalar(self.word, ("A", "scatter", "B"), state)[120:240]
                self.assertEqual(not any(error), subset == 15)

    def test_full_endpoint_catches_cleanup_damage(self):
        broken = copy.deepcopy(self.word)
        broken["C"].pop(80)
        # K and its rank are unchanged, but restoration is a separate obligation.
        self.assertEqual(v.extract(broken), self.cols)
        with self.assertRaisesRegex(v.Reject, "complete scalar endpoint"):
            v.build(broken)

    def test_source_pins_and_recompression(self):
        pins = json.loads((HERE / "SOURCES.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in pins["files"]:
                dst = root / path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(v.ROOT / path, dst)
            path = root / v.WORD
            payload = gzip.decompress(path.read_bytes())
            path.write_bytes(gzip.compress(payload, compresslevel=1, mtime=80))
            self.assertEqual(v.load_word(root), self.word)
            bad = json.loads(payload)
            bad["D"][80][2].pop()
            path.write_bytes(gzip.compress(json.dumps(bad).encode(), mtime=80))
            with self.assertRaisesRegex(v.Reject, "source pin"):
                v.load_word(root)

    def test_cli_rejects_changed_certificate_under_optimization(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            bad = copy.deepcopy(self.cert)
            bad["nullity"] = 299
            path.write_text(json.dumps(bad))
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"), "--check", str(path)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("certificate mismatch", result.stderr)
            self.assertNotIn("PASS_R420", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
