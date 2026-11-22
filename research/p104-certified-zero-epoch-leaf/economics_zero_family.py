#!/usr/bin/env python3
"""Directed arithmetic for the no-paid-taint zero-tuple family.

Bounds use the pinned #8041 integer-root interval reader. We generously retain
all original target mass and grant deletion of every selected tensor block;
even the unsplit raw moment still fails at kappa=0.00389046.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent/'pinned'))
from price_audit import BIT_TARGET,BIT_PAID,moment,UNIT,K
T=Counter(BIT_TARGET);P=Counter(BIT_PAID);S=Counter({1:8136,2:5616,4:72})
assert sum(S.values())==13824 and sum(k*v for k,v in S.items())==19656
power=268;t=1-K
Tlo,Thi=moment(T,t);Plo,Phi=moment(P,t);Slo,Shi=moment(S,t)
assert 14*Shi<Tlo
assert 14**power>10**300
raw_deficit=Plo**power-Thi**power-Shi**power
assert raw_deficit>0
assert 10_000*raw_deficit>Thi**power
print(json.dumps({'kappa':str(K),'power':power,
 'family_raw_paid_rank_hist':dict(S),
 'family_tuple_count':'13824**268',
 'exact_family_moment':'(8136 + 5616*2**(1-k) + 72*4**(1-k))**268',
 'family_moment_over_unpruned_target_moment':'< 10**-300',
 'raw_paid_less_family_minus_unpruned_target_over_target':'> 1/10000',
 'scope':'generously keep all target moments, discard all identified paid tuple moments, omit all split penalties; directed integer-root enclosures'},indent=2))
print('PASS_ZERO_FAMILY_STILL_INSUFFICIENT_AT_TRIAL')
