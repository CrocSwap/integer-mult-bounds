#!/usr/bin/env python3
"""One fixed conditional scalar screen; no compiler/emitter/native run.
Uses the retained outer ledger formulas only; applicability remains conditional.
"""
from check_merge import Q,HERE,F,need,moment,interval,sub,scale,logint,alt,power
from hashlib import sha256
import json,runpy

GRID=10**50
def down(x):return Q((x*GRID).__floor__(),GRID)
def up(x):return Q((x*GRID).__ceil__(),GRID)
def expone(x):
    if x>0:
        a,b=expone(-x);return down(1/b),up(1/a)
    x=-x;n=0
    while x>=Q(1,50):x/=2;n+=1
    a,b=down(alt(x,17)),up(alt(x,18))
    for _ in range(n):a,b=down(a*a),up(b*b)
    return a,b
def rp(r,t):
    a,b=sorted(t*x for x in logint(r))
    return expone(a)[0],expone(b)[1]
def mom(h,t):
    return tuple(sum((n*rp(r,t)[i] for r,n in h.items()),Q(0)) for i in (0,1))
def divide(a,b):return a[0]/b[1],a[1]/b[0]
def main():
    A=json.loads((F/'4610-round6-ARITHMETIC.json').read_text())
    T={int(k):n for k,n in A['targets'].items()};P={int(k):n for k,n in A['paid'].items()}
    P[1]-=36;P[2]+=18
    k=Q('.0030220');tested=k+Q(1,10**11);gap=(tested-k)/7
    need(k>Q('.0030217758') and tested<Q('.0034'),'comparison and inherited BIT domain')
    target,paid=moment(T,tested),moment(P,tested)
    def logmoment(h,C):
        return tuple(sum((n*power(r,C)[i]*logint(r)[i] for r,n in h.items()),Q(0)) for i in (0,1))
    # f'(C)=-sum_T r^(1-C)logr+sum_P r^(1-C)logr.
    # Separate monotonicity bounds this derivative over the complete [0,tested].
    derivative_upper=logmoment(P,Q(0))[1]-logmoment(T,tested)[0]
    need(derivative_upper<0,'strict monotonicity on the whole pre-test interval')
    alpha=divide(paid,target)
    cut=rp(20,Q(1,5));gamma=divide(mom(P,1-tested+Q(1,5)),(cut[0]*target[0],cut[1]*target[1]))
    delta=divide((Q(sum(T.values())*21),)*2,(rp(20,tested)[0]*target[0],rp(20,tested)[1]*target[1]))
    alpha_gap=Q(1,10**11);theta=Q(63,64)
    need(alpha[1]<1-alpha_gap and gamma[1]<Q(97,100) and delta[1]<Q(97,100),'strict contraction and both charged tails')
    normalized=1/(1+1024*alpha_gap)+Q(4,2**32)
    eta=scale(rp(145,-1024*tested),1-tested)
    capacity={'normalized_paid_below_one':normalized<1,'split_and_round':20**64<21**63,
      'paid_tail_block':Q(97,100)**128<Q(1,16),'completion_tail_block':Q(97,100)**128<Q(1,16),
      'shifted_exits':2*20**(1024*64)<=145**(1024*63),'eta_above_theta_power':eta[0]>theta**1000,
      'initial_range':rp(145,1024*tested)[1]<2**1000}
    # Source gap unchanged: verify its frozen integer sufficient height directly.
    step=gap.denominator;j=A['compiler']['integer_test_exponent'];height=A['compiler']['H']
    capacity.update({'same_gap':gap==Q(A['compiler']['gap']),
      'height_encoding':height==step*j and height>8*1024,
      'uniform_integer_wins':(step*j+1)**1000<2**j,
      'predecessor_integer_fails':(step*(j-1)+1)**1000>=2**(j-1)})
    need(all(capacity.values()),'finite sufficient scalar capacity')
    params={'kappa':k,'tested_saving':tested,'complex_uniform_saving':k+6*gap,
      'b':k+5*gap,'a':k+4*gap,'q':k+3*gap,'bit_saving':Q('.0034'),
      'epsilon':1-gap,'beta':1-3*gap,'r0':gap/10,'stop':gap,'layout':gap,'d':gap}
    ledger=runpy.run_path(str(F/'4610-outer-endpoint.py'))['ledger']
    outer=ledger(params)
    outer['functional_checks']['actual_new_BIT_stock_sublinear']=params['beta']*(1-Q('.004'))
    need(len(outer['strict_checks'])==54 and len(outer['functional_checks'])==4,'literal source inventory')
    need(all(v>0 for g in ('strict_checks','functional_checks') for v in outer[g].values()),'all outer arithmetic positive')
    controls={}
    for name,patch in [('old_BIT',{'bit_saving':Q('.0027')}),('closed_uniform',{'complex_uniform_saving':params['b']}),
                       ('closed_epsilon',{'epsilon':Q(1)}),('unfunded_endpoint',{'kappa':tested})]:
        bad=ledger(dict(params,**patch));failed=[n for n,v in bad['strict_checks'].items() if v<=0]
        need(failed,'reject unsupported '+name);controls[name]=failed
    result={'status':'PASS_CONDITIONAL_ONE_FUSION_FIXED_COMPILER_PARAMETER_SCREEN',
      'physical_witness_supplied':False,'compiler_executed':False,'kappa':str(k),'tested':str(tested),'gap':str(gap),
      'margin':interval(sub(target,paid)),'reserve_margin_M_minus_T_1e11':interval(sub(scale(target,1-alpha_gap),paid)),
      'derivative_domain':['0',str(tested)],'uniform_derivative_upper':interval((derivative_upper,derivative_upper))['upper'],
      'positive_entire_pretest_interval':True,
      'alpha':interval(alpha),'gamma':interval(gamma),'delta':interval(delta),'eta':interval(eta),
      'normalized_paid_upper':str(normalized),'capacity':capacity,'finite_height':height,
      'outer':outer,'controls':controls,
      'conditions':['actual all-port all-input forward/raw-dual native fusion with unchanged targets',
        'unchanged native scalar/routing/denominator/precision/template closure bounds or separately rebilled replacements',
        'unchanged whole-job completed-child and spectator contracts',
        'admitted uniform complex supplier at stated saving; inherited ordinary BIT/stock interface',
        'same nine outer cost formulas and semantic C1=1 premises'],
      'source_sha256':{p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(F.iterdir()) if p.is_file()}}
    print(json.dumps(result,indent=2,sort_keys=True,default=str))
if __name__=='__main__':main()
