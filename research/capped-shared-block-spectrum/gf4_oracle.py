#!/usr/bin/env python3
"""Independent F4 all-rank/all-cap census through dimension three.

Field elements are 0,1,alpha,alpha+1 with alpha^2=alpha+1.
New packed-column action/elimination engine; no predecessor or F2 code import.
@CubeJerry + substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import time


def require(ok, message):
    if not ok:
        raise ValueError(message)


def scale(vector, coefficient, low_mask):
    if coefficient == 0:
        return 0
    if coefficient == 1:
        return vector
    low, high = vector & low_mask, (vector >> 1) & low_mask
    alpha_times = high | ((low ^ high) << 1)
    return alpha_times if coefficient == 2 else alpha_times ^ vector


def image(columns, vector, low_mask):
    result, j = 0, 0
    while vector:
        result ^= scale(columns[j], vector & 3, low_mask)
        vector >>= 2
        j += 1
    return result


def rank(vectors, low_mask):
    basis = {}
    inverse = (0, 1, 3, 2)
    for vector in vectors:
        while vector:
            coordinate = (vector.bit_length()-1)//2
            coefficient = (vector >> (2*coordinate)) & 3
            if coordinate not in basis:
                basis[coordinate] = scale(vector, inverse[coefficient], low_mask)
                break
            vector ^= scale(basis[coordinate], coefficient, low_mask)
    return len(basis)


def zero_profile(columns, low_mask):
    dimension = len(columns)
    old_rank = dimension
    images = columns
    for power in range(1, dimension+1):
        current = rank(images, low_mask)
        if current == old_rank:
            return dimension-current, power-1
        if power == dimension:
            return dimension-current, power
        old_rank = current
        images = [image(columns, vector, low_mask) for vector in images]
    raise RuntimeError('unreachable rank stabilization')


def decode(code, dimension):
    mask = (1 << (2*dimension))-1
    return [(code >> (2*dimension*j)) & mask for j in range(dimension)]


def main():
    started = time.monotonic()
    cases, pairs = [], 0
    for r in range(1, 4):
        low_mask = sum(1 << (2*j) for j in range(r))
        profiles = []
        for code in range(1 << (2*r*r)):
            if code % 4096 == 0:
                require(time.monotonic()-started < 90, '90-second stopping cap')
            profiles.append(zero_profile(decode(code, r), low_mask))
        for k in range(r+1):
            endpoint = sum(1 << (2*(j*r+j)) for j in range(k))
            maxima, eligible, witnesses = [-1]*(r+1), [0]*(r+1), [None]*(r+1)
            for code, (za, ca) in enumerate(profiles):
                zb, cb = profiles[code ^ endpoint]
                pairs += 1
                for m in range(max(1, ca, cb), r+1):
                    eligible[m] += 1
                    if za+zb > maxima[m]:
                        maxima[m], witnesses[m] = za+zb, code
            for m in range(1, r+1):
                ell = m if m % 2 else m-1
                target = min(2*r-k % 2, r+(r-k)*ell)
                require(maxima[m] == target, 'F4 envelope mismatch '+str((r, k, m, maxima[m], target)))
                witness = witnesses[m]
                cases.append({'r': r, 'k': k, 'm': m, 'maximum': maxima[m], 'formula': target,
                              'eligible_matrices': eligible[m], 'A_columns': decode(witness, r),
                              'B_columns': decode(witness ^ endpoint, r)})
        print('PASS_F4_DIMENSION', r, len(profiles), flush=True)
    require(scale(2, 2, 1) == 3 and scale(3, 2, 1) == 1, 'irreducible field multiplication')
    require(zero_profile([0, 2, 8], 21) == (3, 3), 'nonbinary nilpotent chain')
    require(zero_profile([2, 8, 32], 21) == (0, 0), 'nonbinary invertible diagonal')
    require(zero_profile([0, 9], 5) == (1, 1), 'mixed zero and alpha primary')
    require(rank([1, 2], 1) == 1, 'F4 dependence differs from F2 additive rank')
    result = {'field': 'F2[alpha]/(alpha^2+alpha+1)', 'coverage': 'Every A over F4, every coordinate-idempotent rank, r=1..3, m=1..r',
              'method': 'Independent packed-column kernel growth and normalized Gaussian elimination over F4; no predecessor imports',
              'endpoint_matrices': pairs, 'cases': cases, 'controls': ['irreducible_field_multiplication', 'nonbinary_nilpotent_chain', 'nonbinary_invertible_diagonal',
                           'mixed_zero_and_alpha_primary', 'field_linear_dependence'],
              'stopping_rule': '90 seconds checked every 4096 matrix profiles; exhaustive declared domain completed',
              'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'limits': 'Finite F4 corroboration; not a proof for larger dimensions or arbitrary characteristic-two fields.'}
    result['marker'] = 'PASS_ALL_RANK_ALL_CAP_F4_CENSUS'
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
