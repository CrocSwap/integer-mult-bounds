"""Conditional #8035 4+4->8 invoices; no replacement word is installed."""
from collections import Counter
from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from pathlib import Path
from types import SimpleNamespace
import json, sys

if len(sys.argv)!=3:
    raise SystemExit('usage: check.py RESTORED_8035_MACHINE RESULT_JSON')
SOURCE=Path(sys.argv[1]).resolve()
OUTPUT=Path(sys.argv[2]).resolve()
sys.path.insert(0,str(SOURCE))
from upstream import install, HERE
install()
from calibration import (SMALL_GAP,SPLIT_TARIFF,HIGH_RATE,COMPLEX_C,SPLIT_TILT,PRODUCTIVE_TILT,prices)
from independent_binary_price import raw_moments,mass,rank_price,log_rank
from strict_moment import certify
from strong_binary import graph,caller,native_word
from strong_complex import load_changed,word
from outer_budget import qualify
from resources import requirements

def decimal(x):
    with localcontext() as ctx:
        ctx.prec=45
        return str(Decimal(x.numerator)/Decimal(x.denominator))

def bounds(T,P,c):
    t=1-c
    return mass(T,t,0)-mass(P,t,1),mass(T,t,1)-mass(P,t,0)

def hist(T,P):
    return {'target_count':sum(T.values()),'paid_count':sum(P.values()),
            'target':dict(sorted(T.items())),'paid':dict(sorted(P.items()))}

def modified(original,n,extra_rank1=0):
    P=original.copy();P[4]-=2*n;P[8]+=n;P[1]+=extra_rank1
    assert min(P.values())>=0
    return P

def derivative_lower(T,P,left,right):
    # D(c)=T(1-c)-P(1-c); independently enclose -D'(c)
    # on the complete interval 0<=left<=c<=right<=1.
    total=Q(0)
    for r in T.keys()|P.keys():
        s=T[r]-P[r]
        if not s or r==1:continue
        l,h=log_rank(r)
        low=rank_price(r,1-right)[0]*l
        high=rank_price(r,1-left)[1]*h
        total+=s*(low if s>0 else high)
    return total

def interval_strings(lohi):
    return {'lower':str(lohi[0]),'upper':str(lohi[1]),
            'lower_decimal':decimal(lohi[0]),'upper_decimal':decimal(lohi[1])}

def reject(*args):
    try:qualify(*args)
    except ArithmeticError:return
    raise AssertionError('unfunded signed control passed')

T,P=raw_moments(graph(),caller())
physical=native_word(285)
assert Counter(p.rank for p in physical.targets)==T and Counter(p.rank for p in physical.paid)==P
assert (sum(T.values()),sum(P.values()))==(18906,104904)
target=Q('.00389046');q=7
P6=modified(P,6);P7=modified(P,7);P36=modified(P,36);P36repair=modified(P,36,1)
assert bounds(T,P6,target)[1]<0<bounds(T,P7,target)[0]
assert bounds(T,P36repair,target)[1]<0
for paid in (P6,P36repair):
    assert derivative_lower(T,paid,target,Q(1,250))>0

bit_c=Q((Q('.00389050')*2**56).__floor__(),2**56)
assert target<bit_c<Q(1,250)
t,z,w=1-bit_c,SPLIT_TILT,PRODUCTIVE_TILT
den=mass(T,t,0)
alpha=mass(P7,t,1)/den
gamma=mass(P7,t+z,1)/(rank_price(12,z)[0]*den)
lam=rank_price(15,w)[1]*mass(T,t-w,1)/den
surplus=1-alpha**285-Q(1,64)*gamma**285-lam**285
assert surplus>Q(2,2**47)
fake=lambda h: [SimpleNamespace(rank=r) for r,n in h.items() for _ in range(n)]
invoice=SimpleNamespace(power=285,floor=15,low_cut=12,high_cut=12,targets=fake(T),paid=fake(P7))
bit_check=certify(invoice,bit_c,z,w,285,46,15,split_weight=Q(1,64))
surplus268=1-alpha**268-Q(1,64)*gamma**268-lam**268
assert surplus268>Q(2,2**50)
invoice268=SimpleNamespace(power=268,floor=15,low_cut=12,high_cut=12,targets=fake(T),paid=fake(P7))
bit_check268=certify(invoice268,bit_c,z,w,268,49,15,split_weight=Q(1,64))

g,layout=load_changed(HERE/'inputs')
positive=word(g,layout)
CT=Counter(p.rank for p in positive.targets);CP=Counter(p.rank for p in positive.paid)
assert (sum(CT.values()),sum(CP.values()))==(52608,281568)
positive_check=certify(positive,COMPLEX_C,Q(19,64),Q(23,64),128,14,16)
ctarg=bounds(CT,CP,target)
assert ctarg[0]>0

base=replace(SMALL_GAP,rank_logs=HIGH_RATE.rank_logs,bit_c=bit_c,
             ordinary=Q('.0038904998'),kappa=target,positive_stop_denominator=10**14)
strong=replace(base,kappa=Q('.003890463256835937'),positive_stop_denominator=10**20)
profiles={}
base268=replace(SPLIT_TARIFF,rank_logs=HIGH_RATE.rank_logs,bit_c=bit_c,
                ordinary=Q('.0038904998'),kappa=target,positive_stop_denominator=10**14)
for name,p in [('target',base),('target_268',base268),('near_positive_cap',strong)]:
    bit_debit,num_debit,rows=prices(p)
    assert (bit_debit,num_debit)==((21 if p.power==268 else 22),10)
    gap=Q(1,p.positive_stop_denominator); cap=COMPLEX_C-Q(num_debit,p.complex_log)
    signed=qualify(p.kappa,gap,p.ordinary,cap)
    reject(p.kappa,Q(0),p.ordinary,cap)
    reject(p.kappa,gap,p.kappa+4*gap,cap)
    reject(p.kappa,gap,p.ordinary,p.kappa+5*gap)
    previous=Q(0);stages=[]
    for h,covered,rate in rows:
        limit=min(p.eta,(249*covered+previous)/250)
        assert previous<rate<limit
        stages.append({'height':h,'covered':str(covered),'rate':str(rate),'limit':str(limit),'margin':str(limit-rate)})
        previous=rate
    stock=requirements(p)
    assert stock['all_size_margin_lower_at_entrance']>0
    profiles[name]={'kappa':str(p.kappa),'kappa_decimal':decimal(p.kappa),'gap':str(gap),
       'binary_debit':bit_debit,'numeric_debit':num_debit,'ordinary':str(p.ordinary),
       'positive_cap':str(cap),'positive_cap_decimal':decimal(cap),'signed':signed,
       'stages':stages,'stock':stock}

result={'scope':'Hypothetical seven valid placements; unchanged other productive and paid labels, typed ownership, supplier admission and all inherited premises. No replacement word constructed.',
  'target_kappa':str(target),'trial_c':str(bit_c),'trial_c_decimal':decimal(bit_c),
  'replacement_placements':7,'raw_binary_original':hist(T,P),'raw_binary_7':hist(T,P7),
  'raw_positive_48':hist(CT,CP),'binary_margin_target_6':interval_strings(bounds(T,P6,target)),
  'binary_margin_target_7':interval_strings(bounds(T,P7,target)),
  'binary_margin_target_36':interval_strings(bounds(T,P36,target)),
  'binary_margin_target_36_plus_one_rank1':interval_strings(bounds(T,P36repair,target)),
  'positive_margin_target':interval_strings(ctarg),
  'six_derivative_magnitude_lower':str(derivative_lower(T,P6,target,Q(1,250))),
  'all36_plus_repair_derivative_magnitude_lower':str(derivative_lower(T,P36repair,target,Q(1,250))),
  'strict_split_weight':str(Q(1,64)),'strict_surplus_floor_e18':(surplus*10**18).__floor__(),
  'strict_required':str(Q(2,2**47)),'bit_checker':bit_check,'positive_checker':positive_check,
  'strict_268_surplus_floor_e18':(surplus268*10**18).__floor__(),
  'strict_268_required':str(Q(2,2**50)),'bit_checker_268':bit_check268,
  'profiles':profiles}
OUTPUT.write_text(json.dumps(result,indent=2,default=str)+'\n')
print('PASS_CONDITIONAL_7_PLACEMENT_INVOICE, NOT AN INSTALLED WORD')
print('six margin',decimal(bounds(T,P6,target)[1]),'seven margin',decimal(bounds(T,P7,target)[0]))
print('36 plus rank1',decimal(bounds(T,P36repair,target)[1]))
print('strict surplus >=',Q(result['strict_surplus_floor_e18'],10**18))
for name,row in profiles.items():
    print(name,'kappa',row['kappa_decimal'],'signed',row['signed'],'A',row['stock']['log2_sufficient_public_precision'])
