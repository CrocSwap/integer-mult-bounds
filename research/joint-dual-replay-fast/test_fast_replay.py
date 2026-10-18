#!/usr/bin/env python3
"""Fast unit checks for the adapter's mask algebra and entry guards."""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')

from itertools import combinations
from pathlib import Path
import random
import subprocess
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fast_replay
from fast_replay import expected_mask, tables


def literal(triples, common, triple):
    return sum(1 << i for i, t in enumerate(triples)
               if common in t and not (set(t) & (set(triple) - {common})))


class MaskAlgebra(unittest.TestCase):
    def test_identity_on_exhaustive_small_shapes(self):
        for h in range(3, 9):
            triples, center, pair, _, _ = tables(h)
            for i, triple in enumerate(triples):
                for common in triple:
                    self.assertEqual(expected_mask(center, pair, common, list(triple)),
                                     literal(triples, common, list(triple)))
                self.assertEqual(expected_mask(center, pair, triple[0], [triple[0]]),
                                 literal(triples, triple[0], [triple[0]]))

    def test_identity_on_random_shapes_and_repeats(self):
        rng = random.Random(20261014)
        for h in (3, 5, 8, 12):
            triples, center, pair, _, _ = tables(h)
            for _ in range(200):
                common = rng.randrange(h)
                size = rng.choice((1, 3))
                pool = [x for x in range(h) if x != common]
                triple = [common] + rng.sample(pool, min(size - 1, len(pool)))
                triple = sorted(triple) if size == 3 else [common]
                if size == 3 and len(triple) != 3:
                    continue
                self.assertEqual(expected_mask(center, pair, common, triple),
                                 literal(triples, common, triple))

    def test_corrupted_table_disagrees(self):
        triples, center, pair, _, _ = tables(23)
        corrupt = [row[:] for row in pair]
        corrupt[0][1], corrupt[0][2] = corrupt[0][2], corrupt[0][1]
        self.assertTrue(any(expected_mask(center, corrupt, 0, [0, 1, 5]) !=
                            literal(triples, 0, [0, 1, 5]) for _ in (0,)))


class EntryGuards(unittest.TestCase):
    def test_shim_reexports_the_adapter(self):
        sys.path.insert(0, str(HERE / 'shim'))
        import binary_frame_replay as shim
        self.assertIs(shim.replay, fast_replay.replay)
        self.assertIs(shim.check_word, fast_replay.check_word)

    def test_optimized_interpreter_refuses(self):
        process = subprocess.run([sys.executable, '-O', str(HERE / 'fast_replay.py')],
                                 capture_output=True, text=True)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn('Assertions must remain enabled', process.stderr)


if __name__ == '__main__':
    unittest.main()
