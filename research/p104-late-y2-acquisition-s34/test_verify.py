#!/usr/bin/env python3
"""Exercise the published CLI in disposable, Git-free source exports.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
These are evidence-integrity controls, separate from the mathematical faults
replayed in verify.py and independent.py. No checker or producer is imported.
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
NATIVE = HERE.parent / 'p104-native-channel' / 'inputs'


class PublishedEvidence(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='p104-late-export-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / 'research' / HERE.name
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns('__pycache__'))
        self.native = self.package.parent / 'p104-native-channel' / 'inputs'
        self.native.mkdir(parents=True)
        for name in ('LOWRANK-WITNESS.json', 'P104-FIXTURE.json'):
            shutil.copyfile(NATIVE / name, self.native / name)

    def command(self, script, *args, error=None):
        result = subprocess.run([sys.executable, '-I', '-O', '-B', str(self.package / script), *args],
                                cwd=self.root, capture_output=True, text=True, timeout=90)
        output = result.stdout + result.stderr
        if error is None:
            self.assertEqual(result.returncode, 0, output)
        else:
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn(error, output)
        return output

    def rewrite(self, filename, mutate):
        path = self.package / filename
        value = json.loads(path.read_text())
        mutate(value)
        path.write_text(json.dumps(value) + '\n')

    def inventory(self):
        return {str(p.relative_to(self.root)): sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*') if p.is_file()}

    def test_git_free_export_is_read_only(self):
        before = self.inventory()
        self.assertIn('PASS_P104_LATE_Y2_S34', self.command('verify.py', '--regenerate'))
        self.assertIn('PASS_INDEPENDENT_P104_LATE_Y2_S34', self.command('independent.py'))
        self.assertEqual(self.inventory(), before)

    def test_all_three_immutable_inputs_fail_closed(self):
        for path in (self.native / 'LOWRANK-WITNESS.json', self.native / 'P104-FIXTURE.json',
                     self.package / 'inputs' / 'PR2460-CIRCUIT.json'):
            with self.subTest(source=path.name):
                original = path.read_bytes()
                path.write_bytes(original + b'\n')
                try:
                    self.command('verify.py', error='source pin: ' + path.name)
                    self.command('independent.py', error='input hash')
                finally:
                    path.write_bytes(original)

    def test_missing_and_altered_receipt_fail_closed(self):
        path = self.package / 'RESULT.json'
        original = path.read_bytes()
        path.unlink()
        self.command('verify.py', error='FileNotFoundError')
        self.assertFalse(path.exists())
        path.write_bytes(original)
        self.rewrite('RESULT.json', lambda r: r['candidate'].__setitem__('added_rank_mass', 827))
        self.command('verify.py', error='complete receipt equality')
        self.command('independent.py', error='independent receipt: candidate')

    def test_capture_metadata_must_match_literal_events(self):
        def change_cut(circuit):
            circuit['late_acquisition']['routes'][0]['captures'][1]['cut'] += 1
        self.rewrite('CIRCUIT.json', change_cut)
        self.command('verify.py', error='literal route binding')

    def test_even_canceling_changes_to_retained_groups_are_rejected(self):
        def change_retained_group(circuit):
            helper = next(r for r in circuit['initial_frames'] if not r.startswith('LATE'))
            events = circuit['insertions'][0]['events']
            events[:0] = [['add', 'Y0', helper, '1', []], ['add', 'Y0', helper, '-1', []]]
        self.rewrite('CIRCUIT.json', change_retained_group)
        self.command('verify.py', error='retained insertion stream')

    def test_producer_refuses_to_overwrite_evidence(self):
        path = self.package / 'CIRCUIT.json'
        before = path.read_bytes()
        self.command('build.py', '--out', str(path), error='FileExistsError')
        self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
