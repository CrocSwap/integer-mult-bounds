"""Bounded real relaxation of the unrestricted rational rank-two geometry.

An UNKNOWN result excludes nothing. SAT is accepted only after rational,
independent replay. No point-additivity, form or covariance is imposed.
"""
import argparse
from fractions import Fraction as Q
from itertools import combinations
import json
from pathlib import Path
import time


CLIQUE = [(0,1,2),(0,3,4),(0,5,6),(1,3,5),(1,4,6),(2,3,6),(2,4,5)]
TRIPLES = list(combinations(range(9), 3))
EDGES = [(s,t) for s,t in combinations(TRIPLES,2) if len(set(s)&set(t)) == 1]


def multiply(a,b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]


def verify_factors(factors, dimension):
    """Exact Q check of BA=I and both directed cross products on every edge."""
    assert set(factors) == set(TRIPLES)
    for t,(a,b) in factors.items():
        assert len(a)==dimension and all(len(row)==2 for row in a)
        assert len(b)==2 and all(len(row)==dimension for row in b)
        assert all(isinstance(x,(int,Q)) for matrix in (a,b) for row in matrix for x in row)
        assert multiply(b,a)==[[1,0],[0,1]], ('normalization',t)
    for s,t in EDGES:
        assert multiply(factors[s][1],factors[t][0])==[[0,0],[0,0]], ('edge',s,t)
        assert multiply(factors[t][1],factors[s][0])==[[0,0],[0,0]], ('edge',t,s)
    return {'vertices':len(TRIPLES),'unordered_edges':len(EDGES),'dimension':dimension,'rank':2}


def control_factors():
    """Two copies of the rank-eight rational representation, without gauge."""
    out={}
    for t in TRIPLES:
        w=[Q(int(i in t))-Q(1,3) for i in range(8)]
        dual=[(x+sum(w))/2 for x in w]
        a=[[0,0] for _ in range(16)];b=[[0]*16 for _ in range(2)]
        for k in range(2):
            for i in range(8): a[8*k+i][k]=w[i];b[k][8*k+i]=dual[i]
        out[t]=(a,b)
    return out


def inverse(matrix):
    n=len(matrix)
    rows=[[Q(x) for x in row]+[Q(i==j) for j in range(n)] for i,row in enumerate(matrix)]
    for j in range(n):
        pivot=next(i for i in range(j,n) if rows[i][j])
        rows[j],rows[pivot]=rows[pivot],rows[j]
        divisor=rows[j][j];rows[j]=[x/divisor for x in rows[j]]
        for i in range(n):
            if i!=j:
                value=rows[i][j]
                rows[i]=[x-value*y for x,y in zip(rows[i],rows[j])]
    return [row[n:] for row in rows]


def gauged_control():
    """Replay the actual anchor/support normalization in dimension sixteen."""
    from covariant_block_test import rank
    factors=control_factors();columns=[]
    residual=[[Q(i==j) for j in range(16)] for i in range(16)]
    for t in CLIQUE:
        a,b=factors[t];columns.extend([list(col) for col in zip(*a)])
        p=multiply(a,b)
        residual=[[x-y for x,y in zip(row,pr)] for row,pr in zip(residual,p)]
    for col in zip(*residual):
        if rank(columns+[list(col)])>len(columns):columns.append(list(col))
    assert len(columns)==16
    g=[list(row) for row in zip(*columns)];ginv=inverse(g)
    result={t:(multiply(ginv,a),multiply(b,g)) for t,(a,b) in factors.items()}
    for t,(a,b) in result.items():
        if t in CLIQUE:
            i=CLIQUE.index(t)
            assert a==[[int(j==2*i+k) for k in range(2)] for j in range(16)]
            assert b==[[int(j==2*i+k) for j in range(16)] for k in range(2)]
        else:
            for i,c in enumerate(CLIQUE):
                if len(set(t)&set(c))==1:
                    assert all(a[2*i+j][k]==b[k][2*i+j]==0 for j in range(2) for k in range(2))
    return result


def solve(dimension=15, timeout_ms=30000):
    import z3
    start=time.monotonic();solver=z3.SolverFor('QF_NRA')
    solver.set(timeout=timeout_ms)
    factors={};var_count=0
    for ti,t in enumerate(TRIPLES):
        a=[[0,0] for _ in range(dimension)];b=[[0]*dimension for _ in range(2)]
        if t in CLIQUE:
            i=CLIQUE.index(t)
            for k in range(2): a[2*i+k][k]=1;b[k][2*i+k]=1
        else:
            blocked={2*i+k for i,c in enumerate(CLIQUE) if len(set(t)&set(c))==1 for k in range(2)}
            for j in range(dimension):
                if j not in blocked:
                    for k in range(2):
                        a[j][k]=z3.Real(f'a_{ti}_{j}_{k}')
                        b[k][j]=z3.Real(f'b_{ti}_{k}_{j}')
                        var_count+=2
        factors[t]=(a,b)
    equations=0
    def constrain(b,a,diagonal=False):
        nonlocal equations
        for i in range(2):
            for j in range(2):
                terms=[b[i][k]*a[k][j] for k in range(dimension)
                       if not (isinstance(b[i][k],int) and b[i][k]==0)
                       and not (isinstance(a[k][j],int) and a[k][j]==0)]
                expr=z3.simplify(z3.Sum([z3.RealVal(0)]+terms)==int(diagonal and i==j))
                if not z3.is_true(expr): solver.add(expr);equations+=1
    for a,b in factors.values(): constrain(b,a,True)
    for s,t in EDGES:
        constrain(factors[s][1],factors[t][0]);constrain(factors[t][1],factors[s][0])
    built=time.monotonic();result=solver.check();end=time.monotonic()
    report={'status':str(result).upper(),'dimension':dimension,'rank':2,'ground_points':9,
            'solver':'z3 '+z3.get_version_string(),'timeout_ms':timeout_ms,
            'variables':var_count,'nontrivial_equations':equations,
            'build_seconds':built-start,'solve_seconds':end-built,
            'restrictions':'Only a simultaneous rational gauge for the seven fixed Fano projectors. No covariance or additive labels.',
            'interpretation':'No new geometry or multiplication bound unless exact rational replay passes.'}
    if result==z3.unknown: report['reason']=solver.reason_unknown()
    elif result==z3.sat:
        model=solver.model();rational={}
        try:
            def rationalize(x):
                if isinstance(x,int): return Q(x)
                y=model.eval(x,model_completion=True)
                if not z3.is_rational_value(y): raise ValueError('Algebraic real model; not a rational certificate')
                return Q(y.numerator_as_long(),y.denominator_as_long())
            for t,(a,b) in factors.items():
                rational[t]=([[rationalize(x) for x in row] for row in a],
                             [[rationalize(x) for x in row] for row in b])
            report['exact_rational_replay']=verify_factors(rational,dimension)
            report['factors']=[{'triple':t,'A':[[str(x) for x in row] for row in a],
                               'B':[[str(x) for x in row] for row in b]} for t,(a,b) in rational.items()]
        except ValueError as e: report['uncertified_model']=str(e)
    else:
        report['interpretation']='Solver UNSAT over R; obtain a replayable mathematical certificate before using this as a theorem.'
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--timeout-ms',type=int,default=30000)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    report=solve(timeout_ms=args.timeout_ms)
    report['positive_control']=verify_factors(control_factors(),16)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='factors'},indent=2))
