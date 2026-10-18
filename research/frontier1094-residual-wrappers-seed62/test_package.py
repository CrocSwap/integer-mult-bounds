# SPDX-License-Identifier: Apache-2.0
"""Controls for the residual-wrapper audit (about 30 s).

Run: python3 -I -B -m unittest discover -s research/frontier1094-residual-wrappers-seed62 -p test_package.py -v
"""
import ast
import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import closed_form as B  # noqa: E402
import verify as V  # noqa: E402

R, A = V.load_1781()
DATA, ADAPTERS, CHECKS, BINDING = V.bind(R)
WORD, PROGRAMS = DATA['word'], DATA['programs']
FRAMES = WORD['frames']
REC = ADAPTERS['recipes']
RESULT = json.loads((HERE / 'RESULT.json').read_text())


def parts(k):
    E, U = V.end_of(k)
    return E, U, len(FRAMES[U]) - len(FRAMES[E])


class Binding(unittest.TestCase):
    def test_decoy_adapters_rejected(self):
        with self.assertRaisesRegex(V.Reject, 'pinned by the owner audit'):
            V.bind(R, member_overrides={'adapters': V.MEMBERS['decoy']})

    def test_archive_byte_flip_rejected(self):
        raw = bytearray((V.ROOT / R.CASES['archive']['path']).read_bytes())
        raw[-1] ^= 1
        with self.assertRaisesRegex(Exception, 'archive digest'):
            V.bind(R, archive_bytes=bytes(raw))

    def test_binding_recorded(self):
        self.assertEqual(BINDING['residual_adapters_sha256'], RESULT['binding']['residual_adapters_sha256'])
        self.assertFalse(BINDING['wrapper_checks_in_owner_audit'])
        self.assertIn('fresh_invoice', BINDING['wrapper_checks_pinned_by'])

    def test_invoice_pin_mismatch_rejected(self):
        with self.assertRaisesRegex(V.Reject, 'pinned by the fresh invoice|bound by the certificate'):
            V.bind(R, member_overrides={'invoice': V.MEMBERS['audit']})


class Inventory(unittest.TestCase):
    def test_counts(self):
        inv = V.inventory(A, WORD, PROGRAMS, ADAPTERS)
        self.assertEqual(inv, RESULT['inventory'])
        self.assertEqual(inv['kinds'], {'cold_hpe': 12, 'enter_hpe': 2, 'full_end': 22})

    def test_dropped_pre_event_rejected(self):
        progs = copy.deepcopy(PROGRAMS)
        i = next(n for n, e in enumerate(progs['forward']) if e[0] == 'residual_adapter' and e[1] == 'pre')
        del progs['forward'][i]
        with self.assertRaisesRegex(V.Reject, 'one pre and one post'):
            V.inventory(A, WORD, progs, ADAPTERS)

    def test_wrong_event_key_rejected(self):
        progs = copy.deepcopy(PROGRAMS)
        i = next(n for n, e in enumerate(progs['forward']) if e[0] == 'residual_adapter' and len(e) == 5)
        progs['forward'][i] = progs['forward'][i][:4]            # a hyperplane-end event read as its FULL key
        with self.assertRaisesRegex(V.Reject, 'residual event key'):
            V.inventory(A, WORD, progs, ADAPTERS)

    def test_record_vector_mismatch_rejected(self):
        bad = copy.deepcopy(ADAPTERS)
        bad['recipes']['423']['vectors'] = [46]
        with self.assertRaisesRegex(V.Reject, 'record frames 423'):
            V.inventory(A, WORD, PROGRAMS, bad)


class Kernels(unittest.TestCase):
    def test_kernel_b_reproduces_the_published_frame_kernels(self):
        e = json.loads((V.ROOT / R.CASES['fixtures']['pr702']['path']).read_text())['identities']
        self.assertTrue(all(B.kernel_digest_702(i['frame']) == i['kernel_sha256'] for i in e[:4]))

    def test_kernel_b_matches_kernel_a_on_frame_columns(self):
        for f in (2, 124, 423, 1000):
            U = FRAMES[f]
            k = A.c_gates(A.canonical_frame(U))
            cols = A.columns(A.run(A.canonical_frame(U), A.radix(k)), A.radix(k))
            for x in (0, 5, 300):
                col, e = B.frame_column(U, x)
                self.assertEqual(e, k)
                self.assertEqual(col, cols.get(x, {}))

    def test_both_kernels_accept_samples_and_reject_a_phase_mutant(self):
        for k in ('2', '0:124', '0:1000', '3:998'):
            E, U, w = parts(k)
            r = REC[k]
            self.assertIsNone(B.wrapper_identity(FRAMES[E], FRAMES[U], r['left'], r['right'], w))
            bad = dict(r['left'], phase=(r['left']['phase'] + 1) % 4)
            self.assertIsNotNone(B.wrapper_identity(FRAMES[E], FRAMES[U], bad, r['right'], w))
            self.assertFalse(A.same_operator(A.canonical_frame(FRAMES[E]) + A.monomial(r['right']) + A.fourier(w)
                                             + A.monomial(bad), A.canonical_frame(FRAMES[U])))

    def test_kernel_b_monomial_and_fourier_match_kernel_a(self):
        self.assertIn('equal kernel A', V.cross_check(A, WORD, ADAPTERS))

    def test_lean_pairs_are_records(self):
        cal = V.calibrate(R, ADAPTERS)
        cal['kernel_B_vs_kernel_A'] = V.cross_check(A, WORD, ADAPTERS)
        self.assertEqual(cal, RESULT['calibration'])

    def test_kernel_b_imports_only_the_standard_library(self):
        tree = ast.parse((HERE / 'closed_form.py').read_text())
        mods = {a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        mods |= {n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        self.assertLessEqual(mods, {'hashlib', 'json'})


class Controls(unittest.TestCase):
    def test_recorded_controls_all_reject(self):
        for name, value in RESULT['controls'].items():
            if name == 'producer_wrapper_checks':
                continue
            self.assertTrue(value.startswith('rejected') or value.startswith('other basis rejected'), name)

    def test_hyperplane_end_record_fails_against_full(self):
        k = '0:1000'
        E, U, w = parts(k)
        r = REC[k]
        self.assertFalse(A.same_operator(A.canonical_frame(FRAMES[E]) + A.monomial(r['right']) + A.fourier(9)
                                         + A.monomial(r['left']), A.canonical_frame(FRAMES[1])))

    def test_result_reports_all_records_exact(self):
        ev = RESULT['evaluation']
        self.assertEqual((ev['records'], ev['kernel_A_exact'], ev['kernel_B_exact']), (36, 36, 36))


if __name__ == '__main__':
    unittest.main()
