"""Mathematical and corruption controls for phase-local dyadic gauges."""
import copy
import importlib.util
import itertools
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('v', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = v.engine()
        cls.word, cls.programs, _, _ = cls.lib.load()
        cls.receipt, cls.witnesses = v.compute()

    def test_01_exhaustive_tiny_path_oracle(self):
        checked = 0
        symbols = list(itertools.product((-1, 0, 1), (False, True)))
        for n in (1, 2, 3):
            for seq in itertools.product(symbols, repeat=n):
                rows = [[i, b, unit] for i, (b, unit) in enumerate(seq)]
                base = sum(abs(b) - int(unit and b == 0) for b, unit in seq)
                brute = min(abs(ks[0]) + abs(ks[-1]) +
                            sum(abs(a - b) for a, b in zip(ks, ks[1:])) +
                            sum(abs(k - b) - int(unit and k == b)
                                for k, (b, unit) in zip(ks, seq)) - base
                            for ks in itertools.product(range(-2, 3), repeat=n))
                self.assertEqual(v.solve_run(rows)['delta'], brute)
                checked += 1
        self.assertEqual(checked, 258)

    def test_02_unit_discount_changes_optimum(self):
        rows = [[0, 1, True], [1, 1, True]]
        answer = v.solve_run(rows)
        self.assertEqual((answer['delta'], answer['path']), (-2, [1, 1]))
        self.assertEqual(v.solve_run([[0, 1, False], [1, 1, False]])['delta'], 0)

    def test_03_expanded_domain_agrees(self):
        for scenario in ('orientations', 'on_pr1214'):
            for result in self.receipt[scenario].values():
                for run in result['schedule']:
                    self.assertEqual(v.solve_run(run['terms'], extra=9)['delta'], run['delta'])

    def test_04_missing_entry_scale_rejected(self):
        for orientation in self.programs:
            events = copy.deepcopy(self.witnesses[orientation])
            i = next(i for i, e in enumerate(events) if e[0] == 'scalar' and
                     e[1][:2] == ['scale', ['L', 427]])
            events.pop(i)
            with self.assertRaises(ValueError):
                self.lib.replay(events, orientation)

    def test_05_missing_final_scale_rejected(self):
        for orientation in self.programs:
            events = copy.deepcopy(self.witnesses[orientation])
            i = max(i for i, e in enumerate(events) if e[0] == 'scalar' and
                    e[1][:2] == ['scale', ['L', 427]])
            events.pop(i)
            with self.assertRaises(ValueError):
                self.lib.replay(events, orientation)

    def test_06_wrong_inverse_orientation_rejected(self):
        winner = self.receipt['orientations']['forward']
        candidate = v.construct(self.lib, self.programs['backward'], winner['helper'], winner['schedule'])
        # Conjugation is still algebraically exact, but the inverse orientation
        # cannot inherit forward pricing: its optimum has reflected exponents.
        self.lib.replay(candidate, 'backward')
        price = self.lib.invoice(candidate, 'copy-init')['real_primitives']
        self.assertNotEqual(price, self.receipt['orientations']['backward']['after']['real_primitives'])

    def test_07_nonzero_boundary_rejected(self):
        result = copy.deepcopy(self.receipt['orientations']['forward'])
        # Force two separate scalar runs into one schedule, carrying its gauge
        # through an unchanged adapter/climb boundary.
        a, b = result['schedule']
        a['terms'] += b['terms']
        a['path'] += b['path']
        a['path'][len(a['path']) - len(b['path']) - 1] = -1
        with self.assertRaises(ValueError):
            v.construct(self.lib, self.programs['forward'], result['helper'], [a])

    def test_08_vendor_tamper_and_missing_pin(self):
        original = v.HERE
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            (folder / 'vendor/pr1161').mkdir(parents=True)
            sources = json.loads((HERE / 'SOURCES.json').read_text())
            del sources['vendor']['PROOF.md']
            (folder / 'SOURCES.json').write_text(json.dumps(sources))
            try:
                v.HERE = folder
                with self.assertRaisesRegex(ValueError, 'vendor inventory'):
                    v.engine()
                sources['vendor']['PROOF.md'] = '0' * 64
                (folder / 'SOURCES.json').write_text(json.dumps(sources))
                for filename in sources['vendor']:
                    (folder / 'vendor/pr1161' / filename).write_bytes(b'corrupt')
                with self.assertRaisesRegex(ValueError, 'vendor pin'):
                    v.engine()
            finally:
                v.HERE = original

    def test_09_profiles_and_full_cost(self):
        for orientation in self.programs:
            result = self.receipt['on_pr1214'][orientation]
            self.assertEqual(result['after']['paid_profile'], result['original_before']['paid_profile'])
            self.assertEqual(result['original_before']['complex_primitives'] -
                             result['after']['complex_primitives'], 1094)
            self.assertLessEqual(result['after']['prefix_bits'], 68)

    def test_10_wrapped_witness_is_inside_wrapper_domain(self):
        for orientation, events in self.programs.items():
            result = self.receipt['wrapped_example'][orientation]
            self.assertEqual((result['helper'], result['delta'], result['wrapped_helpers_checked']),
                             (652, -36, 240))
            self.assertIn(652, {e[2] for e in events if e[0] == 'residual_adapter'})
            self.assertEqual(result['before']['paid_profile'], result['after']['paid_profile'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
