from fractions import Fraction as Fr
from skel import X
import sys
def best(h, cst, v, S=(3,5,7,9,11)):
    out={}
    for s in S:
        r=X(s,h,1,Fr(cst,v))
        out[s]=float(r['hi']) if r else None
    return out
for h,cst,v in [(8,63,111),(9,64,112),(8,72,120),(8,62,111),(8,54,102),(9,56,104),(8,7,63*1)]:
    print(h,cst,v, {k:('%.4e'%x if x else None) for k,x in best(h,cst,v).items()})
