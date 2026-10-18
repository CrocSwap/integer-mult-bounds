"""Relocated replay and corrupt-input rejection controls."""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def run():
    result = []
    with tempfile.TemporaryDirectory(prefix='signed-rank-validation-') as tmp:
        base = Path(tmp)

        def trial(name, mutate=None, optimized=False, needle=None):
            target = base/name
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('__pycache__'))
            if mutate:
                mutate(target)
            command = [sys.executable, '-B', '-I', '-S']
            if optimized:
                command.append('-O')
            command.append(str(target/'verify.py'))
            started = time.monotonic()
            proc = subprocess.run(command, cwd=base, capture_output=True, text=True, timeout=60)
            if needle:
                if proc.returncode == 0 or needle not in proc.stdout+proc.stderr:
                    raise ValueError(name+': expected rejection missing\n'+proc.stdout+proc.stderr)
            elif proc.returncode or 'PASS_SIGNED_RANK_TRANSPORT' not in proc.stdout:
                raise ValueError(name+': replay failed\n'+proc.stdout+proc.stderr)
            result.append({'name': name, 'returncode': proc.returncode,
                           'seconds': time.monotonic()-started})

        def repin(path, name):
            manifest = json.loads((path/'MANIFEST.json').read_text())
            manifest['files'][name] = sha256((path/name).read_bytes()).hexdigest()
            (path/'MANIFEST.json').write_text(json.dumps(manifest))

        trial('relocated-isolated-replay')
        trial('optimized-python-rejected', optimized=True, needle='Run without -O')

        def corrupt_source(path):
            source = path/'model.py'
            source.write_text(source.read_text()+'\n# altered pin\n')
        trial('corrupt-source-pin', corrupt_source, needle='Source integrity mismatch: model.py')

        def corrupt_expected(path):
            source = path/'EXPECTED.json'
            data = json.loads(source.read_text())
            data['cases']['false-potential-nine']['endpoint'] = [0, 0, 0]
            source.write_text(json.dumps(data))
            repin(path, source.name)
        trial('repinned-false-endpoint', corrupt_expected, needle='Expected result mismatch')

        def corrupt_inverse(path):
            source = path/'transport.py'
            old = 'result.extend([gate]*(3 if gate[2] < 3 else 1))'
            text = source.read_text()
            if old not in text:
                raise ValueError('Missing inverse mutation anchor')
            source.write_text(text.replace(old, 'result.append(gate)'))
            repin(path, source.name)
        trial('repinned-wrong-phase-inverse', corrupt_inverse, needle='Forward/inverse identity failed')

        def negate_pairing(path):
            source = path/'transport.py'
            text = source.read_text()
            source.write_text(text.replace('mass = E.cast(a)*b', 'mass = -(E.cast(a)*b)'))
            repin(path, source.name)
        trial('repinned-corrupt-pairing', negate_pairing, needle='Forward/inverse row mass is not one')

    return {'status': 'PASS_SIGNED_RANK_CLI_CONTROLS', 'python': sys.version.split()[0], 'checks': result}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    report = run()
    if args.out:
        args.out.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, sort_keys=True))
