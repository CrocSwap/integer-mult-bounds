# Exact cost_w(T) for T = {(C'h)|_Y}, Y = lines of a label 7-flat with 36 lines (PAYS §4 danger family for the Swap Conjecture).
# cost_w = sum_w w*(dim V_w - dim V_{w-1}), V_w = span{ T_F : F flat of M|Y, rank F <= w }, T_F = {h : (Ch)(t)=0 for t in Y\F}  (greedy/matroid exact).
import sys, itertools
from lib import *
import sympy as sp
def closure_lines(lines,Ylines):
    labs=[LAB[t] for t in lines]
    basis=[]
    for v in labs:
        for b in basis: v=min(v,v^b)
        if v: basis.append(v)
    def inspan(x):
        for b in basis: x=min(x,x^b)
        return x==0
    return frozenset(t for t in Ylines if inspan(LAB[t])), len(basis)
def qrank(rows):
    if not rows: return 0
    return sp.Matrix(rows).rank()
def kernel(rows):
    if not rows: return sp.eye(8)
    ns=sp.Matrix(rows).nullspace()
    return sp.Matrix.hstack(*ns) if ns else sp.zeros(8,0)
def run(Y):
    Y=list(Y)
    flats={}
    frontier=[closure_lines([],Y)]
    seen={frontier[0][0]}
    allf=[frontier[0]]
    while frontier:
        nf=[]
        for F,r in frontier:
            for t in Y:
                if t in F: continue
                G2=closure_lines(list(F)+[t],Y)
                if G2[0] not in seen: seen.add(G2[0]); nf.append(G2); allf.append(G2)
        frontier=nf
    byr={}
    for F,r in allf: byr.setdefault(r,[]).append(F)
    span=sp.zeros(8,0); prev=0; cost=0; prof=[]
    for w in sorted(byr):
        for F in byr[w]:
            rows=[C[t] for t in Y if t not in F]
            K=kernel(rows)
            if K.shape[1]==0: continue
            M=sp.Matrix.hstack(span,K)
            if M.rank()>prev:
                # keep a basis
                cols=[M[:,i] for i in range(M.shape[1])]
                B=[]; 
                for c in cols:
                    if sp.Matrix.hstack(*(B+[c])).rank()>len(B): B.append(c)
                span=sp.Matrix.hstack(*B); 
                cost+=w*(len(B)-prev); prof+= [w]*(len(B)-prev); prev=len(B)
        if prev==8: break
    return cost,prof,len(allf)
if __name__=='__main__':
    # all 7-dim label subspaces containing >=36 lines: enumerate as kernels of 2-dim functional spaces on F2^9
    par=lambda x: bin(x).count('1')&1
    res=set()
    for a in range(1,512):
        for b in range(a+1,512):
            if (a^b)<b: continue
            Yl=frozenset(t for t in range(n) if not par(a&LAB[t]) and not par(b&LAB[t]))
            if len(Yl)>=36: res.add(Yl)
    res=sorted(res,key=lambda s:sorted(s))
    print('7-flats with >=36 lines:',len(res),'sizes',set(len(s) for s in res)); sys.stdout.flush()
    lo,hi=int(sys.argv[1]),int(sys.argv[2])
    for i,Y in enumerate(res[lo:hi],lo):
        swap=[t for t in Y if all(Bd[t][s]==0 for s in Y if s!=t and any(C[s][j]*C[t][j] for j in range(8)) and sum(C[s][j]*C[t][j] for j in range(8))!=0) ]
        c,prof,nfl=run(Y)
        print(i,'|Y|',len(Y),'Q-rank',qrank([C[t] for t in Y]),'exact cost_w',c,prof,'flats',nfl, '***' if c<len(Y) else ''); sys.stdout.flush()
