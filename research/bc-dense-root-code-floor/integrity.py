#!/usr/bin/env python3
"""Git-free export and fail-closed source/receipt controls; ywz65 + OpenAI Codex."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run(package):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py')],
                          capture_output=True, text=True, timeout=180)


def main():
    with tempfile.TemporaryDirectory(prefix='bc-root-floor-') as tmp:
        package = Path(tmp)/'export'
        shutil.copytree(HERE, package)
        good = run(package)
        need(good.returncode == 0 and 'PASS_BC_DENSE_ROOT_CODE_FLOOR' in good.stdout,
             'Git-free positive export failed: '+good.stderr)
        source = package/'snapshots/pr2272-search.py'
        original = source.read_bytes()
        source.write_bytes(b"raise RuntimeError('MUST_NOT_EXECUTE')\n"+original)
        bad = run(package)
        need(bad.returncode != 0 and 'snapshot hash mismatch' in bad.stderr
             and 'RuntimeError: MUST_NOT_EXECUTE' not in bad.stderr,
             'source corruption was not rejected before extraction')
        source.write_bytes(original)
        receipt = package/'RESULT.json'
        expected = json.loads(receipt.read_text())
        changed = json.loads(receipt.read_text())
        changed['positive_source_bound_decoders'][0]['cost'] = True
        need(changed == expected, 'bool/int equality control is not relevant')
        receipt.write_text(json.dumps(changed))
        bad = run(package)
        need(bad.returncode != 0 and 'typed receipt mismatch' in bad.stderr,
             'typed receipt corruption was accepted')
    print('PASS_BC_ROOT_FLOOR_INTEGRITY git_free=1 corruptions=2')


if __name__ == '__main__':
    main()
