"""Exact screen for S8-covariant labels on k*standard_7 + r*trivial.

This includes two standard copies sharing one scalar coordinate (dimension
15). It does NOT classify every S8 representation or arbitrary labels.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json
from covariant_block_test import pieces, mul, rank


def modular_rank_sparse(rows, prime=101):
    basis={}
    for row in rows:
        row={i:x%prime for i,x in row.items() if x%prime}
        while row:
            pivot=min(row)
            if pivot not in basis:
                inv=pow(row[pivot],-1,prime)
                basis[pivot]={i:x*inv%prime for i,x in row.items()}
                break
            scale=row[pivot]
            for i,x in basis[pivot].items():
                value=(row.get(i,0)-scale*x)%prime
                if value:row[i]=value
                else:row.pop(i,None)
    return len(basis)


def stabilizer_centralizer_rank(k=2,r=1):
    """Integer commutation equations in the e_i-e_7 standard basis."""
    n=7*k+r;rows=[]
    for u,v in [(0,1),(1,2),(3,4),(4,5),(5,6),(6,7)]:
        p=list(range(8));p[u],p[v]=p[v],p[u]
        g=[[0]*n for _ in range(n)]
        for copy in range(k):
            for i in range(7):
                for j in range(7):g[7*copy+i][7*copy+j]=int(p[j]==i)-int(p[7]==i)
        for i in range(7*k,n):g[i][i]=1
        for i in range(n):
            for j in range(n):
                row={}
                for l in range(n):
                    row[l*n+j]=row.get(l*n+j,0)+g[i][l]
                    row[i*n+l]=row.get(i*n+l,0)-g[l][j]
                rows.append(row)
    return n*n-modular_rank_sparse(rows)


def audit():
    h=8;t={0,1,2};u={0,3,4}
    wt=[Q(int(i in t))-Q(3,8) for i in range(8)]
    wu=[Q(int(i in u))-Q(3,8) for i in range(8)]
    norm=sum(x*x for x in wt);cross=sum(x*y for x,y in zip(wt,wu));c=cross/norm
    assert (norm,cross,c)==(Q(15,8),Q(-1,8),Q(-1,15))
    a=pieces(8,tuple(t))[0];b=pieces(8,tuple(u))[0]
    assert rank(mul(a,b))==1
    assert stabilizer_centralizer_rank()==17
    # Sharp control for this representation family: a second trivial line
    # allows two copies of the usual dimension-eight geometry on eight points.
    alpha=Q(15,16);beta=Q(1,16)
    rr=[[alpha,0,beta,0],[0,alpha,0,beta],
        [alpha,0,beta,0],[0,alpha,0,beta]]
    dd=[[0]*4 for _ in range(4)]
    for i in range(4):dd[i][i]=c if i<2 else 1
    assert mul(rr,rr)==rr and rank(rr)==2
    assert mul(mul(rr,dd),rr)==[[0]*4 for _ in range(4)]
    # Stabilizer decomposition: 2-dimensional inside standard (multiplicity k),
    # 4-dimensional outside standard (multiplicity k), trivial (multiplicity k+r).
    # Its exhibited block endomorphisms give 2*k^2+(k+r)^2 independent maps.
    dims=[]
    for k,r in [(1,0),(1,1),(1,8),(2,0),(2,1)]:
        measured=stabilizer_centralizer_rank(k,r);expected=2*k*k+(k+r)**2
        assert measured==expected
        dims.append({'standard_copies':k,'trivial_copies':r,'commutant_dimension':measured})
    return {'status':'EXACT SCOPED EXCLUSION; NO NEW KAPPA',
            'scope':'S8-covariant rank-two idempotents for all triples of eight points in k copies of the standard 7-space plus r trivial lines, with 7*k+r<=15. No common symmetric form for the idempotents assumed.',
            'not_excluded':'Other S8 representations; nonsymmetric covariance actions outside this family; all noncovariant dimension-15 representations on nine points.',
            'normalized_cross_line_pairing':str(c),'inside_standard_cross_rank':1,
            'commutant_dimension_checks':dims,'shared_scalar_cross_determinant':str(c*c),
            'dimension_16_trivial_block_control':[[str(x) for x in row] for row in rr],
            'proof':['The stabilizer S3 x S5 splits each standard 7-space into dimensions 2,4,1. The commutant is Mat_k + Mat_k + Mat_(k+r).',
                     'A rank-two idempotent either occupies one multiplicity direction in the inside 2-space, or lies entirely in the trivial isotypic block; the outside 4-space cannot occur.',
                     'The inside case fails: its adjacent product is (A_T A_U) tensor E^2, nonzero since E is a rank-one idempotent and A_T A_U has rank one.',
                     'In the trivial block, adjacency forces R D R=0, where R^2=R, rank R=2 and D=diag(c I_k,I_r), c=-1/15.',
                     'If k<=1, RDR=R+(c-1)R E R=0 would imply rank R<=k, a contradiction.',
                     'If k=2, the dimension limit gives r<=1. D is invertible, so rank(DR)=2 while RDR=0 puts its image in ker R of dimension at most one. Contradiction.']}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=audit();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])
