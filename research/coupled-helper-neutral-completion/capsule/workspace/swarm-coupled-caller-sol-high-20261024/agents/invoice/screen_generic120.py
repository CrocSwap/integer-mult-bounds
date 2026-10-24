#!/usr/bin/env python3
"""Bounded proposed120bank p/split and two-half gauge-price screen.

Reuses only the complete invoice definition in #5405 section1; does not rerun
its ceiling or dynamic program. No actual global/gauge closure is asserted.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import argparse
import json
from exact_moments import moment, minus, encode, need

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
FORMULA=ROOT/'controller5405-successor-package-20261024/research/controller-ceiling-convexity/numerical/inputs/5405-UPSTREAM-EXACT-PROOF.md'
REF=ROOT/'swarm-next-gain-sol-high-20261024/agents/numeric/INVOICE-v2.json'
LOCAL={1:2193,2:412,3:510,4:127,5:40}
HELPERS={4:28,7:7,8:47,9:318}


def scaled(c,n):
    return Counter({r:v*n for r,v in c.items()})


def folded(n):
    return 8*n+n%2


def invoice(p,a):
    need(2<=p<=16 and 0<=a<=p-1,'bounded p/split domain')
    n=p+2
    # FULL endpoints and all odd stages; internal even stages are QUERY.
    mask=[int(s in (0,2*p) or s%2==1)for s in range(2*p+1)]
    need(sum(mask)==n,'p+2 full stages')
    shorts=[]
    for j in range(1,p):
        stages=list(range(0,2*j)) if j<=a else list(range(2*j+1,2*p+1))
        h=sum(mask[s]for s in stages)
        need(mask[2*j]==0,'internal even QUERY specialization')
        shorts.append(h)
    need(sorted(shorts)==sorted(list(range(2,a+2))+list(range(2,p-a+1))),
         'source formula versus length expression')
    lengths=shorts+[n]
    P,T=scaled(LOCAL,n),scaled(HELPERS,n)
    P[1]+=112*(p-1)
    idle,main,auxidle,auxmain=Counter(),Counter(),Counter(),Counter()
    for h in shorts:
        idle[8*h]+=224
        auxidle[folded(h)]+=16
    for h in lengths:
        main[1+8*h]+=224
        auxmain[folded(h)]+=16
    P.update(idle);T.update(main)
    oldP,oldT=P.copy(),T.copy()
    P.update(auxidle);T.update(auxmain)
    P[1]+=8*n;P[9]+=8*n
    even=sum(h%2==0 for h in lengths)
    perhalf=8*(sum(lengths)-len(lengths)+even)
    decode=2*perhalf
    P[1]+=decode
    difference={r:auxmain[r]-auxidle[r] for r in set(auxmain)|set(auxidle)}
    need({r:v for r,v in difference.items()if v}=={folded(n):16},
         'all short auxiliary targets/idles cancel exactly')
    return {'p':p,'a':a,'b':p-1-a,'full_stages':n,'queries':p-1,
            'old_paid':oldP,'old_targets':oldT,'paid':P,'targets':T,
            'short_lengths':shorts,'all_output_lengths_each_half':lengths,
            'length_sum_each_half':sum(lengths),'even_lengths_each_half':even,
            'auxiliary_idle':auxidle,'auxiliary_main':auxmain,
            'local_extension_paid':{1:8*n,9:8*n},
            'conditional_gauge_decode_H1_each_half':perhalf,
            'conditional_gauge_decode_H1_both_halves':decode,
            'additional_F_or_code_cost_H1':None,
            'all_ordinary_global_costs':None,
            'unclosed_idle_code_costs':None,
            'lost_main_or_helper_targets':None,
            'admission':False}


def run():
    raw=FORMULA.read_bytes()
    need(sha256(raw).hexdigest()=='77dc9ce552be7dc9c9a32850c2f2cf0eff92cfe2e0a0e316db210a1667a8d32b',
         'exact #5405 invoice definition changed')
    # Exact source binding: generic p16/a7 must reproduce every old term.
    ref=json.loads(REF.read_bytes());base=invoice(16,7)
    need(all(base[key]==Counter({int(k):v for k,v in ref['histograms'][name].items()})
             for key,name in [('old_paid','paid'),('old_targets','productive')]),
         'generic formula fails literal full p16/a7 invoice')
    need(base['conditional_gauge_decode_H1_both_halves']==1440,
         'p16 both-half decode control')
    kappas=list(map(F,['.00302728823','.0031','.0033','.00339']))
    entries=[]
    for p in range(2,17):
        for a in range(p):
            row=invoice(p,a);checks=[]
            for k in kappas:
                t=1-k
                margin=minus(moment(row['targets'],t),moment(row['paid'],t))
                # Both scenarios remain unconstructed lower-bill assumptions.
                checks.append({'kappa':k,'margin_after_both_half_decode':margin,
                               'extra_F896H1_margin':(margin[0]-896,margin[1]-896),
                               'passes_without_additional_F':margin[0]>0,
                               'passes_with_additional_F896':margin[0]>896,
                               'remaining_unknown_cost_budget_H1_floor':
                                   max(-1,margin[0].numerator//margin[0].denominator)
                                   if margin[0]>0 else None})
            row['checks']=checks;entries.append(row)
    summary=[]
    for j,k in enumerate(kappas):
        best=max(entries,key=lambda r:r['checks'][j]['margin_after_both_half_decode'][0])
        summary.append({'kappa':k,'best_p':best['p'],'best_a':best['a'],
                        'best_margin_after_both_halves':best['checks'][j]['margin_after_both_half_decode'],
                        'best_decode_H1':best['conditional_gauge_decode_H1_both_halves'],
                        'passing_splits_without_additional_F':sum(r['checks'][j]['passes_without_additional_F']for r in entries),
                        'passing_splits_with_additional_F896':sum(r['checks'][j]['passes_with_additional_F896']for r in entries)})
    return {'status':'CONDITIONAL_BOUNDED_NEW120_CONTRACT_AND_DECODE_SCREEN',
            'formula_source':str(FORMULA.relative_to(ROOT)),
            'formula_sha256':sha256(raw).hexdigest(),
            'reference_sha256':sha256(REF.read_bytes()).hexdigest(),
            'number_of_p_split_pairs':len(entries),'p_range':[2,16],
            'source_definition_only':'#5405 section1, no analytic-ceiling rerun or successor',
            'decode_formula_per_half':'8*(sum(output_lengths)-number_of_rows+number_of_even_lengths)',
            'summary':summary,'entries':entries,
            'actual_global_closure':False,'new_kappa':None,'admission':False,
            'premises':['actual120bank global diagonal and two-sided main autonomy',
                        'all shared-centralQ ordered products with absolute phase',
                        'gauge formula transports every actual row, with paid cost shown',
                        'all whole-idle code compatibility and normalization',
                        'all retained400helpers and private9zero returns perlocal'],
            'unknown_never_zero':['additional F transformations','idle code repairs',
                                  'lost main/helper targets','all enlarged ordinary costs',
                                  'fresh global precision/compiler/outer funding']}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();need(not args.output.exists(),'immutable output exists')
    result=run();args.output.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
    print(json.dumps(encode({'status':result['status'],'summary':result['summary'],
                             'new_kappa':None,'admission':False})))
