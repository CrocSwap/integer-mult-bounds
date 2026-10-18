#!/usr/bin/env python3
"""Relocation and corruption checks for this mathematical evidence package.

Prepared for alluri-ritual with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def run(script, *args):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(script), *map(str, args)],
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def main():
    pins = json.loads((HERE / 'SOURCE-PINS.json').read_text())
    with tempfile.TemporaryDirectory(prefix='factory5 package with spaces ') as tmp:
        root = Path(tmp)
        package = root / 'research/complex-factory5-resynthesis'
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        for rel in pins['files']:
            dest = root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, dest)
        verifier = package / 'verify.py'
        result = run(verifier)
        if result.returncode:
            raise RuntimeError('Relocated replay failed:\n' + result.stdout)
        cases = []

        def reject(name, path, changed, reason):
            saved = path.read_bytes()
            try:
                path.write_bytes(changed)
                result = run(verifier)
                if result.returncode == 0 or reason not in result.stdout:
                    raise RuntimeError(name + ': wrong rejection\n' + result.stdout)
                cases.append(name)
            finally:
                path.write_bytes(saved)

        source = root / 'research/complex-k492-owner-repair/code/construct_k_triangle.py'
        reject('changed_pinned_constructor', source, source.read_bytes()+b'\n# corrupt\n',
               'Source pin mismatch')
        circuit = package / 'CIRCUIT.json'
        cert = json.loads(circuit.read_text())
        cert['original'].pop()
        reject('fabricated_original_window', circuit, json.dumps(cert).encode(),
               'original gates are not the literal constructor window')
        expected = package / 'RESULT.json'
        value = json.loads(expected.read_text())
        value['status'] = 'corrupted'
        reject('changed_expected_receipt', expected, json.dumps(value).encode(),
               'receipt differs from frozen result')
        source_pins = package / 'SOURCE-PINS.json'
        saved = source_pins.read_bytes()
        source_pins.unlink()
        result = run(verifier)
        source_pins.write_bytes(saved)
        if result.returncode == 0 or 'SOURCE-PINS.json' not in result.stdout:
            raise RuntimeError('Missing source pins accepted')
        cases.append('missing_source_pins')
        existing = root / 'existing output'
        existing.mkdir()
        marker = existing / 'keep.txt'
        marker.write_text('preserve')
        result = run(verifier, '--out', existing)
        if result.returncode == 0 or marker.read_text() != 'preserve':
            raise RuntimeError('Existing output was not protected')
        cases.append('existing_output_preserved')
    print('PASS_PACKAGE_CONTROLS relocation=1 rejections=' + str(len(cases)))


if __name__ == '__main__':
    main()
