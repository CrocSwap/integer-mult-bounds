"""Contact failure controls. Prepared with substantial OpenAI Codex assistance."""
import copy
import unittest
from audit import audit, core, embed, phase

class Contacts(unittest.TestCase):
    def test_coordinate_port(self):
        maps = core(1, [1 << i for i in range(1, 9)])
        self.assertEqual(len(maps), 4)
        # A coordinate permutation preserves weight: exit translations vanish.
        self.assertEqual(maps[2], {'translation': 0, 'inverse_translation': 0})

    def test_bad_basis(self):
        for basis in ([1 << i for i in range(8)], [2]*8, [1 << i for i in range(1, 8)],
                      [1 << i for i in range(1, 8)] + [1 << 9]):
            with self.subTest(basis=basis), self.assertRaises(ValueError):
                core(1, basis)
        for q in (0, 3, 512):
            with self.assertRaises(ValueError):
                core(q, [1 << i for i in range(1, 9)])

    def test_stage_embedding(self):
        for s in range(1, 20):
            self.assertEqual(embed(1 | (1 << 9), s), 1 | (1 << (9+8*(s-1))))
        self.assertNotEqual(embed(1 << 9, 1), embed(1 << 9, 19))

    def test_phase_controls(self):
        terms = [(3, 1)]
        self.assertEqual(phase(terms, 3), 0)
        # Linear-only evaluation would give two; this exercises the mixed term.
        self.assertNotEqual(phase(terms, 3), 2)

    def test_wrong_caller(self):
        original = {'ambient_rank':161, 'stages':19,
                    'events':[['LOCAL', s, 0, 1] for s in range(1,20)]}
        for key, value in [('ambient_rank',160), ('stages',18), ('events',original['events'][:-1]),
                           ('events',list(reversed(original['events'])))]:
            c = copy.deepcopy(original); c[key] = value
            with self.assertRaises(ValueError): audit(c, {'recipes':[]}, [])

if __name__ == '__main__':
    unittest.main()
