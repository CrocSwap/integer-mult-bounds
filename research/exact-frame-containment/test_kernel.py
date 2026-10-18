"""Independent Fraction oracle and failure controls for exact containment."""
from fractions import Fraction
from itertools import product
from math import gcd, lcm
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kernel import ExactContainment


def fraction_basis(matrix):
    """Independent Gauss-Jordan elimination, normalizing pivots to one."""
    rows = [list(map(Fraction, row)) for row in matrix]
    pivot_row = 0
    for col in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(pivot_row, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        factor = rows[pivot_row][col]
        rows[pivot_row] = [x / factor for x in rows[pivot_row]]
        for i in range(len(rows)):
            if i != pivot_row:
                factor = rows[i][col]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[pivot_row])]
        pivot_row += 1
    return rows[:pivot_row]


def canonical(matrix):
    result = []
    for row in fraction_basis(matrix):
        denominator = lcm(*(x.denominator for x in row))
        ints = [int(x * denominator) for x in row]
        divisor = gcd(*ints)
        result.append(tuple(x // divisor for x in ints))
    return tuple(result)


def oracle(source, target):
    # Retain the original *representation* rule, not only abstract row spaces.
    return canonical(target) == target and len(fraction_basis(source + target)) == len(target)


def cases():
    # Every rectangular binary presentation with <=2 rows and <=3 columns,
    # crossed with every target presentation of the same width.
    for width in range(4):
        rows = list(product((0, 1), repeat=width))
        matrices = [m for count in range(3) for m in product(rows, repeat=count)]
        for source in matrices:
            for target in matrices:
                yield source, target
    rng = random.Random(90)
    for i in range(800):
        width = rng.randrange(1, 17)
        raw = tuple(tuple(rng.randrange(-4, 5) for _ in range(width))
                    for _ in range(rng.randrange(width + 3)))
        target = canonical(raw)
        source = tuple(tuple(sum(rng.randrange(-3, 4) * row[j] for row in target)
                                    for j in range(width))
                       for _ in range(rng.randrange(5)))
        # Every other generated source is constructed as actual row combinations.
        if i % 2:
            coefficients = [tuple(rng.randrange(-3, 4) for _ in target)
                            for _ in range(rng.randrange(5))]
            source = tuple(tuple(sum(c * row[j] for c, row in zip(cs, target))
                                 for j in range(width)) for cs in coefficients)
        if i % 7 == 0 and source:
            source = tuple(tuple(x * (2**257 + 1) for x in row) for row in source)
        yield source, target
        if target:
            yield source, (tuple(2 * x for x in target[0]),) + target[1:]


MUTATIONS = {
    "omit_all_free_coordinates": ("return width, tuple(equations)", "return width, ()",
                                  ((0, 1),), ((1, 0),)),
    "omit_last_free_coordinate": ("return width, tuple(equations)",
                                  "return width, tuple(equations[:-1])",
                                  ((1, 0, 1),), ((1, 0, 0),)),
    "wrong_coefficient_sign": ("row[free] * (scale // row[p])", "-row[free] * (scale // row[p])",
                               ((2, 2),), ((1, 1),)),
    "omit_pivot_denominator": ("scale // row[p]", "1",
                               ((1, 0, 1),), ((1, 0, 1), (0, 2, 1))),
    "accept_noncanonical_target": ("if prepared is None:\n            return False",
                                   "if prepared is None:\n            return True",
                                   ((1, 0),), ((2, 0),)),
}


class KernelTests(unittest.TestCase):
    def test_exhaustive_and_seeded_against_fraction_oracle(self):
        engine = ExactContainment()
        count = 0
        for source, target in cases():
            self.assertEqual(engine(source, target), oracle(source, target), (source, target))
            count += 1
        self.assertEqual(count, 7339)

    def test_target_presentation_contract(self):
        engine = ExactContainment()
        for target in (((2, 0),), ((-1, 0),), ((0, 0),),
                       ((1, 0), (1, 0)), ((0, 1), (1, 0)), ((1, 1), (0, 1))):
            self.assertFalse(engine((), target), target)
        self.assertTrue(engine(((6, 3), (0, 0), (-4, -2)), ((2, 1),)))
        self.assertTrue(engine(((0, 0),), ()))
        self.assertFalse(engine(((0, 1),), ()))
        self.assertTrue(engine((), ()))

    def test_input_shape_type_and_equal_cache_keys(self):
        engine = ExactContainment()
        self.assertTrue(engine(((1, 0),), ((1, 0),)))
        for value in (True, 1.0, Fraction(1)):
            with self.assertRaises(TypeError):
                engine(((1, 0),), ((value, 0),))
            with self.assertRaises(TypeError):
                engine(((value, 0),), ((1, 0),))
        for source, target in ((((1, 0, 0),), ((1, 0),)),
                               ((), ((1, 0), (0, 1, 0))),
                               (((0,), (0, 0)), ())):
            with self.assertRaises(ValueError):
                engine(source, target)
        for size in (-1, True, 1.0):
            with self.assertRaises(ValueError):
                ExactContainment(size)
        with self.assertRaises(TypeError):
            engine([[1, 0]], ((1, 0),))

    def test_content_cache_eviction_and_immutability(self):
        engine = ExactContainment(cache_size=3)
        for value in range(12):
            target = ((1, value),)
            self.assertTrue(engine(target, target))
            self.assertFalse(engine(((0, 1),), target))
            self.assertEqual(target, ((1, value),))
        self.assertEqual(engine.prepare.cache_info().currsize, 3)
        self.assertEqual(engine.checked_width.cache_info().currsize, 3)
        self.assertFalse(engine(((1, 1),), ((1, 0),)))
        self.assertTrue(engine(((1, 1),), ((1, 1),)))
        no_cache = ExactContainment(cache_size=0)
        self.assertTrue(no_cache(((2, 1),), ((2, 1),)))
        self.assertEqual(no_cache.prepare.cache_info().currsize, 0)

    def test_kernel_mutations(self):
        code = Path(__file__).with_name("kernel.py").read_text()
        for name, (old, new, source, target) in MUTATIONS.items():
            self.assertEqual(code.count(old), 1, name)
            namespace = {}
            exec(compile(code.replace(old, new), name, "exec"), namespace)
            actual = namespace["ExactContainment"]()(source, target)
            self.assertNotEqual(actual, oracle(source, target), name)


if __name__ == "__main__":
    unittest.main()
