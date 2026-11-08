# Find an ordering of chain-nested root units with product = -I (exact rationals).
import sys, itertools
from fractions import Fraction as Q
def thin_vectors(gL,gR,n,fL,fR,A,E):
    sL,sR=gL%2,gR%2
    def vec(a,u,p=0,q=0):
        x=[Q(0)]*n;y=[Q(0)]*n
        x[A]=Q(a);y[A]=Q(u)
        for i,f in enumerate(fL): x[f]=Q(a+1);y[f]=Q((1-u)*(-1)**i)
        for r,h in enumerate(reversed(fR)): x[h]=Q(1-a);y[h]=Q((u-1)*(-1)**r)
        if E is not None: x[E]=Q(q);y[E]=Q(p)
        return x,y
    if sL==sR==1: return [vec(0,1,0,1),vec(-1,2,1,0),vec(-1,3,1,-1)]
    if sL==sR==0: return [vec(0,1,0,1),vec(-1,0,1,0),vec(-1,-1,1,-1)]
    if sL==1: return [vec(0,1),vec(-1,0)]
    return [vec(0,1),vec(1,2)]
def mm(A,B):
    Bt=list(zip(*B)); return [[sum(a*b for a,b in zip(r,c)) for c in Bt] for r in A]
def units(gL,gR):
    nf=1+gL+gR;e=nf%2;n=nf+e;A=0
    fL=list(range(1,1+gL));fR=list(range(1+gL,1+gL+gR));E=nf if e else None
    Ls=[];Rs=[]
    for i in range(gL):
        x=[Q(0)]*n;y=[Q(0)]*n
        x[A]=Q(1);y[A]=Q(1);x[fL[i]]=Q(1);y[fL[i]]=Q(-1)
        for j in range(i): x[fL[j]]=Q(2)
        Ls.append((x,y,{A}|set(fL[:i+1])))
    for m in range(gR):
        x=[Q(0)]*n;y=[Q(0)]*n
        x[A]=Q(-1);y[A]=Q(1);x[fR[m]]=Q(1);y[fR[m]]=Q(1)
        for l in range(m+1,gR): x[fR[l]]=Q(2)
        Rs.append((x,y,{A}|set(fR[m:])))
    th=[(x,y,None) for x,y in thin_vectors(gL,gR,n,fL,fR,A,E)]
    return n,Ls,Rs,th
def T(x,y,c):
    n=len(x);return [[Q(int(i==j))-c*x[i]*y[j] for j in range(n)] for i in range(n)]
def search(gL,gR):
    n,Ls,Rs,th=units(gL,gR)
    N=len(Ls)+len(Rs)+len(th)
    sols=[]
    for pos in itertools.combinations(range(N),len(th)):
        for perm in itertools.permutations(range(len(th))):
            seq=[];li=iter(Ls+Rs);ti=iter(perm)
            for k in range(N):
                seq.append(th[next(ti)] if k in pos else next(li))
            for c in (Q(2),Q(1)):
                P=[[Q(int(i==j)) for j in range(n)] for i in range(n)]
                for (x,y,m) in seq: P=mm(T(x,y,c),P)
                if all(P[i][j]==(-1 if i==j else 0) for i in range(n) for j in range(n)):
                    sols.append((pos,perm,c))
    return sols
if __name__=="__main__":
    for g in [(1,1),(2,2)]:
        s=search(*g);print(g,len(s),s[:4])
