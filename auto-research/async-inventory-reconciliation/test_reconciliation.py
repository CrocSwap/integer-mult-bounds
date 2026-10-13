"""Failure-mode tests for the companion, using the pinned historical fixture."""
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('inventory_reconciliation', HERE / 'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class ReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins = V.read_json(HERE / 'SOURCE-PINS.json')
        cls.data = V.read_json(V.EXACT / 'INPUTS.json')
        cls.receipt = V.read_json(V.RECEIPTS / 'EXACT-WALL-146.json')
        engine_path = V.EXACT / 'moment.py'
        spec = importlib.util.spec_from_file_location('archived_moment_for_tests', engine_path)
        engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(engine)
        cls.costs = V.exact_costs(cls.data, engine, False)
        cls.input_hash = V.digest((V.EXACT / 'INPUTS.json').read_bytes())
        cls.engine_hash = V.digest(engine_path.read_bytes())

    def test_patterns_match_generating_function_counts(self):
        # Coefficients of product_w (1-z^w)^-1, independently accumulated.
        ways = [1] + [0] * 48
        for width in (5, 7, 8, 9):
            for total in range(width, 49):
                ways[total] += ways[total - width]
        for capacity in (8, 16, 32, 48):
            patterns = V.all_patterns(capacity, [5, 7, 8, 9])
            self.assertEqual(len(patterns), sum(ways[:capacity + 1]))
            self.assertEqual(len(patterns), len(set(patterns)))
            self.assertIn((0, 0, 0, 0), patterns)

    def test_modified_source_bytes_rejected(self):
        original = b'{"status":"PASS_LOCAL_CONSTRUCTOR_ONLY"}\n'
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'RESULT.json'
            path.write_bytes(original)
            self.assertEqual(V.pinned_bytes(path, V.digest(original)), original)
            path.write_bytes(original + b' ')
            with self.assertRaisesRegex(ValueError, 'Source bytes changed'):
                V.pinned_bytes(path, V.digest(original))

    def test_constructor_status_cannot_be_promoted(self):
        def load_changed(relative):
            source = V.read_json(V.ARCHIVE / relative)
            source['status'] = 'PASS_FULL_PHYSICAL_ADMISSION'
            return source
        with self.assertRaisesRegex(ValueError, 'Source scope changed'):
            V.source_rows(self.data, self.pins, load_changed)

    def test_label_aliases_are_required_and_scoped(self):
        load = lambda relative: V.read_json(V.ARCHIVE / relative)
        rows = V.source_rows(self.data, self.pins, load)
        self.assertEqual(len(rows), 146)
        self.assertEqual(sum(r['label'] != r['source_label'] for r in rows), 3)
        pins = deepcopy(self.pins)
        pins['label_aliases'] = {}
        with self.assertRaisesRegex(ValueError, 'Source label differs'):
            V.source_rows(self.data, pins, load)

    def test_removed_charges_fail_on_mathematics(self):
        data = deepcopy(self.data)
        for row in data['word_menu']:
            row['profile'].pop('1')
        with self.assertRaisesRegex(ValueError, 'Nonpositive obstruction margin'):
            V.check_receipt(data, self.receipt, self.costs, 'mercator',
                            self.input_hash, self.engine_hash)

    def test_infeasible_dual_fails_before_report_comparison(self):
        receipt = deepcopy(self.receipt)
        receipt['alpha']['48'] = str(Q(receipt['alpha']['48']) + 1)
        with self.assertRaisesRegex(ValueError, 'Infeasible dual inequality'):
            V.check_receipt(self.data, receipt, self.costs, 'mercator',
                            self.input_hash, self.engine_hash)

    def test_source_count_is_not_confused_with_boolean(self):
        data = deepcopy(self.data)
        # The actual rank-seven count is one, and Python's True == 1.
        self.assertEqual(data['word_menu'][0]['profile']['7'], 1)
        data['word_menu'][0]['profile']['7'] = True
        with self.assertRaisesRegex(ValueError, 'Invalid positive integer counts'):
            V.source_rows(data, self.pins, lambda relative: V.read_json(V.ARCHIVE / relative))


if __name__ == '__main__':
    unittest.main()
