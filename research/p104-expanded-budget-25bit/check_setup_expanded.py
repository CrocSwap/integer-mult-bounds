"""Check the charged 25-bit installer for the exact high profile.

The fixed native-constructor and serial budget are distinct from WASI tracing,
recurring activation, and an execution of the astronomical terminal input.
"""
from hashlib import sha256
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
import json
import sys
from tempfile import TemporaryDirectory

if not __debug__:
    raise RuntimeError('Assertions must be enabled')
runtime = Path(sys.argv[1]).resolve()
portable = Path(sys.argv[2]).resolve()
pins = {
    'grades.py': '6124744b40f806c80b6f10010a72e755bc11d64a8cc9a04f5e8316799eb6f05d',
    'transport.py': '9eb8f0d77a4c53fc4fddffdfe198cab930b6d1f49e2b6d43c970397051bb7818',
    'retimed_supplier.py': '2a87c2781ca93fa854aee098dcb7c50a65f2a46267ba926e3997b442e5a25f2c',
    'installations.py': '509c7ffec6f9bb26178a095ec9c9b219331b544a1ac7e6a53d0efe3fa17c8215',
}
for filename, digest in pins.items():
    assert sha256((runtime / filename).read_bytes()).hexdigest() == digest, filename
sys.path[:0] = [str(runtime), str(portable)]
from upstream import install
install()
import installations
from band_product import prepare_native, production_supplier
from compiler_state import construct
from grades import WeightedRecipe
from record_census import inspect
from tape_directory import dump
from transport import Recipe

entry, terminal = installations.ENTRY, installations.TERMINAL

def scalar_values(profile):
    return {
        'kappa_numerator': profile.kappa.numerator,
        'kappa_denominator': profile.kappa.denominator,
        'eta_numerator': profile.eta.numerator,
        'eta_denominator': profile.eta.denominator,
        'positive_stop_denominator': profile.positive_stop_denominator,
    }

def bounded_scalars(profile):
    values = scalar_values(profile)
    return (all(type(x) is int and abs(x).bit_length() <= 128 for x in values.values())
            and profile.positive_stop_denominator > 0)

assert list(installations.PROFILES.values()) == [entry, terminal]
assert all(bounded_scalars(profile) for profile in installations.PROFILES.values())
scalar_bits = {name: {key: abs(value).bit_length() for key, value in scalar_values(profile).items()}
               for name, profile in installations.PROFILES.items()}
oversized = {
    'kappa_numerator': replace(terminal, kappa=Fraction(1 << 128, 1)),
    'kappa_denominator': replace(terminal, kappa=Fraction(1, 1 << 128)),
    'eta_numerator': replace(terminal, eta=Fraction(1 << 128, 1)),
    'eta_denominator': replace(terminal, eta=Fraction(1, 1 << 128)),
    'positive_stop_denominator': replace(terminal, positive_stop_denominator=1 << 128),
    'nonpositive_stop_denominator': replace(terminal, positive_stop_denominator=0),
}
assert all(not bounded_scalars(profile) for profile in oversized.values())
heights = (*entry.rank_logs, entry.complex_log, *terminal.rank_logs, terminal.complex_log)
assert heights == (3000, 3080, 1024, 8192, 38102, 604362, 18845936)
assert len(heights) == 7 and all(1024 <= h < 2**25 for h in heights)
assert 92*(2**25-1) < 2**32 and 1024*(2**25-1)+3 < 2**35
carrier_steps = 2*2048*(2**25+1)
scalar_steps = 7*2**24
assert carrier_steps + scalar_steps == 137556398080 < 2**40
w, n = 2**38, 2**68 + 2**40
h = 2*w + 2
store = 4*w*n
lookup = 8*store*512*128
local = 2**16*(h+4)*(7*h+9) + 8*2**16*(h+4)**2
setup = (n+1)*(lookup+local+2**120)*2**32
assert setup == 217364571993743287866367176320080817069553173293686105666269057384448
assert setup < 2**228
saved = Recipe.open, Recipe.width, WeightedRecipe.open, WeightedRecipe.width

def forbidden(*args, **kwargs):
    raise AssertionError('Fixed constructor tried to materialize a native width/calendar')

Recipe.open = forbidden
Recipe.width = property(forbidden)
WeightedRecipe.open = forbidden
WeightedRecipe.width = property(forbidden)
try:
    state = construct()
    layers = state[0]
    assert [[r.rank_log for r in layer] for layer in layers] == [list(heights[:3]), list(heights[3:])]
    assert tuple(prepare_native(terminal)) == layers[1]
    assert all(r.width_log == 92*r.rank_log for layer in layers for r in layer)
    assert all(r.targets is state[1].targets and r.paid is state[1].paid and r.cells is state[1].cells
               for layer in layers for r in layer[:-1])
    assert layers[0][-1].cells is layers[1][-1].cells
    assert layers[0][-1].targets is layers[1][-1].targets
    supplier = production_supplier(terminal.complex_log, terminal.positive_stop_denominator)
    assert supplier.recipe is layers[1][-1]
    assert supplier.carrier.bit_length() == terminal.complex_log+1 and supplier.carrier.bit_count() == 1
    with TemporaryDirectory(prefix='expanded-setup-directory-') as temp:
        path = Path(temp) / 'directory.dag'
        with path.open('wb') as stream:
            count = dump(stream,state)
        census = inspect(path)
        digest = sha256(path.read_bytes()).hexdigest()
        assert count == census['records'] == 2407819
        assert census['largest_integer_bits'] < 2**38 and census['bytes'] < 2**38
finally:
    Recipe.open, Recipe.width, WeightedRecipe.open, WeightedRecipe.width = saved
print('PASS_EXPANDED_SETUP', json.dumps({
    'heights': heights, 'max_parameter_bits': max(heights).bit_length(),
    'profile_scalar_encoding_bits': scalar_bits, 'scalar_guard_bits': 128,
    'oversized_or_invalid_scalar_controls_rejected': sorted(oversized),
    'actual_terminal_carrier_bits': supplier.carrier.bit_length(),
    'directory_records': count, 'directory_bytes': census['bytes'],
    'largest_directory_integer_bits': census['largest_integer_bits'], 'directory_sha256': digest,
    'matches_recorded_directory': digest == '09acde5f62a913bd4c22b38b4e4bca849e1459ba1ec2f83e9699507286909fb7',
    'extra_action_ceiling': 2**40, 'added_carrier_scalar_steps': carrier_steps+scalar_steps,
    'serial_transition_upper': setup, 'power_of_two_upper': 228,
    'scope': 'native fixed constructor and serial upper bound; no new WASI trace',
},sort_keys=True), flush=True)
