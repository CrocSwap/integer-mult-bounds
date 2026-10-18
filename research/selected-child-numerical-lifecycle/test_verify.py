"""Behavioral, source and receipt controls; runs with Python optimization."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('child_lifetime_audit', PACKAGE / 'verify.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = audit.load_sources()

    def test_one_residue_underbudget(self):
        record = audit.execute(self.m, {'kind': 'pair'}, bounds=(20493, 22), fail='budget')
        self.assertTrue(record['source_rejected'])

    def test_one_index_underbudget(self):
        record = audit.execute(self.m, {'kind': 'good', 'good': True, 'rank': 42, 'coordinate': 167},
                               bounds=(20494, 21), fail='budget')
        self.assertTrue(record['source_rejected'])

    def test_failure_after_complete_weight(self):
        record = audit.execute(self.m, {'kind': 'pair', 'history': 'P'}, fail='weight')
        self.assertTrue(record['source_rejected'])
        self.assertEqual(record['callbacks'], 2)

    def test_coordinate_at_child_endpoint(self):
        record = audit.execute(self.m, {'kind': 'unit', 'half': True}, fail='coordinate')
        self.assertTrue(record['source_rejected'])
        self.assertEqual(record['extensions'], 0)

    def test_pair_field_127_excluded(self):
        self.assertTrue(audit.execute(self.m, {'kind': 'pair'}, fail='field')['source_rejected'])

    def test_missing_current_field(self):
        self.assertTrue(audit.execute(self.m, {'kind': 'pair'}, fail='missing_current')['source_rejected'])

    def test_negative_inverse_is_not_sign_alone(self):
        p = {'kind': 'pair', 'field': 126, 'modulus': 9, 'high_digit': 1, 'negative': True}
        c = audit.fixture(self.m, **p)
        try:
            c.request.negative_inverse = False
            value = self.m.numeric.selected_coefficient(c.plan, c.ring, c.ix, c.program,
                        c.fields, c.specs, 0, c.request)
            self.assertNotEqual(value.inspect(), c.expected)
            self.assertNotEqual((-value.inspect()) % 9, c.expected)
        finally:
            c.r.rollback(set())
            c.ix.rollback(set())

    def test_retained_input_checker_detects_corruption(self):
        c = audit.fixture(self.m)
        try:
            saved = audit.state(c)
            inputs = tuple((bytes(t.cells), t.head) for t in (c.program.tape, c.fields.tape))
            c.coord.cells[1] ^= 1
            with self.assertRaisesRegex(ValueError, 'entry ownership'):
                audit.preserved(c, saved, inputs)
        finally:
            c.r.rollback(set())
            c.ix.rollback(set())

    def test_entry_head_contract(self):
        c = audit.fixture(self.m)
        try:
            c.coord.head = 2
            with self.assertRaisesRegex(ValueError, 'entry heads'):
                with audit.Observe(self.m, c):
                    pass
        finally:
            c.r.rollback(set())
            c.ix.rollback(set())

    def test_literal_cells_detect_unowned_data(self):
        c = audit.fixture(self.m)
        try:
            spare = c.r.literal(1)
            c.r.free(spare)
            spare.cells[1] = self.m.words.ONE
            with self.assertRaisesRegex(ValueError, 'occupied numerical cells'):
                audit.Observe(self.m, c).cells()
            spare.cells[1] = self.m.words.BLANK
        finally:
            c.r.rollback(set())
            c.ix.rollback(set())

    def test_every_consumed_source_is_authenticated(self):
        with tempfile.TemporaryDirectory(prefix='child-sources-') as scratch:
            copy = Path(scratch) / 'package'
            shutil.copytree(PACKAGE, copy, ignore=shutil.ignore_patterns('__pycache__'))
            manifest = json.loads((copy / 'SNAPSHOT.json').read_text(encoding='utf-8'))
            for entry in manifest['files']:
                target = copy / entry['path']
                raw = target.read_bytes()
                target.write_bytes(raw + b'\n')
                with self.assertRaisesRegex(ValueError, 'SHA256'):
                    audit.sources(copy)
                target.write_bytes(raw)
            (copy / 'vendor/children.py').unlink()
            with self.assertRaisesRegex(ValueError, 'regular scientific source'):
                audit.sources(copy)

    def test_receipt_types_and_missing_result(self):
        original = json.loads((PACKAGE / 'RESULT.json').read_text(encoding='utf-8'))
        altered = json.loads(json.dumps(original))
        altered['fixtures'][0]['source_rejected'] = 0
        with tempfile.TemporaryDirectory(prefix='child-receipt-') as scratch:
            path = Path(scratch) / 'RESULT.json'
            path.write_text(json.dumps(altered), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'fixed typed receipt'):
                audit.check_result(original, path)
            path.unlink()
            with self.assertRaises(FileNotFoundError):
                audit.check_result(original, path)


if __name__ == '__main__':
    unittest.main()
