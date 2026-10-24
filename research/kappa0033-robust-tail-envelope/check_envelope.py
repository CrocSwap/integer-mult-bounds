#!/usr/bin/env python3
"""Exact finite certificates supporting the written integer-profile envelope.
No pricing, fractional powers, physical data or imported research engine.
Chris R / Clear1nsight, with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from fractions import Fraction as F
import json
from math import comb
from pathlib import Path
import resource
import signal

ROOT=Path(__file__).resolve().parent
P0={1:6611,2:1236,3:1530,4:381,5:120,8:8}
T0={4:84,7:21,8:117,9:954,25:240}

def need(ok,message):
    if not ok:raise ValueError(message)
def hist(value):return {int(k):n for k,n in value.items()}
def load(name):return json.loads((ROOT/name).read_bytes())

def validate_model(m):
    need(m['C']=='330007/100000000' and m['rho']=='1/1000000000','fixed exponent/reserve changed')
    need((m['cutoff'],m['floor'],m['offset'],m['product_power'])==(8,9,'1/5',1024),'fixed tail tuple changed')
    need(hist(m['P0'])==P0 and hist(m['T0'])==T0,'fixed baseline profiles changed')
    need(m['R0_upper_strict']==43 and m['R0_upper_is_explicit_conditional_premise'] is True,'conditional R0 premise changed')
    need(m['one_strict_mixed_budget_required'] is True,'separate quotas cannot replace the one mixed budget')
    need(not m['new_targets_allowed'] and not m['paid_deletions_allowed'] and not m['signed_netting_allowed'],'honest gross-ledger restrictions changed')
    need(m['all240H25_hypothetical'] is True,'hypothetical targets promoted to admission')
    need(not m['rank_bound_is_ambient_certificate'],'rank estimate is not an ambient certificate')
    need(not m['actual_future_ledger_checked'] and not m['physical_data_included'] and not m['compiler_admitted'] and m['funded_kappa'] is None,'scope overclaim')

def validate_ledger(A,L,new_targets=None,paid_deletions=None):
    """Syntax/domain check only: it does not evaluate or accept the mixed budget."""
    need(not new_targets and not paid_deletions,'no new targets or paid deletions')
    for label,data in [('A',A),('L',L)]:
        need(type(data) is dict,'finite histogram object required')
        for key,count in data.items():
            need(type(key) is str and key.isascii() and key.isdecimal() and str(int(key))==key and int(key)>0,'canonical positive integer rank required')
            need(type(count) is int and count>=0,'nonnegative integer multiplicity required')
            if label=='L':need(count<=T0.get(int(key),0),'loss is not a subhistogram of T0')

def run():
    m=load('MODEL.json');validate_model(m)
    C=F(m['C']);rho=F(m['rho']);t=1-C;u=F(m['offset']);v=m['product_power']
    need(0<C<F(1,256) and F(1,2)<t<1 and t+u>1,'analytic parameter domain failed')
    need(0<rho<F(1,44),'loss-bound reserve domain failed')
    paid_mass=sum(r*n for r,n in P0.items());target_mass=sum(r*n for r,n in T0.items());B=sum(T0.values())
    need((paid_mass,target_mass,B)==(15861,16005,1416),'baseline mass/count differs')
    need(max(T0)==25 and P0[8]==8 and all(r<=5 for r in P0 if r!=8),'coarse baseline rank hypotheses differ')
    target_binomial=sum(comb(256,k)*64**(4-k) for k in range(5))
    target_threshold=25*64**4
    need(target_binomial>target_threshold,'target binomial certificate failed')
    paid_factor_gap=8*19**5-5*20**5
    need(paid_factor_gap>0,'paid factor certificate failed')
    baseline_target_lower=F(target_mass*64,65)
    baseline_paid_upper=F(19,20)*paid_mass+F(64,20)
    need(baseline_target_lower==F(1024320,65) and baseline_paid_upper==F(301423,20),'baseline rational constants differ')
    need(F(43)/(1-rho)<44 and 43**2==1849 and 1849<8*3**5==1944,'integer-addition rank envelope failed')
    target_lower=baseline_target_lower-44
    gamma_upper=(baseline_paid_upper+129)/target_lower
    delta_upper=F(B*9)/target_lower
    need(target_lower==F(1021460,65)>0,'remaining target denominator failed')
    need(gamma_upper==F(19760195,20429200)<F(97,100),'gamma rational bound failed')
    need(delta_upper==F(828360,1021460)<F(97,100),'delta rational bound failed')
    gamma_gap=97*20429200-100*19760195;delta_gap=97*1021460-100*828360
    need(gamma_gap==5612900 and delta_gap==16245620,'tail cross-product margins differ')
    tail_binomial=97**2+32*3*97+comb(32,2)*9
    need(tail_binomial>2*97**2 and v==32*32,'tail-power binomial certificate failed')
    reserve_threshold=F(1,256*(2**32-4))
    need(reserve_threshold==F(1,1099511626752) and rho>reserve_threshold,'reserve gap domain failed')
    envelope_upper=F(1)/(1+v*rho)+F(4,2**32)
    need(envelope_upper<1,'finite rational three-moment envelope failed')
    # Domain examples are not a search or verification of all future profiles.
    validate_ledger({'1':8},{})
    controls=[]
    tests=[('fractional_addition',lambda:validate_ledger({'1':F(1,2)},{})),
           ('signed_netting',lambda:validate_ledger({'25':1,'1':-1},{})),
           ('loss_not_subhistogram',lambda:validate_ledger({}, {'25':241})),
           ('new_targets',lambda:validate_ledger({}, {},new_targets={'26':1})),
           ('paid_deletions',lambda:validate_ledger({}, {},paid_deletions={'1':1}))]
    for name,operation in tests:
        try:operation()
        except ValueError:controls.append(dict(name=name,observed='REJECTED_INVALID_LEDGER_DOMAIN'))
        else:raise ValueError('ledger-domain mutant survived: '+name)
    for name,key,value in [('separate_quotas_replace_mixed','one_strict_mixed_budget_required',False),
                           ('ambient_overclaim','rank_bound_is_ambient_certificate',True),
                           ('earned_target_overclaim','all240H25_hypothetical',False),
                           ('changed_parameter','C','1/256')]:
        bad=json.loads(json.dumps(m));bad[key]=value
        try:validate_model(bad)
        except ValueError:controls.append(dict(name=name,observed='REJECTED_CHANGED_THEOREM_HYPOTHESIS'))
        else:raise ValueError('model mutant survived: '+name)
    # A=42H1,L=H4 meet the two loose quotas but cannot fit R0<43.
    validate_ledger({'1':42},{'4':1})
    mixed_trap_lower=42+2*(1-rho)
    need(42<43 and 4<44 and mixed_trap_lower>43,'independent-quota countercontrol failed')
    return dict(status='PASS_STATIC_RATIONAL_INTEGER_PROFILE_ENVELOPE',
        parameters=dict(C=str(C),rho=str(rho),t=str(t),c=8,b=9,u=str(u),v=v),
        exact_certificates=dict(paid_rankmass=paid_mass,target_rankmass=target_mass,target_count=B,
            target_binomial_scaled_sum=target_binomial,target_binomial_scaled_threshold=target_threshold,
            paid_factor_integer_gap=paid_factor_gap,baseline_target_lower=str(baseline_target_lower),
            baseline_paid_tail_upper=str(baseline_paid_upper),loss_upper=44,additional_paid_tail_upper=129,
            remaining_target_lower=str(target_lower),gamma_upper=str(gamma_upper),delta_upper=str(delta_upper),
            gamma_cross_product_margin=gamma_gap,delta_cross_product_margin=delta_gap,
            tail_binomial_scaled_sum=tail_binomial,tail_binomial_scaled_threshold=2*97**2,
            reserve_threshold=str(reserve_threshold),three_moment_upper=str(envelope_upper),
            three_moment_positive_gap=str(1-envelope_upper),mixed_quota_trap_lower=str(mixed_trap_lower)),
        negative_controls=controls,
        universal_coverage='PROOF.md supplies quantified reasoning for every finite honest integer A and subhistogram L; finite checks are not enumeration.',
        R0_upper_assumed=True,actual_future_mixed_budget_verified=False,all240H25_hypothetical=True,
        rank_bound_is_ambient_certificate=False,physical_data_included=False,compiler_admitted=False,funded_kappa=None)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);a=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(128*1024*1024,128*1024*1024));signal.alarm(30)
    try:value=run()
    except Exception as e:
        with a.receipt.open('x') as out:json.dump(dict(status='FAIL',exception=type(e).__name__,message=str(e)),out,indent=2);out.write('\n')
        raise
    with a.receipt.open('x') as out:json.dump(value,out,indent=2);out.write('\n')
    print(json.dumps(value,sort_keys=True))
