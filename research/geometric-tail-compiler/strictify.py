"""Exact adaptive completion/compiler parameters. Apache-2.0.
Dugongue with OpenAI Codex assistance; formulas from zxv's higher-moment
strictification and logarithmic majorant, retained by Cao Yifan et al.
"""
from fractions import Fraction as Q

def need(ok, why):
    if not ok: raise ValueError(why)

def completed_upper(v, reserve, gamma, delta):
    need(all(isinstance(x,Q) for x in (reserve,gamma,delta)), 'Exact rational envelopes required')
    need(isinstance(v,int) and v>=0, 'Nonnegative integer tensor power')
    need(0<reserve<1 and 0<gamma<1 and 0<delta<1, 'Strict rational contraction envelopes')
    return 1/(1+v*reserve)+2*gamma**v+2*delta**v

def tensor_power(reserve, gamma, delta):
    def wins(v): return completed_upper(v,reserve,gamma,delta)<1
    lo,hi=0,1
    while not wins(hi):lo,hi=hi,2*hi
    while hi-lo>1:
        mid=(lo+hi)//2
        if wins(mid):hi=mid
        else:lo=mid
    need(wins(hi) and not wins(hi-1), 'Least power for this sufficient bound')
    return hi

def logarithm_power(theta, eta_lower, initial_upper):
    need(all(isinstance(x,Q) for x in (theta,eta_lower,initial_upper)), 'Exact rational majorant inputs required')
    need(0<theta<1 and eta_lower>0 and initial_upper>0, 'Positive majorant inputs')
    def wins(p):return theta**p<eta_lower and 2**p>initial_upper
    lo,hi=0,1
    while not wins(hi):lo,hi=hi,2*hi
    while hi-lo>1:
        mid=(lo+hi)//2
        if wins(mid):hi=mid
        else:lo=mid
    need(wins(hi) and (hi==1 or not wins(hi-1)), 'Least admissible positive logarithm power')
    return hi

def finite_threshold(gap, power):
    need(isinstance(gap,Q), 'Exact rational gap required')
    need(gap>0 and isinstance(power,int) and power>=1, 'Positive compiler gap and integer power')
    step=(gap.denominator+gap.numerator-1)//gap.numerator
    need(Q(1,step)<=gap, 'Conservative integer gap grid')
    def wins(j):return (step*j+1)**power<2**j
    lo,hi=0,1
    while not wins(hi):lo,hi=hi,2*hi
    while hi-lo>1:
        mid=(hi+lo)//2
        if wins(mid):hi=mid
        else:lo=mid
    need(wins(hi) and (hi==1 or not wins(hi-1)), 'Checked finite integer threshold')
    return {'step':step,'j':hi,'H':step*hi}
