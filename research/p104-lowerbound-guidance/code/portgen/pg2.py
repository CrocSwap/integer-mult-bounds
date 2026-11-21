from pg1 import *
from fractions import Fraction as F
r104 = D(56)/104; S104 = D('865.58')/104
def solve_rb(h, target, c, eta, sig):
    # rb with ceiling == target (ceiling decreasing in rb); None if target unreachable on [0,1]
    lo, hi = D(0), D(1)
    if ceiling(rung(h,hi,c,eta,sig),False)[0] > target: return D(1)  # even rb=1 above target
    if ceiling(rung(h,lo,c,eta,sig),False)[0] < target: return D(0)
    for _ in range(40):
        m = (lo+hi)/2
        if ceiling(rung(h,m,c,eta,sig),False)[0] > target: lo = m
        else: hi = m
    return hi
models = [('U k=inf, X+HS', ck('inf'), 1, D(0)), ('U k=4, X+HS', ck(4), 1, D(0)), ('U k=inf, S_spec/n=P104', ck('inf'), 0, S104)]
for name, c, eta, sig in models:
    base = ceiling(rung(9, r104, c, eta, sig), False)[0]
    print(f'== {name}: P104 ceiling {float(base):.7f}')
    print(' h | rho_eq (match P104) | rho_.01 | NG floor 2/(h+1) | ceiling at rho=7/13 | at rho=1')
    for h in (3,4,5,6,7,8,9,10,11,12,13,16,17,25,27,33,64,81,729):
        re = solve_rb(h, base, c, eta, sig); r1 = solve_rb(h, D('0.01'), c, eta, sig)
        print(f' {h} | {float(re):.5f} | {float(r1):.5f} | {2/(h+1):.5f} | {float(ceiling(rung(h,r104,c,eta,sig),False)[0]):.6f} | {float(ceiling(rung(h,D(1),c,eta,sig),False)[0]):.6f}')
    sys.stdout.flush()
