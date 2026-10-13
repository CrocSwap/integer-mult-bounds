"""Derive an exact scalable whole-family assignment from a fractional pattern solution.
Floating discovery is followed by rational equalities and two independent moment checks.
No claim that a floating LP proves global optimality, or that aggregate slots are admitted.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
from math import lcm,expm1,log
import json,sys,types,hashlib
r=Path.cwd();out=r/'r715-rational-hosting-fixed';assert not out.exists();out.mkdir()
sys.path[:0]=[str(r/'complex447-search'),str(r/'source450-review/code'),str(r/'source443-review/code/engines')]
import hosting_core as HC,moment as M,base_two_moment as M2
src=r/'source450-review/code/hosting_k.py';s=src.read_text().split('\ndef solve_tape',1)[0]
s=s.replace('integ = np.ones(n)','integ = np.zeros(n)').replace('x = [int(round(t)) for t in res.x]','from fractions import Fraction\n    x = [Fraction(float(t)).limit_denominator(1000000) for t in res.x]')
HK=types.ModuleType('fractional_hosting');HK.__file__=str(src);exec(s,HK.__dict__)
local=json.loads((r/'r715-factored-replica-screen/WORD/LOCAL.json').read_text());widths=local['widths'];H={int(k):v for k,v in local['profile'].items()}
ns={};text=(r/'screen_whole454_complex.py').read_text();exec(('def schedule(K):'+text.split('def schedule(K):',1)[1].split('\nfor L,T in',1)[0]).replace('rank=8*','rank=7*'),ns)
K=5;m=78;stages=2*K+1;sc=ns['schedule'](K);win={i:x for i,x in HC.windows(sc).items() if x[1] and x[2]};counts=Counter(widths);avail={(s,w):n for s in range(stages) for w,n in counts.items()};copies=240
current=Q(json.loads((r/'r715-factor-replica64-strong-RESULT.json').read_text())['bit_lower']);c=float(current);HK.cost=lambda rank,m:rank*expm1(c*log(m/rank))/c if rank else 0
ys,zs,_=HK.solve(win,copies,avail,m,host_all=True,maxk=max(x[1] for x in win.values())//min(widths))
for i in win:
 assert sum(n for (ii,pat),n in ys.items() if ii==i)==copies
 for w in counts:
  assert sum(n*pat.count(w) for (ii,pat),n in ys.items() if ii==i)==sum(n for (ii,ww,s),n in zs.items() if ii==i and ww==w)
for (s,w),n in avail.items():assert sum(k for (i,ww,ss),k in zs.items() if ss==s and ww==w)==n
assert all(n>=0 for n in list(ys.values())+list(zs.values()))
T=lcm(*(n.denominator for n in list(ys.values())+list(zs.values())));y={k:int(n*T) for k,n in ys.items()};z={k:int(n*T) for k,n in zs.items()};assert all(Q(y[k],T)==n for k,n in ys.items()) and all(Q(z[k],T)==n for k,n in zs.items())
HC.save_selection(out/'SELECTION.json','bit',y,z,0)
P=Counter({rank:n*stages*T for rank,n in H.items()})
for e in sc:
 if e['kind']=='idle' and e['idx'] not in win and e['rank']>0:P[e['rank']]+=copies*T
for (i,pat),n in y.items():
 rank=win[i][1]-sum(pat);assert rank>=0
 if rank:P[rank]+=n
W=copies*K*T;assert m*W-sum(rank*n for rank,n in P.items())==408*T
cert=M.certify(P,m,W,True);lo,hi=Q(cert['lower']),Q(cert['upper'])
for x,below in [(lo,True),(hi,False)]:
 a,b=M2.moment(m,W,list(P.items()),x);d,e=M2.moment(m,W,[(1,32*m*m*sum(P.values()))],x);assert b+e/10**16<1 if below else a+d/10**16>1
result=dict(status='PASS_EXACT_RATIONAL_PATTERN_COUNTS_AND_TWO_MOMENTS',replicas=T,bit_lower=str(lo),bit_upper=str(hi),profile=dict(sorted(P.items())),projected_kappa=float(lo/(1+lo)),gain_over_replica64_bit=float(lo/current-1),source_local_sha256=hashlib.sha256((r/'r715-factored-replica-screen/WORD/LOCAL.json').read_bytes()).hexdigest(),scope='Exact nonnegative integral scaled assignment satisfying every pattern/stage/width equality and both moment checks; explicit per-helper expansion, native physical replay, prefixes and final composition pending. No LP optimality theorem claimed.')
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
