#!/usr/bin/env python3
"""Exact rational checks for the e=1 host-strip transition; no word legality claim.

Requires SymPy. Equations mirror sgProd, sgG, sgK in pinned CallerSGram.lean.
"""
import argparse
from itertools import combinations
from pathlib import Path
import subprocess
import sympy as s

PIN = {
    'CallerExtraThin.lean': '6cb7618e691f52b647e168494d3218d80dda9915',
    'CallerRC2.lean': '321ec331931fecddd844f3b12fe0caf27178269c',
    'CallerSGram.lean': '6c03a7f3b3c50fe4340cd105378409ca39abc474',
    'CallerThin.lean': 'f85fc659414297e2444489f9982bf966d5fadb9f',
    'EasyWireK.lean': '6201126ea61e61ad39d0b3f2a59f1dc6d4b955c0',
}
HERE = Path(__file__).resolve().parent

def source_check():
    for name, expected in PIN.items():
        result = subprocess.check_output(['git', 'hash-object', str(HERE/'source'/name)], text=True).strip()
        assert result == expected, (name, result, expected)
    print('Pinned source blob checks: PASS (%d files)' % len(PIN))

def frame(A, B, blocks):
    n, m = A.shape
    assert B.shape == A.shape and sorted(i for block in blocks for i in block) == list(range(m))
    time = {i:t for t, block in enumerate(blocks) for i in block}
    G = B.T * A
    K = s.Matrix(m, m, lambda i,j: (2 if i == j else 0) +
                 (G[i,j] if time[i] <= time[j] else -G[i,j]))
    P = s.eye(n)
    for block in blocks:
        P = (s.eye(n) + A[:,block] * B[:,block].T) * P
    return P, G, K

def block(M, rows, cols):
    return M.extract(rows, cols)

def verify_singleton_set_rc2(A, B, blocks, k):
    # Reproduce rc2_set's counts at l=2 with the published all-singleton singP.
    masks=[]
    for r in range(A.rows):
        masks.append({t for t in range(k) if any(A[r,i] != 0 or B[r,i] != 0
                                                for i in blocks[t])})
    G=B.T*A
    for t in range(k):
        partners=[u for u in range(k) if u != t]
        for size in range(len(partners)+1):
            for selection in combinations(partners,size):
                T=set(selection)
                cols=[i for u in selection for i in blocks[u]]
                rho=block(G,blocks[t],cols).rank()
                # pc_r(t)={t}: disjoint from T and size one.
                deep=sum(t in M and len(M)>=2 for M in masks)
                shallow=sum(t in M and bool(M & T) and len(M)<2 for M in masks)
                assert rho <= deep + shallow
    counts=[sum(t in M and len(M)>=2 for M in masks) for t in range(k)]
    print('  singP masks:', [sorted(x) for x in masks], '; eligible role counts:',counts)
    print('  rc2_set at l=2, all partner subsets: PASS')

def report(label, A, B, blocks, k):
    P, G, K = frame(A, B, blocks)
    m, n = A.cols, A.rows
    host = [i for bl in blocks[:k] for i in bl]
    Kh = block(K, host, host)
    d, pair = [], {}
    for j, r in enumerate(blocks[:k]):
        diag = block(K, r, r)
        assert len(r) == 2 and diag.det() != 0
        others = [i for t, bl in enumerate(blocks[:k]) if t != j for i in bl]
        strip_rank = block(K, r, others).rank()
        d.append(2-strip_rank)
        for t, c in enumerate(blocks[:k]):
            if j != t:
                pair[(j,t)] = block(G,r,c).rank()
    print(label)
    print('  n=%d, hosts=%d, thins=%d, excess=%d' % (n,k,m-2*k,m-n-2))
    print('  P = -I:', P == -s.eye(n), '; ranks G, K, Kh:', G.rank(),K.rank(),Kh.rank())
    print('  diagonal determinants:',[block(K, r, r).det() for r in blocks[:k]])
    print('  pair Gram ranks:', pair, '; off-diagonal strip deficiencies:',d)
    assert P == -s.eye(n), 'full product must equal -I'
    assert G.rank() == n and K.rank() <= m-n
    assert all(x >= 1 for x in pair.values())
    verify_singleton_set_rc2(A,B,blocks,k)
    assert all(Kh.rank() >= 2+sum(d[j] for j in range(k) if j != t) for t in range(k))
    if m-n-2 == 1 and k >= 3:
        assert sum(d) <= 1
    return P,G,K,d

def source_control():
    # Direct transcription of CallerSGram.lean uu, vv, A3 and B3, 0-based.
    uu = [[1,2],[0,1],[1,0]]
    vv = [[-s.Rational(1,3),-s.Rational(2,3)],[1,0],[-s.Rational(5,2),1]]
    A = s.Matrix(4,6,lambda r,c: uu[c//2][r//2] if r%2 == c%2 else 0)
    B = s.Matrix(4,6,lambda r,c: vv[c//2][r//2] if r%2 == c%2 else 0)
    _,_,K,d=report('Published e=0 control (CallerSGram.A3/B3):',A,B,[[0,1],[2,3],[4,5]],3)
    assert K.rank()==2 and d == [0,0,0]

def two_stage_tight_boundary():
    # With fixed type-B K gauge, two shared hubs and no local roles.
    J=s.Matrix([[1,-1],[1,1]])
    A=s.Matrix.hstack(J-2*s.eye(2),J-2*s.eye(2))
    B=s.Matrix.hstack(s.eye(2),s.eye(2))
    _,_,K,d=report('e=0, two-host two-hub signed-frame witness:',A,B,[[0,1],[2,3]],2)
    assert K.rank()==2 and d==[0,0]
    assert all(block(K,bl,bl)==J for bl in ([0,1],[2,3]))
    print('  both host K blocks match fixed type-B gauge: PASS')
    print('  Frame example only; no Legal word, grammar, contacts, or invoice established.')

def matrix_boundary_controls():
    # Host-matrix-only threshold controls. These are not signed-frame claims.
    # K_ss=I_2; every off-diagonal block diag(0,1); rank k+1.
    for k in range(2, 7):
        M=s.zeros(2*k)
        for i in range(k):
            for j in range(k):
                M[2*i,2*j] = 1 if i == j else 0
                M[2*i+1,2*j+1] = 1
        deficits=[]
        for i in range(k):
            rows=[2*i,2*i+1]
            cols=[c for j in range(k) if j != i for c in (2*j,2*j+1)]
            assert block(M,rows,rows).det() == 1
            deficits.append(2-block(M,rows,cols).rank())
        assert deficits == [1]*k and M.rank() == k+1
        print('Host-matrix threshold k=%d, e=%d: rank=%d, all deficiencies=1: PASS' %
              (k,k-1,M.rank()))
    # k=3, e=1: the theorem's one deficient stage is attainable as a matrix.
    U=s.Matrix([[1,0,0],[0,1,0],[0,1,0],[0,0,1],[0,1,0],[0,0,1]])
    V=s.Matrix([[1,0,0,0,0,0],[0,1,1,0,1,0],[0,0,0,1,0,1]])
    M=U*V
    deficits=[]
    for i in range(3):
        rows=[2*i,2*i+1]
        cols=[c for j in range(3) if j != i for c in (2*j,2*j+1)]
        assert block(M,rows,rows).det() != 0
        deficits.append(2-block(M,rows,cols).rank())
    assert M.rank()==3 and deficits==[1,0,0]
    print('Host-matrix sharpness k=3, e=1: one deficient strip: PASS')

def projected_core_and_sign_controls():
    # Four-stage rank-3 arbitrary host matrix: one deficient strip; deleting it leaves rank 2.
    U=s.Matrix([[1,0,0],[0,1,0],[0,1,0],[0,0,1],
                [0,1,0],[0,0,1],[0,1,0],[0,0,1]])
    V=s.Matrix([[1,0,0,0,0,0,0,0],
                [0,1,1,0,1,0,1,0],
                [0,0,0,1,0,1,0,1]])
    K=U*V
    assert K.rank()==3
    assert all(block(K,[2*t,2*t+1],[2*t,2*t+1]).det()!=0 for t in range(4))
    assert 2-block(K,[0,1],list(range(2,8))).rank()==1
    assert block(K,list(range(2,8)),list(range(2,8))).rank()==2
    print('Projected-core control: rank 3; one deficient stage; complement rank 2: PASS')
    # Four ordered stages a<b<c<d; rows (a,c), columns (b,d).
    I=s.eye(2)
    alt=s.BlockMatrix([[I,I],[-I,I]]).as_explicit()
    assert alt.det()==4 and alt.rank()==4
    changed=s.BlockMatrix([[I,I],[I,I]]).as_explicit()
    assert changed.det()==0 and changed.rank()==2
    assert all(int(x)%2 == int(y)%2 for x,y in zip(alt,changed))
    print('Alternating sign block: det=4, rank=4; sign-flip/mod-2 control rank=2: PASS')
    # Other-lane concrete configuration: 38 matching edges + 35 duplicate roles.
    edges=[(2*i,2*i+1) for i in range(38)]
    role_edges=edges+edges[:35]
    graph={tuple(sorted(edge)) for edge in role_edges}
    independent=set(range(0,76,2))
    assert len(role_edges)==73 and len(graph)==38 and len(independent)==38
    assert not any(a in independent and b in independent for a,b in graph)
    from fractions import Fraction
    from math import ceil
    assert ceil(Fraction(76*(76-2),4))==1406
    assert ceil(Fraction(76*(76-3),6))==925
    print('k=76 configuration: 73 degree-2 roles, 38 distinct edges, independent 38: PASS')
    print('  two-hub necessary distinct edges: e=0 >=1406, e=1 >=925')

def rank_one_factor(M):
    assert M.rank() == 1
    j = next(j for j in range(M.cols) if M[:,j] != s.zeros(M.rows,1))
    a = M[:,j]
    i = next(i for i in range(M.rows) if a[i] != 0)
    b = M[i,:] / a[i]
    assert a*b == M
    return a,b.T

def three_stage_witness():
    # Two universal hubs, five local roles: exact host G has only hub overlaps.
    D=[s.Matrix([[-1,0],[-2,1]]), s.diag(1,-1), s.Matrix([[-1,2],[0,1]])]
    J=s.Matrix([[1,-1],[1,1]])
    V=[d.inv()*J for d in D]
    Ah=s.zeros(7,6); Bh=s.zeros(7,6)
    row=2
    for t in range(3):
        sl=slice(2*t,2*t+2)
        Ah[0:2,sl]=V[t]
        Bh[0:2,sl]=s.eye(2)
        residual=J-2*s.eye(2)-V[t]
        C,E=residual.rank_decomposition()
        r=residual.rank()
        Ah[row:row+r,sl]=E
        Bh[row:row+r,sl]=C.T
        row+=r
    assert row==7
    eye=s.eye(7)
    P=eye
    for t in range(3):
        sl=slice(2*t,2*t+2)
        P=(eye+Ah[:,sl]*Bh[:,sl].T)*P
    assert P.det()==1 and (P+eye).rank()==4
    target=-P.inv()
    # Exact products T1*T2*T3*T4=target, first three transvections.
    u=[s.Matrix([3,7,-2,1,1,0,-1]),
       s.Matrix([-4,-10,3,-1,-1,1,1]),
       s.Matrix([-s.Rational(2,5),2,-s.Rational(6,5),s.Rational(2,5),s.Rational(2,5),-s.Rational(2,5),-s.Rational(2,5)])]
    f=[s.Matrix([1,3,8,-8,0,0,0]),
       s.Matrix([0,1,s.Rational(12,5),-2,-s.Rational(2,5),s.Rational(2,5),0]),
       s.Matrix([0,0,1,5,-6,1,-5])]
    Ts=[eye+u[i]*f[i].T for i in range(3)]
    assert all((T-eye).rank()==1 and (T-eye)**2==s.zeros(7) and T.det()==1 for T in Ts)
    H=Ts[2].inv()*Ts[1].inv()*Ts[0].inv()*target
    assert (H-eye).rank()==1 and H*H==eye and H.det()==-1
    assert Ts[0]*Ts[1]*Ts[2]*H*P == -eye
    # Rightmost acts first, so chronological thin order is H, T3, T2, T1.
    As=[Ah]; Bs=[Bh]
    for transfer in [H,Ts[2],Ts[1],Ts[0]]:
        aa,bb=rank_one_factor(transfer-eye)
        As.append(aa); Bs.append(bb)
    A=s.Matrix.hstack(*As); B=s.Matrix.hstack(*Bs)
    blocks=[[0,1],[2,3],[4,5],[6],[7],[8],[9]]
    _,G,K,d=report('e=1, three-host two-hub signed-frame witness:',A,B,blocks,3)
    assert d == [0,0,0] and K.rank()==3
    assert all(block(K,bl,bl)==J for bl in blocks[:3])
    masks=[{t for t in range(3) if any(A[r,i]!=0 or B[r,i]!=0 for i in blocks[t])}
           for r in range(7)]
    assert masks[:2]==[set(range(3)),set(range(3))]
    assert all(len(x)==1 for x in masks[2:])
    assert all(block(G,blocks[i],blocks[j]).rank()==2 for i in range(3) for j in range(3) if i!=j)
    print('  three fixed-gauge hosts, two universal hubs, five local roles: PASS')
    print('  four thin factors: one reflection, three transvections: PASS')
    print('  Frame example only; no Legal word, grammar, contacts, or invoice established.')

def witness(mutate=False):
    # Each host V is a conjugate of the fixed type-B gauge (-1,1/2).
    V0=s.Matrix([[1,1,0],[-2,-1,0],[0,0,1]])
    V1=s.Matrix([[1,0,0],[0,1,1],[0,-2,-1]])
    H=s.Matrix([[1,0,0],[-2,-1,-1],[0,0,1]])
    U=s.Matrix([[1,-1,-1],[0,3,2],[0,-2,-1]])
    eye=s.eye(3)
    assert H*H == eye and (H-eye).rank()==1 and H.det()==-1
    assert (U-eye).rank()==1 and (U-eye)**2 == s.zeros(3) and U.det()==1
    assert H*U*V1*V0 == -eye
    embed0=s.Matrix([[1,0],[0,1],[0,0]])
    embed1=s.Matrix([[0,0],[1,0],[0,1]])
    R=s.Matrix([[1,1],[0,-2]])
    core=s.Matrix([[1,1],[-2,-1]])
    As=[]; Bs=[]
    for E in (embed0,embed1):
        As.append(E*(core-s.eye(2))*R)
        Bs.append(E*(R.inv().T))
    aq,bq=rank_one_factor(U-eye)
    ah,bh=rank_one_factor(H-eye)
    if mutate:
        aq[0] += 1
    As.extend([aq,ah]); Bs.extend([bq,bh])
    A=s.Matrix.hstack(*As); B=s.Matrix.hstack(*Bs)
    P,G,K=frame(A,B,[[0,1],[2,3],[4],[5]])
    if mutate:
        print('Mutated QUERY column preserves P=-I:',P == -eye)
        assert P == -eye, 'negative control detected changed block transfer'
        return
    print('  witness A=',A.tolist())
    print('  witness B=',B.tolist())
    _,_,K,d=report('e=1, two-host signed-frame witness:',A,B,[[0,1],[2,3],[4],[5]],2)
    canonical=s.Matrix([[1,-1],[1,1]])
    assert block(K,[0,1],[0,1]) == canonical
    assert block(K,[2,3],[2,3]) == canonical
    assert d == [1,1]
    assert all(block(A,range(3),idx).rank()==2 and block(B,range(3),idx).rank()==2
               for idx in ([0,1],[2,3]))
    print('  host K blocks match fixed type-B gauge (-1, 1/2): PASS')
    print('  both host A and B submatrices have rank 2: PASS')
    print('  thin factors: QUERY-like unipotent; IDLE_ODD-like reflection: PASS')
    print('  Frame example only; no Legal word, grammar, contacts, or invoice established.')

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--mutate',action='store_true')
    args=parser.parse_args()
    source_check()
    if not args.mutate:
        source_control()
        two_stage_tight_boundary()
        matrix_boundary_controls()
        projected_core_and_sign_controls()
        three_stage_witness()
    witness(args.mutate)
