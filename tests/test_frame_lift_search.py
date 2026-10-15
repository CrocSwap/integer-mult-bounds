"""Frame-lattice model of research/frame-lift-search on the in-repository #571 prefix word.

Checks the two facts the optimality search relies on: the model's climb census equals the native paid profile,
and every feasible assignment (here the input) lies between the least and greatest solutions, both of which are
themselves accepted by the climb census.
"""
import gzip, json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research/frame-lift-search'))
import frame_lift as L  # noqa: E402
from least import least  # noqa: E402

WORD = ROOT / 'research/complex-pr615-ceiling/vendor/structural_gain/frontier-composition/combined-prefix-word/FULL-WORD.json.gz'


class FrameLattice(unittest.TestCase):
    def test_least_input_greatest(self):
        word = json.load(gzip.open(WORD))
        prof = L.profile(word)
        self.assertEqual({str(k): n for k, n in sorted(prof.items())}, word['report']['local_profile'])
        ch = L.chains(word); G, orig = L.greatest(word); lo, _ = least(word, ch, len(orig))
        self.assertTrue(all(a & ~b == 0 for a, b in zip(lo, orig)))
        self.assertTrue(all(a & ~b == 0 for a, b in zip(orig, G)))
        mass = sum(r * n for r, n in prof.items())
        for X in (lo, G):   # both extremes are admissible chains with the same rank mass
            p = L.profile(word, X)
            self.assertEqual(sum(r * n for r, n in p.items()), mass)

    def test_overpromotion_rejected(self):
        word = json.load(gzip.open(WORD))
        G, orig = L.greatest(word)
        i = next(g for g, (a, b) in enumerate(zip(orig, G)) if a != b)
        bad = list(G); bad[i] = L.FULLMASK
        with self.assertRaises(AssertionError):
            L.profile(word, bad)


if __name__ == '__main__':
    unittest.main()
