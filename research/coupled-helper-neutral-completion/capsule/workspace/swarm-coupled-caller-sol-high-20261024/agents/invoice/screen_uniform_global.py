#!/usr/bin/env python3
"""Distinct uniform120 global budget: mandatory coarse middle query and boundaries.

Does not rerun the other chat's bare uniform p5 two-point screen. All global
closure, inverse-child normalization and source compiler applications remain
unproved. No submitted provider/inverse/pricing evaluator is imported.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import argparse,json
from exact_moments import moment,minus,homogeneous_limit,encode,need
from screen_generic120 import invoice as previous_invoice,LOCAL,HELPERS,scaled

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
INVERSE_MANIFEST=HERE.parent/'source/RUNTIME-MANIFEST.json'
HEAD='123ffa6aa7c1866ac60c67739841f71d95b3edf7'


def invoice(p,a,boundary_H1):
    need(3<=p<=16 and 0<=a<p,'bounded p/split domain')
    need(boundary_H1 in (0,120,240,480),'named boundary scenario')
    old=previous_invoice(p,a);n=p+2;lengths=old['all_output_lengths_each_half']
    P,T=scaled(LOCAL,n),scaled(HELPERS,n)
    # Uniform local extension is24H1+8H9, not the nonuniform8H1+8H9.
    P[1]+=24*n;P[9]+=8*n
    # Uniform query is120 ports; every retained whole idle has240 owners.
    P[1]+=120*(p-1)
    idles=Counter();main=Counter()
    for h in old['short_lengths']:idles[8*h]+=240
    for h in lengths:main[1+8*h]+=240
    P.update(idles);T.update(main)
    # Mandatory new global seam price distinguishes this campaign from the
    # bare uniform screen owned elsewhere. Boundaries are additional.
    P[1]+=120+boundary_H1
    return {'p':p,'a':a,'b':p-1-a,'full_stages':n,
            'paid':P,'targets':T,'uniform_query_count':p-1,
            'uniform_query_H1_each':120,'whole_idle':idles,'main':main,
            'main_bank_width':120,'local_extension_paid':{1:24*n,9:8*n},
            'mandatory_extra_middle_H1':120,
            'named_additional_boundary_H1':boundary_H1,
            'ordinary_global_code_and_boundaries':None,
            'lost_helpers_or_main':None,'actual_global_closure':False,
            'source_inverse_positive_helper_normalizers_admitted':False}


def run():
    kappas=list(map(F,['.00302728823','.0031','.0033']))
    rows=[]
    for p in range(3,17):
        for a in range(p):
            # Store one common target and each complete changed paid scenario.
            variants=[]
            for boundary in (0,120,240,480):
                inv=invoice(p,a,boundary);P,T=inv['paid'],inv['targets'];checks=[]
                for k in kappas:
                    t=1-k;margin=minus(moment(T,t),moment(P,t))
                    checks.append({'kappa':k,'raw_margin':margin,
                                   'strict_raw_pass':margin[0]>0,
                                   'additional_H1_budget_floor':
                                       max(0,margin[0].numerator//margin[0].denominator)
                                       if margin[0]>0 else None})
                variants.append({'boundary_H1':boundary,'paid':P,
                                 'paid_count':sum(P.values()),
                                 'paid_rank_mass':sum(r*c for r,c in P.items()),
                                 'checks':checks})
            row=invoice(p,a,0)
            row.update(variants=variants,target_count=sum(row['targets'].values()),
                       target_rank_mass=sum(r*c for r,c in row['targets'].items()))
            row.pop('paid');rows.append(row)
    summaries=[]
    for j,k in enumerate(kappas):
        for i,boundary in enumerate((0,120,240,480)):
            best=max(rows,key=lambda row:row['variants'][i]['checks'][j]['raw_margin'][0])
            check=best['variants'][i]['checks'][j];margin=check['raw_margin']
            budget={}
            if margin[0]>0:
                budget={rank:homogeneous_limit(margin,rank,1-k)
                        for rank in (1,8,9,16,32,64,145)}
            summaries.append({'kappa':k,'additional_boundary_H1':boundary,
                              'best_p':best['p'],'best_a':best['a'],
                              'best_margin':margin,
                              'passing_p_split_count':sum(
                                  row['variants'][i]['checks'][j]['strict_raw_pass']for row in rows),
                              'additional_paid_or_lost_target_budget':budget})
    # Rank-mass accounting is a separate source/term-count sanity check.
    c=invoice(16,7,0)
    need(sum(r*n for r,n in c['targets'].items())-sum(r*n for r,n in c['paid'].items())==1344,
         'p16 full uniform plus mandatory query rank surplus')
    manifests=[]
    if INVERSE_MANIFEST.exists():
        manifests.append({'path':str(INVERSE_MANIFEST.relative_to(ROOT)),
                          'sha256':sha256(INVERSE_MANIFEST.read_bytes()).hexdigest(),
                          'scope':'Static source custody only; no inverse scientific replay or normalizer admission'})
    return {'status':'CONDITIONAL_UNIFORM120_GLOBAL_SEAM_AND_BOUNDARY_BUDGET',
            'inverse5411_exact_head':HEAD,'source_bindings':manifests,
            'p_range':[3,16],'p_split_cases':len(rows),
            'kappas':kappas,'mandatory_extra_middle_H1':120,
            'additional_boundary_H1_scenarios':[0,120,240,480],
            'local_extension_paid_each':{1:24,9:8},
            'local_helpers_each':HELPERS,'queries':{'ports':120},
            'main_idle_multiplicity':240,'rank_rule':'IDLE8h; main1+8h, including full p+2 path',
            'summary':summaries,'rows':rows,
            'no_bare_uniform_two_point_screen':True,
            'actual_global_closure':False,
            'source_inverse_positive_helper_normalizers_admitted':False,
            'ordinary_costs':None,'fresh_precision':None,'full_compiler_outer_endpoint':None,
            'new_kappa':None,'admission':False,
            'unknowns':['actual middle and boundary endpoint','all inverse positive-child normalizers',
                        'all lost main/helper targets','complete owned returns and scratch lifetimes',
                        'complete ordinary/machine/precision work','source-applicable compiler and outer funding']}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();need(not args.output.exists(),'immutable receipt exists')
    result=run();args.output.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
    print(json.dumps(encode({'status':result['status'],'summary':result['summary'],
                             'new_kappa':None,'admission':False})))
