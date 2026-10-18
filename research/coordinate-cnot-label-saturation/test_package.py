#!/usr/bin/env python3
"""Actual-file corruptions and optimized read-only relocation; Apache-2.0."""
import contextlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
INPUT = Path('research/coordinate-cnot-register-bound/PROOF.md')


@contextlib.contextmanager
def exported():
    with tempfile.TemporaryDirectory(prefix='cnot-label-saturation-') as directory:
        root = Path(directory)
        package = root/'research'/PACKAGE.name
        shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns('__pycache__'))
        (root/INPUT).parent.mkdir(parents=True)
        shutil.copy2(ROOT/INPUT, root/INPUT)
        yield root, package


def run(package, script, optimized=True):
    argv = [sys.executable, '-I', '-B']
    if optimized:
        argv.append('-O')
    return subprocess.run(argv+[str(package/script)], cwd=package.parents[1],
                          text=True, capture_output=True, timeout=90)


class PackageTests(unittest.TestCase):
    def test_readonly_minimal_export(self):
        with exported() as (root, package):
            files = [p for p in root.rglob('*') if p.is_file()]
            before = {p.relative_to(root): p.read_bytes() for p in files}
            try:
                for p in files:
                    p.chmod(0o444)
                for script in ('verify.py', 'independent.py'):
                    result = run(package, script)
                    self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
                self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in files})
            finally:
                for p in files:
                    p.chmod(0o644)

    def test_source_bytes_and_missing_input(self):
        for missing in (False, True):
            with self.subTest(missing=missing), exported() as (root, package):
                if missing:
                    (root/INPUT).unlink()
                else:
                    (root/INPUT).write_bytes((root/INPUT).read_bytes()+b'\ncorruption\n')
                result = run(package, 'verify.py')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('REJECT_LABEL_SATURATION', result.stderr)

    def test_typed_receipt_corruptions(self):
        def changed_minimum(d):
            d['four_swap_minimum_interval'] = [12, 12]

        def bool_count(d):
            d['schema_version'] = True

        def float_count(d):
            d['three_swap_minimum'] = 9.0

        def proof_cut(d):
            d['witnesses'][0]['trace']['covector_rank'] = 0

        for mutate in (changed_minimum, bool_count, float_count, proof_cut):
            with self.subTest(mutation=mutate.__name__), exported() as (_, package):
                path = package/'RESULT.json'
                data = json.loads(path.read_text())
                mutate(data)
                path.write_text(json.dumps(data))
                result = run(package, 'verify.py')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('receipt mismatch', result.stderr)

    def test_both_engines_reject_word_and_census_corruptions(self):
        for mutation in ('word', 'census', 'attainer', 'missing_witness'):
            with self.subTest(mutation=mutation), exported() as (_, package):
                path = package/'RESULT.json'
                data = json.loads(path.read_text())
                if mutation == 'word':
                    data['witnesses'][0]['word'].pop()
                elif mutation == 'census':
                    data['censuses'][1]['layers'][6]['sha256'] = '0'*64
                elif mutation == 'attainer':
                    data['two_swap_attainers']['by_a_count']['2'] -= 1
                else:
                    data['witnesses'].pop()
                path.write_text(json.dumps(data))
                for script in ('verify.py', 'independent.py'):
                    result = run(package, script)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('REJECT_', result.stderr)

    def test_duplicate_nonfinite_and_source_inventory(self):
        for mutation in ('duplicate', 'nonfinite', 'source'):
            with self.subTest(mutation=mutation), exported() as (_, package):
                path = package/'RESULT.json'
                if mutation == 'duplicate':
                    path.write_text('{"schema_version":1,'+path.read_text()[1:])
                elif mutation == 'nonfinite':
                    path.write_text('{"bad":NaN,'+path.read_text()[1:])
                else:
                    path = package/'SOURCES.json'
                    data = json.loads(path.read_text())
                    data['files'] = [r for r in data['files'] if r['usage'] != 'input']
                    path.write_text(json.dumps(data))
                result = run(package, 'verify.py')
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn('REJECT_', result.stderr)


if __name__ == '__main__':
    unittest.main()
