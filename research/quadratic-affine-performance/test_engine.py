"""Differential and negative-control tests for the batched row engine.

Every row of every small fixture is compared against the verbatim base-commit
reference (`inner` per pair, `sum(1<<j ...)` row construction). The heavy
fixture is subsampled here for test runtime; benchmark.py compares it in full.
Run: python3 -B -m unittest discover -s research/quadratic-affine-performance -p 'test_engine.py' -v
"""
import json
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from experiments.quadratic_affine import (family, vector, inner, rank_witness,
                                          _orthogonality_rows, _lane_flags, _gather_lanes)
from reference import reference_rows, rank_witness_reference

FIXTURES = json.loads((ROOT / 'scripts/experiments/quadratic_affine_witnesses.json').read_text())


def brute_gather(flags, lanes):
    return sum(1 << k for k in range(lanes) if (flags >> (8 * k + 7)) & 1)


class Primitives(unittest.TestCase):
    def test_gather_matches_brute_force(self):
        rng = random.Random(1234)
        for lanes in (1, 2, 3, 7, 8, 9, 63, 64, 65, 200, 300):
            for pattern in ('random', 'all', 'single'):
                flags = 0
                for k in range(lanes):
                    if pattern == 'all' or (pattern == 'single' and k == lanes - 1) or rng.random() < 0.5:
                        flags |= 1 << (8 * k + 7)
                self.assertEqual(_gather_lanes(flags, lanes), brute_gather(flags, lanes),
                                 (lanes, pattern))

    def test_lane_flags_match_brute_force_with_borrow_chains(self):
        rng = random.Random(99)
        for trial in range(400):
            lanes = rng.randint(1, 150)
            vals = [2 * rng.randint(0, 32) for _ in range(lanes)]
            if trial % 2 == 0:  # long zero runs force borrow chains through many lanes
                vals = [0 if rng.random() < 0.85 else 2 * rng.randint(1, 32) for _ in range(lanes)]
            x = 0
            for k, v in enumerate(vals):
                x |= v << (8 * k)
            want = sum(1 << (8 * k + 7) for k in range(lanes) if vals[k] == 0)
            self.assertEqual(_lane_flags(x, lanes), want, vals[:20])

    def test_odd_lanes_break_the_swar_test(self):
        """Negative control: without pre-doubled (even) lanes the SWAR zero
        test false-flags a value-1 lane behind a zero run; that is why the
        masks hold doubled counts."""
        lanes = 4
        vals = [0, 0, 1, 0]  # lane 2 = 1 sits behind two zero lanes
        x = 0
        for k, v in enumerate(vals):
            x |= v << (8 * k)
        naive = sum(1 << (8 * k + 7) for k in range(lanes) if (x - int.from_bytes(b'\x01' * lanes, 'little')
                     & ~x & int.from_bytes(b'\x80' * lanes, 'little')) >> (8 * k + 7) & 1)
        self.assertNotEqual(naive, sum(1 << (8 * k + 7) for k in range(lanes) if vals[k] == 0),
                            'odd-lane adversary should mis-flag; control would be vacuous')


class RowsAgainstReference(unittest.TestCase):
    def test_every_row_of_small_and_medium_fixtures(self):
        for index in range(11):
            w = FIXTURES[index]
            f = family(w['t'], w['complex_phases'], w['parity'])
            vectors = [vector(f, i) for i in w['sample']]
            rows = _orthogonality_rows(vectors, f['D'], w['independent_rows'])
            self.assertEqual(rows, reference_rows(vectors, w['independent_rows']),
                             'fixture %d rows differ from the reference engine' % index)

    def test_heavy_fixture_rows_subsampled(self):
        w = FIXTURES[11]
        f = family(w['t'], w['complex_phases'], w['parity'])
        vectors = [vector(f, i) for i in w['sample']]
        chosen = w['independent_rows'][::211]
        rows = _orthogonality_rows(vectors, f['D'], chosen)
        self.assertEqual(rows, reference_rows(vectors, chosen))

    def test_random_samples_small_families(self):
        rng = random.Random(7)
        for t, complex_phases, parity in ((2, True, None), (3, False, 0), (3, False, 1),
                                          (3, True, None), (4, False, None)):
            f = family(t, complex_phases, parity)
            for _ in range(4):
                sample = rng.sample(range(f['n']), min(f['n'], 40))
                chosen = rng.sample(range(len(sample)), min(len(sample), 12))
                vectors = [vector(f, i) for i in sample]
                self.assertEqual(_orthogonality_rows(vectors, f['D'], chosen),
                                 reference_rows(vectors, chosen))

    def test_rank_witness_matches_reference(self):
        for index in range(11):
            w = FIXTURES[index]
            self.assertEqual(rank_witness(**w), rank_witness_reference(**w), 'fixture %d' % index)

    def test_row_corruption_changes_digest(self):
        """Negative control: a one-bit row change must change the recorded
        digest, so the byte-identical digests in the certificate are evidence."""
        w = dict(t=3, complex_phases=False, parity=None, sample=FIXTURES[2]['sample'],
                 independent_rows=FIXTURES[2]['independent_rows'])
        good = rank_witness(**w)
        f = family(w['t'], w['complex_phases'], w['parity'])
        vectors = [vector(f, i) for i in w['sample']]
        rows = _orthogonality_rows(vectors, f['D'], w['independent_rows'])
        rows[w['independent_rows'][0]] ^= 1  # flip one column bit
        from hashlib import sha256
        bytewidth = (len(w['sample']) + 7) // 8
        digest = sha256()
        for i in w['independent_rows']:
            digest.update(rows[i].to_bytes(bytewidth, 'little'))
        self.assertNotEqual(digest.hexdigest(), good['independent_row_sha256'])

    def test_broken_gather_is_detected(self):
        """Negative control: dropping a gather stage must be caught by the
        same row comparison the benchmark uses."""
        w = FIXTURES[5]
        f = family(w['t'], w['complex_phases'], w['parity'])
        vectors = [vector(f, i) for i in w['sample']]
        good = _orthogonality_rows(vectors, f['D'], w['independent_rows'])
        broken = {}
        for i in w['independent_rows']:
            s, lo, hi = vectors[i]
            broken[i] = (good[i] ^ (1 << i)) & ~1  # emulate a dropped final gather stage
        self.assertNotEqual(broken, reference_rows(vectors, w['independent_rows']))


class RejectionsPreserved(unittest.TestCase):
    def test_reference_and_shipped_reject_identically(self):
        for call in (dict(t=1, complex_phases=False, parity=None, sample=[0, 0], independent_rows=[0]),
                     dict(t=1, complex_phases=False, parity=None, sample=[0, 1], independent_rows=[0, 0]),
                     dict(t=1, complex_phases=False, parity=None, sample=[0, 1], independent_rows=[2]),
                     dict(t=1, complex_phases=False, parity=None, sample=[0, 4], independent_rows=[0])):
            with self.assertRaises(ValueError):
                rank_witness(**call)
            with self.assertRaises(ValueError):
                rank_witness_reference(**call)

    def test_dependent_rows_still_fail(self):
        """The claimed-independence rejection fires on a crafted dependent
        row set, proving failure detection is intact through the new path."""
        import experiments.quadratic_affine as qa
        original = qa._orthogonality_rows
        try:
            qa._orthogonality_rows = lambda vectors, D, indices: {0: 0b001, 1: 0b010, 2: 0b011}
            with self.assertRaises(ValueError):
                qa.rank_witness(1, False, None, [0, 1, 2, 3], [0, 1, 2])
        finally:
            qa._orthogonality_rows = original


if __name__ == '__main__':
    unittest.main()
