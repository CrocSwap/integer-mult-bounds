#!/usr/bin/env python3
"""Mathematical, coverage and corruption controls for the historical census.
Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('j_order', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = v.source_data(HERE)
        cls.rows = v.parse_records(cls.raw)
        cls.hist = cls.rows[0]['_hist']

    def test_transcendental_intervals_against_high_precision_decimal(self):
        with localcontext() as ctx:
            ctx.prec = 95
            for arg in (Q(1), Q(4, 3), Q(2), Q(3), Q(5), Q(19), Q(100)):
                lo, hi = v.log_interval(arg)
                exact = (Decimal(arg.numerator) / Decimal(arg.denominator)).ln()
                self.assertLessEqual(Decimal(lo) / Decimal(v.SCALE), exact)
                self.assertGreaterEqual(Decimal(hi) / Decimal(v.SCALE), exact)
            for arg in (Q(0), Q(1, 1000), Q(1, 200), Q(1, 12)):
                a, b = v.round_interval(arg, arg)
                lo, hi = v.exp_interval(a, b)
                exact = (Decimal(arg.numerator) / Decimal(arg.denominator)).exp()
                self.assertLessEqual(Decimal(lo) / Decimal(v.SCALE), exact)
                self.assertGreaterEqual(Decimal(hi) / Decimal(v.SCALE), exact)

    def test_reference_moment_consistency(self):
        # Secondary check only: the census never imports this historical engine.
        spec = importlib.util.spec_from_file_location('historical_moment', HERE / 'sources/pr315-moment.py')
        reference = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reference)
        for i in (0, 96, 760):
            row = self.rows[i]
            a = Q(row['a'])
            H, W = v.profile(row['_hist'])
            ours = v.moment_interval(row['_hist'], a)
            theirs = reference.moment(H, 100, W, a, True)
            self.assertLessEqual(Q(ours[0], v.SCALE), theirs[1])
            self.assertLessEqual(theirs[0], Q(ours[1], v.SCALE))

    def test_saved_float_scores_are_not_evidence(self):
        rows = json.loads(self.raw)
        rows[0]['J'] = 'untrusted unused score'
        rows[0]['kappa'] = None
        rows[0]['kappa_fl'] = 'untrusted unused score'
        self.assertEqual(v.reconcile(json.dumps(rows)), json.loads((HERE / 'RESULT.json').read_text()))

    def test_omitted_fallback_changes_certified_endpoint(self):
        row = self.rows[0]
        hi = Q((Q(row['a']) * v.ROOT_GRID).__floor__() + 2, v.ROOT_GRID)
        H, W = v.profile(self.hist)
        no_fallback = sum(r * n * v.power_interval(100, r, hi)[1] for r, n in H.items())
        self.assertLess(no_fallback, 100 * W * v.SCALE)
        self.assertGreater(v.moment_interval(self.hist, hi)[0], v.SCALE)

    def test_stock_floor_is_rejected(self):
        hist = dict(self.hist)
        hist[3] += 1
        with self.assertRaisesRegex(ValueError, 'nonintegral archived stock'):
            v.profile(tuple(sorted(hist.items())))

    def test_wrong_root_proposal_fails_moment_sign(self):
        bad = Q(self.rows[0]['a']) + Q(1, 1000)
        self.assertGreater(v.moment_interval(self.hist, bad)[0], v.SCALE)

    def test_prime_signature_exact_tie_control(self):
        # Two different histograms can have identical J:
        # 4 rank-1 + 1 rank-4 and 4 rank-2 both have mass 8 and J=8 log(50).
        self.assertEqual(v.j_signature(((1, 4), (4, 1))), v.j_signature(((2, 4),)))
        # Such a tie must be explicitly resolved, never silently ordered.
        interval = v.j_interval(v.j_signature(((2, 4),)))
        with self.assertRaisesRegex(ValueError, 'unresolved interval order'):
            v.order(interval, interval)

    def test_omitted_and_duplicate_records_rejected(self):
        rows = json.loads(self.raw)
        with self.assertRaisesRegex(ValueError, 'expected 761'):
            v.parse_records(json.dumps(rows[:-1]))
        rows[-1] = deepcopy(rows[0])
        with self.assertRaisesRegex(ValueError, 'record coverage'):
            v.parse_records(json.dumps(rows))

    def test_wrong_histogram_types_and_metadata_rejected(self):
        for key, value in (('mass', self.rows[0]['mass'] + 1), ('N', True), ('Wn', self.rows[0]['Wn'] - 1)):
            rows = json.loads(self.raw)
            rows[0][key] = value
            with self.assertRaises(ValueError):
                v.parse_records(json.dumps(rows))
        rows = json.loads(self.raw)
        rows[0]['hist']['1'] = True
        with self.assertRaisesRegex(ValueError, 'invalid histogram'):
            v.parse_records(json.dumps(rows))

    def test_source_corruption_and_missing_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copy(HERE / 'SOURCES.json', root)
            shutil.copytree(HERE / 'sources', root / 'sources')
            path = root / 'sources/analysis_b_summary.json'
            path.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'source digest'):
                v.source_data(root)
            path.unlink()
            with self.assertRaisesRegex(ValueError, 'source inventory'):
                v.source_data(root)

    def test_actual_counterexample_to_reported_point_nine_bound(self):
        rows = {r['name']: r for r in self.rows}
        left = v.j_interval(v.j_signature(rows['u0089']['_hist']))
        right = v.j_interval(v.j_signature(rows['u0302']['_hist']))
        self.assertGreater(Q(right[0] - left[1], v.SCALE), Q(9, 10))
        self.assertLess(Q(right[1] - left[0], v.SCALE), Q(926, 1000))


if __name__ == '__main__':
    unittest.main()
