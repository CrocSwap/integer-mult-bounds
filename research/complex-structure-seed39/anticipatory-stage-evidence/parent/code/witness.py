"""Spec loader: spec values are EXPECTED values, compared only after independent recomputation.
WITNESS_DISCOVER=1 runs the same recomputation without comparing pinned values (pin() records only);
it is used once to produce outputs for generate_spec.py, after which the strict run must pass.
"""
import json,os
from collections import Counter
from pathlib import Path
SPEC=json.loads(Path(os.environ['WITNESS_SPEC']).read_text())
DISCOVER=os.environ.get('WITNESS_DISCOVER')=='1'
X=SPEC.get('expected',{})
PROVIDERS=SPEC.get('providers',{})
DISPATCH={(s,r):p for s,r,p in SPEC['dispatch']}
CALL_ORDER=[tuple(x)for x in SPEC['call_order']]
# width-8 spot helpers: PR558's helpers 270, 282, 294, 306, or their images under a K-triangle word's 504 -> R helper map
# (verify.py checks the spec value against the constructor's HELPER-MAP.json)
SPOT=tuple(SPEC.get('width_spot_helpers',(270,282,294,306)))
# A pivot swap moves a kernel family's pivot role p -> x; the old pivot p becomes an ordinary cold helper and its width
# goes 8 -> 9 (construction/layers, PR641 PROOF-NOTE-PIVOT). Expected spot widths are derived from the package's pinned
# pivot-swap recipe (path and sha256 in the spec), not from free data: 9 at a swapped-out pivot, 8 otherwise.
_PKG=Path(os.environ['WITNESS_SPEC']).resolve().parents[1]
def _old_pivots():
 ps=SPEC.get('pivot_swap')
 if not ps:return frozenset()
 raw=(_PKG/ps['recipe']).read_bytes();import hashlib
 assert hashlib.sha256(raw).hexdigest()==ps['sha256'],'pivot-swap recipe pin'
 return frozenset(s['pivot']for s in json.loads(raw)['swaps'])
OLD_PIVOTS=_old_pivots()
def spot_widths(v=112):
 """Expected residual widths at the spot helpers (helper indices) of the gauge44 provider."""
 return tuple(9 if 2*v+h in OLD_PIVOTS else 8 for h in SPOT)
PIDS=tuple(sorted(set(DISPATCH.values())))
COUNTS=dict(Counter(DISPATCH.values()))
assert DISCOVER or set(PROVIDERS)==set(PIDS),'spec providers differ from dispatch providers'
def lookup(key):
 """Dotted spec path; a segment may itself contain dots when it names a file (split at most once per known file suffix)."""
 v=SPEC;parts=key.split('.')
 while parts:
  for n in range(len(parts),0,-1):
   k='.'.join(parts[:n])
   if isinstance(v,dict) and k in v:v=v[k];parts=parts[n:];break
  else:raise KeyError('spec has no key %s'%key)
 return v
def pin(key,got):
 """Strict mode: got must equal the spec value at dotted key; the failure names the key."""
 if DISCOVER:
  if os.environ.get('WITNESS_RECORD'):   # discovery bookkeeping only: append (key, value) for the spec writer
   with open(os.environ['WITNESS_RECORD'],'a')as f:f.write(json.dumps([key,got],default=str)+chr(10))
  return got
 want=lookup(key)
 assert got==want,'SPEC MISMATCH %s: expected %s got %s'%(key,json.dumps(want)[:400],json.dumps(got,default=str)[:400])
 return got
def partner(pid):
 """A different provider for substitution controls (next in sorted order)."""
 assert len(PIDS)>1
 return PIDS[(PIDS.index(pid)+1)%len(PIDS)]

# Replica-sensitive quantities are frozen by the independently checked parent lift.
GEO=SPEC['geometry']
REPLICAS=GEO['replicas']; CALLS=GEO['stages']*REPLICAS
assert type(REPLICAS) is int and REPLICAS>0
assert (GEO['stages'],GEO['pairs'],GEO['dimension'])==(9,4,73)
assert set(CALL_ORDER)=={(s,r) for s in range(GEO['stages']) for r in range(REPLICAS)}
DATA=2*112*GEO['pairs']*REPLICAS
DEFICIT=DATA-64*CALLS
PAYLOAD=GEO['charged_prefix_bits']
assert PAYLOAD==1<<(192+(GEO['dimension']+1)//2+2*CALLS+4).bit_length()
PARENT_LIVE=GEO['parent_live'];PARENT_PHYSICAL=GEO['parent_physical'];PARENT_IDLE=GEO['parent_idle'];PARENT_HELPERS=GEO['parent_helpers']
assert PARENT_PHYSICAL==PARENT_LIVE+PARENT_HELPERS+8+2
