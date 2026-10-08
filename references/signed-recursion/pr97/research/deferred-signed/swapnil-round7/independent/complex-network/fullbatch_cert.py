"""Certified fully batched complex saving from a residual histogram, and kappa on our stack with the
batched two-stage bit interchange (a_b = 22157/(5*10^9))."""
import sys, json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts'))
from fractions import Fraction as Q
from bc import ln_upper, exp_lower
from certificate_round3 import evaluate

def ln_up(x):  # certified U > ln x, tight
    return ln_upper(Q(x), rel=Q(1,10**13))

def cert(hist,W,m,s,grid=10**12):
    ws=[(Q(r*c,W*m), ln_up(Q(m,r))) for r,c in hist.items()]
    assert sum(r*c for r,c in hist.items())==s
    mom=lambda a: sum(w/(1-a*U) for w,U in ws)
    lo,hi=0,10**8
    assert mom(Q(hi,grid))>1
    while hi-lo>1:
        mid=(lo+hi)//2
        if all(Q(mid,grid)*U<1 for _,U in ws) and mom(Q(mid,grid))<1: lo=mid
        else: hi=mid
    return Q(lo,grid), 1-mom(Q(lo,grid))

def sqrt_up(x,g=10**12):
    n=math.isqrt(x.numerator*g*g//x.denominator)+1; r=Q(n,g); assert r*r>x; return r

def path_bound(m,h,A):
    q=m+6*h; assert A<q<2*A
    return sum(c*sqrt_up(c) for c in (Q(A,m),Q(q-A,m)))

if __name__=='__main__':
    ab=Q(22157,5*10**9)
    for f in sys.argv[1:]:
        d=json.load(open(f)); hist={int(k):v for k,v in d['hist'].items()}
        m=d['m']; a,gap=cert(hist,d['W'],m,d['s'])
        A=max(hist); pb=path_bound(m,d['h'],A)
        print(f, 'ranks',len(hist),'a_c',a,'gap %.3e'%gap,'maxrank',A,'m',m,'pathbound<0.999',pb<Q(999,1000),float(pb))
        for g in ('pathwise','crude'):
            r=evaluate(ab,a,Q(1,1000),g,m_c=m,s_c=d['s'])
            print('   ',g,r['ok'],'kappa',r['kappa'],'%.4e 2^%.3f'%(r['kappa'],math.log2(r['kappa'])),r['binding'],r['bad'])
