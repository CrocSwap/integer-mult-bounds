import sys, itertools, random, time, pickle
sys.argv=[sys.argv[0]]+sys.argv[1:]
from lib2 import *
FC=np.array(D['FC'],dtype=np.int64)
FCl=[tuple(int(a) for a in FC[t]) for t in range(v)]
def key(w):
    j=next((i for i in range(8) if w[i]!=0),None)
    if j is None: return None
    c=w[j]; return tuple(Fr(a)/c for a in w)
RK={}
for t in range(v):
    RK[key(FCl[t])]=t
def nonorth(a,b): return a!=b and Gm[a][b]!=0
def solve_config(J,m,us,kR=5):
    """J: list of 5 column idx; m in J; us: dict j->root line t for R-terms. returns terms or None"""
    Jc=[c for c in range(8) if c not in J]; I=Jc+[m]
    # a_c for c in J\m
    a={}
    for c in J:
        if c==m: continue
        val=FCl[us[c]][c]
        if val==0: return None
        a[c]=Fr(1,val)
    # a_m free: try values later; first determine v_i for i in Jc using a (they involve only c in J incl m!)
    # A[i,c]=a_c*c_{u_c}[i], includes c=m with a_m unknown. Solve for a_m by requiring roots.
    outs=[]
    for am in [Fr(x,y) for x in (1,-1,2,-2,3,-3,1,1) for y in (1,2,3,4)]:
        a2=dict(a); a2[m]=am
        A=[[Fr(0)]*8 for _ in range(8)]
        for c in J:
            for i in range(8): A[i][c]=a2[c]*FCl[us[c]][i]
        vs={}
        ok=True
        for i in I:
            w=[Fr(int(i==c))-A[i][c] for c in range(8)]
            k=key(w)
            if k is None or k not in RK: ok=False;break
            vs[i]=(w,RK[k])
        if not ok: continue
        # rows not in I must match identity: A row r = e_r
        if any(A[r][c]!=Fr(int(r==c)) for r in range(8) if r not in I for c in range(8)): continue
        outs.append((a2,vs))
    return outs
def terms_from(J,us,a2,vs):
    X=[];Y=[];types=[]
    for c in J:
        x=[a2[c]*FCl[us[c]][i] for i in range(8)]; y=[Fr(int(i==c)) for i in range(8)]
        X.append(x);Y.append(y);types.append(('R',us[c],c))
    for i,(w,t) in vs.items():
        x=[Fr(int(r==i)) for r in range(8)]; X.append(x);Y.append(list(w));types.append(('C',t,i))
    return X,Y,types
def kernel(M,ncols):
    # M list of rows (len ncols) Fractions -> basis of right nullspace
    A=[r[:] for r in M]; piv=[];r=0
    for c in range(ncols):
        p=next((i for i in range(r,len(A)) if A[i][c]!=0),None)
        if p is None: continue
        A[r],A[p]=A[p],A[r]; pv=A[r][c]; A[r]=[x/pv for x in A[r]]
        for i in range(len(A)):
            if i!=r and A[i][c]!=0:
                f=A[i][c]; A[i]=[x-f*y for x,y in zip(A[i],A[r])]
        piv.append(c); r+=1
    free=[c for c in range(ncols) if c not in piv]
    out=[]
    for f in free:
        v_=[Fr(0)]*ncols; v_[f]=Fr(1)
        for i,c in enumerate(piv): v_[c]=-A[i][f]
        out.append(v_)
    return out
if __name__=='__main__':
    chunk=int(sys.argv[1]); nch=int(sys.argv[2]); TL=float(sys.argv[3])
    t0=time.time(); stats={}; nconf=0; best=999
    Js=list(itertools.combinations(range(8),5))
    for ji,J in enumerate(Js):
        if ji%nch!=chunk: continue
        Jc=[c for c in range(8) if c not in J]
        for m in J:
            cand={}
            for j in J:
                allowed=set(Jc)|{m,j}
                cand[j]=[t for t in range(v) if FCl[t][j]!=0 and all(FCl[t][c]==0 for c in range(8) if c not in allowed)]
            # m: support subset of Jc+m
            for prod in itertools.product(*[cand[j] for j in J]):
                us=dict(zip(J,prod))
                if len(set(prod))<5: continue
                if not all(nonorth(a_,b_) for a_,b_ in itertools.combinations(prod,2)): continue
                res=solve_config(J,m,us)
                if not res: continue
                for a2,vs in res:
                    vl=[t for (_,t) in vs.values()]
                    if len(set(vl))<4 or not all(nonorth(a_,b_) for a_,b_ in itertools.combinations(vl,2)): continue
                    X,Y,types=terms_from(J,us,a2,vs)
                    # check sum x y^T = I
                    S=[[sum(X[k][i]*Y[k][j] for k in range(9)) for j in range(8)] for i in range(8)]
                    assert all(S[i][j]==int(i==j) for i in range(8) for j in range(8))
                    nconf+=1
                    stats.setdefault('conf',[]).append((J,m,prod,tuple(vl)))
                    if time.time()-t0>TL: break
    print('chunk',chunk,'configs',nconf,flush=True)
    pickle.dump(stats,open(f'conf9_{chunk}.pkl','wb'))
