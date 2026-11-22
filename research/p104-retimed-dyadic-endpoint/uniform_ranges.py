#!/usr/bin/env python3
"""Exact parameter checks for the dfd stage-store/retimed uniform ranges."""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(Path(sys.argv[1]).resolve()))
sys.path.insert(1,str(ROOT))
from upstream import install
install()
from installations import BINARY_C
from raw_binary_stage import binary_word
from unpowered_price import certify, intervals
from strict_moment import UNIT

w=binary_word()
targets,paid=Counter(w.targets),Counter(w.paid)
old=Q(4484997569314581,2**60)
newmargin,new=certify(BINARY_C,(targets,paid))
oldmargin,prior=certify(old,(targets,paid))
t=1-BINARY_C
assert 0<BINARY_C<Q(1,250) and t>Q(996,1000)
assert newmargin>0 and oldmargin>0
assert set(new)==set(prior) and len(new)==24
assert sum(targets.values())==18906<2**16
assert sum(paid.values())==104904<2**19
assert max(targets)==127 and min(paid)==1 and max(paid)==56
assert all(4*k>=5*r and q>0 for (r,k),q in new.items())
assert min(new.values())/sum(targets.values())>Q(1,2**64)
assert all(sum(q for (r,k),q in new.items() if r==rr)==1 for rr in paid)
targets_mass={k:n*intervals(k,t)[0] for k,n in targets.items()}
paid_mass={r:n*intervals(r,t)[1] for r,n in paid.items()}
T,P=sum(targets_mass.values()),sum(paid_mass.values())
assert all(sum(paid_mass[r]*q for (r,z),q in new.items() if z==k)
           == Q(targets_mass[k]*P,T) for k in targets)
assert Q(P,T)>Q(99,100) and Q(P,UNIT)>10
assert 6**77 > 2**20*5**77
assert 2**21 < (1024*134*32768)**77
# For H>=1024, N>=2: t>1/2 and L>=4 give t*L^t>1;
# 2N < N^6. Therefore ceil integral births <2 N^6 per tick.
assert Q(1,2)**2*32768 > 1 and 2*2 < 2**6
# <=2N^6 births/tick, <N^77 lifetime, <2^67 fields/context.
# Therefore 2^68 N^83 < N^92 whenever 68<9H.
assert 68 < 9*1024
assert 8*(20+91)==888 < 2**10
assert 2*8*256*80*22*3 < 2**25
assert 67*2**16 < 2**23
result={'binary_trial':str(BINARY_C),'raw_target_count':sum(targets.values()),
        'raw_paid_count':sum(paid.values()),'target_max':max(targets),
        'paid_min':min(paid),'paid_max':max(paid),'cells':len(new),
        'support_same_as_dfd_trial':True,'row_sums_and_capacity_equalities':True,
        'minimum_share_per_target':str(min(new.values())/sum(targets.values())),
        'max_reduced_cell_bits':max(max(q.numerator.bit_length(),q.denominator.bit_length()) for q in new.values()),
        'raw_mass_ratio_lower':str(Q(P,T)), 'two_scale_positive_counts':[105216,564144,54],
        'lifetime_ratio_guard':'(6/5)^77 > 2^20',
        'cohort_guard':'2^68 N^83 < N^92 for H>=1024',
        'stage_head_allowance':888,
        'scope':'exact parameter and source checks; dfd source-to-role interpretation is written'}
Path(sys.argv[2]).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('PASS_461_UNIFORM_SOURCE_RANGES_AND_COUPLING_CAPACITIES')
