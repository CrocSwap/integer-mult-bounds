"""Finite dense-oracle and corruption tests; not an all-size proof."""
from pathlib import Path
import json
import sys

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P))
sys.dont_write_bytecode = True
sys.set_int_max_str_digits(100000)
from bounded import G, F, compose, require, reference


def main():
    fixtures = [
        (([G(F(1, 4))], [F(1, 4)]), ([G(F(1, 2))], [F(1, 2)])),
        (([G(F(3, 8), F(1, 4))]*3, [F(1, 2)]*3),
         ([G(F(-1, 2)), G(F(1, 4), F(1, 4))], [F(1, 2)]*2)),
        (([G(), G(F(1, 4), F(1, 2))], [F(0), F(3, 4)]), ([], [])),
        (([], []), ([G(F(4095, 8192))]*3, [F(1, 2)]*3)),
        (([G(F(15, 16))]*2, [F(15, 16)]*2),
         ([G(F(15, 16))]*2, [F(15, 16)]*2)),
        (([], []), ([], [])),
        (([G(F((1 << 90)-1, 1 << 91))]*3, [F(1, 2)]*3),
         ([G(F((1 << 83)-1, 1 << 85), F((1 << 77)-3, 1 << 80)),
           G(F((1 << 100)-1, 1 << 101))], [F(1, 2)]*2)),
    ]
    units = [G(1), G(0, 1), G(F(3, 5), F(4, 5)), G(F(-5, 13), F(12, 13))]
    rows = []
    controls = {name:[] for name in ['omit_negative_history', 'coarse_fir', 'coarse_gauge']}
    nonzero = {name:0 for name in ['delta_A', 'delta_B', 'delta_alpha', 'delta_plus', 'delta_minus',
                                  'max_fir_error', 'max_window_error']}
    for fixture_id, (inside, outside) in enumerate(fixtures):
        for length in [1, 2, 3, 8, 17]:
            phases = [units[(3*i+2) % len(units)] for i in range(length)]
            for direction in [-1, 1]:
                for bits in [32, 64]:
                    u = F(1, 1 << bits)
                    x0 = [G(F(i-3, 4)+u, F(2*i-3, 8)-u) for i in range(length)]
                    y0 = [G(F(i+19, 8)-u, F(3-i, 4)+u) for i in range(length)]
                    require(all((v/u).denominator == 1 and (v/u).numerator % 2
                                for array in (x0, y0) for value in array for v in (value.re, value.im)),
                            'every incoming component has odd lowest bit')
                    x, y = x0.copy(), y0.copy()
                    error, audit = compose(x, y, inside, outside, phases, direction, 7, bits, audit=True)
                    require(x == x0, 'bounded source restoration')
                    want = reference.exact_mixed(x0, inside[0], outside[0], phases, direction, 7)
                    actual = max((v-v0-w).norm2() for v, v0, w in zip(y, y0, want))
                    require(actual <= error**2, 'original factor-matrix error bound')
                    plain_x, plain_y = x0.copy(), y0.copy()
                    plain_error, _ = compose(plain_x, plain_y, inside, outside, phases, direction, 7, bits)
                    require(plain_x == x and plain_y == y and plain_error == error,
                            'no-audit execution is identical')
                    compose(x, y, inside, outside, phases, direction, 7, bits, -1)
                    require(x == x0 and y == y0, 'literal inverse restores both arrays')
                    for name in controls:
                        mx, my = x0.copy(), y0.copy()
                        compose(mx, my, inside, outside, phases, direction, 7, bits, mutation=name)
                        if any((v-v0-w).norm2() > error**2 for v, v0, w in zip(my, y0, want)):
                            controls[name].append(len(rows))
                    for name in nonzero:
                        if name.startswith('delta_'):
                            nonzero[name] += bool(audit['preparation'][name])
                        else:
                            nonzero[name] += any(call.get(name, 0) > 0 for call in audit['calls'])
                    rows.append(dict(fixture=fixture_id, length=length, direction=direction, bits=bits,
                                     error_bound=error, actual_error_squared=actual, audit=audit,
                                     source_restored=True, inverse_cancels=True, plain_equals_audit=True))
        print('PASS bounded fixture', fixture_id, 'cumulative cases', len(rows), flush=True)
    require(all(controls.values()), 'all mathematical controls nonvacuous')
    require(all(nonzero.values()), 'all newly bounded preparation components round nontrivially')
    require(any(row['actual_error_squared'] > 0 for row in rows), 'actual nonzero output errors')
    result = dict(status='PASS_BOUNDED_ADDITIVE_FINITE', rows=rows, rejected=controls,
                   nonzero_rounding=nonzero, borrowed_length_arrays=0,
                   scope='Finite rounded original-factor inverse checks with no dirty connector. '
                         'The universal proof and original prime-power kernel bridge are separate package components.')
    print('PASS', len(rows), 'bounded additive cases', {k:len(v) for k, v in controls.items()}, nonzero)
    return result


if __name__ == '__main__':
    main()
