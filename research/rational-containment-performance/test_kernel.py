"""Independent Fraction elimination, complete small domains, and faulty kernels."""
import argparse
from fractions import Fraction
from itertools import product
import json
from math import gcd, lcm
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from kernel import Containment


def rational_basis(matrix):
    """Independent normalized Fraction Gaussian elimination; no production import."""
    rows = [list(map(Fraction, row)) for row in matrix]
    rank = 0
    for col in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        divisor = rows[rank][col]
        rows[rank] = [value / divisor for value in rows[rank]]
        for i in range(len(rows)):
            if i != rank:
                multiplier = rows[i][col]
                rows[i] = [a - multiplier * b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rows[:rank]


def integer_basis(matrix):
    answer = []
    for row in rational_basis(matrix):
        scale = lcm(*(value.denominator for value in row))
        entries = tuple(int(value * scale) for value in row)
        divisor = gcd(*entries)
        answer.append(tuple(value // divisor for value in entries))
    return tuple(answer)


class KernelTests(unittest.TestCase):
    def setUp(self):
        self.contains = Containment()

    def test_coordinate_lattice(self):
        # Every pair of coordinate subspaces through dimension six: 5460 pairs.
        for width in range(1, 7):
            spaces = [tuple(tuple(int(i == j) for i in range(width))
                            for j in range(width) if mask >> j & 1)
                      for mask in range(1 << width)]
            for a, source in enumerate(spaces):
                for b, target in enumerate(spaces):
                    self.assertEqual(self.contains(source, target), a & b == a)

    def test_all_binary_two_by_three_presentations(self):
        # 64 source presentations x 64 target presentations, including dependencies.
        matrices = [tuple((bits[:3], bits[3:])) for bits in product((0, 1), repeat=6)]
        targets = [(integer_basis(matrix), len(rational_basis(matrix))) for matrix in matrices]
        for source in matrices:
            for target, rank in targets:
                expected = len(rational_basis(source + target)) == rank
                self.assertEqual(self.contains(source, target), expected)

    def test_seed88_signed_frames(self):
        rng = random.Random(88)
        for width in range(1, 13):
            for trial in range(24):
                rows = tuple(tuple(rng.randrange(-4, 5) for _ in range(width))
                             for _ in range(rng.randrange(width + 3)))
                target = integer_basis(rows)
                if trial % 2:
                    source = tuple(tuple(sum(rng.randrange(-3, 4) * row[j] for row in target)
                                         for j in range(width)) for _ in range(3))
                else:
                    # Positive combinations use a common coefficient across coordinates.
                    coefficients = [[rng.randrange(-3, 4) for _ in target] for _ in range(3)]
                    source = tuple(tuple(sum(c * row[j] for c, row in zip(cs, target))
                                         for j in range(width)) for cs in coefficients)
                expected = len(rational_basis(source + target)) == len(target)
                self.assertEqual(self.contains(source, target), expected)

    def test_nonunit_pivots_and_large_integers(self):
        for a, b in ((2, 3), (2**127 - 1, 2**61 - 1)):
            target = ((a, 0, 1), (0, b, 1))
            self.assertTrue(self.contains(((a, b, 2),), target))
            self.assertFalse(self.contains(((a, b, 1),), target))
        self.assertTrue(self.contains(((0, 6, 2, 10),), ((0, 3, 1, 5),)))
        self.assertFalse(self.contains(((1, 6, 2, 10),), ((0, 3, 1, 5),)))

    def test_noncanonical_targets_preserve_reference_semantics(self):
        for target in (((2, 2),), ((-1, -1),), ((0, 0),),
                       ((0, 1), (1, 0)), ((1, 1), (0, 1)), ((1, 0), (1, 0))):
            self.assertFalse(self.contains((), target))
            self.assertFalse(self.contains(target, target))

    def test_empty_full_zero_and_dependent_sources(self):
        self.assertTrue(self.contains((), ()))
        self.assertTrue(self.contains(((),), ()))
        self.assertTrue(self.contains(((0, 0), (0, 0)), ()))
        self.assertFalse(self.contains(((0, 1),), ()))
        self.assertTrue(self.contains(((2, 4), (1, 2), (0, 0)), ((1, 2),)))
        self.assertTrue(self.contains(((7, -11),), ((1, 0), (0, 1))))
        self.assertFalse(self.contains(((1, 0),), ((0, 1),)))

    def test_cache_keys_eviction_and_no_mutable_results(self):
        contains = Containment(capacity=1)
        a, b = ((1, 1),), ((1, -1),)
        self.assertTrue(contains(a, a))
        self.assertFalse(contains(a, b))
        self.assertTrue(contains(a, a))
        info = contains.cache_info()
        self.assertEqual((info.currsize, info.misses), (1, 3))
        self.assertTrue(contains(a, a))
        self.assertEqual(contains.cache_info().hits, 1)
        contains.cache_clear()
        self.assertEqual(contains.cache_info().currsize, 0)
        self.assertTrue(Containment(capacity=0)(a, a))

    def test_malformed_inputs_fail_even_after_cache_hit(self):
        self.assertTrue(self.contains(((1, 0),), ((1, 0),)))
        for source, target in (([[1, 0]], ((1, 0),)), (((1.0, 0),), ((1, 0),)),
                               (((1, 0),), ((True, 0),)), (((1, 0),), ((1.0, 0),))):
            with self.assertRaises(TypeError):
                self.contains(source, target)
        for source, target in ((((1,),), ((1, 0),)), (((1,), (1, 0)), ()),
                               ((), ((1,), (0, 1)))):
            with self.assertRaises(ValueError):
                self.contains(source, target)
        for capacity in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                Containment(capacity)


def mutation_checks():
    source = (PACKAGE / 'kernel.py').read_text()
    mutations = {
        'drop_all_equations': ('return tuple(checks)', 'return ()'),
        'reverse_annihilator_sign': ('-row[free] * (scale // row[p])', 'row[free] * (scale // row[p])'),
        'omit_pivot_denominator': ('(scale // row[p])', 'scale'),
        'accept_noncanonical_target': ('if equations is None:\n', 'if equations is None:\n            return True\n'),
    }
    receipts = {}
    with tempfile.TemporaryDirectory(prefix='containment-mutants-') as temporary:
        folder = Path(temporary)
        (folder / 'test_kernel.py').write_bytes((PACKAGE / 'test_kernel.py').read_bytes())
        for name, (before, after) in mutations.items():
            if source.count(before) != 1:
                raise RuntimeError('Mutation target drift: ' + name)
            (folder / 'kernel.py').write_text(source.replace(before, after))
            result = subprocess.run([sys.executable, '-I', '-B', str(folder / 'test_kernel.py')],
                                    capture_output=True, text=True, timeout=120)
            receipt = json.loads(result.stdout.strip().splitlines()[-1])
            if result.returncode != 1 or receipt['failures'] == 0 or receipt['errors']:
                raise RuntimeError('Mutation did not fail arithmetically: ' + name + result.stderr)
            receipts[name] = receipt
    return receipts


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mutations', action='store_true')
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(KernelTests))
    receipt = dict(tests=result.testsRun, failures=len(result.failures), errors=len(result.errors))
    if result.wasSuccessful() and args.mutations:
        receipt['mutations'] = mutation_checks()
    print(json.dumps(receipt, sort_keys=True))
    sys.exit(0 if result.wasSuccessful() else 1)
