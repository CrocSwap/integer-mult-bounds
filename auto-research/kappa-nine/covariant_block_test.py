"""Construction experiment 2: covariant rank-two triple labels.

Investigate dimensions h-1 and h under their standard/natural permutation
actions. This changes label rank and does not assume point-additive frames.
It does retain vertex-permutation covariance, which the rejection makes explicit.
"""
from fractions import Fraction as Q
from itertools import combinations, permutations, product
from pathlib import Path
import argparse
import json
from target_budget import encode, require
from block_fano_obstruction import rank_two_budget


def mul(A,B):
    return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]


def add(A,B):return [[a+b for a,b in zip(x,y)] for x,y in zip(A,B)]
def scale(c,A):return [[c*x for x in row] for row in A]
def eye(h):return [[Q(i==j) for j in range(h)] for i in range(h)]
def zero(h):return [[Q(0) for _ in range(h)] for _ in range(h)]


def rank(A):
    A=[list(map(Q,row)) for row in A];r=0
    for col in range(len(A[0])):
        pivot=next((i for i in range(r,len(A)) if A[i][col]),None)
        if pivot is None:continue
        A[r],A[pivot]=A[pivot],A[r];v=A[r][col];A[r]=[x/v for x in A[r]]
        for i in range(r+1,len(A)):
            v=A[i][col]
            if v:A[i]=[a-v*b for a,b in zip(A[i],A[r])]
        r+=1
    return r


def pieces(h,T):
    S=set(T);u=h-3
    local=[[Q(i==j and i in S)-Q(int(i in S and j in S),3) for j in range(h)] for i in range(h)]
    outside=[[Q(i==j and i not in S)-Q(int(i not in S and j not in S),u) for j in range(h)] for i in range(h)]
    v=[Q(u if i in S else -3) for i in range(h)];norm=sum(x*x for x in v)
    between=[[x*y/norm for y in v] for x in v]
    constant=[[Q(1,h) for _ in range(h)] for _ in range(h)]
    return local,outside,between,constant


def quotient_commutant(h):
    # Six orbit coefficients: inside diagonal/offdiagonal, outside diagonal/
    # offdiagonal, and the two rectangular directions. Row/column sums vanish
    # in the canonical extension of an endomorphism of sum-zero vectors.
    u=h-3
    constraints=[[1,2,0,0,u,0],[0,0,1,u-1,0,3],
                 [1,2,0,0,0,u],[0,0,1,u-1,3,0]]
    require(rank(constraints)==3,'commutant dimension')
    return constraints


def audit():
    h=16;T=(0,1,2);U=(0,3,4)
    A,B,C,J=pieces(h,T);Z=zero(h);I=eye(h)
    for P,r in ((A,2),(B,h-4),(C,1),(J,1)):
        require(mul(P,P)==P and rank(P)==r,'spectral projector')
    for X,Y in combinations((A,B,C,J),2):
        require(mul(X,Y)==Z and mul(Y,X)==Z,'orthogonal decomposition')
    require(add(add(A,B),add(C,J))==I,'full decomposition')
    # In the sum-zero space the commutant has the three scalar summands
    # A,B,C. Idempotence forces each coefficient to be 0 or 1.
    ranks=[(a,b,c,2*a+(h-4)*b+c) for a,b,c in product((0,1),repeat=3)]
    rank_two=[row for row in ranks if row[-1]==2]
    require(rank_two==[(1,0,0,2)],'unique quotient candidate')
    AU=pieces(h,U)[0];cross=mul(A,AU)
    require(cross!=Z,'unexpected annihilation')
    input_vector=[Q(int(i==0)-int(i==5)) for i in range(h)]
    output=[sum(a*b for a,b in zip(row,input_vector)) for row in cross]
    require(output==[Q(4,9),Q(-2,9),Q(-2,9)]+[Q(0)]*(h-3),'cross witness')
    # Natural h-space also has a 2D trivial isotypic component. Its only
    # rank-two idempotent is identity on it (C+J), unless A is selected.
    # Every C_T+J fixes the common constant line, hence cannot annihilate.
    natural=add(C,J);natural_U=add(pieces(h,U)[2],J)
    ones=[[Q(1)] for _ in range(h)]
    require(mul(mul(natural,natural_U),ones)==ones,'common-line witness')
    # Check actual covariance of candidate under generators in and outside T.
    for i,j in ((0,1),(1,2),(3,4),(14,15)):
        perm=list(range(h));perm[i],perm[j]=perm[j],perm[i]
        for P in (A,B,C,J):
            require([[P[perm[x]][perm[y]] for y in range(h)] for x in range(h)]==P,'stabilizer covariance')
    candidates=[rank_two_budget(15,Q(5)),rank_two_budget(16,Q(3))]
    require(all(p['moment_interval'][1]<1 for p in candidates),'no optimistic headroom')
    return dict(status='EXACT NEGATIVE CONSTRUCTION EXPERIMENT; NO NEW KAPPA',
                changed_assumption='Rank-two labels with arbitrary stabilizer-invariant rational matrices, in place of the rank-one triple projectors.',
                retained_assumption='Full S_h covariance under the natural permutation action or its sum-zero standard subspace.',
                ambient_dimensions=[15,16],ground_size=h,label_rank=2,
                quotient_commutant_constraints=quotient_commutant(h),quotient_commutant_dimension=3,
                projector_component_ranks=[2,12,1],unique_rank_two_quotient_choice=rank_two,
                adjacent_triples=[T,U],cross_product_rank=rank(cross),
                rational_input=input_vector,rational_nonzero_output=output,
                natural_alternative='Identity on the 2D trivial isotypic component; contains/fixes the common constant line and therefore fails neighbor annihilation.',
                optimistic_budgets=candidates,
                proof=['Stabilizer covariance makes a matrix constant on six coordinate-pair orbits. On the sum-zero quotient its row/column constraints have rank three.',
                       'The three independent mutually annihilating projectors A,B,C span that commutant, with ranks 2,h-4,1.',
                       'For h>=7 only A is a rank-two idempotent in this commutant. The explicit adjacent pair has A_T A_U nonzero.',
                       'In the full natural space the trivial component has dimension two. The additional rank-two choice is its identity; all such choices share the constant line.',
                       'Both cases fail. This excludes these actions for h>=7; the exact control here is h=16.'],
                continuation='Stop fully covariant standard/natural block labels. Noncovariant matrices, different group actions, induced subfamilies and different graphs are not excluded.',
                complex_compatibility='No candidate bit labels survive, so no complex transfer claim. A future asymmetric block solution would still need its own phase geometry and side/precision proof.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=audit()
    if args.output:args.output.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
    print('PASS exact covariance classification and adjacent-pair rejection in dimensions 15 and 16')
