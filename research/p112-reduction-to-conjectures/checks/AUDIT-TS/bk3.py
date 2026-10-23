# AUDIT-TS bk3: third implementation of the BK/BK7 survivor enumeration (count-vector recursion; own packing via subset sums).
from itertools import product
g=[0,1,2,4,8,12,20,36]; g72=[0,1,2,4,8,12,20,32]; dl=[0,53,78,92,100,106,109,111,112]
def multisets(n,lo=2):
    if n==0: yield (); return
    for w in range(lo,8):
        for r in multisets(n-1,w): yield (w,)+r
def feas(ws,b):          # ws ascending
    for lev in range(1,b+1):
        X=ws[:len(ws)-(b-lev)]; G=sum(g[w] for w in X); T=sum(g72[w] for w in X)
        ok = (T>=53 or G>=73) if lev==1 else (T>=78 or G>=82) if lev==2 else G>=dl[lev]
        if not ok: return False
    return True
def kill(ws,b):
    X=ws[:len(ws)-b]
    if sum(g[w] for w in X)>=53: return False
    tot=sum(X)
    if tot<=7: return True
    sums={0}
    for w in X: sums|={s+w for s in sums}
    return any(s<=6 and tot-s<=6 for s in sums)
for b in range(5,9):
    row=[]
    for t in range(1,7):
        S=[ws for n in range(b,b+t+1) for ws in multisets(n) if sum(w-2 for w in ws)<6*b and feas(ws,b) and not kill(ws,b)]
        row.append((t,len(S),max((6*b-sum(w-2 for w in ws) for ws in S),default=None)))
    print(b,row,flush=True)
