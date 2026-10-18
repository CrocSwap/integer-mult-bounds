"""Sufficient precision admission independent of cyclic length."""
from fractions import Fraction as F
from common import need,original


def ceil_log2(value):
    need(type(value) in (F,int) and value>0,'positive exact logarithm')
    value=F(value)
    n,d=value.numerator,value.denominator
    e=n.bit_length()-d.bit_length()
    larger=n>(d<<e) if e>=0 else (n<<-e)>d
    return e+int(larger)


def admission(beta,bits):
    need(type(beta) in (F,int) and 0<beta<=F(1,2),'certified stable margin')
    need(type(bits) is int,'integer working precision')
    g=ceil_log2(1/F(beta))
    need(bits>=2*g+8,'uniform working precision W>=2g+8')
    depth=2*g+(bits-1).bit_length()+4
    beta0=F(1,1<<g)
    need(4*(depth+1)<=(1<<(bits-g)),'uniform depth admission')
    return dict(g=g,bits=bits,beta0=beta0,effective_depth=depth)


def error_bound(B,beta,bits):
    need(type(B) in (F,int) and B>=0,'nonnegative exact source bound')
    record=admission(beta,bits)
    return original.solve_error_bound(B,record['beta0'],bits,record['effective_depth'])
