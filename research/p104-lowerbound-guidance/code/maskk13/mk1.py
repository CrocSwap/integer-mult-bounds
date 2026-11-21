"""MASKK13 mk1: SPARSE law [P] (every U: #roles with mask inside U <= 2|U|-2) on controls and on the k13 Turan-tight placements.
Design = list of (mask frozenset, idle pieces).  Also the Lemma-A refinement and the type-level count of the k13 family."""
import sys,itertools,pickle
sys.path.insert(0,'../rescuebuild')
F=frozenset
def sparse(k,R):
    bad=[]
    for r in range(2,k):
        for U in itertools.combinations(range(k),r):
            U=F(U);c=sum(1 for M,P in R if M<=U)
            if c>2*len(U)-2:bad.append((tuple(sorted(U)),c,2*len(U)-2))
    return bad
def lemmaA(k,R):
    bad=[]
    for r in range(2,k):
        for U in itertools.combinations(range(k),r):
            U=F(U);S=[M for M,P in R if M<=U]
            rk=[min(2,sum(1 for M in S if t in M)) for t in U]
            if len(S)>sum(rk)-max(rk):bad.append(tuple(sorted(U)))
    return bad
if __name__=='__main__':
    from rb1 import C1
    from rb9 import C33
    for nm,k,R in (('C1',3,C1),('c33',6,C33)):
        print(nm,'n roles',len(R),'SPARSE viol',len(sparse(k,R)),'LemmaA viol',len(lemmaA(k,R)))
    k=13;A=F(range(6));W=F(range(6,13));H=F(range(13))
    # P1: R=A, pairs = all 21 pairs of W ; P2: R = 6-subset of the 7-side, pairs = K6 + star
    P1=[(H,[]),(H,[]),(A,[])]+[(F(p),[]) for p in itertools.combinations(sorted(W),2)]
    Wl=sorted(W);v=Wl[0];R2=F(Wl[1:])
    P2=[(H,[]),(H,[]),(R2,[])]+[(F(p),[]) for p in itertools.combinations(range(6),2)]+[(F({v,w}),[]) for w in Wl[1:]]
    for nm,R in (('P1',P1),('P2',P2)):
        b=sparse(k,R);print(nm,'roles',len(R),'SPARSE viols',len(b),'worst',max(b,key=lambda x:x[1]-x[2]),'LemmaA viols',len(lemmaA(k,R)))
