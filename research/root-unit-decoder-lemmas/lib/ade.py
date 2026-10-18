import itertools, numpy as np, sys
sys.setrecursionlimit(10000)
def lines(R):
    out=[];seen=set()
    for r in R:
        r=np.array(r,float); i=np.nonzero(np.abs(r)>1e-9)[0][0]
        if r[i]<0: r=-r
        key=tuple(np.round(r*2).astype(int))
        if key not in seen: seen.add(key); out.append(r)
    return np.array(out)
def A(n):
    R=[];
    for i in range(n+1):
        for j in range(i+1,n+1):
            v=[0]*(n+1);v[i]=1;v[j]=-1;R.append(v)
    return lines(R)
def D(n):
    R=[]
    for i in range(n):
        for j in range(i+1,n):
            for s in (1,-1):
                v=[0]*n;v[i]=1;v[j]=s;R.append(v)
    return lines(R)
def E8():
    R=[list(r) for r in D(8)]
    for sg in itertools.product((1,-1),repeat=8):
        if sg.count(-1)%2==0: R.append([s*.5 for s in sg])
    return lines(R)
def E7():
    R=E8(); s=np.ones(8)*.5; return R[np.abs(R@s)<1e-9]
def E6():
    R=E7(); s=np.ones(8)*.5; b=R[0]; return R[np.abs(R@b)<1e-9] if False else E6b()
def E6b():
    R=E8(); a=np.ones(8)*.5; b=np.zeros(8); b[6]=1; b[7]=1
    # E6 = roots orthogonal to an A2 in E8: take two roots r1,r2 with <r1,r2>=-1
    r1=R[0]; r2=[r for r in R if abs(r@r1+1)<1e-9 or abs(r@r1-1)<1e-9][0]
    return R[(np.abs(R@r1)<1e-9)&(np.abs(R@r2)<1e-9)]
def f2rank(M):
    M=(M%2).astype(np.uint8).copy(); r=0; n,m=M.shape
    for c in range(m):
        p=[i for i in range(r,n) if M[i,c]]
        if not p: continue
        M[[r,p[0]]]=M[[p[0],r]]
        for i in range(n):
            if i!=r and M[i,c]: M[i]^=M[r]
        r+=1
    return r
def maxclique(adj):
    n=len(adj); best=[]
    nb=[set(np.nonzero(adj[i])[0]) for i in range(n)]
    def ex(R,P):
        nonlocal best
        if len(R)+len(P)<=len(best): return
        if not P:
            best=list(R); return
        for v in sorted(P):
            ex(R+[v],P&nb[v]); P=P-{v}
            if len(R)+len(P)<=len(best): return
    ex([],set(range(n))); return best
