import sys
exec(open('qb1.py').read().split("if __name__")[0])
def dualfeas(k,obj_sign):
    ells=list(range(3,k+1)); wm=1-(9**s-8**s); nl=len(ells)
    P=tuple([2]*(k//2)+[1]*(k%2)); vh=val(k,P); m=k%2
    cols=[(D,tuple([1]*D)) for D in range(1,k+1)]+[(D,(D,)) for D in range(1,k+1)]+[(D,tuple([2]*(D//2)+[1]*(D%2))) for D in range(2,k+1)]
    cols=list(dict.fromkeys(cols))
    Tv=None
    for it in range(400):
        # vars w_l>=0 ; constraints: for each col: v-1+wm*m + w.rho <=0 ; hub equality: v_hub-1+wm*m_h + w.rho_h = 0 ; minimize obj
        A=np.array([rows(k,D,Pc,ells)[1:] for D,Pc in cols]); mm=np.array([rows(k,D,Pc,ells)[0] for D,Pc in cols])
        b=np.array([1-val(D,Pc)-wm*mm_ for (D,Pc),mm_ in zip(cols,mm)])
        ah=rows(k,k,P,ells)[1:]; bh=1-vh-wm*m
        c=np.array(ells,float)*obj_sign
        r=linprog(c,A_ub=A,b_ub=b,A_eq=ah[None,:],b_eq=[bh],bounds=(0,None),method='highs')
        if r.status!=0: return None
        w=np.r_[wm,r.x]
        pr=price(k,w,0,ells,1,k,0)
        viol=[(sc-1,D,Pc) for sc,D,Pc in pr if sc-1>1e-12 and (D,Pc) not in cols]
        if not viol: return r.x,ells,max(sc-1 for sc,_,_ in pr)
        cols+=[(D,Pc) for _,D,Pc in sorted(viol,reverse=True)[:10]]
    return None
k=int(sys.argv[1])
for sg in (1,-1):
    out=dualfeas(k,sg)
    if out is None: print('infeasible/no conv'); continue
    x,ells,mx=out; print('sign',sg,'maxPhi',mx,'support',{l:round(v,6) for l,v in zip(ells,x) if v>1e-9})
