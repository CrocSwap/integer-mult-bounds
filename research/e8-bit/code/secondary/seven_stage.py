"""SECONDARY, conditional: kappa under PR #363's seven-stage complex value, and the bit word priced in the bridged
layouts B_K (K = 2: the five-stage layout of this package, reproduced; K = 3: seven stages, needs a seven-stage bit
construction that does not exist yet).  b3 = 932783231884153/10^18 is PR #363's certified complex coarse saving
(DaysSky, e8-seven-stage at 9df55da; verify it with that package's verify.sh).  bridged.py is vendored unchanged
from PR #363 (code/complex/code/bridged.py).
usage: seven_stage.py KAPPA.json (this package's step-8 receipt)"""
import sys, os, json, importlib.util
from fractions import Fraction as Q
from collections import Counter
HERE=os.path.dirname(os.path.abspath(__file__)); P=os.path.join(HERE,'..','pricing')
def load(n):
    s=importlib.util.spec_from_file_location(n,os.path.join(P,n+'.py')); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
moment=load('moment'); other=load('base_two_moment'); outer=load('outer')
sys.path.insert(0,HERE); import bridged
k=json.load(open(sys.argv[1])); h,v,m5=k['h'],120,k['m']; R=k['W']-4*v
H5=Counter({int(a):c for a,c in k['normalized_histogram'].items()})
idle5=bridged.check(2,h)['blocks_per_role_pair']; assert sorted(idle5)==sorted([2*h+2,2*h-2,h-1,4])
for r in idle5: H5[r]-=2*v
local=Counter()
for r,c in H5.items():
    if c: assert c%5==0; local[r]=c//5
grid=Q(1,10**18)
def coarse(H,m,W):
    root=moment.certify(dict(H),m,W,True); c=Q(int(Q(root['lower'])*10**18),10**18)
    assert moment.moment(H,m,W,c,True)[1]<1<moment.moment(H,m,W,c+grid,True)[0]
    fb=32*m*m*sum(H.values()); _,up=other.moment(m,W,list(H.items()),c); _,bad=other.moment(m,W,[(1,fb)],c)
    lo,_=other.moment(m,W,list(H.items()),c+grid); badlo,_=other.moment(m,W,[(1,fb)],c+grid)
    assert up+Q(1,10**16)*bad<1<lo+Q(1,10**16)*badlo
    return c
def kappa(c,b):
    eta=Q(1,10**12); beta=Q(1,10**9); cap=(1-beta)*b
    sv=min(c,Q(((cap-grid)*10**18).__floor__(),10**18)); binding='bit' if sv==c else 'complex'
    chain=[Q(384599,10**10)]
    for _ in range(3): a=(1-sv)*sv+sv*chain[-1]; assert chain[-1]<a<sv<1-a; chain.append(a)
    bit=chain[-1]; bridge=dict(semantic=dict(C0=dict(base=2,exponent=210000),strict_literal_gap=1),rows=dict(degree_gap=Q(10**6)-Q(51*20161,25)))
    q=bit*(1-2*eta); mn=(1-eta)*q/(1+q); t=mn*10**18; kk=Q((t.numerator-1)//t.denominator,10**18)
    asm=outer.assembly(bit,b,bridge,kk,eta=eta,beta=beta); assert len(asm['strict_constraints'])==47
    try: outer.assembly(bit,b,bridge,kk+grid,eta=eta,beta=beta); raise SystemExit('adjacent admitted')
    except AssertionError: pass
    return kk,binding
b2=Q(876248285600677,10**18); b3=Q(932783231884153,10**18)
res={}
for K in (2,3):
    m=(2*K+1)*h; lay=bridged.check(K,h,split=(m-1)//2 if K>2 else None)
    H=Counter({r:(2*K+1)*c for r,c in local.items()})
    for r in lay['blocks_per_role_pair']: H[r]+=2*v
    W=2*K*v+R; assert m*W-sum(r*c for r,c in H.items())==2*K*v-(2*K+1)*72 and 2*max(H)<m
    c=coarse(H,m,W); res[K]=c
    print('bit word in B_%d (%d stages, m %d, W %d, idle %s): bit coarse c = %s = %.12e'%(K,2*K+1,m,W,lay['blocks_per_role_pair'],c,float(c)))
assert res[2]==Q(k['bit_coarse']), 'B_2 must reproduce the five-stage bit coarse saving'
for name,c,b in [('five-stage bit + #352 five-stage complex (PRIMARY)',res[2],b2),('five-stage bit + #363 seven-stage complex',res[2],b3),
                 ('seven-stage bit (no construction yet) + #363 seven-stage complex',res[3],b3)]:
    kk,bd=kappa(c,b); print('kappa [%s]: %s = %.12e (%s-bound)'%(name,kk,float(kk),bd))
