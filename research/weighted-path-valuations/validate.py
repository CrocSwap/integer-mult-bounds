"""Relocation, gzip and command-line rejection controls (standard library only)."""
import argparse
from hashlib import sha256
from pathlib import Path
import gzip
import json
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def run():
    checks = []
    with tempfile.TemporaryDirectory(prefix='weighted-path-validation-') as tmp:
        base = Path(tmp)

        def trial(name, edit=None, optimized=False, needle=None):
            target = base/name
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('__pycache__'))
            if edit:
                edit(target)
            command = [sys.executable, '-B', '-I', '-S']
            if optimized:
                command.append('-O')
            command.append(str(target/'verify.py'))
            started = time.monotonic()
            proc = subprocess.run(command, cwd=base, capture_output=True, text=True, timeout=60)
            if needle:
                if proc.returncode == 0 or needle not in proc.stdout+proc.stderr:
                    raise ValueError(name+': expected rejection not observed\n'+proc.stdout+proc.stderr)
            elif proc.returncode != 0 or 'PASS_WEIGHTED_PATH_VALUATIONS' not in proc.stdout:
                raise ValueError(name+': replay failed\n'+proc.stdout+proc.stderr)
            checks.append({'name': name, 'returncode': proc.returncode,
                           'seconds': time.monotonic()-started})

        def repin(path, name):
            manifest = json.loads((path/'MANIFEST.json').read_text())
            manifest['files'][name] = sha256((path/name).read_bytes()).hexdigest()
            (path/'MANIFEST.json').write_text(json.dumps(manifest))

        trial('relocated-isolated-replay')
        trial('optimized-python-rejected', optimized=True, needle='Run without -O')

        def recompress(path):
            source = path/'words.json.gz'
            source.write_bytes(gzip.compress(gzip.decompress(source.read_bytes()), compresslevel=1, mtime=123))
        trial('equivalent-gzip-accepted', recompress)

        def corrupt_payload(path):
            source = path/'words.json.gz'
            source.write_bytes(gzip.compress(gzip.decompress(source.read_bytes())+b'\n', mtime=0))
        trial('changed-word-payload-rejected', corrupt_payload, needle='Word payload mismatch')

        def corrupt_source(path):
            source = path/'model.py'
            source.write_text(source.read_text()+'\n# source mutation\n')
        trial('changed-source-rejected', corrupt_source, needle='Source integrity mismatch: model.py')

        def missing_choice(path):
            source = path/'CERTIFICATES.json'
            data = json.loads(source.read_text())
            data['cases'][0]['frame_certificates'].pop()
            source.write_text(json.dumps(data))
            repin(path, source.name)
        trial('repinned-missing-choice-rejected', missing_choice, needle='Incomplete frame coverage')

        def missing_case(path):
            source = path/'CERTIFICATES.json'
            data = json.loads(source.read_text())
            data['cases'].pop()
            source.write_text(json.dumps(data))
            repin(path, source.name)
        trial('repinned-missing-word-rejected', missing_case, needle='Unresolved source corpus mismatch')

        def zero_gap(path):
            source = path/'CERTIFICATES.json'
            data = json.loads(source.read_text())
            case = next(c for c in data['cases'] if c['global_certificate'] is not None)
            data['vectors'][case['global_certificate']] = [0]*15
            source.write_text(json.dumps(data))
            repin(path, source.name)
        trial('repinned-zero-gap-rejected', zero_gap, needle='Nonpositive determinant valuation gap')

    return {'status': 'PASS_WEIGHTED_PATH_CLI_CONTROLS', 'python': sys.version.split()[0],
            'checks': checks}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    report = run()
    if args.out:
        args.out.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, sort_keys=True))
