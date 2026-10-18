# SPDX-License-Identifier: Apache-2.0
"""Controls for the late-entrance census (about 40 s).

Run: python3 -I -B -m unittest discover -s research/r439-late-entrance-census-seed09 -p test_package.py -v
"""
import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import census as E  # noqa: E402
import engine2 as F  # noqa: E402
import verify as V  # noqa: E402

RESULT = json.loads((HERE / 'RESULT.json').read_text())
P = V.load_word(*V.WORDS['PR589'])
W = E.Word(P)
ST = W.raw()
K = ST['K']
CL = E.closure(W, W.first_contact())
SUP = E.supports(CL['elig'])
WF = E.W_fav(W, ST)
WA = E.W_sweep(W, ST, 'A6')
v = W.v


def cm(regs):
    return sum(1 << (r - 2 * v) for r in regs)


class Binding(unittest.TestCase):
    def test_word_byte_flip_rejected(self):
        path, digest = V.WORDS['PR589']
        raw = bytearray((V.ROOT / path).read_bytes())
        raw[100] ^= 1
        with self.assertRaisesRegex(V.Reject, 'B word digest'):
            V.load_word(path, digest, bytes(raw))

    def test_wrong_pin_rejected(self):
        path, _ = V.WORDS['PR1188']
        with self.assertRaisesRegex(V.Reject, 'B word digest'):
            V.load_word(path, V.WORDS['PR589'][1])


class Structure(unittest.TestCase):
    def test_closure_and_supports(self):
        self.assertEqual((len(CL['L']), len(SUP), CL['meets']), (366, 4954, 549))

    def test_K_is_the_raw_response(self):
        self.assertEqual(sum(bin(x).count('1') for x in K), 18085)
        self.assertEqual(E.response(K, cm((444, 470))), [])                          # the #1179 kernel pair
        self.assertEqual([v + t for t in E.response(K, cm((578,)))], [113, 118, 150, 153, 192, 197, 214, 219])

    def test_engine2_agrees_on_K_and_spans(self):
        rep = F.replay_sets(P)
        geo = F.Geometry(P)
        self.assertEqual(rep['K'], K)
        self.assertTrue(all(F.same_span(a, b) for a, b in zip(WF, F.W_fav(P, rep, geo))))
        self.assertTrue(all(F.same_span(a, b) for a, b in zip(WA, F.W_A6(P, rep, geo))))


class Census(unittest.TestCase):
    def test_lc_fav_admits_only_the_kernel_pair_and_the_triple(self):
        self.assertEqual(E.census(W, K, WF, SUP), [((444, 470), 0), ((444, 470, 578), 8)])

    def test_a6_admits_only_the_kernel_pair(self):
        self.assertEqual(E.census(W, K, WA, SUP), [((444, 470), 0)])

    def test_no_single_helper_in_any_class(self):
        for X in (WF, WA):
            self.assertFalse([s for s, _ in E.census(W, K, X, SUP) if len(s) == 1])

    def test_dimension_bounds(self):
        self.assertEqual(max(len(x) for x in WF), 5)
        self.assertEqual(max(len(x) for x in WA), 4)

    def test_a6_inside_lc_fav(self):
        self.assertTrue(all(F.same_span(list(a) + list(b), list(b)) for a, b in zip(WA, WF)))

    def test_relaxation_is_a_superset_and_has_one_nonzero_class(self):
        rel = E.relax(W, K, WF, CL['elig'])
        self.assertEqual(len(rel), 1)
        (V0, d), = rel.items()
        self.assertEqual(len(V0), 1)
        self.assertEqual(sorted(map(tuple, d['kernel'])), [(444, 470), (578,)])
        span = E.Span()
        for kv in d['kernel']:
            span.add(cm(kv))
        for S, _ in E.census(W, K, WF, SUP):            # every LC-fav admission lies in the relaxed kernel
            self.assertTrue(set(S) <= set(CL['elig'][V0]))
            self.assertFalse(span.add(cm(S)))

    def test_result_records_the_same_census(self):
        self.assertEqual(RESULT['summary']['LC_fav_late'], [[444, 470, 578]])
        self.assertEqual(RESULT['summary']['A6_late'], [])
        self.assertEqual(RESULT['summary']['singles_admitted'], 0)
        self.assertEqual(RESULT['summary']['source_donors_late'], 0)


class Controls(unittest.TestCase):
    def test_sanity_pre_a_window_admits_everything(self):
        allj = [1 << j for j in range(W.R)]
        self.assertEqual(len(E.census(W, K, [list(x) + allj for x in WF], SUP)), len(SUP))

    def test_flipped_K_bit_rejects_the_kernel_pair(self):
        Kf = list(K)
        Kf[1] ^= 1 << (470 - 2 * v)
        self.assertEqual(E.census(W, Kf, WF, [frozenset((444, 470))]), [])

    def test_sanity_cleared_K_column_admits_578(self):
        K0 = [x & ~(1 << (578 - 2 * v)) for x in K]
        self.assertEqual(E.census(W, K0, WF, [frozenset((578,))]), [((578,), 0)])

    def test_relaxed_carrier_frame_admits_the_triple_in_a6(self):
        full = next(i for i, f in enumerate(P['frames']) if len(f) == v)
        Wrel = E.W_sweep(W, ST, 'A6', next_override={77: full})
        self.assertEqual(E.census(W, K, Wrel, [frozenset((444, 470, 578))]), [((444, 470, 578), 8)])

    def test_dropping_a_reader_breaks_the_admission(self):
        # remove every snapshot and carrier contribution to target 150's LC-fav space: the triple is rejected
        Wcut = [x if v + t != 150 else [] for t, x in enumerate(WF)]
        self.assertEqual(E.census(W, K, Wcut, [frozenset((444, 470, 578))]), [])

    def test_synthetic_witness_replays(self):
        wlib = V.load_wlib()
        S, Wt = V.synthetic(P)
        self.assertEqual((V.canonical_sha(S), V.canonical_sha(Wt)), (V.SYN_SHA, V.WITNESS_SHA))
        wlib.replay(Wt)
        no_late = copy.deepcopy(Wt)
        no_late['B'] = S['B']                          # without its three post-scatter reads
        with self.assertRaises(AssertionError):
            wlib.replay(no_late)
        bad = copy.deepcopy(Wt)
        bad['C'] = bad['C'][:-1]                       # drop the closing shear: the witness must break
        with self.assertRaises(AssertionError):
            wlib.replay(bad)

    def test_frame_closure_detects_a_dropped_label(self):
        bad = copy.deepcopy(P)
        f = next(i for i, fr in enumerate(bad['frames']) if len(fr) >= 3)
        bad['frames'][f] = bad['frames'][f][1:]
        self.assertNotEqual(F.Geometry(bad).closed(f, v), bad['frames'][f])

    def test_recorded_a6r_status(self):
        trip = RESULT['words']['PR589']['late_survivors']['444,470,578']
        self.assertEqual(trip['T'], [113, 118, 150, 153, 192, 197, 214, 219])
        self.assertEqual(trip['A6_covered'], [150, 197])
        self.assertEqual(trip['A6R_T_only_covered'], [150, 153, 192, 197])
        self.assertEqual(trip['A6R_covered'], trip['T'])
        self.assertEqual(RESULT['summary']['triple_status'], 'OPEN')


if __name__ == '__main__':
    unittest.main()
