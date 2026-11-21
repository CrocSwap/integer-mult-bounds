from inst5 import *
from rects import *
import sys
R=max_rects(h,labs,readers,gathers,4)
print('maximal rects',len(R),'by price',{r:sum(1 for x in R if x[2]==r) for r in range(1,5)})
C=covers(R,nz,4)
print('covers with sum price<=4:',len(C))
import pickle; pickle.dump((R,C),open('cl5.pkl','wb'))
for c in C[:20]: print([ (len(R[i][0]),len(R[i][1]),R[i][2]) for i in c])
