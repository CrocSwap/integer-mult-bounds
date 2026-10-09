"""Actual joint entrance gauges on the frozen relaxed PR211 frame word.
Experimental adapter, prepared with OpenAI Codex assistance; Apache-2.0.
Pinned supplier files are never modified.
"""
from pathlib import Path
from copy import deepcopy
from collections import defaultdict
import sys,json,hashlib
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
PACKAGE=D.parent;ROOT=PACKAGE.parents[1]
P=ROOT/'research/paired-cube-diagonal-bit-168'
sys.path.insert(0,str(P/'bit'))
from word import Candidate as Original
class Candidate(Original):
 def __init__(self):
  super().__init__()
  self.original_w=deepcopy(self.w)
  pairs=json.loads((D/'pairs.json').read_text())
  assert len(pairs)==1760 and set(b for b,d in pairs)==set(self.donor)
  assert len(set(d for b,d in pairs))==1760
  old=dict(self.pairs);changed=[(b,d) for b,d in pairs if old[b]!=d]
  assert changed==[(18892,8292),(18894,8293)]
  assert all(d not in self.source.values() and d not in self.gauge and d not in self.rootroles for b,d in changed)
  assert all(self.last[d]<self.readtime[b] for b,d in pairs)
  self.pairs=pairs;self.donor=dict(pairs);self.w['pairs']=[[d,b] for b,d in pairs]
  self.phys={s:self.donor.get(s,s) for s in range(self.R)}
  assert all(self.phys[a]!=self.phys[b] for a,b,n in self.ops)
  self.framepath=PACKAGE/'frames/opframe-bases.json'
  for i,rows in json.loads(self.framepath.read_text()):self.opframe[i]=self.register(rows)
  self.changed_frames=[i for i,(a,b) in enumerate(zip(self.original_opframe,self.opframe))if a!=b]
  self.endframe={s:self.opframe[xs[-1]]for s,xs in self.role_ops.items()}
  groups=json.loads((D/'joint-selection.json').read_text())
  oldorder=self.order[:];touched={s for i in self.phase1 for s in self.ops[i][:2]};sources=set(self.source.values())
  co=[set()for _ in range(self.R)]
  for r,s in zip(self.g['roots'],self.w['rootroles']):co[s].update(r['targets'])
  for a,b,n in reversed(self.ops):co[b].update(co[a])
  newroles=[]
  for group in groups:
   f=self.register(group['gauge_basis']);assert self.C.dimf[f] in (18,19) and self.C.nondeg(f)
   for s in group['roles']:
    assert s not in self.gauge and s not in sources and s not in touched and s not in self.donor
    assert self.C.sub(f,self.opframe[self.role_ops[s][0]])
    targets=sorted(co[s]);assert targets==group['role_targets'][str(s)]
    z=dict(role=s,frame=f,dim=self.C.dimf[f],targets=targets)
    self.gauge[s]=z;self.w['gauges'].append(z);self.w['reads'][str(s)]=len(self.phase1);self.readtime[s]=0;newroles.append(s)
  self.order=sorted(newroles,key=lambda s:self.gauge[s]['dim'])+oldorder
  assert len(newroles)==16 and len(set(newroles))==16
  self.newroles=newroles
  assert self.original_w==json.loads(__import__('gzip').decompress(self.input_paths[2].read_bytes()))
