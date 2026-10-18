"""Replay the pinned PR628 kernels through the grouped dirty construction."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import importlib.util
import json

from budgets import plan
from gaussian import G
from grouped import compose, exact_mixed
from weighted import require

P = Path(__file__).resolve().parent


def main():
    pins = json.loads((P/'SOURCE-PINS.json').read_text())
    for row in pins['sources']:
        data = (P/row['path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'pinned source SHA256')
        require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == row['git_blob'],
                'pinned source Git blob')
    spec = importlib.util.spec_from_file_location('pinned628', P/'vendor/check.py')
    predecessor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(predecessor)
    data = json.loads((P/'vendor/FACTORS.json').read_text())
    rows, certificates = [], []
    for fixture in data:
        state = predecessor.certify(fixture)
        r = state['radix']
        phi = sum(__import__('math').gcd(r, j) == 1 for j in range(1, r))
        budget = plan(r, phi, 128, 0, 4, 2)
        beta = state['beta']
        inside, outside = ([], []), ([], [])
        for is_inside, value in state['factors']:
            pair = inside if is_inside else outside
            pair[0].append(G(*value))
            pair[1].append(1-beta)
        # Independently validate the common-bound premises for these finite
        # prepared polynomials. The all-size existence proof is separate.
        mass = sum(abs(z[0])+abs(z[1]) for z in state['q'])
        H = F(state['certificate']['inverse_norm_bound'])
        common_K = F(1 << budget['k0'])
        require(mass <= 1 << r, 'prepared polynomial coefficient mass')
        require(r*(1 << (r-1))*mass*mass*H <= common_K, 'common stable-group Wiener bound')
        modes = ['product'] + (['common'] if r in (3, 4) else [])
        for mode in modes:
            for length in (1, 2):
                phases = [G(F(3, 5), F(4, 5)) if i % 2 == 0 else G(F(-5, 13), F(12, 13))
                          for i in range(length)]
                for direction in (-1, 1):
                    bits = 768
                    u = F(1, 1 << bits)
                    x0 = [G(F(i-3, 4)+u, F(i-1, 8)-u) for i in range(length)]
                    y0 = [G(F(i+7, 8)-u, F(3-i, 4)+u) for i in range(length)]
                    z0 = [G(F(-13+i, 4)+u, F(7-i, 8)-u) for i in range(length)]
                    x, y, z = x0.copy(), y0.copy(), z0.copy()
                    supplied = common_K if mode == 'common' else None
                    stats, bound = compose(x, y, z, inside, outside, phases, direction, r, bits,
                                           audit=r <= 5, wiener_bound=supplied)
                    require(x == x0 and z == z0, 'kernel dirty restoration')
                    want = exact_mixed(x0, inside[0], outside[0], phases, direction, r)
                    errors = [a-b-c for a, b, c in zip(y, y0, want)]
                    require(all(v.norm2() <= bound**2 for v in errors), 'original root-factor dense oracle')
                    perturb = F(state['certificate']['factorization_inverse_error_bound'])*max(v.upper() for v in x0)
                    require(bound+perturb <= F(1, 1 << 128), 'original prime-power target error')
                    compose(x, y, z, inside, outside, phases, direction, r, bits, -1, wiener_bound=supplied)
                    require(x == x0 and y == y0 and z == z0, 'kernel inverse word cancellation')
                    for stat in stats:
                        if 'solver' in stat:
                            solver = stat['solver']
                            n = solver['dimension']
                            require(solver['maximum_minor_bits'] <= n*(solver['input_bits']+(n-1).bit_length())+1,
                                    'fraction-free intermediate minor bit bound')
                    rows.append(dict(radix=r, embedding=fixture['embedding'], length=length, direction=direction,
                                     bits=bits, mode=mode, common_K=common_K if supplied else None,
                                     bound=bound, coefficient_perturbation=perturb, total_error_bound=bound+perturb,
                                     max_error_squared=max(v.norm2() for v in errors),
                                     source_restored=True, connector_restored=True, inverse_cancels=True, stats=stats))
        certificates.append(state['certificate'])
        print('PASS kernel', r, fixture['embedding'], 'cumulative cases', len(rows), flush=True)
    result = dict(status='PASS', sources_checked=len(pins['sources']),
        certificates=certificates, cases=rows,
        scope='Finite original-kernel replay with exact rational coefficient enclosure and dirty restoration. '
              'The supplied common Wiener bound is separately checked on every prepared polynomial. '
              'No common-label, Clifford, full transform, or kappa claim.')
    print('PASS', len(rows), 'original-kernel grouped cases')
    return result


if __name__ == '__main__':
    main()
