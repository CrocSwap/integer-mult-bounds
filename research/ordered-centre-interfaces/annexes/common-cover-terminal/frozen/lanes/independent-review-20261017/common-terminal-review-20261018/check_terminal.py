#!/usr/bin/env python3
"""Check common-cover terminal maps, complete phase coefficients, and cost scope."""
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SOURCE = LANES/'encoded-controller/common-monomial-terminal-20261018'
N = 73
UNIT = [1 << i for i in range(N)]
PINS = {
    'encoded-controller/common-monomial-terminal-20261018/FREEZE.json':
        'e342c8d646a5c7cb5ee8cfd53d231c91a572b24894b9217a3a9533c00cce09f0',
    'encoded-controller/common-monomial-terminal-20261018/COMMON-TERMINAL.md':
        'd57d298a6b5394270fa2360d15d867b406f7fbc5e69d62829b978edda29b05ad',
    'encoded-controller/common-monomial-terminal-20261018/check_common_terminal.py':
        '4d28d8b98cf6de28e6eb2195e5ca1e461ab0aea5991a3aa700f2a1330fef5cfe',
    'encoded-controller/common-monomial-terminal-20261018/TERMINAL-PROGRAMS.json':
        'c87e99deeffa12b30b37f633c784118623aba1a4680ad3ae925d29be4f91a4d6',
    'encoded-controller/common-monomial-terminal-20261018/CHECKS.json':
        '27f222e13cc26291fe3d0dd25b1740029c906f5cbb080db79d9599fb262795b2',
    'bridge-access-20261017/cycle-cover-response-20261018/CYCLE-COVER-PROGRAMS.json':
        '759f85673b0fda9ba4ff7312c18c80f8a8b72a3ad0a7b1192a8d08571d0095da',
    'encoded-controller/NORMALIZATION-PROGRAMS.json':
        '7ce02810ecaca13ba084c365ec9c781a211e3c94dbf0f64e8717ca6d1c0b0ca9',
    'circuit-interface/INTERFACE.json':
        '5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3',
    'encoded-controller/cover-line-terminal-limit-20261018/FREEZE.json':
        '4103d8e89f10b8d8dcf7ba54c8e51cc6c685e36b9fff40ad86dc1d6bf532a427',
    'encoded-controller/cover-line-terminal-limit-20261018/LIMIT.md':
        '5e71f90893fafd7e85a7fd49617f6982dfada8079e1223a29135bb957f0707c3',
}


def need(test, label):
    if not test:
        raise ValueError(label)


def parity(value):
    return value.bit_count() & 1


def apply(columns, value):
    out = 0
    for j, column in enumerate(columns):
        if value >> j & 1:
            out ^= column
    return out


def compose(left, right):
    return [apply(left, column) for column in right]


def transpose(columns):
    return [sum(((column >> j) & 1) << i for i, column in enumerate(columns)) for j in range(N)]


def poly_sum(*terms):
    out = {}
    for coefficient, polynomial in terms:
        for monomial, value in polynomial.items():
            new = (out.get(monomial, 0)+coefficient*value) % 4
            if new:
                out[monomial] = new
            else:
                out.pop(monomial, None)
    return out


def bit_phase(vector):
    support = [j for j in range(N) if vector >> j & 1]
    out = {(j,): 1 for j in support}
    out.update({(i, j): 2 for j in support for i in support if i < j})
    return out


def full_phase(columns):
    out = {(j,): column.bit_count() % 4 for j, column in enumerate(columns) if column.bit_count() % 4}
    out.update({(i, j): 2 for j in range(N) for i in range(j) if parity(columns[i] & columns[j])})
    return out


def translation_phase(vector):
    return {(j,): 2 for j in range(N) if vector >> j & 1}


def gmultiply(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def kernel_checks(record, cycle):
    q = record['q']
    last = record['second_native_line']
    child = record['X_child']
    g = child['right_view_payload_at_output_cover_h_columns']
    gi = child['left_view_payload_columns_in_h_coordinates']
    offset = child['left_view_payload_offset']
    epsilon = cycle['FULL_E_inverse_output_translation']
    need(child['rank'] == 2 and child['sign'] == 1, 'One positive rank-two child')
    need(len(g) == len(gi) == N and compose(g, gi) == compose(gi, g) == UNIT, 'Both payload view inverse orders')
    need(gi == transpose(g), 'Orthogonal payload basis')
    need(g[:2] == [q, last] and apply(g, offset) == epsilon, 'Exact child directions and output offset')
    need(child['output_translation_in_h_coordinates'] == epsilon, 'Serialized output translation')
    need(child['right_view_cover_columns'] == cycle['L_inverse_columns'], 'Actual source cover direction')
    transvections = child['basis_transvections_in_time_order']
    need(len(transvections) == 2 and all(not parity(v) for v in transvections), 'Two orthogonal transvections')
    reconstructed = list(UNIT)
    for v in transvections:
        reconstructed = [column ^ (v if parity(v & column) else 0) for column in reconstructed]
    swap = child['basis_input_axis_swap']
    need(swap == [1, 65], 'Literal input-axis swap')
    reconstructed[swap[0]], reconstructed[swap[1]] = reconstructed[swap[1]], reconstructed[swap[0]]
    need(reconstructed == g, 'Literal basis construction')
    need(parity(q) == parity(last) == 1 and not parity(q & last), 'Independent orthogonal native lines')
    # The numerators below have a common denominator four.
    one_line = ((1, 1), (1, -1))
    child_kernel = {mask: gmultiply(one_line[mask & 1], one_line[mask >> 1]) for mask in range(4)}
    actual = {apply(g, mask) ^ apply(g, offset): value for mask, value in child_kernel.items()}
    wanted = {epsilon: (0, 2), epsilon ^ q: (2, 0),
              epsilon ^ last: (2, 0), epsilon ^ q ^ last: (0, -2)}
    need(actual == wanted and len(actual) == 4, 'Complete translated Gaussian child kernel')
    # Check every address coefficient of G(G^-1 w + offset + mask).
    need(compose(g, gi) == UNIT, 'Address coefficients for every payload input')
    for mask in range(4):
        need(apply(g, offset ^ mask) == epsilon ^ (q if mask & 1 else 0) ^ (last if mask & 2 else 0),
             'Every affine child branch')


def controller_check(schedule):
    events = [e for e in schedule if e['kind'] in ('local', 'idle', 'bridge', 'terminal')]
    need(sum(e['kind'] != 'idle' for e in events) == 19 and sum(e['kind'] == 'idle' for e in events) == 10,
         'Pinned retained content and idle counts')
    columns = [{(j, 0): 1} for j in range(8)]

    def add(target, source, coefficient, power=0):
        for (output, exponent), value in list(columns[source].items()):
            key = output, exponent+power
            new = columns[target].get(key, 0)+coefficient*value
            if new:
                columns[target][key] = new
            else:
                columns[target].pop(key, None)

    for event in reversed(events):
        if event['kind'] == 'local':
            x, y = 2*event['pair'], 2*event['pair']+1
            if event['reverse']:
                add(y, x, -1, -1)
            else:
                add(x, y, 1, 1)
        elif event['kind'] == 'bridge':
            d, s, value = 2*event['dst'], 2*event['src'], event['coefficient']
            add(s, d, value)
            add(d+1, s+1, -value)
    wanted = []
    for j in range(4):
        wanted.extend([{(2*j+1, 1): 1}, {(2*j, -1): -1}])
    need(columns == wanted, 'Free Laurent reverse columns of the actual controller')
    old = [e['event'] for e in schedule if e['kind'] == 'retained_physical_event'
           and e['event']['kind'] == 'terminal_Y_translations']
    need(len(old) == 1 and old[0]['pairs'] == [0, 1, 2, 3], 'The old terminal has one line-square map per port pair')
    return {'actual_content_events': 19, 'actual_idle_sites': 10, 'arbitrary_input_blocks': 8,
            'arithmetic': 'Free Laurent integer coefficients; no cycle relation is used.'}


def main():
    for relative, pin in PINS.items():
        need(sha256((LANES/relative).read_bytes()).hexdigest() == pin, 'Source pin '+relative)
    payload = json.loads((SOURCE/'TERMINAL-PROGRAMS.json').read_bytes())
    cycles = json.loads((LANES/'bridge-access-20261017/cycle-cover-response-20261018/CYCLE-COVER-PROGRAMS.json').read_bytes())
    ports = json.loads((LANES/'circuit-interface/INTERFACE.json').read_bytes())['ports']
    schedule = json.loads((LANES/'encoded-controller/NORMALIZATION-PROGRAMS.json').read_bytes())['schedule']
    controller = controller_check(schedule)
    need(len(payload['records']) == len(cycles['records']) == len(ports) == 112, 'Every actual port')
    plain_full = full_phase(UNIT)
    report = []
    for p, (record, cycle) in enumerate(zip(payload['records'], cycles['records'])):
        need(record['port'] == cycle['port'] == p and record['q'] == cycle['q'] == ports[p], 'Actual port binding')
        q, last = record['q'], record['second_native_line']
        left, inverse = cycle['L_columns'], cycle['L_inverse_columns']
        delta, epsilon = cycle['FULL_E_output_translation'], cycle['FULL_E_inverse_output_translation']
        need(inverse == transpose(left) and compose(left, inverse) == compose(inverse, left) == UNIT,
             'Orthogonal cover permutation and both inverse orders')
        need(apply(inverse, q) == last == 1 << 65 and apply(left, epsilon) == delta, 'Source line and translation order')
        need(not parity(q & apply(left, q)) and parity(q & last) == parity(apply(left, q) & q),
             'The general line-cut rank theorem applies to this actual port')
        need(compose(left, left) != UNIT, 'Wrong cover direction is detected')
        sequence = cycle['cycle_vectors']
        need(len(sequence) == 10 and sequence[0] == q and sequence[-1] == last,
             'Ten actual cycle directions')
        need([apply(left, v) for v in sequence] == sequence[1:]+sequence[:1], 'Literal cover cycle')
        forward_phase = full_phase(inverse)
        inverse_phase = full_phase(left)
        need(poly_sum((1, plain_full), (-1, forward_phase)) == translation_phase(delta),
             'Complete forward FULL phase coefficients')
        need(poly_sum((1, plain_full), (-1, inverse_phase)) == translation_phase(epsilon),
             'Complete inverse FULL phase coefficients')
        line_q, line_last = bit_phase(q), bit_phase(last)
        input_v = poly_sum((1, inverse_phase), (-1, line_last))
        terminal_x = poly_sum((1, translation_phase(epsilon)), (1, line_q), (1, line_last))
        need(poly_sum((1, input_v), (1, terminal_x)) == poly_sum((1, plain_full), (1, line_q)),
             'All X phase coefficients equal the raw FQ endpoint')
        need(poly_sum((1, forward_phase), (1, translation_phase(delta))) == plain_full,
             'All Y phase coefficients equal the raw F endpoint')
        need(record['Y_source_map'] == {'cover_columns': left, 'payload_translation_in_h_coordinates': delta},
             'Literal Y cover and translation map')
        need(record['final_exchange'] == '(X,Y)=(processed_V,-processed_U)', 'Exact final bank sign')
        need(delta and epsilon, 'Omitted FULL translations change every port map')
        need(poly_sum((1, input_v), (1, translation_phase(epsilon)), (2, line_q))
             != poly_sum((1, plain_full), (1, line_q)), 'Using the same line twice is rejected')
        need(poly_sum((1, input_v), (1, translation_phase(epsilon)), (1, line_q))
             != poly_sum((1, plain_full), (1, line_q)), 'Omitting the source line is rejected')
        need(poly_sum((1, input_v), (1, translation_phase(epsilon)), (1, line_last))
             != poly_sum((1, plain_full), (1, line_q)), 'Omitting the target line is rejected')
        kernel_checks(record, cycle)
        report.append({'port': p, 'complete_phase_polynomial': True, 'complete_affine_kernel': True,
                       'native_fourier_rank': 2, 'both_cover_address_orders': True})
    inventory = {'pairs': 4, 'ports_per_bank': 112, 'rank_two_children': 448, 'native_rank_mass': 896,
                 'child_wrapper_maps': 896, 'FULL_source_maps': 448, 'total_monomial_maps': 1344,
                 'old_line_square_maps_removed': 448, 'net_added_monomial_maps': 896,
                 'retained_signed_exchanges': 448, 'retained_unit_complex_ADDs': 1344,
                 'retained_exchange_real_primitives': 10752,
                 'new_top_level_scalar_primitives_beyond_retained_exchange': 0, 'new_full_cover_records': 0}
    need(payload['inventory_per_replica'] == inventory, 'Exact finite map and native inventory')
    result = {'status': 'PASS_INDEPENDENT_COMMON_COVER_TERMINAL', 'source_pins': PINS,
              'controller': controller, 'ports': report, 'inventory_per_replica': inventory,
              'method': 'Full Z4 polynomial coefficients and exact affine four-point Gaussian kernel; reverse columns for the pinned content schedule; no producer imports.',
              'scope': 'Finite terminal with admitted map and child operations. No recursive hosting, map-time price, complete supplier invoice, or precision certificate.',
              'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE/'CHECKS.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'])


if __name__ == '__main__':
    main()
