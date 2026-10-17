# K9 (graphic) embedding test of served sets: exists 36 distinct lines h_ab (a<b in 9) with star h_1k independent and every triangle rank 2?
import numpy as np, itertools, sys
L=[tuple(map(int,l.split()[1:])) for l in open('lines.txt')]
pos={}
for t,v in enumerate(L): pos[v]=t; pos[tuple(-x for x in v)]=t
def refl(v,w):
    d=sum(a*b for a,b in zip(w,v))//4
    return tuple(a-d*b for a,b in zip(w,v))
gv=list(L)
s=[t for t in range(1,120) if sum(a*b for a,b in zip(L[0],L[t]))==0][0]
h0=tuple(a+b for a,b in zip(L[0],L[s]))
key=lambda x: max(x,tuple(-a for a in x))
seen={key(h0):h0}; fr=[h0]
while fr:
    nf=[]
    for h in fr:
        for v in gv:
            h2=refl(v,h); k=key(h2)
            if k in seen: continue
            seen[k]=h2; nf.append(h2)
    fr=nf
D7=list(seen.values()); assert len(D7)==1080   # same insertion order as mk.py orbit()
def vec(tok): return np.array(L[int(tok[1:])] if tok[0]=='r' else D7[int(tok[1:])])
cache={}
def dep3(x,y,z,V):
    k=tuple(sorted((x,y,z)))
    if k not in cache: cache[k]=np.linalg.matrix_rank(np.array([V[x],V[y],V[z]]))==2
    return cache[k]
def has_k9(toks):
    V={t:vec(t) for t in toks}; S=list(toks)
    # parallel elements impossible (distinct lines)
    dep={}
    for x,y in itertools.combinations(S,2):
        dep[(x,y)]=dep[(y,x)]=[z for z in S if z!=x and z!=y and dep3(x,y,z,V)]
    def indep(st): return np.linalg.matrix_rank(np.array([V[t] for t in st]))==len(st)
    def stars(st,start):
        if len(st)==8: yield list(st); return
        for i in range(start,len(S)):
            x=S[i]
            if all(dep[(x,y)] for y in st) and indep(st+[x]):
                yield from stars(st+[x],i+1)
    for st in stars([],0):
        pairs=list(itertools.combinations(range(8),2))
        assign={}
        used=set(st)
        def rec(i):
            if i==len(pairs): return True
            j,k=pairs[i]
            for z in dep[(st[j],st[k])]:
                if z in used: continue
                # triangle consistency with already-assigned pairs sharing a vertex
                ok=True
                for l in range(8):
                    if l in (j,k): continue
                    a=assign.get((min(j,l),max(j,l))); b=assign.get((min(k,l),max(k,l)))
                    if a is not None and b is not None and not dep3(z,a,b,V): ok=False;break
                if not ok: continue
                assign[(j,k)]=z; used.add(z)
                if rec(i+1): return True
                del assign[(j,k)]; used.discard(z)
            return False
        if rec(0): return True
    return False
if __name__=="__main__":
    sets={}
    for line in open(sys.argv[1]):
        p=line.split(); toks=tuple(sorted(p[p.index('S')+1:])); sets.setdefault(toks,[]).append(p[1:3])
    print('distinct served sets',len(sets),file=sys.stderr)
    nk=0
    for toks,es in sets.items():
        r=has_k9(toks)
        if r: nk+=1; print('K9 EMBEDS',len(toks),es[:3])
    print('sets with K9 embedding:',nk,'of',len(sets))
