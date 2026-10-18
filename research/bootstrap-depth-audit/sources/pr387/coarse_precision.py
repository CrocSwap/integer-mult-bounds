"""Retain 24 certified decimal places in the unchanged paid PR384 moment.
Both independently written rational engines and the original positive fallback
are retained. Decimal arithmetic proposes endpoints; it never admits them.
"""
from pathlib import Path
from fractions import Fraction as Q
import importlib.util
ROOT=Path(__file__).resolve().parent

def module(name):
    spec=importlib.util.spec_from_file_location('precision_'+name,ROOT/'source384/code/engines'/(name+'.py'))
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj

def certify(profile,m,stock,original_coarse):
    M=module('moment');B=module('base_two_moment');H={int(k):v for k,v in profile.items()}
    assert (m,stock)==(73,14727)
    assert m*stock-sum(r*n for r,n in H.items())==2496
    root=M.certify(H,m,stock,True);lo=Q(root['lower']);hi=Q(root['upper']);step=Q(1,10**24)
    assert hi-lo==step and original_coarse<lo<hi<original_coarse+Q(1,10**18)
    low_interval=M.moment(H,m,stock,lo,True);high_interval=M.moment(H,m,stock,hi,True)
    assert low_interval[1]<1<high_interval[0]
    fallback=32*m*m*sum(H.values());density=Q(1,10**16)
    _,up=B.moment(m,stock,list(H.items()),lo);_,bad=B.moment(m,stock,[(1,fallback)],lo)
    lower,_=B.moment(m,stock,list(H.items()),hi);bad_lower,_=B.moment(m,stock,[(1,fallback)],hi)
    assert up+density*bad<1<lower+density*bad_lower
    return dict(status='PASS_TWO_EXACT_MOMENT_ENGINES',coarse_lower=str(lo),coarse_upper=str(hi),original_coarse=str(original_coarse),coarse_gain=str(lo-original_coarse),grid=str(step),density=str(density),fallback_rank_one_calls=fallback,profile_unchanged=True,first_engine_lower_residual_upper=str(low_interval[1]-1),first_engine_upper_residual_lower=str(high_interval[0]-1),second_engine_lower_residual_upper=str(up+density*bad-1),second_engine_upper_residual_lower=str(lower+density*bad_lower-1),next_coarse_grid_rejected=True)
