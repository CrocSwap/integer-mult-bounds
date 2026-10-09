#!/usr/bin/env python3
"""First overnight family screen; no stronger multiplication witness."""
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import json

from certify import Parameters, constraints, margins, require, verify_sources
from experiments.subset_core_family import specification, ledger, side_budget, rectangle_ledger, rational_companion, complex_count_screen
from prepare_layers import serializable

ROOT=Path(__file__).resolve().parents[1]
TARGET=Q(1,2**25)
INTERFACE_TARGET=Q(16,10**8)


def hypothetical_assembly(ab,ac,kappa=TARGET):
    """Parameter check conditioned on both finite interfaces, not their proof.

    This does not check a new complex network's scalar charge, guard constant,
    residual kernel hypotheses, or either transfer theorem.
    """
    require(all(isinstance(x,Q) and 0<x<1 for x in (ab,ac,kappa)),
            'Use exact positive rational savings and kappa below one')
    beta=Q(1,100);zeta=Q(1,1000);epsilon=Q(199,1000)
    bottleneck=min(ab,(1-beta)*ac)
    p=Parameters(1-ab,1-ac,epsilon,Q(1),1-Q(199,200)*bottleneck,
                 1-Q(99,100)*bottleneck,kappa,beta=beta,
                 delta=Q(1,10000),C1=5-4*beta+zeta)
    chi=p.tau+(1-beta)*max(p.sigma-p.tau,0)
    cs=constraints(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    cs['packed_overhead']=p.lam-chi
    cs['reserved_axes']=p.lamp-max(0,1-p.c)
    gs=margins(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    return dict(parameters=vars(p),constraint_slacks=cs,margins=gs,
                minimum_margin=min(gs.values()),
                parameter_system_passes=all(x>0 for x in cs.values()) and min(gs.values())>kappa,
                finite_networks_verified=False,new_guard_verified=False,
                status='HYPOTHETICAL INTERFACE TARGET ONLY; NOT A MULTIPLICATION WITNESS')


def family_screen(q,maximum_h=96):
    rows=[]
    for h in range(2*q,maximum_h+1):
        if (q-1)*h==(2*q-1)**2:continue
        raw=ledger(h,q)
        if not raw['positive']:continue
        # This free-side count is only a benchmark, not a constructed network.
        free=ledger(h,q,0)
        rows.append(dict(h=h,n=raw['n'],central_factor_size=raw['central_factor_size'],
                         rational_dimension=h,deficit_fraction=Q(raw['deficit'],raw['N']),
                         raw=raw,free_side_benchmark=free))
    best=max(rows,key=lambda r:r['free_side_benchmark']['saving_lower']) if rows else None
    return dict(q=q,k=2*q-1,j=q-1,maximum_h=maximum_h,
                first_positive_h=rows[0]['h'] if rows else None,
                best_free_side_benchmark_h=best['h'] if best else None,
                best_free_side_benchmark=best['free_side_benchmark'] if best else None,
                rows=rows,
                scope='Finite h screen with explicit incidence factors; no optimality over arbitrary cores or side circuits.')


def certificate():
    assembly=hypothetical_assembly(INTERFACE_TARGET,INTERFACE_TARGET)
    require(assembly['parameter_system_passes'],'Interface target does not support assembly')
    complex_block=hypothetical_assembly(INTERFACE_TARGET,Q(5,10**9))
    require(not complex_block['parameter_system_passes'],'Retained complex network unexpectedly suffices')
    screens=[family_screen(q) for q in (2,4,8,16)]
    seven=[]
    for h in range(23,41):
        spec=specification(h,4);base=rectangle_ledger(h,4)
        seven.append(dict(h=h,specification=spec,rectangle_baseline=base,
                          target_budget=side_budget(h,4,INTERFACE_TARGET),
                          necessary_budget=side_budget(h,4,5*TARGET),
                          independent_materialized_input_roles=comb(h,3)*comb(h-3,4),
                          independent_input_ratio=Q(comb(h,3)*comb(h-3,4),spec['n'])))
        require(seven[-1]['independent_input_ratio']==35,'Fixed-intersection input count failed')
    best=max(seven,key=lambda r:r['rectangle_baseline']['saving_lower'])
    require(best['rectangle_baseline']['saving_upper']<Q(296,10**11),
            'Baseline unexpectedly improves retained bit saving; audit before claim')
    sources=('scripts/audit_subset_cores.py','scripts/experiments/subset_core_family.py',
             'scripts/experiments/rank_product_core.py','scripts/incidence_rectangles.py',
             'docs/research/subset-core-family.md')
    return dict(status='NEW GENERATIVE CORE FAMILY; SIDE COST REMAINS TOO LARGE; NO NEW KAPPA',
                upstream_commit=verify_sources(),target_kappa=TARGET,
                retained_kappa=Q(1,2**31),interface_target=INTERFACE_TARGET,
                hypothetical_assembly=assembly,retained_complex_rejection=complex_block,
                family_screens=screens,seven_subset_side_screens=seven,
                best_rectangle_baseline=best,
                rational_companion=rational_companion(4),
                complex_count_screens=[dict(h=h,raw=complex_count_screen(h,4),
                    free_side_benchmark=complex_count_screen(h,4,0)) for h in range(22,41,2)],
                scope='Raw networks follow the proved factored compiler. Rectangle figures are count screens, not a complete new frame certificate. Free-side figures and interface targets are explicitly hypothetical.',
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/subset-core-family.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    best=result['best_rectangle_baseline']
    print('PASS subset-core ledger and hypothetical interface target; no stronger kappa.')
    print('Best screened seven-subset rectangle count:',best['h'],float(best['rectangle_baseline']['saving_lower']))
