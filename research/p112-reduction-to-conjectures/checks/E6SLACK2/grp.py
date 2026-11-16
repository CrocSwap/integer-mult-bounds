import sys,pickle
sys.path.insert(0,'../CARRIER'); sys.path.insert(0,'../SC-B2')
import lib
from lib import lab,lines,n,ip
import cov as C
from sympy.combinatorics import Permutation, PermutationGroup
E6=sorted(C.parabolic((0,1,2,3,4,5))); assert len(E6)==36
Tl=[int(x) for x in open('labs.txt').read().split()[1:]]
Tidx=[lab.index(x) for x in Tl]; assert set(Tidx)==set(range(n))-set(E6)
A2=[t for t in Tidx if all(ip(lines[t],lines[e])==0 for e in E6)]; print('A2 lines',A2)
li={l:i for i,l in enumerate(lines)}
def canon(v): return lib.canon(tuple(v))
def refl(r):
    rr=ip(r,r)  # =2? ip uses //4 ; roots norm 8 -> 2
    perm=[]
    for l in lines:
        c=ip(l,r)  # (l,r)
        v=tuple(x-c*y for x,y in zip(l,r))   # l - (l,r) r  (norm 2 => reflection l-(l,r)r)
        perm.append(li[canon(v)])
    return perm
gens=[refl(lines[t]) for t in E6]+[refl(lines[t]) for t in A2]
G=PermutationGroup([Permutation(p) for p in gens]); print('order mod +-',G.order())
pickle.dump((gens,Tidx,A2,E6),open('grp.pkl','wb'))
# orbits on T
orb=G.orbits(); print(sorted(len(o) for o in orb))
