# SPDX-License-Identifier: Apache-2.0
"""Directed rational outer inequalities for the inherited parameterized signed caller.

The 54 strict and four functional expressions follow the P104 dual-supplier
gate at 4f7c67ae387cc91580f469aeda4d508b372b9ec1. The positive and ordinary
caps come independently from the actual single-band profiles.
"""
from fractions import Fraction as Q


def margins(k,g,ordinary,positive):
    a,b,q=k+4*g,k+5*g,k+3*g
    ep,be=1-g,1-3*g
    r0=g/10
    sigma,tau=1-b,1-a
    internal=tau+(1-g)*max(sigma-tau,0)
    leaf=sigma+g*(1-sigma)
    lam=1-(q+a)/2
    xi=ep*(1+q)-Q(3,32)+g
    key=be+1-ep
    powers=[ep*q,a,1-ep+q*be,1-ep+a*be,1-ep+be,Q(3,32)+xi-ep,
            xi+Q(1,2)-ep,ep,1-(ep+be+48-128+2)]
    strict=[ordinary-a,b-a,q,b-q,a-q,g,1-g,(1-g)*b-a,1-internal-q,1-leaf-q,
            lam-tau,lam-sigma,lam-internal,1-q-lam,1-q-leaf,ep,1-ep,xi-Q(1,2),ep-xi,
            be,ep-be,1-be,1-(2*xi-2)-r0-be,1-(2*xi-2)-be,1-ep-r0,1-ep,r0,1-key,
            1-be-2*(1-ep),128-48-be,g,ep-a,Q(1,32)-b,Q(2**45-7**16),Q(2),2-xi,
            Q(5),1-be,1-be,1-ep,powers[2]-powers[0],g,k-Q('.001730970419199163702738'),
            1-ep,Q(11,2)]+[x-k for x in powers]
    functional=[1-be,be*(1-Q(3,1000)),128-48-ep-be-1,be*(1-Q(1,250))]
    assert len(strict)==54 and len(functional)==4
    return strict,functional,positive-b


def qualify(k,g,ordinary,positive):
    strict,functional,paid=margins(k,g,ordinary,positive)
    if min(*strict,*functional,paid)<=0:
        raise ArithmeticError('signed outer budget has an unfunded inequality')
    return {'strict':len(strict),'functional':len(functional),
            'smallest_margin':str(min(*strict,*functional,paid)),
            'ordinary_margin':str(ordinary-k-4*g),'positive_margin':str(paid)}
