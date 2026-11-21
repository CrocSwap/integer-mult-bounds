import sys
sys.path.insert(0,'../netattr')
from fractions import Fraction as Fr
from common import *
def rankQ(M):
    M=[[Fr(x) for x in r] for r in M]; r=0
    for c in range(len(M[0]) if M else 0):
        p=next((i for i in range(r,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        for i in range(len(M)):
            if i!=r and M[i][c]!=0:
                f=M[i][c]/M[r][c]; M[i]=[x-f*y for x,y in zip(M[i],M[r])]
        r+=1
    return r
def levelsum(h,nodes,F,G,N):
    n=len(G); tot=0
    for l in range(1,h+1):
        Ml=[[0]*n for _ in range(n)]
        for g,(a,_) in enumerate(nodes):
            if dimof(a)<l: continue
            for d,(_,b) in enumerate(nodes):
                if dimof(b)>=l or N[d][g]==0: continue
                for t in range(n):
                    if G[t][d]:
                        for p in range(n): Ml[t][p]+=G[t][d]*N[d][g]*F[g][p]
        tot+=rankQ(Ml)
    return tot
levelsum_nodes=levelsum
