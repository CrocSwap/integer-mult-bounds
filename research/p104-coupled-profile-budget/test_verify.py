"""Semantic certificate faults and an optimized, Git-free public replay."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
spec = importlib.util.spec_from_file_location('budget_check', PACKAGE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
cost_spec = importlib.util.spec_from_file_location('pinned_cost_test', ROOT / 'research/complex-local-word-ceiling/ceiling.py')
cost = importlib.util.module_from_spec(cost_spec)
cost_spec.loader.exec_module(cost)


class CertificateFaults(unittest.TestCase):
    def setUp(self):
        self.certificate = v.read_json(PACKAGE / 'CERTIFICATE.json')

    def test_positive_and_recursive_history_inventory(self):
        v.check_certificate(self.certificate, cost)
        proposed = subprocess.run([sys.executable, '-I', '-O', '-B',
                                   str(PACKAGE / 'propose.py')], capture_output=True,
                                  text=True, timeout=30, check=False)
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        self.assertEqual(json.loads(proposed.stdout), self.certificate)
        def compositions(total):
            if total == 0:
                yield []
            else:
                for first in range(1, total + 1):
                    for tail in compositions(total - first):
                        yield [first, *tail]
        actual = {tuple(jumps): column for jumps, column in v.histories()}
        self.assertEqual(set(actual), {tuple(c) for c in compositions(9)})
        for jumps in compositions(9):
            running, caps = 0, [0] * 7
            stops = {0}
            for rank in jumps:
                end = running + rank
                for k in range(max(1, running), min(7, end - 1) + 1):
                    if running > 0 and end < 9:
                        caps[k - 1] = 2 ** (7 - rank)
                running = end
                stops.add(end)
            self.assertEqual(actual[tuple(jumps)], caps + [int(1 in stops), int(8 in stops)])

    def test_uncoupled_cheap_history_rejects(self):
        self.certificate['primal'] = {'129': '208'}
        with self.assertRaisesRegex(ValueError, 'primal coupled capacities'):
            v.check_certificate(self.certificate, cost)

    def test_dual_overcharge_and_missing_bound_reject(self):
        bad = copy.deepcopy(self.certificate)
        bad['dual'][3] = '1'
        with self.assertRaisesRegex(ValueError, 'dual history inequality'):
            v.check_certificate(bad, cost)
        self.certificate['dual'] = ['0'] * 9
        with self.assertRaisesRegex(ValueError, 'dual strict exclusion moment'):
            v.check_certificate(self.certificate, cost)

    def test_wrong_bracket_and_negative_weights_reject(self):
        bad = copy.deepcopy(self.certificate)
        bad['a_lo'], bad['a_hi'] = '3/1000', '30000001/10000000000'
        with self.assertRaisesRegex(ValueError, 'primal strict feasible moment'):
            v.check_certificate(bad, cost)
        self.certificate['primal']['129'] = '-1'
        with self.assertRaisesRegex(ValueError, 'nonnegative primal/dual'):
            v.check_certificate(self.certificate, cost)


class PublicExport(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / 'research' / PACKAGE.name
        self.package.mkdir(parents=True)
        for name in ('verify.py', 'CERTIFICATE.json', 'EXPECTED.json'):
            shutil.copyfile(PACKAGE / name, self.package / name)
        for name in v.PINS:
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)

    def run_check(self, *args):
        return subprocess.run([sys.executable, '-I', '-O', '-Werror', '-B',
                               str(self.package / 'verify.py'), *args], cwd=self.root,
                              capture_output=True, text=True, timeout=30, check=False)

    def test_unchanged_gitfree_export_and_exclusive_output(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        answer = self.run_check()
        self.assertEqual(answer.returncode, 0, answer.stderr)
        self.assertIn('PASS_P104_COUPLED_PROFILE_BUDGET', answer.stdout)
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        output = self.root / 'receipt.json'
        self.assertEqual(self.run_check('--out', str(output)).returncode, 0)
        saved = output.read_bytes()
        repeat = self.run_check('--out', str(output))
        self.assertNotEqual(repeat.returncode, 0)
        self.assertIn('FileExistsError', repeat.stderr)
        self.assertEqual(saved, output.read_bytes())

    def test_source_drift_rejects_before_import(self):
        source = self.root / 'research/complex-local-word-ceiling/ceiling.py'
        source.write_text("raise RuntimeError('must not execute')\n", encoding='utf-8')
        answer = self.run_check()
        self.assertNotEqual(answer.returncode, 0)
        self.assertIn('source hash:', answer.stderr)
        self.assertNotIn('RuntimeError: must not execute', answer.stderr)

    def test_receipt_and_duplicate_key_faults_reject(self):
        path = self.package / 'EXPECTED.json'
        data = json.loads(path.read_text())
        data['finite_premises']['forced'][3] = 4824
        path.write_text(json.dumps(data))
        answer = self.run_check()
        self.assertNotEqual(answer.returncode, 0)
        self.assertIn('complete expected receipt', answer.stderr)
        data = v.read_json(PACKAGE / 'EXPECTED.json')
        data['finite_premises']['target_bypass'][0] = False
        path.write_text(json.dumps(data))
        answer = self.run_check()
        self.assertNotEqual(answer.returncode, 0)
        self.assertIn('complete expected receipt', answer.stderr)
        (self.package / 'CERTIFICATE.json').write_text('{"primal":{},"primal":{}}')
        answer = self.run_check()
        self.assertNotEqual(answer.returncode, 0)
        self.assertIn('duplicate JSON key', answer.stderr)


if __name__ == '__main__':
    unittest.main()
