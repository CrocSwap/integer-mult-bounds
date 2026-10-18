"""Independent full Cartesian enumeration versus degree-pruned traversal."""
from itertools import product
from math import comb
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from experiments import signed_sparse_core as core


def cartesian_terms(h, q):
    for choices in product(range(4), repeat=h):
        r = choices.count(1)
        s = choices.count(2) + choices.count(3)
        if r + 2*s > q-1 or comb(q-1-r-s, s) % 2 == 0:
            continue
        masks = [sum(1 << i for i, c in enumerate(choices) if c in kinds)
                 for kinds in ((1, 3), (2,), (1, 2), (3,))]
        yield (masks[0], masks[1]), (masks[2], masks[3])


class SignedSparseEnumeration(unittest.TestCase):
    def test_every_admissible_small_stream_in_order(self):
        for q in (2, 4, 8):
            for h in range(q, 9):
                with self.subTest(h=h, q=q):
                    self.assertEqual(list(core.coefficient_terms(h, q)),
                                     list(cartesian_terms(h, q)))

    def test_expansion_budget_still_rejected(self):
        with self.assertRaises(Exception):
            list(core.coefficient_terms(9, 2))

    def test_missing_mixed_term_breaks_factor_identity(self):
        terms = list(core.coefficient_terms(4, 4))
        # Delete an np term with a nonzero negative-indicator evaluation.
        index = next(i for i, (x, y) in enumerate(terms) if x[1] == 2)
        del terms[index]
        with patch.object(core, 'coefficient_terms', return_value=iter(terms)):
            with self.assertRaisesRegex(Exception, 'factor identity failed'):
                core.expand_factor(4, 4)

    def test_duplicated_constant_breaks_factor_identity(self):
        terms = list(core.coefficient_terms(4, 4))
        terms.append(terms[0])  # Cancels the constant in characteristic two.
        with patch.object(core, 'coefficient_terms', return_value=iter(terms)):
            with self.assertRaisesRegex(Exception, 'factor identity failed'):
                core.expand_factor(4, 4)


if __name__ == '__main__':
    unittest.main()
