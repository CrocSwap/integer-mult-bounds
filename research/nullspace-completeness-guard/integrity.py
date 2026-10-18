"""Git-free export and real artifact-corruption controls; Apache-2.0."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = HERE.relative_to(ROOT)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    with tempfile.TemporaryDirectory(prefix='nullspace-guard-') as folder:
        root = Path(folder)
        package = root / REL
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
        for item in sources['files']:
            if item['usage'] == 'input':
                dst = root / item['path']
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / item['path'], dst)
        def run(expected=None, optimized=True):
            argv = [sys.executable] + (['-O'] if optimized else [])
            argv += ['-B', str(package / 'verify.py'), '--controls-only']
            env = os.environ.copy()
            env.pop('PYTHONOPTIMIZE', None)
            result = subprocess.run(argv, cwd=root, env=env, capture_output=True,
                                    text=True, timeout=60)
            if expected is None:
                require(result.returncode == 0, result.stdout + result.stderr)
            else:
                require(result.returncode != 0 and expected in result.stderr,
                        'corruption failed closed check: ' + result.stdout + result.stderr)
        run()
        paths = [root / 'research/bit-reuse-147/word147.py',
                 root / 'references/partial-gauge/pr97/linalg.py',
                 package / 'snapshots/pr2537-verify.py']
        for path in paths:
            original = path.read_bytes()
            path.write_bytes(b'raise RuntimeError("UNAUTHENTICATED_CODE_EXECUTED")\n' + original)
            try:
                run('changed snapshot:' if path.parent.name == 'snapshots' else 'changed source:')
            finally:
                path.write_bytes(original)
        receipt = package / 'RESULT.json'
        data = json.loads(receipt.read_text(encoding='utf-8'))
        data['controls']['noncanonical_bases_accepted'] = 1  # Python 1 == True is insufficient.
        receipt.write_text(json.dumps(data), encoding='utf-8')
        run('typed receipt mismatch')
    print('PASS_NULLSPACE_GIT_FREE_EXPORT_AND_4_CORRUPTION_CONTROLS')


if __name__ == '__main__':
    main()
