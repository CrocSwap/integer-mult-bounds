import sys; sys.path.insert(0,'.')
from e8 import *
a1,a3=S[0],S[2]
T=[mask(off(v)) for v in (a1,a1+a3,a3)]   # pairs 01,02,12
for x1 in (0,1):
    with open('jobs_p3_x%d'%x1,'w') as f:
        f.write('6 %d 3\n'%x1); [f.write('%d %d\n'%(m&((1<<64)-1),m>>64)) for m in T]
