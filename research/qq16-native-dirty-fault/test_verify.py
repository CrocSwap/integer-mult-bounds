#!/usr/bin/env python3
"""Behavioral controls for the precise native-fault implication.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
V = types.ModuleType("fault_verifier")
V.__file__ = str(HERE / "verify.py")
exec(compile((HERE / "verify.py").read_bytes(), V.__file__, "exec"), V.__dict__)
N = V.N


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet, cls.word, cls.recipes, cls.residuals = V.load(V.ROOT)
        cls.events = V.expand(cls.packet)

    def test_global_phase_is_not_discarded(self):
        used = next(e for e in self.events if e[0] == "climb")
        old, new = used[3:5]
        rec = deepcopy(V.recipes_by_key(self.recipes)[0][old, new])
        before, after = N.frame(self.word["frames"][old]), N.frame(self.word["frames"][new])
        self.assertEqual(N.recipe(before, rec), after)
        rec["left"]["phase"] = (rec["left"]["phase"] + 1) % 4
        self.assertNotEqual(N.recipe(before, rec), after)

    def test_frame_adapters_cannot_be_ignored(self):
        rec = V.recipes_by_key(self.recipes)[1]["source", 39]
        image = N.mono(N.ONE, N.monomial_key(rec["left"]))
        self.assertEqual(image, N.frame(self.word["frames"][rec["frame"]]))
        self.assertNotEqual(image, N.ONE)
        self.assertEqual(N.mono(image, N.monomial_key(rec["left"]), True), N.ONE)

    def test_kernel_normalization(self):
        self.assertEqual(N.line(N.ONE, 67), N.ONE)
        self.assertEqual(N.line(N.ONE, 67, normalize=False), N.scaled(N.ONE, Q(2)))
        # Analytic single-basis column, independently specified coefficients.
        basis = N.vector([int(i == 0) for i in range(512)])
        want_re, want_im = [0]*512, [0]*512
        want_re[0] = want_re[67] = 1
        want_im[0], want_im[67] = 1, -1
        self.assertEqual(N.line(basis, 67), N.vector(want_re, want_im, 1))
        full = basis
        for axis in range(9):
            full = N.line(full, 1 << axis)
        self.assertNotEqual(full, basis)  # full frame is not physical identity
        self.assertEqual(sum(x*x for x in full[0] + full[1]), 2**(2*full[2]))

    def test_wrapper_all_input_components(self):
        # Distinct tagged components, not the constant-vector positive fixture.
        value = N.vector([i*67-1234 for i in range(512)], [i*i-9 for i in range(512)])
        keys = {e[2] for e in self.events if e[0] == "native_line"}
        for key in sorted(keys):
            entry = self.packet["native_line_recipes"][key]
            self.assertEqual(N.recipe(value, entry["recipe"]), N.line(value, entry["label"], entry["sign"]))
        rec = deepcopy(self.packet["native_line_recipes"][sorted(keys)[0]]["recipe"])
        rec["left"]["phase"] = (rec["left"]["phase"] + 1) % 4
        self.assertNotEqual(N.recipe(N.ONE, rec), N.ONE)

    def test_monomial_phase_convention(self):
        # Symmetric Q and strict-upper Q must encode the same quadratic form.
        rows = [1 << i for i in range(9)]
        upper = [0]*9
        upper[1] = 1 << 7
        symmetric = upper.copy()
        symmetric[7] = 1 << 1
        linear = [0]*9
        key1 = tuple(rows), tuple(upper), tuple(linear), 0, 0
        key2 = tuple(rows), tuple(symmetric), tuple(linear), 0, 0
        self.assertEqual(N.mono(N.ONE, key1), N.mono(N.ONE, key2))
        expected = N.vector([-1 if i & 2 and i & 128 else 1 for i in range(512)])
        self.assertEqual(N.mono(N.ONE, key1), expected)

    def test_error_location_and_restoration(self):
        response = V.witness(self.events)
        initial = [Q(0)]*712
        earlier, _ = V.scalar_run(self.events, initial, (24434, Q(1)))
        self.assertEqual(sum(bool(x) for x in earlier[224:704]), 102)
        self.assertNotEqual(earlier, response)
        with self.assertRaisesRegex(ValueError, "zero witness at residual boundary"):
            V.scalar_run(self.events, initial, (24434, Q(1)), require_zero_wrappers=True)

    def test_exact_and_absolute_error_escapes(self):
        response = V.witness(self.events)
        for exponent in (0, 67, 256):
            initial = [Q(0)]*712
            initial[112], initial[359] = Q(1), Q(2**exponent)
            exact, cut = V.scalar_run(self.events, initial)
            self.assertEqual(exact, initial)
            self.assertEqual(cut, (-4*initial[359], initial[359]))
            absolute, _ = V.scalar_run(self.events, initial, (V.FAULT, Q(1, 256)))
            self.assertEqual(absolute, [x+q/256 for x, q in zip(initial, response)])
            self.assertEqual(max(abs(a-b) for a, b in zip(absolute[:224], exact[:224])), Q(1, 512))
        initial[359] = 0
        self.assertEqual(V.scalar_run(self.events, initial, (V.FAULT, Q(0)))[0], initial)

    def test_fault_binding_and_source_invalidation(self):
        bad = deepcopy(self.packet)
        bad["core_words"]["forward"][V.FAULT][1][3] = -4
        with self.assertRaisesRegex(ValueError, "fault event binding"):
            V.expand(bad)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            archive = root / "research/community-frontier1042-audit/selected-replay.tar.gz"
            archive.parent.mkdir(parents=True)
            archive.write_bytes(b"altered source")
            with self.assertRaisesRegex(ValueError, "source pin"):
                V.load(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
