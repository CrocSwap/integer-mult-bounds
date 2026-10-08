"""Deterministic bounded-minor certificate for the fixed middle-axis basis.

Copyright 2026 icekylinx, Apache-2.0. AI-assisted integration of the supplied
rankone_30_internal_profiles proof and certificate; no probabilistic tests.
"""
from math import comb, factorial, isqrt, prod


def require(condition, message):
    if not condition:
        raise ValueError(message)


def mersenne_prime(exponent):
    require(exponent >= 3 and all(exponent % d for d in range(2, isqrt(exponent)+1)),
            'Lucas–Lehmer requires a prime exponent')
    modulus = (1 << exponent)-1
    state = 4
    for _ in range(exponent-2):
        state = (state*state-2) % modulus
    require(state == 0, 'Lucas–Lehmer primality certificate failed')
    return modulus


def verify(certificate, profile):
    require(certificate['h'] == profile['h'] == 30, 'Wrong exactness dimension')
    primes = [mersenne_prime(e) for e in (61, 31, 19)]
    cases = ((2, 75516, 561108), (3, 5394, 29316), (4, 10788, 344978))
    require(len(certificate['cases']) == len(cases), 'Wrong number of minor cases')
    bounds = []
    for case, (rank, denominator, numerator) in zip(certificate['cases'], cases):
        require((case['correction_rank_bound'], case['common_denominator_upper'],
                 case['correction_numerator_absolute_upper']) ==
                (rank, denominator, numerator), 'Changed rational-frame bound')
        bound = sum(comb(30,j)*factorial(j)*numerator**j*denominator**(rank-j)
                    for j in range(rank+1))
        used_primes = primes if rank == 4 else primes[:1]
        require(case['primes'] == used_primes, 'Wrong exactness primes')
        require(int(case['all_minor_numerator_upper']) == bound, 'Minor bound mismatch')
        require(int(case['prime_product']) == prod(used_primes), 'Prime product mismatch')
        require(prod(used_primes) > bound, 'Insufficient CRT modulus for exact zeros')
        require(min(used_primes) > denominator, 'Possible noninvertible denominator')
        bounds.append(bound)
    for actual, expected in (
            ('frames', 'distinct_frames'),
            ('distinct_matrices', 'rank_above_two_matrices'),
            ('crt_matrices', 'matrices_requiring_three_primes'),
            ('crt_disagreements', 'disagreements_between_the_three_modular_profiles'),
            ('R', 'role_count'), ('loss', 'loss'), ('rank_sum', 'total_internal_rank')):
        require(profile[actual] == certificate[expected], 'Wrong profile count: '+actual)
    require(profile['crt_disagreements'] == 0, 'Selected modular profiles disagree')
    require(profile['field_prime'] == primes[0], 'Wrong primary profile field')
    require(sum(t*c for t,c in enumerate(profile['blocks'])) == profile['rank_sum'],
            'Block rank mass mismatch')
    return dict(deterministic_primality=True, bounded_minors_exact=True,
                primes=primes, numerator_bounds=bounds,
                all_selected_profiles_recomputed=True)
