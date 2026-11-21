# FEWSTOPS checker: PRICEKIT exact replay + independent legality (public strict ascent, owned nested, co-location)
# + every public row and exit frame identical to t7669; then exact PRICEKIT kappa.
from load import *
from reassign import SM as _SM
def smask(S):
    m=0
    for v in S: m|=1<<v
    return m
def legal(W2):
    sm=[smask(span(b)) for b in W2['frames']]; bad=[]
    for i,e in enumerate(W2['program']):
        if e[0]=='MOVE':
            a,b=sm[e[2]],sm[e[3]]
            if e[1]<n:
                if not (a&b==a and a!=b): bad.append(('pub-not-strict-ascent',i))
            else:
                if not (a&b==a or a&b==b) or a==b: bad.append(('owned-not-nested',i))
    return bad
BASE=None
def check(W2, label='', digits=30):
    global BASE
    if BASE is None: BASE=pk.replay(W)
    r=pk.replay(W2); bad=legal(W2)
    same=all(r['rows'][x]==BASE['rows'][x] for x in range(n))
    nat=pk.native_from_word(W2); ci=pk.caller_invoice(C); inv=pk.invoice(ci,nat); k=pk.kappa(inv['T'],inv['P'],digits)
    return dict(label=label, replay_ok=r['ok'], problems=r['problems'][:5], legality_bad=len(bad), bad=bad[:5], rows_equal=same,
                S=k['S'], kappa_lo=str(k['lo'])[:digits], status=k['status'], moves=sum(1 for e in W2['program'] if e[0]=='MOVE'))
