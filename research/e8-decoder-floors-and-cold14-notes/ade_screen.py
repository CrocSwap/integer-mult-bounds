import sys, itertools, numpy as np
from fractions import Fraction as Fr
sys.path.insert(0, '/Users/joelpulikkan/imb-main/research/format-limits/scripts')
from e8units import f2_rank
from skel import X

def roots_A(n):  # in R^{n+1}
    R=[]
    for i in range(n+1):
        for j in range(i+1,n+1):
            v=[0]*(n+1); v[i]=1; v[j]=-1; R.append(v)
    return np.array(R)
def roots_D(n):
    R=[]
    for i in range(n):
        for j in range(i+1,n):
            for s in (1,-1):
                v=[0]*n; v[i]=1; v[j]=s; R.append(v)
    return np.array(R)
def roots_E8():
    R=[list(r) for r in roots_D(8)]
    for signs in itertools.product((1,-1),repeat=8):
        if signs[0]==1 and signs.count(-1)%2==0: R.append([s*0.5 for s in signs])
    return np.array(R)
def E7():
    R=roots_E8(); s=np.ones(8)*0.5
    return R[np.abs(R@s)<1e-9]
def E6():
    R=roots_E8(); a=np.ones(8)*0.5; b=np.zeros(8); b[6]=1;b[7]=1  # pick two orthogonal roots
    b=R[[i for i in range(len(R)) if abs(R[i]@a)<1e-9][0]]
    R7=R[np.abs(R@a)<1e-9]; return R7[np.abs(R7@b)<1e-9]
def stats(name,R):
    G=np.rint(R@R.T).astype(int); v=int(len(R)); h=int(np.linalg.matrix_rank(G))
    B=(1+G)%2; c=int(f2_rank(B))
    x=Fr(c*h, v)
    vals=[(s,X(s,h,1,x)) for s in (3,5,7,9)]; vals=[(s,float(r["hi"])) for s,r in vals if r]; best=max(vals,key=lambda t:t[1]) if vals else (0,0.0)
    print(f"{name:6s} v={v:4d} h={h:2d} c={c:3d} x~c*h/v={float(x):.3f}  X*={best[1]:.4e}@s{best[0]}")
for n in (4,5,6,7,8): stats(f"A{n}",roots_A(n))
for n in (4,5,6,7,8,9,10,12): stats(f"D{n}",roots_D(n))
stats("E6",E6()); stats("E7",E7()); stats("E8",roots_E8())
