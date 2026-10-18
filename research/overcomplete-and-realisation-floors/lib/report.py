"""One PASS/FAIL line per assertion, so verify.sh can count them.  A check script exits 1 if any of its lines failed."""
import sys
_fails = 0
_n = 0


def check(ident, cond, msg):
    global _fails, _n
    _n += 1
    if not cond:
        _fails += 1
    print('%s %s  %s' % ('PASS' if cond else 'FAIL', ident, msg), flush=True)


def finish():
    sys.exit(1 if _fails else 0)
