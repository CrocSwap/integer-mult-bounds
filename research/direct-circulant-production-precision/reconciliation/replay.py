"""Path-only replay adapter preserving frozen publication bytes.

The original seven registered checks retain their source programs and flags.
The four compiler-cut checks execute in disposable byte-identical copies so
their regenerated elapsed-time receipts cannot rewrite the published review.
The eighth registration executes the added interval/selector checks similarly.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def authenticate():
    receipt = json.loads((HERE / 'PRESERVED-CUTS.json').read_text())
    require(sha256((HERE / 'REMOTE-VERIFY.json').read_bytes()).hexdigest()
            == receipt['remote_verify_sha256'], 'original remote verification commands changed')
    for row in receipt['files']:
        data = (PACKAGE / row['path']).read_bytes()
        require(sha256(data).hexdigest() == row['sha256'], 'preserved remote file changed: ' + row['path'])
    for path, expected in json.loads((HERE / 'FROZEN-ADDITIONS.json').read_text()).items():
        require(sha256((PACKAGE / path).read_bytes()).hexdigest() == expected,
                'frozen supplement changed: ' + path)


def compare(actual, frozen, elapsed=False):
    left, right = json.loads(actual.read_text()), json.loads(frozen.read_text())
    if elapsed:
        left.pop('seconds', None)
        right.pop('seconds', None)
    require(left == right, 'replayed proof-relevant receipt changed: ' + str(frozen))


def run(argv, cwd, seconds):
    print('REPLAY ' + ' '.join(map(str, argv)), flush=True)
    subprocess.run(list(map(str, argv)), cwd=cwd, timeout=seconds, check=True)


def legacy(index, temporary, copied):
    require(index in range(3, 7), 'select one of the four preserved compiler checks')
    command = json.loads((HERE / 'REMOTE-VERIFY.json').read_text())['commands'][index]
    argv = [sys.executable if arg == '{python}' else arg.replace('{package}', str(copied))
            for arg in command['argv']]
    if index in (3, 4):
        relative = 'compiler-cuts/EVIDENCE.json'
        actual = copied / relative
    else:
        relative = 'compiler-cuts/review/' + ('EVIDENCE.json' if index == 5 else 'EVIDENCE-OPTIMIZED.json')
        # The newer remote command already redirects its receipt outside the
        # package. Give that same output a private per-run location as well.
        output_index = argv.index('--output') + 1
        actual = temporary / ('legacy-normal.json' if index == 5 else 'legacy-optimized.json')
        argv[output_index] = str(actual)
    run(argv, temporary, command['timeout_seconds'])
    compare(actual, PACKAGE / relative, elapsed=True)
    print('PASS_PRESERVED_COMPILER_REPLAY ' + str(index), flush=True)


def additions(temporary, copied):
    cuts = copied / 'compiler-intervals'
    sharp = copied / 'spectral-downset'
    python = [sys.executable, '-I', '-W', 'error', '-B']
    run([*python, cuts / 'audit.py'], temporary, 300)
    compare(cuts / 'EVIDENCE.json', PACKAGE / 'compiler-intervals/EVIDENCE.json')
    for optimized in (False, True):
        flags = [sys.executable, '-I', *(['-O'] if optimized else []), '-W', 'error', '-B']
        output = temporary / ('interval-optimized.json' if optimized else 'interval-normal.json')
        run([*flags, cuts / 'review/independent.py', '--source', cuts, '--output', output], temporary, 120)
        compare(output, PACKAGE / 'compiler-intervals/review/EVIDENCE.json')
    # This explicit path is the only adaptation to the frozen source checker.
    run([*python, sharp / 'check.py', '--parent', copied, '--cuts', cuts], temporary, 60)
    compare(sharp / 'EVIDENCE.json', PACKAGE / 'spectral-downset/EVIDENCE.json')
    for optimized in (False, True):
        flags = [sys.executable, '-I', *(['-O'] if optimized else []), '-W', 'error', '-B']
        output = temporary / ('selector-optimized.json' if optimized else 'selector-normal.json')
        run([*flags, sharp / 'review/independent.py', '--candidate', sharp,
             '--cuts', cuts, '--parent', copied, '--output', output], temporary, 120)
        compare(output, PACKAGE / 'spectral-downset/review/EVIDENCE.json')
    print('PASS_RELATIVE_INTERVAL_AND_SHARP_SELECTOR_ADDITIONS', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--legacy', type=int)
    choice.add_argument('--additions', action='store_true')
    args = parser.parse_args()
    authenticate()
    with TemporaryDirectory(prefix='circulant-reconciled-replay-') as directory:
        temporary = Path(directory)
        copied = temporary / 'package'
        shutil.copytree(PACKAGE, copied)
        if args.legacy is not None:
            legacy(args.legacy, temporary, copied)
        else:
            additions(temporary, copied)
    authenticate()


if __name__ == '__main__':
    main()
