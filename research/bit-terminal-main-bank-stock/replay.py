"""Recompute both frozen receipts from the three exact in-tree BIT sources."""
from pathlib import Path
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def verify(script, expected, *args):
    argv = [sys.executable, '-I', '-B', str(PACKAGE / script), *map(str, args)]
    actual = subprocess.run(argv, cwd=ROOT, check=True, stdout=subprocess.PIPE).stdout
    if actual != (PACKAGE / expected).read_bytes():
        raise ValueError(f'frozen receipt mismatch: {expected}')


if __name__ == '__main__':
    if sys.implementation.name != 'cpython' or sys.version_info[:2] != (3, 12) or not __debug__:
        raise SystemExit('Use CPython 3.12 with assertions enabled')
    verify('verify.py', 'RESULT.json', ROOT)
    word = ROOT / 'research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz'
    verify('audit.py', 'AUDIT.json', word, PACKAGE / 'RESULT.json')
    print('PASS_BIT_TERMINAL_MAIN_BANK_STOCK_AND_INDEPENDENT_AUDIT')
