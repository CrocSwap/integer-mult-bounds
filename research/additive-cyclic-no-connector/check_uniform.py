"""Execute at the stated uniform budget, with certified common Wiener input."""
from pathlib import Path
import sys
import json
import importlib.util
from math import gcd

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P))
sys.dont_write_bytecode = True
sys.set_int_max_str_digits(100000)
from bounded import G, F, compose, require, reference
from additive_budget import plan



def main():
    source = P/'vendor'
    spec = importlib.util.spec_from_file_location('pinned628uniform', source/'check.py')
    predecessor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(predecessor)
    rows = []
    for fixture in json.loads((source/'FACTORS.json').read_text()):
        if fixture['radix'] not in [3, 4, 5, 7]:
            continue
        state = predecessor.certify(fixture)
        r, beta = state['radix'], state['beta']
        phi = sum(gcd(r, j) == 1 for j in range(1, r))
        inside, outside = ([], []), ([], [])
        for is_inside, value in state['factors']:
            pair = inside if is_inside else outside
            pair[0].append(G(*value))
            pair[1].append(1-beta)
        for length in [1, 2]:
            provisional = plan(r, phi, 128, 0, 4, length)
            bits = provisional['working']
            # Declare the actual arbitrary incoming grid, including its low bit.
            budget = plan(r, phi, 128, bits, 4, length)
            require(budget['working'] == bits, 'working-grid fixed point')
            common = F(1 << budget['k0'])
            mass = sum(abs(z[0])+abs(z[1]) for z in state['q'])
            H = F(state['certificate']['inverse_norm_bound'])
            require(mass <= 1 << r and r*(1 << (r-1))*mass*mass*H <= common,
                    'actual prepared polynomial certifies common Wiener bound')
            for direction in [-1, 1]:
                u = F(1, 1 << bits)
                x0 = [G(F(i-3, 4)+u, F(i-1, 8)-u) for i in range(length)]
                y0 = [G(F(i+7, 8)-u, F(3-i, 4)+u) for i in range(length)]
                phases = [G(F(3, 5), F(4, 5)) if i % 2 == 0 else G(F(-5, 13), F(12, 13))
                          for i in range(length)]
                x, y = x0.copy(), y0.copy()
                error, audit = compose(x, y, inside, outside, phases, direction, r, bits,
                                        audit=True, wiener_bound=common)
                require(x == x0, 'uniform exact source restoration')
                require(error <= F(1, 1 << 130), 'uniform quarter-target execution error')
                want = reference.exact_mixed(x0, inside[0], outside[0], phases, direction, r)
                require(all((v-v0-w).norm2() <= error**2 for v, v0, w in zip(y, y0, want)),
                        'uniform dense original-factor inverse')
                perturbation = F(state['certificate']['factorization_inverse_error_bound'])*max(v.upper() for v in x0)
                require(error+perturbation <= F(1, 1 << 128), 'original target with uniform budget')
                prep = audit['preparation']
                for key, limit in [('width_A','polynomial'), ('width_B','polynomial'), ('alpha_bits','alpha'),
                                   ('width_plus','numerator'), ('width_minus','numerator')]:
                    require(prep[key] <= budget[limit], 'actual preparation width within uniform cap')
                for call in audit['calls']:
                    require(call['K'] <= 1 << (budget['k0']+1) and call['S'] <= 1 << budget['s0'],
                            'actual Wiener and companion bounds')
                    require(call.get('numerator_mass', 0) <= 1 << budget['j0'], 'actual numerator mass')
                    for key, limit in [('scalar_bits','scalar'), ('window_bits','window'),
                                       ('gauge_bits','gauge'), ('fir_bits','fir')]:
                        if key in call:
                            require(call[key] <= budget[limit], 'actual data width within uniform cap')
                compose(x, y, inside, outside, phases, direction, r, bits, -1, wiener_bound=common)
                require(x == x0 and y == y0, 'uniform exact inverse')
                rows.append(dict(radix=r, length=length, direction=direction, bits=bits,
                                 budget=budget, execution_error=error, kernel_error=perturbation,
                                 source_restored=True, inverse_cancels=True, audit=audit))
        print('PASS uniform additive radix', r, 'cumulative cases', len(rows), flush=True)
    print('PASS', len(rows), 'uniform-budget original kernel cases')
    return dict(status='PASS_UNIFORM_ADDITIVE', cases=rows)


if __name__ == '__main__':
    main()
