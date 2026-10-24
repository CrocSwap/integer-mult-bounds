"""Fully paid p16 invoice and ordinary BIT conversion; no global kappa claim.

Uses credited source-bound tail engines of Cinna Davis and zxv. The changed
helper ABI retains arbitrary independent rank4 endpoints, rather than paying
to complete them to rank8. Jacob Alan Sussman's mixed-target recursion and
Mark/Matarener's PR4697 parameter derivation are explicit predecessors.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import importlib.util,json,sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
THIN=ROOT/'research/query-thinned-controllers'
LOCAL={1:1319,2:1342,3:78,4:39,5:102,6:10,7:18}
OLD_LOCAL={1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}
HELPERS={4:4,8:432}
PARAMS={'tested':F('.00347545'),'uniform':F('.00347544'),
        'cover_gap':F(1,2**18)+F(1,10**10),'atom':F('.00346'),
        'admitted':F('.0034597'),'old_backend':F('.0000384599'),
        'alpha_gap':F(1,2**32),'prime_coefficient':2**26}

def need(c,m):
    if not c:raise ValueError(m)

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s)
    sys.modules[n]=m;s.loader.exec_module(m);return m

def source_engines():
    sys.path.insert(0,str(THIN))
    v=load(THIN/'verify.py','compact_productive_credited_tail')
    e=load(ROOT/'research/higher-moment-strictification/verify.py','compact_productive_exact_intervals')
    return v,e

def invoice(local,helpers):
    need(local==LOCAL and helpers==HELPERS,'Actual local paid/target profile required')
    row=json.loads((THIN/'BIT-CONTROLLER.json').read_bytes())
    old=row['invoice'];calls=old['thick_calls']
    need(calls==18 and old['thin_queries']==1665,'Literal p16 full/query inventory')
    targets=Counter({int(k):v for k,v in old['targets'].items()})
    paid=Counter({int(k):v for k,v in old['paid'].items()})
    targets[8]-=calls*439
    targets.update({k:calls*v for k,v in helpers.items()})
    for k,n in OLD_LOCAL.items():paid[k]-=calls*n
    paid.update({k:calls*v for k,v in local.items()})
    need(all(v>=0 for v in targets.values())and all(v>=0 for v in paid.values()),'No negative jobs')
    targets={k:v for k,v in sorted(targets.items())if v}
    paid={k:v for k,v in sorted(paid.items())if v}
    need(sum(targets.values())==11400 and sum(paid.values())==57339,'All independent originals and actual queries')
    need(targets[4]==72 and targets[8]==7776 and paid[4]==702,'Partial helper physical jobs')
    surplus=sum(k*v for k,v in targets.items())-sum(k*v for k,v in paid.items())
    need(surplus==753==old['rank_surplus'],'No new first-moment credit')
    return {'targets':targets,'paid':paid,'rank_surplus':surplus,
            'thick_calls':calls,'thin_queries':1665,'original_fields':11400,
            'main_original_fields':3552,'helper_original_fields':7848}

def certify(inv,params=None):
    p=dict(PARAMS if params is None else params)
    V,E=source_engines()
    tail=V.tail(E,inv,p['tested'],p['uniform'],17,18,p['alpha_gap'])
    c1=p['uniform']-p['cover_gap'];d=p['atom'];old=p['old_backend']
    ordinary=(1-d)*c1+d*old;b=p['admitted']
    need(p['tested']>p['uniform']>c1>0,'Tested/uniform/covered strict gaps')
    need(d>ordinary>b>0 and d<1-ordinary,'Ordinary adapter, recurrence and stock costs')
    need(p['prime_coefficient']>256/p['cover_gap'],'Actual bad-class fallback prime allowance')
    comparison={'current_admitted':F('.0034'),'current_exact_ordinary':F('.0034363538396')}
    old_c1=F('.003459')-F(1,2**18)
    comparison['PR4697_fixed_C0_prime_saturated_sup']=old_c1/(1+old_c1-old)
    gains={k:b/v-1 for k,v in comparison.items()}
    need(gains['current_exact_ordinary']>F(1,1000),'At least0.1% actual ordinary improvement')
    return {'params':p,'after_cover':c1,'ordinary_exact':ordinary,'admitted':b,
            'tail':tail,'comparators':comparison,'relative_gains':gains,
            'margins':{'adapter':d-ordinary,'ordinary_relaxation':ordinary-b,
                       'stock':1-ordinary-d,'prime_allowance':p['prime_coefficient']-256/p['cover_gap']},
            'WORD_changed':True,'new_whole_kappa':None,
            'scope':'Conditional ordinary BIT supplier only; main selected/complex result unchanged.'}

def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):encode(v)for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [encode(v)for v in x]
    return x

if __name__=='__main__':
    inv=invoice(LOCAL,HELPERS);result=certify(inv)
    print(json.dumps(encode({'invoice':inv,'certificate':result}),indent=2))
