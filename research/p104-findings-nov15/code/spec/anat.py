# SPECBREAK R3: exact S anatomy of #7617 (best7616 x 7113 caller) + PRICEKIT prizes of contract-side levers.
import sys, math
sys.path.insert(0, '../../PRICEKIT')
import pricekit as pk
from collections import Counter
W = pk.load('../../ATTACK/STACK7616/best7616.json.gz')
C = pk.load('../../MONOCALLER/7113_CALLER.json')
nat = pk.native_from_word(W); ci = pk.caller_invoice(C)
base = pk.price(pk.invoice(ci, nat), 30); k0 = base['kappa']['lo']
print('BASE', pk.cite('#7617', base))
mass = lambda h: sum(r*v for r, v in h.items())
sl = pk.check_slots(C, nat)
L = ci['nJ']; ports = ci['ports']
tot = 0
for ty in ('A', 'B'):
    t = C['types'][ty]; n = len(t['diagonal']); hdr = sl[ty]['header']
    Tm = sum(int(dg[0]) % 2 + 8*sum(dg[2:]) for dg in t['diagonal'])
    idle = sum(8*len(e[3]) + (e[1] == 'IDLE_ODD') for e in C['events'] if e[0] == ty and e[1] in ('IDLE_ONE', 'IDLE_ODD'))
    q = sum(1 for e in C['events'] if e[0] == ty and e[1] == 'QUERY')
    odd = sum(1 for e in C['events'] if e[0] == ty and e[1] == 'IDLE_ODD')
    mains = 8*sum(sl[ty]['covered'])
    print(ty, 'ports', ports[ty], 'fields', n, 'T/port', Tm, '= 8*header', 8*hdr, '+ phase', Tm - 8*hdr,
          '| idle mass', idle, '+ main mass', mains, '=', idle + mains, '(8*hdr + odd idles', 8*hdr + odd, ')',
          '| sign units: QUERY', q, 'IDLE_ODD', odd, '| net/port', Tm - idle - mains - q)
    tot += ports[ty]*(Tm - idle - mains - q)
own = sum(abs(len(W['frames'][e[3]]) - len(W['frames'][e[2]])) for e in W['program'] if e[0] == 'MOVE' and e[1] >= W['public'])
print('ports*(phase - sign) =', tot, ' owned/call', own, ' S =', tot - L*own, ' (PRICEKIT S', base['S'], ')')
# D0 split
def d0(h): return sum(v*r*math.log(r) for r, v in h.items() if r > 1)
mm = Counter(); [mm.update(v) for v in nat['main_moves'].values()]
print('D0 parts per invoice: caller T %.1f  caller P %.1f  native helpers T %.1f  mains P %.1f  other native P %.1f' % (
    d0(ci['T']), d0(ci['P']), L*d0(nat['T']), L*d0(mm), L*(d0(nat['P']) - d0(mm))))
def prize(label, dT=None, dP=None, cT=None, cP=None):
    T = Counter(ci['T']); P = Counter(ci['P'])
    for r, v in (cT or {}).items(): T[r] += v
    for r, v in (cP or {}).items(): P[r] += v
    c2 = dict(ci); c2['T'] = +T; c2['P'] = +P
    n2 = pk.native_param(nat, 96, 8, dT=dT, dP=dP)
    pr = pk.price(pk.invoice(c2, n2), 30); k = pr['kappa']['lo']
    print('%-58s S %5d  kappa %s  x%.5f' % (label, pr['S'], pk.kstr(pr['kappa'], 14), float(k / k0)))
prize('(a) rho 2->1 on A: one QUERY less per A port', cP={1: -96})
prize('(a2) rho 2->1 on A and B (B: one IDLE_ODD -> IDLE_ONE)', cP={1: -96, 9: -8, 8: 8})
prize('(b) owned c -1 (2 rank-1 owned jobs less per call)', dP={1: -2})
prize('(c) D-bound: every main paid as ONE rank-8 MOVE', dP={**{r: -v for r, v in mm.items()}, 8: 400})
prize('(d) one extra odd field per A port, T[9]+P[9] (neutral)', cT={9: 96}, cP={9: 96})
prize('(e) one extra phase unit per A port per call (+17/port)', cT={1: 17*96})
