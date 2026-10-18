#!/usr/bin/env python3
"""Exact signed P104 rank-two framed mixers, all values zero-restored.

A complete finite F2-frame construction, NOT a native/hosted P104 supplier.
"""
from functools import lru_cache
from itertools import combinations,product
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('mix_v',HERE/'verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
E=tuple((a,b) for a,b in combinations(range(8),2) if (a^b).bit_count()==1)
F=v.support_family()
assert len(E)==12 and len(F)==104
CONFLICT=[sum(1<<j for j,(c,d) in enumerate(E) if a in (c,d) or b in (c,d)) for a,b in E]
ALLOWED=[sum(1<<j for j,(a,b) in enumerate(E) if (s>>a&1) and (s>>b&1)) for s in F]
@lru_cache(None)
def matching(mask):
    if not mask:return ()
    bit=mask&-mask;j=bit.bit_length()-1
    no=matching(mask^bit)
    yes=(E[j],)+matching(mask&~CONFLICT[j])
    return yes if len(yes)>len(no) else no

def invoice(bank):
    rank=832+16*bank.bit_count();adds=8*bank.bit_count()
    for S,A in zip(F,ALLOWED):
        n=S.bit_count();p=len(matching(bank&A))
        adds+=n-p;rank+=n*(n-1)-2*p*(n-p)
    return rank,adds,2*bank.bit_count()
prices=[invoice(bank) for bank in range(4096)]
winners=[i for i,x in enumerate(prices) if x[0]==min(vv[0] for vv in prices)]
assert winners==[1781,1995,2526,2995,3437,3646]
assert all(prices[i]==(1520,320,16) for i in winners)
assert prices[0]==(2224,416,0) and prices[4095]==(1552,336,24)

def sources(bank,t):
    regs={str(i):v.Register(v.vec(1<<i),(1<<i,),str(i)) for i in range(8)}
    for j,(a,b) in enumerate(E):
        if not (bank>>j)&1:continue
        U=(1<<a,1<<b);ra,rb=regs[str(a)],regs[str(b)]
        t.move(ra,U);t.move(rb,U)
        plus=v.Register((0,)*8,(),f'{a},{b}+')
        minus=v.Register((0,)*8,(),f'{a},{b}-')
        t.move(plus,U);t.move(minus,U)
        t.accum(plus,ra);t.accum(plus,rb)
        t.accum(minus,ra);t.accum(minus,rb,-1)
        t.move(ra,ra.home);t.move(rb,rb.home)
        plus.home=U;minus.home=U
        regs[plus.label]=plus;regs[minus.label]=minus
    return regs

def target(S,coeff,regs,t,pairs):
    h=v.hyperplane(S)
    selected=set(i for a,b in pairs for i in (a,b))
    ingredients=[(str(i),coeff[i]) for i in range(8) if S>>i&1 and i not in selected]
    ingredients +=[(f'{a},{b}'+('+' if coeff[a]==coeff[b] else '-'),coeff[a]) for a,b in pairs]
    y=v.Register((0,)*8,(),f'target_{S}')
    frame=[]
    for name,sgn in ingredients:
        reg=regs[name]
        assert v.included(reg.home,h)
        for basis in reg.home:
            assert not v.contains(tuple(frame),basis)
            frame.append(basis)
        t.move(y,frame);t.move(reg,frame)
        t.accum(y,reg,sgn)
        t.move(reg,reg.home)
    t.move(y,h)
    assert y.data==tuple(coeff[i] if S>>i&1 else 0 for i in range(8))
    assert v.rank(y.frame)==8

def clean(bank,regs,t):
    for j,(a,b) in enumerate(E):
        if not (bank>>j)&1:continue
        ra,rb=regs[str(a)],regs[str(b)]
        plus,minus=regs[f'{a},{b}+'],regs[f'{a},{b}-']
        U=(1<<a,1<<b)
        assert plus.frame==minus.frame==U
        t.move(ra,U);t.move(rb,U)
        t.accum(plus,rb,-1);t.accum(plus,ra,-1)
        t.accum(minus,rb,1);t.accum(minus,ra,-1)
        assert plus.data==minus.data==(0,)*8
        t.move(plus,());t.move(minus,())
        t.move(ra,ra.home);t.move(rb,rb.home)
    assert all(r.data==(0,)*8 and r.frame==() for k,r in regs.items() if ',' in k)
    assert all(regs[str(i)].frame==regs[str(i)].home and regs[str(i)].data==v.vec(1<<i) for i in range(8))

bank=winners[0]
selected=[matching(bank&A) for A in ALLOWED]
t=v.Trace();regs=sources(bank,t)
assert (t.rank_cost,t.adds)==(64,32)
for S,M in zip(F,selected):
    signs=[1 if (S+i).bit_count()%2 else -1 for i in range(8)]
    target(S,signs,regs,t,M)
clean(bank,regs,t)
assert (t.rank_cost,t.adds)==(1520,320),(t.rank_cost,t.adds)

signed=0
for S,M in zip(F,selected):
    members=[i for i in range(8) if S>>i&1]
    for x in product((-1,1),repeat=len(members)):
        coeff=[0]*8
        for i,c in zip(members,x):coeff[i]=c
        t=v.Trace();regs=sources(bank,t)
        target(S,coeff,regs,t,M)
        clean(bank,regs,t)
        signed+=1
assert signed==2288
print('PASS_RANK2_MIXERS banks=4096 winner_count=6 frame_rank=1520 adds=320 helpers=16 signed=2288 zero_restored=YES native=UNPROVEN')
