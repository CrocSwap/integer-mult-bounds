from e8shard import *
N=120
Q120=[[dot(U[t],U[s]) for s in range(N)] for t in range(N)]
# rows on all 120 lines
rows120=[]
for (zp,z) in pairs:
    d,dp=idx[z],idx[zp]; c=int(G[d,dp])
    rows120.append(([Fr(int(G[p,d])) for p in range(N)],[Fr(int(G[s,dp]),2*c) for s in range(N)]))
bad=0
for t in range(N):
    for s in range(N):
        if Q120[t][s]:
            v=sum(w[t]*u[s] for w,u in rows120)
            if v!=(1 if t==s else 0): bad+=1
print('identity violations on 120 lines',bad)
def pr120(Pp):
    out=[]
    for w,u in rows120:
        D=[t for t in Pp if w[t]!=0]; S=[s for s in Pp if u[s]!=0]
        if not D or not S: continue
        out.append(rk2([sum(Q120[t][s]<<j for j,s in enumerate(S)) for t in D]))
    return out
Pp=[t for t in range(N) if G[t,117]==0]
print(len(Pp),pr120(Pp))
import random
random.seed(5)
def gr(Pp): return rk2([sum(Q120[t][s]<<j for j,s in enumerate(Pp)) for t in Pp])
seen={}
for k in (1,2,3,4,5):
    for trial in range(2500):
        S=random.sample(range(120),k)
        Pp=[t for t in range(N) if all(G[t,s]==0 for s in S)]
        if len(Pp)<4: continue
        p=pr120(Pp); g=len(Pp)-sum(p); r=gr(Pp)
        key=(r,len(Pp))
        if key not in seen or g>seen[key][0]: seen[key]=(g,p,S)
for key in sorted(seen): print('gramrank,n',key,'gain',seen[key][0],seen[key][1])
