"""Check the literal upper fence, 3-type integer cutoff births and timed returns."""
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
from typed_transport import NativeType, TypedPlan, column_header, decode_header

assert LOWER == 1164 and SCALES == (1, 2, 3) and WEIGHTS == (1, 45, 2025)
assert UPPER_DIVISOR == 1724


def verify_constructor_call(height):
    recipe = numerical_recipe(height)
    carrier = 1 << height

    def verify(n, types, cells, t, lower, upper, volume, ticks, rounds, **options):
        assert (n, lower, t) == (carrier, LOWER, 1 - GAUSSIAN_C)
        assert upper == 2 * (carrier // (1724 * 459))
        assert upper > 2 * (carrier // (2048 * 459))
        assert upper % 2 == 0 and 4 * 387 * (upper - 8) < n
        assert len(cells) == 125 and tuple(word.multiplicity for word in types) == WEIGHTS
        assert (volume, ticks, rounds) == (carrier**6, carrier**82, carrier**2)
        assert options == {"width": 1 << (92 * height), "delay_base": 1 << 19}
        return True

    original = grades.TypedPlan
    try:
        grades.TypedPlan = verify
        assert recipe.open()
    finally:
        grades.TypedPlan = original


heights = (ENTRY.complex_log, TERMINAL.complex_log)
assert heights == (1024, 52270)
for height in heights:
    verify_constructor_call(height)
print("PASS_LITERAL_UPPER_FENCE", UPPER_DIVISOR, LOWER, heights, flush=True)

for band, expected in ((LOWER, (4, 8, 12)), (LOWER + 2, (6, 12, 18))):
    widths = []
    for kind, scale in enumerate(SCALES):
        header = column_header(band - 8, kind)
        cols, decoded_kind = decode_header(header)
        assert (cols, decoded_kind) == (band - 8, kind) and (header & 3) == kind
        widths.append(cols * scale)
    assert tuple(width % 24 for width in widths) == expected
assert (LOWER - 8, 2 * (LOWER - 8), 3 * (LOWER - 8)) == (1156, 2312, 3468)

native = tuple(NativeType((2,), (1,), weight) for weight in WEIGHTS)
shares = {(a, 1, b, 2): Q(w, sum(WEIGHTS)) for a in range(3) for b, w in enumerate(WEIGHTS)}
t = 1 - GAUSSIAN_C
n, volume = 65536, 2**34
plan = TypedPlan(n, native, shares, t, LOWER, 4126, volume, 3, 16, delay_base=3, padding=1)
mass = Measure(t, volume, 64 * n.bit_length())
assert plan.bands.start == LOWER and (LOWER - 2, 0) not in plan.count
for band in plan.bands:
    for kind, weight in enumerate(WEIGHTS):
        assert plan.count[band, kind] == ceil(weight * mass.mass(band, band + 2)[1])
assert {(a, link.kind) for (_, a, _), ls in plan.send.items() for link in ls} == {
    (a, b) for a in range(3) for b in range(3)
}
grants = []
for recipient in range(3):
    for link in plan.receive[LOWER, recipient, 0]:
        assert link.band in (2 * LOWER, 2 * LOWER + 2) and plan.delay[LOWER] < plan.delay[link.band]
        assert link.count > 0
        grants.append((recipient, link.kind, link.band, link.count))
assert len(grants) == 18 and plan.source_width > 0 and plan.leaves_per_epoch > 0
print("PASS_LITERAL_LOWER_CUTOFF", LOWER, (1156, 2312, 3468), grants, plan.leaves_per_epoch, flush=True)
