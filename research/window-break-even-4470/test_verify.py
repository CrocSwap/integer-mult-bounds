#!/usr/bin/env python3
"""Rejecting and positive controls for verify.py (fast subset)."""
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v  # noqa: E402

S = v.bind()


def exact(src, **kw):
    args = dict(V=112, d=8, cjobs=src['centre_jobs'], crank=8, p=src['pairs'], a=src['prefix'])
    args.update(kw)
    return v.invoice(src, args['V'], args['d'], args['cjobs'], args['crank'], args['p'], args['a'], exact=True)


def as_int(c):
    return {r: int(m) for r, m in c.items() if m}


class Controls(unittest.TestCase):
    def test_reproduces_4470(self):
        T, P = exact(S)
        self.assertEqual(as_int(T), S['targets'])
        self.assertEqual(as_int(P), S['paid'])

    def test_changed_helper_count_rejected(self):
        bad = dict(S); bad['H'] = dict(S['H']); bad['H'][9] += 1
        self.assertNotEqual(as_int(exact(bad)[0]), S['targets'])

    def test_dropped_centre_rejected(self):
        self.assertNotEqual(as_int(exact(S, cjobs=0)[1]), S['paid'])

    def test_wrong_pair_count_rejected(self):
        self.assertNotEqual(as_int(exact(S, p=S['pairs'] + 1)[0]), S['targets'])

    def test_no_surplus_no_saving(self):
        # D6-like tie unit (v = D = 30, T = 6, k = 6): S = -V < 0 for every controller
        for p in (4, 16, 30):
            self.assertEqual(v.root(*v.invoice(S, 24, 4, 6, 24 / 6, p, p // 2)), 0.0)

    def test_saving_increases_with_lines_per_dimension(self):
        a = v.root(*v.invoice(S, 9 * 8 - 8, 6, 8, (56 - 8) / 8, 20, 9))
        b = v.root(*v.invoice(S, 11 * 8 - 8, 6, 8, (56 - 8) / 8, 20, 9))
        self.assertLess(a, b)

    def test_theorem_b_caps(self):
        self.assertEqual([v.cap(h) for h in range(3, 10)], [3, 4, 5, 8, 9, 16, 17])

    def test_root_matches_linearisation(self):
        T, P = v.invoice(S, 112, 8, 8, 8, 16, 7)
        surplus = sum(r * m for r, m in T.items()) - sum(r * m for r, m in P.items())
        G = sum(m * r * __import__('math').log(r) for r, m in T.items()) - \
            sum(m * r * __import__('math').log(r) for r, m in P.items())
        self.assertAlmostEqual(surplus, 752, places=6)
        self.assertLess(abs(v.root(T, P) - surplus / G), 3e-5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
