"""SLACK win.py [exact, sympy]: abstract window block.  Units u0,u1 (stage A, earlier), u2,u3 (stage B).  Gram G = y_i . x_j from Lemma S:
G[i,j] = (W Z^T)_ij if i later than j, -(W Z^T)_ij if earlier, stage block G_ss = [[0,g],[h,0]] with W_s Z_s^T = [[1,-g],[h,1]].
Prefix action on coefficients beta (v = sum beta_j x_j): T_i: beta -> beta - 2 e_i (G[i,:] beta), applied u0,u1,u2,u3.
A b_K>0 block needs A beta = -beta with Z^T beta = 0 (v orthogonal to all later y, NESTPROOF L1/L3)."""
import sympy as sp
g0,h0,g1,h1=sp.symbols('g0 h0 g1 h1')
z=sp.symbols('z0:8')
Z0=sp.Matrix(2,2,z[:4]); Z1=sp.Matrix(2,2,z[4:])
K0=sp.Matrix([[1,-g0],[h0,1]]); K1=sp.Matrix([[1,-g1],[h1,1]])
W0=K0*Z0.T.inv(); W1=K1*Z1.T.inv()
W=sp.Matrix.vstack(W0,W1); Zm=sp.Matrix.vstack(Z0,Z1); WZ=W*Zm.T
G=sp.zeros(4,4)
for i in range(4):
    for j in range(4):
        si,sj=i//2,j//2
        if si>sj: G[i,j]=WZ[i,j]
        elif si<sj: G[i,j]=-WZ[i,j]
G[0,1]=g0; G[1,0]=h0; G[2,3]=g1; G[3,2]=h1
A=sp.eye(4)
for i in range(4):
    Ai=sp.eye(4); Ai[i,:]=Ai[i,:]-2*G[i,:]; A=Ai*A
# restrict to S0 = ker Z^T: basis N (4x2)
N=sp.Matrix.hstack(*Zm.T.nullspace())
M=sp.Matrix.hstack(A*N+N)          # (A+I) on S0 ; need nontrivial kernel
print('rank of (A+I)|S0 generic:', M.rank(simplify=True) if False else None)
import random
p=2147483629
def num(sub):
    Mn=M.subs(sub); return sp.Matrix(Mn).applyfunc(sp.nsimplify)
cnt={}
for trial in range(6):
    sub={s:sp.Rational(random.randint(-9,9),random.randint(1,5)) for s in (g0,h0,g1,h1)+z}
    try: Mn=M.subs(sub); r=Mn.rank()
    except Exception as ex: r='err'
    cnt[r]=cnt.get(r,0)+1
print('rank (A+I) on S0 at random rational params:',cnt)
# solve for parameters making rank < 2: 2x2 minors of the 4x2 matrix all vanish
Mf=sp.simplify(M)
dets=[sp.factor(sp.together(Mf[[i,j],:].det())) for i in range(4) for j in range(i+1,4)]
for d in dets: print('minor:',d)
