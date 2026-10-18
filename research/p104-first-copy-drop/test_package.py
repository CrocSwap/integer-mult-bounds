"""Byte regeneration, relocation and actual subprocess rejection controls."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def run(script, *args, optimized=True, cwd=None, good=True):
    command = [sys.executable, '-I', '-B']
    if optimized:
        command.append('-O')
    command += [str(script)] + list(map(str, args))
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if good and result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    if not good and result.returncode == 0:
        raise RuntimeError('deliberate failure unexpectedly accepted')
    return result


def main():
    verified = run(ROOT / 'verify.py')
    print(verified.stdout, end='')
    with tempfile.TemporaryDirectory(prefix='p104-copy-drop-') as directory:
        tmp = Path(directory)
        generated = tmp / 'regenerated.json'
        run(ROOT / 'census.py', generated, optimized=False, cwd=tmp)
        if generated.read_bytes() != (ROOT / 'CERTIFICATE.json').read_bytes():
            raise ValueError('certificate regeneration differs')
        relocated = tmp / 'relocated with spaces'
        shutil.copytree(ROOT, relocated)
        for p in relocated.rglob('*'):
            if p.is_file():
                p.chmod(0o444)
        receipt = run(relocated / 'verify.py', cwd=tmp)
        if receipt.stdout != verified.stdout:
            raise ValueError('read-only relocation receipt differs')
        cert = relocated / 'CERTIFICATE.json'
        cert.chmod(0o644)
        original = cert.read_bytes()
        data = json.loads(original)
        data['frame_records'][0]['minimum_added'] = 21
        cert.write_text(json.dumps(data)+'\n')
        rejected = run(relocated / 'verify.py', cwd=tmp, good=False)
        if 'independent frame census mismatch' not in rejected.stderr:
            raise ValueError('wrong threshold corruption rejection')
        cert.write_bytes(original)
        data = json.loads(original)
        data['witness']['ranks'][3] = 5
        cert.write_text(json.dumps(data)+'\n')
        rejected = run(relocated / 'verify.py', cwd=tmp, good=False)
        if 'attaining ranks differ' not in rejected.stderr:
            raise ValueError('wrong invoice corruption rejection')
        cert.write_bytes(original)
        source = relocated / 'sources/PR968-verify.py'
        source.chmod(0o644)
        source.write_bytes(source.read_bytes()+b' ')
        rejected = run(relocated / 'verify.py', cwd=tmp, good=False)
        if 'source pin mismatch' not in rejected.stderr:
            raise ValueError('wrong source corruption rejection')
        before = hashlib.sha256(generated.read_bytes()).hexdigest()
        rejected = run(ROOT / 'census.py', generated, optimized=False, cwd=tmp, good=False)
        if 'FileExistsError' not in rejected.stderr or hashlib.sha256(generated.read_bytes()).hexdigest() != before:
            raise ValueError('occupied output not preserved')
    print('PASS_P104_FIRST_COPY_DROP_PACKAGE regeneration=PASS relocation=PASS controls=4')


if __name__ == '__main__':
    main()
