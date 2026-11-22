"""Check both numerical grade inventories with independent log and exp intervals."""

from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import sys

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from upstream import HERE, install
install()
from independent_binary_price import log_rank, rank_price
from installations import GAUSSIAN_C, TERMINAL
from strong_complex import load_changed, word
from unpowered_price import certify

raw = word(*load_changed(HERE/"inputs"))
targets = Counter(p.rank for p in raw.targets)
paid = Counter(p.rank for p in raw.paid)


def histogram(scale):
    h = Counter(targets)
    h.subtract(paid)
    for r in targets.keys() | paid.keys():
        h[scale*r] += targets[r]-paid[r]
    h[1] += 1008
    h[Q(1,2)] -= 2016
    return h


def power(r,t):
    r = Q(r)
    a,b = rank_price(r.numerator,t)
    d,e = rank_price(r.denominator,t)
    return a/e,b/d


def margin(h,c):
    lower = upper = 0
    for r,n in h.items():
        a,b = power(r,1-c)
        lower += min(n*a,n*b)
        upper += max(n*a,n*b)
    return lower,upper


def doubled(counts):
    result = counts.copy()
    for grade, count in counts.items():
        result[8*grade] += count
    return result


old_target, old_paid = doubled(targets), doubled(paid)
old_paid[1] -= 1008
old_paid[Q(1, 2)] += 2016
before, old_cells = certify(Q(2092819, 2**29), (old_target, old_paid))
after, revised_cells = certify(Q(1071523491, 2**38), (old_target, old_paid))
assert min(before, after) > 0 and old_cells.keys() == revised_cells.keys()
assert len(revised_cells) == 54 and sum(v != revised_cells[k] for k, v in old_cells.items()) == 45
old = histogram(8)
lo,hi = Q(".0038981803447950341293615588"),Q(".0038981803447950341293615589")
assert margin(old,lo)[0] > 0 and margin(old,hi)[1] < 0
assert margin(old,TERMINAL.kappa)[1] < -Q(17,100)
for j in range(16):
    # Differentiate sum h_r*(r/16)^t. Bound the signed derivative on the full interval.
    derivative = 0
    for r,n in old.items():
        q = Q(r)/16
        a,b = log_rank(q.numerator)
        d,e = log_rank(q.denominator)
        endpoints = (*power(q,Q(j,16)), *power(q,Q(j+1,16)))
        derivative += min(n*z*y for z in (a-e,b-d) for y in (min(endpoints),max(endpoints)))
    assert derivative > 302770
assert margin(histogram(79),GAUSSIAN_C)[0] > 0
assert TERMINAL.kappa > hi
print("PASS_INDEPENDENT_RAW_CROSSING",lo,hi,"and funded 79-column dilation")
