from lib import *
def apply(rows,e):
    if e[0]=='add':
        _,t,s,a,b,*_=e;q=Q(a,b);rt=rows[t]
        for j,x in list(rows[s].items()):
            z=rt.get(j,0)+q*x
            if z:rt[j]=z
            else:rt.pop(j,None)
    else:
        _,t,a,b,*_=e;q=Q(a,b);rows[t]={j:q*x for j,x in rows[t].items()}
def init(): return [{i:Q(1)} if i<112 else {} for i in range(716)]
