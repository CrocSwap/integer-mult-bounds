"""Complete row comparisons and rejection controls for exact Gram packing."""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from experiments.single_intersection import minor_rows, verify_feature_orbit


def reference_minor_rows(labels, j):
    """Directed formula from the pinned predecessor, with no symmetry reuse."""
    return [sum(1 << b for b, T in enumerate(labels)
                if S == T or (S & T).bit_count() == j) for S in labels]


class SingleIntersectionPacking(unittest.TestCase):
    def test_regenerated_certificates_change_only_the_source_binding(self):
        root = Path(__file__).resolve().parents[1]
        source = 'scripts/experiments/single_intersection.py'
        current = hashlib.sha256((root / source).read_bytes()).hexdigest()
        for name, expected in (
            ('single-intersection.json',
             '59bca430c5cda9050b346f0f89ff980c9e610a30786cd19677911a1eb433d5b8'),
            ('affine-vector-screens.json',
             'f72787ebf4a991e32705c7fb7ef7ad559a9964b27c0f91d1b5a034c05027cfb0'),
        ):
            with self.subTest(certificate=name):
                value = json.loads((root / 'certificates' / name).read_text())
                self.assertEqual(value['source_sha256'][source], current)
                value['source_sha256'][source] = (
                    '08ddae46e5621a5b4c525b504e67ae655abe9b49461d894feaa7abc89a51847d')
                if name == 'affine-vector-screens.json':
                    # The later accepted Leech production update also changed
                    # this certificate's own helper pin. Bind that exact source
                    # before restoring its predecessor for the full payload hash.
                    companion = 'scripts/experiments/affine_vector_screens.py'
                    successor = 'c499289fc25b5d180df22f70694a7b1c4cfed68f00a9a59bbf4f7ae1b52327a9'
                    self.assertEqual(value['source_sha256'][companion], successor)
                    self.assertEqual(hashlib.sha256((root / companion).read_bytes()).hexdigest(), successor)
                    value['source_sha256'][companion] = '756778eeca27f490adc7354a122dc50c40375156259991469c47a90949118ea1'
                payload = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
                self.assertEqual(hashlib.sha256(payload).hexdigest(), expected)

    def test_all_small_subset_relations_and_permutations(self):
        rng = random.Random(86)
        for h in range(2, 8):
            for k in range(1, h + 1):
                labels = [sum(1 << a for a in points)
                          for points in combinations(range(h), k)]
                rng.shuffle(labels)
                for j in range(-1, k + 2):
                    with self.subTest(h=h, k=k, j=j):
                        self.assertEqual(minor_rows(labels, j),
                                         reference_minor_rows(labels, j))

    def test_byte_boundaries_mixed_weights_and_large_labels(self):
        rng = random.Random(86)
        for n in (0, 1, 7, 8, 9, 15, 16, 17, 63, 64, 65, 127, 128, 129):
            # High bits detect accidental truncation of the labels themselves.
            labels = [((i + 1) << 130) | rng.randrange(1, 1 << 25)
                      for i in range(n)]
            rng.shuffle(labels)
            for j in (-1, 0, 1, 7, 15, 200):
                with self.subTest(n=n, j=j):
                    rows = minor_rows(labels, j)
                    self.assertEqual(rows, reference_minor_rows(labels, j))
                    self.assertTrue(all(row >> n == 0 for row in rows))

    def test_invalid_labels_are_rejected(self):
        for labels in ([1, 1], [0], [-1], [True], [1.0], [1, 2, 1]):
            with self.subTest(labels=labels), self.assertRaises(ValueError):
                minor_rows(labels, 0)

    def test_nonclosed_and_dependent_orbit_witnesses_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'not permutation invariant'):
            verify_feature_orbit(4, 2, 1, [3])
        # These four triples sum to zero in the point-incidence features.
        with self.assertRaisesRegex(ValueError, 'Feature basis is dependent'):
            verify_feature_orbit(5, 3, 1, [7, 11, 21, 25])


if __name__ == '__main__':
    unittest.main()
