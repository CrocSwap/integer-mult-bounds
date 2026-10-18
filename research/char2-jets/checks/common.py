"""Shared helpers of the checks: path bootstrap and PASS/FAIL reporting (one line per assertion; exit status 1 on any FAIL)."""
import os, sys, time
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG + '/lib')
import kit
kit.BIN = os.environ.get('TTD_BIN') or PKG + '/c/bin'
BAD = [0]; T0 = [time.time()]
def report(name, ok, msg=''):
    print('%s %s  %s' % ('PASS' if ok else 'FAIL', name, msg), flush=True)
    if not ok: BAD[0] += 1
def done():
    print('   (%.1fs)' % (time.time() - T0[0]), flush=True)
    sys.exit(1 if BAD[0] else 0)
