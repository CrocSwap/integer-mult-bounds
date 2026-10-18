"""Shared helpers: input paths (relative to the package root) and PASS/FAIL printing."""
import gzip, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN = os.path.join(ROOT, 'inputs')
FAILED = []
def jgz(name):
    with gzip.open(os.path.join(IN, name)) as f:
        return json.load(f)
def jplain(name):
    with open(os.path.join(IN, name)) as f:
        return json.load(f)
def check(tag, cond, detail=''):
    print(('PASS ' if cond else 'FAIL ') + tag + (' | ' + detail if detail else ''))
    if not cond:
        FAILED.append(tag)
def done():
    sys.exit(1 if FAILED else 0)
