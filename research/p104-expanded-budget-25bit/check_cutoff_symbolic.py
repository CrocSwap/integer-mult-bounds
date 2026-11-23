"""Check the literal upper fence, integer cutoff births and timed returns."""
from fractions import Fraction as Q
from dataclasses import dataclass
from hashlib import sha256
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


# Trace the real source expression with exact symbolic powers for high H.
# At small H, the same intercepted call is compared against literal integers.
@dataclass(frozen=True)
class Pow2:
    exp: int
    def __pow__(self, power):
        assert type(power) is int and power >= 0
        return Pow2(self.exp * power)
    def __floordiv__(self, divisor):
        assert type(divisor) is int and divisor > 0
        return FloorPow2(self.exp, divisor)

@dataclass(frozen=True)
class FloorPow2:
    exp: int
    divisor: int
    def __rmul__(self, factor):
        assert type(factor) is int and factor > 0
        return TimesFloorPow2(factor, self.exp, self.divisor)

@dataclass(frozen=True)
class TimesFloorPow2:
    factor: int
    exp: int
    divisor: int

class ShiftCount(int):
    def __rlshift__(self, base):
        assert base == 1
        return Pow2(int(self))

def realize(x):
    if isinstance(x, Pow2):
        return 1 << x.exp
    if isinstance(x, TimesFloorPow2):
        return x.factor * ((1 << x.exp) // x.divisor)
    return x

def call_arguments(height, symbolic):
    recipe = numerical_recipe(height)
    old_rank, old_width, original = recipe.rank_log, recipe.width_log, grades.TypedPlan
    try:
        if symbolic:
            recipe.rank_log, recipe.width_log = ShiftCount(height), ShiftCount(92*height)
        grades.TypedPlan = lambda *args, **kwargs: (args, kwargs)
        return recipe.open()
    finally:
        recipe.rank_log, recipe.width_log, grades.TypedPlan = old_rank, old_width, original

def verify_constructor_call(height):
    recipe = numerical_recipe(height)
    args, options = call_arguments(height, True)
    n, types, cells, t, lower, upper, volume, ticks, rounds = args
    assert (n, lower, t) == (Pow2(height), LOWER, 1-GAUSSIAN_C)
    divisor = UPPER_DIVISOR * recipe.ambient
    other_divisor = 2048 * recipe.ambient
    assert divisor == 1724*306 and other_divisor == 2048*306
    assert upper == TimesFloorPow2(2, height, divisor)
    assert len(cells) == 88 and tuple(word.multiplicity for word in types) == WEIGHTS
    assert (volume, ticks, rounds) == (Pow2(6*height), Pow2(82*height), Pow2(2*height))
    assert options == {"width": Pow2(92*height), "delay_base": 1 << 19}
    # For x=2^H >= 2^30, both floor separation and admission hold.
    # floor(x/a)-floor(x/b) >= floor(x*(b-a)/(a*b)).
    assert height >= 30 and (1 << 30)*(other_divisor-divisor) >= divisor*other_divisor
    assert 2*((1 << 30)//divisor) > LOWER
    # 4*258*(upper-8) < x follows from upper <= 2*x/divisor.
    assert 2*4*258 < divisor
    return {'height':height,'carrier_power':height,'volume_power':6*height,
            'ticks_power':82*height,'rounds_power':2*height,
            'width_power':92*height,'upper_divisor':divisor,
            'trace':'symbolic-exact-operator-interception'}

# Authenticate the actual open() implementation, not a rewritten stand-in.
assert sha256((Path(sys.argv[1])/'grades.py').read_bytes()).hexdigest() == '6124744b40f806c80b6f10010a72e755bc11d64a8cc9a04f5e8316799eb6f05d'
for sample in (1024, 2048):
    actual, actual_kw = call_arguments(sample, False)
    symbolic, symbolic_kw = call_arguments(sample, True)
    assert tuple(map(realize, symbolic)) == actual
    assert {k:realize(v) for k,v in symbolic_kw.items()} == actual_kw
    verify_constructor_call(sample)

heights = (ENTRY.complex_log, TERMINAL.complex_log)
assert heights == (1024, 490950)
traces = [verify_constructor_call(height) for height in heights]
print("PASS_EXACT_SYMBOLIC_UPPER_FENCE", UPPER_DIVISOR, LOWER, traces, flush=True)

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
