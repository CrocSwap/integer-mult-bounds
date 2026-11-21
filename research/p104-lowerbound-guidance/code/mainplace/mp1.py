"""MAINPLACE mp1: k8 nested-split-chain candidates (forced shape from RELAY-HALL, see MP.md): hubs (X|X^c),(Y|Y^c);
D4 roles on X, X^c, Y, Y^c split into pairs; chords = the 8 pair pieces (mains). Check rblaw laws + STAR + RELAY-HALL."""
import sys,itertools
sys.path.insert(0,'code/rescuebuild')
import rblaw
F=frozenset
def pairings(S):
    S=sorted(S);a=S[0]
    for b in S[1:]:
        r=[x for x in S if x not in(a,b)]
        yield (F({a,b}),F(r))
def hall(k,R):
    """RELAY-HALL [P]: for all t!=s, roles of E_t \\ E_s matched injectively to pieces q containing t with M_r >= q (multi pieces only; mains carry none)."""
    bad=[]
    pcs=[(r,p) for r,(M,P) in enumerate(R) for p in P]
    for t in range(k):
        Et=[r for r,(M,P) in enumerate(R) if t in M]
        Qt=[(o,p) for o,p in pcs if t in p and len(p)>=2]
        for s in range(k):
            if s==t:continue
            U=[r for r in Et if s not in R[r][0]]
            adj={r:[i for i,(o,p) in enumerate(Qt) if p<=R[r][0]] for r in U}
            match={}
            def aug(r,seen):
                for i in adj[r]:
                    if i in seen:continue
                    seen.add(i)
                    if i not in match or aug(match[i],seen):match[i]=r;return True
                return False
            if not all(aug(r,set()) for r in U):bad.append(('HALL',t,s))
    return bad
def design(X,Y,px,pxc,py,pyc):
    k=8;A=F(range(k));Xc=A-X;Yc=A-Y
    R=[(A,[X,Xc]),(A,[Y,Yc]),(X,list(px)),(Xc,list(pxc)),(Y,list(py)),(Yc,list(pyc))]
    for P in (px,pxc,py,pyc):
        for p in P:R.append((p,[]))
    return R
if __name__=='__main__':
    k=8;A=F(range(k));X=F({0,1,2,3})
    seen=set();out=[]
    for Y in [F({4,5,6,7}),F({0,4,5,6}),F({0,1,4,5})]:
        for px in pairings(X):
         for pxc in pairings(A-X):
          for py in pairings(Y):
           for pyc in pairings(A-Y):
            R=design(X,Y,px,pxc,py,pyc)
            V=rblaw.violations(k,R,full=True);S=rblaw.star_zero(k,R);H=hall(k,R)
            tag=(len(X&Y),sorted(tuple(sorted(p)) for P in (px,pxc,py,pyc) for p in P))
            print('|XnY|',len(X&Y),'pairs',tag[1],'viol',len(V),V[:3],'star',S[:2],'hall',H[:2],flush=True)
