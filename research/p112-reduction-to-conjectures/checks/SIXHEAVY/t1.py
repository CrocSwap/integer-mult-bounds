import time
from sa import *
t=time.time()
for w in (4,5,6,7):
    F=flats(w); print(w,len(F),max(map(pc,F)),time.time()-t,flush=True)
types={}
for k in range(0,8):
    for J in itertools.combinations(range(8),k):
        O=off_parab(J); types.setdefault(pc(O),[]).append(J)
for s in sorted(types): print(s,len(types[s]),types[s][:3])
