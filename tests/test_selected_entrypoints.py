"""Reject public restatements that drift from the selected record."""
from pathlib import Path
import importlib.util
import json
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('selected_entrypoints', ROOT / 'scripts/verify_selected_entrypoints.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class SelectedEntryPoints(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / checker.RECORD).read_text(encoding='utf-8'))
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name in checker.ENTRY_POINTS + (checker.RECORD, self.record['previous_record']):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def tearDown(self):
        self.tmp.cleanup()

    def failures(self, record=None):
        return [(f['entry'], f['field'], f['status'])
                for f in checker.check(record or self.record, self.root) if f['status'] != 'match']

    def edit(self, name, old, new):
        p = self.root / name
        text = p.read_text(encoding='utf-8')
        self.assertEqual(text.count(old), 1, (name, old))
        p.write_text(text.replace(old, new), encoding='utf-8')

    def test_current_tree(self):
        findings = checker.check(self.record, ROOT)
        self.assertEqual([f for f in findings if f['status'] != 'match'], [])
        self.assertEqual(len(findings), 18)

    def test_reject_superseded_restatements(self):
        # The exact stale values present at base 9a16422 before this change.
        cases = [
            ('CITATION.cff', 'kappa = 1661957774647029/1000000000000000000\n  = 0.001661957774647029',
             'kappa = 51110230636731/31250000000000000\n  = 0.001635527380375392',
             {('CITATION.cff', 'kappa', 'mismatch'), ('CITATION.cff', 'decimal', 'mismatch')}),
            ('CITATION.cff', 'selected checkpoint is PR890', 'selected checkpoint is PR626',
             {('CITATION.cff', 'primary PR', 'mismatch')}),
            ('CONTRIBUTING.md', '(docs/research/community-frontier890-review.md)',
             '(docs/research/community-frontier741-review.md)',
             {('CONTRIBUTING.md', 'current review', 'mismatch')}),
            ('CONTRIBUTING.md', 'currently `make frontier890-verify`', 'currently `make frontier741-verify`',
             {('CONTRIBUTING.md', 'replay', 'mismatch')}),
            ('CONTRIBUTORS.md', 'composition: #890 with #589, κ=0.001661957774647029',
             'composition: #799 with #589, κ=0.001661634653669567',
             {('CONTRIBUTORS.md', 'primary PR', 'mismatch'), ('CONTRIBUTORS.md', 'decimal', 'mismatch')}),
        ]
        for name, old, new, expected in cases:
            with self.subTest(name=name, new=new):
                self.edit(name, old, new)
                self.assertEqual(set(self.failures()), expected)
                self.edit(name, new, old)
        self.assertEqual(self.failures(), [])

    def test_reject_rounded_or_altered_kappa(self):
        self.edit('README.md', '=0.001661957774647029.', '=0.00166195777464703.')
        self.assertEqual(self.failures(), [('README.md', 'decimal', 'mismatch')])
        self.edit('README.md', '=0.00166195777464703.', '=0.0016619577746470290.')
        self.assertEqual(self.failures(), [])
        self.edit('README.md', r'\frac{1661957774647029}', r'\frac{1661957774647030}')
        self.assertEqual(self.failures(), [('README.md', 'kappa', 'mismatch')])

    def test_power_of_ten_forms(self):
        # Earlier README checkpoints print 10^{18} denominators and x10^{-4} decimals.
        self.edit('README.md', r'{1000000000000000000}=0.001661957774647029.',
                  r'{10^{18}}=1.661957774647029\times10^{-3}.')
        self.assertEqual(self.failures(), [])
        self.edit('README.md', r'=1.661957774647029\times10^{-3}.', r'=1.661957774647029\times10^{-4}.')
        self.assertEqual(self.failures(), [('README.md', 'decimal', 'mismatch')])

    def test_missing_anchor_fails(self):
        self.edit('CONTRIBUTING.md', 'currently `make frontier890-verify`', 'the selected record\'s command')
        self.assertEqual(self.failures(), [('CONTRIBUTING.md', 'replay', 'missing')])
        (self.root / 'CITATION.cff').unlink()
        self.assertIn(('CITATION.cff', 'file', 'missing'), self.failures())

    def test_status_page_binding(self):
        self.edit('docs/research/current-status.md', 'Cold replay: `make frontier890-verify`',
                  'Cold replay: `make frontier799-verify`')
        self.assertEqual(self.failures(), [('docs/research/current-status.md', 'replay', 'mismatch')])

    def test_record_bindings(self):
        record = dict(self.record, reproduce='make frontier999-verify')
        self.assertEqual(set(self.failures(record)), {
            ('CONTRIBUTING.md', 'replay', 'mismatch'), ('docs/research/current-status.md', 'replay', 'mismatch'),
            (checker.RECORD, 'replay target', 'missing')})
        record = dict(self.record, previous_kappa='1661634653669568/1000000000000000000')
        self.assertEqual(self.failures(record), [(checker.RECORD, 'previous kappa', 'mismatch')])
        heads = dict(self.record['reviewed_dependency_heads'], **{'869': self.record['audited_source_head']})
        record = dict(self.record, reviewed_dependency_heads=heads)
        self.assertEqual(set(self.failures(record)), {('CITATION.cff', 'primary PR', 'mismatch'),
                                                      ('CONTRIBUTORS.md', 'primary PR', 'mismatch')})


if __name__ == '__main__':
    unittest.main()
