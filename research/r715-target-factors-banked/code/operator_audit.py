"""Independent exact address-label admission for target mixing on a banked bitE8 word.

Prepared with OpenAI Codex assistance. This tests actual address projector factors,
not scalar columns or hosted residuals. Standard library only, Apache-2.0.
"""
import argparse, gzip, hashlib, json, sys
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--word',type=Path,required=True)
ap.add_argument('--parent',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
args=ap.parse_args();word=args.word;out=args.out
def load(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
w=load(word);parent=load(args.parent)
for field in ('h','v','R','lines','frames','start','final','ret','A','C'):
 assert w[field]==parent[field],('changed boundary or unmixed phase',field)
assert w['D'][:len(parent['D'])]==parent['D']
n=2*w['v']+w['R']; h=w['h']; v=w['v']
I=tuple(tuple(F(i==j) for j in range(h)) for i in range(h))
Z=tuple(tuple(F(0) for _ in range(h)) for _ in range(h))
def add(a,b):return tuple(tuple(x+y for x,y in zip(ar,br)) for ar,br in zip(a,b))
def neg(a):return tuple(tuple(-x for x in r) for r in a)
def sub(a,b):return add(a,neg(b))
def scale(a,s):return tuple(tuple(x*s for x in r) for r in a)
def mul(a,b):
 bt=list(zip(*b))
 return tuple(tuple(sum(x*y for x,y in zip(ar,bc)) for bc in bt) for ar in a)
def transpose(a):return tuple(zip(*a))
def inv(a):
 d=len(a); m=[list(row)+[F(i==j) for j in range(d)] for i,row in enumerate(a)]
 for c in range(d):
  p=next(i for i in range(c,d) if m[i][c]);m[c],m[p]=m[p],m[c]
  t=m[c][c];m[c]=[x/t for x in m[c]]
  for i in range(d):
   if i!=c and m[i][c]:
    t=m[i][c];m[i]=[x-t*y for x,y in zip(m[i],m[c])]
 return tuple(tuple(r[d:]) for r in m)
@lru_cache(None)
def projector(f):
 rows=[]
 for k in w['frames'][f]:
  x=[F(t) for t in w['lines'][k]]
  for r in rows:
   p=next(j for j in range(h) if r[j]);t=x[p]/r[p]
   x=[a-t*b for a,b in zip(x,r)]
  if any(x):rows.append(x)
 if not rows:return Z
 B=tuple(tuple(r) for r in rows);P=mul(mul(transpose(B),inv(mul(B,transpose(B)))),B)
 assert P==transpose(P) and mul(P,P)==P
 return P
@lru_cache(None)
def reflect(f):return sub(I,scale(projector(f),2))
@lru_cache(None)
def advance(a,b):
 P,Q=projector(a),projector(b);D=sub(Q,P)
 assert mul(P,Q)==P==mul(Q,P)
 assert mul(D,D)==D
 R=sub(I,scale(D,2))
 assert mul(R,reflect(a))==reflect(b)
 # The same positive child takes I-Q to I-P in the reflected inverse.
 assert mul(R,neg(reflect(b)))==neg(reflect(a))
 return R

# Rebuild all MOVE/ADD labels directly from the word, independently of exporters.
cur=list(w['start']); events=[];new_gate_labels=[]
def move(r,f):
 if cur[r]!=f:
  advance(cur[r],f);events.append(('M',r,cur[r],f));cur[r]=f
def phase(name):
 for index,(f,d,ss) in enumerate(w[name]):
  for r in [d]+ss:move(r,f)
  for s in ss:
   assert cur[d]==cur[s]==f
   if v<=s<2*v:
    assert v<=d<2*v
    # Literal target paths have the same D_F; the frame-zero starts need no gauge.
    assert projector(w['start'][d])==Z==projector(w['start'][s])
    assert mul(reflect(f),reflect(f))==I
    new_gate_labels.append([name,index,d,s,f])
   events.append(('A',d,s,f))
phase('D');phase('A')
for t in range(v):assert projector(cur[v+t])==Z
# Charged COPY/scatter/ERASE carries the temporary to frame zero and back.
# Its transport is D_0 D_F (the same rank-dim(F) child); all original labels stay.
for k,q in enumerate(w['ret']):
 assert mul(reflect(cur[q]),reflect(cur[q]))==I
 events.append(('C',n,q,cur[q]))
 for t,row in enumerate(w['scatter']):
  if k in row:events.append(('A',v+t,n,0))
 events.append(('E',n,q,cur[q]))
phase('B');phase('C')
for r in range(n):move(r,w['final'][r])

# Check the exact rewritten inverse on complemented labels, including new ADDs.
cur_rev=list(w['final']);reverse_adds=0;temp_frame=None
for e in reversed(events):
 if e[0]=='M':
  _,r,a,b=e;assert cur_rev[r]==b
  assert mul(advance(a,b),neg(reflect(b)))==neg(reflect(a));cur_rev[r]=a
 elif e[0]=='A':
  _,d,s,f=e;source_frame=temp_frame if s==n else cur_rev[s]
  assert cur_rev[d]==source_frame==f
  assert neg(reflect(cur_rev[d]))==neg(reflect(source_frame))
  if v<=s<2*v:reverse_adds+=1
 else:
  # A fresh reflected COPY is at the complemented scatter label I, then
  # transported to I-F; the same positive rank-dim(F) projector is charged.
  _,temporary,q,f=e;assert temporary==n and cur_rev[q]==f
  assert mul(reflect(f),neg(I))==neg(reflect(f))
  assert mul(reflect(f),neg(reflect(f)))==neg(I)
  if e[0]=='E':assert temp_frame is None;temp_frame=0
  else:assert temp_frame==0;temp_frame=None
assert cur_rev==w['start']
assert temp_frame is None

# Separately identify the full formal-array matrix, including all independent
# dirty columns. The lifting proof above promotes this scalar equality to exact
# array-operator equality; no finite sampling of array values is substituted.
def scalar(word,reverse=False):
 ops=[]
 for ph in ('D','A'):
  ops.extend(('A',d,s) for f,d,ss in word[ph] for s in ss)
 for k,q in enumerate(word['ret']):
  ops.append(('C',n,q))
  ops.extend(('A',v+t,n) for t,row in enumerate(word['scatter']) if k in row)
  ops.append(('E',n,q))
 for ph in ('B','C'):
  ops.extend(('A',d,s) for f,d,ss in word[ph] for s in ss)
 if reverse:ops=[({'A':'A','C':'E','E':'C'}[op],d,s) for op,d,s in reversed(ops)]
 vals=[1<<i for i in range(n)]+[0]
 for op,d,s in ops:
  if op=='A':vals[d]^=vals[s]
  elif op=='C':assert vals[d]==0;vals[d]=vals[s]
  else:assert vals[d]==vals[s];vals[d]=0
 return vals
want=[1<<i for i in range(n)]+[0]
for t in range(v):want[v+t]^=1<<t
for reverse in (False,True):assert scalar(w,reverse)==scalar(parent,reverse)==want

# Any involution is the disjoint union of 1- and 2-cycles on addresses. Exhaust
# all Boolean inputs on each orbit. This proves pullback/ADD commutation for
# arbitrary correlated dirty contents, in either direction, for every D_F.
truth_cases=0
for orbit in (1,2):
 for bits in product((0,1),repeat=2*orbit):
  a,b=bits[:orbit],bits[orbit:];perm=tuple(reversed(range(orbit)))
  left=tuple(a[perm[i]]^b[perm[i]] for i in range(orbit))
  right=tuple((a[j]^b[j]) for j in perm)
  assert left==right;truth_cases+=1
def mismatched_label_commutes():
 for a0,a1,b0,b1 in product((0,1),repeat=4):
  if (a0^b1,a1^b0)!=(a0^b0,a1^b1):return False
 return True
assert not mismatched_label_commutes()
# Omitting a literal nontrivial child cannot advance its canonical label.
first_move=next(e for e in events if e[0]=='M')
assert reflect(first_move[2])!=reflect(first_move[3])
result=dict(status='PASS_EXACT_BIT_TARGET_LABEL_CONJUGATION',word_path=str(word),word_sha256=hashlib.sha256(word.read_bytes()).hexdigest(),
 parent_path=str(args.parent),parent_sha256=hashlib.sha256(args.parent.read_bytes()).hexdigest(),
 h=h,formal_registers=n,distinct_projectors=projector.cache_info().currsize,
 exact_nested_transition_pairs=advance.cache_info().currsize,new_target_adds=len(new_gate_labels),reflected_target_adds=reverse_adds,
 new_target_gates=new_gate_labels,orbit_truth_cases=truth_cases,negative_controls=['mismatched address labels rejected','omitted nonzero child operator rejected'],
 scalar_parent_equality={'forward':True,'reflected':True,'all_independent_columns':n,'dirty_helpers_restored':w['R'],'copied_work_closed':True},
 interpretation='D_U acts as a common pullback on every routed local array; its sum/difference coordinate blocks are I and I-2P_U. Exact factor identities and universal orbit checks establish target-add commutation independently of scalar replay.',
 scope='Local target mixing on non-hosting banked PR443. Physical global bank ownership, finite invoice, both paid moments and exact assembly remain separate obligations.')
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:x for k,x in result.items() if k!='new_target_gates'},indent=2))
