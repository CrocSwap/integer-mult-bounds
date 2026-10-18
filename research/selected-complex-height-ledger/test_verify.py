"""Source-bound rejection and certificate tests. Apache-2.0."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('height_ledger', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class HeightLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, _ = v.load()
        cls.result = json.loads((HERE / 'RESULT.json').read_text())

    def test_actual_source_budget(self):
        ledger, coefficients = v.audit(self.data)
        self.assertEqual(v.canonical(ledger), v.canonical(self.result['ledger']))
        self.assertEqual(len(coefficients), 332)
        self.assertEqual(v.recurrence(ledger), self.result['recurrence'])

    def test_wrong_rank_reaches_native_binding(self):
        events = copy.deepcopy(self.data['programs']['forward'])
        next(e for e in events if e[0] == 'climb')[-1] = 48
        directed = {(r['old'], r['new']): r for r in self.data['recipes']['children']}
        endpoints = {(r['role'], r['port']): r for r in self.data['recipes']['endpoint_adapters']}
        with self.assertRaisesRegex(ValueError, '^native child rank binding$'):
            v.local_ledger(events, directed, endpoints, self.data['wrappers']['recipes'], self.data['word']['frames'])

    def test_changed_bridge_is_not_charged_as_unit(self):
        data = copy.deepcopy(self.data)
        next(e for e in data['template']['execution_schedule'] if e['kind'] == 'bridge')['coefficient'] = 2
        with self.assertRaisesRegex(ValueError, '^selected bridge coefficient$'):
            v.audit(data)

    def test_singular_adapter_rejected(self):
        data = copy.deepcopy(self.data)
        data['recipes']['children'][0]['left']['matrix_rows'][0] = 0
        with self.assertRaisesRegex(ValueError, '^invertible binary monomial$'):
            v.monomial_inventory(data)

    def test_missing_idle_dispatch_rejected(self):
        data = copy.deepcopy(self.data)
        event = next(e for e in data['template']['execution_schedule'] if e['kind'] == 'idle_cover_sweep')
        event['kind'] = 'terminal'
        with self.assertRaisesRegex(ValueError, '^complete child dispatch$'):
            v.audit(data)

    def test_time_normalization_cannot_replace_height_mass(self):
        ledger = copy.deepcopy(self.result['ledger'])
        ledger['unnormalized_rank_mass_per_cover'] //= 14336
        with self.assertRaisesRegex(ValueError, '^height mass must equal the unnormalized emitted children$'):
            v.recurrence(ledger)

    def test_receipt_number_type_and_extra_fields_are_observable(self):
        self.assertEqual(v.canonical({1: 2, 48: 3, 7: 4}),
                         v.canonical({'1': 2, '48': 3, '7': 4}))
        changed = copy.deepcopy(self.result)
        changed['ledger']['children_per_cover'] = float(changed['ledger']['children_per_cover'])
        self.assertNotEqual(v.canonical(changed), v.canonical(self.result))
        changed = copy.deepcopy(self.result)
        changed['unverified'] = True
        self.assertNotEqual(v.canonical(changed), v.canonical(self.result))

    def test_pending_source_integrity(self):
        with tempfile.TemporaryDirectory(prefix='height-ledger-test-', dir=HERE) as directory:
            temporary = Path(directory)
            shutil.copyfile(HERE / 'SOURCES.json', temporary / 'SOURCES.json')
            shutil.copytree(HERE / 'sources', temporary / 'sources')
            with mock.patch.object(v, 'PACKAGE', temporary):
                v.authenticate()
                source = temporary / 'sources/pr2287/arithmetic.py'
                source.write_bytes(source.read_bytes() + b'\n# altered source\n')
                with self.assertRaisesRegex(ValueError, '^changed pending source: sources/pr2287/arithmetic.py$'):
                    v.authenticate()


if __name__ == '__main__':
    unittest.main()
