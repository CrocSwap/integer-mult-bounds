#!/usr/bin/env python3
"""Price explicit abstract profiles; no physical/source-body checker is imported.
Chris R / Clear1nsight, substantial OpenAI Codex assistance; Apache-2.0.
The analytic interval extension is written in PROOF.md, not inferred from points.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import resource
import signal
import time

ROOT=Path(__file__).resolve().parent
LIBRARY_SHA256='8f443aa005f5c7c4e2286524e815074787cc109a06cc66e56f362f8cc7854b01'
PAID={1:6611,2:1236,3:1530,4:381,5:120,8:8}
HELPERS={4:84,7:21,8:117,9:954}

def need(ok,message):
    if not ok:raise ValueError(message)
def hist(x):return Counter({int(k):v for k,v in x.items()})
def add(x,y):return x[0]+y[0],x[1]+y[1]
def neg(x):return -x[1],-x[0]
def sub(x,y):return add(x,neg(y))
def scale(x,n):return (x[0]*n,x[1]*n) if n>=0 else (x[1]*n,x[0]*n)
def ceil(x):return -((-x.numerator)//x.denominator)
def pack(x):
    q=10**24;lo=x[0].numerator*q//x[0].denominator;hi=ceil(x[1]*q)
    def show(n):
        s='-' if n<0 else '';n=abs(n);return s+str(n//q)+'.'+str(n%q).zfill(24)
    return dict(lower=str(x[0]),upper=str(x[1]),decimal_lower=show(lo),decimal_upper=show(hi))
def unpack(x):return F(x['lower']),F(x['upper'])
def quota(budget,tariff):
    need(budget[0]>0 and tariff[0]>0,'strict positive budget/tariff required')
    low=ceil(budget[0]/tariff[1])-1;high=ceil(budget[1]/tariff[0])-1
    need(low==high and low>=0,'strict integer quota unresolved')
    return int(low)

def validate_model(m):
    need(hist(m['paid_lower_bound'])==Counter(PAID),'paid lower-bound hypothesis changed')
    need(hist(m['helper_upper_bound'])==Counter(HELPERS),'helper upper-bound hypothesis changed')
    need(hist(m['hypothetical_main_upper_bound'])==Counter({25:240}),'main upper-bound hypothesis changed')
    need(m['all240_main_targets_unearned'] is True,'target credit must remain unearned')
    need(m['physical_derivation_admitted'] is False and m['funded_kappa'] is None,'scope cannot become physical/kappa admission')
    need(m['standalone_tail']==dict(count=8,rank=17,independently_paid=True,extra_productive_credit=0),'standalone independently billed tail hypothesis changed')
    need(m['normalized_pairing']==dict(normalizer=6,paired_H25_terms=8,paired_H17_costs=8,residual_H25_terms=232),'normalized pairing hypothesis changed')
    need(m['domain']==dict(C_lower='33/10000',C_upper_exclusive='1'),'theorem domain changed')
    need(m['points']==[dict(C='33/10000',rho='0'),dict(C='330007/100000000',rho='1/1000000000')],'point contract changed')


def static_tail_structure(p,t):
    direct=Counter(t);direct.subtract(p);direct[17]-=8
    # Algebraic grouping only: eight granted H25 terms paired with eight H17 costs.
    grouped=Counter({25:8,17:-8});grouped.update({25:232,9:954,8:109,7:21})
    grouped.subtract({5:120,4:297,3:1530,2:1236,1:6611})
    clean=lambda c:{r:n for r,n in c.items() if n}
    need(clean(direct)==clean(grouped),'normalized scalar regrouping differs from complete profile')
    need(25>17>6 and all(r>6 for r in (25,9,8,7)) and all(0<r<6 for r in (5,4,3,2,1)),'derivative sign separation failed')
    numerator=256+100*16+4950
    need(100*99//2==4950 and numerator==6806 and numerator>17*256,'exact binomial tail comparison failed')
    return dict(signed_after_tail=clean(direct),normalizer=6,paired_target_rank=25,paired_tail_rank=17,
                binomial_first_three_terms='6806/256 > 17',tail_at_C0_strict_lower=128,
                whole_domain='33/10000 <= C < 1',analytic_extension='PROOF.md: A(t)/6^t strictly increasing for0<t<1')


def run():
    start=time.monotonic();m=json.loads((ROOT/'MODEL.json').read_text());validate_model(m)
    controls=[]
    for name in ('paid_profile','tail_pairing','unearned_credit','standalone_scope'):
        bad=json.loads(json.dumps(m))
        if name=='paid_profile':bad['paid_lower_bound']['1']-=1
        elif name=='tail_pairing':bad['normalized_pairing']['paired_H25_terms']=7
        elif name=='unearned_credit':bad['all240_main_targets_unearned']=False
        else:bad['standalone_tail']['independently_paid']=False
        try:validate_model(bad)
        except ValueError:controls.append(dict(name=name,expected='REJECT_CHANGED_THEOREM_HYPOTHESIS',observed='REJECT_CHANGED_THEOREM_HYPOTHESIS'))
        else:raise ValueError('model mutation survived: '+name)
    p=hist(m['paid_lower_bound']);h=hist(m['helper_upper_bound']);t=h+hist(m['hypothetical_main_upper_bound'])
    structure=static_tail_structure(p,t)
    library=ROOT/'independent_powers.py';need(sha256(library.read_bytes()).hexdigest()==LIBRARY_SHA256,'public independent library bytes changed')
    spec=importlib.util.spec_from_file_location('abstract_profile_independent_powers',library)
    a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    points=[]
    for choice in m['points']:
        C=F(choice['C']);rho=F(choice['rho']);engine=a.Powers(C)
        def f(r):
            x=engine(r);return F(x[0],a.Q),F(x[1],a.Q)
        def moment(profile):
            result=(F(0),F(0))
            for r,n in profile.items():result=add(result,scale(f(r),n))
            return result
        pm=moment(p);tm=moment(t);hm=moment(h);raw=sub(tm,pm);budget=sub(scale(tm,1-rho),pm)
        need(budget[0]>0 and raw[1]<43 and budget[1]<43,'optimistic point bound failed')
        quotas=[]
        for r in (1,4,8,9,25):
            paid_cost=f(r);lost_cost=scale(f(r),1-rho);qp=quota(budget,paid_cost);ql=quota(budget,lost_cost)
            quotas.append(dict(rank=r,additional_paid_tariff=pack(paid_cost),maximum_strict_additional_paid_alone=qp,
                lost_target_tariff=pack(lost_cost),maximum_strict_lost_target_alone=ql,target_inventory_in_conditional_profile=t[r],
                inventory_limited_target_loss_alone=min(ql,t[r]),main_target_credit_unearned=(r==25),quotas_not_additive=True))
        alpha=(pm[0]/tm[1],pm[1]/tm[0])
        points.append(dict(C=str(C),rho=str(rho),all_240H25_unearned=True,paid_moment=pack(pm),conditional_target_moment=pack(tm),
            conditional_raw_decoder_budget=pack(raw),conditional_B_rho=pack(budget),helper_only_moment=pack(hm),
            helper_only_B_rho=pack(sub(scale(hm,1-rho),pm)),conditional_alpha=pack(alpha),conditional_rho_max=pack((1-alpha[1],1-alpha[0])),quotas=quotas,
            mixed_constraint='sum paid_add[r]*r^(1-C)+(1-rho)*sum lost_target[r]*r^(1-C) < conditional_B_rho; each quota alone, never additive',
            remaining_decoder_unknown=True,compiler_admitted=False,physical_target_admitted=False))
    need(F(points[0]['C'])==F(33,10000) and F(points[0]['rho'])==0,'wrong anchor for analytic theorem')
    return dict(status='PASS_EXPLICIT_PROFILE_AND_DECLARED_STANDALONE_TAIL_BOUND',
        fixed_paid=dict(p),retained_helpers=dict(h),unearned_main={25:240},conditional_targets=dict(t),points=points,
        static_tail_structure=structure,negative_controls=controls,
        at_C0_raw_upper_less_than=43,at_C0_tail_strict_lower=128,at_C0_after_tail_strict_upper=-85,
        additional_eight_H1_budget_shift='-8 exactly at both points; all larger paid profiles only worsen this upper bound',
        funded_kappa=None,all240_targets_unearned=True,physical_derivation_admitted=False,
        scope='Explicit mathematical profile upper/lower hypotheses and independently paid8H17 grammar only; no universal decoder/circuit barrier or free-fusion obstruction.',
        environment=dict(elapsed_seconds=time.monotonic()-start,maximum_resident_set_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024));signal.alarm(30)
    try:result=run()
    except Exception as exc:
        with args.receipt.open('x') as out:json.dump(dict(status='FAIL',exception=type(exc).__name__,message=str(exc)),out,indent=2);out.write('\n')
        raise
    with args.receipt.open('x') as out:json.dump(result,out,indent=2);out.write('\n')
    print(json.dumps(result,sort_keys=True))
