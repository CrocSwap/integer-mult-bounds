#!/usr/bin/env python3
"""Separate Fraction oracle and bounded file/claim controls for the stock audit."""
import copy
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('stock_audit', HERE/'verify.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def oracle_branch(record, branch, endpoint):
    """Use independent Fraction arithmetic and the closed saving formula."""
    saving = min(F(record['bit_lower']), (1-F(1, 10**24))*F(record[endpoint]))-F(1, 10**27)
    start = F(384599, 10**10)
    rows = []
    for index, item in enumerate(record[branch], 1):
        old = saving-saving**(index-1)*(saving-start)
        new = saving-saving**index*(saving-start)
        gaps = {'atom': saving-new, 'borrowing': 1-new-saving,
                'remainder': 1-new-saving*(1-old), 'stock': 1-saving}
        delta = min(gaps.values())
        qterm, linear = F(36)/delta**2, F(1032)/delta
        ceil = lambda a: -(-a.numerator//a.denominator)
        L = max(ceil(qterm), ceil(linear))
        value = F(L)*delta/2
        H = value.numerator//value.denominator-4
        rows.append({'old': str(old), 'exponent': str(new), 'gaps': {k: str(v) for k, v in gaps.items()}, 'gap': str(delta), 'cutoff_log2': str(L), 'stock_headroom_log2': H})
    return saving, rows


class StockAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads((ROOT/audit.ASSEMBLY).read_bytes())

    def test_independent_closed_form_oracle_all_fourteen(self):
        actual = audit.analyze(self.record)
        for branch, endpoint in audit.BRANCHES:
            saving, rows = oracle_branch(self.record, branch, endpoint)
            self.assertEqual(str(saving), actual[branch]['common_saving'])
            self.assertEqual(7, len(rows))
            for expected, observed in zip(rows, actual[branch]['stages']):
                self.assertEqual(expected, {k: observed[k] for k in expected})
                self.assertEqual(observed['original_guard_cap_exp']+4, observed['relaxed_fit_cap_exp'])

    def test_adjacent_integer_headroom_and_active_cutoff(self):
        self.assertFalse(audit.fit_guard(40, '-1', -100))
        self.assertFalse(audit.fit_guard(40, '0', -100))
        for branch, endpoint in audit.BRANCHES:
            _, rows = oracle_branch(self.record, branch, endpoint)
            for row in rows:
                delta, L, H = F(row['gap']), int(row['cutoff_log2']), row['stock_headroom_log2']
                self.assertGreaterEqual(L*delta/2, H+4)
                self.assertLess(L*delta/2, H+5)
                self.assertTrue(audit.fit_guard(L, row['gap'], H))
                self.assertFalse(audit.fit_guard(L, row['gap'], H+1))
                self.assertFalse(audit.fit_guard(L, row['gap'], H+4))
                self.assertTrue((L-1)*delta**2 < 36 or (L-1)*delta < 1032)

    def test_factor_sixteen_strict_fit_and_domain(self):
        # The source proof gives k <= factor*e/64 + 1. No huge 2^L is formed.
        for e in (8, 9, 16, 128, 1024):
            self.assertLess(F(16*e, 64)+1, F(e, 2))
        self.assertEqual(F(16*4, 64)+1, F(4, 2))
        self.assertGreater(F(32*8, 64)+1, F(8, 2))

    def test_arithmetic_mutations(self):
        for branch, _ in audit.BRANCHES:
            for field in ('gap', 'exponent', 'cutoff_log2'):
                changed = copy.deepcopy(self.record)
                value = changed[branch][3][field]
                changed[branch][3][field] = str(int(value)-1) if field == 'cutoff_log2' else str(F(value)+F(1, 10**100))
                with self.assertRaises(audit.AuditError):
                    audit.analyze(changed)

    def test_source_boundary_and_unproved_claim_mutations(self):
        result = audit.compute()
        boundary = result['source_boundary']
        self.assertEqual('NOT_ESTABLISHED', boundary['status'])
        self.assertEqual((120, 73), (boundary['historical_candidate']['m'], boundary['selected_candidate']['m']))
        self.assertEqual(0, boundary['completed_inner_leaf_external_extra_stock'])
        self.assertFalse(boundary['external_252_is_actual_internal_reserve'])
        mutations = (
            lambda q: q['source_boundary'].__setitem__('selected_additive_57604_recurrence', 'ESTABLISHED'),
            lambda q: q['source_boundary'].__setitem__('actual_stage_stock_coefficients', [57604]*7),
            lambda q: q['source_boundary'].__setitem__('inherited_old_leaf_reserve_coefficient', 252),
            lambda q: q['branches']['bootstrap']['stages'][0].__setitem__('actual_stock_coefficient', 0),
        )
        for mutate in mutations:
            changed = copy.deepcopy(result)
            mutate(changed)
            with self.assertRaises(audit.AuditError):
                audit.validate_claim(changed)

    def test_exact_json_and_rational_domain(self):
        self.assertNotEqual(audit.typed(True), audit.typed(1))
        for raw in ('{"x":1,"x":2}', '{"x":1.0}', '{"x":NaN}'):
            with self.assertRaises(audit.AuditError):
                audit.load_json(raw)
        with self.assertRaises(audit.AuditError):
            audit.R(True)

    def make_relocation(self, where):
        target = where/'repo'
        package = target/'research'/HERE.name
        shutil.copytree(HERE, package)
        manifest = json.loads((HERE/'SOURCES.json').read_bytes())
        for f in manifest['files']:
            src, dst = ROOT/f['path'], target/f['path']
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
        return target, package

    def run_relocated(self, package, *args):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py'), *map(str, args)], cwd=package, text=True, capture_output=True)

    def test_relocated_optimized_receipt_source_and_manifest_controls(self):
        with tempfile.TemporaryDirectory(prefix='selected-stock-test-') as directory:
            base = Path(directory)
            target, package = self.make_relocation(base)
            replay = self.run_relocated(package)
            self.assertEqual(0, replay.returncode, replay.stderr)
            catalogue = target/'docs/research/agent-task-catalog.json'
            catalogue.write_text('changed working catalogue priority data')
            self.assertEqual(0, self.run_relocated(package).returncode)
            manifest_path = package/'SOURCES.json'
            original_manifest = manifest_path.read_bytes()
            manifest = json.loads(original_manifest)
            for mutate in (
                lambda q: q.__setitem__('base_commit', '0'*40),
                lambda q: q['pending_sources'][0].__setitem__('head', '0'*40),
                lambda q: next(f for f in q['files'] if f['usage'] == 'input').__setitem__('git_blob', '0'*40),
                lambda q: q['files'].append(copy.deepcopy(q['files'][0])),
            ):
                changed = copy.deepcopy(manifest)
                mutate(changed)
                manifest_path.write_text(json.dumps(changed))
                bad = self.run_relocated(package)
                self.assertNotEqual(0, bad.returncode)
            manifest_path.write_bytes(original_manifest)
            source = target/audit.ROWS
            old_source = source.read_bytes()
            source.write_bytes(old_source+b'\nchanged source\n')
            self.assertNotEqual(0, self.run_relocated(package).returncode)
            source.write_bytes(old_source)
            receipt = package/'RESULT.json'
            old_receipt = receipt.read_bytes()
            false_receipt = json.loads(old_receipt)
            false_receipt['source_boundary']['actual_stage_stock_coefficients'] = [0]*7
            receipt.write_text(json.dumps(false_receipt))
            self.assertNotEqual(0, self.run_relocated(package).returncode)
            receipt.write_bytes(old_receipt)
            existing = base/'existing.json'
            existing.write_text('retain me')
            self.assertNotEqual(0, self.run_relocated(package, '--write-result', existing).returncode)
            self.assertEqual('retain me', existing.read_text())
            internal = package/'must-not-be-written.json'
            self.assertNotEqual(0, self.run_relocated(package, '--write-result', internal).returncode)
            self.assertFalse(internal.exists())


if __name__ == '__main__':
    unittest.main()
