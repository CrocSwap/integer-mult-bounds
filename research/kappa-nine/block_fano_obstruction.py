"""Construction experiment 1: rank-two labels at the Fano saturation dimension.

Exact rejection for dimension 7*l on the full intersection-one triple graph
on at least nine points. General rational idempotents are allowed. No common
form, symmetry, point-additive ansatz or simultaneous diagonalization assumed.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, permutations
from pathlib import Path
import argparse
import hashlib
import json
from target_budget import encode, moment, require


def fano_planes():
    canonical=sorted({tuple(sorted((a-1,b-1,(a^b)-1))) for a in range(1,8) for b in range(a+1,8) if a^b})
    require(len(canonical)==7,'seven Fano lines')
    planes=sorted({tuple(sorted(tuple(sorted(p[i] for i in line)) for line in canonical)) for p in permutations(range(7))})
    require(len(planes)==30,'labeled Fano planes')
    return planes


def clique_incidence(points=9):
    triples=list(combinations(range(points),3));index={t:i for i,t in enumerate(triples)}
    rows=[];metadata=[]
    for seven in combinations(range(points),7):
        for plane in fano_planes():
            lines=[tuple(seven[i] for i in line) for line in plane]
            require(len({x for line in lines for x in line})==7,'point coverage')
            require(all(len(set(a)&set(b))==1 for a,b in combinations(lines,2)),'clique')
            rows.append([int(t in lines) for t in triples]);metadata.append(lines)
    return triples,rows,metadata


def rank_witness(rows,prime=101):
    basis={};selected=[];pivots=[]
    for i,row in enumerate(rows):
        x=[v%prime for v in row]
        for col,b in sorted(basis.items()):
            value=x[col]
            if value:x=[(v-value*w)%prime for v,w in zip(x,b)]
        col=next((j for j,v in enumerate(x) if v),None)
        if col is not None:
            pivot=x[col];inv=pow(pivot,-1,prime)
            basis[col]=[(v*inv)%prime for v in x]
            selected.append(i);pivots.append(pivot)
        if len(basis)==len(row):break
    return selected,pivots


def determinant_mod(matrix,prime):
    """Independent dense square-matrix replay, including row swaps."""
    A=[row.copy() for row in matrix];n=len(A);det=1
    require(all(len(row)==n for row in A),'square determinant')
    for c in range(n):
        pivot=next((i for i in range(c,n) if A[i][c]%prime),None)
        if pivot is None:return 0
        if pivot!=c:A[pivot],A[c]=A[c],A[pivot];det=-det
        value=A[c][c]%prime;det=det*value%prime;inv=pow(value,-1,prime)
        for i in range(c+1,n):
            scale=A[i][c]*inv%prime
            for j in range(c,n):A[i][j]=(A[i][j]-scale*A[c][j])%prime
    return det%prime


def rank_two_budget(d=14,role_ratio=Q(5)):
    """Optimistic transferred rank-l ledger, NOT an established block transfer.

    h=16 triple labels, r=16 central factors, l=2. Charge the proposed endpoint,
    data/growth, center loss and both auxiliary boundaries; grant full batching.
    """
    ell,n,r=2,560,16;m=d*d;W=2+2*role_ratio
    rows=Counter({(d-ell)**2:Q(2),ell*ell:Q(1)})
    rows[ell*(d-ell)]+=4
    rows[d*ell]+=2*role_ratio+Q(2*r*ell*(d-ell),n*d*ell)
    rows[m-d*ell]+=2*role_ratio
    return dict(ambient_dimension=d,label_rank=ell,triple_ground_size=16,
                roles_per_label=role_ratio,moment_interval=moment(rows,m,W),
                status='Optimistic block ledger only. Neither label geometry nor physical transfer supplied.')


def audit():
    triples,rows,metadata=clique_incidence()
    selected,pivots=rank_witness(rows)
    require(len(selected)==84,'Fano incidence not full column rank')
    chosen=[rows[i] for i in selected];det=determinant_mod(chosen,101)
    require(det!=0,'independent determinant replay')
    require(all(sum(row)==7 for row in chosen),'constant solution')
    # The constant matrix family P_T=I/7 solves every clique-sum equation.
    # Full column rank makes it unique entry by entry. It is not idempotent:
    residual=Q(1,7)**2-Q(1,7)
    require(residual!=0,'idempotent contradiction')
    # Rank-one control on nine points: F_ST=(|S cap T|-1)/2 has rank eight.
    # Factor through w_S=(1_S-1/3*1), sum w_S=0, a rational 8-space.
    F=[[Q(len(set(s)&set(t))-1,2) for t in triples] for s in triples]
    residues=[[int(x.numerator*pow(x.denominator,-1,101)%101) for x in row] for row in F]
    low,_=rank_witness(residues)
    require(len(low)==8,'rank-eight control')
    for s,t,row in ((s,t,F[i][j]) for i,s in enumerate(triples) for j,t in enumerate(triples)):
        ws=[Q(int(x in s))-Q(1,3) for x in range(8)]
        wt=[Q(int(x in t))-Q(1,3) for x in range(8)]
        require((sum(x*y for x,y in zip(ws,wt))+sum(ws)*sum(wt))/2==row,'rational factor control')
    budgets=[rank_two_budget(d,R) for d in (14,15,16) for R in (Q(1),Q(3),Q(5))]
    require(rank_two_budget()['moment_interval'][1]<1,'candidate lacked optimistic headroom')
    return dict(status='EXACT NEGATIVE CONSTRUCTION EXPERIMENT; NO NEW KAPPA',
                changed_assumption='Rank-two rational labels instead of rank-one triple lines; arbitrary noncommuting rational idempotents permitted.',
                scope='Full intersection-one triple graph on h>=9; rank-l idempotents in dimension 7*l, for any positive integer l.',
                selected_target='h=16, l=2, d=14; favorable optimistic moment but impossible labels',
                rows_available=len(rows),columns=len(triples),field_prime=101,
                selected_cliques=[metadata[i] for i in selected],selected_row_indices=selected,
                determinant_mod_prime=det,idempotent_residual=residual,
                matrix_sha256=hashlib.sha256(bytes(v for row in chosen for v in row)).hexdigest(),
                proof=['Seven mutually annihilating rank-l idempotents in dimension 7*l sum to I: their image spaces form a direct sum filling the space.',
                       'Apply this to each Fano clique on any fixed nine ground points.',
                       'The 84 selected clique-incidence rows have a nonzero determinant modulo 101, hence are invertible over Q.',
                       'Each matrix entry therefore has the unique solution P_T=I/7 on all 84 triples.',
                       'But (I/7)^2-I/7=(-6/49)I is nonzero. Contradiction.',
                       'Restriction to nine points extends the exclusion to every h>=9.'],
                controls={'rank_one_dimension_eight_fitting_matrix':True,'rank_two_dimension_sixteen_control_on_nine_points':'Direct sum of two rank-eight factors; this is only a geometry control, not a full network.'},
                optimistic_budget_table=budgets,
                continuation='Stop d=14. Dimensions 15 and higher, or a different graph, are not excluded. A target-capable block network still requires a side circuit, copied transfer and complex companion.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=audit()
    if args.output:args.output.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
    print('PASS 84-by-84 exact Fano clique rank certificate; rank-l dimension 7*l excluded for h>=9')
