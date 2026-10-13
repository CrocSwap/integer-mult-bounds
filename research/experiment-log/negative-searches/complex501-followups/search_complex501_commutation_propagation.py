"""Proven scalar commutations plus local frame reassignment, nomination only."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import sys,json,gzip,copy,math,time,hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'source496-review/vendor/complex/e8-complex-gauge-kernel/code'));import gk_word as G
O=R/'complex501-commutation-propagation';O.mkdir(exist_ok=False);W=json.load(gzip.open(R/'pr501-retimed-word.json.gz'));base=G.profile(W);widths=G.widths_of(W);b=float(Fraction(json.load(open(R/'source501-delta-review/EXPECTED.json'))['complex_lower']));cost=lambda r:r*math.expm1(b*math.log(73/r))/b+32*73**2/1e16*73**b/b if r else 0
basecost=sum(cost(r)*n for r,n in base.items());bestcost=basecost;ledger=[];t0=time.monotonic()
def regs(e):return set(e[1:3]) if e[0]=='add' else {e[1]}
def commute(e,f):
 if e[0]==f[0]=='add':return e[1]!=f[2] and f[1]!=e[2]
 if e[0]==f[0]=='scale':return True
 s,a=(e,f) if e[0]=='scale' else (f,e)
 return s[3]!=0 and (s[2]==s[3] or s[1] not in regs(a))
def propagate(w,direction):
 n=240+w['report']['R'];start={r:G.basis([w['ports'][r]]) if r<120 else G.basis(w.get('start_extra',{}).get(str(r),[])) if r>=240 else () for r in range(n)};end={r:G.perp(w['ports'][r-120]) if 120<=r<240 else G.FULL for r in range(n)}
 cur=start if direction=='up' else end
 for part in (['A','B'] if direction=='up' else ['B','A']):
  if direction=='down' and part=='A':
   for r,F in zip(w['centers'],w['center_frames']):cur[r]=G.basis(F)
   for t in range(120):cur[120+t]=G.basis(w.get('target_levels',{}).get(str(t),[]))
  for e in (w[part] if direction=='up' else reversed(w[part])):
   rr=regs(e);old=G.basis(e[-1])
   nf=G.basis(list(old)+[v for r in rr for v in cur[r]]) if direction=='up' else G.basis(set.intersection(G.span(old),*(G.span(cur[r]) for r in rr)))
   e[-1]=list(nf)
   for r in rr:cur[r]=nf
 return w
for part in ['A','B']:
 for j in range(531 if part=='A' else 0,len(W[part])-1):
  e,f=W[part][j:j+2]
  if not regs(e)&regs(f) or not commute(e,f) or G.basis(e[-1])==G.basis(f[-1]):continue
  for direction in ['up','down']:
   w=copy.deepcopy(W);w[part][j:j+2]=[copy.deepcopy(f),copy.deepcopy(e)];row=dict(part=part,index=j,direction=direction)
   try:
    w=propagate(w,direction);assert w['A'][:531]==W['A'][:531],'gauge prelude changed';H=G.profile(w);assert G.widths_of(w)==widths,'entrance widths changed';value=sum(cost(r)*n for r,n in H.items());row.update(status='PASS_LOCAL_PROFILE_ONLY',delta_float=value-basecost,profile=dict(sorted(H.items())))
    if value<bestcost-1e-9:
     bestcost=value;candidate=w;candidate['cleanup']=[G.inverse(z,G.FULL) for z in reversed(candidate['A']+candidate['B']) if not 120<=z[1]<240];candidate['report']['local_profile']={str(r):n for r,n in sorted(H.items())};raw=json.dumps(candidate,sort_keys=True,separators=(',',':')).encode();(O/'BEST-WORD.json.gz').write_bytes(gzip.compress(raw,mtime=0));(O/'BEST.json').write_text(json.dumps(row,indent=2)+'\n');print('NEW BEST',row,flush=True)
   except AssertionError as err:row.update(status='REJECTED_LOCAL_PROFILE',error=str(err))
   ledger.append(row)
(O/'LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n');result=dict(trials=len(ledger),outcomes=dict(Counter(x['status'] for x in ledger)),improvement_float=basecost-bestcost,seconds=time.monotonic()-t0,scope='Adjacent algebraically commuting operations only; entrances preserved. Any lower local score still needs exact global pricing and full physical admission.')
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True)
