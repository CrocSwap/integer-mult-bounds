#!/usr/bin/env python3
"""Exact complete-complement series, retaining all recursive costs.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from intervals import I, need, rank_power
from certificate import inventory, ALPHA, coefficient


def capacity(s, terms=512):
    need(type(terms) is int and 2 <= terms <= 2048,'bounded series terms')
    s=Q(s)
    need(0 < s < 1,'binomial exponent domain')
    paid,targets,m = inventory()
    ranks=sorted(set(paid)|set(targets))
    pa={r:rank_power(r,ALPHA) for r in ranks}
    # Group the exact pair expression into at most 16 geometric sequences.
    weights={r:I(0) for r in ranks}
    for r,pr in paid.items():
        for k,wk in targets.items():
            if k>r:
                weights[k]=weights[k]+pr*wk*pa[r]
                weights[r]=weights[r]-pr*wk*pa[k]
    powers={r:I(1) for r in ranks}
    a, total, tail = I(s), I(0), I(1)
    for j in range(1,terms+2):
        for r in ranks:
            powers[r]=powers[r]*Q(r,m)
        b=sum((weights[r]*powers[r] for r in ranks),I(0))/(j-ALPHA)
        if j <= terms:
            total=total+a*b
            tail=tail*(1-s/j)
            a=a*(j-s)/(j+1)
        else:
            # Positive omitted binomial series <= tail*x^(terms+1).
            remainder=tail*b
    return I(total.lo,total.hi+max(Q(0),remainder.hi)), remainder


def full_margin(s, terms=512):
    paid,targets,m=inventory()
    c=coefficient(paid,targets,I(s))
    cap,tail=capacity(s,terms)
    exit_term=(c['leaf']+c['boundary'])*rank_power(m,I(-Q(s)))/(I(s)-ALPHA)
    return cap-exit_term, cap, tail


def full_certificate():
    results={}
    for s,wanted in [(Q('0.99738855928'),-1),(Q('0.99738855931'),1),
                     (Q('0.99739'),1)]:
        margin,cap,tail=full_margin(s)
        need(margin.hi<0 if wanted<0 else margin.lo>0,'complete recurrence sign')
        results[str(s)]={'margin':margin.decimal(8),'capacity':cap.decimal(8),
                          'series_tail_upper':I(tail.hi).decimal(8)}
    return {'status':'PASS_EXACT_COMPLEMENT_SIGNS','terms':512,
            'scalar_exponent_interval':['0.99738855928','0.99738855931'],
            'scalar_saving_interval':['0.00261144069','0.00261144072'],
            'explicit_upper_exponent':'0.99739','endpoint_certificates':results,
            'no_new_kappa':True}


def series_controls():
    """Exact square-root fixtures independently challenge the positive tail."""
    checks, omissions = 0, 0
    for terms in (16,32):
        for u in (Q(0),Q(1,4),Q(1,3),Q(1,2),Q(1)):
            x, exact = 1-u*u, 1-u
            coefficient, tail, total = Q(1,2),Q(1),Q(0)
            for j in range(1,terms+1):
                total += coefficient*x**j
                tail *= 1-Q(1,2*j)
                coefficient *= (j-Q(1,2))/(j+1)
            need(total <= exact <= total+tail*x**(terms+1),
                 'independent exact square-root binomial control')
            checks += 1
            if x>0:
                need(total<exact,'omitted positive series tail was accepted')
                omissions += 1
    rejected = 0
    for thunk in (lambda:capacity(Q(0)),lambda:capacity(Q(1)),
                  lambda:capacity(Q(1,2),0),lambda:capacity(Q(1,2),2049)):
        try:
            thunk()
        except ValueError:
            rejected += 1
        else:
            raise ValueError('invalid series parameter accepted')
    return {'exact_square_root_fixtures':checks,'missing_tail_rejections':omissions,
            'domain_rejections':rejected}


if __name__=='__main__':
    import json
    print(json.dumps(full_certificate(),indent=2))
