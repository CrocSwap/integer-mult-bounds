from ls import *
from collections import Counter
def meetings(W2):
    setup(W2); P2=W2['program']; st=stays_of(W2)
    node={}; par=[]
    for r in range(n):
        for k in range(len(st[r])): node[(r,k)]=len(par); par.append(len(par))
    def fd(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    ev2stay={}
    for r in range(n):
        for k,(c,evs,_) in enumerate(st[r]):
            for i in evs: ev2stay[(i,r)]=k
    pinev={}
    for i,e in enumerate(P2):
        if e[0] in ('ADD','COPY'):
            d,s_=e[1],e[2]
            if d<n and s_<n:
                a=fd(node[(d,ev2stay[(i,d)])]); b=fd(node[(s_,ev2stay[(i,s_)])])
                if a!=b: par[a]=b
    for i,e in enumerate(P2):
        if e[0] in ('ADD','COPY') and (e[1]>=n)!=(e[2]>=n):
            r=e[1] if e[1]<n else e[2]; pinev.setdefault(fd(node[(r,ev2stay[(i,r)])]),[]).append(i)
    members={}
    for (r,k),x in node.items(): members.setdefault(fd(x),[]).append((r,k))
    return st,members,pinev
if __name__=='__main__':
    st,members,pinev=meetings(W)
    sz=Counter(len(v) for v in members.values())
    print('meeting sizes',sorted(sz.items())[:30], 'max',max(sz))
    big=sorted(members.values(),key=len)[-5:]
    for b in big: print(len(b), Counter(kind(r) for r,k in b), Counter(dm(st[r][k][0]) for r,k in b))
    print('pinned',len(pinev))
    # how many public stays per meeting kind, charts per meeting
