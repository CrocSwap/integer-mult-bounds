#!/usr/bin/env python3
"""Git-free export and source/receipt controls; ywz65 with OpenAI Codex."""
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


def run(package, *args):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py'), *args],
                          capture_output=True, text=True, timeout=180)


def main():
    with tempfile.TemporaryDirectory(prefix='qq16-caller-grid-') as tmp:
        root = Path(tmp)/'export'
        package = root/'research'/HERE.name
        shutil.copytree(HERE, package)
        for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if item['usage'] == 'input':
                target = root/item['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT/item['path'], target)
        good = run(package)
        need(good.returncode == 0 and 'PASS_QQ16_CALLER_GRID' in good.stdout,
             'Git-free replay failed: '+good.stderr)
        for source, error in (
            (package/'vendor/pr2540/verify.py', 'snapshot hash:'),
            (package/'vendor/pr2540/WORD.json', 'snapshot hash:'),
            (root/'research/joint-query/evidence/BRIDGE-REVIEW.md', 'input hash:')):
            original = source.read_bytes()
            source.write_bytes(b"raise RuntimeError('MUST_NOT_EXECUTE')\n"+original)
            bad = run(package, '--authenticate-only')
            need(bad.returncode != 0 and error in bad.stderr
                 and 'RuntimeError: MUST_NOT_EXECUTE' not in bad.stderr,
                 'corrupt source not rejected before retained import')
            source.write_bytes(original)
        receipt = package/'RESULT.json'
        expected = json.loads(receipt.read_text())
        changed = json.loads(receipt.read_text())
        changed['controls']['six_fraction_bits_reject_single_term'] = 1
        need(changed == expected, 'bool/int equality control is not effective')
        receipt.write_text(json.dumps(changed))
        bad = run(package)
        need(bad.returncode != 0 and 'typed receipt mismatch' in bad.stderr,
             'typed receipt mutation accepted')
    print('PASS_QQ16_CALLER_INTEGRITY git_free=1 source_corruptions=3 typed_receipt=1')


if __name__ == '__main__':
    main()
