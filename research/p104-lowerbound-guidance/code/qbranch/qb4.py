import sys
exec(open('qb1.py').read().split("if __name__")[0])
def duals(k):
    # re-run solve capturing duals
    ells=list(range(3,k+1)); Dmin=1; Lmax=k; n=2*k-1
    rhs=np.array([2*k]*(1+len(ells)),float)
    cols=[(D,tuple([1]*D)) for D in range(1,k+1)]+[(2,(2,)),(k,tuple([2]*(k//2)+[1]*(k%2)))]
    cols=list(dict.fromkeys(cols))
    for it in range(300):
        c=-np.array([val(D,P)-1 for D,P in cols]);A=np.array([rows(k,D,P,ells) for D,P in cols]).T
        r=linprog(c,A_ub=np.vstack([-A,-np.ones((1,len(cols)))]),b_ub=np.r_[-rhs,-n],method='highs')
        w=-r.ineqlin.marginals[:len(rhs)]; lam=-r.ineqlin.marginals[-1]
        pr=price(k,w,0,ells,1,k,0)
        new=[(sc-1-lam,D,P) for sc,D,P in pr if sc-1-lam>1e-9 and (D,P) not in cols]
        if not new: break
        cols+=[(D,P) for _,D,P in sorted(new,reverse=True)[:12]]
    return w,lam,r,cols
k=int(sys.argv[1]); w,lam,r,cols=duals(k)
print('k',k,'F*104/k',(-r.fun+2*k-2)*104/k,'count mult',lam,'wm',w[0]); print('w_l',np.round(w[1:],6)); print('sum w',w[1:].sum())
