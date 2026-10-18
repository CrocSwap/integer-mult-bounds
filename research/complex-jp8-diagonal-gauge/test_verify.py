#!/usr/bin/env python3
"""Independent integer row replay and adverse controls; Apache-2.0.

Substantial OpenAI Codex assistance for Luis Leon (@mythrilium).
Independence here means a separate arithmetic implementation, not a second
human reviewer. Does not use Fraction for its matrix arithmetic.
"""
import copy
import importlib.util
import json
import random
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gauge_verify", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def binary_exponent(x):
    if x <= 0 or x & (x - 1):
        raise ValueError("positive power of two required")
    return x.bit_length() - 1


def integer_replay(word, n, backward=False):
    # Row r represents 2**exponents[r] * sum_j rows[r][j] x_j.
    rows = [{r: 1} for r in range(n)]
    exponents = [0] * n
    for op in word:
        if op[0] == "scale":
            r, p, q = op[1:4]
            e = binary_exponent(abs(p)) - binary_exponent(q)
            if backward:
                e = -e
            exponents[r] += e
            if p < 0:
                rows[r] = {j: -x for j, x in rows[r].items()}
        elif op[0] == "add":
            t, s, p, q = op[1:5]
            if backward:
                t, s, p = s, t, -p
            source_exp = exponents[s] - binary_exponent(q)
            target_exp = exponents[t]
            common = min(source_exp, target_exp)
            updated = {j: x << (target_exp - common) for j, x in rows[t].items()}
            for j, x in rows[s].items():
                value = updated.get(j, 0) + (p * x << (source_exp - common))
                if value:
                    updated[j] = value
                else:
                    updated.pop(j, None)
            rows[t], exponents[t] = updated, common
        else:
            raise ValueError("unknown native operation")
    # Canonicalize by removing common factors of two in each integer row.
    result = []
    for row, e in zip(rows, exponents):
        shift = min(((abs(x) & -abs(x)).bit_length() - 1 for x in row.values()), default=0)
        result.append((e + shift, {j: x >> shift for j, x in row.items()}))
    return result


class GaugeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word, cls.programs, cls.spec = V.load_inputs()
        cls.cert = json.loads((HERE / "CERTIFICATE.json").read_text())
        cls.g = cls.cert["exponents"]
        cls.old = cls.word["cleanup"]
        cls.new = V.transform(cls.old, cls.g)
        cls.n = len(cls.g)
        cls.edges = V.native_edges(cls.old)

    def test_all_cleanup_columns_both_orientations(self):
        for back in (False, True):
            self.assertEqual(integer_replay(self.old, self.n, back), integer_replay(self.new, self.n, back))

    def test_exact_cost_from_explicit_odd_parts(self):
        # Derive the invariant odd-numerator part independently.
        old_total = new_total = 0
        for op in self.old:
            if op[0] == "scale":
                continue
            t, s, p, q = op[1:5]
            a = abs(p)
            twos = (a & -a).bit_length() - 1
            odd = a >> twos
            e = twos - binary_exponent(q)
            constant = 2 + len(bin(odd)[2:]) + bin(odd).count("1")
            old_total += constant + abs(e)
            new_total += constant + abs(e + self.g[t] - self.g[s])
        new_total += 2 * sum(abs(e) for e in self.g)
        self.assertEqual(2 * (old_total - new_total), 6154)

    def test_omitted_boundary_scales_fail(self):
        reference = integer_replay(self.old, self.n)
        self.assertNotEqual(reference, integer_replay(self.new[1:], self.n))
        self.assertNotEqual(reference, integer_replay(self.new[:-1], self.n))

    def test_wrong_conjugation_sign_fails(self):
        bad = copy.deepcopy(self.new)
        boundary = sum(e != 0 for e in self.g)
        for i, op in enumerate(self.old):
            if op[0] == "add" and self.g[op[1]] != self.g[op[2]]:
                # Original coefficient in one changed gate fails the map.
                bad[boundary + i] = copy.deepcopy(op)
                break
        self.assertNotEqual(integer_replay(self.old, self.n), integer_replay(bad, self.n))

    def test_dual_mutations_rejected(self):
        dual = self.cert["edge_dual"]
        bad = dual[:]
        bad[0] = 2
        with self.assertRaisesRegex(ValueError, "box"):
            V.check_duality(self.edges, self.g, bad)
        with self.assertRaisesRegex(ValueError, "gap"):
            V.check_duality(self.edges, self.g, [0] * len(dual))
        # Box-feasible flow may still violate divergence.
        with self.assertRaisesRegex(ValueError, "divergence"):
            V.check_duality(self.edges, self.g, [1] * len(dual))
        changed_g = self.g[:]
        changed_g[0] += 100
        with self.assertRaisesRegex(ValueError, "gap"):
            V.check_duality(self.edges, changed_g, dual)

    def test_duality_synthetic_enumeration(self):
        # A two-node example: min 2(|g0|+|g1|)+3|2+g0-g1| = 4.
        edges = [(0, 1, 2)] * 3
        self.assertEqual(V.check_duality(edges, [-2, 0], [1, 1, 0]), 4)
        costs = [2 * (abs(a) + abs(b)) + 3 * abs(2 + a - b)
                 for a in range(-5, 6) for b in range(-5, 6)]
        self.assertEqual(min(costs), 4)

    def test_private_work_and_alias_controls(self):
        with self.assertRaisesRegex(ValueError, "boundary"):
            V.primitive_coefficient_check(V.Q(3, 8), omit_clear=True)
        with self.assertRaisesRegex(ValueError, "alias"):
            V.native_edges([["add", 0, 0, 1, 1, 1]])

    def test_frame_and_cleanup_binding_controls(self):
        with self.assertRaisesRegex(ValueError, "full-frame"):
            V.native_edges([["add", 0, 1, 1, 1, 0]])
        bad = copy.deepcopy(self.programs["forward"])
        pos = bad.index(["phase", "full_frame_cleanup"]) + 1
        bad[pos][1][3] *= 2
        with self.assertRaisesRegex(ValueError, "pinned contiguous"):
            V.splice(bad, self.old, self.new, False)

    def test_endpoint_neutral_prefix_excursion_rejected(self):
        # Exact identity but a coefficient-work payload far beyond the allowance.
        events = [["scalar", ["clear", ["C", r]], 1] for r in range(8)]
        events += [["scalar", ["scale", ["L", 0], 2 ** 193, 1], 1],
                   ["scalar", ["scale", ["L", 0], 1, 2 ** 193], 1]]
        with self.assertRaisesRegex(ValueError, "prefix"):
            V.replay(events, 1, 0, False)

    def test_integer_engine_against_small_rational_maps(self):
        rng = random.Random(35)
        for _ in range(25):
            ops = []
            for _ in range(20):
                t, s = rng.sample(range(4), 2)
                ops.append(["add", t, s, rng.choice([-3, -1, 1, 3]), 2 ** rng.randrange(4), 1])
            for back in (False, True):
                result = integer_replay(ops, 4, back)
                rows = [[V.Q(i == j) for j in range(4)] for i in range(4)]
                for op in ops:
                    t, s, p, q = op[1:5]
                    if back:
                        t, s, p = s, t, -p
                    rows[t] = [x + V.Q(p, q) * y for x, y in zip(rows[t], rows[s])]
                for r, (e, ints) in enumerate(result):
                    self.assertEqual(rows[r], [V.power2(e) * ints.get(j, 0) for j in range(4)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
