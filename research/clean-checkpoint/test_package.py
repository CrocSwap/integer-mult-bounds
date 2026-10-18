#!/usr/bin/env python3
"""Portable-package and optimized-mode corruption controls (standard library)."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, help='existing parent for temporary copies')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='checkpoint-controls-', dir=args.work) as temp:
        copied = Path(temp) / 'relocated package with spaces'
        shutil.copytree(HERE, copied, ignore=shutil.ignore_patterns('__pycache__'))
        def run(marker, success):
            result = subprocess.run([sys.executable, '-I', '-O', '-B',
                                     str(copied/'verify.py')],
                                    cwd=temp, capture_output=True, text=True)
            output = result.stdout+result.stderr
            need((result.returncode == 0) == success and marker in output,
                 'unexpected subprocess result: '+output)
        run('PASS_CLEAN_CHECKPOINT', True)
        source = copied/'vendor/pr628-dirty.py'
        original = source.read_bytes()
        source.write_bytes(original+b'\n# corrupted source\n')
        run('source SHA256', False)
        source.write_bytes(original)
        expected = copied/'EXPECTED.json'
        original_receipt = expected.read_bytes()
        data = json.loads(original_receipt)
        data['selected']['leaf_calls'] -= 1
        expected.write_text(json.dumps(data))
        run('complete certificate mismatch', False)
        expected.write_bytes(original_receipt)
        adapter = copied/'checkpoint.py'
        text = adapter.read_text()
        guard = "need(all(v == c.ZERO for v in clean), 'checkpoint must initially be zero')"
        need(text.count(guard) == 1, 'unique clean guard mutation site')
        adapter.write_text(text.replace(guard, 'pass  # deliberately removed clean guard'))
        run('accepted interface control: dirty', False)
        guard = "need(all(phases is not a for a in arrays), 'phase array must be distinct')"
        need(text.count(guard) == 1, 'unique phase guard mutation site')
        adapter.write_text(text.replace(guard, 'pass  # deliberately removed phase guard'))
        run('accepted interface control: phase_alias_0', False)
    print('PASS_PACKAGE_CONTROLS: relocation; source, receipt, clean-guard and phase-guard corruptions rejected under -I -O')


if __name__ == '__main__':
    main()
