"""Execute unchanged predecessor arithmetic, with assertions enabled."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sources import HERE,ROOT,pins,load
from fractions import Fraction as Q
import fixtures
from compare import polynomial


def need(ok,why):
    if not ok: raise ValueError(why)


def main():
    need(sys.flags.optimize==0,'predecessor assertions enabled')
    pins()
    pricing=load('pinned1392',HERE/'vendor/pr1392/research/pr1048-certified-repair/pricing.py')
    old=load('pinned1508',ROOT/'research/pr1048-algebraic-order/oracle.py')
    rows=[]
    for quadratic in (False,True):
        a,b,m,W,s=fixtures.tie(quadratic)
        delta={r:b.get(r,0)-a.get(r,0) for r in set(a)|set(b)}
        ll,lh=pricing.old.ln_bounds(s,34);dl,dh=pricing.old.ln_bounds(Q(2),34)
        lower,upper=ll/dh,lh/dl
        if quadratic: lower/=2;upper/=2
        need(0<lower<upper<Q(1,10),'original exponent domain')
        lo,hi=pricing.signed_price(delta,lower,upper,m=m,terms=34)
        need(lo<0<hi,'source signed-price enclosure safely unresolved at genuine tie')
        at_zero=pricing.signed_price(delta,Q(0),Q(0),m=m,terms=34)
        exact=sum(r*n for r,n in delta.items())+Q(32*m*m,10**16)*sum(delta.values())
        need(at_zero[0]<=exact<=at_zero[1],'source surcharge normalization')
        rows.append({'quadratic':quadratic,'source_status':'UNRESOLVED signed interval contains zero',
                     'exponent_interval':list(map(str,(lower,upper))),
                     'signed_interval':list(map(str,(lo,hi)))})
    a,b,m,W,s=fixtures.tie(True)
    try: old.root_order(polynomial(a,m,W),polynomial(b,m,W))
    except ValueError as error: need(str(error)=='unresolved root comparison after 512 bisections','predecessor exact control reason')
    else: raise ValueError('quadratic tie unexpectedly covered by linear-gcd predecessor oracle')
    print(json.dumps({'status':'PASS_PINNED_SURCHARGE_PROBE','pricing':rows,
                      'old_linear_gcd_oracle':'UNRESOLVED at exact irrational common root; outside predecessor supported profile contract'},sort_keys=True))


if __name__=='__main__':main()
