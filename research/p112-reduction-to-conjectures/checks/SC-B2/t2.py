from cov2 import *
import time
E7=parabolic((0,1,2,3,4,5,6)); T=[t for t in range(n) if t not in set(E7)]
print(len(T))
for ws in ([7,7],[7,7,1],[7,6,1,1,1,1],[7,5,5],[7,6,3],[6,6,6],[6,6,6,1],[7,5,4,1]):
    t0=time.time(); print(ws,cover_set(T,ws),round(time.time()-t0,1),flush=True)
