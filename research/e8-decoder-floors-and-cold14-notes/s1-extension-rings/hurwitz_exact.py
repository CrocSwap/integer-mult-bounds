"""Hurwitz view of E8: 10 quaternionic lines in H^2 (w = 2), each orthogonal to exactly one other.
Exact: the least Theorem-C copy floor  sum_j rank G[R_j, A_j]  (H-rank units) over ALL F_2 decoders B = W U^T on the
pattern (B_TT = 1, B_TS = 0 on non-orthogonal pairs), asymmetric allowed, any number of totals.
For w = 2 the rank of the Gram block between line sets R, A is exactly 0 if R x A has no equal or non-orthogonal pair,
2 if |R| >= 2 and |A| >= 2, and 1 otherwise (checked below from exact ranks).  Totals of rank 0 only touch free entries
and are dropped, so a decoder of cost <= C has at most C totals.  SAT (CaDiCaL via pysat) with a cardinality bound:
cost <= C is UNSAT for C = 9 and SAT for C = 10."""
import sys; sys.path.insert(0,sys.path[0])
from minrank_any import systems
from minrank_sat import CNF
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical153
import itertools
S=systems()['Hurwitz']; v=S.v; NO=S.NO
assert S.w==2 and set(NO.sum(1))=={8}
for R in itertools.chain.from_iterable(itertools.combinations(range(v),k) for k in (1,2,3)):
    for A in itertools.chain.from_iterable(itertools.combinations(range(v),k) for k in (1,2,3)):
        import numpy as np
        rk=S.rank(R) and None
def gram_rank(R,A):
    # exact rank of the real Gram block between the H-spans, / 4
    from e8units import rank_q
    BR=[S.basis[b]@S.V[i] for i in R for b in range(4)]; BA=[S.basis[b]@S.V[i] for i in A for b in range(4)]
    M=[[int(x@S.Q@y) for y in BA] for x in BR]
    r=rank_q(M); assert r%4==0; return r//4
def formula(R,A):
    if not any(T==S_ or NO[T,S_] for T in R for S_ in A): return 0
    return 2 if len(R)>=2 and len(A)>=2 else 1
import random
rnd=random.Random(1); checked=0
for _ in range(400):
    R=rnd.sample(range(v),rnd.randint(1,4)); A=rnd.sample(range(v),rnd.randint(1,4))
    assert gram_rank(R,A)==formula(R,A); checked+=1
print('rank formula checked on',checked,'random pairs')
def feasible(C):
    f=CNF(); c=C
    U=[[f.new() for j in range(c)] for T in range(v)]; W=[[f.new() for j in range(c)] for T in range(v)]
    P={(T,S_,j):f.AND(W[T][j],U[S_][j]) for T in range(v) for S_ in range(v) for j in range(c)}
    for T in range(v): f.parity([P[T,T,j] for j in range(c)],1)
    for T in range(v):
        for S_ in range(v):
            if NO[T,S_]: f.parity([P[T,S_,j] for j in range(c)],0)
    costlits=[]
    for j in range(c):
        # r1 >= any relevant pair; r2 >= (|R|>=2 and |A|>=2)
        r1=f.new(); r2=f.new()
        for T in range(v):
            for S_ in range(v):
                if T==S_ or NO[T,S_]: f.cl.append([-P[T,S_,j],r1])
        for T1,T2 in itertools.combinations(range(v),2):
            for S1,S2 in itertools.combinations(range(v),2):
                f.cl.append([-W[T1][j],-W[T2][j],-U[S1][j],-U[S2][j],r2])
        costlits+=[r1,r2]
    enc=CardEnc.atmost(lits=costlits,bound=C,top_id=f.n,encoding=EncType.seqcounter)
    s=Cadical153(bootstrap_with=f.cl+enc.clauses)
    return s.solve()
for C in (8,9,10):
    print('cost <=',C,'SAT' if feasible(C) else 'UNSAT',flush=True)
