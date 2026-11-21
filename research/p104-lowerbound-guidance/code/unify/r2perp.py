# UNIFY: the R2TEST run read as a ⊥-NetW (owned ascent = node a=c^⊥,b=c'^⊥; owned descent = relay). Exact, own code.
import sys; sys.path.insert(0,'../netattr')
from common import *
from zz_level import levelsum_nodes
h=4; labs=[1,2,7,11,13]; n=5
def sp(*v): return span(list(v))
P=lambda S: perp(S,h)
c1,c1p=sp(13),sp(1,12); c2,c2p=sp(12),sp(7,12)
j=(P(c1),P(c1p)); k=(P(c2),P(c2p))
print('dims a,b j',dimof(j[0]),dimof(j[1]),'k',dimof(k[0]),dimof(k[1]))
print('relay legal b_j<=a_k:',j[1]<=k[0],' slack e=',dimof(k[0])-dimof(j[1]),' owned descent cost',dimof(c1p)-dimof(c2))
# gathers = intake ports (content y_s needs q_s in a = c^⊥, i.e. cold), deposits = reader ports (q_t ⊥ b, i.e. q_t in c')
L={x:i for i,x in enumerate(labs)}
for nm,(a,b),ins,outs in (('j',j,[7,11],[1]),('k',k,[1,2],[7,11])):
    print(nm,'intakes cold:',all(q in a for q in ins),' readers legal:',all(all(dot(q,y)==0 for y in b) for q in outs))
# Rec rows (port order 1,2,7,11,13 = y0..y4? R2: t0:y2+y3, t2:y0+y1+y2, t3:y0+y1+y3) -> j: y2,y3 -> X0; k: y0,y1 (+relayed j) -> X2,X3
F=[[0]*n for _ in range(2)]; G=[[0]*2 for _ in range(n)]
F[0][2]=F[0][3]=1; F[1][0]=F[1][1]=1; G[0][0]=1; G[2][1]=G[3][1]=1; H=[[0,0],[1,0]]
from netgen import net_M
M,N=net_M(G,H,F); Qm=[[dot(s,t) for t in labs] for s in labs]
print('odd pattern rows:',[[M[t][p]*Qm[t][p] for p in range(n)] for t in range(n)])
print('D_perp=',sum(dimof(a)-dimof(b) for a,b in (j,k)),' level sum=',levelsum_nodes(h,[j,k],F,G,N))
