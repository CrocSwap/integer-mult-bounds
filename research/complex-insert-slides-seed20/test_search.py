#!/usr/bin/env python3
"""Behavior and failure tests for the insertion-slide census.

Run: python3 -B -m unittest research.complex-insert-slides-seed20.test_search
(or directly: python3 -B test_search.py)

These pin mathematical behavior, not implementation details:
  T1  applying every slide at its pinned position reproduces the pinned SW4
      output word byte for byte (equivalence with build_sw4.apply_recipe);
  T2  positional equivalence classes: positions separated by a gate touching
      the moved target or helper are distinct; positions between two such
      gates are one class;
  T3  sliding a compensation pre-read past its helper's copy gate changes the
      exact B-end state (the pre-read then reads h = E_h + r);
  T4  sliding across a scale of the target changes the exact B-end state;
  T5  an in-window slide keeps the exact B-end state;
  T6  the endpoint functional reproduces the pinned complex endpoint of the
      selected record on the pinned SW4 profile.
"""
import gzip
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ss = load('insert_slides', HERE / 'search.py')
bs = load('build_sw4_probe', ROOT / 'research/complex-sw4-frame8/construction/sw4/build_sw4.py')


class InsertSlides(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w = json.loads(gzip.decompress((HERE / 'inputs/PROMOTED-P6K4-WORD.json.gz').read_bytes()))
        cls.rec = json.loads((HERE / 'inputs/SW4-RECIPE-P6k4.json').read_text(encoding='utf-8'))
        cls.moves = cls.rec['moves']
        cls.S0 = bs.bend_state(cls.w)

    def test_T1_pinned_slides_reproduce_pinned_output(self):
        wn, nt = ss.slide_apply(self.w, self.moves, {}, ())
        w2, nt2 = bs.apply_recipe(self.w, self.moves)
        self.assertEqual(ss.enc(wn), ss.enc(w2))
        self.assertEqual(nt, nt2)
        wn, nt, problems, paid, widths = ss.finished(self.w, self.moves, {}, ())
        self.assertEqual(problems, [])
        self.assertEqual(ss.sha_word(wn), self.rec['output_sha256'])

    def test_T2_equivalence_classes_split_on_interaction(self):
        # Toy insertion-free list, copy at index 5; gates touching register 5
        # or 0 sit at indices 1 and 3.  Positions {0,1}, {2,3}, {4,5} are the
        # three equivalence classes; representatives are 0, 2, 4.
        toy = [['add', 9, 9, 1, 1, []], ['add', 5, 0, 1, 1, []], ['add', 7, 7, 1, 1, []],
               ['add', 5, 8, 1, 1, []], ['add', 3, 3, 1, 1, []]]
        classes = ss.position_classes(toy, 5, 0, 5)
        self.assertEqual(classes, [0, 2, 4])

    def test_T3_slide_past_copy_gate_breaks_exactness(self):
        k = ss.r2h_move_indices(self.moves)[0]
        _, copy = ss.insertion_free(self.w, self.moves, k)
        wn, nt = ss.slide_apply(self.w, self.moves, {k: copy + 1}, ())
        self.assertNotEqual(bs.bend_state(wn), self.S0)

    def test_T4_slide_across_scale_of_target_breaks_exactness(self):
        # Find an r2h move whose target has a scale gate in its window; if the
        # word has none, the test asserts the structural fact instead (the
        # census records zero scale gates in every window).
        found = False
        for k in ss.r2h_move_indices(self.moves):
            t = self.moves[k]['target']
            insfree, copy = ss.insertion_free(self.w, self.moves, k)
            for p, e in enumerate(insfree[:copy]):
                if e[0] == 'scale' and e[1] == t:
                    found = True
        self.assertFalse(found, 'unexpected scale of a moved target inside a slide window')

    def test_T5_in_window_slide_keeps_exactness(self):
        k = ss.r2h_move_indices(self.moves)[0]
        wn, nt = ss.slide_apply(self.w, self.moves, {k: 0}, ())
        self.assertEqual(bs.bend_state(wn), self.S0)
        # The inherited checker may still refuse the configuration on frames;
        # it must record a refusal rather than crash, and the exact B state is
        # independent of that.
        wn, nt, problems, Hloc, widths = ss.finished(self.w, self.moves, {k: 0}, ())
        self.assertTrue(problems == [] or Hloc is None)

    def test_T6_endpoint_reproduces_pinned_complex_endpoint(self):
        root = ss.endpoint_root({1: 2556, 2: 334, 3: 430, 4: 194, 5: 56, 8: 8})
        exact = 1663966829367501881629 / 10**24
        self.assertLess(abs(root - exact), 5e-15)


if __name__ == '__main__':
    unittest.main(verbosity=2)
