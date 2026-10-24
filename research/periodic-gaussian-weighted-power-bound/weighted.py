"""Source-compatible weighted power certificate. JoyboyBrian; Apache-2.0."""
from fractions import Fraction as Q
from dataclasses import replace
from service import need


def certificate(source_size, excess, alpha, entry_bits, target=20, radius=1):
    need(all(type(v)is int for v in (source_size,excess,alpha,entry_bits,target,radius)), 'integer parameters')
    need(0<excess<source_size and alpha>=1 and entry_bits>=8 and target>=1 and radius>=1, 'certificate domain')
    theta=Q(excess,source_size); a=alpha*alpha
    epsilon=Q(1,1<<(entry_bits+6)); inflation=1/(1-epsilon)
    contraction=2*inflation/(20**a*(1-Q(1,20**(3*a))))
    need(0<contraction<1,'uniform weighted contraction')
    exponent=Q(5*a,4)/theta
    gauge_bits=-(-exponent.numerator//exponent.denominator)
    gauge=1<<gauge_bits
    steps=1;tail=radius*gauge*contraction/(1-contraction)
    while tail>Q(1,1<<(target+2)):
        tail*=contraction;steps+=1
    return steps,tail,contraction,gauge_bits


def adopt(reference, original, target=20):
    # Only an original prepare(reference,target,radius) Plan is admitted.
    s=reference.spec
    steps,tail,contraction,gauge_bits=certificate(s.source_size,s.excess,s.alpha,s.entry_bits,target,original.radius)
    h=Q(1,1<<original.bits)
    numeric=(original.coefficient_degree*h*original.state_bound+2*h)/original.gap
    need(tail+numeric<=Q(1,1<<(target+1)), 'complete new error')
    return replace(original,steps=steps,error_bound=tail+numeric),dict(
        contraction=str(contraction),gauge_bits=gauge_bits,steps=steps,
        old_steps=original.steps),tail,numeric


def geometry_controls():
    count=0;wraps=0;cross=0
    for S in (5,8,17,384):
        for K in ((1,2,3) if S!=384 else (1,)):
            theta=Q(K,S);rho=1+theta
            phase=lambda i:(theta*i+Q(1,2)).numerator//(theta*i+Q(1,2)).denominator
            beta=lambda i:theta*i-phase(i)
            w=min(4,(S-1)//2)
            for i in range(S):
                for h in range(-w,w+1):
                    if not h:continue
                    j=(i+h)%S;bi=beta(i);bj=beta(j)
                    delta=(bi+theta*h)**2-bj*bj
                    need(delta>=0,'nearest residue majorant')
                    lhs=(rho*h+bi)**2-bj*bj
                    rhs=rho*h*h-(bi*bi-bj*bj)/theta
                    need(lhs-rhs==rho/theta*delta,'exact all-branch factorization')
                    count+=1;wraps+=int(i+h!=j);cross+=int(phase(i)!=phase(j))
    # Omitting the large gauge falsely funds one term for this actual entry.
    S=384;theta=Q(1,S);bi=-Q(1,2);bj=-Q(191,384);h=1
    need((1+theta)*h*h-(bi*bi-bj*bj)/theta < 1, 'ungauged entry is not tiny')
    return dict(entries=count,wraps=wraps,cross_phase=cross)
