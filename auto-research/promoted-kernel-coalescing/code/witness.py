"""Strict frozen witness specification. Pins are compared after independent recomputation.
Discovery mode is disabled in this package. Prepared with OpenAI Codex assistance.
Adapted from PR576; Apache-2.0.
"""
import json,os
from collections import Counter
from pathlib import Path
SPEC=json.loads(Path(os.environ['WITNESS_SPEC']).read_text())
assert os.environ.get('WITNESS_DISCOVER')!='1', 'Discovery is disabled in the frozen admission package'
DISCOVER=False
X=SPEC.get('expected',{})
PROVIDERS=SPEC.get('providers',{})
DISPATCH={(s,r):p for s,r,p in SPEC['dispatch']}
CALL_ORDER=[tuple(x)for x in SPEC['call_order']]
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
 if DISCOVER:return got
 want=lookup(key)
 assert got==want,'SPEC MISMATCH %s: expected %s got %s'%(key,json.dumps(want)[:400],json.dumps(got,default=str)[:400])
 return got
def partner(pid):
 """A different provider for substitution controls (next in sorted order)."""
 assert len(PIDS)>1
 return PIDS[(PIDS.index(pid)+1)%len(PIDS)]
