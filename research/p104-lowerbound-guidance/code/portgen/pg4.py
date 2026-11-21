from pg1 import *
def solve(h, tgt):
    lo, hi = D(0), D(1)
    if ceiling(rung(h,hi),False)[0] > tgt: return D(1)
    if ceiling(rung(h,lo),False)[0] < tgt: return D(0)
    for _ in range(32):
        m=(lo+hi)/2
        if ceiling(rung(h,m),False)[0] > tgt: lo=m
        else: hi=m
    return hi
T2 = D('0.0207429')
print('U k=inf X+HS: rho needed to match .0207429 (P104 best caller-universal, with S_spec) ; NG-only checks')
for h in (3,4,5,6,7,8,9,10,12,14,16,18,19,20,21,22,23,24):
    r2 = solve(h, T2); re = solve(h, ceiling(rung(9,D(56)/104),False)[0])
    print(f' h={h}: rho(.0207)={float(r2):.5f}  rho_eq={float(re):.5f}  2/(h+1)={2/(h+1):.5f}  1/(h+1)={1/(h+1):.5f}'); sys.stdout.flush()
