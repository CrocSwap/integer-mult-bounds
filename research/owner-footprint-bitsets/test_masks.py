"""Exact-set oracle and actual-source mutation tests; stdlib only."""
import importlib.util
import itertools
from pathlib import Path
import random
import unittest

sp = importlib.util.spec_from_file_location('adapter', Path(__file__).with_name('adapter.py'))
A = importlib.util.module_from_spec(sp)
sp.loader.exec_module(A)


def oracle(interval_mask, is_prefix):
    count = 0
    # Every subset of [0,n), n<=8, against every legal interval in [0,n).
    # The reference uses Python sets; it never uses the bit-mask predicates.
    for n in range(9):
        for bits in itertools.product((False, True), repeat=n):
            cells = {i for i, bit in enumerate(bits) if bit}
            encoded = sum(2 ** i for i in cells)
            if is_prefix(encoded) != (cells == set(range(len(cells)))):
                raise AssertionError('prefix oracle')
            for start in range(n + 1):
                for width in range(n - start + 1):
                    interval = set(range(start, start + width))
                    mask = interval_mask(start, width)
                    if mask != sum(2 ** i for i in interval):
                        raise AssertionError('interval oracle')
                    if bool(encoded & mask) != bool(cells & interval):
                        raise AssertionError('overlap oracle')
                    joined = encoded | mask
                    if joined.bit_count() != len(cells | interval):
                        raise AssertionError('cardinality oracle')
                    if is_prefix(joined) != (cells | interval == set(range(len(cells | interval)))):
                        raise AssertionError('union prefix oracle')
                    count += 1
    return count


class Masks(unittest.TestCase):
    def test_exhaustive_small_domain(self):
        self.assertEqual(oracle(A.interval_mask, A.is_prefix), 18943)

    def test_seeded_large_domain(self):
        rng = random.Random(91)
        for _ in range(2000):
            cap = rng.randrange(4097)
            cells = set(rng.sample(range(cap), rng.randrange(min(cap, 200) + 1)))
            start = rng.randrange(cap + 1)
            width = rng.randrange(cap - start + 1)
            old = sum(2 ** i for i in cells)
            interval = set(range(start, start + width))
            mask = A.interval_mask(start, width)
            self.assertEqual(mask, sum(2 ** i for i in interval))
            self.assertEqual(bool(old & mask), bool(cells & interval))
            joined = old | mask
            self.assertEqual(joined.bit_count(), len(cells | interval))
            self.assertEqual(A.is_prefix(joined), cells | interval == set(range(len(cells | interval))))

    def test_large_sparse_and_empty_boundaries(self):
        for end in (0, 1, 31, 32, 48, 63, 64, 65, 1024, 8192):
            self.assertEqual(A.interval_mask(end, 0), 0)
            self.assertTrue(A.is_prefix(A.interval_mask(0, end)))
            if end:
                self.assertFalse(A.is_prefix(A.interval_mask(1, end)))
                self.assertEqual(A.interval_mask(end, 1).bit_count(), 1)
        # Equal cardinality does not imply equal occupied cells or a prefix.
        self.assertFalse(A.is_prefix(sum(2 ** i for i in (0, 1, 3, 4))))

    def test_actual_kernel_mutants_are_detected(self):
        source = (A.HERE / 'adapter.py').read_text()
        mutations = [
            ('((1 << width) - 1) << offset', '((1 << width) - 1)'),
            ('((1 << width) - 1) << offset', '(1 << width) << offset'),
            ('((1 << width) - 1) << offset', '((1 << width) - 1) << (offset + 1)'),
            ('mask & (mask + 1) == 0', 'True'),
            ('mask & (mask + 1) == 0', 'mask == 0'),
        ]
        for old, new in mutations:
            self.assertEqual(source.count(old), 1)
            ns = {'__name__': 'mutant', '__file__': str(A.HERE / 'adapter.py')}
            exec(compile(source.replace(old, new), '<mutated-adapter>', 'exec'), ns)
            with self.assertRaises(AssertionError, msg=new):
                oracle(ns['interval_mask'], ns['is_prefix'])

    def test_pins_and_counted_source_substitution(self):
        A.check_pins()
        source = (A.ROOT / A.CHECKER).read_text()
        result = A.transformed(source)
        for old, new in A.REPLACEMENTS:
            self.assertEqual(result.count(new), 1)
            with self.assertRaisesRegex(ValueError, 'anchor changed'):
                A.transformed(source.replace(old, ''))
            with self.assertRaisesRegex(ValueError, 'anchor changed'):
                A.transformed(source + old)
        self.assertEqual(result.count('need('), source.count('need('))


if __name__ == '__main__':
    unittest.main()
