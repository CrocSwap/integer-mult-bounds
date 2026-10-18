#!/usr/bin/env python3
"""Clean source export and admission-failure controls; Apache-2.0, Codex assistance."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, label):
    if not ok:
        raise ValueError(label)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='qnode6 package with spaces ') as temporary:
        root = Path(temporary) / 'source export'
        package = root / 'research' / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        source = json.loads((HERE / 'SOURCES.json').read_text())
        for relative in source['files']:
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)
        script = package / 'verify.py'
        command = [sys.executable, '-I', '-O', '-B', str(script)]
        result = subprocess.run(command + ['--replay-search'] + (['--native'] if args.native else []),
                                cwd=temporary, capture_output=True, text=True)
        need(result.returncode == 0, 'clean optimized export: ' + result.stdout + result.stderr)
        print(result.stdout, end='')
        controls = []

        def rejected(label, expected, extra=()):
            process = subprocess.run(command + list(extra), cwd=temporary,
                                     capture_output=True, text=True)
            need(process.returncode != 0 and expected in process.stdout + process.stderr,
                 label + ' did not reject at the intended boundary: ' + process.stdout + process.stderr)
            controls.append(label)

        word = root / 'research/e8-r480-dead-totals/data/bitE8mut-r480.json.gz'
        original = word.read_bytes()
        word.write_bytes(original + b'changed input')
        rejected('changed immutable supplier', 'source digest:')
        word.write_bytes(original)

        pins = package / 'SOURCES.json'
        original = pins.read_bytes()
        changed = json.loads(original)
        changed['files'].pop('research/r480-qnode5-seed05/search.py')
        pins.write_text(json.dumps(changed))
        rejected('missing dependency pin', 'missing required source pin')
        pins.write_bytes(original)

        candidate = package / 'CANDIDATE.json'
        original = candidate.read_bytes()
        changed = json.loads(original)
        changed['best']['gates'][0][0] = 0
        candidate.write_text(json.dumps(changed))
        rejected('bad recipe frame', 'block frame/destination')
        candidate.write_bytes(original)

        changed = json.loads(original)
        changed['best']['budgets'][0][1] += 1
        candidate.write_text(json.dumps(changed))
        rejected('incorrect search precision receipt', 'search/replay precision mismatch')
        candidate.write_bytes(original)

        certificate = package / 'CERTIFICATE.json'
        original = certificate.read_bytes()
        changed = json.loads(original)
        changed['subsets'][7]['adds'] -= 1
        certificate.write_text(json.dumps(changed))
        rejected('incorrect complete bill certificate', 'certificate drift')
        certificate.write_bytes(original)

        existing = Path(temporary) / 'existing output'
        existing.mkdir()
        marker = existing / 'keep.bin'
        marker.write_bytes(b'do not replace')
        before = hashlib.sha256(marker.read_bytes()).hexdigest()
        rejected('existing output directory', 'File exists', ['--output', str(existing)])
        need(before == hashlib.sha256(marker.read_bytes()).hexdigest() and
             list(existing.iterdir()) == [marker], 'existing output was modified')
        print('PASS_R480_QNODE6_PACKAGE clean_export=True optimized=True '
              f'native={args.native} rejection_controls={len(controls)}')


if __name__ == '__main__':
    main()
