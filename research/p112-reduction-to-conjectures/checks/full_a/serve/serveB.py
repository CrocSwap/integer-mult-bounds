# SERVE impl B (python/numpy): independent recomputation of served(E) with NO leftover tables / W-transport.
# E8 rebuilt from Cartan matrix; lines identified with impl A's line numbering via doubled coords + Bourbaki simple roots.
# served(E) = #roots in E + #roots r not in E with Off(r)\E inside a union of two 7-flats + #norm-4 vectors h (|Off|=78) with Off(h)\E inside such a union.
import numpy as np, sys
L=[tuple(map(int,l.split()[1:])) for l in open('lines.txt')]
S=np.array([[1,-1,-1,-1,-1,-1,-1,1],[2,2,0,0,0,0,0,0],[-2,2,0,0,0,0,0,0],[0,-2,2,0,0,0,0,0],[0,0,-2,2,0,0,0,0],[0,0,0,-2,2,0,0,0],[0,0,0,0,-2,2,0,0],[0,0,0,0,0,-2,2,0]])
C=np.rint(np.linalg.solve(S.T.astype(float),np.array(L).T.astype(float)).T).astype(int)   # root coefficient vectors (own labels from these)
G=S@S.T//4*0+ (S@S.T)//4        # Cartan-ish Gram: (alpha_i,alpha_j) (norm 2 -> diag 2)
assert (np.diag(G)==2).all()
IP=C@G@C.T                       # inner products of the 120 lines
lab=np.array([1|sum(int(C[t][k]%2)<<(k+1) for k in range(8)) for t in range(120)])
par=lambda a: np.array([bin(a&int(l)).count('1')&1==0 for l in lab])
Z=[par(a) for a in range(512)]   # Z[0] all True (a=0 means no condition): skip a=0 pairs? (flat = 2 independent hyperplanes)
# norm-4 vectors up to sign: sums of orthogonal pairs
d7=set()
for i in range(120):
    for j in range(i+1,120):
        if IP[i,j]==0:
            for sg in (1,-1):
                v=C[i]+sg*C[j]; d7.add(min(tuple(v),tuple(-v)))
d7=[np.array(v) for v in d7]; assert len(d7)==1080
def offmask(v):  # boolean over lines, <line,v> != 0
    return (C@G@v)!=0
# covering test: R inside X u Y, X,Y 7-flats  <=>  R splits into two parts each of label F2-rank <=7 (flat = lines with label in a 7-dim subspace)
def _red(b,x):
    for y in b: x=min(x,x^y)
    return x
def covered(R):
    R=[int(lab[t]) for t in range(120) if R[t]]
    def rec(i,bx,by):
        while i<len(R):
            x=R[i]
            if _red(bx,x)==0 or _red(by,x)==0: i+=1; continue
            if len(bx)<7:
                nb=bx+[_red(bx,x)]
                if rec(i+1,nb,by): return True
            if len(by)<7 and (len(by)>0 or len(bx)>0):   # symmetry break: first branching line goes to X
                nb=by+[_red(by,x)]
                if rec(i+1,bx,nb): return True
            return False
        return True
    return rec(0,[],[])
def served(E):
    Eb=np.zeros(120,bool); Eb[list(E)]=True
    n=int(Eb.sum())
    for r in range(120):
        if Eb[r]: continue
        if covered((IP[r]!=0)&~Eb): n+=1
    for h in d7:
        if covered(offmask(h)&~Eb): n+=1
    return n
if __name__=="__main__":
    for line in sys.stdin:
        E=list(map(int,line.split()))
        if E: print(served(E),flush=True)
