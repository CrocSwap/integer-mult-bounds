#!/usr/bin/env python3
"""Exact complete residual histogram and moment for the paired complex network.

Research check: use PR #10's whole-residual child on every nonzero edge.
This supplies complex-layer headroom, not a new multiplication witness.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import isqrt
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from paired_complex import PairedComplex
from complex_circuit import Checks, compile_roles
from prime_field_network import complex_counts
from search_network import log_integer_bounds
from prepare_layers import serializable


class RankTrace:
    def __init__(self, dimensions):
        self.dim = list(dimensions)
        self.histogram = Counter()
        self.descents = []
        self.path_loss = [0]*len(dimensions)
        self.path_rank = [0]*len(dimensions)

    def gate(self, roles, dimension):
        roles = set(roles)
        for role in roles:
            old = self.dim[role]
            rank = abs(dimension-old)
            if rank:
                self.histogram[rank] += 1
            descent = max(0, old-dimension)
            if descent:
                self.descents.append(descent)
            self.path_loss[role] += descent
            self.path_rank[role] += rank
            self.dim[role] = dimension
        loss = max(self.path_loss[r] for r in roles)
        rank = max(self.path_rank[r] for r in roles)
        for role in roles:
            self.path_loss[role], self.path_rank[role] = loss, rank


def invocation(c, code, dimensions, stage, inverse):
    """Materialize physical ranks, including the shared stage 1--3 bank.

    Stage one stops its scratch at h. Stage three starts that same bank at h;
    its first use therefore charges the join exactly once. The middle-stage
    bank enters at zero and exits at m. Data terminals stay at stage endpoints.
    """
    h, m, v, r = c.h, c.h**3, len(c.triples), code['roles']
    x = {t:i for i,t in enumerate(c.triples)}
    y = {t:v+i for i,t in enumerate(c.triples)}
    side = lambda slot: 2*v+slot
    centers = tuple(range(2*v+r, 2*v+r+h+1))
    a = h**(stage-1)
    low, high = (a-1)*h, a*h
    trace = RankTrace([a]*v+[a-1]*v+[h if stage==3 else 0]*(r+h+1))
    pieces = {t:[] for t in c.triples}
    for i,slot in code['outputs'].items():
        pieces[c.pieces[i][0]].append(side(slot))

    def mix(mode, reverse=False):
        for node,ins,outs in reversed(code['gates']) if reverse else code['gates']:
            frame = {'low':low, 'high':high, 'label':low+dimensions[node],
                     'complement':high-dimensions[node]}[mode]
            trace.gate((side(s) for s in ins+outs), frame)

    def inject(bank, frame):
        for t in c.triples:
            trace.gate([bank[t]]+pieces[t], frame)

    def copy(bank, frame):
        for t,slot in code['sources'].items():
            trace.gate((bank[t], side(slot)), frame)

    def central(bank, frame):
        trace.gate(tuple(bank.values())+centers, frame)

    if not inverse:
        mix('low'); inject(y,low); mix('low',True); central(y,low)
        copy(x,low+1); central(x,high); central(y,low)
        mix('label'); inject(y,high-1); mix('high',True)
        central(x,high); copy(x,high)
    else:
        copy(y,a-1); central(y,low); mix('low'); inject(x,low+1)
        mix('complement',True); central(x,high); central(y,low)
        copy(y,high-1); central(x,high); mix('high'); inject(x,high)
        mix('high',True)
    for role in x.values(): trace.gate((role,),high)
    for role in y.values(): trace.gate((role,),high-1)
    for role in range(2*v,len(trace.dim)):
        trace.gate((role,),h if stage==1 else m)
    assert trace.descents == [h]*(h+1)
    assert max(trace.path_loss) == h
    assert max(trace.path_rank) <= m+2*h
    return trace.histogram


def counts(h=28):
    c = PairedComplex(h)
    checks, code = Checks(c), compile_roles(c)
    dimensions = {node:checks.label(node).dim for node in c.active}
    histogram = Counter()
    for stage,inverse in ((1,False),(2,True),(3,False)):
        histogram.update(invocation(c,code,dimensions,stage,inverse))
    v,m,R = len(c.triples),h**3,code['roles']
    width = 2*v*v*(v+R+h+1)
    total = 2*v**3*m-2*v**3+2*v*v*(R+h+1)*m+6*v*v*h*(h+1)
    histogram = {rank:copies*v*v for rank,copies in sorted(histogram.items())}
    assert sum(rank*copies for rank,copies in histogram.items()) == total
    assert max(histogram) == m-2*h < m
    assert histogram[m-2*h] == v*v*(R+h+1)
    assert histogram[m-h*h] == v*v*(R+h+1)
    if h==28:
        baseline = complex_counts()
        assert width==baseline['W'] and total==baseline['s']
    return dict(h=h,m=m,v=v,roles=R,W=width,s=total,eta=1-Q(total,width*m),
                residual_histogram=histogram)


def sqrt_upper(x, grid=10**12):
    n = isqrt(x.numerator*grid*grid//x.denominator)+1
    result = Q(n,grid)
    assert result*result > x
    return result


def guard(n,beta=Q(1,1000),zeta=Q(1,10000)):
    """Convex path enclosure, allowing every edge to be one child.

    For rho=3/2, the largest sum of powers with total rank <=q and each
    rank <=A is A^rho+(q-A)^rho, since A<q<2A. No path enumeration is needed.
    """
    h,m,W,s = (n[k] for k in ('h','m','W','s'))
    q,A = m+6*h,max(n['residual_histogram'])
    assert A<q<2*A and A<m
    chunks = [Q(A,m),Q(q-A,m)]
    bound = sum((r*sqrt_upper(r) for r in chunks),Q(0))
    theta = Q(999,1000)
    assert bound<theta
    E=64*(W+m+1)**3
    assert 36*W**3+4*s+4*W+8*m+4<E
    constant=1000*(E+16*m+1)
    assert constant*(1-theta)>=E and constant>=16*m
    raw=128*m*(1+1/zeta)*constant
    C0=-(-raw.numerator//raw.denominator)
    return dict(q=q,maximum_residual=A,rho=Q(3,2),extremal_chunks=chunks,
                path_moment_upper=bound,theta_upper=theta,E=E,
                dependency_constant=constant,C0=C0,C1=Q(3,2)-beta/2+zeta)


def moment_data(n):
    weights, logs = [],[]
    for rank,copies in n['residual_histogram'].items():
        weights.append(Q(rank*copies,n['W']*n['m']))
        upper = log_integer_bounds(n['m'])[1]-log_integer_bounds(rank)[0]
        # Compact outward rounding keeps the exact rational moments readable.
        logs.append(Q(-(-upper.numerator*10**9//upper.denominator),10**9))
    assert sum(weights)==1-n['eta']
    return weights,logs


def moment(a,weights,logs):
    assert all(0<=a*ell<1 for ell in logs)
    return sum((w/(1-a*ell) for w,ell in zip(weights,logs)),Q(0))


def certificate(h=28):
    n=counts(h); weights,logs=moment_data(n)
    lo,hi,grid=0,10**7,10**12
    assert moment(Q(hi,grid),weights,logs)>1
    while hi-lo>1:
        mid=(hi+lo)//2
        if moment(Q(mid,grid),weights,logs)<1:lo=mid
        else:hi=mid
    a=Q(lo,grid)
    reference=ROOT/'references/pr10'
    manifest=json.loads((reference/'SOURCE.json').read_text())
    for name,digest in manifest['sha256'].items():
        assert sha256((reference/name).read_bytes()).hexdigest()==digest
    paths=('scripts/experiments/complex_all_residuals.py',
           'scripts/experiments/assembly_breakthrough_guard.py',
           'scripts/paired_complex.py','scripts/paired_triple_circuit.py',
           'scripts/complex_circuit.py','scripts/prime_field_network.py',
           'scripts/search_network.py','tests/test_complex_all_residuals.py',
           'tests/test_complex_residual_histogram.py',
           'docs/research/complex-all-residuals.md')
    return dict(status='COMPLEX LAYER HEADROOM; NO NEW MULTIPLICATION WITNESS',
                counts=n,complex_saving=a,rank_mass_weights=weights,
                logarithm_upper_bounds=logs,moment_upper=moment(a,weights,logs),
                next_grid_moment=moment(Q(hi,grid),weights,logs),guard=guard(n),
                batching_reference=manifest,
                proof_sha256={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in paths},
                scope='Whole-residual batching uses the pinned PR #10 complex row and '
                      'guard induction arguments. Full finite frame correctness remains '
                      'the inherited paired complex construction. No bit saving changes.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h',type=int,default=28)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(); result=certificate(args.h)
    if args.output:
        args.output.write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS complex saving',result['complex_saving'],'guard C1',result['guard']['C1'],
          'moment gap',float(1-result['moment_upper']))
