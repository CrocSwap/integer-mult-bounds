"""Preserve the eighth registered replay and append accepted grid checks.

All scientific programs and source bytes are frozen. New receipts are written
into disposable copies and compared with the published normal/optimized ones.
"""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate():
    frozen = json.loads((HERE/'FROZEN.json').read_text())
    for relative, expected in frozen['files'].items():
        need(sha256((HERE/relative).read_bytes()).hexdigest() == expected,
             'frozen grid source or review changed: '+relative)


def run(argv, cwd, timeout):
    print('REPLAY '+' '.join(map(str, argv)), flush=True)
    subprocess.run(list(map(str, argv)), cwd=cwd, check=True, timeout=timeout)


def grid_replay():
    with TemporaryDirectory(prefix='circulant-grid-replay-') as directory:
        temporary = Path(directory)
        copied = temporary/'grid-arithmetic'
        shutil.copytree(HERE, copied)
        for optimized in (False, True):
            mode = 'optimized' if optimized else 'normal'
            evidence = 'EVIDENCE-OPTIMIZED.json' if optimized else 'EVIDENCE.json'
            # The frozen author program imports its sibling module. Preserve
            # its original -B invocation; the independent checker uses -I.
            flags = [sys.executable, *(['-O'] if optimized else []), '-W', 'error', '-B']
            author = temporary/('author-'+mode+'.json')
            run([*flags, copied/'check.py', '--output', author], temporary, 120)
            need(author.read_bytes() == (HERE/evidence).read_bytes(), 'fresh author receipt differs')
            review = temporary/('review-'+mode+'.json')
            run([*flags[:1], '-I', *flags[1:], copied/'review/independent.py',
                 '--source', copied, '--output', review], temporary, 120)
            need(review.read_bytes() == (HERE/'review'/evidence).read_bytes(),
                 'fresh independent receipt differs')


def main():
    authenticate()
    run([sys.executable, '-I', '-W', 'error', '-B',
         PACKAGE/'reconciliation/replay.py', '--additions'], PACKAGE, 480)
    grid_replay()
    authenticate()
    print('PASS_PRESERVED_ADDITIONS_AND_GRID_ARITHMETIC', flush=True)


if __name__ == '__main__':
    main()
