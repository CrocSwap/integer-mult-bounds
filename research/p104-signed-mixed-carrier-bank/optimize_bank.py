#!/usr/bin/env python3
"""Exact exhaustive 12-edge-bank cost audit in the relaxed P104 model."""
from itertools import combinations
import importlib.util
from pathlib import Path
p=Path(__file__).resolve().parent/'verify.py'
s=importlib.util.spec_from_file_location('p104_mixed_verify',p)
mod=importlib.util.module_from_spec(s)
s.loader.exec_module(mod)
support_family=mod.support_family
E=tuple((i,j) for i,j in combinations(range(8),2) if (i^j).bit_count()==1)
assert len(E)==12
conflict=[sum(1<<k for k,(a,b) in enumerate(E) if i in (a,b) or j in (a,b)) for i,j in E]
match=[0]*4096
for bank in range(1,4096):
    bit=bank&-bank; j=bit.bit_length()-1
    match[bank]=max(match[bank^bit],1+match[bank&~conflict[j]])
F=support_family()
assert len(F)==104
allowed=[sum(1<<j for j,(a,b) in enumerate(E) if s>>a&1 and s>>b&1) for s in F]
costs=[]
for bank in range(4096):
    counts=[s.bit_count()-match[bank&available] for s,available in zip(F,allowed)]
    costs.append((832+10*bank.bit_count()+sum(k*(k-1) for k in counts),
                 4*bank.bit_count()+sum(counts)))
best=min(x[0] for x in costs)
winners=[i for i,x in enumerate(costs) if x[0]==best]
assert best==1312 and winners==[4095]
assert min(x[1] for x in costs)==288
assert costs[0]==(2224,416) and costs[4095]==(1312,288)
print('PASS_BANK_4096 rank=1312 adds=288 winner=4095 no_kappa')
