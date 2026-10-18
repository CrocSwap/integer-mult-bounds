#!/usr/bin/env python3
"""Behavioral controls for a relocated offline research package."""
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rehash(root, name):
    manifest = json.loads((root/'MANIFEST.json').read_text(encoding='utf-8'))
    manifest['sha256'][name] = sha256((root/name).read_bytes()).hexdigest()
    (root/'MANIFEST.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')


def main():
    started = time.monotonic()
    data = {str(p.relative_to(ROOT)): p.read_bytes() for p in ROOT.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts}
    results = []
    # TemporaryDirectory owns its one verified absolute temporary root.
    with tempfile.TemporaryDirectory(prefix='rational audit with spaces ') as td:
        top = Path(td).resolve()

        def run(name, mutate=None, expected=None, extra=()):
            root = (top/name).resolve()
            need(top in root.parents, 'Test target escaped temporary root')
            for path, value in data.items():
                target = root/path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(value)
            if mutate:
                mutate(root)
            result = subprocess.run([sys.executable, '-I', '-B', '-O', str(root/'verify.py'), *extra],
                                    cwd=top, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, timeout=120)
            if expected is None:
                need(result.returncode == 0 and 'PASS_RATIONAL_CIRCLE_BOUND' in result.stdout,
                     name+' failed: '+result.stdout)
            else:
                need(result.returncode != 0 and expected in result.stdout,
                     name+' did not reject expected fault: '+result.stdout)
            results.append(name)
            print('PASS '+name, flush=True)

        run('pristine relocated optimized')

        def source_drift(root):
            p = root/'vendor/prime-power-proof.md'
            p.write_bytes(p.read_bytes()+b'\nChanged source\n')
            rehash(root, 'vendor/prime-power-proof.md')
        run('source bytes drift', source_drift, 'Source SHA-256 mismatch')

        def git_drift(root):
            p = root/'SOURCES.json'
            obj = json.loads(p.read_text(encoding='utf-8'))
            obj['files'][0]['git_blob'] = '0'*40
            p.write_text(json.dumps(obj), encoding='utf-8')
            rehash(root, 'SOURCES.json')
        run('wrong source Git blob', git_drift, 'Source Git-blob mismatch')

        def proof_drift(root):
            p = root/'PROOF.md'
            p.write_bytes(p.read_bytes()+b'\nChanged proof\n')
        run('unrecorded proof drift', proof_drift, 'Package hash mismatch: PROOF.md')

        def receipt_drift(root):
            p = root/'EXPECTED.json'
            obj = json.loads(p.read_text(encoding='utf-8'))
            obj['budgets'][-1]['new_bits'] -= 1
            p.write_text(json.dumps(obj), encoding='utf-8')
            rehash(root, 'EXPECTED.json')
        run('changed expected budget', receipt_drift, 'Expected evidence mismatch')

        def mutate_code(old, new):
            def mutate(root):
                p = root/'verify.py'
                code = p.read_text(encoding='utf-8')
                need(code.count(old) == 1, 'Mutation anchor is not unique')
                p.write_text(code.replace(old, new), encoding='utf-8')
                rehash(root, 'verify.py')
            return mutate

        run('lost reflection conjugation',
            mutate_code('mirror = [ONE, -a.conj()]', 'mirror = [ONE, -a]'),
            'Circle modulus preservation')
        run('wrong closure denominator sign',
            mutate_code('denom = phase**length-root**length', 'denom = phase**length+root**length'),
            'Dense / geometric inverse disagreement')
        run('refuse expected overwrite', expected='Refusing to overwrite evidence',
            extra=('--emit', str(ROOT/'EXPECTED.json')))
    print(json.dumps({'status': 'PASS_PACKAGE_CONTROLS', 'tests': results,
                      'count': len(results), 'seconds': round(time.monotonic()-started, 3)}, sort_keys=True))


if __name__ == '__main__':
    main()
