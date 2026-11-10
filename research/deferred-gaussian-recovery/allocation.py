"""Source-first exact finite endpoint allocation; not a production controller.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction

def need(ok,message):
    if not ok:raise ValueError(message)
def clog(n):
    need(type(n) is int and n>0,'positive integer log');return (n-1).bit_length()
def allocation(S,b,Gamma,groups=1,Lmax=4,normalizers=(0,)):
    need(all(type(x) is int for x in (S,b,Gamma,groups)),'integer endpoint descriptors')
    need(S>0 and b>=1 and S<1<<b and Gamma>=0 and groups>=1,'source-bound endpoint domain')
    need(type(Lmax) is int and Lmax>=4 and all(type(x) is int and x>=0 for x in normalizers),'integer upper bound on actual compression descriptors')
    a=2*clog(S)+2*b+7
    tau=a+2*Gamma+2
    z=tau+Gamma+clog(groups)+1
    q=max(101,b+2,a+3*Gamma+7,z+clog(max(8,2*Lmax)),max(normalizers))
    return dict(a=a,tau=tau,z=z,q=q,source_target=max(1,z+2),W=q+3*Gamma+4*b+6,
                recovery_shift=2*b+4+3*Gamma)

def bounds(S,b,Gamma,q,a):
    lam=Fraction(1,1<<Gamma);epsilon=Fraction(1,1<<a);eta=lam**3*epsilon;h=Fraction(1,1<<q)
    first=lam/4+eta
    # Use 2h for complex product rounding, avoiding an irrational constant.
    product=first**2+2*h
    opposite=lam*product+eta
    final=eta*(1+lam**2/2+lam*eta)+lam*2*h
    restored=final/lam**3
    integer=restored*S*S*(1<<(2*b+4))
    return dict(lam=lam,eta=eta,first=first,product=product,opposite=opposite,
                restored=restored,integer_error=integer,epsilon=epsilon)
