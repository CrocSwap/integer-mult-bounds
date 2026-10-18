#!/usr/bin/env python3
"""Optimized Git-free replay plus source, archive, inventory and receipt controls."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    with tempfile.TemporaryDirectory(prefix='relative-history-export-') as temporary:
        root = Path(temporary)
        package = root/'research'/HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for name in json.loads((HERE/'VERIFY.json').read_bytes())['inputs']:
            destination = root/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, destination)
        need(not (root/'.git').exists(), 'Git-free export')

        def replay(suite='all'):
            return subprocess.run([sys.executable, '-O', '-B', str(package/'verify.py'), '--suite', suite],
                                  cwd=root, capture_output=True, text=True, timeout=240)

        files = [path for path in root.rglob('*') if path.is_file()]
        directories = sorted([path for path in root.rglob('*') if path.is_dir()],
                             key=lambda path: len(path.parts), reverse=True)
        for path in files:
            path.chmod(0o444)
        for path in (*directories, root):
            path.chmod(0o555)
        try:
            completed = replay()
        finally:
            for path in (root, *reversed(directories)):
                path.chmod(0o755)
            for path in files:
                path.chmod(0o644)
        need(completed.returncode == 0 and 'PASS_LIFTING_RELATIVE_HISTORY' in completed.stdout,
             'optimized read-only export: '+completed.stderr)

        source = root/'research/batched-spaced-lifting/model.py'
        raw = source.read_bytes()
        source.write_bytes(raw+b'\n# changed live input\n')
        failure = replay('controls')
        need(failure.returncode != 0 and 'live source SHA256' in failure.stderr, 'source drift rejected')
        source.write_bytes(raw)

        archive = package/'inputs/pr3122.tar'
        raw = archive.read_bytes()
        archive.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
        failure = replay('controls')
        need(failure.returncode != 0 and 'immutable PR3122 archive' in failure.stderr, 'archive drift rejected')
        archive.write_bytes(raw)

        result = package/'RESULT.json'
        raw = result.read_bytes()
        receipt = json.loads(raw)
        receipt['controls']['alias'] = 1
        result.write_text(json.dumps(receipt))
        failure = replay('controls')
        need(failure.returncode != 0 and 'complete typed hierarchy receipt' in failure.stderr,
             'boolean/integer receipt substitution rejected')
        result.write_bytes(raw)

        manifest = package/'VERIFY.json'
        changed = json.loads(manifest.read_bytes())
        changed['inputs'].remove('research/batched-spaced-lifting/model.py')
        manifest.write_text(json.dumps(changed))
        failure = replay('controls')
        need(failure.returncode != 0 and 'complete live input inventory' in failure.stderr,
             'undeclared live input rejected')
    print('PASS_LIFTING_RELATIVE_HISTORY_EXPORT_CONTROLS')


if __name__ == '__main__':
    main()
