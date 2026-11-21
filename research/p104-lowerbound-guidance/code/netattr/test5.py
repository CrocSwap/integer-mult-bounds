from inst5 import *
from exact import *
for B in (3,4):
    st,c,R,res=min_mass(h,labs,T,Q,B,verbose=False)
    print('B',B,st,len(res),[R[i][2] for i in c] if c else None)
