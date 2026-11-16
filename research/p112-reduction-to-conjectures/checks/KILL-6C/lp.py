from scipy.optimize import linprog
from math import comb
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:64}; N={1:1,2:3,3:6,4:12,5:20,6:36,7:63}
rows={303:[6]*10+[5,5],315:[7,7,7,6,6,6,6,6,5,5,5,4],400:[6]*10+[5,4,1,1],401:[6]*10+[5,4,2],402:[6]*10+[5,5,1],409:[6]*11+[5],411:[7]+[6]*9+[5,5],417:[7,7]+[6]*7+[5,5,5],425:[7,7,7]+[6]*5+[5]*4}
for r,ws in rows.items():
    p=len(ws); M=p  # x_m m=1..p
    c=[m for m in range(1,p+1)]
    A=[];b=[]
    for k in range(1,8):
        A.append([comb(p-m,k-m) if m<=k else 0 for m in range(1,p+1)]); b.append(comb(p,k)*N[k])
    res=linprog(c,A_ub=A,b_ub=b,A_eq=[[1]*p],b_eq=[120],bounds=[(0,None)]*p)
    print(r,p,sum(g[w] for w in ws),round(res.fun,2))
