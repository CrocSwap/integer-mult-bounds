from cov2 import *
import time
# sanity: root Off set (57 lines) vs (7,7)+1 should be coverable? with G3 results (7,6)+k<=4 no
# rank-7 parabolic E7: I = simple roots 0..7 minus something. find E7: size 63
sizes={}
for I in itertools.combinations(range(8),7):
    sizes[I]=len(parabolic(I))
print(sizes)
