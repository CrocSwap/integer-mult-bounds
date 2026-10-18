#!/usr/bin/env python3
"""Black-box export and rejection controls. Tekalign / OpenAI Codex, Apache-2.0."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    package = Path(__file__).resolve().parent
    repo = package.parents[1]
    manifest = json.loads((package / 'VERIFY.json').read_bytes())
    with tempfile.TemporaryDirectory(prefix='idle-four-site-') as directory:
        root = Path(directory)
        target = root / package.relative_to(repo)
        target.mkdir(parents=True)
        for name in ('verify.py', 'RESULT.json', 'SOURCES.json'):
            shutil.copyfile(package / name, target / name)
        for name in manifest['inputs']:
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(repo / name, destination)

        def run(expected=None):
            p = subprocess.run([sys.executable, '-I', '-B', '-O', str(target / 'verify.py')],
                               cwd=root, capture_output=True, text=True, timeout=60)
            if expected is None:
                require(p.returncode == 0 and 'PASS_IDLE_FOUR_SITE_RIGIDITY' in p.stdout,
                        'export failed: ' + p.stdout + p.stderr)
            else:
                require(p.returncode != 0 and expected in p.stderr,
                        'wrong rejection: ' + p.stdout + p.stderr)

        require(not (root / '.git').exists(), 'export must have no Git database')
        run()
        result = target / 'RESULT.json'
        original = result.read_bytes()
        parsed = json.loads(original)
        result.write_text(json.dumps(parsed, sort_keys=False, separators=(',', ':')))
        run()  # Whitespace changes do not change the mathematical receipt.
        parsed['new_kappa'] = 0  # Python equality alone would confuse 0 with False.
        result.write_text(json.dumps(parsed))
        run('stored result mismatch')
        result.write_bytes(original)

        source = root / manifest['inputs'][0]
        original_source = source.read_bytes()
        source.write_bytes(original_source + b'\n')
        run('source SHA256')
        source.unlink()
        run('missing or linked input')
        source.write_bytes(original_source)
        run()
    print('PASS_IDLE_FOUR_SITE_EXPORT optimized_runs=6 rejecting_controls=3')


if __name__ == '__main__':
    main()
