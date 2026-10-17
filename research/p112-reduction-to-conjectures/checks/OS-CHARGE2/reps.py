# orbit reps of all Off(h) sets (h = r or r+s, norm 2,4,6, and f) under signs x Aut(Hamming); dump with size + type
import json, itertools, numpy as np
D=json.load(open('data.json')); FC=np.array(D['FC']); L=np.array(D['L']); E8=np.array(D['E8'])
v=len(L)
allr=list(E8)+[-r for r in E8]
dirs={}
def off(h): return sum(1<<t for t in range(v) if abs(L[t]@h)>1e-9)
for f in D['F0']: dirs.setdefault(off(np.array(f)),'f')
for r in E8:
    dirs.setdefault(off(r),'root')
for a,b in itertools.combinations(range(len(allr)),2):
    s=allr[a]+allr[b]; nn=round(s@s)
    if nn in (4,6): dirs.setdefault(off(s),'n%d'%nn)
supp=set(tuple(np.nonzero(row)[0]) for row in FC)
code=set(frozenset(s) for s in supp)
perms=[p for p in itertools.permutations(range(8)) if all(frozenset(p[i] for i in s) in code for s in code)]
key={tuple(np.round(FC[t]).astype(int)):t for t in range(v)}
def act(p,sg,t):
    x=np.zeros(8)
    for i in range(8): x[p[i]]=FC[t][i]*sg[i]
    k=tuple(np.round(x).astype(int)); km=tuple(-a for a in k)
    return key.get(k,key.get(km))
G=[[act(p,[1]*8,t) for t in range(v)] for p in perms]
for i in range(8):
    sg=[1]*8; sg[i]=-1; G.append([act(tuple(range(8)),sg,t) for t in range(v)])
def img(g,T):
    out=0; y=T
    while y:
        t=(y&-y).bit_length()-1; y&=y-1; out|=1<<g[t]
    return out
seen=set(); reps=[]
for T in sorted(dirs,key=lambda T:(bin(T).count('1'),T)):
    if T in seen: continue
    orb={T}; st=[T]
    while st:
        x=st.pop()
        for g in G:
            y=img(g,x)
            if y not in orb: orb.add(y); st.append(y)
    seen|=orb; reps.append((T,dirs[T],len(orb)))
with open('reps.txt','w') as fo:
    for T,ty,n in reps:
        print(bin(T).count('1'),ty,n,format(T,'x'),file=fo); print(bin(T).count('1'),ty,n)
# also generator perms for C
with open('gens.txt','w') as fo:
    for g in G: print(*g,file=fo)
print(len(G),'group elements listed (perms+signflips)')
