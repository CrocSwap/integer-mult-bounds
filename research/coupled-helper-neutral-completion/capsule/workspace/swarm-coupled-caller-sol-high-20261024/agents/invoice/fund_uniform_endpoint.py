#!/usr/bin/env python3
"""Prepared independent endpoint/next-grid/outer arithmetic for uniform120.

Root execution only, after a promising actual word. Source compiler application,
ordinary work and physical global admission are explicitly separate gates.
Fresh atanh72/Taylor40 moments; frozen prior independent54+4 outer transcription.
No candidate/provider/author evaluator is imported.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
from collections import Counter
import argparse,importlib.util,json,time
from exact_moments import moment,power,minus,encode,need
from screen_uniform_global import invoice

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PRIOR=ROOT/'swarm-next-gain-sol-high-20261024/agents/numeric'
ENGINE=PRIOR/'exact_engine.py'
ENGINE_SHA='9ef7ee4082631566eb7903c3e21e517ef58039dca2a47104a2279c459589eb47'


def load_outer():
    need(sha256(ENGINE.read_bytes()).hexdigest()==ENGINE_SHA,
         'frozen independent outer transcription changed')
    spec=importlib.util.spec_from_file_location('prior_independent_outer',ENGINE)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.ledger


def evaluate(k,s,logpower,boundary):
    inv=invoice(16,7,boundary)
    return evaluate_profiles(inv['paid'],inv['targets'],k,s,logpower,
                             {'p':16,'a':7,'model':'uniform120-independent-g',
                              'mandatory_middle_H1':120,'boundary_H1':boundary})


def evaluate_profiles(P,T,k,s,logpower,model_metadata):
    need(F('.00302728823')<k<s<F('.0034'),'meaningful new endpoint/tested/BIT order')
    need(logpower in (1000,1100,1200),'bounded explicit logarithm choices')
    P,T=Counter(P),Counter(T)
    gap=(s-k)/7;need(gap.numerator==1,'exact unit height grid required')
    ambient,cutoff,floor,offset,B,theta,reserve=145,20,21,F(1,5),1024,F(63,64),F(1,10**12)
    t=1-s;target,paid=moment(T,t),moment(P,t)
    raw=minus(target,paid)
    alpha=paid[1]/target[0]
    gamma=moment(P,t+offset)[1]/(power(cutoff,offset)[0]*target[0])
    delta=F(floor*sum(T.values()))/(power(cutoff,s)[0]*target[0])
    eta=t*power(ambient,-B*s)[0]
    normalized=1/(1+B*reserve)+F(4,2**32)
    rounding_debit=F(4,2**32)
    minimum_reserve=rounding_debit/(B*(1-rounding_debit))
    predicates={'positive_tested_moment':raw[0]>0,
                'funded_alpha_reserve':alpha<1-reserve,
                'higher_paid_tail':gamma<F(97,100),
                'completion_target_tail':delta<F(97,100),
                'tail_domain':t+offset>=1,
                'normalized_completion_rounding':normalized<1,
                'tail_block':F(97,100)**128<F(1,16),
                'total_tails':4*F(97,100)**B<F(4,2**32),
                'split':cutoff**64<floor**63,
                'shifted_exits':2*cutoff**(B*64)<=ambient**(B*63),
                'eta':eta>theta**logpower,
                'initial_range':power(ambient,B*s)[1]<2**logpower}
    need(all(predicates.values()),'unfunded numerical predicates: '+
         ','.join(n for n,v in predicates.items()if not v))
    step=gap.denominator

    def wins(j):
        return (step*j+1)**logpower<2**j

    left,right=1,2
    while not wins(right):left,right=right,2*right
    while right-left>1:
        mid=(left+right)//2
        if wins(mid):right=mid
        else:left=mid
    j=right;H=step*j
    need(H>8*B and wins(j) and not wins(j-1),'exact height grid/preceding check')
    # Stronger admitted BIT comes from the frozen independent source receipt.
    prior_invoice=json.loads((PRIOR/'INVOICE-v2.json').read_bytes())
    sourcekeys=prior_invoice['source_keys']
    sourcepath=ROOT/'swarm-next-gain-sol-high-20261024/repository'/sourcekeys['path']
    need(sha256(sourcepath.read_bytes()).hexdigest()==sourcekeys['sha256'],
         'current source outer predicate definition changed')
    bit_atom,after_cover,bit_admitted=F(1,250),F(69,20000),F(17,5000)
    bit_actual=(1-bit_atom)*after_cover+bit_atom*F('.0000384599')
    need(bit_actual==F(8590884599,2500000000000) and bit_actual>bit_admitted>s,
         'ordinary BIT conversion/order')
    params=dict(kappa=k,tested_saving=s,complex_uniform_saving=k+6*gap,
                b=k+5*gap,a=k+4*gap,q=k+3*gap,bit_saving=bit_admitted,
                bit_atom=bit_atom,epsilon=1-gap,beta=1-3*gap,r0=gap/10,
                stop=gap,layout=gap,d=gap)
    outer=load_outer();margins,strict,functional=outer(params)
    need(set(strict)==set(sourcekeys['strict']) and set(functional)==set(sourcekeys['functional']),
         'complete source outer predicate inventory mismatch')
    need(len(strict)==54 and len(functional)==4 and min(strict.values())>0
         and min(functional.values())>0,'unfunded outer row')
    controls={'preceding_height_grid_rejected':not wins(j-1),
              'insufficient_reserve_completion_rejected':
                 1/(1+B*F(1,10**13))+F(4,2**32)>1,
              'old_log1000_eta_rejected_at_high_saving':
                 (eta<=theta**1000) if k>=F('.0033') else None,
              'ordinary_BIT_stock':1-bit_actual-bit_atom>0}
    bad=dict(params,bit_saving=F('.0027'))
    _,badstrict,badfunctional=outer(bad)
    controls['old_BIT_rejected']=any(v<=0 for v in (badstrict|badfunctional).values())
    # Scientific payload validation checks the same complete model definition,
    # not only its hash. Its physical premises remain unproved.
    def validate_profile(paid_profile,target_profile):
        need(Counter(paid_profile)==P and Counter(target_profile)==T,
             'claimed model profile differs from complete uniform invoice')
    mutant=P.copy();mutant[1]-=120
    try:validate_profile(mutant,T)
    except ValueError:controls['omitted_paid_H1_charge_rejected']=True
    else:raise ValueError('omitted paid H1 charge accepted')
    mutantT=T.copy();mutantT[8]+=16
    try:validate_profile(P,mutantT)
    except ValueError:controls['unearned_helper_credit_rejected']=True
    else:raise ValueError('unearned helper target accepted')
    need(all(v for v in controls.values()if v is not None),
         'one numerical or semantic control failed')
    result={'status':'PASS_CONDITIONAL_COMPLETE_PROFILE_ENDPOINT_ARITHMETIC_ONLY',
            'paid':P,'targets':T,'kappa':k,'tested':s,'gain_over_comparison':k-F('.00302728823'),
            'tuple':{'ambient':ambient,'cutoff':cutoff,'floor':floor,'offset':offset,
                     'tensor_power':B,'theta':theta,'logarithm_power':logpower},
            'raw_tested_margin':raw,'alpha_upper':alpha,'gamma_upper':gamma,
            'delta_upper':delta,'eta_lower':eta,'reserve':reserve,
            'strict_minimum_rounding_reserve':minimum_reserve,
            'reserve_above_minimum':reserve>minimum_reserve,
            'reserve_slack':1-reserve-alpha,'completion_slack':1-normalized,
            'predicates':predicates,'gap':gap,'j':j,'H':H,
            'grid_success':wins(j),'preceding_grid_fails':not wins(j-1),
            'grid_scope':'Least grid point for the stated sufficient logarithmic-range inequality only; '
                         'fresh precision may impose another threshold. No whole-compiler minimum.',
            'ordinary_BIT':{'atom':bit_atom,'after_cover':after_cover,'actual':bit_actual,
                            'admitted':bit_admitted,'stock_slack':1-bit_actual-bit_atom},
            'outer':{'parameters':params,'margins':margins,'strict':strict,
                     'functional':functional,'minimum_strict':min(strict.values()),
                     'minimum_functional':min(functional.values())},
            'source_predicates':sourcekeys,'independent_outer_engine_sha256':ENGINE_SHA,
            'controls':controls,
            'actual_global_closure':False,'ordinary_funded':False,
            'fresh_precision_source_applicable':False,
            'compiler_tuple_source_applicable':False,
            'whole_scientific_admission':False,
            'scope':'Numerical endpoint/height/54+4 outer arithmetic for a proposed complete profile. '
                    'No global word, source compiler parameter application, ordinary funding, '
                    'fresh precision or selected promotion is inferred.'}
    result.update(model_metadata)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--kappa',required=True)
    p.add_argument('--tested',required=True);p.add_argument('--logarithm-power',type=int,required=True)
    p.add_argument('--boundary-H1',type=int,choices=(0,120,240,480),required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();need(not a.output.exists(),'immutable receipt exists')
    start=time.monotonic()
    result=evaluate(F(a.kappa),F(a.tested),a.logarithm_power,a.boundary_H1)
    result['seconds']=time.monotonic()-start
    a.output.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
    print(json.dumps(encode({k:result[k]for k in ('status','kappa','tested','j','H',
                            'actual_global_closure','whole_scientific_admission')})))
