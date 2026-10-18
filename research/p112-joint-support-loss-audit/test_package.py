#!/usr/bin/env python3
"""Package boundary and semantic rejection controls; Apache-2.0."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('joint_loss_audit', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = v.load_geometry()
        cls.receipt = json.loads((HERE / 'RESULT.json').read_text())
        cls.supports, cls.codes = v.words_from_pairing(cls.data)

    def test_full_rank_corollary(self):
        rows = self.receipt['added_price_screen']
        self.assertEqual([r['size'] for r in rows], list(range(1, 44)))
        self.assertEqual(min(r['copy_lower_bound'] for r in rows), 66)
        self.assertEqual(v.added_reader_premises(self.data),
                         self.receipt['added_reader_premises'])

    def test_missing_codeword_rejected_by_literal_oracle(self):
        row = self.receipt['exact_maxima'][24]
        mask = v.mask_of(row['witness_ports'])
        codes = copy.deepcopy(self.codes)
        j = next(j for j, c in enumerate(codes) if mask in c)
        codes[j].remove(mask)
        with self.assertRaisesRegex(ValueError, 'kernel versus literal'):
            v.checked_losses(self.data, codes, mask)

    def test_mutated_claim_receipts_rejected(self):
        for key, change in [('maximum', 0), ('extension', 1), ('bill', 2)]:
            bad = copy.deepcopy(self.receipt)
            if change == 0:
                bad['exact_maxima'][36]['maximum_loss'] = 4
            elif change == 1:
                bad['four_reader_supports'][0]['extra_for_second'] = 11
            else:
                bad['added_price_screen'][-1]['copy_lower_bound'] = 65
            with self.subTest(key=key), self.assertRaises(ValueError):
                v.validate_result(self.receipt, bad)

    def test_all_minimal_four_supports_have_literal_margin(self):
        for row in self.receipt['four_reader_supports']:
            mask = v.mask_of(row['ports'])
            self.assertEqual(v.direct_losses(self.data, mask), row['losses'])
            self.assertEqual(sum(row['losses']), 4)
        self.assertEqual(len(self.receipt['four_reader_supports']), 42)

    def test_modular_rank_is_only_a_lower_bound(self):
        # This integer matrix has rational rank8 but modular rank0: the
        # proof cannot use equality of field ranks without its upper bound.
        diag3 = [[3 * (i == j) for j in range(8)] for i in range(8)]
        self.assertEqual(v.rank_mod3(diag3), 0)
        bad = copy.deepcopy(self.data)
        bad['X'] = [[3 * x for x in row] for row in bad['X']]
        with self.assertRaisesRegex(ValueError, 'eight-minor'):
            v.added_reader_premises(bad)

    def test_optimized_readonly_relocation_and_source_fault(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / 'research' / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            source = root / v.GEOMETRY
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(v.ROOT / v.GEOMETRY, source)
            for p in root.rglob('*'):
                if p.is_file():
                    p.chmod(0o444)
            result = subprocess.run([sys.executable, '-I', '-O', '-B',
                                     str(package / 'verify.py')], cwd=root,
                                    capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('PASS_P112_JOINT_SUPPORT_LOSS', result.stdout)
            source.chmod(0o644)
            bad = copy.deepcopy(self.data)
            bad['labels'][0] ^= 1
            source.write_text(json.dumps(bad))
            result = subprocess.run([sys.executable, '-I', '-O', '-B',
                                     str(package / 'verify.py')], cwd=root,
                                    capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('geometry source pin', result.stderr)
            self.assertFalse(any(root.rglob('__pycache__')))


if __name__ == '__main__':
    unittest.main()
