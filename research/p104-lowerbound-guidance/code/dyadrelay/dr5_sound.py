"""dr5: exact soundness on built frames C1, c33, c12, c22 (masks from callercut/cc0, stage order = index order):
(a) per-set SUBDY: for every stage set M (|M|>=2) and every J: sum over M's rank-tree nodes (levels<=J) of
    #{r meets X and Y, no piece of r contains X and meets Y}  >= R_J(|M|)   (PIECE2-CROSS summed; piece-aware, stronger than used)
    and node-wise PIECE2-CROSS with c = cyclic alternations (both orientations).
(b) SPARSE: #{r : M_r inside U} <= 2|U|-2 for every U.
(c) the averaged type rows of dr4 (all ic1 rows + SUBDY + SPARSE) via ic1.verify (exists-check over main counts like ic2)."""
import sys,io,contextlib,itertools,os
sys.path.insert(0,'code/callercut')
sys.path.insert(0,'code/intcaller')
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
with contextlib.redirect_stdout(io.StringIO()):import cc0
import dr4,ic1
with contextlib.redirect_stdout(io.StringIO()):import ic2
def alt(X,Y,k):
    seq=[('X' if s in X else 'Y') for s in range(k) if s in X or s in Y]
    if not seq:return 0
    runs=sum(1 for i in range(len(seq)) if seq[i]!=seq[i-1])
    return runs//2 if runs else 0
def pieces_of(M,P):
    listed=set().union(*P) if P else set()
    return [frozenset(p) for p in P]+[frozenset([s]) for s in M-listed]
def credit(M,pcs,X,Y):
    if not (M&X and M&Y):return 0
    return 0 if any(X<=p and p&Y for p in pcs) else 1
def check(name,k,R):
    roles=[(frozenset(M),pieces_of(set(M),P)) for M,P in R]
    worst=None;nodes=0;bad=0
    for d in range(2,k+1):
        for Ms in itertools.combinations(range(k),d):
            Jm=max(0,(d-1).bit_length()-1)
            tot=0;rhs=0
            for J in range(0,Jm+1):
                l=J
                for j in range(2**l):
                    Z=[Ms[i] for i in range(j,d,2**l)]
                    X=set(Z[0::2]);Y=set(Z[1::2])
                    if not Y:continue
                    c=alt(X,Y,k);assert c==len(Z)//2,(Ms,J,Z)
                    for A,B in ((X,Y),(Y,X)):
                        cr=sum(credit(M,p,A,B) for M,p in roles);nodes+=1
                        if cr<2*c:bad+=1
                    tot+=sum(credit(M,p,X,Y) for M,p in roles);rhs+=2*c
                assert rhs==ic1.RJ(d,J)
                sl=tot-rhs
                if worst is None or sl<worst[0]:worst=(sl,Ms,J)
    sp=min(2*u-2-sum(1 for M,p in roles if M<=set(U)) for u in range(1,k+1) for U in itertools.combinations(range(k),u))
    print('%-10s k=%d roles=%d  PIECE2-CROSS nodes %d violations %d | per-set SUBDY min slack %s at %s J=%d | SPARSE min slack %d'%(name,k,len(roles),nodes,bad,worst[0],worst[1],worst[2],sp))
check('C1',3,cc0.C1);check('c33',6,cc0.C33)
for nm in ['c12_tm1o2','c22_tm1o2']:
    k,R=cc0.fromjson(cc0.BASE+'UNIMODEL/arm1/caller_%s.json'%nm);check(nm,k,R)
print('-- averaged type rows (ic2 checker with dr4 rows: ic1 + SUBDY + SPARSE):')
ic2.check('C1',3,ic2.frame_types(cc0.C1));ic2.check('c33',6,ic2.frame_types(cc0.C33))
for nm in ['c12_tm1o2','c22_tm1o2']:
    k,R=cc0.fromjson(cc0.BASE+'UNIMODEL/arm1/caller_%s.json'%nm)
    ic2.check(nm,k,[(len(M),tuple([1]*len(M)),0) for M,P in R],fixed=False)
