"""Finite prime witnesses (PR1786, chafreaky, unchanged), a real underflow control and exact power checks.

The small prime fixtures are not a verification of the asymptotic prime
theorem or its enormous eventual cutoff at the headline epsilon.
"""
import argparse
import json
import math
from fractions import Fraction as F
from pathlib import Path

if not __debug__:
    raise RuntimeError('Assertions must be enabled')
ap = argparse.ArgumentParser()
ap.add_argument('--out', type=Path, required=True)
args = ap.parse_args()

def prime(n):
    if n < 2 or (n % 2 == 0 and n != 2):
        return False
    return all(n % d for d in range(3, math.isqrt(n)+1, 2))

def interval(p, t):
    return F((2*p*p-1)*t, 2*p*p), F((4*p*p-1)*t, 4*p*p)

def valid(p, targets, primes):
    if len(primes) != len(targets) or len(set(primes)) != len(primes):
        return False
    if any(t < 2 or t & (t-1) for t in targets):
        return False
    for t, q in zip(targets, primes):
        lo, hi = interval(p, t)
        if not (prime(q) and lo < q <= hi and math.gcd(q, t) == 1):
            return False
        theta = F(t, q)-1
        if not F(1, 4*p*p) < theta <= F(1, 2*p*p-1):
            return False
    return F(1, 2) < F(math.prod(primes), math.prod(targets)) < 1

fixtures = []
for p in (16, 32, 64, 128, 256):
    targets = [2**27]*3+[2**28]*3
    chosen = []
    for t in targets:
        lo, hi = interval(p, t)
        q = lo.__floor__()+1
        while q <= hi and (q in chosen or not prime(q)):
            q += 1
        assert q <= hi
        chosen.append(q)
    assert valid(p, targets, chosen)
    duplicate = chosen[:]
    duplicate[1] = duplicate[0]
    even = chosen[:]
    even[0] = targets[0]
    outside = chosen[:]
    q = interval(p, targets[0])[1].__floor__()+1
    while not prime(q):
        q += 1
    outside[0] = q
    non_dyadic = targets[:]
    non_dyadic[0] = 2*chosen[0]
    controls = {
        'duplicate_source_prime': not valid(p, targets, duplicate),
        'dyadic_number_used_as_prime': not valid(p, targets, even),
        'prime_outside_requested_interval': not valid(p, targets, outside),
        'non_dyadic_target': not valid(p, non_dyadic, chosen),
    }
    assert all(controls.values())
    fixtures.append(dict(p=p, targets=targets, primes=chosen,
        theta=[str(F(t, q)-1) for t, q in zip(targets, chosen)],
        source_to_target_ratio=str(F(math.prod(chosen), math.prod(targets))),
        rejected_controls=controls))

# Real counterexample to keeping the old Cp-bit absolute weight precision.
# w_min=exp(-a/(4 theta)). Since log(2)<1, E>P implies w_min<2^-P.
p = 32
example = next(x for x in fixtures if x['p'] == p)
theta = F(example['theta'][0])
# Here log(16p)=9 log 2. Bounds 2/3<log2<7/10 and 3<pi<22/7
# put 4 log(16p)/pi strictly between 4 and 9; the legal alpha is 3.
assert F(4*9)*F(2, 3)/F(22, 7) > 4
assert F(4*9)*F(7, 10)/3 < 9
assert sum(F(7, 10)**j/math.factorial(j) for j in range(5)) > 2
alpha = 3
low_a, high_a = F(27), F(198, 7)
low_exponent, high_exponent = low_a/(4*theta), high_a/(4*theta)
online = 128*p
L = (p-1).bit_length()
setup = online+64*p*p*L
assert low_exponent > online
assert F(setup-online, 2) > high_exponent
underflow = dict(p=p, alpha=alpha, a_lower=str(low_a), a_upper=str(high_a),
    theta=str(theta), source_prime=example['primes'][0], target=example['targets'][0],
    negative_log_weight_lower=str(low_exponent), online_precision=online,
    old_precision_rounds_weight_to_zero=True, setup_precision=setup,
    relative_error_exponent_margin=str(F(setup-online, 2)-high_exponent))

# Universal power relationships used by the written generic locality lemma.
norm_power = inverse_power = 10
scale_power = 2*norm_power
gap_power = 2*(norm_power+inverse_power)
iteration_power = gap_power+2
band_power = 1
radius_power = iteration_power+band_power
halo_power, core_power = 48, 128
assert (scale_power, gap_power, iteration_power, radius_power) == (20, 40, 42, 43)
assert halo_power > radius_power and core_power > halo_power+1
assert 40 < radius_power  # A=p^40 is not covered by this conservative witness.
assert 7**16 < 2**45
assert 7**5 > 2**14       # tau=14/5 is unsupported by the chosen Strassen format.

report = dict(status='PASS_FINE_PADDING_FINITE_CONTROLS',
    prime_fixtures=fixtures, prime_witness_count=sum(len(x['primes']) for x in fixtures),
    primality_method='Deterministic trial division through integer square root',
    weight_underflow_control=underflow,
    generic_locality=dict(norm_power=norm_power, inverse_power=inverse_power,
        scale_power=scale_power, contraction_gap_power=gap_power,
        iteration_power=iteration_power, radius_power=radius_power,
        halo_power=halo_power, core_power=core_power),
    strassen_power_gap=2**45-7**16,
    scope='Finite arithmetic fixtures and failure witnesses only. The cited prime theorem, analytic conditioning and circuit/halo lemmas remain written mathematical inputs; no finite cutoff or full multiplication implementation is verified here.')
args.out.write_text(json.dumps(report, sort_keys=True, indent=2)+'\n')
print(report['status'], 'prime witnesses', report['prime_witness_count'])
