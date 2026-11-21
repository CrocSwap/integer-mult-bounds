#!/usr/bin/env python3
"""Bounded Q=0 event LP, independent of unpublished CALLERCUT/KASYM logs.

Rows are necessary consequences of the event matching and averaged RC2
theorems in pinned PR #7852; see README.md. scipy is used for discovery only.
"""
import argparse
import json
from fractions import Fraction
from decimal import Decimal, localcontext
from pathlib import Path

def power_bounds(base, places=12):
    scale = 10**places
    target = base**99 * scale**100
    with localcontext() as ctx:
        ctx.prec = places + 60
        q = int(Decimal(base) ** (Decimal(99) / 100) * scale)
    while (q+1)**100 <= target: q += 1
    while q**100 > target: q -= 1
    assert q**100 <= target < (q+1)**100
    return Fraction(q, scale), Fraction(q+1, scale)

def data(k, tails=True):
    # Columns r_d (d=2..k), e_a (a=1..k).  Nonnegative.
    cols = [('r', d) for d in range(2,k+1)] + [('e', a) for a in range(1,k+1)]
    eqnames = ['roles','incidence']
    E = [[int(t=='r') for t,d in cols], [d if t=='r' else -d for t,d in cols]]
    eb = [2*k-2,0]
    names = ['mains']
    A = [[-int(t=='e' and d==1) for t,d in cols]]
    b = [-2*k]
    def weight(l,d): return k-1 if l <= d else d-1
    for l in range(2,k+1):
        names.append('rc2_'+str(l))
        A.append([-d*weight(l,d) if t=='r' else (d*weight(l,d) if d>=2 else 0) for t,d in cols])
        b.append(-2*k*(k-1))
    if tails:
        for l in range(2,k+1):
            names.append('match_'+str(l))
            A.append([(-d if t=='r' else d) if d>=l else 0 for t,d in cols])
            b.append(0)
    costs = [power_bounds(8*d+1)[1] if t=='r' else -power_bounds(8*d)[0] for t,d in cols]
    return cols,eqnames,E,eb,names,A,b,costs

def probe(k, tails=True):
    import numpy as np
    from scipy.optimize import linprog
    cols,eqnames,E,eb,names,A,b,c = data(k,tails)
    result = linprog(-np.array([float(x) for x in c]), A_ub=np.array(A,dtype=float), b_ub=np.array(b,dtype=float),
                     A_eq=np.array(E,dtype=float), b_eq=np.array(eb,dtype=float), bounds=(0,None),
                     method='highs', options={'time_limit':30})
    if not result.success: return {'k':k,'success':False,'message':result.message}
    # Convert numerical dual into rationals; every adjustment is verified.
    grid = 10**12
    y=[Fraction(max(0,round(-x*grid)),grid) for x in result.ineqlin.marginals]
    z=[Fraction(round(-x*grid),grid) for x in result.eqlin.marginals]
    def slack(j): return sum(y[i]*A[i][j] for i in range(len(y))) + sum(z[i]*E[i][j] for i in range(2)) - c[j]
    # Decrease incidence equality multiplier until each event column dominates.
    correction = max([Fraction(0)] + [-slack(j)/d for j,(t,d) in enumerate(cols) if t=='e'])
    z[1] -= correction
    # Then increase role-count multiplier to repair every role column.
    correction = max([Fraction(0)] + [-slack(j) for j,(t,d) in enumerate(cols) if t=='r'])
    z[0] += correction
    slackvals=[slack(j) for j in range(len(cols))]
    assert all(v>=0 for v in y) and all(v>=0 for v in slackvals)
    raw = sum(y[i]*b[i] for i in range(len(y))) + sum(z[i]*eb[i] for i in range(2))
    bound = Fraction(104,k)*raw
    rows=[{'name':names[i],'weight':str(v),'rhs':b[i]} for i,v in enumerate(y) if v]
    prim=[{'column':str(cols[i]),'value':x} for i,x in enumerate(result.x) if x>1e-7]
    return {'k':k,'tails':tails,'success':True,'numerical_value':-result.fun*104/k,
            'certified_bound':str(bound),'certified_decimal':float(bound),
            'strictly_below_bar':bound<Fraction(128891,1000),'dual_eq':{eqnames[i]:str(v) for i,v in enumerate(z)},
            'dual_nonzero':rows,'primal_numerical_nonzero':prim,'min_slack':str(min(slackvals)),
            'source':'event relaxation, derived independently; not original certificate'}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('k',type=int,nargs='+')
    parser.add_argument('--no-tails',action='store_true')
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    results=[probe(k,not args.no_tails) for k in args.k]
    text=json.dumps(results,indent=2)+'\n'
    if args.out: args.out.write_text(text)
    else: print(text,end='')
