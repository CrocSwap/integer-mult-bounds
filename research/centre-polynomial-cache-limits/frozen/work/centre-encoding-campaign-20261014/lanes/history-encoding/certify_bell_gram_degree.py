"""Certify a characteristic-zero Gram degree lower bound by one minor."""

from hashlib import sha256, shake_256
from pathlib import Path
import argparse
import json
import numpy as np


PIN = '5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3'
PRIME = 65537
CONSTANT = 11
DEGREE = 409


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def vector(seed):
    data = shake_256(seed.encode()).digest(8192)
    return np.frombuffer(data, dtype='<u2').astype(np.int64).reshape(8, 512)


def determinant(matrix):
    values = matrix.copy()
    n = len(values)
    answer = 1
    swaps = 0
    for column in range(n):
        candidates = np.flatnonzero(values[column:, column])
        require(len(candidates) > 0, 'Hankel minor has a nonzero pivot')
        row = column+int(candidates[0])
        if row != column:
            values[[row, column]] = values[[column, row]]
            swaps += 1
        pivot = int(values[column, column])
        answer = answer*pivot % PRIME
        normalized = values[column, column+1:]*pow(pivot, -1, PRIME) % PRIME
        values[column+1:, column+1:] = (
            values[column+1:, column+1:]
            - values[column+1:, column, None]*normalized[None, :]) % PRIME
        values[column+1:, column] = 0
    return answer*(-1)**swaps % PRIME, swaps


def main(args):
    raw = args.interface.read_bytes()
    require(sha256(raw).hexdigest() == PIN, 'Actual supplier interface pin')
    source = json.loads(raw)
    R = np.zeros((8, 112), dtype=np.int64)
    for k, row in enumerate(source['R']):
        for port, value in row.items():
            R[k, int(port)] = int(value)
    require(np.array_equal(R@R.T, 56*np.eye(8, dtype=np.int64)), 'Actual Gram normalization')
    require(all(PRIME % d for d in range(2, 257)), 'Prime modulus')
    inverse4 = pow(4, -1, PRIME)
    addresses = np.arange(512, dtype=np.int64)
    targets, signs = [], []
    for q in source['ports']:
        translation = (q & CONSTANT).bit_count() % 2
        targets.append(addresses ^ (q if translation else 0))
        signs.append([1 if translation else 1-2*((q & a).bit_count() % 2)
                      for a in range(512)])
    targets = np.asarray(targets, dtype=np.int64)
    signs = np.asarray(signs, dtype=np.int64)

    def apply(value):
        lifted = (R.T@value) % PRIME
        acted = np.take_along_axis(lifted, targets, axis=1)*signs
        return ((R@acted) % PRIME)*inverse4 % PRIME

    seed = 'actual-bell-gram-c11-trial0'
    initial = vector(seed)
    observer = vector(seed+'-observer')
    value = initial.copy()
    moments = []
    for _ in range(2*DEGREE-1):
        moments.append(int(np.sum(observer*value) % PRIME))
        value = apply(value)
    hankel = np.asarray([[moments[i+j] for j in range(DEGREE)]
                         for i in range(DEGREE)], dtype=np.int64)
    det, swaps = determinant(hankel)
    require(det != 0, 'Nonzero exact Hankel determinant')
    # A duplicate last row makes the same elimination detect dependence.
    control = hankel.copy()
    control[-1] = control[0]
    try:
        determinant(control)
    except ValueError:
        control_rejected = True
    else:
        control_rejected = False
    require(control_rejected, 'Dependent-row control')
    report = {
        'status': 'PASS_EXACT_CHARACTERISTIC_ZERO_GRAM_DEGREE_LOWER_BOUND',
        'source_sha256': PIN, 'field_prime': PRIME, 'bell_constant': CONSTANT,
        'operator': 'A_c=(1/4) sum actual112 r_q r_q^T P_q(c)',
        'bell_action': 'P_q(c)=X_q if parity(q&c)=1, else Z_q',
        'operator_dimension': 4096, 'tensor_size': 1,
        'initial_seed': seed, 'observer_seed': seed+'-observer',
        'seed_expansion': 'SHAKE2568192bytes, little-endian unsigned16, reshape8by512',
        'hankel_definition': 'H[i,j]=observer^T A_c^(i+j) initial, 0<=i,j<409',
        'hankel_size': DEGREE, 'hankel_determinant_mod_prime': det,
        'elimination_row_swaps': swaps, 'moments_count': len(moments),
        'moments': moments,
        'moments_sha256': sha256(json.dumps(moments).encode()).hexdigest(),
        'dependent_row_control_rejected': control_rejected,
        'proved_minimal_polynomial_degree_lower_bound_over_Q': DEGREE,
        'arithmetic_bound': 'Every int64 product is below2^33 and every moment sum is below2^45; all reductions are exact.',
        'scope': 'One actual doubled-Walsh Bell block forces degree at least409 for any annihilating scalar polynomial in characteristic zero. This does not bound general weighted ADD circuits, matrix-valued encodings, or native decoder cost.'}
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(report['status'])
    print(json.dumps({key: report[key] for key in ('hankel_size', 'hankel_determinant_mod_prime',
                                                  'moments_sha256')}, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args())
