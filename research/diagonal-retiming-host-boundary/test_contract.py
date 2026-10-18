"""Small independent operator oracle for the shared-role trace implication.

Prepared by @ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
import importlib.util
import itertools
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('trace_checker', Path(__file__).with_name('verify.py'))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def execute(events, inputs):
    values = list(inputs)
    for event in events:
        op = event[1]
        tag, target = op[0], op[1][1]
        if tag == 'clear':
            values[target] = 0
        elif tag == 'scale':
            values[target] = op[2]*values[target] % 5
        elif tag == 'copy':
            values[target] = values[op[2][1]]
        elif tag == 'add':
            values[target] = (values[target]+op[3]*values[op[2][1]]) % 5
        else:
            raise ValueError('oracle unknown operation')
    return tuple(values)


class TraceContractTests(unittest.TestCase):
    def test_all_six_event_permutations_on_all_dirty_f5_inputs(self):
        original = [
            ['scalar', ['scale', ['L', 0], 2], 0],
            ['scalar', ['add', ['L', 1], ['L', 0], 1], 0],
            ['scalar', ['clear', ['L', 2]], 0],
            ['scalar', ['add', ['L', 3], ['L', 2], 1], 0],
            ['scalar', ['scale', ['L', 2], 3], 0],
            ['scalar', ['copy', ['L', 0], ['L', 3]], 0],
        ]
        inputs = list(itertools.product(range(5), repeat=4))
        expected = [execute(original, state) for state in inputs]
        accepted = rejected = 0
        for order in itertools.permutations(range(6)):
            candidate = [original[i] for i in order]
            try:
                checker.occurrence_projection(original, candidate)
            except ValueError:
                rejected += 1
                continue
            accepted += 1
            self.assertEqual([execute(candidate, state) for state in inputs], expected)
        self.assertGreater(accepted, 1)
        self.assertGreater(rejected, 1)
        self.assertEqual(accepted+rejected, 720)

    def test_occurrence_inventory_cannot_hide_a_duplicate(self):
        one = ['scalar', ['scale', ['L', 0], 2], 0]
        two = ['scalar', ['scale', ['L', 1], 3], 0]
        with self.assertRaisesRegex(ValueError, 'inventory'):
            checker.occurrence_projection([one, two], [one, one])

    def test_unknown_original_event_fails_closed(self):
        unknown = ['unlisted_workspace_writer', 0]
        with self.assertRaisesRegex(ValueError, 'unknown local event'):
            checker.occurrence_projection([unknown], [unknown])


if __name__ == '__main__':
    unittest.main()
