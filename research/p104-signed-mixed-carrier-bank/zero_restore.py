#!/usr/bin/env python3
"""Exact zero-restoration of a signed P104 mixed bank in the relaxed frame model.

No native supplier, recursive invoice or new exponent is claimed.
"""
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("mixed_primary", HERE/"verify.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
E=tuple((a,b) for a,b in combinations(range(8),2) if (a^b).bit_count()==1)
assert len(E)==12
CONFLICT=tuple(sum(1<<j for j,(c,d) in enumerate(E)
                   if a in (c,d) or b in (c,d)) for a,b in E)
F=v.support_family()
assert len(F)==104
ALLOWED=tuple(sum(1<<j for j,(a,b) in enumerate(E)
                  if s>>a&1 and s>>b&1) for s in F)

@lru_cache(maxsize=None)
def matching(mask):
    if not mask: return ()
    bit=mask&-mask; idx=bit.bit_length()-1
    drop=matching(mask^bit)
    take=(E[idx],)+matching(mask&~CONFLICT[idx])
    return take if len(take)>len(drop) else drop

def cost(bank):
    reads=[s.bit_count()-len(matching(bank&allowed))
           for s,allowed in zip(F,ALLOWED)]
    q=bank.bit_count()
    # Build plus/minus; deliver; reverse build to erase both helpers.
    return (832+20*q+sum(k*(k-1) for k in reads),8*q+sum(reads),2*q)

cases=[cost(b) for b in range(4096)]
winners=[b for b,c in enumerate(cases) if c[0]==min(x[0] for x in cases)]
assert winners==[1781,1995,2526,2995,3437,3646]
assert min(x[1] for x in cases)==320
assert all(cases[b]==(1408,320,16) for b in winners)
assert cases[0]==(2224,416,0)
assert cases[4095]==(1432,336,24)

def cleanup(bank,regs,trace):
    cleaned=0
    for j,(a,b) in enumerate(E):
        if not bank>>j&1: continue
        U=(1<<a,1<<b)
        ra,rb=regs[str(a)],regs[str(b)]
        plus,minus=regs[f"{a},{b}+"],regs[f"{a},{b}-"]
        trace.move(ra,U);trace.move(rb,U)
        trace.move(plus,U);trace.move(minus,U)
        trace.accum(plus,rb,-1);trace.accum(plus,ra,-1)
        trace.accum(minus,rb,1);trace.accum(minus,ra,-1)
        assert plus.data==minus.data==(0,)*8
        trace.move(plus,());trace.move(minus,())
        trace.move(ra,ra.home);trace.move(rb,rb.home)
        assert plus.frame==minus.frame==()
        assert ra.data==v.vec(1<<a) and rb.data==v.vec(1<<b)
        cleaned+=1
    return cleaned

bank=winners[0]
edges=[edge for j,edge in enumerate(E) if bank>>j&1]
choices=[matching(bank&allowed) for allowed in ALLOWED]
assert len(edges)==8
t=v.Trace();regs=v.sources(edges,t)
assert (t.rank_cost,t.adds)==(80,32)
for S,M in zip(F,choices):
    signs=[-1 if (S+i).bit_count()%2 else 1 for i in range(8)]
    v.assemble(S,signs,regs,t,M)
assert cleanup(bank,regs,t)==8
assert (t.rank_cost,t.adds)==(1408,320)
assert all(r.frame==() and r.data==(0,)*8 for k,r in regs.items() if "," in k)
assert all(regs[str(i)].data==v.vec(1<<i) and
           regs[str(i)].frame==regs[str(i)].home for i in range(8))

signed_cases=0
for S,M in zip(F,choices):
    members=[i for i in range(8) if S>>i&1]
    for coeffs in product((-1,1),repeat=len(members)):
        signs=[0]*8
        for i,c in zip(members,coeffs): signs[i]=c
        t=v.Trace();regs=v.sources(edges,t)
        v.assemble(S,signs,regs,t,M)
        cleanup(bank,regs,t)
        assert all(r.frame==() and r.data==(0,)*8
                   for k,r in regs.items() if "," in k)
        signed_cases+=1
assert signed_cases==2288
print("PASS_ZERO_RESTORE banks=4096 winner_count=6 frame_rank=1408 adds=320"
      " helpers=16 signed_cases=2288 native=UNPROVEN no_kappa")
