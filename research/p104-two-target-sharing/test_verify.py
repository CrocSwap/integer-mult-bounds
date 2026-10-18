#!/usr/bin/env python3
"""Behavioral certificate failure controls in disposable Git-free exports.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


class CertificateBehavior(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='p104-sharing-behavior-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root/'research'/HERE.name
        self.package.mkdir(parents=True)
        for path in HERE.iterdir():
            if path.is_file():
                shutil.copy2(path, self.package/path.name)
        source = self.root/'research/p104-native-channel/inputs'
        source.mkdir(parents=True)
        for name in ('LOWRANK-WITNESS.json', 'P104-FIXTURE.json'):
            shutil.copy2(ROOT/'research/p104-native-channel/inputs'/name, source/name)

    def run_check(self, *args, script='verify.py'):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(self.package/script), *map(str, args)],
                              cwd=self.root, text=True, capture_output=True, timeout=60)

    def fails(self, result, reason):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(reason, result.stderr)

    def test_read_only_git_free_export(self):
        files = [p for p in self.root.rglob('*') if p.is_file()]
        before = {str(p.relative_to(self.root)): sha256(p.read_bytes()).hexdigest() for p in files}
        for p in files:
            p.chmod(0o444)
        directories = [p for p in self.root.rglob('*') if p.is_dir()]
        for p in directories:
            p.chmod(0o555)
        try:
            result = self.run_check('--regenerate')
            self.assertEqual(result.returncode, 0, result.stderr)
            independent = self.run_check(script='independent.py')
            self.assertEqual(independent.returncode, 0, independent.stderr)
            after = {str(p.relative_to(self.root)): sha256(p.read_bytes()).hexdigest()
                     for p in self.root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
        finally:
            for p in directories:
                p.chmod(0o755)
            for p in files:
                p.chmod(0o644)

    def test_missing_receipt_is_not_regenerated(self):
        receipt = self.package/'RESULT.json'
        receipt.unlink()
        self.fails(self.run_check(), 'FileNotFoundError')
        self.assertFalse(receipt.exists())

    def test_changed_receipt_rejected(self):
        p = self.package/'RESULT.json'
        data = json.loads(p.read_text())
        data['minimum_helper_lifetimes'] = 77
        p.write_text(json.dumps(data))
        self.fails(self.run_check(), 'fixed receipt mismatch')

    def test_source_drift_rejected(self):
        p = self.root/'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'
        p.write_text(p.read_text()+' ')
        self.fails(self.run_check(), 'source hash: LOWRANK-WITNESS.json')

    def test_duplicate_and_boolean_json_rejected(self):
        p = self.package/'CIRCUIT.json'
        original = p.read_text()
        p.write_text('{"schema_version":1,' + original[1:])
        self.fails(self.run_check(), 'duplicate JSON key')
        data = json.loads(original)
        data['targets'] = [0, True]
        p.write_text(json.dumps(data))
        self.fails(self.run_check(), 'circuit schema/targets')

    def test_existing_output_is_preserved(self):
        output = self.root/'receipt.json'
        output.write_text('protected output\n')
        self.fails(self.run_check('--out', output), 'FileExistsError')
        self.assertEqual(output.read_text(), 'protected output\n')

    def test_endpoint_control_is_sensitive_to_removed_check(self):
        p = self.package/'verify.py'
        original = p.read_text()
        predicate = "        need(rows[name] == expected, 'endpoint coefficients: '+name)"
        self.assertEqual(original.count(predicate), 1)
        p.write_text(original.replace(predicate, '        pass  # Deliberately disabled in disposable control.'))
        self.fails(self.run_check(), 'control accepted: dirty-compensation-omission')


if __name__ == '__main__':
    unittest.main()
