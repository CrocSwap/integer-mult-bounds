#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the conditional producer envelope.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
"""
from copy import deepcopy
from fractions import Fraction as Q
import json
from pathlib import Path
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
V = types.ModuleType("producer_envelope")
V.__file__ = str(HERE / "verify.py")
exec(compile((HERE / "verify.py").read_bytes(), V.__file__, "exec"), V.__dict__)


def clear_all():
    return [["scalar", ["clear", ["C", i]], 0] for i in range(8)]


def add(d, s, a=1, b=1):
    return ["scalar", ["add", d, s, a, b], 0]


def scalar_norm2(v):
    return sum(x * x for x in v)


def plus(a, b, c=Q(1)):
    return tuple(x + c * y for x, y in zip(a, b))


def rotate(v):
    return (-v[1], v[0])


def reflect(v):
    return (v[0], -v[1])


def oracle_step(states, event):
    """Actual two-dimensional noncommuting isometries, not a scalar shadow."""
    if event[0] == "scalar":
        g = event[1]
        d = g[1][1] + (704 if g[1][0] == "C" else 0)
        if g[0] == "clear":
            return d, (Q(0), Q(0)), True
        if g[0] == "scale":
            return d, tuple(Q(g[2], g[3]) * x for x in states[d]), False
        s = g[2][1] + (704 if g[2][0] == "C" else 0)
        return d, plus(states[d], states[s], Q(g[3], g[4])), False
    d = event[1][1] + (704 if event[1][0] == "C" else 0)
    f = rotate if event[0] == "native_line" else reflect
    return d, f(states[d]), False


class EnvelopeTests(unittest.TestCase):
    def test_inherited_endpoint_geometry_and_mutants(self):
        packet = V.load()
        self.assertEqual(V.endpoint_calibration(packet)["F_data_norm_over_H"], "58")
        wrong = deepcopy(packet)
        wrong["K_rows"][0]["0"] = "1/2"
        with self.assertRaisesRegex(ValueError, "K=R"):
            V.endpoint_calibration(wrong)
        wrong = deepcopy(packet)
        wrong["A_ports"][0] = wrong["T_ports"][0]
        with self.assertRaisesRegex(ValueError, "port partition"):
            V.endpoint_calibration(wrong)

    def test_noncommuting_state_dependent_errors_at_every_cut(self):
        l0, l1, h, c = ["L", 0], ["L", 1], ["L", 224], ["C", 0]
        events = clear_all() + [
            ["native_line", h, "R", 0, 0], add(l0, h, 3, 4),
            ["cover_map", l0, "S", 0, 0], add(c, l0, -1, 2),
            ["native_line", c, "R", 0, 0], add(l1, c),
            ["scalar", ["scale", h, -1, 2], 0],
            ["native_line", h, "R", 0, 0], add(l0, l1, -1)] + clear_all()
        trace = []
        report = V.stage(events, trace)
        self.assertNotEqual(rotate(reflect((1, 2))), reflect(rotate((1, 2))))
        for u in (Q(0), Q(1, 64), Q(1, 128)):
            self.assertLessEqual(report["defect_sites"] * u, Q(1, 2))
            ideal = [(Q(0), Q(0)) for _ in range(712)]
            ideal[0], ideal[1], ideal[224] = (Q(1), Q(0)), (Q(0), Q(1)), (Q(-1), Q(0))
            noisy = ideal.copy()
            for t, (event, row) in enumerate(zip(events, trace)):
                d, ideal_value, cleared = oracle_step(ideal, event)
                _, actual_value, _ = oracle_step(noisy, event)
                ideal[d] = ideal_value
                # A coherent, state-dependent error rotated away from its operand.
                noise = (Q(0), Q(0)) if cleared else tuple(u * x for x in rotate(actual_value))
                noisy[d] = plus(actual_value, noise)
                error = plus(noisy[d], ideal[d], -1)
                bound = 2 * u * Q(row["J"])
                self.assertLessEqual(scalar_norm2(error), bound * bound, (u, t))
                self.assertLessEqual(scalar_norm2(noisy[d]), (2 * Q(row["P"]))**2, (u, t))

    def test_positive_polynomial_derivative(self):
        events = clear_all() + [add(["L", 0], ["L", 224], -3, 4),
                  ["native_line", ["L", 224], "R", 0, 0],
                  add(["C", 0], ["L", 0]), add(["L", 1], ["C", 0], 1, 2)] + clear_all()
        trace = []
        V.stage(events, trace)
        polynomials = [{0: Q(1)} for _ in range(704)] + [{} for _ in range(8)]
        for e, record in zip(events, trace):
            if e[0] == "scalar":
                g = e[1]
                d = g[1][1] + 704 * (g[1][0] == "C")
                if g[0] == "clear":
                    polynomials[d] = {}
                else:
                    s = g[2][1] + 704 * (g[2][0] == "C")
                    p = dict(polynomials[d])
                    for power, value in polynomials[s].items():
                        p[power] = p.get(power, Q(0)) + abs(Q(g[3], g[4])) * value
                    polynomials[d] = {k + 1: v for k, v in p.items()}
            else:
                d = e[1][1]
                polynomials[d] = {k + 1: v for k, v in polynomials[d].items()}
            self.assertEqual(sum(polynomials[d].values()), Q(record["P"]))
            self.assertEqual(sum(k * v for k, v in polynomials[d].items()), Q(record["J"]))

    def test_feedback_factor_cannot_be_dropped(self):
        u = Q(1, 4)
        actual_error = (1 + u)**2 - 1
        self.assertGreater(actual_error, 2 * u)
        self.assertLessEqual(actual_error, 2 * u * (1 + u))
        self.assertLessEqual(actual_error, 2 * u * 2)

    def test_dirty_ratio_and_noisy_helper_carry(self):
        # x+=h; x-=h, with a legal final relative fault, restores h exactly.
        u, dirty = Q(1, 1024), Q(2**20)
        data_error = 2 * u * dirty
        self.assertGreater(data_error, 2 * u)  # data-only input bound is insufficient.
        # F: h+=x; h-=x with the final defect 2u, starting x=1,h=0.
        returned_h = 2 * u
        self.assertGreater(returned_h, 0)  # reusing the old D=0 bound is invalid.
        # B: t+=h with defect u*h; t-=h exactly. The carried error is an operand.
        terminal = (1 + u) * returned_h - returned_h
        self.assertEqual(terminal, 2 * u * u)
        self.assertGreater(terminal, 0)
        self.assertLessEqual(returned_h, 0 + 2 * u)

    def test_native_and_map_defects_must_be_counted(self):
        for event in (["native_line", ["L", 0], "R", 0, 0],
                      ["cover_map", ["L", 0], "S", 0, 0]):
            full = V.stage(clear_all() + [event])
            omitted = V.stage(clear_all())
            self.assertEqual(Q(full["terminal"]["data"]["J"]), 1)
            self.assertEqual(Q(omitted["terminal"]["data"]["J"]), 0)
            self.assertGreater(Q(1, 64), 2 * Q(1, 64) * Q(omitted["terminal"]["data"]["J"]))

    def test_private_transient_and_clear_ownership(self):
        events = clear_all() + [add(["C", 0], ["L", 0]),
                               ["native_line", ["C", 0], "R", 0, 0]] + clear_all()
        r = V.stage(events)
        self.assertGreater(Q(r["all_cut"]["J"]["J"]), 0)
        self.assertEqual(Q(r["terminal"]["data"]["J"]), 0)
        with self.assertRaisesRegex(ValueError, "uninitialized"):
            V.stage([add(["C", 0], ["L", 0])] + clear_all())
        with self.assertRaisesRegex(ValueError, "owned CLEAR"):
            V.stage([["scalar", ["clear", ["L", 224]], 0]] + clear_all())
        with self.assertRaisesRegex(ValueError, "unknown event"):
            V.stage([["unpriced_multiwire_child", 0]])
        body = [clear_all()[0], ["cover_map", ["L", 0], "S", 0, 0], clear_all()[0]]
        malformed = {"programs": {"F_0": [["private_sweep", "bad", body]]}}
        with self.assertRaisesRegex(ValueError, "owner-local"):
            V.expand(malformed, "F_0")
        malformed["programs"]["F_0"][0][2] = [add(["C", 0], ["L", 0]), clear_all()[0]]
        with self.assertRaisesRegex(ValueError, "first/last"):
            V.expand(malformed, "F_0")

    def test_sign_invariance_and_scalar_price_change(self):
        events = clear_all() + [add(["L", 0], ["L", 224], -1, 2)]
        a = V.stage(events)
        changed = deepcopy(events)
        changed[-1][1][3] *= -1
        b = V.stage(changed)
        self.assertEqual(a["all_cut"], b["all_cut"])
        self.assertNotEqual(a["event_sha256"], b["event_sha256"])
        changed[-1][1][4] = 1
        self.assertGreater(Q(V.stage(changed)["all_cut"]["J"]["J"]), Q(a["all_cut"]["J"]["J"]))

    def test_exact_budget_and_logarithm_controls(self):
        r = json.loads((HERE / "RESULT.json").read_text())
        c = r["composition"]
        jf, jb = Q(c["F_persistent_J"]), Q(c["B_persistent_J"])
        self.assertTrue(2**61 < jf < 2**62)
        self.assertTrue(2**81 < jb < 2**82)
        for beta, delta in ((0, 0), (64, 0), (64, 12), (127, 300)):
            uf, ub = Q(2)**(-beta-delta-71), Q(2)**(-beta-delta-102)
            self.assertLessEqual(2 * uf * jf * 2**delta, Q(2)**(-beta-8))
            self.assertLessEqual(2 * ub * jb * 2**(delta+6), Q(2)**(-beta-13))
            self.assertLess(26977 * max(uf, ub), Q(1, 2))
        # One fewer bit fails this particular majorant, not every implementation.
        self.assertGreater(2 * Q(2)**-101 * jb * 64, Q(2)**-13)
        self.assertEqual(Q(c["decoded_error_ratio"]), Q(7587, 8192))
        for value, expected in ((Q(1, 8), -3), (1, 0), (Q(3, 2), 1), (2, 1), (Q(17, 8), 2)):
            self.assertEqual(V.ceil_log2(value), expected)

    def test_corrupted_input_rejected_before_math(self):
        original_root = V.ROOT
        sources = json.loads((HERE / "SOURCES.json").read_text())
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            root = Path(temp)
            for item in sources["files"]:
                if item["usage"] == "input":
                    target = root / item["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((original_root / item["path"]).read_bytes())
            target = root / V.CERT
            target.write_bytes(target.read_bytes() + b"changed")
            try:
                V.ROOT = root
                with self.assertRaisesRegex(ValueError, "source hash"):
                    V.load()
            finally:
                V.ROOT = original_root


if __name__ == "__main__":
    unittest.main()
