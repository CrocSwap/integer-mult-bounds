from meet import *
from lub import bounds, join
st,members,pinev=meetings(W)
mid={}
for m,Lm in members.items():
    for x in Lm: mid[x]=m
L,U=bounds(P)
init=[SM_[x] for x in W['initial']]; fin=[SM_[x] for x in W['final']]
def pq(r,k):
    p=st[r][k-1][0] if k>0 else init[r]; q=st[r][k+1][0] if k+1<len(st[r]) else fin[r]; return p,q
pairs=[]
for r in range(n):
    for k in range(len(st[r])-1):
        e1=[i for i in st[r][k][1]]; e2=[i for i in st[r][k+1][1]]
        jl=0
        for i in e1+e2: jl=join(jl,L[i]) if jl else L[i]
        mu=(1<<512)-1
        for i in e1+e2: mu&=U[i]
        if jl&mu==jl: pairs.append((r,k))
print('mergeable consecutive stay pairs (per-register, fixed order):',len(pairs), Counter(kind(r) for r,k in pairs))
for r,k in pairs[:6]:
    m1,m2=mid[(r,k)],mid[(r,k+1)]
    print('reg',r,kind(r),'stays',k,k+1,'dims',dm(st[r][k][0]),dm(st[r][k+1][0]),'meet sizes',len(members[m1]),len(members[m2]),'pinned',m1 in pinev,m2 in pinev)
    for (x,j) in members[m1]:
        p,q=pq(x,j); print('    M1 member',kind(x),x,'p,G,q dims',dm(p),dm(st[x][j][0]),dm(q),'next meeting==M2' if j+1<len(st[x]) and mid.get((x,j+1))==m2 else '')
    for (x,j) in members[m2]:
        p,q=pq(x,j); print('    M2 member',kind(x),x,'p,G,q dims',dm(p),dm(st[x][j][0]),dm(q),'prev meeting==M1' if j>0 and mid.get((x,j-1))==m1 else '')
