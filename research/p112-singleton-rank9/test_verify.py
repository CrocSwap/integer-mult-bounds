#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Semantic failure controls, separate from the complete finite replay."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('singleton_verifier', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lines, cls.frame, cls.live, cls.ip, cls.pairing = v.model()
        cls.alpha, cls.beta = next((a, b) for a in cls.live for b in cls.live
                                  if cls.ip[a][b] % 2)
        cls.recorded = json.loads((HERE / 'CERTIFICATE.json').read_text())

    def factors(self, h=None):
        return v.fixture_factors(self.live, self.frame, self.ip, self.alpha,
                                 self.beta, v.IMAG, h or v.identity(9))

    def validate(self, d, t, alpha=None, beta=None, amplitude=None):
        return v.validate_fixture(d, t, self.live, self.ip, self.pairing,
                                  self.alpha if alpha is None else alpha,
                                  self.beta if beta is None else beta,
                                  v.IMAG if amplitude is None else amplitude)

    def test_positive_exact_imaginary_completion(self):
        self.assertEqual(self.validate(*self.factors()), [8] * 8 + [0])

    def test_omitted_free_correction_changes_an_entry(self):
        d, t = self.factors()
        d[self.live.index(self.alpha)][8] = v.ZERO
        with self.assertRaisesRegex(v.Invalid, 'incorrect single-entry'):
            self.validate(d, t)

    def test_complex_conjugation_is_not_ordinary_transpose(self):
        d, t = self.factors()
        t = [[(x[0], -x[1]) for x in row] for row in t]
        with self.assertRaisesRegex(v.Invalid, 'incorrect single-entry'):
            self.validate(d, t)

    def test_nonreciprocal_factor_change_fails(self):
        h = v.identity(9)
        h[8][0] = v.ONE
        d, _ = self.factors(h)
        _, t = self.factors()
        with self.assertRaisesRegex(v.Invalid, 'incorrect single-entry'):
            self.validate(d, t)

    def test_omitted_compensation_breaks_even_entry(self):
        h = v.identity(9)
        for j in range(8):
            h[j][0] = v.scalar(self.ip[self.alpha][self.frame[j]])
        shear = v.identity(9)
        shear[8][0] = v.scalar(-4)
        d, t = self.factors(v.matmul(h, shear))
        self.assertEqual(self.validate(d, t), [7] + [8] * 7 + [1])
        d = [row[:8] + [v.ZERO] for row in d]
        # The canceled self-entry contributes zero at (alpha,alpha);
        # the discarded singleton-side term was its required compensation.
        pos = self.live.index(self.alpha)
        actual = v.sum_gaussian(v.mul(x, y) for x, y in zip(d[pos], t[pos]))
        self.assertNotEqual(actual, v.scalar(4))
        with self.assertRaisesRegex(v.Invalid, 'incorrect single-entry'):
            self.validate(d, t)

    def test_missing_hyperplane_fails_coverage(self):
        hypers = v.functionals(self.pairing)[:-1]
        with self.assertRaisesRegex(v.Invalid, 'missing or repeated'):
            v.kernel_census(self.lines, self.frame, self.live, self.ip,
                            self.pairing, hypers)

    def test_corrupted_pairing_changes_the_label_space(self):
        broken = self.pairing[:]
        broken[0] ^= 1 << 2
        with self.assertRaisesRegex(v.Invalid, 'functional space'):
            v.functionals(broken)

    def test_false_kernel_receipt_fails(self):
        bad = copy.deepcopy(self.recorded)
        bad['kernel_census']['reduced_normals'][0]['normal_lines'].pop()
        with self.assertRaisesRegex(v.Invalid, 'certificate differs'):
            v.check_receipt(self.recorded, bad)

    def test_false_cost_receipt_fails(self):
        bad = copy.deepcopy(self.recorded)
        bad['fixtures'][0]['term_costs'][0] = 7
        with self.assertRaisesRegex(v.Invalid, 'certificate differs'):
            v.check_receipt(self.recorded, bad)

    def test_even_pair_is_outside_free_correction_scope(self):
        d, t = self.factors()
        with self.assertRaisesRegex(v.Invalid, 'odd-entry scope'):
            self.validate(d, t, beta=self.alpha)

    def test_zero_amplitude_is_outside_rank_nine_scope(self):
        with self.assertRaisesRegex(v.Invalid, 'nonzero'):
            self.validate(*self.factors(), amplitude=v.ZERO)

    def test_source_drift_fails(self):
        old_root = v.ROOT
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                target = root / 'research/complex-frame-pair-decoders/PROOF.md'
                target.parent.mkdir(parents=True)
                target.write_text('changed model convention\n')
                v.ROOT = root
                with self.assertRaisesRegex(v.Invalid, 'source input drift'):
                    v.check_sources()
        finally:
            v.ROOT = old_root

    def test_singular_basis_change_fails(self):
        h = v.identity(9)
        h[8] = h[0][:]
        with self.assertRaisesRegex(v.Invalid, 'singular'):
            self.factors(h)


if __name__ == '__main__':
    unittest.main(verbosity=2)
