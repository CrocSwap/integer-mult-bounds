"""Additional arithmetic, contract, decomposition and degree-loss controls."""
from fractions import Fraction as F
import bounded
from gaussian import G
from grouped import exact_mixed
from weighted import require
from precision import ceil_log2


def main():
    boundary_cases = 0
    for exponent in range(-300, 301):
        power = F(2)**exponent
        for value in [power, power*F(999, 1000), power*F(1001, 1000), power/3, power*F(7, 5)]:
            result = ceil_log2(value)
            require(F(2)**(result-1) < value <= F(2)**result, 'independent logarithm bracket')
            boundary_cases += 1
    rejected = []
    for value in [F(0), F(-1)]:
        try:
            ceil_log2(value)
        except ValueError:
            rejected.append('nonpositive logarithm '+str(value))
        else:
            raise ValueError('nonpositive logarithm accepted')

    bits, length = 64, 3
    u = F(1, 1 << bits)
    x0 = [G(F(i-3, 4)+u, F(i-1, 8)-u) for i in range(length)]
    y0 = [G(F(i+7, 8)-u, F(3-i, 4)+u) for i in range(length)]
    phases = [G(F(3, 5), F(4, 5)), G(F(-5, 13), F(12, 13)), G(0, 1)]
    inside = ([G(F(3, 8), F(1, 4))]*3, [F(1, 2)]*3)
    outside = ([G(F(-1, 2)), G(F(1, 4), F(1, 4))], [F(1, 2)]*2)
    for name in ['data alias', 'phase alias', 'root alias', 'nonunit phase',
                 'off grid', 'boolean precision', 'zero sign', 'wrong direction',
                 'unit radius', 'false small Wiener premise']:
        x, y, phi = x0.copy(), y0.copy(), phases.copy()
        a, b, width, sign, direction, common = inside, outside, bits, 1, 1, None
        if name == 'data alias':
            y = x
        elif name == 'phase alias':
            phi = x
        elif name == 'root alias':
            a = (x, [F(1, 2)]*length)
        elif name == 'nonunit phase':
            phi[0] = G(2)
        elif name == 'off grid':
            x[0] += G(u/2)
        elif name == 'boolean precision':
            width = True
        elif name == 'zero sign':
            sign = 0
        elif name == 'wrong direction':
            direction = 0
        elif name == 'unit radius':
            a = (inside[0], [F(1)]*3)
        else:
            common = F(1, 2)
        before_x, before_y = x.copy(), y.copy()
        try:
            bounded.compose(x, y, a, b, phi, direction, 7, width, sign, wiener_bound=common)
        except ValueError:
            require(x == before_x and y == before_y, 'rejected contract preserves data')
            rejected.append(name)
        else:
            raise ValueError('invalid contract accepted: '+name)

    want = exact_mixed(x0, inside[0], outside[0], phases, 1, 7)
    original_prepare = bounded.prepare
    for name in ['alter positive numerator', 'alter negative numerator', 'omit positive summand',
                 'omit negative summand', 'wrong positive orientation', 'wrong negative orientation']:
        def altered(*args, **kwargs):
            groups, error, details = original_prepare(*args, **kwargs)
            index = 0 if 'positive' in name else 1
            is_inside, q, numerator, K, S = groups[index]
            numerator = numerator.copy()
            if name.startswith('alter'):
                numerator[-1] += G(1)
            elif name.startswith('omit'):
                numerator = []
            else:
                is_inside = not is_inside
            groups[index] = (is_inside, q, numerator, K, S)
            return groups, error, details
        bounded.prepare = altered
        try:
            x, y = x0.copy(), y0.copy()
            error, _ = bounded.compose(x, y, inside, outside, phases, 1, 7, bits)
            require(x == x0, 'decomposition defects still restore source')
            require(any((v-v0-w).norm2() > error**2 for v, v0, w in zip(y, y0, want)),
                    'dense oracle detects decomposition defect: '+name)
            rejected.append(name)
        finally:
            bounded.prepare = original_prepare

    edges = []
    edge_fixtures = [
        ('leading degree loss', ([G(F(1, 2)), G()], [F(1, 2), F(0)]),
         ([G(F(1, 1 << 2000))], [F(1, 2)]), 64),
        ('all zero inside roots', ([G()]*3, [F(0)]*3), ([], []), 64),
        ('repeated close poles across groups', ([G(1-F(1, 1 << 40))]*2, [1-F(1, 1 << 40)]*2),
         ([G(1-F(1, 1 << 40))]*2, [1-F(1, 1 << 40)]*2), 512),
    ]
    for name, a, b, width in edge_fixtures:
        for size in [1, 2]:
            for direction in [-1, 1]:
                edge_u = F(1, 1 << width)
                x_initial = [G(F(i-3, 4)+edge_u, F(i-1, 8)-edge_u) for i in range(size)]
                y_initial = [G(F(i+7, 8)-edge_u, F(3-i, 4)+edge_u) for i in range(size)]
                phi = phases[:size]
                x, y = x_initial.copy(), y_initial.copy()
                error, details = bounded.compose(x, y, a, b, phi, direction, 3, width, audit=True)
                expected = exact_mixed(x_initial, a[0], b[0], phi, direction, 3)
                require(x == x_initial, 'edge source restoration')
                require(all((v-v0-w).norm2() <= error**2 for v, v0, w in zip(y, y_initial, expected)),
                        'edge dense inverse bound')
                if name == 'leading degree loss':
                    require(details['preparation']['delta_B'] > 0 and details['preparation']['delta_alpha'] > 0,
                            'degree-loss rounding is nonvacuous')
                    require(y == y_initial, 'tiny scalar rounded to zero within its charged error')
                if name == 'repeated close poles across groups':
                    require(error < F(1, 1 << 128), 'close-pole case has a meaningful absolute bound')
                bounded.compose(x, y, a, b, phi, direction, 3, width, -1)
                require(x == x_initial and y == y_initial, 'edge exact inverse cancellation')
                edges.append(dict(name=name, length=size, direction=direction, bits=width, error_bound=error,
                                  source_restored=True, inverse_cancels=True))
    result = dict(status='PASS_ADDITIVE_CONTROLS', logarithm_boundaries=boundary_cases,
                   rejected=rejected, edge_cases=edges)
    print('PASS', boundary_cases, 'precision boundaries;', len(rejected), 'rejections;', len(edges), 'edge cases')
    return result


if __name__ == '__main__':
    main()
