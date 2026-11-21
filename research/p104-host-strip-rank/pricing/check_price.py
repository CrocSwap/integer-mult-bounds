#!/usr/bin/env python3
"""Exact k=76 price screens plus arbitrary-e graph arithmetic.

The real-word implications need the stated frame and piece-partition
hypotheses. Integer inequalities enclose all powers; no floats are used.
"""
from collections import Counter
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from fractions import Fraction as F
from hashlib import sha1
from math import comb
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE_DIR = HERE.parent
SCALE = 10**12
K = 76
BAR = F(128891,1000)
ROOTS = {}


def check_pins():
    expected={
        'CallerSGram.lean':'6c03a7f3b3c50fe4340cd105378409ca39abc474',
        'CallerEv.lean':'ad5aba9f52bd1d4b60c3023a8325ff68310c5561',
        'CallerHPQ.lean':'d1c93bc474630c0c251f8e1c7b08f5fe4f67e32e',
        'HPDual.lean':'cfeb604c351b23d95a843269dc353e341e11368f',
        'SchemaCostB.lean':'b6a1c4b03a81a99e59c433d110871f605bef9694',
    }
    for n,h in expected.items():
        b=(BASE_DIR/'source'/n).read_bytes()
        assert sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==h,n
    return expected


def root_bounds(b):
    if b not in ROOTS:
        rhs=b**99*SCALE**100
        lo,hi=0,(b+1)*SCALE
        while lo+1<hi:
            m=(lo+hi)//2
            if m**100<=rhs:lo=m
            else:hi=m
        assert lo**100<=rhs<(lo+1)**100
        ROOTS[b]=(F(lo,SCALE),F(lo if lo**100==rhs else lo+1,SCALE))
    return ROOTS[b]


def expr(items=()):
    x=Counter()
    for b,c in items:x[b]+=F(c)
    return {b:c for b,c in x.items() if c}


def add(*xs):return expr((b,c) for x in xs for b,c in x.items())
def mul(x,c):return expr((b,c*F(c0)) for b,c0 in x.items())


def interval(x):
    lo=hi=F(0)
    for b,c in x.items():
        a,z=root_bounds(b)
        lo+=c*(a if c>=0 else z)
        hi+=c*(z if c>=0 else a)
    return lo,hi


def display(v,rnd):
    with localcontext() as c:
        c.prec=45;c.rounding=rnd
        return str((Decimal(v.numerator)/Decimal(v.denominator)).quantize(Decimal('0.000000000001')))


def emit(x):
    a,b=interval(x)
    return {'coefficient_by_base':{str(k):str(v) for k,v in sorted(x.items())},
            'exact_lower':str(a),'exact_upper':str(b),
            'decimal_lower':display(a,ROUND_FLOOR),'decimal_upper':display(b,ROUND_CEILING)}


def v(d):return expr([(8*d+1,1),(8*d,-1)])
def split(d):return expr([(8,1),(8*(d-1),1),(8*d,-1)])
def delta(d):return {} if d==0 else expr([(1,1),(8*d,1),(8*d+1,-1)])


def certify_discrete_monotonicity():
    # Each comparison is independently enclosed using exact rational endpoints.
    for d in range(2,K):
        assert interval(add(v(d),mul(v(d+1),-1)))[0]>0,('v',d)
        assert interval(add(split(d+1),mul(split(d),-1)))[0]>0,('split',d)
    for d in range(K):
        assert interval(add(delta(d+1),mul(delta(d),-1)))[0]>0,('delta',d)
    for d in range(2,K-1):
        # split(d+1)-delta(d) increases when the odd event itself is a
        # proper piece of a split role of degree at least d+1.
        f=add(split(d+1),mul(delta(d),-1))
        g=add(split(d+2),mul(delta(d+1),-1))
        assert interval(add(g,mul(f,-1)))[0]>0,('coupled',d)


def turan_min_edges(k,r):
    q,t=divmod(k,r)
    return t*comb(q+1,2)+(r-t)*comb(q,2)


def graph_arithmetic():
    data=[]
    for rank in range(2,28):
        minimum=turan_min_edges(K,rank)
        data.append({'rank_upper':rank,'e':rank-2,'min_nonhub_edges':minimum,
                     '73_pair_role_excluded':minimum>73})
    assert data[24]['rank_upper']==26 and data[24]['min_nonhub_edges']==74
    assert data[25]['rank_upper']==27 and data[25]['min_nonhub_edges']==71
    clusters=[]
    for rank in range(2,6):
        lower=turan_min_edges(K,rank)
        upper=(rank+1)*73+(rank-1)*K//2
        clusters.append({'e':rank-2,'rank_upper':rank,'global_edge_lower':lower,
                         'disjoint_cluster_capacity_upper':upper,'excluded':lower>upper})
    assert [x['excluded'] for x in clusters]==[True,True,True,False]
    return {'pair_only':data,'disjoint_cluster_necessary_screen':clusters}


def main():
    pins=check_pins()
    certify_discrete_monotonicity()
    # The two global singleton-piece hubs contribute 2*(p(609)-76p(8));
    # 76 singleton leaves contribute 76*(p(9)-p(8)); and 73 degree>=2
    # remaining roles are bounded by 73*(p(17)-p(16)). Q=T=1.
    base=mul(expr([(609,2),(17,73),(9,76),(8,-228),(16,-73),(1,-1)]),F(104,K))
    norm=F(104,K)
    # Broader base for arbitrary D>=1 on all 149 other roles: v(D)<=v(1).
    assert interval(add(v(1),mul(v(2),-1)))[0]>0
    broad_base=mul(expr([(609,2),(9,149),(8,-301),(1,-1)]),norm)
    broad_excess=add(broad_base,mul(expr([(1,-1)]),norm),mul(delta(76),2*norm))
    assert interval(broad_excess)[1]<BAR
    cases={
        'any_excess_e_at_least1_no_piece_partition': add(base,mul(expr([(1,-1)]),norm),mul(delta(76),2*norm)),
        'two_split_any_odd_mask': add(base,mul(split(2),-2*norm),mul(delta(76),norm)),
        'one_split_degree3_odd_mask_at_most2': add(base,mul(split(3),-norm),mul(delta(2),norm)),
        'one_split_degree4_packed_odd_mask_at_most26': add(base,mul(split(4),-norm),mul(delta(26),norm)),
        'one_split_degree5_any_odd_mask': add(base,mul(split(5),-norm),mul(delta(76),norm)),
        'one_split_degree2_query_control': add(base,mul(split(2),-norm)),
        'one_split_degree2_singleton_odd_control': add(base,mul(split(2),-norm),mul(delta(1),norm)),
        'one_split_degree3_mask3_control': add(base,mul(split(3),-norm),mul(delta(3),norm)),
        'one_split_degree4_mask76_control': add(base,mul(split(4),-norm),mul(delta(76),norm)),
    }
    for name in list(cases)[:5]:assert interval(cases[name])[1]<BAR,name
    for name in list(cases)[5:]:assert interval(cases[name])[0]>BAR,name
    assert interval(add(expr([(1,1)]),mul(delta(76),-1)))[0]>0
    # If the odd event is itself a proper piece of a split role with degree
    # >=3, then for d>=2 use split(d+1)-delta(d), and for d=1 use split(3).
    attached_d1=add(base,mul(split(3),-norm),mul(delta(1),norm))
    attached_d2=cases['one_split_degree3_odd_mask_at_most2']
    assert interval(attached_d1)[1]<interval(attached_d2)[0]
    assert interval(attached_d2)[1]<BAR
    output={'sources_git_blob_sha1':pins,'k':K,'Q':1,
            'tight_cases':{'T':1,'e':0},'excess_case':{'T':'1+e','e':'integer >= 1'},
            'role_template':{'full_mask_hubs':2,'hub_pieces':'76 singleton pieces each',
                             'leaves':76,'other_nonleaf_roles':73,'stagewise_matching_required':True,
                             'piece_partition_matching_required_for_split_cases_only':True},
            'broader_excess_role_template':{'full_mask_hubs':2,'hub_pieces':'76 singleton pieces each',
                                             'other_roles':149,'other_degrees':'1..76',
                                             'stagewise_matching_required':True,'piece_partition_required':False},
            'broader_excess_model_upper':emit(broad_base),
            'broader_excess_repo_upper':emit(broad_excess),
            'baseline_upper':emit(base), 'conditional_upper_bounds':{k:emit(v) for k,v in cases.items()},
            'attached_singleton_upper':emit(attached_d1),
            'attached_piece_size_at_least2_upper':emit(attached_d2),
            'split_penalty_unscaled_degree2':emit(split(2)),
            'odd_idle_correction_unscaled_size76':emit(delta(76)),
            'graph':graph_arithmetic(),
            'integer_root_certificates':{str(b):{'floor':int(a*SCALE),'ceiling':int(z*SCALE),'denominator':SCALE}
                                         for b,(a,z) in sorted(ROOTS.items())},
            'scope':'Conditional partition-matched two-hub price inequalities and conditional signed-Gram rank filters; no construction, universal k76 bound or kappa gain.'}
    (HERE/'RESULT.json').write_text(json.dumps(output,indent=2)+'\n')
    print('PASS pinned sources, integer power certificates, monotonicity and graph arithmetic')
    print('e>=1, unrestricted other degrees: upper <= '+output['broader_excess_repo_upper']['decimal_upper'])
    for name in list(cases)[:5]:
        r=output['conditional_upper_bounds'][name]
        print(name+': upper <= '+r['decimal_upper'])
    print('controls: one split degree-2 does not meet the target')
    print('result:',HERE/'RESULT.json')


if __name__=='__main__':main()
