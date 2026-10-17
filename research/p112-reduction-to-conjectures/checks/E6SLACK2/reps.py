import sys,pickle
from sympy.combinatorics import Permutation, PermutationGroup
cand,out=sys.argv[1],sys.argv[2]
gens,Tidx,A2,E6=pickle.load(open('grp.pkl','rb'))
pos={t:i for i,t in enumerate(Tidx)}
G=PermutationGroup([Permutation(p) for p in gens])
p0line=A2[0]; S=G.stabilizer(p0line); print('stab order',S.order(),flush=True)
sg=[[pos[g(t)] for t in Tidx] for g in S.generators]   # perms on T indices
p0=pos[p0line]
byw={}; 
for ln in open(cand):
    w,hi,lo=map(int,ln.split()); m=(hi<<64)|lo
    byw.setdefault(w,[]).append(m)
def ap(m,s):
    r=0
    for i in range(84):
        if m>>i&1: r|=1<<s[i]
    return r
res=[]
for w,L in byw.items():
    ix={m:i for i,m in enumerate(L)}; par={}
    def f(x):
        while par.get(x,x)!=x:
            par[x]=par.get(par[x],par[x]); x=par[x]
        return x
    sel=[i for i,m in enumerate(L) if m>>p0&1]
    for i in sel:
        for s in sg:
            j=ix[ap(L[i],s)]
            a,b=f(i),f(j)
            if a!=b: par[a]=b
    reps=sorted({f(i) for i in sel}); print('w',w,'containing p0',len(sel),'orbit reps',len(reps),flush=True)
    res+=[(w,i) for i in reps]
with open(out,'w') as o:
    o.write("%d\n"%p0)
    for w,i in res: o.write("%d %d\n"%(w,i))
