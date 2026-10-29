from cov3 import *
E7=parabolic((0,1,2,3,4,5,6)); T=[t for t in range(n) if t not in set(E7)]
for ws in ([7,7],[7,7,1],[7,6,1,1,1,1],[7,5,5],[7,6,3],[6,6,6],[6,6,6,1],[7,5,4,1]):
    t0=time.time(); print(ws,cover_set3(T,ws),round(time.time()-t0,1),flush=True)
E6=(0,1,2,3,4,5); T=[t for t in range(n) if t not in set(parabolic(E6))]
t0=time.time(); print(cover_set3(T,[6,6,6,5,5,1,1,1],verbose=True),time.time()-t0)
