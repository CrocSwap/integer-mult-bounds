# QBRANCH qb8: Q>=1 LP + conjectural DEG1<=Q row (#D>=2 roles >= 2k-2). float, column generation. [CONJ side data]
import sys
exec(open('qb1.py').read().split("if __name__")[0])
def solve2(k,maxit=800):
    ells=list(range(3,k+1)); nr=1+len(ells)
    rhs=np.r_[[2*k]*nr,2*k-2].astype(float)
    cols=[(D,tuple([1]*D)) for D in range(1,k+1)]+[(2,(2,)),(2,(1,1))]+[(D,(D,)) for D in range(2,k+1)]
    cols=list(dict.fromkeys(cols)); n=2*k-1
    for it in range(maxit):
        A=np.array([np.r_[rows(k,D,P,ells),1.0 if D>=2 else 0.0] for D,P in cols]).T
        c=-np.array([val(D,P)-1 for D,P in cols])
        r=linprog(c,A_ub=np.vstack([-A,-np.ones((1,len(cols)))]),b_ub=np.r_[-rhs,-n],method='highs')
        marg=-r.ineqlin.marginals; w=marg[:nr]; y2=marg[nr]; lam=marg[nr+1]
        pr=price(k,w,0,ells,1,k,0)
        new=[]
        for sc,D,P in pr:
            sc2=sc-1-lam+(y2 if D>=2 else 0)
            if sc2>1e-9 and (D,P) not in cols: new.append((sc2,D,P))
        # D>=2 types also with y2: pricing by D already; but best P per D computed w/o y2 (const per D) fine
        if not new: break
        cols+=[(D,P) for _,D,P in sorted(new,reverse=True)[:12]]
    return (-r.fun+2*k-2)*104/k,[(round(x,3),D,P) for x,(D,P) in zip(r.x,cols) if x>1e-7]
for k in map(int,sys.argv[1:]):
    c,sup=solve2(k); print(k,'HP0',round(HP(k),3),'Q>=1+DEG1<=Q',round(c,3),[t for t in sup if t[0]>0.3][:7],flush=True)
