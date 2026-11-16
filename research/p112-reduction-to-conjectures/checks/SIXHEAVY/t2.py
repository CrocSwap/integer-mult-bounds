import time,sys
from cov import *
FL={w:flats(w) for w in (4,5,6,7)}
O=off_parab((1,2,3,4,5,6,7))  # D7, 78
for ws in [(6,6,6,6),(6,6,6,5,4),(6,6,6,6,4),(6,6,6,6,5),(6,6,6,6,6)]:
    t=time.time(); r=cover2(O,ws,FL); print(ws, 'COVER' if r is not None else 'none', round(time.time()-t,1), flush=True)
