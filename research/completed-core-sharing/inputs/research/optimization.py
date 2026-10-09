"""Historical round-four refinement, superseded by optimization-round5.py.
Independent exact arithmetic refinement of the pinned PR24 histogram.
Only Python stdlib; input is a local JSON file. No downloaded code is imported.
"""
from fractions import Fraction as F
from decimal import Decimal as D, localcontext
from math import factorial
from pathlib import Path
from hashlib import sha256
import json

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'sources/swapnil/certificates/external/pr24-bit-network.json'

def ln_interval(x, terms=50):
    """Atanh series after dyadic reduction, with exact rational remainder."""
    assert x >= 1
    k=0
    while x>=2:
        x/=2
        k+=1
    def series(y):
        z=(y-1)/(y+1)
        s=sum((z**(2*j+1)/F(2*j+1) for j in range(terms)),F(0))*2
        e=2*z**(2*terms+1)/(F(2*terms+1)*(1-z*z))
        return s,s+e
    lo,hi=series(x)
    lo2,hi2=series(F(2))
    return lo+k*lo2,hi+k*hi2

def ceil_grid(x,g=10**40):
    return F(-(-x.numerator*g//x.denominator),g)

def floor_grid(x,g=10**40):
    return F(x.numerator*g//x.denominator,g)

def exp_interval(x, terms=6):
    """Terms 0 through 6, then a geometric upper bound on the tail."""
    assert 0<=x<1
    s=sum((x**j/F(factorial(j)) for j in range(terms+1)),F(0))
    first=x**(terms+1)/factorial(terms+1)
    rem=first/(1-x/F(terms+2))
    return s,s+rem

def inputs():
    data=json.loads(SOURCE.read_text())
    c=data['counts']; W,m,s=c['W'],c['m'],c['total_rank']
    hist=data['child_width_multiplicities']
    assert sum(r*n for r,n in hist)==s
    assert W*m-s==c['deficit']
    assert all(1<=r<m and n>0 for r,n in hist)
    logs=[]
    for r,n in hist:
        lo,hi=ln_interval(F(m,r))
        logs.append((F(r*n,W*m),floor_grid(lo),ceil_grid(hi)))
    return data, logs

def verify_complex():
    """Recheck the regenerated complex histogram and certify its published saving."""
    source=ROOT/'research/complex-h28-source-frames.json'
    data=json.loads(source.read_text())
    hist={int(r):n for r,n in data['hist'].items()}
    W,m,s=data['W'],data['m'],data['s']
    assert data['checker']['bad']==0 and data['sum_ok']
    assert sum(r*n for r,n in hist.items())==s
    assert all(1<=r<m and n>0 for r,n in hist.items())
    logs=[]
    for r,n in hist.items():
        lo,hi=ln_interval(F(m,r))
        logs.append((F(r*n,W*m),floor_grid(lo),ceil_grid(hi)))
    a=F(4079603,250000000000)
    _,upper=moment_interval(a,logs)
    assert upper<1
    return a,data,dict(source=str(source.relative_to(ROOT)),sha256=sha256(source.read_bytes()).hexdigest(),
        a_c=str(a),moment_upper_gap=str(1-upper),moment_upper_gap_decimal=dec(1-upper),
        input_label_checker=data['checker'])

def moment_interval(a, logs):
    lo=hi=F(0)
    for w,L,U in logs:
        lo+=w*exp_interval(a*L)[0]
        hi+=w*exp_interval(a*U)[1]
    return lo,hi

def dec(q):
    with localcontext() as ctx:
        ctx.prec=50
        return str(D(q.numerator)/D(q.denominator))

def assembly(a,ac,m_c,s_c,beta=F(1,1000)):
    """Optimized rational parameters, checked against every round3 row."""
    assert (1-beta)*ac>a
    tau=1-a; sigma=1-ac
    chi=tau+(1-beta)*max(sigma-tau,F(0))
    leaf=sigma+beta*(1-sigma)
    guard_gap=F(1,10**25)
    lam=max(tau,sigma,chi)+guard_gap
    lamp=max(lam,leaf)+guard_gap
    # Explicit integer upper bound on 2+m_c*ln(s_c).
    _,ln_s=ln_interval(F(s_c))
    C1=F(2)+ceil_grid(m_c*ln_s,g=1)
    eps=F(1,1)/(2-lamp)-F(1,10**25)
    x=C1+2
    y=eps
    delta=F(1,10**30)/(1+x)
    mu=(1-eps)/(2*(1+x))
    poly=(1+x)*delta
    constraints={
      'lambda above tau sigma chi':lam-max(tau,sigma,chi),
      'lambda_prime above lambda and leaf':lamp-max(lam,leaf),
      'lambda_prime below one':1-lamp,
      'beta in (0,1)':min(beta,1-beta),
      'guard eps C1 < 1+x':1+x-eps*C1,
      'precision 2eps+y < 1+x':1+x-2*eps-y,
      'sub-block coupling y>=eps':F(1) if y>=eps else F(-1),
      'reservations':lamp-(2*eps-1)/eps,
      'record regime eps<1':1-eps,
      'record parameter mu positive':mu,
      'record parameter mu<(1-eps)/(1+x)':(1-eps)/(1+x)-mu,
      'delta in (0,1/8)':min(delta,F(1,8)-delta),
    }
    margins={
      'prefix moves and top individual round':1-eps,
      'simultaneous butterflies':eps*(1-lamp),
      'fine-bit exposures':1-eps-poly,
      'Gaussian maps':1-eps-poly,
      'chirps twists scalar products':1-eps-poly,
      'packed polynomial products':eps,
      'individually processed reserved axes':1-eps-poly,
      'CRT axis reversal':max(eps,1-eps)*(1-tau),
    }
    k=floor_grid(min(margins.values())-F(1,10**25),10**21)
    assert all(v>0 for v in constraints.values())
    assert all(v>k for v in margins.values())
    simple_k=F(119722292675,10**16)
    assert all(v>simple_k for v in margins.values())
    return dict(a_b=str(a),a_c=str(ac),beta=str(beta),kappa=str(k),kappa_decimal=dec(k),
                simple_kappa=str(simple_k),simple_kappa_decimal=dec(simple_k),
                eps=str(eps),lambda_=str(lam),lambda_prime=str(lamp),x=str(x),y=str(y),delta=str(delta),mu=str(mu),C1=str(C1),
                constraints={n:str(v) for n,v in constraints.items()},margins={n:str(v) for n,v in margins.items()},binding=min(margins,key=margins.get))

if __name__=='__main__':
    data,logs=inputs()
    original=ROOT/'research/pr24-original.json'
    assert sha256(original.read_bytes()).hexdigest()==data['source']['sha256']
    original_data=json.loads(original.read_text())
    assert all(original_data['bit']['counts'][k]==v for k,v in data['counts'].items())
    assert original_data['bit']['child_width_multiplicities']==data['child_width_multiplicities']
    ac,complex_data,complex_result=verify_complex()
    grid=10**22
    lower,upper=119723724000000000,119723730000000000
    assert moment_interval(F(lower,grid),logs)[1]<1
    assert moment_interval(F(upper,grid),logs)[0]>1
    while upper-lower>1:
        mid=(upper+lower)//2
        lo,hi=moment_interval(F(mid,grid),logs)
        if hi<1: lower=mid
        elif lo>1: upper=mid
        else: raise ValueError('Need tighter rational bounds')
    a_lo,a_hi=F(lower,grid),F(upper,grid)
    # kappa < min(eps*a_b,1-eps) implies a_b > kappa/(1-kappa).
    # At kappa=2^-16 the required a_b already makes the moment exceed one.
    impossible_k=F(1,2**16)
    impossible_a=impossible_k/(1-impossible_k)
    negative_gap=moment_interval(impossible_a,logs)[0]-1
    assert negative_gap>0
    result={'status':'Historical round-four refinement; superseded by optimization-round5.json',
        'source':data['source'],'moment_root_lower':str(a_lo),'moment_root_upper':str(a_hi),
        'moment_root_lower_decimal':dec(a_lo),'moment_root_upper_decimal':dec(a_hi),
        'moment_gap_at_lower':dec(1-moment_interval(a_lo,logs)[1]),
        'moment_gap_at_upper':dec(moment_interval(a_hi,logs)[0]-1),
        'assembly_ceiling_upper':str(a_hi/(1+a_hi)),'assembly_ceiling_upper_decimal':dec(a_hi/(1+a_hi)),
        'complex':complex_result,
        'negative_control':dict(kappa=str(impossible_k),required_a_b=str(impossible_a),
          moment_lower_gap=str(negative_gap),moment_lower_gap_decimal=dec(negative_gap)),
        'assembly':assembly(a_lo,ac,complex_data['m'],complex_data['s'])}
    prior=F(59861145819,5*10**15)
    k=F(result['assembly']['kappa'])
    result['prior_kappa']=str(prior)
    result['absolute_improvement']=str(k-prior)
    result['relative_improvement_decimal']=dec(k/prior-1)
    out=ROOT/'research/optimization.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('assembly','complex','negative_control')},indent=2))
    print('COMPLEX GAP',complex_result['moment_upper_gap_decimal'])
    print('NEGATIVE CONTROL GAP',result['negative_control']['moment_lower_gap_decimal'])
    print('ASSEMBLY',result['assembly']['kappa'],result['assembly']['kappa_decimal'])
