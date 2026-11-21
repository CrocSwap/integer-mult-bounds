"""rb13: ablation - for a stalled design, split each multi piece (one at a time) into idle singletons and retest."""
import sys,ast;sys.path.insert(0,'.')
from rb1 import *;from rb10 import roles_of
def builds(k,R,nw=3,tr=8):
    best=9
    for w in range(nw):
        S=FSys(k,R,anywalk(k,w));nr,z=S.solve(w,tries=tr);best=min(best,nr)
        if nr<1e-9:return True,nr
    return False,best
def ablate(k,R):
    out=[]
    for r,(M,P) in enumerate(R):
        for j,p in enumerate(P):
            if len(p)<2:continue
            R2=[x for x in R];R2[r]=(M,P[:j]+P[j+1:]+[F({t}) for t in p])
            b,v=builds(k,R2);out.append((r,sorted(p),b,v))
    return out
if __name__=='__main__':
    k=int(sys.argv[2])
    for l in open(sys.argv[1]).readlines()[int(sys.argv[3]):int(sys.argv[4])]:
        d=ast.literal_eval(l.split(' ',3)[3].strip());R=roles_of(d)
        print(l.split()[1],[(sorted(M),[sorted(p) for p in P]) for M,P in R],flush=True)
        for r,p,b,v in ablate(k,R):print('   split role',r,'piece',p,'->','BUILDS' if b else 'stall %.2e'%v,flush=True)
def fullsplit(R):return [(M,[F({t}) for p in P for t in p]) for M,P in R]
