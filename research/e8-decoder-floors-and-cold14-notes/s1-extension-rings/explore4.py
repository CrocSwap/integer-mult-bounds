import sys; sys.path.insert(0,sys.path[0])
from algebra_lines import *
roots=e8_roots(); I8=np.eye(8,dtype=np.int64)
Li,Lj,Lk=left_quat()
S=set(map(tuple,roots))
for nm,M in (('i',Li),('j',Lj)): assert all(tuple(M@r) in S for r in roots), nm
g=a2_rotation(roots)
for name,basis in (('Gauss',[I8,Li]),('Eisen',[I8,g]),('Hurwitz',[I8,Li,Lj,Lk])):
    reps,NO=lines_over(roots,basis)
    w,K=clique_number(NO)
    print(name,'v',len(reps),'deg nonorth',sorted(set(NO.sum(1))),'clique',w, 'rank of clique',arank(reps,basis,K))
