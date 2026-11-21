# QBRANCH qb9: full-enumeration Q>=1 reduced LP (all partitions, D=1..k, parts<=D) k small, float; compare to chart
import sys
exec(open('qb7.py').read().split("if __name__")[0])
def parts(n,m=None):
    m=m or n
    if n==0: yield (); return
    for i in range(min(n,m),0,-1):
        for r in parts(n-i,i): yield (i,)+r
for k in map(int,sys.argv[1:]):
    ells=list(range(3,k+1)); cols=[(D,P) for D in range(1,k+1) for P in parts(D)]
    A=np.array([rows_f(k,D,P,ells) for D,P in cols]).T; c=-np.array([val_f(D,P)-1 for D,P in cols])
    rhs=np.array([2*k]*(1+len(ells)),float)
    r=linprog(c,A_ub=np.vstack([-A,-np.ones((1,len(cols)))]),b_ub=np.r_[-rhs,-(2*k-1)],method='highs')
    print(k,len(cols),'LP',(-r.fun+2*k-2)*104/k,'chart',float(chart(k)[0]),[(round(x,3),D,P) for x,(D,P) in zip(r.x,cols) if x>1e-7][:6],flush=True)
