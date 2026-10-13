"""Bounded necessary-subsystem search: uniform mode 3 with regular blocks.

Only the 42 Y labels and seven anchors are tested; X-label extension remains
required. UNKNOWN excludes nothing; a SAT result needs exact rational replay.
"""
from fractions import Fraction as Q
from itertools import combinations,permutations
from pathlib import Path
import argparse
import json
import time
from local_rank_test import Y,line_graph,color_y
from local_support_elimination import ADJ,CLIQUE,TRIPLES,INDEX,initial_supports,classes
from noncovariant_search import multiply


def coordinate_supports(exceptions):
    base,_=initial_supports((3,)*7);colors=[line_graph(k)['colors'] for k in range(7)]
    supports={};forced={}
    for i in Y:
        support=set();nonzero=set()
        for k in range(7):
            if not base[i]>>k&1:continue
            if k in exceptions:support.update([2*k,2*k+1])
            else:
                coordinate=2*k+colors[k][str(i)]
                support.add(coordinate);nonzero.add(coordinate)
        supports[i]=support;forced[i]=nonzero
    return supports,forced


def verify_partial(factors,exceptions):
    supports,forced=coordinate_supports(exceptions)
    assert set(factors)==set(Y)
    for i,(a,b) in factors.items():
        assert len(a)==14 and all(len(row)==2 for row in a)
        assert len(b)==2 and all(len(row)==14 for row in b)
        assert all(isinstance(x,(int,Q)) for m in (a,b) for row in m for x in row)
        for c in range(14):
            if c not in supports[i]:assert a[c]==[0,0] and b[0][c]==b[1][c]==0
            if c in forced[i]:assert any(a[c]) and any(b[k][c] for k in range(2))
        assert multiply(b,a)==[[1,0],[0,1]]
    edges=0
    for i,j in combinations(Y,2):
        if ADJ[i]>>j&1:
            assert multiply(factors[i][1],factors[j][0])==[[0,0],[0,0]]
            assert multiply(factors[j][1],factors[i][0])==[[0,0],[0,0]]
            edges+=1
    return {'Y_labels':42,'Y_edges':edges,'ambient_dimension':14,
            'scope':'Y labels plus their anchor supports only; no X extension or full geometry.'}


def coordinate_control():
    colors=color_y();factors={}
    for i,c in colors.items():
        a=[[0,0] for _ in range(14)];b=[[0]*14 for _ in range(2)]
        for k in range(2):a[2*c+k][k]=1;b[k][2*c+k]=1
        factors[i]=(a,b)
    return factors


def equivalent_minimal_patterns():
    fixed=set(CLIQUE);patterns={}
    for p in permutations(range(7)):
        mapped=[tuple(sorted(p[j] for j in c)) for c in CLIQUE]
        if set(mapped)!=fixed:continue
        permutation=[CLIQUE.index(c) for c in mapped]
        target=tuple(sorted(permutation[k] for k in (0,1,2)))
        patterns.setdefault(target,p)
    assert len(patterns)==7
    return [{'exception_blocks':target,'ground_point_permutation':p} for target,p in sorted(patterns.items())]


def normalization_positions(exceptions):
    supports,forced=coordinate_supports(exceptions);positions={}
    for i in Y:
        pair=set(TRIPLES[i])&set(range(7))
        distinguished=next(k for k,c in enumerate(CLIQUE) if pair<=set(c))
        if distinguished in exceptions:continue
        assert len(forced[i])==2
        c=next(c for c in forced[i] if c//2==distinguished)
        r=next(r for r in forced[i] if r!=c)
        # Verify the singleton coordinate that makes the local gauge valid.
        group=next(y for _,y in classes() if i in y)
        outside=7 if 7 in TRIPLES[i] else 8
        clique=[j for j in group if outside in TRIPLES[j]]
        assert all(c not in supports[j] for j in clique if j!=i)
        positions[i]=(c,r)
    assert len(positions)==24
    return positions


def solve(exceptions=(0,1,2),timeout_ms=20000,normalize=False):
    import z3
    supports,forced=coordinate_supports(exceptions)
    solver=z3.SolverFor('QF_NRA');solver.set(timeout=timeout_ms)
    start=time.monotonic();factors={};variables=0;equations=0;inequalities=0
    positions=normalization_positions(exceptions) if normalize else {}
    for i in Y:
        a=[[0,0] for _ in range(14)];b=[[0]*14 for _ in range(2)]
        for c in supports[i]:
            for k in range(2):
                a[c][k]=z3.Real(f'a_{i}_{c}_{k}');b[k][c]=z3.Real(f'b_{i}_{k}_{c}');variables+=2
        if i in positions:
            c,r=positions[i]
            a[c]=[1,0];a[r]=[0,1]
            b[0][c]=1;b[1][c]=0;b[0][r]=0
            variables-=7
        for c in forced[i]:
            solver.add(z3.Or(a[c][0]!=0,a[c][1]!=0),z3.Or(b[0][c]!=0,b[1][c]!=0));inequalities+=2
        factors[i]=(a,b)
    def equation(terms,value):
        nonlocal equations
        expr=z3.simplify(z3.Sum([z3.RealVal(0)]+terms)==value)
        if not z3.is_true(expr):solver.add(expr);equations+=1
    for i in Y:
        a,b=factors[i]
        for k in range(2):
            for l in range(2):equation([b[k][c]*a[c][l] for c in supports[i]],int(k==l))
    for i,j in combinations(Y,2):
        if not ADJ[i]>>j&1:continue
        for u,v in [(i,j),(j,i)]:
            for k in range(2):
                for l in range(2):
                    equation([factors[u][1][k][c]*factors[v][0][c][l] for c in supports[u]&supports[v]],0)
    # Redundant but useful inverse identities on each saturated three-label clique.
    for _,group in classes():
        for outside in (7,8):
            clique=[i for i in group if outside in TRIPLES[i]]
            coordinates=sorted(set.union(*(supports[i] for i in clique)))
            assert len(coordinates)==6
            for c in coordinates:
                for d in coordinates:
                    equation([factors[i][0][c][k]*factors[i][1][k][d]
                              for i in clique for k in range(2)
                              if c in supports[i] and d in supports[i]],int(c==d))
    built=time.monotonic();answer=solver.check();ended=time.monotonic()
    result={'status':str(answer).upper(),'solver':'z3 '+z3.get_version_string(),
            'exceptions':list(exceptions),'requested_timeout_ms':timeout_ms,
            'variables':variables,'nontrivial_equalities':equations,'nonzero_vector_constraints':inequalities,
            'local_basis_normalization':normalize,'normalized_labels':len(positions),
            'build_seconds':built-start,'solve_seconds':ended-built,
            'scope':'Necessary 42-Y-label subsystem of uniform mode 3; exactly four regular blocks, with the remaining three unrestricted. No X labels or multiplication construction.',
            'claim':'No new geometry or exponent.'}
    if answer==z3.unknown:result['reason']=solver.reason_unknown()
    elif answer==z3.sat:
        model=solver.model()
        def rational(x):
            if isinstance(x,int):return Q(x)
            value=model.eval(x,model_completion=True)
            if not z3.is_rational_value(value):raise ValueError('Algebraic real values; rational certification still required.')
            return Q(value.numerator_as_long(),value.denominator_as_long())
        try:
            exact={i:([[rational(x) for x in row] for row in a],[[rational(x) for x in row] for row in b]) for i,(a,b) in factors.items()}
            result['exact_replay']=verify_partial(exact,exceptions)
            result['factors']=[{'vertex':i,'A':[[str(x) for x in row] for row in a],'B':[[str(x) for x in row] for row in b]} for i,(a,b) in exact.items()]
        except ValueError as error:result['uncertified_model']=str(error)
    else:result['claim']='Solver UNSAT only: require a mathematical or independently replayable certificate before claiming exclusion.'
    result['all_exceptional_positive_control']=verify_partial(coordinate_control(),range(7))
    result['equivalent_minimal_patterns']=equivalent_minimal_patterns()
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--timeout-ms',type=int,default=20000)
    parser.add_argument('--normalize',action='store_true')
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=solve(timeout_ms=args.timeout_ms,normalize=args.normalize);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('factors','equivalent_minimal_patterns')},indent=2))
