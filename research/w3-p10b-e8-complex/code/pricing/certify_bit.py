"""Exact bit coarse saving + outer assembly for a PR249-format p=10 local word, using PR #315's engines
(moment.py, base_two_moment.py, outer.py) and its math_check.run logic, with a given complex coarse b."""
import sys, json, importlib.util, os
from fractions import Fraction as Q
from collections import Counter
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import cost as C
P=os.environ['PR315']+'/'
def load(n):
    s=importlib.util.spec_from_file_location(n,P+n+'.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
moment=load('moment'); other=load('base_two_moment'); outer=load('outer')
d=sys.argv[1]; b=Q(sys.argv[2]) if len(sys.argv)>2 else Q(787306366225361,10**18)
s,fr,dim,rec=C.load_snapshot(d)
H,resid,v=C.local_profile(rec,s,dim,h=20); prof,W,m,deficit=C.five_stage(H,resid,v,h=20)
T=12; norm={int(k):int(c)*T for k,c in prof.items() if c}; Wn=Q(4*v*20+resid,20)*T; assert Wn.denominator==1; Wn=int(Wn); m=100
mass=sum(k*c for k,c in norm.items()); print('normalized W',Wn,'calls',sum(norm.values()),'mass',mass,'deficit',m*Wn-mass,'maxchild',max(norm))
root=moment.certify(dict(norm),m,Wn,True); c=Q(int(Q(root['lower'])*10**18),10**18)
bm=moment.moment(norm,m,Wn,c,True); nextbm=moment.moment(norm,m,Wn,c+Q(1,10**18),True); assert bm[1]<1<nextbm[0]
fallback=32*m*m*sum(norm.values())
_,upper=other.moment(m,Wn,list(norm.items()),c); _,bad=other.moment(m,Wn,[(1,fallback)],c)
lower,_=other.moment(m,Wn,list(norm.items()),c+Q(1,10**18)); badlower,_=other.moment(m,Wn,[(1,fallback)],c+Q(1,10**18))
assert upper+Q(1,10**16)*bad<1<lower+Q(1,10**16)*badlower
print('bit coarse c =',c,float(c),'(two engines + 1e-16 fallback, adjacent grid excluded)')
grid=Q(1,10**18); eta=Q(1,10**12); beta=Q(1,10**9); cap=(1-beta)*b
sv=min(c,Q(((cap-grid)*10**18).__floor__(),10**18)); binding='bit' if sv==c else 'complex'
sm=bm if sv==c else moment.moment(norm,m,Wn,sv,True); assert 0<sv<=c and sm[1]<1
if binding=='complex': assert sv+grid>cap-grid, 'complex-bound saving not tight against the cap'
chain=[Q(384599,10**10)]
for _ in range(3):
    a=(1-sv)*sv+sv*chain[-1]; assert chain[-1]<a<sv<1-a; chain.append(a)
bit=chain[-1]
bridge=dict(proof='PROOF.md',representation='Exact powers with source-bound finite overcharges',semantic=dict(G=dict(base=2,exponent=30000),E=dict(base=2,exponent=100000),B_upper=dict(base=2,exponent=100001),C0=dict(base=2,exponent=210000),C1=1,strict_literal_gap=1,induction_gap_lower=1),rows=dict(coefficient=20161,degree=10**6,suffix_slope=4*10**6,degree_gap=Q(10**6)-Q(51*20161,25)))
q=bit*(1-2*eta); minimum=(1-eta)*q/(1+q); ticks=minimum*10**18; k=Q((ticks.numerator-1)//ticks.denominator,10**18)
asm=outer.assembly(bit,b,bridge,k,eta=eta,beta=beta); assert len(asm['strict_constraints'])==47 and min(asm['strict_constraints'].values())>0
try:
    outer.assembly(bit,b,bridge,k+Q(1,10**18),eta=eta,beta=beta); raise SystemExit('ADJACENT ADMITTED')
except AssertionError: pass
if binding=='complex':
    try: outer.assembly(cap,b,bridge,k,eta=eta,beta=beta)
    except AssertionError as e: assert 'leaf_saving_above_bit' in str(e); print('complex leaf cap itself rejected (leaf_saving_above_bit), as in PR #315 math_check')
    else: raise SystemExit('complex leaf cap admitted')
print('complex b =',b,float(b),'| binding:',binding)
print('KAPPA =',k,'=',format(float(k),'.12e'),'| 47 strict constraints positive, adjacent grid point rejected')
print('vs PR315 kappa 7.6423e-4: %+.3f%%'%(100*(float(k)/7.6423e-4-1)))
json.dump(dict(word=d,normalized_histogram=norm,W=Wn,m=m,bit_coarse=str(c),complex_coarse=str(b),binding=binding,kappa=str(k),kappa_float=float(k)),open(d+'/kappa.json','w'),indent=1)
