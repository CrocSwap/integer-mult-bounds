"""Conditional exact repricing on freshly reproduced PR305 arithmetic.

The caller supplies measured or explicitly provisional histogram and role-width
deltas. No baseline physical admission or candidate admission is asserted.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import json
import reproduce_pr305 as base

def price(histogram_delta,residual_delta,pivot_delta=None,label='provisional'):
    base.verify_sources()
    H,profile=base.final_profile();inv=base.inventory()
    H.update({r:5*n for r,n in histogram_delta.items()})
    assert min(H.values())>=0
    H=Counter(base.clean(H))
    families=Counter(inv['residual_census']);families.update(residual_delta)
    assert min(families.values())>=0
    families=Counter(base.clean(families))
    pivots=Counter(inv['pivot_residual_census']);pivots.update(pivot_delta or {})
    patterns=[dict(widths=[7]*12+[4]*9,count=10)]
    for width,count in sorted(pivots.items()):
        patterns.append(dict(widths=[width]*4+[24]+[4]*(24-width),count=15*count))
    supplied=Counter()
    for row in patterns:
        assert sum(row['widths'])==120
        supplied.update({r:n*row['count'] for r,n in Counter(row['widths']).items()})
    for width in (3,4,6,24):
        remainder=60*families[width]-supplied[width]
        assert remainder>=0 and 120%width==0 and remainder%(120//width)==0
        if remainder:patterns.append(dict(widths=[width]*(120//width),count=remainder//(120//width)))
    supplied=Counter()
    for row in patterns:
        supplied.update({r:n*row['count'] for r,n in Counter(row['widths']).items()})
    assert supplied==Counter({r:60*n for r,n in families.items()})
    banks=sum(row['count'] for row in patterns)
    assert 120*banks==60*base.mass(families)
    stock=422400+5*banks;W=F(stock,60);deficit=120*W-base.mass(H)
    assert deficit==4400
    root=base.bracket(H,120,W);assembly=base.assembly(root['lower'])
    baseline_kappa=F(base.read('expected/kernel-pins.json')['kappa'])
    return dict(status='CONDITIONAL_CANDIDATE_PROFILE_ARITHMETIC',label=label,
        physical_admission=False,all_size_theorem=False,
        local_histogram_delta=histogram_delta,residual_role_delta=residual_delta,
        final_histogram=base.clean(H),calls=sum(H.values()),rank_mass=base.mass(H),
        residual_census=base.clean(families),physical_R=sum(families.values()),
        banks_per_stage=banks,total_banks=5*banks,literal_stock=stock,
        packing_patterns=patterns,packing_unused_coordinates=0,
        unreplicated_stock=W,deficit=deficit,bit_root_bracket=root,assembly=assembly,
        kappa_improvement_over_pr305=assembly['kappa']-baseline_kappa,
        improvement_percent=100*(assembly['kappa']/baseline_kappa-1),
        scope='Repriced declared profile only. Supplied deltas require independent exact changed-stage/chronology, geometry, scalar-cost and finite-invoice validation before admission.')

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    result=price({1:87,2:137,3:-137,4:18,5:-16,6:-2},{24:-70,23:70},{23:70},
        label='PROVISIONAL direct70; two newly reused donor aliases awaiting chronological verification; no final12 delta')
    path=Path(__file__).with_name('direct70-provisional-receipt.json')
    path.write_text(json.dumps(base.ae.serial(result),indent=2)+'\n')
    print(json.dumps(base.ae.serial(dict(kappa=result['assembly']['kappa'],
        kappa_decimal=result['assembly']['kappa_decimal'],calls=result['calls'],rank_mass=result['rank_mass'],
        stock=result['literal_stock'],improvement_percent=base.ex.dec(result['improvement_percent']),
        bit_root_bracket=[result['bit_root_bracket'][key] for key in ('lower','upper')],
        physical_admission=False)),indent=2))
