# YCARRIER: exact fuzz of the LEVEL-CUT law D >= sum_l rank_Q M_l for NetW with relays of ANY slack.
# M_l = sum over gatherers g (dim a_g >= l) and depositors d (dim b_d < l) of G[:,d] N[d,g] F[g,:], N=(I-H)^-1.
import random, sys
from fractions import Fraction as Fr
random.seed(int(sys.argv[1]) if len(sys.argv)>1 else 1)
dot=lambda a,b: bin(a&b).count('1')&1
def span(B):
    S={0}
    for b in B: S|={x^b for x in S}
    return frozenset(S)
def dimS(S): return len(S).bit_length()-1
def rank(Mx):
    M=[r[:] for r in Mx]; r=0
    if not M: return 0
    for c in range(len(M[0])):
        p=next((i for i in range(r,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        for i in range(len(M)):
            if i!=r and M[i][c]!=0:
                f=M[i][c]/M[r][c]; M[i]=[x-f*y for x,y in zip(M[i],M[r])]
        r+=1
    return r
def randsub(h,d):
    while True:
        B=[random.randrange(1,1<<h) for _ in range(d)]
        S=span(B)
        if dimS(S)==d: return S
def trial(h,nn,ctrl):
    V=1<<h; labs=[x for x in range(1,V) if bin(x).count('1')%2==1]
    ports=random.sample(labs,min(len(labs),random.randint(3,7)))
    nodes=[]
    for k in range(nn):
        da=random.randint(1,h); a=randsub(h,da)
        db=random.randint(0,da); bl=[x for x in a]
        # b subset a of dim db
        while True:
            B=span(random.sample(sorted(a-{0}) or [0],min(db,len(a)-1)))
            if dimS(B)==db and B<=a: break
        nodes.append((a,B))
    D=sum(dimS(a)-dimS(b) for a,b in nodes)
    n=len(ports)
    F=[[Fr(random.choice([0,1,-1,2])) if q in a else Fr(0) for q in ports] for a,b in nodes]
    G=[[Fr(random.choice([0,1,-1,2])) if all(not dot(t,x) for x in b) else Fr(0) for (a,b) in nodes] for t in ports]
    H=[[Fr(0)]*nn for _ in range(nn)]
    for k in range(nn):
        for j in range(k):
            ok = nodes[j][1]<=nodes[k][0]
            if (ok or ctrl) and random.random()<.5: H[k][j]=Fr(random.choice([1,-1,2,Fr(1,2)]))
    # N=(I-H)^-1, H strictly lower => N = sum H^i
    N=[[Fr(int(i==j)) for j in range(nn)] for i in range(nn)]; P=[r[:] for r in N]
    for _ in range(nn):
        P=[[sum(P[i][m]*H[m][j] for m in range(nn)) for j in range(nn)] for i in range(nn)]
        N=[[N[i][j]+P[i][j] for j in range(nn)] for i in range(nn)]
    tot=0
    for l in range(1,h+1):
        Ml=[[Fr(0)]*n for _ in range(n)]
        for g in range(nn):
            if dimS(nodes[g][0])<l: continue
            for d in range(nn):
                if dimS(nodes[d][1])>=l or N[d][g]==0: continue
                for t in range(n):
                    if G[t][d]==0: continue
                    c=G[t][d]*N[d][g]
                    for p in range(n): Ml[t][p]+=c*F[g][p]
        tot+=rank(Ml)
    return D,tot
for h in (3,4,5):
    for ctrl in (False,True):
        viol=tight=0; T=400
        for _ in range(T):
            D,L=trial(h,random.randint(2,5),ctrl)
            viol+=L>D; tight+=L==D
        print('h=%d %s: trials %d, violations %d, tight %d'%(h,'CONTROL(relay rule off)' if ctrl else 'legal',T,viol,tight),flush=True)
