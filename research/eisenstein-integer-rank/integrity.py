#!/usr/bin/env python3
"""Git-free full replay and pre-import source/typed receipt controls."""
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


def run(package, filename='verify.py'):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/filename)],
                          capture_output=True, text=True, timeout=180)


def main():
    with tempfile.TemporaryDirectory(prefix='eisenstein-integer-rank-') as tmp:
        root = Path(tmp)/'export'
        package = root/'research'/HERE.name
        shutil.copytree(HERE, package)
        inputs = [r for r in json.loads((HERE/'SOURCES.json').read_text())['files'] if r['usage']=='input']
        for item in inputs:
            target = root/item['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT/item['path'], target)
        good = run(package)
        need(good.returncode == 0 and 'PASS_EISENSTEIN_INTEGER_RANK' in good.stdout,
             'Git-free complete replay failed: '+good.stderr)
        for item in inputs:
            source = root/item['path']
            original = source.read_bytes()
            source.write_bytes(b"raise RuntimeError('MUST_NOT_EXECUTE')\n"+original)
            bad = run(package, 'replay.py')
            need(bad.returncode != 0 and 'source SHA:' in bad.stderr
                 and 'RuntimeError: MUST_NOT_EXECUTE' not in bad.stderr,
                 'source corruption not rejected before retained import')
            source.write_bytes(original)
        receipt = package/'RESULT.json'
        expected = json.loads(receipt.read_text())
        value = json.loads(receipt.read_text())
        value['same_object_rank_after_mutation'] = True
        need(value == expected, 'bool/int equality control not effective')
        receipt.write_text(json.dumps(value))
        bad = run(package)
        need(bad.returncode != 0 and 'typed receipt mismatch' in bad.stderr,
             'corrupted receipt accepted')
    print('PASS_EISENSTEIN_INTEGER_RANK_INTEGRITY git_free=1 source_corruptions=2 receipt=1')


if __name__ == '__main__':
    main()
