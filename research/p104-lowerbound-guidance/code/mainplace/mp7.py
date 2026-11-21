"""MAINPLACE mp7: soundness of TRIPLE law [P] on built frames: every 3 stages have >= 3 roles containing >= 2 of them."""
import sys,itertools
sys.path.insert(0,'code/callercut')
import io,contextlib
with contextlib.redirect_stdout(io.StringIO()):import cc0
def tri(name,k,R):
    w=None
    for T in itertools.combinations(range(k),3):
        c=sum(1 for M,P in R if len(M&set(T))>=2);sl=c-3
        if w is None or sl<w[0]:w=(sl,T)
    print('%-10s k=%d TRIPLE min slack %s'%(name,k,w))
tri('C1',3,cc0.C1);tri('c33',6,cc0.C33)
for nm in ['c12_tm1o2','c22_tm1o2','c11_tm2','B11_core']:
    k,R=cc0.fromjson(cc0.BASE+'UNIMODEL/arm1/caller_%s.json'%nm);tri(nm,k,R)
k,R=cc0.fromjson(cc0.BASE+'UNIMODEL/swarm/d3star/caller_C1.json');tri('C1json',k,R)
