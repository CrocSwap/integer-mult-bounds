# LOWD residual clique test (see clique.py). Usage: clique2.py KMIN  -> per Ic (|Ic|<=3): max clique size, # cliques >= KMIN passing the joint test
import sys, json, itertools, pickle, numpy as np
import sympy as sp
D=json.load(open('data.json')); LAB=D['LAB']; FC=np.array(D['FC'],dtype=np.int64); v=112
par=lambda x: bin(x).count('1')&1
O={z:set(t for t in range(v) if par(z&LAB[t])) for z in range(1,512)}
compat,null=pickle.load(open('null.pkl','rb'))
KMIN=int(sys.argv[1]); ICS=sys.argv[2] if len(sys.argv)>2 else 'all'
def theta(z,z2): return sorted(O[z]&O[z2])
def rank(M): return np.linalg.matrix_rank(np.array(M,dtype=float)) if len(M) else 0
def edge(i,z,i2,z2,S):
    key=(min(z,z2),max(z,z2))
    if key not in null: return False
    N=null[key]
    if N=='ALL': return True
    # subspace of span(N) supported in S
    Nm=np.array(N).T  # 8 x d
    out=[c for c in range(8) if c not in S]
    A=sp.Matrix(Nm[out,:].tolist()) if out else sp.zeros(0,Nm.shape[1])
    ker=A.nullspace() if out else [sp.eye(Nm.shape[1])[:,k] for k in range(Nm.shape[1])]
    if not ker: return False
    H=[sp.Matrix(Nm.tolist())*k for k in ker]
    return any(h[i]!=0 for h in H) and any(h[i2]!=0 for h in H)
def joint(cl,Ic):
    # unknowns: for each (i,z) in cl, eta on coords [i]+Ic
    coords=[[i]+list(Ic) for i,z in cl]; off=[0]
    for c in coords: off.append(off[-1]+len(c))
    rows=[]
    for a in range(len(cl)):
        for b in range(a+1,len(cl)):
            for t in theta(cl[a][1],cl[b][1]):
                r=[0]*off[-1]
                for k,c in enumerate(coords[a]): r[off[a]+k]+=int(FC[t][c])
                for k,c in enumerate(coords[b]): r[off[b]+k]-=int(FC[t][c])
                rows.append(r)
    M=sp.Matrix(rows) if rows else sp.zeros(1,off[-1])
    ker=M.nullspace()
    if not ker: return False
    return all(any(k[off[a]]!=0 for k in ker) for a in range(len(cl)))
Ics=[c for r in range(4) for c in itertools.combinations(range(8),r)]
if ICS!='all': Ics=[tuple(map(int,x.split(','))) if x else () for x in ICS.split(';')]
for Ic in Ics:
    I=[i for i in range(8) if i not in Ic]
    V=[(i,z) for i in I for z in compat[i]]
    adj={x:set() for x in V}
    for a in range(len(V)):
        i,z=V[a]
        for b in range(a+1,len(V)):
            i2,z2=V[b]
            if i2==i or z2==z: continue
            if edge(i,z,i2,z2,set([i,i2])|set(Ic)): adj[V[a]].add(V[b]); adj[V[b]].add(V[a])
    ne=sum(len(s) for s in adj.values())//2
    # cliques with distinct i: DFS over vertices sorted by i
    best=[0]; found=[]
    def dfs(cl,cands):
        if len(cl)>best[0]: best[0]=len(cl)
        if len(cl)>=KMIN:
            if joint(cl,Ic): found.append(list(cl))
        for x in sorted(cands):
            nc={y for y in cands&adj[x] if y[0]>x[0]}
            # bound: distinct i remaining
            if len(cl)+1+len({y[0] for y in nc})<KMIN: continue
            dfs(cl+[x],nc)
    dfs([],set(V))
    print('Ic',Ic,'vertices',len(V),'edges',ne,'max clique(distinct i)',best[0],'cliques>=%d passing joint'%KMIN,len(found),flush=True)
    if found: pickle.dump(found,open('found_%s.pkl'%('_'.join(map(str,Ic)) or 'none'),'wb'))
