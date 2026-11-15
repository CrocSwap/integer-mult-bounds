"""escape pricing: dying pair/single entering k, dying after d, plus ONE slack role entering at stage j_e<=d (mask j_e..e_end)."""
import sys; sys.path.insert(0,'.')
from step1 import dying, go, L, nl
import step1
B=go('B control',[],0)
for c in (2,1):
  for k in (0,1):
    for d in range(max(k,1),nl-2):
      for je in range(k+1 if k==0 else 0, d+1):
        for eend in (d, nl-1):
          sp=[('L',k,d,c,0)]; ms=dying(sp); ms.append(set(range(je,eend+1)))
          from layout_price import invoice, price
          T,P,Z=invoice(ms,L,step1.capS(ms)); r=price(T,P,'c=%d k=%d d=%d slack@%d..%d'%(c,k,d,je,eend),quiet=True)
          m=min(x/y for x,y in zip(r,B))
          if m>=1.005: print('PASS c=%d k=%d d=%d slack %d..%d min ratio %.4f td %.4f'%(c,k,d,je,eend,m,r[0]/B[0]))
