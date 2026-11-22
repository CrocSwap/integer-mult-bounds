"""Check the true weighted Gaussian exterior owner at both installed ranks."""

from fractions import Fraction as Q
from itertools import islice
import json
from pathlib import Path
import sys

RUNTIME = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RUNTIME))
from upstream import install

install()
from upstream import HERE

_, _, _, source = install()
from strong_complex import artifacts
from clock_ports import clock_word
from grades import numerical_recipe, WEIGHTS
from installations import ENTRY, TERMINAL, GAUSSIAN_C
from unpowered_price import certify
from periodic import Job
from raw48 import ComplexRaw
from transport import axes, ceil

A = artifacts(source / "research/grade14-native-realization", HERE / "inputs")
w = clock_word(A)
recipe = numerical_recipe(TERMINAL.complex_log)
targets, paid = recipe.targets, recipe.paid
c = GAUSSIAN_C
margin, flows = certify(c, (targets.histogram, paid.histogram))
assert margin > 0 and flows == recipe.cells and flows[112, 258] == 1
assert paid.variants[0].histogram[112] == 0 and paid.variants[1].histogram[112] > 0
assert (
    targets.variants[0].histogram[258] == 0
    and targets.variants[1].histogram[258] == 624
)
pi = flows[112, 258] * WEIGHTS[1] / targets.histogram[258]
assert pi == Q(1, 624)
roots = tuple(
    p.tag for p in w.targets if p.rank == 129 and p.tag[:2] == ("root", "rotated")
)
assert len(roots) == 384


class Column:
    window = 1
    swap = None


class Field:
    def __init__(self):
        self.swaps = []

    def swap(self, l, r, n, service):
        self.swaps.append((l, r, n))


out = []
for H in (ENTRY.complex_log, TERMINAL.complex_log):
    M = 1 << H
    U = 2 * (M // (2048 * 306))
    e = 2 * (3 * U // 8)
    lo, hi = Q(e * 258, 112), Q((e + 2) * 258, 112)
    assert U < lo < hi < M
    assert 90 * (hi - lo) * M * pi > 4
    size = 258 * (e - 8)
    period = 4 * ceil(Q(M, 4 * size))
    tickets = tuple(islice(axes(M, size, period, 0), 3))
    f = Field()
    raw = ComplexRaw(A, {}, Column(), low=0, bundle=1, slots=M)
    # The alignment performs these first three iterations before seeing any
    # other slot. The full physical job is exponentially larger.
    raw.align(f, Job(0, tickets), tuple(range(3)))
    assert period == 1620 and tickets == (0, 324, 648) and f.swaps[0] == (1, 324, 1)
    out.append(
        dict(
            H=H,
            cell=[1, 112, 1, 258],
            share=str(pi),
            rotated_roots=len(roots),
            first_root=roots[0],
            period=period,
            tickets=tickets,
            first_swap=f.swaps[0],
        )
    )
print(json.dumps(out, indent=2))
