"""Exact integer certificates for the scheduled child volumes."""
from math import comb
from fractions import Fraction
import json


def clog(n):
    return (n - 1).bit_length()


def geometry(u):
    """All arities m with u=ceil(log2(m)) have these same d, t."""
    v = clog(u + 2)
    d = 1
    while (2*d)**3*v <= u:
        d *= 2
    t = (u+2*d*d-2+d*d-1)//(d*d)
    return v, d, t


def certificate(u):
    _, d, t = geometry(u)
    h = 2*d-1
    # Outward integer bounds avoid constructing q, N and the reserve array.
    return 33+2+clog(h)+h*t+1+(d+1)*h+d*t+d*(d-1)*clog(t)


def exact_small(u):
    _, d, t = geometry(u)
    h, q = 2*d-1, 2**t
    dim = 4+2*h*q**h
    load = comb(h,d)**(d+1)*(q-1)**d*t**(d*(d-1))
    assert 2**33*dim*(1+load) <= 2**certificate(u)
    depth = (u+3)//4
    # Sum the closed rational geometric series without a quadratic bit loop.
    quarters = Fraction(4,3)*(1-Fraction(1,4**depth))
    assert 3*2*quarters < 8
    assert 3*4**depth*Fraction(1,16**depth) == 3*Fraction(1,4**depth)


def main():
    base = 2**17
    probes = {base, base+1}
    for j in range(17,160):
        probes.update(n for n in range(2**j-3,2**j+2) if n>=base)
    for j in range(4,44):
        d = 2**j
        for v in range(10,150):
            u = d**3*v
            if abs(clog(u+2)-v)<=1:
                probes.update(n for n in (u-1,u,u+1) if n>=base)
    for u in probes:
        v,d,t = geometry(u)
        assert d**3*v <= u < (2*d)**3*v
        assert (t-1)*d*d < u+2*d*d-2 <= t*d*d
        if u>base:
            # u-1<s<=u; floor(log2(u+1)) <= log2(s+2).
            lower_log = (u+1).bit_length()-1
            assert certificate(u)**3 <= 10**3*(u-1)**2*lower_log
    exacts=list(range(65,257,7))+[511,512,513,1023,1024,2047,base-1,base]
    for u in exacts:
        exact_small(u)
    assert Fraction(1,4)+Fraction(27,4)+2+Fraction(6,17)<10
    print(json.dumps({"rounding_probes": len(probes), "literal_geometry_and_repair_checks": len(exacts)}))


if __name__=="__main__":
    main()
