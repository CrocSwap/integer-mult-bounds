# PORTGEN pg1: per-port parametric rung. Own code; ceiling/cover logic retyped from UNIMODEL/runggen/rg1.py. stdlib Decimal-50.
# f(s) = c*A_u(s) - 2*rb*psi_h(s) - eta*H_u(s) - sig*p_u(s), u=h-1; kappa = 1 - s*, s* = first root of f from s=0 side.
import signal, sys; signal.alarm(1500)
from decimal import Decimal as D, getcontext
getcontext().prec = 50
def pw(r, s): return D(1) if r == 1 else (D(r).ln()*s).exp()
def ev(f, s): return sum(c*pw(r, s) for r, c in f.items())
def ub(f, lo, hi): return sum((c*pw(r, hi if (c > 0) == (r > 1) else lo)) if r != 1 else c for r, c in f.items())
def add(*fs):
    o = {}
    for k, f in fs:
        for r, c in f.items(): o[r] = o.get(r, D(0)) + D(k)*c
    return o
def rung(h, rb, c=D(2), eta=1, sig=D(0)):
    u = h-1
    A = {2*u+1: D(1), u: D(-2)}; PSI = {h: D(1), u: D(-1)}
    H = {1: D(1), u-1: D(1), u: D(-1)} if u > 2 else ({1: D(2), u: D(-1)} if u == 2 else {1: D(1)})
    P = {1: D(u)/(u-1), u: D(-1)/(u-1)}
    return add((c, A), (-2*D(rb), PSI), (-eta, H), (-D(sig), P))
def ceiling(f, cover=True, N=400):
    prev = D(0)
    for i in range(1, N+1):
        s = D(i)/N
        if ev(f, s) >= 0: break
        prev = s
    else: return D(0), True
    lo, hi = prev, s
    for _ in range(90):
        mid = (lo+hi)/2
        if ev(f, mid) >= 0: hi = mid
        else: lo = mid
    sstar = lo
    if not cover: return 1-sstar, None
    end = sstar - D('1e-9'); stack = [(D(0), end)]; ok = True; cells = 0
    while stack:
        a, b = stack.pop(); cells += 1
        if ub(f, a, b) < 0: continue
        if b - a < D('1e-12') or cells > 200000: ok = False; break
        m = (a+b)/2; stack += [(a, m), (m, b)]
    return 1-sstar, ok
def ck(k): return D(2) if k == 'inf' else 2-D(2)/k
if __name__ == '__main__':
    r104 = D(56)/104; S104 = D('865.58')/104
    print('CONTROLS (h=9, rb=56/104):')
    for k in ('inf', 17, 4):
        print(f' k={k}: X+HS {ceiling(rung(9,r104,ck(k)))}  S_spec(no HS) {ceiling(rung(9,r104,ck(k),0,S104))}')
