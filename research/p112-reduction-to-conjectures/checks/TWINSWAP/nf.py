# Check the (1,1) m=10 universal dual-basis normal form on random exact X̂ (rank 9) with non-disjoint supports.
import random, sympy as sp
random.seed(1)
for trial in range(20):
    Xh=sp.Matrix(9,10,lambda i,j: random.randint(-3,3))
    if Xh.rank()<9: continue
    # Ŷ: solve X̂ Ŷᵀ = diag(I8,0); particular + kernel shift
    y2=Xh.nullspace()[0]
    cols=[]
    for i in range(8):
        sol,par=Xh.gauss_jordan_solve(sp.Matrix([1 if r==i else 0 for r in range(9)]))
        cols.append(sol.subs({s:random.randint(-2,2) for s in sol.free_symbols}))
    Yh=sp.Matrix.hstack(*cols).T.col_join(y2.T)   # 9x10
    assert Xh*Yh.T==sp.diag(*([1]*8+[0]))
    x2=Xh.row(8); K=[k for k in range(10) if x2[k]!=0 and y2[k]!=0]
    JQ=[k for k in range(10) if y2[k]!=0]; JP=[k for k in range(10) if x2[k]!=0]
    a=JQ[0]; ap=[k for k in JP if k!=a][0]
    X=Xh[:8,:]; Y=Yh[:8,:]
    Yp=Y - (Y[:,a]/y2[a])*y2.T
    Xp=X - (X[:,ap]/x2[ap])*x2
    others=[k for k in range(10) if k not in (a,ap)]
    M=sum((Xp[:,k]*Yp[:,k].T for k in others), sp.zeros(8,8))
    print('K size',len(K),'a in K',a in K,'dual-basis sum == I8:',M==sp.eye(8), ' <x_a,y_l> = -y2_l*?:', all(sp.simplify((Xp[:,a].T*Yp[:,l])[0]*y2[a]+y2[l])==0 for l in others))
