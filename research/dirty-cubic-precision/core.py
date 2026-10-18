"""Cubic dirty-prefix budgets. See PROOF.md for universal hypotheses."""
from fractions import Fraction as F
from math import gcd, isqrt

def need(ok,label):
    if not ok:raise ValueError(label)

def logceil(x):
    x=F(x);need(x>0,'positive logarithm input')
    j=x.numerator.bit_length()-x.denominator.bit_length()
    return j+(x>F(2)**j)

def primepower(r):
    if type(r) is not int or r<3:return False
    prime=next((i for i in range(2,isqrt(r)+1) if r%i==0),r)
    rest=r
    while rest%prime==0:rest//=prime
    return rest==1

def resources(n):
    need(type(n) is int and n>0,'factor count')
    depth=(n-1).bit_length();q=1<<(n.bit_length()-1)
    return depth,3*q*n-2*q*q,2*3**depth

def uniform(r,p,m,incoming):
    need(primepower(r),'prime power radix >=3')
    need(all(type(x) is int and x>=0 for x in (p,m,incoming)) and p>=1,'integer precision')
    n=r-1;ell=logceil(r);h,N,C=resources(n)
    phi=sum(gcd(j,r)==1 for j in range(1,r))
    d0=1+2*ell+r*n*phi;a0=2*d0+r+2;g=d0+ell+2*r+2
    e=max(d0+1,a0+1,p+2*a0+m+4);b=max(n*ell,e+r+3)
    J=a0+2*r+ell+1+2*h;A=3*g+logceil(13*(r+1))
    w=max(incoming,A,2*g+1,p+3+logceil(N)+A+m+3*J)
    need(w<=max(incoming,p)+m+16*r**3,'cubic working precision')
    need(b<=p+m+7*r**3,'cubic coefficient precision')
    return dict(radix=r,target_bits=p,magnitude_bits=m,input_bits=incoming,n=n,phi=phi,
                depth=h,leaf_calls=N,coefficient_row_bound=C,circle_exponent=d0,
                original_inverse_exponent=a0,margin_exponent=g,coefficient_error_exponent=e,
                factor_bits=b,prefix_exponent=J,local_error_exponent=A,working_bits=w)

def check_uniform(row):
    need(all(type(v) is int for v in row.values()),'integer certificate')
    need(row==uniform(row['radix'],row['target_bits'],row['magnitude_bits'],row['input_bits']), 'certificate fields')
    w,p,m,J,A,N,g=(row[k] for k in ('working_bits','target_bits','magnitude_bits','prefix_exponent','local_error_exponent','leaf_calls','margin_exponent'))
    need(w>=row['input_bits'] and w>=2*g+1,'input grid and closure')
    need(w-p-m-3*J-A-3>=0 and N<=1<<(w-p-m-3*J-A-3),'execution error exponent')
    need(row['coefficient_error_exponent']>=p+2*row['original_inverse_exponent']+m+4,'coefficient perturbation')

def execution(n,G,a,D,bits):
    need(G>=1 and a>0 and D>=0 and type(bits) is int and bits>=0,'execution hypotheses')
    h,N,C=resources(n);B=C*G;t=N*B*B*a*F(1,1<<bits)
    need(t<=F(1,2),'feedback smallness')
    return dict(prefix_bound=B,leaf_calls=N,feedback=t,magnitude=2*B*D+1,error=2*t*(B*D+1))

def choose(n,G,a,D,target,incoming,beta):
    need(0<beta<=1 and type(target) is int and target>=0 and type(incoming) is int and incoming>=0,'grid parameters')
    _,N,C=resources(n);B=C*G
    bits=max(incoming,target+logceil(2*N*B*B*a*(B*D+1)),logceil(2/beta**2))
    result=execution(n,G,a,D,bits)
    need(result['error']<=F(1,1<<target),'target error')
    return bits,result
