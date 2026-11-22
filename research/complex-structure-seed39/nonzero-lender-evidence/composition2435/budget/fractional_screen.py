#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Nominate and exactly check conditional fractional whole-helper capacity.

This deliberately omits owner chronology and family exclusion. No construction
or kappa claim. Tekalign (@tekuuu), substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
import argparse
import importlib.util
import json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from sympy import Matrix, Rational
import price_composition as p

CAP=(8,16,32,48,73)
WIDTHS=(4,5,7,8,9)
STOCK=(49728,33152,33152,33152)

def patterns(cap,j=0,pat=()):
    if j==len(WIDTHS):
        yield pat
    else:
        for n in range(cap//WIDTHS[j]+1):
            yield from patterns(cap-n*WIDTHS[j],j+1,pat+(n,))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path);args=ap.parse_args()
    raw=p.read(p.HERE/'CONDITIONAL-LITERAL.json')
    widths=p.integer_counter(raw['conditional_width_inventories']['extra'])
    rhs=STOCK+tuple(666*widths[w] for w in WIDTHS)
    vs=[(cap,pat) for cap in CAP for pat in patterns(cap) if cap!=73 or any(pat)]
    p.need(len(vs)==5927,'pattern coverage')
    A=np.zeros((9,len(vs)),dtype=int)
    spec=importlib.util.spec_from_file_location('fractional_moment',p.ENGINE)
    engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
    b=p.COMPARISON
    E={r:r*(float(73/r)**float(b)-1) for r in range(1,52)}
    pad=[(0,[])]
    for cap in range(1,74):
        pad.append(min((pad[cap-r][0]+E[r],pad[cap-r][1]+[r]) for r in range(1,min(cap,51)+1)))
    costs=[]
    for j,(cap,pat) in enumerate(vs):
        if cap!=73:A[CAP.index(cap),j]=1
        A[4:,j]=pat
        costs.append(pad[cap-sum(w*n for w,n in zip(WIDTHS,pat))][0])
    sol=linprog(costs,A_eq=A,b_eq=rhs,bounds=(0,None),method='highs')
    p.need(sol.success,'fractional LP failed')
    chosen=[j for j,x in enumerate(sol.x) if x>1e-6]
    exact=Matrix(A[:,chosen].tolist()).gauss_jordan_solve(Matrix(rhs))[0]
    vals=[Q(int(x.p),int(x.q)) for x in exact]
    p.need(all(x>0 for x in vals),'nonpositive exact support')
    p.need([sum(int(A[i,j])*x for j,x in zip(chosen,vals)) for i in range(9)]==list(rhs),'exact capacity equalities')
    idle=Counter();banks=Q(0);witness=[]
    for j,x in zip(chosen,vals):
        cap,pat=vs[j];res=cap-sum(w*n for w,n in zip(WIDTHS,pat));parts=pad[res][1]
        p.need(sum(parts)==res and all(1<=r<=51 for r in parts),'padding coverage')
        if cap==73:banks+=x
        idle.update({r:n*x for r,n in Counter(parts).items()})
        witness.append(dict(capacity=cap,pattern=list(pat),copies=str(x),padding=parts))
    H=Counter(idle)
    for tag,n in (('gauge44',249),('extra',417)):
        H.update({r:n*c for r,c in p.integer_counter(raw['conditional_local_profiles'][tag]).items()})
    live=Q(66304)+banks
    p.need(73*live-sum(r*n for r,n in H.items())==23680,'rank deficit')
    # Integer rescaling leaves the exact moment unchanged and permits the
    # Decimal nomination used by the inherited certifier.
    import math
    denominator=math.lcm(live.denominator,*(n.denominator for n in H.values()))
    Hi={r:int(n*denominator) for r,n in H.items()};Wi=int(live*denominator)
    bracket=engine.certify(Hi,73,Wi,bad=True)
    lo,hi=engine.moment(Hi,73,Wi,b,bad=True)
    receipt=dict(status='PASS_EXACT_CONDITIONAL_FRACTIONAL_PRIMAL_NO_OWNER_OR_CONSTRUCTION_CLAIM',
        rate=str(b),patterns=len(vs),widths=dict(widths),stock=STOCK,demand=rhs[4:],
        witness=witness,banks=str(banks),live=str(live),idle={r:str(n) for r,n in sorted(idle.items())},
        global_profile={r:str(n) for r,n in sorted(H.items())},deficit=23680,
        root_lower=bracket['lower'],root_upper=bracket['upper'],
        moment_minus_one_at_comparison=[engine.decimal(lo-1),engine.decimal(hi-1)],
        pass_comparison=hi<1,float_dual=list(sol.eqlin.marginals),
        assumption=raw['assumption'],physical_obligation=raw['physical_obligation'],
        scope='Exactly feasible fractional capacity/priced residual witness for the conditional profile only. Global temporal windows, physical family exclusion, actual copy/frame composition and modern outer admission remain unresolved. Floating optimization only nominates support; stock/demand/padding/deficit and moment signs checked exactly. No kappa claim.')
    if args.out:args.out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status']);print(json.dumps({k:receipt[k] for k in ('banks','root_lower','root_upper','pass_comparison','moment_minus_one_at_comparison')},indent=2))

if __name__=='__main__':main()
