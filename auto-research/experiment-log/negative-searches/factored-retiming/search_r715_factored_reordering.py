"""Search frame changes with stable B reordering; preserve all noncommuting gate orders."""
from pathlib import Path
from collections import Counter,defaultdict
import json,sys,math,hashlib
r=Path.cwd();src=Path(sys.argv[1]) if len(sys.argv)>1 else r/'r715-rekernel-publication/research/r715-retimed-kernel-pool/data/word.json';out=Path(sys.argv[2]) if len(sys.argv)>2 else r/'r715-reordered-b-search';assert not out.exists();out.mkdir()
sys.path.insert(0,str(r/'source454-review/e8-r740-replica32/code'));import e8core as E
w=json.loads(src.read_text());L=E.Lat(w['lines']);fs=E.to_masks(w,L);dims=[L.dim(f) for f in fs];v=w['v'];n=2*v+w['R'];baseline=E.replay(w,L=L,masks=fs,span_mode='z');assert not baseline['viol']
# Every destination is a target, with one helper or target operand; helpers are constant in B.
assert all(v<=d<2*v and len(ss)==1 and ss[0]>=v for f,d,ss in w['B'])
gates=w['B'];regs=[(d,ss[0]) for f,d,ss in gates];frames=[f for f,d,ss in gates];initial=frames[:]
left=w['start'][:];right=w['final'][:];support=[1<<i if i<v else 0 for i in range(n)]
for ph in ('D','A'):
 for f,d,ss in w[ph]:
  for x in [d]+ss:left[x]=f
  for s in ss:support[d]|=support[s]
for g in reversed(w['C']):
 f,d,ss=g
 for x in [d]+ss:right[x]=f
for x in range(v,2*v):assert left[x]==0
byreg=defaultdict(list)
for i,rr in enumerate(regs):
 for x in rr:byreg[x].append(i)
deps=[]
for i,(_,d,ss) in enumerate(gates):
 for j in range(i+1,len(gates)):
  _,e,tt=gates[j]
  if d in tt or e in ss:deps.append((i,j))
depof=defaultdict(list)
for a,b in deps:depof[a].append((a,b));depof[b].append((a,b))
def key(i,nf=None,change=None):return (dims[nf if i==change else frames[i]],i)
assert all(key(a)<key(b) for a,b in deps),'initial stable rank order changes a dependent pair'
from fractions import Fraction
c=float(Fraction(json.loads((r/'r715-factor-replica64-strong-RESULT.json').read_text())['bit_lower']));cost=lambda d:d*math.expm1(c*math.log(78/d))/c if d else 0
def chaincost(x,i=None,nf=None):
 ff=[left[x]]+sorted({nf if j==i else frames[j] for j in byreg[x]},key=lambda f:dims[f])+[right[x]]
 if any(fs[a]&~fs[b] for a,b in zip(ff,ff[1:])):return None
 return sum(cost(dims[b]-dims[a]) for a,b in zip(ff,ff[1:]))
for x in byreg:assert chaincost(x) is not None
needs=[]
for f,d,ss in gates:
 need=0
 for operand in ss:need|=support[operand];support[d]|=support[operand]
 needs.append(need)
history=[];tested=0
for sweep in range(12):
 moves=0
 for i,(d,s) in enumerate(regs):
  old=frames[i];before=sum(chaincost(x) for x in regs[i]);need=needs[i];best=None
  for nf,mask in enumerate(fs):
   if nf==old or need&~mask:continue
   if any(fs[left[x]]&~mask or mask&~fs[right[x]] for x in regs[i]):continue
   if any(not(key(a,nf,i)<key(b,nf,i)) for a,b in depof[i]):continue
   vals=[chaincost(x,i,nf) for x in regs[i]];tested+=1
   if any(t is None for t in vals):continue
   delta=sum(vals)-before
   if delta<-1e-8 and (best is None or delta<best[0]):best=(delta,nf)
  if best:
   delta,nf=best;frames[i]=nf;history.append(dict(gate=i,old=old,new=nf,delta=delta));moves+=1
 print('sweep',sweep,'moves',moves,'total',len(history),flush=True)
 if not moves:break
w['B']=[[frames[i],gates[i][1],gates[i][2]] for i in sorted(range(len(gates)),key=key)]
a=E.replay(w,L=L,masks=fs,span_mode='z');assert not a['viol'];assert sum(k*n for k,n in a['H'].items())==sum(k*n for k,n in baseline['H'].items())
raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode();(out/'WORD.json').write_bytes(raw)
res=dict(status='PASS_REORDERED_B_LOCAL_GLOBAL_PENDING' if history else 'PASS_NO_REORDERED_B_GAIN',source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),word_sha256=hashlib.sha256(raw).hexdigest(),changes=history,noncommuting_pairs=len(deps),candidates_tested=tested,profile=dict(a['H']),original_profile=dict(baseline['H']))
(out/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(res['status'],dict(a['H']),flush=True)
