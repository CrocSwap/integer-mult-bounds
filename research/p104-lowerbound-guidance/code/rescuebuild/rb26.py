"""rb26: is a design feasible with a GENERIC rank-(2k-2) matrix on Z in place of the walk matrix Ghat? (separates piece/support
obstructions from walk-structure obstructions)."""
import sys,ast;sys.path.insert(0,'.')
from rb1 import *;from rb10 import roles_of
def zproj(k):
    P=np.eye(2*k)
    for c in range(2):
        v=np.zeros(2*k);v[c::2]=1;v/=np.linalg.norm(v);P-=np.outer(v,v)
    return P
def generic_test(k,R,seeds=4,tries=8):
    best=9
    for sd in range(seeds):
        rng=np.random.default_rng(sd);P=zproj(k);G=P@rng.normal(size=(2*k,2*k))@P
        S=FSys(k,R,anywalk(k,0));S.G=G;nr,z=S.solve(sd,tries=tries);best=min(best,nr)
        if nr<1e-10:return True,nr
    return False,best
if __name__=='__main__':
    k=int(sys.argv[1])
    for l in [x for x in open(sys.argv[2]) if 'SURVIVES' in x][int(sys.argv[3]):int(sys.argv[4])]:
        d=ast.literal_eval(l[l.index('((('):].strip());print(l.split('val ')[1].split()[0],'generic-G',generic_test(k,roles_of(d)),flush=True)
