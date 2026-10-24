"""Complete source-relative recursive screens. No unknown bridge is free."""
from collections import Counter
from decimal import Decimal,localcontext
from fractions import Fraction as F
from algebra import need

def screen(f):
    t=f.old;paid=Counter({int(k):v for k,v in f.selected['paid'].items()})
    targets=Counter({int(k):v for k,v in f.selected['targets'].items()})
    local=Counter({int(k):v for k,v in f.p['paid'].items()})
    local.update({1:8,8:8})
    helpers=Counter({int(k):v for k,v in f.p['autonomous_native_helpers'].items()})
    helpers[9]+=8
    need(local==Counter({int(k):v for k,v in f.selected['local_paid'].items()}),'source local paid binding')
    need(helpers==Counter({int(k):v for k,v in f.selected['local_helpers'].items()}),'source helper targets binding')
    census_paid=Counter();census_targets=Counter()
    for event in f.controller['physical_events']:
        if event[0]=='LOCAL':census_paid.update(local);census_targets.update(helpers)
        elif event[0]=='QUERY_SHEAR':census_paid[1]+=112
        elif event[0]=='IDLE':census_paid[8*len(event[2])]+=224
    for row in f.controller['diagonal']:census_targets[1+8*sum(row[1:])]+=112
    need(census_paid==paid and census_targets==targets,'complete chronological source bill')
    calls=sum(e[0]=='LOCAL' and e[3] for e in f.controller['physical_events'])
    need(calls==16,'source applicable backward census')
    supplied=paid.copy();supplied[8]-=8*calls
    bought=supplied.copy();bought[1]+=112*calls
    def numerical(p,a,rho=Decimal(1)):
        with localcontext() as c:
            c.prec=65;power=Decimal(1)-a
            T=sum(Decimal(n)*Decimal(r)**power for r,n in targets.items())
            P=sum(Decimal(n)*Decimal(r)**power for r,n in p.items())
            return T-(rho**power)*P,T,P
    # Directed exact r^(249/250) enclosure: no floating-point sign decision.
    scale=2**80;powers={r:t.integer_root(r**249*scale**250,250) for r in set(paid)|set(targets)}
    def interval(p):
        lo=hi=0
        for r,v in powers.items():
            coeff=targets[r]-p[r]
            lo+=coeff*(v if coeff>=0 else v+1)
            hi+=coeff*(v+1 if coeff>=0 else v)
        return [F(lo,scale),F(hi,scale)]
    base004=interval(paid);ideal004=interval(supplied);bought004=interval(bought)
    need(base004[1]<0<ideal004[0] and bought004[1]<0,'exact full .004 decision')
    # If restoration costs g H1/call, the necessary inequality is g < margin/16.
    cap=[v/calls for v in ideal004]
    # Largest nonnegative integer per-call H1 cost certified below cap.
    max_integer=cap[0].numerator//cap[0].denominator
    if F(max_integer)==cap[0]:max_integer-=1
    allocated32=supplied.copy();allocated32[1]+=32*calls
    allocated32_004=interval(allocated32)
    need(allocated32_004[0]>0,'conditional 32 H1 allocation remains inside .004 cap')
    precision=[];allowances=[];allocation_screens=[]
    for s in ['0.0033','0.004','0.006','0.007']:
        a=Decimal(s);margin,T,P=numerical(supplied,a)
        # Hypothetical uniform leading-precision expansion of *all* paid children.
        with localcontext() as c:
            c.prec=65;rho_limit=(T/P)**(1/(1-a))
        m32,T32,P32=numerical(allocated32,a)
        with localcontext() as c:
            c.prec=65;rho32=(T32/P32)**(1/(1-a))
        allocation_screens.append({'saving':s,'conditional_margin_numeric':str(m32),
            'uniform_paid_precision_ceiling_numeric':str(rho32)})
        allowances.append({'saving':s,'conditional_margin_numeric':str(margin),
            'joint_observer_plus_termination_H1_per_call_numeric':str(margin/Decimal(calls)),
            'uniform_paid_precision_factor_ceiling_numeric':str(rho_limit)})
        m,_,_=numerical(supplied,a,Decimal('1.01'))
        precision.append({'saving':s,'margin_if_paid_precision_multiplied_by_1_01_numeric':str(m)})
    # Actual matched forward bank completion buys targets too, so no rank gain.
    bank=f.bank['invoice'];up_paid=sum(int(r)*n for r,n in bank['completion_paid_delta'].items())
    before=sum(int(r)*n for r,n in bank['old_cold_targets'].items())
    after=358*9
    need(up_paid==after-before==136,'forward bank completion rank neutrality')
    return {'source_paid_rank_mass':sum(r*n for r,n in paid.items()),
        'source_target_rank_mass':sum(r*n for r,n in targets.items()),
        'applicable_backward_calls':calls,
        'selected_to_conditional_compressed_exit_delta':{'H8':-128},
        'exact_signed_moment_at_004':{
            'selected':list(map(str,base004)),
            'compressed_observer_supplied_conditionally':list(map(str,ideal004)),
            'full_QY_bought_independently':list(map(str,bought004)),
            'combined_observer_and_termination_H1_per_call_strict_cap_interval':list(map(str,cap)),
            'maximum_certifiably_affordable_integer_H1_per_call':max_integer},
        'unimplemented_design_allocation_32_H1_per_call':{
            'status':'Design budget, not an algorithm or achieved saving',
            'suggested_split_H1_per_call':{'joint_observer':16,'extra_termination':16},
            'exact_signed_moment_interval_at_004':list(map(str,allocated32_004)),
            'numeric_regime_screens':allocation_screens},
        'conditional_numeric_allowances':allowances,'precision_sensitivity':precision,
        'forward_bank_completion_paid_rank':up_paid,'forward_bank_completion_target_rank':after-before,
        'ordinary_BIT_selected_admitted_saving':f.selected['ordinary_BIT']['admitted'],
        'ordinary_BIT_needs_new_admission_for_004':True,
        'candidate_combinations':[
            {'name':'independent decoder','observer':'fresh 112 QY fields per backward call',
             'verdict':'fails exact .004 recursive screen','admissible_new_kappa':None},
            {'name':'forward query bank with no displacement/restoration proof',
             'verdict':'not composable yet: only independent helper xi, forward direction, all paid calls and upgrades retained',
             'admissible_new_kappa':None},
            {'name':'eight-mode rebasing alone','verdict':'fails actual second-generation subspace witness','admissible_new_kappa':None},
            {'name':'balanced history-augmented coupled transducer',
             'verdict':'priority candidate; local boundary compiled, joint endogenous observer and bounded termination unproved',
             'known_boundary_ordinary_per_application':{'ADD':1344,'SCALE':16,'MONOMIAL':240,'new_owned_fields':0},
             'unknown_costs':['joint observation at actual paid source versions','history termination/restoration',
                              'typed caller including thin queries and endpoints','precision and tape compiler','outer admission'],
             'conditional_numeric_allowances_reference':'conditional_numeric_allowances',
             'admissible_new_kappa':None}],
        'scope':'All costs source-relative. Observer and termination share one allowance; no independent stacking of optimistic credits.',
        'new_kappa':None}
