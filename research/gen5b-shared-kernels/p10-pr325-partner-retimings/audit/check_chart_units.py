from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_frame_binding()
contract.verify_bank()
"""Audit actual emitted endpoint-chart coefficient units without upstream code."""
from pathlib import Path
from fractions import Fraction
import gzip, hashlib, json

if not __debug__:
    raise RuntimeError('Assertions must be enabled')
HERE = contract.AUDIT
GLOBAL = contract.GLOBAL
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
programs = json.loads(gzip.decompress((GLOBAL/'normalizers.json.gz').read_bytes()))['chart_programs']
assert len(programs) == 120
values = []
for program in programs.values():
    for name in ('basis_columns', 'inverse'):
        values.extend(Fraction(v) for row in program[name] for v in row)
    for kind, first, second, coefficient in program['factors']:
        assert kind in ('add', 'scale', 'swap')
        if kind != 'swap':
            value = Fraction(coefficient)
            values.append(value)
            if kind == 'scale':
                assert value
                values.append(1/value)
assert all(abs(v.numerator) < 2**80 and v.denominator < 2**80 for v in values)
assert max(abs(v.numerator) for v in values) == 33
assert max(v.denominator for v in values) == 198
# Reject a factor whose nonzero numerator is not a guaranteed retained-prime unit.
assert not (abs(Fraction(2**80 + 1).numerator) < 2**80)
result = {
    'status': 'PASS_FRESH_GLOBAL_CHART_UNIT_BOUNDS',
    'normalizer_sha256': sha(GLOBAL/'normalizers.json.gz'),
    'checker_sha256': sha(__file__),
    'actual_charts': len(programs),
    'maximum_abs_numerator_including_inverse_scales': 33,
    'maximum_denominator': 198,
    'every_nonzero_factor_and_inverse_denominator_below_2pow80': True,
    'out_of_bound_coefficient_rejected': True,
    'scope': 'The 120 actual global endpoint charts and their inverse/factor coefficients are defined at every retained prime above 2^80. This does not certify all other inherited prime interfaces.'
}
(HERE/'GLOBAL-CHART-BOUNDS.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
