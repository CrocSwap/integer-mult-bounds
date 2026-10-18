"""Regeneration, read-only relocation, and real subprocess rejection controls."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def run(script, *args, cwd=None, good=True):
    result = subprocess.run([sys.executable, '-I', '-O', '-B', str(script), *map(str, args)],
                            cwd=cwd, capture_output=True, text=True)
    if good and result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    if not good and result.returncode == 0:
        raise RuntimeError('deliberate failure unexpectedly accepted')
    return result


def main():
    verified = run(ROOT / 'verify.py')
    print(verified.stdout, end='')
    with tempfile.TemporaryDirectory(prefix='hadamard-census-') as temporary:
        tmp = Path(temporary)
        generated = tmp / 'regenerated.json'
        run(ROOT / 'census.py', '--output', generated, cwd=tmp)
        if generated.read_bytes() != (ROOT / 'CERTIFICATE.json').read_bytes():
            raise ValueError('byte-exact certificate regeneration mismatch')
        relocated = tmp / 'relocated'
        shutil.copytree(ROOT, relocated)
        for path in relocated.rglob('*'):
            if path.is_file():
                path.chmod(0o444)
        result = run(relocated / 'verify.py', cwd=tmp)
        if result.stdout != verified.stdout:
            raise ValueError('read-only relocated receipt mismatch')
        certificate = relocated / 'CERTIFICATE.json'
        certificate.chmod(0o644)
        original = certificate.read_bytes()
        data = json.loads(original)
        data['profile_histogram'][0]['paths'] += 1
        certificate.write_text(json.dumps(data) + '\n')
        failure = run(relocated / 'verify.py', cwd=tmp, good=False)
        if 'independent exhaustive histogram mismatch' not in failure.stderr:
            raise ValueError('wrong coverage rejection')
        certificate.write_bytes(original)
        data = json.loads(original)
        data['word'].pop()
        certificate.write_text(json.dumps(data) + '\n')
        failure = run(relocated / 'verify.py', cwd=tmp, good=False)
        if 'dirty connector not restored' not in failure.stderr:
            raise ValueError('wrong restoration rejection')
        certificate.write_bytes(original)
        source = relocated / 'sources/PR997-CONSTRUCTION.json'
        source.chmod(0o644)
        source.write_bytes(source.read_bytes() + b' ')
        failure = run(relocated / 'verify.py', cwd=tmp, good=False)
        if 'source pin mismatch' not in failure.stderr:
            raise ValueError('wrong provenance rejection')
        before = hashlib.sha256(generated.read_bytes()).hexdigest()
        failure = run(ROOT / 'census.py', '--output', generated, cwd=tmp, good=False)
        if 'FileExistsError' not in failure.stderr or hashlib.sha256(generated.read_bytes()).hexdigest() != before:
            raise ValueError('occupied output was not preserved')
    print('PASS_HADAMARD_READOUT_PACKAGE regeneration=PASS relocation=PASS controls=4')


if __name__ == '__main__':
    main()
