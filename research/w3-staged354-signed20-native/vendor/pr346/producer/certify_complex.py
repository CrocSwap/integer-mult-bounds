"""Certify a five-stage complex saving b (10^-18 grid, WITH the 10^-16 bad-class fallback) with PR315's two rational
moment engines (moment.py certify/moment and base_two_moment.py), as PR315's math_check.complex_supplier does."""
import json, gzip, sys, importlib.util
from fractions import Fraction as Q
sys.path.insert(0,'/home/claude/work')
from cprice import five
PK='/home/claude/pr315/research/five-stage-p10-banks/'
def load(name):
    s=importlib.util.spec_from_file_location(name,PK+name+'.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
cost=load('moment'); other=load('base_two_moment')
for path in sys.argv[1:]:
    c=json.load(gzip.open(path,'rt') if path.endswith('.gz') else open(path))
    m,W,H=five(c['blocks'],c['v'],c['h'],c['R']); CH={int(r):n for r,n in H.items()}
    grid=Q(1,10**18)
    root=cost.certify(dict(CH),m,W,True); b=Q(int(Q(root['lower'])*10**18),10**18)
    cm=cost.moment(dict(CH),m,W,b,True); nextcm=cost.moment(dict(CH),m,W,b+grid,True); assert cm[1]<1<nextcm[0]
    fallback=32*m*m*sum(CH.values())
    _,upper=other.moment(m,W,list(CH.items()),b); _,bad=other.moment(m,W,[(1,fallback)],b)
    lower,_=other.moment(m,W,list(CH.items()),b+grid); badlower,_=other.moment(m,W,[(1,fallback)],b+grid)
    assert upper+Q(1,10**16)*bad<1<lower+Q(1,10**16)*badlower
    root0=cost.certify(dict(CH),m,W,False); b0=Q(int(Q(root0['lower'])*10**18),10**18)
    cm0=cost.moment(dict(CH),m,W,b0,False); nx0=cost.moment(dict(CH),m,W,b0+grid,False); assert cm0[1]<1<nx0[0]
    print(path.split('/')[-1],'m',m,'W',W,'R',c['R'],'calls',sum(CH.values()),'mass',sum(k*n for k,n in CH.items()),'maxchild',max(CH))
    print('   b (with fallback, both engines) = %s = %.15e ; without fallback %s'%(b,float(b),b0))
