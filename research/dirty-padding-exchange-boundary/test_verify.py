#!/usr/bin/env python3
"""Failure-detection controls in a small Git-free export. Apache-2.0."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = 'PASS_DIRTY_PADDING_EXCHANGE_BOUNDARY'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def main():
    with tempfile.TemporaryDirectory(prefix='dirty-padding-control-') as name:
        root = Path(name)
        package = root / 'research' / HERE.name
        shutil.copytree(HERE, package)
        pins = json.loads((HERE / 'SOURCES.json').read_text())
        inputs = [row['path'] for row in pins['files'] if row['usage'] == 'input']
        for rel in inputs:
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dst)
        script = package / 'verify.py'
        original = script.read_text()

        def run(success, reason=None):
            done = subprocess.run([sys.executable, '-I', '-O', '-B', str(script)],
                                  cwd=root, text=True, capture_output=True, timeout=15)
            require((done.returncode == 0) == success, 'unexpected exit status')
            require((MARKER in done.stdout) == success, 'incorrect success marker')
            if reason:
                require(reason in done.stderr, 'failure arose at wrong boundary')

        run(True)
        # Disable the actual physical-coordinate exchange in the literal model.
        old = 'out[a + i] = state[a + pi[exchange(x)]]'
        require(original.count(old) == 1, 'mutation anchor changed')
        script.write_text(original.replace(old, 'out[a + i] = state[a + pi[x]]'))
        run(False, 'seven-gate endpoint differs')
        script.write_text(original)
        # A missing additive restriction must fail the complete endpoint check.
        old = 'out[x] ^= state[b]'
        require(original.count(old) == 1, 'restriction anchor changed')
        script.write_text(original.replace(old, 'out[x] ^= 0'))
        run(False, 'seven-gate endpoint differs')
        script.write_text(original)
        # This checks the actual pinned source bytes, not a synthetic digest.
        source = root / inputs[0]
        source.write_bytes(source.read_bytes() + b'\nchanged source\n')
        run(False, 'source pin changed')
    print('PASS_DIRTY_PADDING_FAILURE_CONTROLS groups=4')


if __name__ == '__main__':
    main()
