"""Reproduce the crossing, logarithmic tensor threshold and six-stage ceilings.

The exact rank histograms are reconstructed from the two source programs in
the companion package. All signs and minimal powers are proved by outward
rational bounds. No floating-point decisions enter the certificate.
"""
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import sys


K_LOW = Q("0.003890115286594461129996942")
K_HIGH = Q("0.003890115286594461129996943")
TICKS = 10**18


def enclose(lo, hi, digits=24):
    scale = 10**digits
    def render(n):
        sign = "-" if n < 0 else ""
        a,b = divmod(abs(n),scale)
        return f"{sign}{a}.{b:0{digits}d}"
    return [render((lo*scale).__floor__()),render((hi*scale).__ceil__())]


def load_reference(source):
    spec=importlib.util.spec_from_file_location("p104_outward_series",source/"verify_funding.py")
    lib=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib)
    return lib


def positive_power_bounds(x, n, lib):
    if x==1:
        return x,x
    a,b=lib.down(x),lib.up(x)
    low=high=Q(1)
    while n:
        if n & 1:
            low,high=lib.down(low*a),lib.up(high*b)
        a,b=lib.down(a*a),lib.up(b*b)
        n//=2
    return low,high


def ratios(lib, T, P, c_lo, c_hi, z, w):
    """Each moment is increasing in its exponent: valid for a box of prices."""
    tlo,thi=1-c_hi,1-c_lo
    tl=lib.moment(T,tlo)[0]
    th=lib.moment(T,thi)[1]
    pl=lib.moment(P,tlo)[0]
    ph=lib.moment(P,thi)[1]
    cl,ch=lib.power(12,z)
    kl,kh=lib.power(15,w)
    return ((pl/th,ph/tl),
            (lib.moment(P,tlo+z)[0]/(th*ch),lib.moment(P,thi+z)[1]/(tl*cl)),
            (kl*lib.moment(T,tlo-w)[0]/th,kh*lib.moment(T,thi-w)[1]/tl))


def log_moment_bounds(lib, H, lo, hi):
    l2,u2=lib.log_series(Q(2))
    a=b=Q(0)
    for r,n in H.items():
        h=r.bit_length()-1
        lr,ur=lib.log_series(Q(r,2**h))
        a+=n*lib.power(r,lo)[0]*(h*l2+lr)
        b+=n*lib.power(r,hi)[1]*(h*u2+ur)
    return a,b


def finite_surplus(v, bounds, theta, lib):
    powers=[(positive_power_bounds(a,v,lib)[0],positive_power_bounds(b,v,lib)[1]) for a,b in bounds]
    a,g,l=powers
    return 1-a[1]-theta*g[1]-l[1],1-a[0]-theta*g[0]-l[0]


def first_power(bounds,theta,floor,lib):
    assert all(0<a<=b<1 for a,b in bounds)
    budget=Q(2,floor) if floor else Q(0)
    def classify(v):
        lower,upper=finite_surplus(v,bounds,theta,lib)
        assert lower>budget or upper<=budget, "precision insufficient for sign"
        return lower>budget
    lo,hi=0,1
    while not classify(hi):
        lo,hi=hi,2*hi
    while hi-lo>1:
        mid=(hi+lo)//2
        if classify(mid):
            hi=mid
        else:
            lo=mid
    bad=finite_surplus(hi-1,bounds,theta,lib)
    good=finite_surplus(hi,bounds,theta,lib)
    assert bad[1]<=budget<good[0]
    return {'v':hi,'previous_surplus':enclose(*bad,40),'surplus':enclose(*good,40)}


def stage_ceiling():
    last=Q(0)
    steps=[]
    for _ in range(5):
        a,b=((249*c+last)/250 for c in (K_LOW,K_HIGH))
        la,lb=((x*TICKS).__ceil__()-2 for x in (a,b))
        assert la==lb and (a*TICKS).__floor__()==(b*TICKS).__floor__()
        steps.append(la)
        last=Q(la,TICKS)
    bracket=[(249*c+last)/250 for c in (K_LOW,K_HIGH)]
    assert (bracket[0]*TICKS).__floor__()==(bracket[1]*TICKS).__floor__()==3890115286594445
    return {'first_five_max_ticks':steps,'sixth_limit':enclose(*bracket,30),'max_reporting_tick':3890115286594445}


def main(source):
    # The series reader is the exact #8041 file; the literal graph and caller
    # are loaded from the authenticated #8030 source restored by verify.py.
    lib=load_reference(Path(__file__).resolve().parent)
    sys.path.insert(0,str(source))
    from upstream import install
    install()
    from independent_binary_price import raw_moments
    from strong_binary import graph, caller
    T,P=raw_moments(graph(),caller())
    z,w=Q(593,2048),Q(491,1024)
    left,right=Q('0.0038900'),Q('0.00389046')
    assert lib.difference(T,P,K_LOW)[0]>0 and lib.difference(T,P,K_HIGH)[1]<0
    assert lib.difference(T,P,right)[1]<0
    # D'(c) is the paid log-moment less the productive log-moment.
    p=log_moment_bounds(lib,P,1-right,1-left)
    h=log_moment_bounds(lib,T,1-right,1-left)
    deriv=(p[0]-h[1],p[1]-h[0])
    assert -385000<deriv[0]<=deriv[1]<-383000
    bracket=ratios(lib,T,P,left,right,z,w)
    at_root=ratios(lib,T,P,K_LOW,K_HIGH,z,w)
    assert bracket[1][0]>bracket[2][1] and bracket[1][1]<Q(91,100)
    assert at_root[1][0]>Q('.907225471') and at_root[1][1]<Q('.907225473')
    assert at_root[2][0]>Q('.900009331') and at_root[2][1]<Q('.900009333')
    rows=[]
    for n in (8,10,12,15,18,21,24):
        c=K_LOW-Q(1,10**n)
        bounds=ratios(lib,T,P,c,c,z,w)
        for theta in (Q(1,64),Q(2)):
            answer=first_power(bounds,theta,None,lib)
            rows.append({'crossing_reference_minus_price':f'1e-{n}','theta':str(theta),**answer})
    return {'raw_root_bracket':[str(K_LOW),str(K_HIGH)],'rank_occurrences':[sum(T.values()),sum(P.values())],
            'price_interval':[str(left),str(right)],'raw_derivative':enclose(*deriv,6),
            'split_ratio_at_root':enclose(*at_root[1]),'floor_ratio_at_root':enclose(*at_root[2]),
            'split_ratio_on_interval':enclose(*bracket[1],9),'floor_ratio_on_interval':enclose(*bracket[2],9),
            'six_stage':stage_ceiling(),'minimum_powers':rows}


if __name__=='__main__':
    print(json.dumps(main(Path(sys.argv[1]).resolve()),indent=2))
