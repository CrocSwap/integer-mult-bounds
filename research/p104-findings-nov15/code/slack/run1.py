import sys; sys.path.insert(0,'.')
from icap import *
from layout_price import invoice
import step1
r4 = lambda a,b: 4
r3 = lambda a,b: 4 if b == a+1 else 3
def show(lab, ms):
    out=[]
    T,P,Z = invoice(ms, L, step1.capS(ms)); out.append(price(T,P,'',quiet=True))
    T,P,Z = invoice_iv(ms, r4); out.append(price(T,P,'',quiet=True))
    T,P,Z = invoice_iv(ms, r3); out.append(price(T,P,'',quiet=True))
    return out
B = show('B', two_arm())
print('B rows (boundary / interval-4 / interval-3):', [['%.4f'%x for x in r] for r in B])
def rat(o): return ' | '.join('%+.2f%%' % (100*(min(x/y for x,y in zip(r,B[0]))-1)) for r in o)
# lone window role (B + 1 role on left stages je..ee)
for je in range(0, nl-1):
    for ee in range(je, nl-1):
        ms = two_arm(); ms.append(set(range(je, ee+1)))
        print('B + lone role %d..%d   boundary | iv4 | iv3 :'%(je,ee), rat(show('',ms)))
