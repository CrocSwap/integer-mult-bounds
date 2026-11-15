import sys; sys.path.insert(0,'.')
import layout_price as lp
from layout_price import *
L=17; nl=8
Zof=lambda ms:[sum(1 for m in ms if k in m) for k in range(L)]
def win(w, grow=2, hubs=2):
    """sliding-window arms: role introduced at left stage k lives on stages k..min(k+w-1,nl-1); right mirrored."""
    ms=[set(range(L)) for _ in range(hubs)]
    for k in range(nl): ms+=[set(range(k,min(k+w,nl)))]*grow
    for k in range(L-1,nl-1,-1): ms+=[set(range(max(k-w+1,nl),k+1))]*grow
    return ms
def capS(ms, mode):
    Z=Zof(ms); cap=[]
    for k in range(L-1):
        if k==nl-1: cap.append(0); continue
        S=sum(1 for m in ms if k in m and k+1 in m)
        cap.append(max(S-4,0) if mode=='lemma' else (max(S-2,0) if mode=='opt' else 99))
    return cap
ms=two_arm(); T,P,Z=invoice(ms,L,caps_B(Zof(ms),L,nl)); price(T,P,'B control')
for w in (1,2,3,4,8):
    ms=win(w)
    for mode in ('lemma','opt','none'):
        try: T,P,Z=invoice(ms,L,capS(ms,mode)); price(T,P,'window w=%d caps=%s Zmax %d'%(w,mode,max(Z)))
        except AssertionError as e: print('w',w,mode,'assert',e)
