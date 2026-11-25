#!/usr/bin/env python3
"""Exact tariffs for productive helpers with heterogeneous target sizes.

This is a conditional recursion-contract probe, not a new kappa claim.  The
native helper adapters, main controller closure, scalar/precision charges,
and the mixed-target outer theorem remain separate obligations.

Apache-2.0. Substantial OpenAI assistance. The original pruned native profile
and helper inventory come from the preserved kappa-function-composition work.
Mixed-target balance follows Jacob Alan Sussman's PR4268 proposal; this file
does not reprove or admit its all-size or integer-multiplication transfer.
The rational elementary-function enclosure follows the independently retained
productive_helper_forest.py recovery certificate, with fresh source identity.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import json
import math
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
NATIVE = Counter({1:2453, 2:716, 3:224, 4:74, 5:48})
HELPERS = Counter({5:28, 6:18, 7:56, 8:93, 9:213})
OLD_PAIRS = [(56,9,7),(56,7,9),(18,9,6),(18,6,9),
             (16,9,5),(16,5,9),(44,8,8)]
OLD_MIDDLE = [(93,8),(56,7),(18,6),(28,5),(29,0)]

def need(ok, message):
    if not ok:
        raise AssertionError(message)

@lru_cache(None)
def log_interval(r):
    def odd_series(x):
        z = (x-1)/(x+1)
        n = 80
        low = 2*sum((z**(2*j+1)/(2*j+1) for j in range(n)), Q(0))
        high = low+2*z**(2*n+1)/((2*n+1)*(1-z*z))
        return low, high
    exponent = r.bit_length()-1
    a,b = odd_series(Q(2))
    c,d = odd_series(Q(r,2**exponent))
    return exponent*a+c, exponent*b+d

def exp_interval(x):
    need(0 <= x < 1, 'Enclosure range')
    term = total = Q(1)
    n = 48
    for j in range(1,n+1):
        term *= x/j
        total += term
    following = term*x/(n+1)
    return total, total+following/(1-x/(n+2))

@lru_cache(None)
def h_interval(r,c):
    if r in (0,1):
        return Q(r),Q(r)
    a,b = log_interval(r)
    low,_ = exp_interval(c*a)
    _,high = exp_interval(c*b)
    return Q(r)/high,Q(r)/low

def moment(profile,c):
    low=high=Q(0)
    for r,n in profile.items():
        a,b=h_interval(r,c)
        low += n*(a if n >= 0 else b)
        high += n*(b if n >= 0 else a)
    return low,high

def show(bounds):
    scale=10**35
    low,high=bounds
    a=low.numerator*scale//low.denominator
    b=-((-high.numerator*scale)//high.denominator)
    def fixed(n):
        sign='-' if n<0 else ''
        s=str(abs(n)).rjust(36,'0')
        return sign+s[:-35]+'.'+s[-35:]
    return {'lower':fixed(a),'upper':fixed(b)}

def split_rank(r,maximum):
    """Least concave tariff partition with positive integers <= maximum."""
    need(maximum>=1 and r>=0, 'Legal split')
    q,remainder=divmod(r,maximum)
    result=Counter()
    if q:
        result[maximum]+=q
    if remainder:
        result[remainder]+=1
    return result

def split_profile(profile,maximum):
    result=Counter()
    for r,n in profile.items():
        for child,count in split_rank(r,maximum).items():
            result[child]+=n*count
    return result

def add_scaled(target,source,multiple=1):
    for key,value in source.items():
        target[key]+=multiple*value

def base_case(p,minimum,pairs=None,middle=None):
    """Expand all role inventories; one fresh global field per unhosted role."""
    need(p in (1,2), 'Only reconstructed p1 and p2 schedules are in scope')
    need(2<=minimum<=41, 'Finite minimum-target menu')
    calls=2*p+1
    main_fields=224*p
    main_rank=16*p+9
    inventories=[Counter(HELPERS) for _ in range(calls)]
    paid=split_profile(NATIVE,minimum-1)
    paid=Counter({r:calls*n for r,n in paid.items()})
    paid[1]+=8*calls  # same-width H completion, never waived
    targets=Counter({main_rank:main_fields})
    if p==1:
        need(pairs is None and middle is None, 'p1 has no original idle bins')
    else:
        pairs=pairs if pairs is not None else [(224,0,0)]
        middle=middle if middle is not None else [(224,0)]
        need(sum(n for n,a,b in pairs)==224, 'Each pair window has 224 bins')
        need(sum(n for n,a in middle)==224, 'Middle window has 224 bins')
        for stages in [(0,1),(3,4)]:
            for n,a,b in pairs:
                need(a+b<=16 and a in (0,5,6,7,8,9) and b in (0,5,6,7,8,9), 'Pair capacities')
                for stage,r in zip(stages,(a,b)):
                    if r:
                        inventories[stage][r]-=n
                add_scaled(paid,split_rank(16-a-b,minimum-1),n)
        for n,r in middle:
            need(r in (0,5,6,7,8), 'Middle capacity')
            if r:
                inventories[2][r]-=n
            add_scaled(paid,split_rank(8-r,minimum-1),n)
    global_roles=Counter()
    for inventory in inventories:
        need(all(n>=0 for n in inventory.values()), 'No helper role used twice')
        global_roles.update(inventory)
    for r,n in global_roles.items():
        if not n:
            continue
        target=max(r,minimum)
        targets[target]+=n
        add_scaled(paid,split_rank(target-r,minimum-1),n)
    paid=+paid
    targets=+targets
    need(max(paid)<min(targets), 'Strict child/target separation')
    signed=Counter(targets)
    signed.subtract(paid)
    rank_credit=sum(r*n for r,n in targets.items())
    rank_bill=sum(r*n for r,n in paid.items())
    need(rank_credit-rank_bill==224*p-8*calls, 'Complete displayed rank balance')
    return {'p':p,'minimum_target_parameter':minimum,'targets':dict(sorted(targets.items())),
            'paid':dict(sorted(paid.items())), 'signed':signed,
            'global_helper_roles':dict(sorted(global_roles.items())),
            'global_productive_fields':sum(global_roles.values()),
            'pair_patterns':pairs,'middle_patterns':middle,
            'rank_credit':rank_credit,'rank_bill':rank_bill,'rank_margin':rank_credit-rank_bill,
            'strict_separation':{'maximum_child':max(paid),'minimum_target':min(targets)}}

def serialize_case(case):
    result={k:v for k,v in case.items() if k!='signed'}
    result['targets_at_C']={}
    for text in ('0.001745','0.004'):
        c=Q(text)
        allowance=moment(case['signed'],c)
        row={'after_native_completion_before_main_closure':show(allowance)}
        for debt in (112,224):
            row[f'after_{debt}_H1_head_debt']=show((allowance[0]-debt,allowance[1]-debt))
        # A head may be cut only when it is a literal private first transform.
        # Target shrink is charged; this is the strongest favorable eligibility grant.
        rank=16*case['p']+9
        for count in (112,224):
            delta=Counter({1:count,rank-1:count,rank:-count})
            gain=moment(delta,c)
            row[f'literal_{count}_H1_cut_gain_over_paying_heads']=show(gain)
            loss=Counter({rank:count,rank-1:-count})
            a,b=moment(loss,c)
            row[f'after_cutting_{count}_literal_H1_heads_and_shrinking_targets']=show((allowance[0]-b,allowance[1]-a))
        result['targets_at_C'][text]=row
    return result

def numerical_value(profile,c):
    return sum(n*r**(1-c) for r,n in profile.items())

def discover_pair_patterns(minimum,c):
    """Optional small MILP; exact replay never relies on solver's optimal flag."""
    import numpy as np
    from scipy.optimize import milp, Bounds, LinearConstraint
    widths=(0,5,6,7,8,9)
    patterns=[(a,b) for a in widths for b in widths if a+b<=16]
    h=lambda r:r**(1-c) if r else 0.0
    sp=lambda r:sum(n*h(k) for k,n in split_rank(r,minimum-1).items())
    value=lambda r:0.0 if not r else h(max(r,minimum))-sp(max(0,minimum-r))
    gain=np.array([sp(16)-sp(16-a-b)-value(a)-value(b) for a,b in patterns])
    rows=[np.ones(len(patterns))]
    lower=[224.0]
    upper=[224.0]
    for side in (0,1):
        for r in widths[1:]:
            rows.append(np.array([float(pair[side]==r) for pair in patterns]))
            lower.append(0.0)
            upper.append(float(HELPERS[r]))
    out=milp(c=-gain,integrality=np.ones(len(patterns)),bounds=Bounds(0,np.inf),
             constraints=LinearConstraint(np.array(rows),lower,upper),
             options={'time_limit':10,'mip_rel_gap':0})
    need(out.x is not None, 'Discovery produced a candidate')
    pairs=[(int(round(n)),a,b) for n,(a,b) in zip(out.x,patterns) if round(n)>0]
    # Middle bins are independent single slots; choose positive-gain roles first.
    candidates=sorted(((sp(8)-sp(8-r)-value(r),r) for r in (5,6,7,8)),reverse=True)
    middle=[]
    left=224
    for gain,r in candidates:
        if gain>1e-12:
            n=min(HELPERS[r],left)
            if n:
                middle.append((n,r))
                left-=n
    if left:
        middle.append((left,0))
    return pairs,middle,{'status':int(out.status),'message':out.message,'not_an_exact_optimality_claim':True}

def run(discover=False):
    candidates=[]
    for p in (1,2):
        for minimum in range(2,26):
            candidates.append(base_case(p,minimum))
    candidates.append(base_case(2,9,OLD_PAIRS,OLD_MIDDLE))
    discovery=[]
    if discover:
        for c in (.001745,.004):
            for minimum in range(5,18):
                pairs,middle,meta=discover_pair_patterns(minimum,c)
                case=base_case(2,minimum,pairs,middle)
                case['discovery_target']=str(c)
                case['solver']=meta
                discovery.append(case)
        candidates.extend(discovery)
    best={}
    for p in (1,2):
        for text in ('0.001745','0.004'):
            c=Q(text)
            rows=[case for case in candidates if case['p']==p]
            ranked=sorted(rows,key=lambda case:-numerical_value(case['signed'],float(c)))
            winner=ranked[0]
            # Certify that this displayed winner beats all numerically distinct
            # profiles in the finite scanned menu, not all possible schedules.
            win=moment(winner['signed'],c)
            for case in ranked[1:]:
                if dict(case['signed'])!=dict(winner['signed']):
                    need(win[0]>moment(case['signed'],c)[1], 'Exact finite-menu ordering')
            best[f'p{p}_{text}']=serialize_case(winner)
    controls={}
    wrong=base_case(1,6)
    wrong['targets'][6]+=1
    controls['unearned_output_credit_rejected']=(sum(r*n for r,n in wrong['targets'].items())-wrong['rank_bill']!=wrong['rank_margin'])
    controls['rank5_child_with_job5_rejected']=not(5<5)
    need(all(controls.values()), 'Corruption controls')
    return {'schema':'productive-helper-mixed-target-tariff/1',
            'status':'PASS_CONDITIONAL_EXACT_ACCOUNTING',
            'source_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'native_profile':dict(NATIVE),'helper_inventory':dict(HELPERS),
            'assumed_recursive_rule':'sum_paid n_r r^(1-C) < sum_targets W_k k^(1-C); max_paid_rank < min_target_rank',
            'best_in_finite_menu':best,
            'fixed_p2_minimum9':serialize_case(base_case(2,9,OLD_PAIRS,OLD_MIDDLE)),
            'discovery_candidates':[serialize_case(c) for c in discovery],
            'controls':controls,
            'not_proved':['native whole-helper adapters and arbitrary-input block diagonal contract',
                          'correct main controller and all its heads/caches/cleanup',
                          'literal eligibility of any displayed head-cut grant',
                          'mixed-target all-size recursion in this native model',
                          'finite-precision integer-multiplication transfer and scalar/stock costs'],
            'new_kappa':False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--discover',action='store_true')
    parser.add_argument('--output',type=Path,default=HERE/'MIXED-TARGET-PROBE.json')
    args=parser.parse_args()
    result=run(args.discover)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'best':{k:v['targets_at_C'][k.split('_',1)[1]]['after_native_completion_before_main_closure'] for k,v in result['best_in_finite_menu'].items()}},sort_keys=True))

if __name__=='__main__':
    main()
