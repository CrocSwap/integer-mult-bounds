#!/usr/bin/env python3
"""Exact item-size, 66-root, stop and control guards for the e264 overlay."""
from pathlib import Path
from fractions import Fraction as Q
from unittest.mock import patch
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(Path(sys.argv[1]).resolve()))
sys.path.insert(1,str(ROOT))
from upstream import install
install()
from installations import BINARY_C,GAUSSIAN_C,Profile
from activation import resource_receipt
from outer_budget import margins
from independent_binary_price import rank_price
import transport

p=Profile(tuple(2*10**12*16**j for j in range(7)),36000,
          Q(39,10000),Q('.003890115286594461'),10**21)
D=p.positive_stop_denominator
rec=resource_receipt(p)
H=max(p.rank_logs)
sizes={'max_rank_log_bits':H.bit_length(),
       'max_binary_cut_log_bits':max(rec['binary_cuts']).bit_length(),
       'public_exponent_bits':rec['public_exponent_A'].bit_length(),
       'max_binary_width_log_bits':(92*H).bit_length(),
       'positive_carrier_bits':(1<<p.complex_log).bit_length(),
       'stop_denominator_bits':D.bit_length(),
       'binary_trial_denominator_bits':BINARY_C.denominator.bit_length()}
assert sizes=={'max_rank_log_bits':65,'max_binary_cut_log_bits':65,
               'public_exponent_bits':65,'max_binary_width_log_bits':72,
               'positive_carrier_bits':36001,'stop_denominator_bits':70,
               'binary_trial_denominator_bits':67}
assert max(sizes.values()) < 2**38
assert (D.bit_length()-1,D.bit_count())==(69,29)
assert (17*D)**16 < 2**1182
assert 872*(4*p.complex_log+1) < (1<<p.complex_log)
assert 2*409-49*1024 < -4 # exponent 409-49H/2 < -2 at H>=1024

positive=GAUSSIAN_C-Q(39,256*p.complex_log)
strict,functional,paid=margins(p.kappa,Q(1,D),p.ordinary,positive)
assert len(strict)==54 and len(functional)==4 and min(*strict,*functional,paid)>0
assert all((x*D**2).denominator==1 for x in (*strict,*functional))
assert (paid*D**2).denominator == 3
assert all((x*3*D**2).denominator==1 for x in (*strict,*functional,paid))
gate_bits=max(abs((x*3*D**2).numerator).bit_length() for x in (*strict,*functional,paid))
assert gate_bits<=186

t=1-BINARY_C
assert t.denominator==2**66
measure=transport.Measure(t,1,640)
original=transport.isqrt
counts=[]
for rank in (2,3,15,127):
    count=[0]
    def counted(value):
        count[0]+=1
        return original(value)
    with patch.object(transport,'isqrt',side_effect=counted):
        lo,hi=measure.inverse_power(rank)
    assert count[0]==132 # two isqrt calls at each of 66 root levels
    lower,upper=rank_price(rank,t)
    assert Q(lo,measure.grid)<=1/lower and Q(hi,measure.grid)>=1/upper
    counts.append({'rank':rank,'isqrt_calls':count[0], 'intervals_overlap':True})
result={'sizes_in_bits':sizes,'source_item_allowance_bits':2**38,
        'stage_count':len(p.rank_logs),'positive_count':1,
        'stop_10_21_squares_upper':69,'stop_10_21_selected_products_upper':29,
        'stop_absorption_ceiling_bits':((17*D)**16-1).bit_length(),
        'positive_cap':str(positive),'signed_common_scale':'3*D^2',
        'scaled_signed_max_bits':gate_bits,'measure_controls':counts,
        'generic_66_root_error_log_upper':'409-(49/2)*H',
        'scope':'fixed-item and arithmetic guards; all-size control accounting remains a written proof'}
Path(sys.argv[2]).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print('PASS_461_FIXED_ITEM_STOP_AND_66_ROOT_CONTROLS',flush=True)
