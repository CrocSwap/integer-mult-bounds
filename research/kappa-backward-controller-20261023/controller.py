"""Exact all-backward controller and physical signed-swap wrapper.

The Laurent replay is adapted from Ali Romman PR5383. Cinna Davis supplied
its controller; zxv supplied the retained phase convention. Apache-2.0.
New construction by Ali Romman with substantial OpenAI Codex assistance.
"""
from copy import deepcopy
from fractions import Fraction as Q
from native import ROOT, read, load, need

def replay(word):
    """Check the literal p16 word and both rational boundary programs."""
    need((word['kind'], word['pairs'], word['prefix_pairs'], word['ambient_rank']) == ('complex', 16, 7, 145), 'Source p16/a7 controller')
    zero = (0,) * 34
    def plus(dst, src, q):
        for k, v in src.items():
            value = dst.get(k, Q(0)) + q * v
            if value: dst[k] = value
            else: dst.pop(k, None)
    def shifted(row, term, sign=1):
        return [{tuple(a + b for a, b in zip(k, term)): sign * v for k, v in cell.items()} for cell in row]
    for side in ('left', 'right'):
        matrix = [[Q(i == j) for j in range(32)] for i in range(32)]
        for e in word['boundaries'][side + '_program']:
            if e[0] == 'SWAP': matrix[e[1]], matrix[e[2]] = matrix[e[2]], matrix[e[1]]
            elif e[0] == 'SCALE': matrix[e[1]] = [Q(e[2]) * x for x in matrix[e[1]]]
            else:
                need(e[0] == 'ADD', 'Boundary scalar opcode')
                matrix[e[1]] = [x + Q(e[3]) * y for x, y in zip(matrix[e[1]], matrix[e[2]])]
        need(matrix == [[Q(x) for x in row] for row in word['boundaries'][side]], 'Exact scalar boundary program')
    rows = [[{zero: Q(x)} if Q(x) else {} for x in row] for row in word['boundaries']['right']]
    for e in word['physical_events']:
        if e[0] in ('LOCAL', 'QUERY_SHEAR'):
            _, stage, pair, back = e
            x, y = 2 * pair, 2 * pair + 1
            if back: x, y = y, x
            term = (1 if back else -1,) + (0,) * 33
            for dst, src in zip(rows[y], shifted(rows[x], term)):
                plus(dst, src, Q(-1 if back else 1))
            if e[0] == 'LOCAL':
                term = (0,) + tuple(int(s == stage) for s in range(33))
                for r in (x, y): rows[r] = shifted(rows[r], term)
        elif e[0] == 'Q_POWER':
            need(e[2] in (-2, 2), 'Only even central powers are free')
            rows[e[1]] = shifted(rows[e[1]], (e[2],) + (0,) * 33)
        elif e[0] == 'IDLE':
            term = (0,) + tuple(int(s in e[2]) for s in range(33))
            for r in (2 * e[1], 2 * e[1] + 1): rows[r] = shifted(rows[r], term)
        elif e[0] == 'ADD':
            for dst, src in zip(rows[e[1]], rows[e[2]]): plus(dst, src, Q(e[3]))
        else:
            need(e[0] in ('SWAP', 'SIGNED_SWAP'), 'Controller physical opcode')
            rows[e[1]], rows[e[2]] = rows[e[2]], shifted(rows[e[1]], zero, -1 if e[0] == 'SIGNED_SWAP' else 1)
    out = [[{} for _ in range(32)] for _ in range(32)]
    for i, row in enumerate(word['boundaries']['left']):
        for k, q in enumerate(row):
            if Q(q):
                for j in range(32): plus(out[i][j], rows[k][j], Q(q))
    expected = [[{tuple(word['diagonal'][i]): Q(1)} if i == j else {} for j in range(32)] for i in range(32)]
    need(out == expected, 'All p16 Laurent coefficients, central signs and boundary factors')
    return word



def construct():
    source = read(ROOT / 'research/joint-helper-lattice/CONTROLLER.json')
    replay(source)
    word = deepcopy(source)
    events = []
    sites = []
    for index, event in enumerate(source['physical_events']):
        if event[0] == 'LOCAL' and not event[3]:
            _, stage, pair, _ = event
            x, y = 2 * pair, 2 * pair + 1
            sites.append({'source_index': index, 'stage': stage, 'pair': pair})
            events += [['SIGNED_SWAP', y, x], ['Q_POWER', x, 2],
                       ['LOCAL', stage, pair, True],
                       ['SIGNED_SWAP', x, y], ['Q_POWER', y, -2]]
        else:
            events.append(deepcopy(event))
    need(len(sites) == 2, 'Exactly the two forward sites change')
    word['physical_events'] = events
    word['wrapper_sites'] = sites
    # This field described the old local provider. The new full bill is separate.
    word.pop('invoice')
    replay(word)
    return word


def physical(word):
    n = load('research/pr4359-p7-padding/native_inventory.py', 'backward_wrapper_native_phase')
    path = 'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json'
    recipes = read(ROOT / path)['recipes']
    need(len(recipes) == 112, 'All actual central ports')
    sites = word['wrapper_sites']
    need([site['stage'] for site in sites] == [0, 32], 'Both actual boundary stages')
    dimension = 9 + 8 * 32
    axes = tuple(1 << i for i in range(dimension))
    def completed(stage):
        return n.norm((axis, 1) for axis in axes[:9 + 8 * stage])
    checks, records = 0, []
    for site in sites:
        stage = site['stage']
        spectator = n.norm((axis, 1) for axis in axes[9:9 + 8 * stage])
        for port, recipe in enumerate(recipes):
            q = recipe['q']
            need(0 < q < 512, 'Actual nine-axis central operator')
            basis = recipe['idle_children'][0]['orthogonal_axes'][:8]
            need(all((b & q).bit_count() % 2 == 0 for b in basis), 'Actual route is perpendicular to Q')
            need(all((a & b).bit_count() % 2 == int(i == j) for i, a in enumerate(basis) for j, b in enumerate(basis)), 'Actual eight-vector basis is orthonormal')
            swaps = [] if stage == 0 else [b ^ axes[9 + 8 * (stage - 1) + i] for i, b in enumerate(basis)]
            route = tuple(e ^ n.act(swaps, sum(((e & v).bit_count() % 2) << i for i, v in enumerate(swaps))) for e in axes)
            need(all(n.act(route, route[i]) == axes[i] for i in range(dimension)), 'Involutive actual route')
            need(all((a & b).bit_count() % 2 == int(i == j) for i, a in enumerate(route) for j, b in enumerate(route)), 'Orthogonal actual route')
            need(n.act(route, q) == q, 'Physical routing preserves the central operator')
            raw_x = n.norm([(q, 1)]) if stage == 0 else completed(stage - 1)
            raw_y = () if stage == 0 else n.norm(list(raw_x) + [(q, -1)])
            raw = (raw_x, raw_y)
            entry = (n.norm(list(spectator) + [(q, -1)]), spectator)
            local0 = n.norm(list(spectator) + [(a, -1) for a in axes[:9]])
            local_out = (local0, n.norm(list(local0) + [(q, 1)]))
            out = (completed(stage), n.norm(list(completed(stage)) + [(q, -1)]))
            contacts = [n.contact(a, b, route, dimension) for a, b in list(zip(raw, entry)) + list(zip(local_out, out))]
            delta = n.norm([(a, 1) for a in axes[:9]] + [(q, -1)]) if stage == 0 else n.norm((a, 1) for a in axes[9 + 8 * (stage - 1):9 + 8 * stage])
            for incoming, outgoing in zip(raw, out):
                need(n.polynomial(n.norm(list(outgoing) + [(a, -v) for a, v in incoming]), dimension) == n.polynomial(delta, dimension), 'Actual backward diagonal is D_s')
            cross = n.norm(list(out[0]) + [(a, -v) for a, v in raw[1]])
            need(n.polynomial(cross, dimension) == n.polynomial(n.norm(list(delta) + [(q, 1)]), dimension), 'Actual backward cross term is D_s Q')
            positive = n.polynomial(n.norm([(q, 2)]), dimension)
            negative = n.polynomial(n.norm([(q, -2)]), dimension)
            need(positive == negative and not any(positive[1]) and all(v in (0, 2) for v in positive[0]), 'Both wrapper powers are the same exact translation')
            need(positive != n.polynomial((), dimension), 'The central translation cannot be omitted')
            # Q = a I + b X_q. Check its square on each nine-axis column.
            a, b = (Q(1, 2), Q(1, 2)), (Q(1, 2), Q(-1, 2))
            def mul(z, w):
                return (z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0])
            def add(z, w):
                return (z[0] + w[0], z[1] + w[1])
            zero, one = (Q(0), Q(0)), (Q(1), Q(0))
            square = (add(mul(a, a), mul(b, b)), add(mul(a, b), mul(b, a)))
            need(square == (zero, one), 'Absolute phase of the Gaussian square')
            for address in range(512):
                column = {address: square[0], address ^ q: square[1]}
                column = {x: v for x, v in column.items() if v != zero}
                need(column == {address ^ q: one}, 'Every literal central-square column')
                checks += 1
            records.append({'stage': stage, 'pair': site['pair'], 'port': port, 'q': q, 'contacts': contacts, 'central_translation': q})
    return {'ports': 112, 'stages': [0, 32], 'dimension': dimension,
            'literal_square_columns': checks, 'local_boundary_contacts': 4 * len(records),
            'records': records, 'new_positive_rank_jobs': 0,
            'tensor_lift': 'Factorwise tensor products: (Q tensor f)^2 = (X_q tensor f). Scalar minus signs remain outside the tensor substitution.'}


def controls(word):
    failures = {}
    variants = {}
    bad = deepcopy(word)
    bad['physical_events'].remove(next(e for e in bad['physical_events'] if e[0] == 'Q_POWER'))
    variants['omitted_central_translation'] = bad
    bad = deepcopy(word)
    e = next(e for e in bad['physical_events'] if e[0] == 'Q_POWER')
    e[2] = 1
    variants['unpaid_rank_one_wrapper'] = bad
    bad = deepcopy(word)
    e = next(e for e in bad['physical_events'] if e[0] == 'LOCAL')
    e[3] = False
    variants['wrong_primitive_orientation'] = bad
    bad = deepcopy(word)
    e = next(e for e in bad['physical_events'] if e[0] == 'SIGNED_SWAP')
    e[0] = 'SWAP'
    variants['missing_wrapper_sign'] = bad
    for name, candidate in variants.items():
        try:
            replay(candidate)
        except ValueError as exc:
            failures[name] = str(exc)
        else:
            raise ValueError('Accepted corrupted controller: ' + name)
    return failures
