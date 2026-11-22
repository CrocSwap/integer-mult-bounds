"""Check actual integer births and timed returns at the literal lower cutoff."""
from fractions import Fraction as Q
from pathlib import Path
import sys

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from upstream import install

install()
from grades import LOWER, SCALES, WEIGHTS
from installations import GAUSSIAN_C
from transport import Measure, ceil
from typed_transport import NativeType, TypedPlan, column_header

assert LOWER == 1874 and SCALES == (1, 2) and WEIGHTS == (5, 451)
for band, expected in ((LOWER, (2, 0)), (LOWER+2, (0, 0))):
    widths = []
    for kind, scale in enumerate(SCALES):
        header = column_header(band-8, kind)
        assert header % 2 == kind and header - kind == band-8
        widths.append((header-kind)*scale)
    assert tuple(width % 4 for width in widths) == expected
assert (LOWER-8, 2*(LOWER-8)) == (1866,3732)

native = tuple(NativeType((2,), (1,), weight) for weight in WEIGHTS)
shares = {(a,1,b,2):Q(w,sum(WEIGHTS)) for a in range(2) for b,w in enumerate(WEIGHTS)}
t = 1-GAUSSIAN_C
n, volume = 65536, 2**29
plan = TypedPlan(n, native, shares, t, LOWER, 4126, volume, 3, 16, delay_base=3, padding=1)
mass = Measure(t, volume, 64*n.bit_length())
assert plan.bands.start == LOWER and (LOWER-2,0) not in plan.count
for band in plan.bands:
    for kind, weight in enumerate(WEIGHTS):
        assert plan.count[band,kind] == ceil(weight * mass.mass(band,band+2)[1])
assert {(a,link.kind) for (_,a,_),ls in plan.send.items() for link in ls} == {(0,0),(0,1),(1,0),(1,1)}
grants = []
for recipient in range(2):
    for link in plan.receive[LOWER,recipient,0]:
        assert link.band in (2*LOWER,2*LOWER+2) and plan.delay[LOWER] < plan.delay[link.band]
        assert link.count > 0
        grants.append((recipient,link.kind,link.band,link.count))
assert len(grants) == 8 and plan.source_width > 0 and plan.leaves_per_epoch > 0
print('PASS_LITERAL_LOWER_CUTOFF', LOWER, (1866,3732), grants, plan.leaves_per_epoch, flush=True)
