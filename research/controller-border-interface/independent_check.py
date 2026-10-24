#!/usr/bin/env python3
"""Independent exact p2/p3 event check; Apache-2.0.

Prepared by Dillon with substantial OpenAI assistance. This is an independent
AI review path, not independent human review or formal-kernel verification.
No local construction or predecessor implementation is imported.
"""
from fractions import Fraction as F
from itertools import product
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def literal(p, q, stage):
    # Numeric exact execution on all input columns; no source emitter imported.
    rows=identity(2*p)
    def add(dst,src,c):
        rows[dst]=[a+c*b for a,b in zip(rows[dst],rows[src])]
    def forward(pair,d):
        x,y=2*pair,2*pair+1
        add(y,x,1/q)
        rows[x]=[d*a for a in rows[x]]
        rows[y]=[d*a for a in rows[y]]
    def backward(pair,d):
        x,y=2*pair,2*pair+1
        add(x,y,-q)
        rows[x]=[d*a for a in rows[x]]
        rows[y]=[d*a for a in rows[y]]
    def bridge(dst,src,c):
        add(2*dst,2*src,c)
        add(2*src+1,2*dst+1,-c)
    forward(0,stage[0])
    for pair in range(p):
        backward(pair,stage[2*pair+1])
        if pair+1<p:
            bridge(pair,pair+1,1)
        forward(pair,stage[2*pair+2] if pair+1==p else F(1))
        if pair+1<p:
            bridge(pair,pair+1,-1)
    for pair in range(p-2,-1,-1):
        bridge(pair+1,pair,1)
    for pair in range(p):
        x,y=2*pair,2*pair+1
        rows[x],rows[y]=rows[y],[-z for z in rows[x]]
    return rows


def closed(p,q,stage):
    ds=([stage[0]*stage[1], stage[3]*stage[4]] if p==2 else
        [stage[0]*stage[1],stage[3],stage[5]*stage[6]])
    if p==2:
        a,b=ds
        X=[[a,1-b],[0,b]]
        Y=[[a,0],[a*(1-b),b]]
    else:
        a,b,c=ds
        X=[[a,1-b,c-1],[0,b,1-c],[0,0,c]]
        Y=[[a,0,0],[a*(1-b),b,0],[a*b*(c-1),b*(1-c),c]]
    A=[[F(0)]*(2*p) for _ in range(2*p)]
    for i,j in product(range(p),repeat=2):
        A[2*i][2*j]=X[i][j]/q
        A[2*i+1][2*j+1]=q*Y[i][j]
    return A,ds


def scaled(A,p,e,reverse=False):
    w=[j if parity==0 else p-1-j for j in range(p) for parity in (0,1)]
    if reverse:w=[-v for v in w]
    return [[a*e**(w[j]-w[i]) for j,a in enumerate(row)] for i,row in enumerate(A)]


def inverse(A):
    n=len(A); aug=[row[:]+eye for row,eye in zip(A,identity(n))]
    for j in range(n):
        k=next(i for i in range(j,n) if aug[i][j]);aug[j],aug[k]=aug[k],aug[j]
        fac=aug[j][j];aug[j]=[x/fac for x in aug[j]]
        for i in range(n):
            if i!=j:
                fac=aug[i][j];aug[i]=[x-fac*y for x,y in zip(aug[i],aug[j])]
    return [row[n:] for row in aug]


def extraction(matrices):
    # Lagrange at zero at nonzero dyadic/integer nodes 1,...,p.
    nodes=[F(i+1) for i in range(len(matrices))]
    weights=[]
    for i,x in enumerate(nodes):
        w=F(1)
        for j,y in enumerate(nodes):
            if i!=j:w*=(-y)/(x-y)
        weights.append(w)
    n=len(matrices[0])
    return [[sum(w*A[i][j] for w,A in zip(weights,matrices)) for j in range(n)] for i in range(n)]


def degree_controls():
    """Multiply actual polynomial matrix factors, independent of native code."""
    cases=[]
    for depth in range(1,5):
        length=2**depth
        n=length+1
        def chain(order):
            matrix=[[{0:F(1)} if i==j else {} for j in range(n)] for i in range(n)]
            # Right multiplication by I+epsilon*E_(j,j+1) updates one column.
            for j in order:
                for i in range(n):
                    updated=dict(matrix[i][j+1])
                    for degree,coefficient in matrix[i][j].items():
                        updated[degree+1]=updated.get(degree+1,F(0))+coefficient
                    matrix[i][j+1]=updated
            return matrix
        result=chain(range(length))
        need(result[0][-1]=={length:F(1)}, 'Long chain contains exactly epsilon**(2**depth)')
        need(max(degree for row in result for poly in row for degree in poly)==length,
             'Actual polynomial matrix has exponential degree in binary tree depth')
        need(all(result[i][i]=={0:F(1)} for i in range(n)), 'Every diagonal remains identity')
        need(chain(reversed(range(length)))[0][-1]!={length:F(1)},
             'Reversing chronological factor order changes the long chain')
        cases.append({'binary_tree_depth':depth, 'executed_factors':length, 'actual_degree':length})
    return cases


def precision_controls():
    """Exact dyadic scalar circuit tests the conditioning term in the lemma."""
    cases=[]
    for requested_bits in (2,5,9):
        for pole_order in (1,2,4):
            # Three exact gates epsilon**h, (1+epsilon), epsilon**(-h)
            # have endpoint 1+epsilon. H=2 bounds every contiguous subword.
            k=requested_bits+3
            epsilon=F(1,2**k)
            fractional_bits=requested_bits+3+pole_order*k
            x=F(1)
            after_middle=(epsilon**pole_order*x)*(1+epsilon)
            error=F(1,2**fractional_bits)
            computed=(after_middle+error)*epsilon**(-pole_order)
            need(abs(computed-x)<=F(1,2**(requested_bits+1)),
                 'Conditioned additive-error budget proves requested accuracy')
            omitted_conditioning=F(1,2**(requested_bits+3))
            wrong=(after_middle+omitted_conditioning)*epsilon**(-pole_order)
            need(abs(wrong-x)>F(1,2**requested_bits),
                 'Dropping h*k fails for an actual permitted additive error')
            cases.append({'requested_bits':requested_bits, 'pole_order':pole_order,
                          'dyadic_epsilon_exponent':k, 'funded_fractional_bits':fractional_bits,
                          'funded_error':str(abs(computed-x)),
                          'underfunded_error':str(abs(wrong-x))})
    return cases


def run():
    checks=0
    samples=[]
    for p in (2,3):
        for seed in range(1,13):
            q=F(seed+1,seed+2)
            stage=[F(seed+2*j+3,2*j+2) for j in range(2*p+1)]
            A=literal(p,q,stage)
            expected,ds=closed(p,q,stage)
            need(A==expected, 'Literal event matrix agrees with independently hardcoded p2/p3 matrix')
            wanted=[[A[i][j] if i==j else F(0) for j in range(2*p)] for i in range(2*p)]
            extracted=extraction([scaled(A,p,F(e)) for e in range(1,p+1)])
            need(extracted==wanted, 'Forward Lagrange extraction returns every diagonal column')
            wrong=extraction([scaled(A,p,F(e),True) for e in range(1,p+1)])
            need(wrong!=wanted, 'Opposite weights must fail forward extraction')
            inverse_transpose=list(map(list,zip(*inverse(A))))
            backward=extraction([scaled(inverse_transpose,p,F(e),True) for e in range(1,p+1)])
            wanted_back=[[1/A[i][j] if i==j else F(0) for j in range(2*p)] for i in range(2*p)]
            need(backward==wanted_back, 'Inverse-transpose extraction with reversed weights')
            wrong_back=extraction([scaled(inverse_transpose,p,F(e)) for e in range(1,p+1)])
            need(wrong_back!=wanted_back, 'Same forward weights must fail inverse-transpose extraction')
            checks+=1
            if seed==1:samples.append({'p':p,'q':str(q),'stages':list(map(str,stage)),
                                     'literal_matrix':[[str(x) for x in row] for row in A]})
    return {'status':'PASS_INDEPENDENT_RATIONAL_P2_P3', 'exact_instances':checks,'all_columns':True,'forward_and_inverse_transpose_extraction':True, 'wrong_weight_controls_rejected':2*checks,'samples':samples, 'degree_growth_controls':degree_controls(), 'conditioning_controls':precision_controls()}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
