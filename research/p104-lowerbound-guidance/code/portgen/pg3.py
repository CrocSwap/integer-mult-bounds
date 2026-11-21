from pg1 import *
r104 = D(56)/104
base = ceiling(rung(9, r104), False)[0]
# (a) h thresholds at rho=0 (no decoder mass at all), U k=inf, X+HS
for tgt, lab in ((base, 'P104 parity'), (D('0.01'), '.01')):
    for h in range(14, 200):
        if ceiling(rung(h, D(0)), False)[0] <= tgt:
            print(f'h0({lab}) = {h}: ceiling(rho=0) = {ceiling(rung(h,D(0)))}; h-1: {float(ceiling(rung(h-1,D(0)),False)[0]):.7f}'); break
sys.stdout.flush()
# (b) 7113-shaped caller per port, radices 8->u [MODEL]; mains 400/104 per port at u^s; native X+HS per port
Tcal=[(1,416),(2,416),(3,416),(4,416),(5,416),(6,416),(7,416),(8,416),(9,208),(17,208)]   # radix u*d+1
Pcal=[('1',384),(1,656),('u1',32),(2,416),(3,416),(4,416),(5,416),(6,416),(7,416),(8,208)]  # radix u*l, '1'->1, 'u1'->u+1
def c7113(h):
    u=h-1; o={}
    for d,c in Tcal: o[u*d+1]=o.get(u*d+1,D(0))+D(c)/17/104
    for l,c in Pcal:
        r = 1 if l=='1' else (u+1 if l=='u1' else u*l)
        o[r]=o.get(r,D(0))-D(c)/17/104
    o[u]=o.get(u,D(0))-D(400)/104
    return o
def rung7113(h, rb):
    u=h-1; PSI={h:D(1),u:D(-1)}; H={1:D(1),u-1:D(1),u:D(-1)}
    return add((1,c7113(h)),(-2*D(rb),PSI),(-1,H))
print('7113-shaped control h=9 rho=56/104:', ceiling(rung7113(9, r104)))
print(' c7113(1) per port =', float(ev(c7113(9),D(1))), ' (Theorem-U 2-2/17 =', 2-2/17, ')')
def solve(fn, h, tgt):
    lo, hi = D(0), D(1)
    if ceiling(fn(h,hi),False)[0] > tgt: return D(1)
    if ceiling(fn(h,lo),False)[0] < tgt: return D(0)
    for _ in range(36):
        m=(lo+hi)/2
        if ceiling(fn(h,m),False)[0] > tgt: lo=m
        else: hi=m
    return hi
print(' h | 7113-shaped: ceiling at 7/13 | rho_.01 | rho_eq(.0093454)')
b7 = ceiling(rung7113(9, r104), False)[0]
for h in (4,5,6,7,8,9,10,11,12,13,17):
    print(f' {h} | {float(ceiling(rung7113(h,r104),False)[0]):.6f} | {float(solve(rung7113,h,D("0.01"))):.5f} | {float(solve(rung7113,h,b7)):.5f}'); sys.stdout.flush()
