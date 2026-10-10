import sys, json, collections
import os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from fractions import Fraction as Q
import fixed_prime_math as R
from cost import load_snapshot, local_profile, five_stage
cost=R.load('moment',os.path.join(HERE,'moment.py')); other=R.load('base_two_moment',os.path.join(HERE,'base_two_moment.py')); outer=R.load('outer',os.path.join(HERE,'outer.py'))
d=sys.argv[1]; complex_saving=Q(sys.argv[2]) if len(sys.argv)>2 else R.COMPLEX_SAVING
s,fr,dim,rec=load_snapshot(d)
H,resid,v=local_profile(rec,s,dim)
prof,W,m,deficit=five_stage(H,resid,v)
Wq=Q(4*v)+Q(resid,24); scale=8
assert (Wq*scale).denominator==1
stock=int(Wq*scale); hist={int(k):int(n)*scale for k,n in prof.items()}; calls=sum(hist.values())
mass=sum(r*n for r,n in hist.items())
print('stock',stock,'calls',calls,'mass',mass,'deficit',120*stock-mass)
coarse,nxt,first,first_next,second,second_next=R.certify_coarse(hist,120,stock,calls,cost,other)
cap=R.grid_kappa(coarse)
chain=[R.INITIAL_LEAF]
for level in range(1,21):
    old=chain[-1]; new=(1-coarse)*coarse+coarse*old; chain.append(new)
    if R.grid_kappa(new)==cap: break
bit=chain[-1]
print('coarse',float(coarse),'levels',len(chain)-1,'grid kappa cap',str(cap),float(cap))
# assembly with the given complex saving: bit must stay below (1-beta)*complex
a=min(bit,(1-R.BETA)*complex_saving-Q(1,10**30))
k=min(cap,R.grid_kappa(a))
res=outer.assembly(a,complex_saving,R.bridge_template(),k,eta=R.ETA,beta=R.BETA)
print('complex',float(complex_saving),'kappa',str(k),float(k),'constraints',len(res['strict_constraints']),'min slack>0',min(res['strict_constraints'].values())>0)
try:
    outer.assembly(a,complex_saving,R.bridge_template(),k+Q(1,R.GRID),eta=R.ETA,beta=R.BETA); print('ADJACENT ADMITTED?!')
except AssertionError: print('adjacent grid point rejected')
base=Q(711457853376510,10**18)
print('vs #270 kappa 7.11457853376510e-4: x%.6f (%+.3f%%)'%(float(k/base),100*float(k/base-1)))
