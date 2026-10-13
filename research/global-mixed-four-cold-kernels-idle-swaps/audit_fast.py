"""Run audit_allcold.py unchanged, with copy.deepcopy replaced by an equivalent pickle round-trip.

The audit's 23 mutation controls each deep-copy the whole global template (~90% of its runtime). For the plain
dict/list/tuple/int/str data used there, pickle.loads(pickle.dumps(x)) yields an equal, independent copy with the same
internal aliasing as copy.deepcopy; no audited value, check or output changes. Usage: audit_fast.py AUDIT_SCRIPT args...
"""
import copy, pickle, runpy, sys

_real = copy.deepcopy


def _fast(x, memo=None):
    if memo is not None:
        return _real(x, memo)
    return pickle.loads(pickle.dumps(x, pickle.HIGHEST_PROTOCOL))


copy.deepcopy = _fast
script = sys.argv[1]
sys.argv = sys.argv[1:]
runpy.run_path(script, run_name='__main__')
