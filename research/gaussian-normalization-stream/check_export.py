#!/usr/bin/env python3
"""Cold Git-free, optimized replay and source/typed-receipt failure controls."""
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
    with tempfile.TemporaryDirectory(prefix='normalization-export-') as temporary:
        root = Path(temporary)
        package = root/'research'/HERE.name
        package.mkdir(parents=True)
        for source in HERE.iterdir():
            if source.is_file() and source.suffix in ('.py', '.md', '.json'):
                shutil.copyfile(source, package/source.name)
        manifest = json.loads((HERE/'VERIFY.json').read_bytes())
        for name in manifest['inputs']:
            destination = root/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, destination)
        need(not (root/'.git').exists(), 'Git-free export')

        def replay(suite='all'):
            return subprocess.run([sys.executable, '-O', '-B', str(package/'verify.py'), '--suite', suite],
                                  cwd=root, capture_output=True, text=True, timeout=180)

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
        need(completed.returncode == 0 and 'PASS_GAUSSIAN_NORMALIZATION_STREAM' in completed.stdout,
             'optimized read-only source export: '+completed.stderr)

        source = root/'research/physical-gaussian-leaf/leaf_sources.py'
        original = source.read_bytes()
        source.write_bytes(original+b'\n# changed live source\n')
        failed = replay('controls')
        need(failed.returncode != 0 and 'live source SHA256' in failed.stderr,
             'live source drift rejected before loading')
        source.write_bytes(original)

        result_file = package/'RESULT.json'
        original = result_file.read_bytes()
        receipt = json.loads(original)
        receipt['controls']['failures']['late_inexact_rollback_and_retry'] = 1
        result_file.write_text(json.dumps(receipt))
        failed = replay('controls')
        need(failed.returncode != 0 and 'complete typed normalization receipt' in failed.stderr,
             'boolean-to-integer receipt substitution rejected')
        result_file.write_bytes(original)

        manifest_file = package/'VERIFY.json'
        receipt = json.loads(manifest_file.read_bytes())
        receipt['inputs'].remove('research/physical-gaussian-leaf/leaf_sources.py')
        manifest_file.write_text(json.dumps(receipt))
        failed = replay('controls')
        need(failed.returncode != 0 and 'complete live normalization input inventory' in failed.stderr,
             'undeclared live source rejected')
    print('PASS_GAUSSIAN_NORMALIZATION_EXPORT_CONTROLS')


if __name__ == '__main__':
    main()
