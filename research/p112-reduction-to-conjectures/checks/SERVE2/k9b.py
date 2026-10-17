# SERVE2 independent K9/K8 graphic test: exists star of n-1 independent served vectors e_k and, for each pair a<b, a served vector with coordinate support exactly {a,b}
# (star basis coordinates), such that every triple a,b,c of pair-vectors is coplanar (3x3 det 0 on coords a,b,c).  n=9 -> K9, n=8 -> K8.
import numpy as np, itertools, sys, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import setup2 as S
V0=[np.array(v,float) for v in S.L]; V1=[np.array(v,float) for v in S.D]
def vec(tok): return V0[int(tok[1:])] if tok[0]=='r' else V1[int(tok[1:])]
def graphic(toks,n):
    m=n-1
    T=[vec(t) for t in toks]; N=len(T)
    M=np.array(T)
    def rank(idx): return np.linalg.matrix_rank(M[list(idx)],tol=1e-9)
    plane={}
    def third(x,y):
        k=(x,y)
        if k not in plane:
            r=[z for z in range(N) if z!=x and z!=y and np.linalg.matrix_rank(M[[x,y,z]],tol=1e-9)==2]
            plane[(x,y)]=plane[(y,x)]=r
        return plane[k]
    def stars(st,start):
        if len(st)==m: yield list(st); return
        for i in range(start,N):
            if all(third(i,j) for j in st) and rank(st+[i])==len(st)+1:
                yield from stars(st+[i],i+1)
    for st in stars([],0):
        B=M[st].T                      # 8 x m, columns star vectors
        Cf=np.linalg.lstsq(B,M.T,rcond=None)[0].T   # N x m coordinates
        ok=np.abs(B@Cf.T-M.T).max()<1e-8
        supp=[tuple(np.nonzero(np.abs(Cf[z])>1e-8)[0]) if np.abs(B@Cf[z]-M[z]).max()<1e-8 else None for z in range(N)]
        cand={(a,b):[z for z in range(N) if supp[z]==(a,b)] for a,b in itertools.combinations(range(m),2)}
        if any(not c for c in cand.values()): continue
        pairs=list(cand); asg={}
        def rec(i):
            if i==len(pairs): return True
            a,b=pairs[i]
            for z in cand[(a,b)]:
                good=True
                for c in range(m):
                    if c in (a,b): continue
                    p=asg.get(tuple(sorted((a,c)))); q=asg.get(tuple(sorted((b,c))))
                    if p is None or q is None: continue
                    mat=np.array([Cf[z][[a,b,c]],Cf[p][[a,b,c]],Cf[q][[a,b,c]]])
                    if abs(np.linalg.det(mat))>1e-8: good=False;break
                if good:
                    asg[(a,b)]=z
                    if rec(i+1): return True
                    del asg[(a,b)]
            return False
        if rec(0): return True
    return False
def parse(fn):
    sets={}
    for line in open(fn):
        if ' S ' in line or line.startswith('S'):
            p=line.split(); toks=tuple(sorted(p[p.index('S')+1:])); sets.setdefault(toks,0); sets[toks]+=1
    return sets
if __name__=="__main__":
    n=int(sys.argv[1])
    if sys.argv[2]=='ctl':
        # A_{n-1} subsystem: vectors e_i - e_j (i<j<=n) in E8 coordinates, doubled: 2e_i-2e_j.  find line indices
        L=S.L; ip=lambda u,v: int(np.dot(u,v))//4
        def dfs(path):
            if len(path)==n-1: return path
            for v in L:
                for w in (v,-v):
                    if ip(path[-1],w)==-1 and all(ip(p,w)==0 for p in path[:-1]):
                        r=dfs(path+[w])
                        if r: return r
            return None
        chain=dfs([L[0]]); assert chain
        toks=[]
        for i,j in itertools.combinations(range(n),2):
            v=sum(chain[i:j]); toks.append('r%d'%[t for t in range(120) if (S.L[t]==v).all() or (S.L[t]==-v).all()][0])
        print('A%d control graphic K%d:'%(n-1,n),graphic(toks,n))
    else:
        sets=parse(sys.argv[2]); print('distinct served sets',len(sets)); nk=0
        for i,t in enumerate(sets):
            if graphic(t,n): nk+=1; print('GRAPHIC',len(t))
        print('sets with K%d: %d of %d'%(n,nk,len(sets)))
