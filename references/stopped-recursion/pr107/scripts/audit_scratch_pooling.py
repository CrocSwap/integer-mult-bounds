#!/usr/bin/env python3
"""Upper bound for scratch pooling with the original invocation gate labels."""
from fractions import Fraction as Q
from pathlib import Path
import json

from certify import network,require
from search_network import log_integer_bounds,log_ratio_bounds

ROOT=Path(__file__).resolve().parents[1]


def optimistic_counts(h):
    n=network(h)
    A=n['v']**2*(n['v']*n['zb']+h)
    D=n['N']-2*n['Lb']
    W=n['Wb']-A
    require(n['Wb']==2*n['N']+3*A,'Wrong invocation role count')
    require(D<2*W,'Bad merges might improve the ratio')
    return dict(h=h,m=n['m'],A=A,D=D,W=W,eta=Q(D,W*n['m']))


def certificate():
    rows={}
    for h in range(39,200):
        n=optimistic_counts(h)
        lo_num,hi_num=log_ratio_bounds(1/(1-n['eta']),terms=4)
        lo_den,hi_den=log_integer_bounds(n['m'])
        rows[h]=(lo_num/hi_den,hi_num/lo_den)
    winner=max(rows,key=lambda h:rows[h][0]);lo,hi=rows[winner]
    require(winner==46,'Unexpected pooling optimum')
    require(all(u<lo for h,(l,u) in rows.items() if h!=winner),'Unseparated pooling optimum')
    n200=network(200)
    tail=Q(1,2*n200['zb']*n200['m']-1)
    require(tail<lo,'Unexcluded pooling tail')
    upper=hi*hi/(20*(1-hi))
    require(upper<Q(1,2**74),'Pooling can reach a new dyadic witness')
    n=optimistic_counts(46)
    return dict(scope='Pool only auxiliary roles across invocations; keep every scalar gate and rational gate label of the original complete-triple bit family. Current downstream constraints retained.',
                optimal_optimistic_h=46, counts={k:str(v) for k,v in n.items()},
                primitive_saving_lower=str(lo),primitive_saving_upper=str(hi),
                kappa_upper=str(upper),excludes_2_to_minus_74=True,
                tail_h_start=200,tail_saving_upper=str(tail),
                proof='Only stage-1 to stage-3 joins can have zero backward rank penalty. At most A such joins exist. Every other join costs at least one, and strictly worsens the best possible deficit ratio.')


if __name__=='__main__':
    out=certificate()
    (ROOT/'certificates/scratch-pooling-audit.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: pooling unchanged scratch trajectories cannot reach 2^-74, hence cannot reach 2^-67')
