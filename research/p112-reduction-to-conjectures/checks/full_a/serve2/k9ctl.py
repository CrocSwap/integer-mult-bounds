# positive/negative controls for k9b.graphic (SERVE2 world): A8 subsystem of E8 embeds K9; E6 (roots orthogonal to an A2) does not.
import sys; sys.argv=['x']
import k9b
S=k9b.S; L=S.L
Lt=[tuple(int(x) for x in v) for v in L]; pos={}
for t,v in enumerate(Lt): pos[v]=t; pos[tuple(-x for x in v)]=t
Bm=[(1,-1,-1,-1,-1,-1,-1,1),(2,2,0,0,0,0,0,0),(-2,2,0,0,0,0,0,0),(0,-2,2,0,0,0,0,0),(0,0,-2,2,0,0,0,0),(0,0,0,-2,2,0,0,0),(0,0,0,0,-2,2,0,0),(0,0,0,0,0,-2,2,0)]
th=tuple(sum(c*Bm[i][k] for i,c in enumerate([2,3,4,6,5,4,3,2])) for k in range(8))
rs={Bm[0],Bm[2],Bm[3],Bm[4],Bm[5],Bm[6],Bm[7],tuple(-x for x in th)}; ch=True
while ch:
    ch=False
    for a_ in list(rs):
        for b_ in list(rs):
            d=sum(x*y for x,y in zip(a_,b_))//4; w=tuple(x-d*y for x,y in zip(a_,b_))
            if w not in rs: rs.add(w); ch=True
A8=sorted({pos[r] for r in rs})
a=L[0]; b=[w for w in L if int(a@w)//4==-1 or int(a@(-w))//4==-1][0]
E6=[t for t in range(120) if (L[t]@a)==0 and (L[t]@b)==0]
ra=k9b.graphic(tuple('r%d'%t for t in A8),9); re_=k9b.graphic(tuple('r%d'%t for t in E6),9)
print('A8 lines',len(A8),'E6 lines',len(E6),'A8 graphic',ra,'E6 graphic',re_)
print('CTL-OK' if (len(A8)==36 and len(E6)==36 and ra and not re_) else 'CTL-BAD')
