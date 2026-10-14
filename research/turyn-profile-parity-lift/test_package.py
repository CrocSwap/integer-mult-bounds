#!/usr/bin/env python3
"""On-disk adversarial replay in a minimal offline closure with spaces in its path."""
from pathlib import Path
from contextlib import contextmanager
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = Path('research/turyn-profile-parity-lift')
BASELINE = Path('research/turyn-profile-cnf')


def hashes(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file()}


class OfflinePackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='Turyn actual profiles offline ')
        cls.root = Path(cls.temporary.name)
        for package in (PACKAGE, BASELINE):
            for source in (ROOT/package).rglob('*'):
                if source.is_file() and '__pycache__' not in source.parts:
                    target = cls.root/source.relative_to(ROOT)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, target)
        files = {}
        for package in (PACKAGE, BASELINE):
            files.update(json.loads((ROOT/package/'SOURCES.json').read_text())['files'])
        for name in files:
            target = cls.root/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, target)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def command(self, relative, *arguments, success=True):
        result = subprocess.run([sys.executable, '-I', '-O', '-B', str(self.root/relative), *map(str, arguments)],
                                cwd=self.root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, 'Corruption unexpectedly accepted: '+result.stdout)
        return result.stdout

    @contextmanager
    def replace(self, relative, data):
        path = self.root/relative
        original = path.read_bytes()
        try:
            if data is None:
                path.unlink()
            else:
                path.write_bytes(data)
            yield
        finally:
            path.write_bytes(original)

    def test_all_checkers_run_offline_and_leave_inputs_unchanged(self):
        before = hashes(self.root)
        scripts = [(BASELINE/'verify.py', 'PASS_TURYN_PROFILE_CNF'),
                   (PACKAGE/'verify.py', 'PASS_ACTUAL_TURYN_PROFILE_BLOCK_RANK_9'),
                   (PACKAGE/'verify_full_profiles.py', 'PASS_FULL_TURYN_PROFILES_BLOCK_RANK_9'),
                   (PACKAGE/'algebraic/verify.py', 'PASS_TURYN_ALL_CHAR2_PC_DEGREE_3')]
        for script, marker in scripts:
            with self.subTest(script=str(script)):
                self.assertIn(marker, self.command(script))
        self.assertEqual(hashes(self.root), before)

    def test_literal_coordinate_file_corruption_rejected(self):
        path = PACKAGE/'CERTIFICATE.json'
        data = json.loads((self.root/path).read_text())
        data['profiles'][0]['coordinates'][0][0] += 1
        with self.replace(path, json.dumps(data).encode()):
            self.assertIn('Integer squared norm 32', self.command(PACKAGE/'verify.py', success=False))

    def test_missing_same_class_control_rejected_on_disk(self):
        with self.replace(PACKAGE/'SAME-CLASS-CONTROL.json', None):
            self.assertIn('FileNotFoundError', self.command(PACKAGE/'verify.py', success=False))

    def test_false_full_profile_expected_receipt_rejected(self):
        path = PACKAGE/'FULL-PROFILE-EXPECTED.json'
        data = json.loads((self.root/path).read_text())
        data['profiles'][0]['ports'] -= 1
        with self.replace(path, json.dumps(data).encode()):
            self.assertIn('Exact complete-profile receipt', self.command(PACKAGE/'verify_full_profiles.py', success=False))

    def test_source_drift_rejected_before_geometry(self):
        path = Path('research/leech-lattice/evidence/TURYN-GEOMETRY.json')
        with self.replace(path, (self.root/path).read_bytes()+b'\n'):
            self.assertIn('Pinned source mismatch', self.command(PACKAGE/'verify_full_profiles.py', success=False))

    def test_ordinary_proof_file_corruption_rejected(self):
        path = PACKAGE/'algebraic/ORDINARY-PC-PROOF.json'
        data = json.loads((self.root/path).read_text())
        data['steps'][-1]['inputs'].pop()
        with self.replace(path, json.dumps(data).encode()):
            self.assertIn('Final polynomial is constant one', self.command(PACKAGE/'algebraic/verify.py', success=False))

    def test_both_producers_rebuild_in_minimal_closure(self):
        for subdirectory in ('', 'algebraic'):
            package = PACKAGE/subdirectory
            with tempfile.TemporaryDirectory(prefix='Turyn rebuilt artifacts ') as output:
                self.command(package/'build.py', '--output', output)
                produced = list(Path(output).iterdir())
                self.assertEqual(len(produced), 2 if subdirectory else 5)
                for file in produced:
                    with self.subTest(file=str(package/file.name)):
                        self.assertEqual(file.read_bytes(), (self.root/package/file.name).read_bytes())


if __name__ == '__main__':
    unittest.main(verbosity=2)
