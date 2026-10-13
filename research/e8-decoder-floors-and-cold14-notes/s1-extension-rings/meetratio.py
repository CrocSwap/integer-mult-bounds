import sys,pickle; sys.path.insert(0,sys.path[0])
from algebra_lines import *
name=sys.argv[1]
roots=e8_roots(); I8=np.eye(8,dtype=np.int64); Li,Lj,Lk=left_quat()
basis={'Gauss':[I8,Li],'Eisen':[I8,a2_rotation(roots)]}[name]
reps,NO=lines_over(roots,basis); v=len(reps)
fl=pickle.load(open('flats_%s.pkl'%name,'rb'))
w=4; fl[4]={frozenset(range(v))}
big=[F for F in fl[3] if len(F)==max(len(G) for G in fl[3])]
print('hyperplane flats of max size',len(big),len(big[0]))
best=0
for r in fl:
    for F in fl[r]:
        meet=sum(1 for X in big if F & X)
        best=max(best,meet/r)
        
print('max meet/rank',best)
