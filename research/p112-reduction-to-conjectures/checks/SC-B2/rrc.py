import csv,ast,itertools
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:64}
N={1:1,2:3,3:6,4:12,5:20,6:36,7:63,8:120}
def rrc(comp,j,maxsub=200000):
    """relative root counting: returns (best family size, N_j). comp = tuple of weights (indexed pieces)."""
    m=len(comp); cap=lambda S:sum(g[comp[i]] for i in S)
    allidx=range(m); fam=[]
    cnt=0
    for M in itertools.combinations(allidx,j-1):
        rest=[i for i in allidx if i not in M]
        c=cap(rest)
        if c<57: return 'IMM',N[j]      # a (j-1)-subset whose complement can't carry a root => dead (j-dim space)
        if c<=77: fam.append(frozenset(rest))
        cnt+=1
        if cnt>maxsub: break
    fam.sort(key=lambda s:cap(s))
    ch=[]
    for f in fam:
        if all(cap(f&o)<=56 for o in ch): ch.append(f)
    return len(ch),N[j]
def dead_rrc(comp,jmax=4):
    comp=tuple(sorted(comp,reverse=True))
    for j in range(2,jmax+1):
        r=rrc(comp,j)
        if r[0]=='IMM' or r[0]>r[1]: return j,r
    return None
if __name__=='__main__':
    rs=list(csv.DictReader(open('../SC-B/residue.csv')))
    for r in rs:
        ws=sorted(ast.literal_eval(r['weights']),reverse=True); d=int(r['d']); s=sum(ws)-8*d
        out=[]
        for j in range(2,5):
            comp=ws[d-j:]
            out.append((j,rrc(tuple(comp),j)))
        print(d,s,ws[-9:],out)
