#!/usr/bin/env python3
"""Regressions for literal paid incidences, negative aliases and the CI score tie."""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
from collections import Counter
import gzip
import json
from pathlib import Path
import unittest

from check import strict_word
from endpoints import load_word, original

HERE = Path(__file__).resolve().parent

class FrozenWordControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = json.loads(gzip.decompress((HERE / 'word-23.json.gz').read_bytes()))

    def changed_row(self, field, row, column, value):
        word = dict(self.word)
        word[field] = list(word[field])
        word[field][row] = list(word[field][row])
        word[field][row][column] = value
        return word

    def rejected(self, word):
        with self.assertRaises((AssertionError, KeyError)):
            strict_word(word)

    def test_both_frozen_words(self):
        for h in (23, 25):
            word = json.loads(gzip.decompress((HERE / f'word-{h}.json.gz').read_bytes()))
            self.assertEqual(strict_word(word)['scatter_incidents'], 6*word['v'])

    def test_cancelling_added_scatter_is_still_paid(self):
        word = dict(self.word)
        word['scatter'] = word['scatter'] + [word['scatter'][0], word['scatter'][0]]
        old = Counter(map(tuple, self.word['scatter']))
        new = Counter(map(tuple, word['scatter']))
        self.assertEqual({k: n % 2 for k, n in old.items()}, {k: n % 2 for k, n in new.items()})
        self.rejected(word)

    def test_negative_operation_frame_alias(self):
        g = self.word['ops'][0][2]
        bad = g-len(self.word['frames'])
        self.assertEqual(self.word['frames'][g], self.word['frames'][bad])
        self.rejected(self.changed_row('ops', 0, 2, bad))

    def test_negative_source_slot_alias(self):
        word = dict(self.word)
        word['sources'] = dict(word['sources'])
        key = next(iter(word['sources']))
        word['sources'][key] -= word['R']
        self.rejected(word)

    def test_negative_output_frame_alias(self):
        self.rejected(self.changed_row('outputs', 0, 1, self.word['outputs'][0][1]-len(self.word['frames'])))

    def test_negative_event_frame_alias(self):
        self.rejected(self.changed_row('events', 0, 2, self.word['events'][0][2]-len(self.word['frames'])))

    def test_bad_event_initial_sentinel(self):
        self.rejected(self.changed_row('events', 0, 1, -2))

    def test_repeated_initial_sentinel(self):
        i = next(i for i, (_, old, _) in enumerate(self.word['events']) if old >= 0)
        self.rejected(self.changed_row('events', i, 1, -1))

    def test_negative_scatter_alias(self):
        self.rejected(self.changed_row('scatter', 0, 0, -1))

    def test_python311_discovery_tie_has_identical_exact_cost(self):
        # CI selected entrance at this role under Python3.11; Python3.14
        # selected retirement. Floating gains differ by 2.84e-14 on3.11,
        # while these exact replacement multisets agree identically.
        word, first, last, _, _ = load_word(23)
        replacements = []
        for kind, frame in [('entrance', first[22288]), ('exit', last[22288])]:
            _, (_, removed), (_, merged) = original.evaluate((23, kind, frame, *word['frames'][frame]))
            rows = Counter(merged)
            rows.subtract(removed)
            replacements.append({t: n for t, n in rows.items() if n})
        self.assertEqual(replacements[0], replacements[1])

if __name__ == '__main__':
    unittest.main()
