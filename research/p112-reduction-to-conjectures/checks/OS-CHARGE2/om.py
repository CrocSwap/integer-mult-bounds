import sys; sys.path.insert(0,'../OS-CHARGE')
from base import *
from collections import Counter
par=lambda x: bin(x).count('1')&1
# beta as F2 bilinear form: need Gram on label coords. labels are bit vectors; compute beta via pairing of root reps
# simpler: hyperplanes are kernels of linear functionals phi_x(l)=par(x&l) on the bit-coords used by mylab
C=Counter()
for x in range(1,512):
    n=sum(1 for t in range(v) if not par(x&LAB[t]))
    zs=[i for i in range(8) if not par(x&Z[i])]
    C[(n,len(zs))]+=1
print(sorted(C.items(),reverse=True))
