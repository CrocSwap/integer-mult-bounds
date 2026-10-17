# every non-E7 parabolic J (|J|<=7) lies in one of the 8 maximal non-root ones (literal inclusion of standard subsets) -> Off(J) contains that Off
from sa import *
import itertools
E7=None; R7=[]
for J in itertools.combinations(range(8),7):
    o=pc(off_parab(J)); R7.append((J,o))
print(R7)
E7s=[J for J,o in R7 if o==57]; print('E7 subsets',E7s)
E6=[J for J in itertools.combinations(range(8),6) if pc(off_parab(J))==84]; print('E6',E6)
bad=[]
for k in range(8):
    for J in itertools.combinations(range(8),k):
        if pc(off_parab(J))==57: continue
        if not any(set(J)<=set(K) for K,o in R7 if o!=57) and not any(set(J)<=set(K) for K in E6): bad.append(J)
print('uncovered',bad)
