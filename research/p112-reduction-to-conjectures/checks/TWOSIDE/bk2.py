# TWOSIDE bk2: independent re-implementation of bk1 on cells (5,1),(5,2) (and prints (5,3) survivors for comparison).
# Works with weights w in {2..7} directly; own cap tables; brute-force packing over all bin assignments.
from itertools import product, combinations_with_replacement as cwr
CAPG={2:2,3:4,4:8,5:12,6:20,7:36}; CAPT={2:2,3:4,4:8,5:12,6:20,7:32}
DH=[None,53,78,92,100,106,109,111,112]
def feasible(W,b):
    W=sorted(W)                                      # ascending
    for lev in range(1,b+1):                         # keep the len-(b-lev) smallest... i.e. drop the b-lev largest
        X=W[:len(W)-(b-lev)]
        sg=sum(CAPG[w] for w in X); st=sum(CAPT[w] for w in X)
        if lev==1 and not (st>=53 or sg>=73): return False
        if lev==2 and not (st>=78 or sg>=82): return False
        if lev>=3 and sg<DH[lev]: return False
    return True
def killed(W,b):
    rho=len(W)-b; X=sorted(W)[:rho]
    if sum(CAPG[w] for w in X)>=53: return False
    for asg in product((0,1),repeat=rho):
        if all(sum(w for w,a in zip(X,asg) if a==k)<=6 for k in (0,1)): return True
    return False
b=5
for t in (1,2,3):
    S=[]
    for n in range(b,b+t+1):
        for W in cwr(range(2,8),n):
            if sum(w-2 for w in W)<6*b and feasible(W,b) and not killed(W,b): S.append(tuple(sorted((w-2 for w in W),reverse=True)))
    print(b,t,len(S),sorted(S))
