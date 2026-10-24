"""Reprice against the PR5413 frontier selected during the submission refresh.
The full selected admission remains inherited; this checks its declared prices.
"""
import json
from collections import Counter
from decimal import Decimal,localcontext
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from algebra import need
HERE=Path(__file__).resolve().parent

def screen(f):
    raw=(HERE/'inputs/CURRENT-FUNDING.json').read_bytes();funding=json.loads(raw)
    record=json.loads((HERE/'inputs/CURRENT-SELECTED.json').read_text())
    successor=json.loads((HERE/'inputs/SUCCESSOR-CONTROLLER.json').read_text())
    need(record['source_certificate_sha256']==sha256(raw).hexdigest(),'current selected price receipt hash')
    need(record['kappa']==funding['kappa'],'current selected kappa binding')
    paid=Counter({int(k):v for k,v in funding['paid'].items()})
    targets=Counter({int(k):v for k,v in funding['targets'].items()})
    local=Counter({int(k):v for k,v in f.p['paid'].items()});local[8]+=8
    helpers=Counter({int(k):v for k,v in f.p['autonomous_native_helpers'].items()});helpers[8]+=8
    pc=Counter();tc=Counter();calls=0
    for e in successor['physical_events']:
        if e[0]=='LOCAL':
            need(e[3],'current selected FULL orientation');calls+=1
            pc.update(local);tc.update(helpers)
        elif e[0]=='QUERY_SHEAR':pc[1]+=112
        elif e[0]=='IDLE':pc[8*len(e[2])]+=224
    for row in successor['diagonal']:tc[1+8*sum(row[1:])]+=112
    need(calls==18 and pc==paid and tc==targets,'current whole-caller chronological profile')
    supplied=paid.copy();supplied[1]+=8*calls;supplied[8]-=8*calls
    newtargets=targets.copy();newtargets[9]+=8*calls;newtargets[8]-=8*calls
    oldtargets=Counter({int(k):v for k,v in f.selected['targets'].items()})
    need(newtargets==oldtargets,'restored R9 helper targets are source-bound')
    bought=supplied.copy();bought[1]+=112*calls
    scale=2**80;rs=set(paid)|set(newtargets)
    powers={r:f.old.integer_root(r**249*scale**250,250) for r in rs}
    def interval(p,t):
        lo=hi=0
        for r,v in powers.items():
            c=t[r]-p[r];lo+=c*(v if c>=0 else v+1);hi+=c*(v+1 if c>=0 else v)
        return [F(lo,scale),F(hi,scale)]
    ideal=interval(supplied,newtargets);cap=[x/calls for x in ideal]
    need(50<cap[0]<cap[1]<51,'current exact .004 cap')
    bought_interval=interval(bought,newtargets);need(bought_interval[1]<0,'current fresh decoder loses')
    def numerical(p,t,a):
        with localcontext() as ctx:
            ctx.prec=65;exponent=1-a
            T=sum(Decimal(n)*Decimal(r)**exponent for r,n in t.items())
            P=sum(Decimal(n)*Decimal(r)**exponent for r,n in p.items())
            return T-P,(T/P)**(1/exponent)
    allocations=[];allocated=supplied.copy();allocated[1]+=32*calls
    for s in ['0.0033','0.004','0.006','0.007']:
        a=Decimal(s);m,rho=numerical(supplied,newtargets,a)
        m32,rho32=numerical(allocated,newtargets,a)
        allocations.append({'saving':s,'conditional_margin_numeric':str(m),
            'combined_observer_and_extra_termination_H1_per_call_cap_numeric':str(m/calls),
            'uniform_paid_precision_factor_ceiling_numeric':str(rho),
            'margin_with_unimplemented_32_H1_allocation_numeric':str(m32),
            'precision_ceiling_with_32_H1_allocation_numeric':str(rho32)})
    need(interval(allocated,newtargets)[0]>0,'current conditional 32 H1 allocation passes .004')
    return {'canonical_promotion_commit':'1a3ced60b2f7a46bc70280a04f2eeb8ca027c700',
        'selected_kappa':record['decimal'],'selected_review':record['review'],
        'scope':'New selected promotion acknowledged; price profile replayed here, not complete admission.',
        'paid_jobs':sum(paid.values()),'productive_fields':sum(targets.values()),
        'paid_rank_mass':sum(r*n for r,n in paid.items()),
        'target_rank_mass':sum(r*n for r,n in targets.items()),'applicable_backward_FULLs':calls,
        'conditional_paid_delta':{'H1':144,'H8':-144},
        'conditional_target_delta':{'H8':-144,'H9':144},
        'conditional_restored_target_credit_requires_proved_observer':True,
        'exact_signed_moment_at_004':{'current_selected':list(map(str,interval(paid,targets))),
            'conditional_supplied_observer':list(map(str,ideal)),
            'fresh_112_field_observer':list(map(str,bought_interval)),
            'combined_observer_and_extra_termination_H1_per_call_cap':list(map(str,cap)),
            'unimplemented_32_H1_allocation':list(map(str,interval(allocated,newtargets)))},
        'maximum_certifiably_affordable_integer_H1_per_call':50,
        'conditional_numeric_allowances':allocations,
        'ordinary_BIT_selected_admitted_saving':funding['ordinary_BIT']['admitted'],
        'new_kappa':None}
