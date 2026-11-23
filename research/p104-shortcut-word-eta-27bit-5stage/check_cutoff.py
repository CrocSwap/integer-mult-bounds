"""Check the literal upper fence, integer cutoff births and timed returns."""
from fractions import Fraction as Q
from pathlib import Path
import sys

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from upstream import install

install()
import grades
from grades import LOWER, SCALES, UPPER_DIVISOR, WEIGHTS, numerical_recipe
from installations import ENTRY, GAUSSIAN_C, TERMINAL
from transport import Measure, ceil
from typed_transport import NativeType, TypedPlan, column_header

assert LOWER == 1874 and SCALES == (1, 2) and WEIGHTS == (5, 451)
assert UPPER_DIVISOR == 1724


def verify_constructor_call(height):
    recipe = numerical_recipe(height)
    carrier = 1 << height

    def verify(n, types, cells, t, lower, upper, volume, ticks, rounds, **options):
        assert (n, lower, t) == (carrier, LOWER, 1-GAUSSIAN_C)
        assert upper == 2 * (carrier // (1724 * 306))
        assert upper > 2 * (carrier // (2048 * 306))
        assert upper % 2 == 0 and 4*258*(upper-8) < n
        assert len(cells) == 88 and tuple(word.multiplicity for word in types) == WEIGHTS
        assert (volume, ticks, rounds) == (carrier**6, carrier**82, carrier**2)
        assert options == {"width": 1 << (92*height), "delay_base": 1 << 19}
        return True

    original = grades.TypedPlan
    try:
        grades.TypedPlan = verify
        assert recipe.open()
    finally:
        grades.TypedPlan = original


heights = (ENTRY.complex_log, TERMINAL.complex_log)
assert heights == (1024, 208653)
for height in heights:
    verify_constructor_call(height)
print("PASS_LITERAL_UPPER_FENCE", UPPER_DIVISOR, LOWER, heights, flush=True)

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
