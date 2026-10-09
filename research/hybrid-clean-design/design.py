"""Two bounded design screens. Douglas Colkitt; Apache-2.0.

Exact finite controls support the separately written general arguments.
No finite multiplication network or improved exponent is supplied.
"""
from fractions import Fraction as Q
from itertools import combinations, permutations
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def require(condition,message):
    if not condition:raise AssertionError(message)


def rank(rows,p=None):
    a=[[int(x)%p for x in row] if p else list(map(Q,row)) for row in rows]
    if not a:return 0
    k=0
    for j in range(len(a[0])):
        pivot=next((i for i in range(k,len(a)) if a[i][j]),None)
        if pivot is None:continue
        a[k],a[pivot]=a[pivot],a[k]
        inv=pow(a[k][j],-1,p) if p else 1/a[k][j]
        a[k]=[(x*inv)%p if p else x*inv for x in a[k]]
        for i in range(k+1,len(a)):
            c=a[i][j]
            if c:a[i]=[(x-c*y)%p if p else x-c*y for x,y in zip(a[i],a[k])]
        k+=1
        if k==len(a):break
    return k


def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def transpose(a):return list(map(list,zip(*a)))
def product(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def sub(a,b):return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]


def inverse(a):
    n=len(a);a=[list(map(Q,row))+ident for row,ident in zip(a,eye(n))]
    for j in range(n):
        i=next(i for i in range(j,n) if a[i][j])
        a[i],a[j]=a[j],a[i]
        c=a[j][j];a[j]=[x/c for x in a[j]]
        for i in range(n):
            if i!=j:
                c=a[i][j];a[i]=[x-c*y for x,y in zip(a[i],a[j])]
    return [row[n:] for row in a]


def metric(h):return [[Q(i==j)-Q(1,9) for j in range(h)] for i in range(h)]
def triples(h):return list(combinations(range(h),3))
def vector(S,h):return [Q(i in S) for i in range(h)]


def independent(rows):
    out=[]
    for row in rows:
        if rank(out+[row])>len(out):out.append(row)
    return out


def projector(rows,G):
    basis=independent(rows);B=transpose(basis)
    return product(product(product(B,inverse(product(product(basis,G),B))),basis),G)


def line_projectors(h,binary=False):
    out=[]
    for S in triples(h):
        v=vector(S,h)
        # Binary norm is 3=1. Rational norm for I-J/9 is 2.
        out.append([[int(x*y)%2 if binary else x*(y-Q(1,3))/2 for y in v] for x in v])
    return out


def commutant_dimension(matrices,p=None):
    h=len(matrices[0]);equations=[]
    for P in matrices:
        for i in range(h):
            for j in range(h):
                row=[Q(0)]*(h*h)
                for k in range(h):
                    row[i*h+k]+=P[k][j]
                    row[k*h+j]-=P[i][k]
                equations.append(row)
    return h*h-rank(equations,p)


def connected(h,binary=False):
    sets=list(map(set,triples(h)));seen={0};todo=[0]
    while todo:
        i=todo.pop()
        for j,S in enumerate(sets):
            inner=len(sets[i]&S)%2 if binary else len(sets[i]&S)-1
            if j not in seen and inner:seen.add(j);todo.append(j)
    return len(seen)==len(sets)


def chart_controls():
    rows=[]
    for h in (4,5,6):
        for binary in (False,True):
            dim=commutant_dimension(line_projectors(h,binary),2 if binary else None)
            expected=4 if binary and h==4 else 1
            require(dim==expected,'commutant dimension')
            require(connected(h,binary)==(expected==1),'nonorthogonality graph control')
            require(rank([vector(S,h) for S in triples(h)],2 if binary else None)==h,'span')
            rows.append(dict(h=h,field='F2' if binary else 'Q',commutant_dimension=dim,
                             connected=connected(h,binary)))
    return rows


def readout(h):
    require(h>=6 and h!=9,'nondegenerate retained triple regime')
    ts=triples(h);S=set(range(3));G=metric(h)
    zero=[[Q(0)]*h for _ in range(h)]
    H=sub(eye(h),projector([vector(S,h)],G))
    U=[projector([vector(T,h) for T in ts if set(T)&S=={i}],G) for i in S]
    D=projector([[Q(j==i)-Q(j==h-1) for j in range(h)] for i in range(3,h-1)],G)
    frames=[zero,H]+U
    distances=[[rank(sub(A,B)) for B in frames] for A in frames]
    for i in range(3):
        require(rank(U[i])==h-3 and product(H,U[i])==U[i],'side containment')
        require(product(U[i],D)==D and product(D,U[i])==D,'shared subspace')
        for j in range(3):
            if i!=j:require(rank(sub(U[i],U[j]))==2,'distinct side planes')
    tours=[]
    for order in permutations(range(1,5)):
        walk=(0,)+order+(0,)
        tours.append(sum(distances[a][b] for a,b in zip(walk,walk[1:])))
    require(min(tours)==2*h,'terminal-tour lower bound')
    # Explicit additive tree: central at 0 -> D, side 2/3 -> D,
    # accumulator D -> U1, add side 1, accumulator U1 -> H.
    widths=[rank(D),rank(sub(U[1],D)),rank(sub(U[2],D)),
            rank(sub(U[0],D)),rank(sub(H,U[0]))]
    require(widths==[h-4,1,1,1,2],'readout upper tree')
    require(sum(widths)==h+1,'readout upper cost')
    # Central parity and the three disjoint side terms vary independently.
    coefficients=[[len(set(T)&S)%2 for T in ts]]
    coefficients += [[int(set(T)&S=={i}) for T in ts] for i in S]
    require(rank(coefficients,2)==4,'four scalar readout terms independent')
    return dict(h=h,terminal_distances=distances,minimum_terminal_tour=min(tours),
                any_tree_rank_lower_bound=h,explicit_tree_widths=widths,
                explicit_tree_rank=h+1,useful_rank_capacity=h,
                readout_scalar_rank=4,producer_cost_granted=0)


def clean_identity(h):
    ts=triples(h)
    C=[[len(set(S)&set(T))%2 for T in ts] for S in ts]
    A=[[int(len(set(S)&set(T))==1) for T in ts] for S in ts]
    require(all((C[i][j]+A[i][j])%2==int(i==j) for i in range(len(ts)) for j in range(len(ts))),
            'clean central plus side identity')
    return dict(h=h,inputs=len(ts),binary_central_rank=rank(C,2),identity_checked=True)


def aggregate_budget():
    """Hypothetical replacement interface only; no producer is supplied."""
    spec=importlib.util.spec_from_file_location('design_target_budget',ROOT/'research/kappa-nine/target_budget.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    h,n=23,1771
    bounds={g:module.moment({h-1:n+h,1:g},h,n) for g in (1253,1254)}
    require(bounds[1253][1]<1<bounds[1254][0],'singleton headroom threshold')
    return dict(status='HYPOTHETICAL MISSING-PRODUCER BUDGET',h=h,independent_inputs=n,
        known_children={str(h-1):n+h},bit_saving_screen='1/511',
        remaining_rank_budget_at_exponent_one_strictly_below=n-h*(h-1),
        extra_singletons_accepted=1253,extra_singletons_rejected=1254,
        moment_bounds={str(g):[str(x) for x in pair] for g,pair in bounds.items()},
        construction_supplied=False,complex_partner_supplied=False)


def run():
    sources=['research/fourier-boundary-fusion/REPORT.md',
             'research/computation-fusion-nine/REPORT.md','research/mechanism-prep/REPORT.md',
             'docs/research/shared-computation.md','notes/copied-centers-lemma.tex',
             'notes/compact-control-layout.tex','research/hybrid-clean-design/design.py']
    sources += ['research/kappa-nine/target_budget.py','research/hybrid-clean-design/test_design.py']
    return dict(status='DESIGN SCREENS COMPLETE; NO CONSTRUCTION PROMOTED',
        common_chart_controls=chart_controls(),
        clean_scalar_controls=[clean_identity(h) for h in (6,7)],
        clean_readout_controls=[readout(h) for h in (6,7,10)],
        possible_changed_readout_contract=aggregate_budget(),
        current_dimension_consequences=dict(bit_factors=[23,25],complex_factors=[28,28],
            method='General spanning/nonorthogonality argument, not expanded full tensor enumeration'),
        exclusions_scoped=True,new_exponent_claimed=False,
        source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=run()
    if args.output:args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS: common-chart controls, clean scalar maps, readout tree budgets')
    print('No stronger exponent; neither specified design earns a construction run.')
