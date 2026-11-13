"""Controls for research/independent-global-rank-replay.

The full replay takes about 40 seconds. It runs once for the whole module.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / 'research/independent-global-rank-replay'
spec = importlib.util.spec_from_file_location('independent_replay', PKG / 'replay.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


class FastTests(unittest.TestCase):
    def test_empty_profile_is_an_error(self):
        with self.assertRaises(ValueError):
            replay.solve({}, {})

    def test_rank_zero_is_an_error(self):
        with self.assertRaises(ValueError):
            replay.solve({0: 1, 1: 5}, {2: 1})

    def test_no_sign_change_is_an_error(self):
        with self.assertRaises(ValueError):
            replay.solve({1: 5}, {2: 1})

    def test_derivative_bound_sees_a_rising_term(self):
        # A rank-9 deficit makes the moment rise with k, so the upper bound is positive.
        self.assertGreater(replay.Moment({1: 5}, {9: 1}).derivative_upper('0.01'), 0)
        # A rank-2 surplus makes it fall.
        self.assertLess(replay.Moment({2: 5}, {1: 9}).derivative_upper('0.01'), 0)

    def test_simple_root_is_found(self):
        # m(k) = 400 * 2^(-k) - 399, so the root is log2(400/399).
        import math
        sol = replay.solve({2: 200}, {1: 399})
        self.assertAlmostEqual(float(sol['root']), math.log2(400 / 399), places=12)

    def test_chain_of_three_parts(self):
        frames = replay.Frames([[], [1], [1, 2], [1, 2, 4], [2]])
        self.assertEqual(replay.chain_check(frames, [(0, 1), (1, 2), (2, 3)]), (True, [1, 1, 1]))
        # Broken link: the second part does not start where the first ends.
        self.assertFalse(replay.chain_check(frames, [(0, 1), (0, 2), (2, 3)])[0])
        # A part that is not nested.
        self.assertFalse(replay.chain_check(frames, [(0, 1), (1, 4), (4, 3)])[0])
        # A single part is not a split.
        self.assertFalse(replay.chain_check(frames, [(0, 1)])[0])

    def test_input_pins_hold_and_detect_change(self):
        self.assertEqual(replay.verify_pins(), [])
        pins = replay.input_pins()
        with tempfile.TemporaryDirectory() as tmp:
            for path in pins:
                target = Path(tmp) / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(ROOT / path, target)
            victim = Path(tmp) / sorted(pins)[0]
            victim.write_bytes(victim.read_bytes() + b' ')
            self.assertEqual(replay.verify_pins(Path(tmp)), [sorted(pins)[0]])


class FullReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = replay.run_all()

    def test_everything_passes(self):
        self.assertEqual(self.result['failures'], [])
        self.assertEqual(self.result['status'], 'PASS')

    def test_committed_result_matches(self):
        committed = json.loads((PKG / 'RESULT.json').read_text())
        self.assertEqual(committed, self.result)

    def test_headline_numbers_7000(self):
        inv = self.result['invoice_7000']
        self.assertEqual(inv['credit_mass_per_call'], 7650)
        self.assertEqual(inv['paid_mass_per_call'], 10962)
        self.assertEqual(inv['rank_surplus'], 1520)
        self.assertTrue(inv['crossing'].startswith('0.0036300581746883670859'))

    def test_known_answer_6030(self):
        kn = self.result['known_answer_6030']
        self.assertEqual((kn['productive'], kn['paid'], kn['rank_surplus']), (13444, 66834, 760))
        self.assertEqual(kn['query_term'], 1560)
        self.assertTrue(kn['crossing'].startswith('0.0031258115579118972'))

    def test_every_control_is_rejected_by_its_target(self):
        controls = self.result['controls']
        self.assertEqual(len(controls), 7)
        for name, control in controls.items():
            with self.subTest(name):
                self.assertIn(control['target_check'], control['failed_checks'])
                self.assertTrue(control['rejected'])

    def test_unmutated_inputs_pass_every_target_check(self):
        for section in ('word_7000', 'invoice_7000', 'word_6030', 'known_answer_6030'):
            for name, ok in self.result[section]['checks'].items():
                with self.subTest(section + ':' + name):
                    self.assertTrue(ok)
        targets = {c['target_check'] for c in self.result['controls'].values()}
        # Each target is a check that the unmutated runs above report as passing.
        reported = set()
        for section in ('word_7000', 'invoice_7000', 'word_6030', 'known_answer_6030'):
            reported |= set(self.result[section]['checks'])
        self.assertLessEqual(targets, reported)

    def test_clear_count_is_information_not_a_fault(self):
        self.assertEqual(self.result['word_7000']['information']['owned_erasures_nonzero'], 53)
        self.assertEqual(self.result['word_7000']['faults'], {})


if __name__ == '__main__':
    unittest.main()
