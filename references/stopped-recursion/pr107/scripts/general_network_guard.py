"""Stopped-depth guards for arbitrary certified residual exponents.

This certifies a numerical guard conditional on the supplied node recurrence
and elementary-operation charge. It does not certify a finite network.
"""
from fractions import Fraction as Q
from certify import Parameters,constraints,margins,require


def strict_integer_power(m,s):
    require(type(m) is int and type(s) is int and m>=3 and s>=2,'Invalid network dimensions')
    power=1
    while s>=m**power:power+=1
    return power


def guard(m,s,E,beta,zeta,alpha=None):
    require(all(type(x) is int for x in (m,s,E)) and m>=3 and s>=2 and E>=0,
            'Invalid dimensions or additive node charge')
    require(isinstance(beta,Q) and 0<beta<1 and isinstance(zeta,Q) and zeta>0,
            'Use exact stopping and absorption exponents')
    if alpha is None:alpha=Q(strict_integer_power(m,s))
    require(isinstance(alpha,Q) and alpha>=1,'Residual exponent must be an exact rational at least one')
    require(s**alpha.denominator<m**alpha.numerator,'Residual exponent not certified')
    B=s+E;C1=alpha-(alpha-1)*beta+zeta
    raw=max(Q(128*m*B*B),18*m*B*B*(1+1/zeta))
    C0=-(-raw.numerator//raw.denominator)
    require(s*(8+E)<=9*B*B,'One-piece coefficient bound failed')
    require(C1>1 and C0>=9*m*B*B*(1+1/zeta)+18,'Full layer constant failed')
    return dict(m=m,s=s,E=E,B=B,beta=beta,zeta=zeta,alpha=alpha,
                C0=C0,C1=C1,
                recurrence_assumption='A(e)<=s A(e/m)+E internally; A(e)<=8e at leaves e<d^beta',
                finite_network_and_node_charge_verified=False)


def limiting_ceiling(ab,ac,alpha):
    """Upper bound from only Gaussian, guard, packed and leaf constraints.

    This is not a claimed achievable supremum of all assembly conditions.
    """
    require(all(isinstance(x,Q) and x>0 for x in (ab,ac,alpha)) and alpha>=1,
            'Use exact positive savings and residual exponent >=1')
    t=min(Q(1),ab/ac)
    return dict(stopping_fraction=t,
                upper=min(ab,ac)/max(Q(5),1+(alpha-1)*t),
                complex_to_bit_ratio_for_gaussian_value_of_this_bound=max(Q(1),(alpha-1)/4),
                scope='Upper bound from necessary constraints only; no achievability or network certificate')


def hypothetical_parameters(ab,ac,alpha,beta,kappa=Q(1,2**25)):
    require(all(isinstance(x,Q) and 0<x<1 for x in (ab,ac,beta,kappa)),
            'Use exact positive savings, beta and kappa below one')
    require(isinstance(alpha,Q) and alpha>=1,'Use an exact residual exponent >=1')
    zeta=Q(1,1000);C1=alpha-(alpha-1)*beta+zeta
    epsilon=min(Q(199,1000),Q(999,1000)/C1)
    limiting=min(ab,(1-beta)*ac)
    p=Parameters(1-ab,1-ac,epsilon,Q(1),1-Q(199,200)*limiting,
                 1-Q(99,100)*limiting,kappa,beta=beta,delta=Q(1,10000),C1=C1)
    chi=p.tau+(1-beta)*max(p.sigma-p.tau,0)
    cs=constraints(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    cs['packed_overhead']=p.lam-chi
    cs['reserved_axes']=p.lamp-max(0,1-p.c)
    gs=margins(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    return dict(parameters=vars(p),alpha=alpha,constraint_slacks=cs,margins=gs,
                minimum_margin=min(gs.values()),
                parameter_system_passes=all(x>0 for x in cs.values()) and min(gs.values())>kappa,
                finite_networks_verified=False,scalar_node_charge_verified=False,
                status='HYPOTHETICAL PARAMETER WITNESS ONLY')
