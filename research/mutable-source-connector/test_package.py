#!/usr/bin/env python3
"""Real subprocess corruption, relocation and deterministic-replay checks."""
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


@contextmanager
def relocated():
    # A sibling of the checkout is writable in the desktop sandbox; some
    # Windows redirected system temp directories permit mkdir but not children.
    scratch_parent = ROOT.parent.resolve()
    with tempfile.TemporaryDirectory(prefix='mutable-source-', dir=scratch_parent) as name:
        root = Path(name).resolve()
        if root.parent != scratch_parent:
            raise ValueError('temporary checkout escaped its intended parent')
        package = root / 'research' / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
        for row in manifest['files']:
            if row['usage'] == 'input':
                destination = root / row['path']
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row['path'], destination)
        yield root, package


def replay(package, name='verify.py', extra=()):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(package / name), *map(str, extra)],
                          cwd=package.parent.parent, capture_output=True, text=True, timeout=30)


class PackageTests(unittest.TestCase):
    def test_optimized_relocation_and_regeneration(self):
        with relocated() as (_, package):
            before = {str(p.relative_to(package)): p.read_bytes() for p in package.rglob('*') if p.is_file()}
            for script in ('verify.py', 'independent.py'):
                result = replay(package, script)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            after = {str(p.relative_to(package)): p.read_bytes() for p in package.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            out = package / 'new-certificate.json'
            result = replay(package, extra=('--write', out))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(out.read_bytes(), (package / 'CERTIFICATE.json').read_bytes())
            out.write_bytes(b'occupied\n')
            self.assertNotEqual(replay(package, extra=('--write', out)).returncode, 0)
            self.assertEqual(out.read_bytes(), b'occupied\n')

    def test_semantic_certificate_corruptions(self):
        for field in ('points', 'readout_pairs', 'primitive_count', 'nine_point_histogram', 'unit_complete_tariff'):
            with self.subTest(field=field), relocated() as (_, package):
                path = package / 'CERTIFICATE.json'
                data = json.loads(path.read_text(encoding='utf-8'))
                if field == 'points':
                    data[field][3] ^= 1
                elif field == 'readout_pairs':
                    data[field][0][1] = data[field][0][0]
                elif field == 'nine_point_histogram':
                    data[field]['32'] = 1
                elif field == 'unit_complete_tariff':
                    data[field]['candidate'] -= 12
                else:
                    data[field] -= 12
                path.write_text(json.dumps(data), encoding='utf-8')
                self.assertNotEqual(replay(package).returncode, 0, field)

    def test_source_drift_and_missing_source(self):
        for missing in (False, True):
            with self.subTest(missing=missing), relocated() as (root, package):
                source = root / 'research/universal-connector-boundary/CERTIFICATE.json'
                if missing:
                    source.unlink()
                else:
                    source.write_bytes(source.read_bytes() + b'\n')
                self.assertNotEqual(replay(package).returncode, 0)

    def test_omitted_source_pin(self):
        with relocated() as (_, package):
            path = package / 'SOURCES.json'
            data = json.loads(path.read_text(encoding='utf-8'))
            data['files'] = [r for r in data['files'] if not r['path'].endswith('/NOTICE.md')]
            path.write_text(json.dumps(data), encoding='utf-8')
            self.assertNotEqual(replay(package).returncode, 0)


if __name__ == '__main__':
    unittest.main()
