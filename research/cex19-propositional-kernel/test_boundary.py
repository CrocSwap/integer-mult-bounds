"""Real read-only Git-free replay and corruptions at the source/proof boundary."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def hashes(directory):
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file()}


def run(directory):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(directory / 'verify.py')],
                          capture_output=True, text=True, timeout=120)


def main():
    with tempfile.TemporaryDirectory(prefix='cex19-binding-') as folder:
        package = Path(folder) / 'export'
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        before = hashes(package)
        result = run(package)
        if result.returncode or hashes(package) != before:
            raise ValueError('Git-free positive export failed or changed files: ' + result.stderr[-1000:])
        mutations = [
            ('source/encoding.py', b"raise RuntimeError('SHOULD_NOT_EXECUTE')\n", 'source drift'),
            ('RESULT.json', b'{}\n', 'complete result receipt'),
            ('Certificate.lean', b'-- altered formal source\n', 'Lean source binding'),
        ]
        for name, raw, expected in mutations:
            path = package / name
            old = path.read_bytes()
            path.write_bytes(raw)
            result = run(package)
            path.write_bytes(old)
            if result.returncode == 0 or expected not in result.stderr:
                raise ValueError('mutation not rejected at expected boundary: ' + name)
        path = package / 'RESULT.json'
        old = path.read_bytes()
        path.unlink()
        result = run(package)
        path.write_bytes(old)
        if result.returncode == 0 or 'FileNotFoundError' not in result.stderr:
            raise ValueError('missing receipt accepted')
        if hashes(package) != before:
            raise ValueError('boundary controls failed to restore export')
    print('PASS_CEX19_BOUNDARY git_free_unchanged=1 corruptions_rejected=4')


if __name__ == '__main__':
    main()
