"""Exact native-coefficient caller oracle; @CubeJerry/AI, Apache-2.0."""
import json
import random

from construction import build_tables, need, KEYS, source_representative, target_representative
from kernel import block, rotate
from caller import load_ports, checked_block, fibers, make_backend, request_bits, signed_width

tables = build_tables()
ports, retained = load_ports()
candidate = make_backend(tables)


def ideal(v, f, axis, width, adjoint=False, trace=None):
    # Independent coefficient formula for C_axis tensor 4; no Walsh factorization.
    for indices in fibers(axis):
        old = [v[i] for i in indices]
        for r, index in enumerate(indices):
            terms = [rotate(old[s], (-1 if adjoint else 1)*(4-(r ^ s).bit_count()))
                     for s in range(16)]
            numerator = [-sum(z[k] for z in terms) for k in range(2)]
            need(all(a % 4 == 0 for a in numerator), 'Oracle scale exhausted')
            v[index] = tuple(a//4 for a in numerator)
    return v


def run():
    # Independently bind the fast checked arithmetic to the certified dense map.
    for inverse, section in ((False, source_representative), (True, target_representative)):
        for key in KEYS:
            v = section(key)
            z = tuple((a, v[(5*j+3) % 16]) for j, a in enumerate(v))
            need(tuple(checked_block(z, tables, 64, inverse)) == block(z, tables, inverse),
                 'Fast/dense block equality')
    rng = random.Random(2026110627)
    fixtures = [([(0, 0)]*4096, [(0, 0)]*4096),
                ([(rng.randrange(-8, 9), rng.randrange(-8, 9)) for _ in range(4096)],
                 [(rng.randrange(-8, 9), rng.randrange(-8, 9)) for _ in range(4096)]),
                ([((j % 7)-3, ((j*5) % 11)-5) for j in range(4096)],
                 [((j % 13)-6, ((j*3) % 17)-8) for j in range(4096)]),
                ([((1 << 30)+(j % 7), -(1 << 29)-(j % 5)) for j in range(4096)],
                 [(-(1 << 31)+(j % 11), (1 << 28)+(j % 3)) for j in range(4096)])]
    cases = cuts_checked = 0
    maxima = {}
    for number, (x, y) in enumerate(fixtures):
        for kind in (2, 3):
            for reverse in (False, True):
                gotx, goty, trace, cuts = ports.port(x, y, 4, kind, reverse, 64,
                                                    candidate, retained, True)
                backx, backy, _, _ = ports.port(gotx, goty, 4, kind, not reverse, 64,
                                                candidate, retained, True)
                need((backx, backy) == (x, y), 'Exact two-bank return')
                phasex, phasey, _, _ = ports.port([rotate(z, 1) for z in x],
                    [rotate(z, 1) for z in y], 4, kind, reverse, 64, candidate, retained, True)
                need(phasex == [rotate(z, 1) for z in gotx]
                     and phasey == [rotate(z, 1) for z in goty], 'Port phase covariance')
                exactx, exacty, _, _ = ports.port([tuple(64*a for a in z) for z in x],
                    [tuple(64*a for a in z) for z in y], 4, kind, reverse, 80, ideal, retained, True)
                error = max(sum((64*a-b)**2 for a, b in zip(v, w))
                            for v, w in zip(gotx+goty, exactx+exacty))
                multiplier = (1 if kind == 2 else 5) if reverse else (13 if kind == 2 else 53)
                radius = 50 if reverse else 18
                need(error <= 256*multiplier**2*radius, 'Complete port error')
                maxima[f'{kind}-{reverse}'] = max(maxima.get(f'{kind}-{reverse}', 0), error)
                need(trace['blocks'] == kind*256 and trace['data_additions'] == kind*40960
                     and trace['quarter_shifts'] == kind*8192, 'Complete block arithmetic count')
                for axis, adjoint, before, after in cuts:
                    exact = [tuple(4*a for a in z) for z in before]
                    ideal(exact, 4, axis, 80, adjoint)
                    need(max(sum((4*a-b)**2 for a, b in zip(v, w))
                             for v, w in zip(after, exact)) <= (50 if adjoint else 18),
                         'Actual-input call coordinate error')
                    for ids in fibers(axis):
                        need(tuple(sum(before[i][k] for i in ids) for k in (0, 1)) ==
                             tuple(sum(after[i][k] for i in ids) for k in (0, 1)), 'Fiber sum')
                    cuts_checked += 1
                cases += 1
    rejected = []
    bad_cases = [('alias', lambda: ports.port(fixtures[1][0], fixtures[1][0], 4, 2, False,
                                             64, candidate, retained)),
                 ('wrong-size', lambda: candidate([(0, 0)]*4096, 3, 0, 64)),
                 ('word-overflow', lambda: candidate([(127, 127)]*4096, 4, 0, 8))]
    for name, action in bad_cases:
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('Negative control survived: '+name)
    def wrong_inverse(v, f, axis, width, adjoint=False, trace=None):
        return candidate(v, f, axis, width, False, trace)
    x, y = fixtures[1]
    fx, fy, _, _ = ports.port(x, y, 4, 3, False, 64, candidate, retained, True)
    bx, by, _, _ = ports.port(fx, fy, 4, 3, True, 64, wrong_inverse, retained, True)
    need((bx, by) != (x, y), 'Wrong inverse must fail return')
    rejected.append('forward-as-inverse')
    def wrong_axis(v, f, axis, width, adjoint=False, trace=None):
        return candidate(v, f, 0, width, adjoint, trace)
    x = [tuple(1024*a for a in z) for z in x]
    y = [tuple(1024*a for a in z) for z in y]
    fx, fy, _, _ = ports.port(x, y, 4, 3, False, 64, wrong_axis, retained, True)
    ex, ey, _, _ = ports.port([tuple(64*a for a in z) for z in x],
        [tuple(64*a for a in z) for z in y], 4, 3, False, 80, ideal, retained, True)
    wrong_error = max(sum((64*a-b)**2 for a, b in zip(v, w))
                      for v, w in zip(fx+fy, ex+ey))
    need(wrong_error > 256*53**2*18, 'Wrong axis must fail native accuracy')
    rejected.append('wrong-native-axis')
    grid_cases = []
    for kind in (2, 3):
        for reverse in (False, True):
            P, H = 4, 3
            old_g = retained.request_bits(P, 4, kind, reverse)
            g = request_bits(P, kind, reverse)
            width = signed_width(H, P, kind, reverse)
            need(g == old_g-2 and width == retained.signed_width(H, P, 4, kind, reverse)-2, 'Two-bit retained reduction')
            magnitude = 1 << (H+g)
            x = [(magnitude if j % 3 else -magnitude, 0) for j in range(4096)]
            y = [(0, magnitude if j % 5 else -magnitude) for j in range(4096)]
            # Break alignment without violating the initial magnitude bound.
            x[7] = (magnitude-1, 0)
            y[11] = (0, -magnitude+3)
            fx, fy, _, _ = ports.port(x, y, 4, kind, reverse, width, candidate, retained, True)
            ex, ey, _, _ = ports.port([tuple(64*a for a in z) for z in x],
                [tuple(64*a for a in z) for z in y], 4, kind, reverse, width+8, ideal, retained, True)
            error = max(sum((64*a-b)**2 for a, b in zip(v, w))
                        for v, w in zip(fx+fy, ex+ey))
            need(error <= (64 << (g-P))**2, 'Retained complete physical accuracy')
            bx, by, _, _ = ports.port(fx, fy, 4, kind, not reverse, width, candidate, retained, True)
            need((bx, by) == (x, y), 'Finite-word exact return')
            grid_cases.append({'kind': kind, 'reverse': reverse, 'P': P, 'H': H,
                               'g': g, 'width': width, 'old_g': old_g})
    print(json.dumps({'status': 'PASS_FOUR_AXIS_RETAINED_PORTS', 'fixtures': len(fixtures),
        'port_directions': cases, 'actual_input_cuts': cuts_checked,
        'max_squared_errors_scaled_by_4096': maxima, 'negative_controls': rejected,
        'native_grid': 'g=q+1', 'retained_grid': 'g=q+3', 'fractional_bits_saved': 2,
        'grid_cases': grid_cases}, sort_keys=True))


if __name__ == '__main__':
    run()
