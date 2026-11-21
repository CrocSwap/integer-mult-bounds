import sys
exec(open('qb7.py').read().split("if __name__")[0])
k=int(sys.argv[1]); ells=list(range(3,k+1)); wm=1-(9**sf-8**sf)
a=k%2;b=k//2; Ph=tuple([2]*b+[1]*a)
cols=[(D,tuple([1]*D)) for D in range(1,k+1)]+[(D,(D,)) for D in range(1,k+1)]+[(D,tuple([2]*(D//2)+[1]*(D%2))) for D in range(2,k+1)]
cols=list(dict.fromkeys(cols))
for it in range(500):
    R=[rows_f(k,D,Pc,ells) for D,Pc in cols]
    A=np.array([r[1:] for r in R]); b_=np.array([1-val_f(D,Pc)-wm*r[0] for (D,Pc),r in zip(cols,R)])
    rh=rows_f(k,k,Ph,ells)
    r=linprog(np.array(ells,float)*-1,A_ub=A,b_ub=b_,A_eq=rh[1:][None,:],b_eq=[1-val_f(k,Ph)-wm*rh[0]],bounds=(0,None),method='highs')
    if r.status!=0: print('status',r.status,r.message,'iter',it); break
    w=np.r_[wm,r.x]; pr=price_f(k,w,ells)
    viol=sorted([(sc,D,Pc) for sc,D,Pc in pr if sc>1e-13 and (D,Pc) not in cols],reverse=True)
    print(it,len(cols),'maxviol',viol[0] if viol else None,flush=True)
    if not viol: break
    cols+=[(D,Pc) for _,D,Pc in viol[:10]]
