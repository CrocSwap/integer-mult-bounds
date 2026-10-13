"""Loader shared by the global admission scripts.

WITNESS.json holds inputs only: shape, dispatch, call order and hash pins of PLAN/OWNERS. The scripts compute from it.
EXPECTED.json holds expected values only. pin(key, got) compares a value the script has already recomputed against
EXPECTED; nothing read from EXPECTED feeds a computation. WITNESS_DISCOVER=1 runs the same recomputation without
EXPECTED (pin() returns the recomputed value); spec.py uses that once to write EXPECTED.json.
"""
import json,os
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
WITNESS=json.loads(Path(os.environ['WITNESS_FILE']).read_text())
DISCOVER=os.environ.get('WITNESS_DISCOVER')=='1'
EXPECTED=None if DISCOVER else json.loads(Path(os.environ['WITNESS_EXPECTED']).read_text())
DISPATCH={(s,r):p for s,r,p in WITNESS['dispatch']}
CALL_ORDER=[tuple(x)for x in WITNESS['call_order']]
PIDS=tuple(sorted(set(DISPATCH.values())))
COUNTS=dict(Counter(DISPATCH.values()))
_g=WITNESS['geometry']
geo=SimpleNamespace(v=_g['v'],h=_g['h'],helpers=_g['helpers'],centres=_g['centres'],stages=_g['stages'],replicas=_g['replicas'],
 cold_helpers=tuple(_g['cold_helpers']),columns=2*_g['v']+_g['helpers'],calls=_g['stages']*_g['replicas'])
assert len(DISPATCH)==len(CALL_ORDER)==geo.calls,'dispatch/call_order must cover stages*replicas calls'
def lookup(key):
 """Dotted EXPECTED path; a segment may itself contain dots when it names a file."""
 v=EXPECTED;parts=key.split('.')
 while parts:
  for n in range(len(parts),0,-1):
   k='.'.join(parts[:n])
   if isinstance(v,dict) and k in v:v=v[k];parts=parts[n:];break
  else:raise KeyError('EXPECTED has no key %s'%key)
 return v
def pin(key,got):
 """Strict mode: the recomputed value got must equal EXPECTED at dotted key; the failure names the key."""
 if DISCOVER:return got
 want=lookup(key)
 assert got==want,'SPEC MISMATCH %s: expected %s got %s'%(key,json.dumps(want)[:400],json.dumps(got,default=str)[:400])
 return got
def partner(pid):
 """A different provider for substitution controls (next in sorted order)."""
 assert len(PIDS)>1
 return PIDS[(PIDS.index(pid)+1)%len(PIDS)]
