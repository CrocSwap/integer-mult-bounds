"""Certified local pages for the Gaussian factors of the fine-prime Gaussian transform.

The expansion and inverse use the maps of Harvey and van der Hoeven. The
normalization follows the original-coordinate construction in the repository.
Each real page entry has one common power-of-two denominator. This module
generates its pages without an odd-order Fourier matrix or a supplied tensor.
"""

from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from math import gcd


def ceildiv(x, y):
    return -((-x) // y)


class CoefficientAdmissionError(ValueError):
    """The finite setup cannot certify its coefficients at the selected grid."""


def admit(condition, message):
    if not condition:
        raise CoefficientAdmissionError(message)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pi_bounds(bits):
    """Enclose pi on the setup grid using atan(1/2) + atan(1/3)."""
    scale = 1 << bits

    def arctangent(q):
        total = Fraction(0)
        k = 0
        while True:
            total += Fraction((-1)**k, (2*k+1)*q**(2*k+1))
            k += 1
            next_term = Fraction((-1)**k, (2*k+1)*q**(2*k+1))
            if abs(next_term)*scale*16 < 1:
                return min(total, total+next_term), max(total, total+next_term)

    a, b = arctangent(2)
    c, d = arctangent(3)
    low, high = 4*(a+c)*scale, 4*(b+d)*scale
    return int(low), ceildiv(high.numerator, high.denominator)


def exp_minus_pi(x, bits, pi_pair):
    """Enclose exp(-pi*x) for a nonnegative rational x."""
    require(x >= 0, "negative Gaussian exponent")
    scale = 1 << bits
    if x == 0:
        return scale, scale
    if 3*x >= bits+1:
        return 0, 1
    p_lo, p_hi = pi_pair
    lo = p_lo*x.numerator // x.denominator
    hi = ceildiv(p_hi*x.numerator, x.denominator)
    halves = 0
    while hi > scale//8:
        lo //= 2
        hi = ceildiv(hi, 2)
        halves += 1
    term_low = term_high = scale
    lower = upper = scale
    k = 0
    while True:
        k += 1
        term_low = term_low*lo // (scale*k)
        term_high = ceildiv(term_high*hi, scale*k)
        if k % 2:
            lower -= term_high
            upper -= term_low
        else:
            lower += term_low
            upper += term_high
        if term_high <= 1:
            if k % 2:
                upper += 1
            else:
                lower -= 1
            break
    lower, upper = max(0, lower), min(scale, upper)
    for _ in range(halves):
        lower, upper = lower*lower//scale, ceildiv(upper*upper, scale)
    return lower, upper


def inverse_rational(matrix):
    """Return an exact inverse. The row choices and updates are deterministic."""
    n = len(matrix)
    a = [list(row) + [Fraction(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for c in range(n):
        pivot = next((r for r in range(c,n) if a[r][c]), None)
        admit(pivot is not None, "singular midpoint narrow operator")
        a[c], a[pivot] = a[pivot], a[c]
        z = a[c][c]
        a[c] = [v/z for v in a[c]]
        for r in range(n):
            if r != c and a[r][c]:
                v = a[r][c]
                a[r] = [w-v*u for w,u in zip(a[r],a[c])]
    return [row[n:] for row in a]


def dyadic_shift(norm):
    shift = 0
    while norm > 1 << shift:
        shift += 1
    return shift


def mid(bounds, scale):
    return Fraction(bounds[0]+bounds[1],2*scale)


def radius(bounds, scale):
    return Fraction(bounds[1]-bounds[0],2*scale)


@dataclass(frozen=True)
class RawAxis:
    s: int
    t: int
    alpha: int
    width: int
    setup_bits: int
    positions: tuple
    broad: tuple
    narrow: tuple
    diagonal: tuple
    broad_error: Fraction
    narrow_error: Fraction
    diagonal_error: Fraction
    broad_tail: Fraction
    narrow_tail: Fraction


def build_raw_axis(s,t,alpha,width,setup_bits):
    """Return raw dyadic phases on the entire original padded axis, before normalization.

    Each matrix value is the midpoint of its truncated coefficient enclosure.
    The matrix error bounds include the full omitted periodic tails in each row.
    """
    require(isinstance(s,int) and isinstance(t,int) and 2<=s<t<2*s and t&(t-1)==0
            and gcd(s,t)==1 and isinstance(alpha,int) and alpha>=2,"invalid raw geometry")
    require(isinstance(width,int) and width>=0 and isinstance(setup_bits,int)
            and setup_bits>=8,"invalid raw precision or band")
    grid=1<<setup_bits
    pi=pi_bounds(setup_bits)
    pos=tuple((2*t*j+s)//(2*s) for j in range(s))
    selected=dict(zip(pos,range(s)))
    ratio=Fraction(t,s)
    beta=[ratio*j-k for j,k in enumerate(pos)]
    g_broad=1/(ratio*ratio*alpha**2)
    g_narrow=Fraction(alpha**2)

    @cache
    def weight(e):
        return exp_minus_pi(e,setup_bits,pi)

    def tail(g,prefactor):
        w=Fraction(2*width+1,2)
        _,first=weight(g*w*w)
        u=3*g*(2*width+2)
        # exp(-pi*g*(2W+2)) <= 1/(1+u), since pi>3 and exp(x)>=1+x.
        return 2*prefactor*Fraction(first,grid)*(1+1/u)

    broad=[]
    narrow=[]
    diagonal=[]
    e_a=e_h=e_d=d_hi=Fraction(0)
    for k in range(t):
        row_is_source=k in selected
        if row_is_source:
            a,b=weight(alpha**2*beta[selected[k]]**2)
            admit(a>0,"narrow diagonal reciprocal unresolved")
            d=(grid*grid//b,ceildiv(grid*grid,a))
        else:
            d=(grid,grid)
        diagonal.append(mid(d,grid))
        e_d=max(e_d,radius(d,grid))
        d_hi=max(d_hi,Fraction(d[1],grid))
        al=[0]*t
        au=[0]*t
        hl=[0]*t
        hu=[0]*t
        if not row_is_source:
            al[k]=au[k]=hl[k]=hu[k]=grid
        for h in range(-width,width+1):
            j=(k+h)%t
            if j not in selected:
                continue
            phase=beta[selected[j]]
            a,b=weight(g_broad*(h+phase)**2)
            al[j]+=a//alpha
            au[j]+=ceildiv(b,alpha)
            if row_is_source:
                a,b=weight(g_narrow*(h*h+2*h*phase))
                hl[j]+=a
                hu[j]+=b
        a_bounds=tuple(zip(al,au))
        h_bounds=tuple(zip(hl,hu))
        broad.append(tuple(mid(v,grid) for v in a_bounds))
        narrow.append(tuple(mid(v,grid) for v in h_bounds))
        e_a=max(e_a,sum(radius(v,grid) for v in a_bounds))
        e_h=max(e_h,sum(radius(v,grid) for v in h_bounds))
    tail_a=tail(g_broad,Fraction(1,alpha))
    tail_h=tail(g_narrow,d_hi)
    return RawAxis(s,t,alpha,width,setup_bits,pos,tuple(broad),tuple(narrow),tuple(diagonal),
                   e_a+tail_a,e_h+tail_h,e_d,tail_a,tail_h)
