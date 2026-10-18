import gzip,json,itertools,collections
w=json.loads(gzip.decompress(open(__import__('os').environ['EO_ROOT']+'/inputs/words/w1018.json.gz','rb').read()))
P=w['ports'];R=w['root_lines'];V=112
dot=lambda a,b:bin(a&b).count('1')&1
ip=lambda a,b:sum(x*y for x,y in zip(a,b))
SG=[[(ip(R[t],R[s])//2) for s in range(V)] for t in range(V)]  # ±1 or 0 off-diag
def rank(vs):
    b=[]
    for v in vs:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return len(b)
S=set(P); idx={p:i for i,p in enumerate(P)}
def common(T): return [s for s in range(V) if s not in T and all(SG[t][s]!=0 for t in T)]
def r1classes(T):
    cs=collections.Counter()
    for s in common(T):
        col=tuple(SG[t][s] for t in T)
        if col[0]<0: col=tuple(-c for c in col)
        cs[col]+=1
    return cs
blk=lambda i:i//8
def report(name,groups):
    st=collections.Counter()
    for T in groups:
        cs=r1classes(T); st[(len(common(T)),max(cs.values()) if cs else 0,len(cs))]+=1
    print(name,len(groups),'(|S_T|,max rank1 class,#classes):',sorted(st.items()))
pairs=list(itertools.combinations(range(V),2))
report('pairs dot0 same-block',[p for p in pairs if blk(p[0])==blk(p[1]) and dot(P[p[0]],P[p[1]])==0])
report('pairs dot1 same-block',[p for p in pairs if blk(p[0])==blk(p[1]) and dot(P[p[0]],P[p[1]])==1])
report('pairs dot0 cross',[p for p in pairs if blk(p[0])!=blk(p[1]) and dot(P[p[0]],P[p[1]])==0])
report('pairs dot1 cross',[p for p in pairs if blk(p[0])!=blk(p[1]) and dot(P[p[0]],P[p[1]])==1])
quads=[]
for a,b,c in itertools.combinations(range(V),3):
    d=P[a]^P[b]^P[c]
    if d in S and idx[d]>c: quads.append((a,b,c,idx[d]))
bp=lambda q:tuple(sorted(collections.Counter(blk(i) for i in q).values()))
for pat in [(4,),(2,2),(1,1,2),(1,1,1,1)]:
    report('quads blocks%s'%(pat,),[q for q in quads if bp(q)==pat])
# 8-port dim-4 groups
oct8=[]
