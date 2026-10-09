#!/usr/bin/env python3
"""Bounded exact rank screens, including full-rank orbit certificates."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from fractions import Fraction as Q
import json

from certify import require,verify_sources
from prepare_layers import serializable
from experiments.single_intersection import (core_parameters,spectral_parity_bound,
    intersecting_minor_bound,check_minor,verify_feature_orbit,free_side_bounds)

ROOT=Path(__file__).resolve().parents[1]


def certificate():
    fixture_path=ROOT/'scripts/experiments/single_intersection_witnesses.json'
    fixtures=json.loads(fixture_path.read_text());minors={};minor_results=[]
    for f in fixtures['minors']:
        key=f['h'],f['k'],f['j']
        checked=check_minor(*key,f['labels'],f['independent_row_indices'])
        require(checked['positive_deficit_excluded'],'Minor fixture does not reject')
        minors[key]=checked['binary_rank_lower']
        minor_results.append(dict(h=key[0],k=key[1],j=key[2],labels=len(f['labels']),**checked))
    orbits=[]
    for f in fixtures['feature_orbits']:
        out=verify_feature_orbit(f['h'],f['k'],f['j'],f['labels'])
        out['hypothetical_free_side']=free_side_bounds(f['h'],f['k'],f['j'],out['exact_full_binary_rank'])
        orbits.append(out)
    tally=Counter();rows=[];best={}
    for h in range(4,65):
        for k in range(2,min(15,h//2)+1):
            for j in range(k):
                p=core_parameters(h,k,j);ident=intersecting_minor_bound(h,k,j)
                spec=spectral_parity_bound(h,k,j)
                lb=max(ident['binary_rank_lower'],spec['binary_rank_lower'],minors.get((h,k,j),0))
                require(lb<=p['binary_factor_upper'],'Inconsistent rank bounds')
                if ident['positive_deficit_excluded']:status='identity_minor_exclusion'
                elif spec['positive_deficit_excluded']:status='spectral_parity_exclusion'
                elif p['positive_with_supplied_factor']:status='positive_supplied_factor'
                elif 6*lb*p['d']>=p['n']:status='explicit_minor_exclusion'
                else:status='unresolved'
                tally[status]+=1
                rows.append(dict(h=h,k=k,j=j,n=p['n'],d=p['d'],rank_upper=p['binary_factor_upper'],
                                 rank_lower=lb,status=status))
                if p['positive_with_supplied_factor']:
                    bounds=free_side_bounds(h,k,j,p['binary_factor_upper'])
                    key=k,j
                    if key not in best or bounds['lower']>best[key]['hypothetical_free_side']['lower']:
                        best[key]=dict(h=h,k=k,j=j,rank_upper=p['binary_factor_upper'],hypothetical_free_side=bounds)
    require(len(rows)==5257,'Search domain changed')
    ranking=sorted(best.values(),key=lambda b:b['hypothetical_free_side']['lower'],reverse=True)
    require((ranking[0]['h'],ranking[0]['k'],ranking[0]['j'])==(28,7,3),'Unexpected benchmark winner')
    sources=('scripts/audit_single_intersection.py','scripts/experiments/single_intersection.py',
             'scripts/experiments/single_intersection_witnesses.json','docs/research/single-intersection.md')
    return dict(status='BOUNDED TWO-FIELD RANK SCREEN; NO COMPETITIVE SIDE CIRCUIT OR NEW KAPPA',
                upstream_commit=verify_sources(),retained_kappa=Q(1,2**31),
                domain=dict(h=[4,64],k='2 through min(15,floor(h/2))',j='0 through k-1',cases=len(rows)),
                classifications=dict(tally),rows=rows,explicit_minor_certificates=minor_results,
                exact_feature_orbit_certificates=orbits,best_supplied_factor_benchmarks=ranking,
                scope='Full-support matrices C=I+A_j only. Exclusions need not hold for other supported binary matrices; unresolved cases remain. Free-side savings are not constructions.',
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/single-intersection.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS single-intersection screens:',result['classifications'])
    print('No stronger multiplication bound; unresolved cases are explicitly retained.')
