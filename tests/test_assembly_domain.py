"""Scope, boundary and adverse controls for the arithmetic-only domain audit."""
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('assembly_domain_audit', ROOT / 'scripts/audit_assembly_domain.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AssemblyDomain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.audit()

    def test_published_real_bridge_and_constraints(self):
        control = self.report['published_control']
        self.assertEqual(control['strict_constraint_count'], 47)
        self.assertEqual(Q(control['kappa']), Q(330942774629799, 500000000000000000))

    def test_explicit_domain_is_the_only_failed_slack(self):
        for name in ('domain_boundary', 'above_small_saving_domain', 'larger_arithmetic_only_example'):
            with self.subTest(case=name):
                row = self.report['cases'][name]
                self.assertEqual(set(row['failed_slacks']), {'b_below_one_over32'})
                self.assertEqual(row['other_slacks_strictly_positive'], 46)
                self.assertTrue(row['strict_arithmetic_rejects_with_assumed_bridge'])
                self.assertEqual(len(row['observed_requirement_failures']), 1)
        self.assertEqual(self.report['cases']['domain_boundary']['failed_slacks']['b_below_one_over32'], '0')

    def test_gaussian_range_remains_an_independent_obligation(self):
        row = self.report['cases']['gaussian_range_control']
        self.assertEqual(set(row['failed_slacks']), {'b_below_one_over32', 'alpha_below_one_fourth'})
        self.assertGreater(Q(row['gaussian_r']), Q(1, 4))

    def test_leaf_and_claim_mutations_do_not_disappear(self):
        self.assertIn('phase_leaf_above_bit', self.report['cases']['leaf_order_control']['failed_slacks'])
        self.assertIn('g3_above_kappa', self.report['cases']['excess_kappa_control']['failed_slacks'])
        for row in self.report['cases'].values():
            self.assertTrue(row['strict_arithmetic_rejects_with_assumed_bridge'])

    def test_source_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'source.py'
            path.write_bytes(b'original')
            digest = sha256(path.read_bytes()).hexdigest()
            path.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'Source pin mismatch'):
                audit.pinned_bytes(path, digest)

    def test_float_inputs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'exact Fractions'):
            audit.diagnostic_case(0.04, Q(1, 20), Q(19, 500))

    def test_receipt_is_reproducible(self):
        audit.check_receipt(ROOT / 'docs/research/assembly-domain-audit.json', self.report)

    def check_cli(self, text, *, optimized=False):
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / 'receipt.json'
            receipt.write_bytes(text.encode('utf-8'))
            flags = ['-I', '-O', '-B'] if optimized else ['-I', '-B']
            return subprocess.run(
                [sys.executable, *flags, str(ROOT / 'scripts/audit_assembly_domain.py'),
                 '--check', str(receipt)], capture_output=True, text=True)

    def test_cli_accepts_reformatting_without_changing_claims(self):
        for text in (json.dumps(self.report, sort_keys=True, separators=(',', ':')),
                     json.dumps(self.report, indent=3).replace('\n', '\r\n')):
            with self.subTest(layout=text[:30]):
                result = self.check_cli(text)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('PASS pinned assembly-domain diagnostic', result.stdout)

    def test_cli_rejects_type_coercion_and_conflicting_duplicate_claims(self):
        original = json.dumps(self.report)
        flag = '"strict_arithmetic_rejects_with_assumed_bridge": true'
        mutations = {
            'boolean_as_integer': original.replace(flag, flag.replace('true', '1'), 1),
            'fractional_constraint_count': original.replace(
                '"strict_constraint_count": 47',
                '"strict_constraint_count": 47.0000000000000000000001', 1),
            'contradictory_nested_claim': original.replace(
                flag, flag.replace('true', 'false') + ', ' + flag, 1),
            'contradictory_nested_count': original.replace(
                '"strict_constraint_count": 47',
                '"strict_constraint_count": 0, "strict_constraint_count": 47', 1),
        }
        for name, text in mutations.items():
            # Establish the old comparison's false acceptance on this exact report.
            self.assertEqual(json.loads(text), self.report)
            for optimized in (False, True):
                with self.subTest(mutation=name, optimized=optimized):
                    result = self.check_cli(text, optimized=optimized)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertNotIn('PASS pinned assembly-domain diagnostic', result.stdout)
                    expected = 'Duplicate diagnostic receipt key' if name.startswith('contradictory') else 'Diagnostic receipt differs'
                    self.assertIn(expected, result.stderr)

    def test_full_claim_content_remains_bound(self):
        mutations = []
        changed = json.loads(json.dumps(self.report))
        changed['cases']['domain_boundary']['failed_slacks']['b_below_one_over32'] = '1/100'
        mutations.append(changed)
        changed = json.loads(json.dumps(self.report))
        changed['unproved'].reverse()
        mutations.append(changed)
        changed = json.loads(json.dumps(self.report))
        del changed['source_sha256']
        mutations.append(changed)
        changed = json.loads(json.dumps(self.report))
        changed['extra_unproved_claim'] = True
        mutations.append(changed)
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / 'receipt.json'
            for index, changed in enumerate(mutations):
                with self.subTest(mutation=index):
                    receipt.write_text(json.dumps(changed), encoding='utf-8')
                    with self.assertRaisesRegex(ValueError, 'Diagnostic receipt differs'):
                        audit.check_receipt(receipt, self.report)


if __name__ == '__main__':
    unittest.main()
