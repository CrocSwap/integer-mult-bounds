#!/usr/bin/env python3
"""Check a signed response with eight selected ports and dyadic gauges."""
import ast
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STRUCTURED = HERE.parent / 'structured-centres'
sys.path.insert(0, str(STRUCTURED))
import check_structured_centres as source
import check_rank8_gauges as gauge

p = source.p
SELECTED = [0, 7, 15, 36, 42, 46, 79, 89]
SIGNS = [1, -1, 1, -1, 1, -1, 1, -1]


def restrict(matrix, ports):
    index = {port: i for i, port in enumerate(ports)}
    return [{index[j]: value for j, value in matrix[i].items() if j in index}
            for i in ports]


def dyadic(value):
    return value.denominator & (value.denominator - 1) == 0


def unit(value):
    numerator = abs(value.numerator)
    return numerator and numerator & (numerator - 1) == 0 and dyadic(value)


def inverse_word(word):
    result = []
    for event in reversed(word):
        gate = event[1]
        if gate[0] == 'add':
            result.append(gauge.scalar('add', gate[1][1], gate[2][1], -F(*gate[3:5])))
        else:
            p.need(gate[0] == 'scale', 'Invertible scalar gate')
            result.append(gauge.scalar('scale', gate[1][1], 1 / F(*gate[2:4])))
    return result


def swap_word(left, right):
    return [gauge.scalar('add', left, right, F(1)),
            gauge.scalar('add', right, left, F(-1)),
            gauge.scalar('add', left, right, F(1)),
            gauge.scalar('scale', right, F(-1))]


def monomial_word(matrix, ports):
    word, seen = [], set()
    for i in ports:
        if i in seen:
            continue
        p.need(len(matrix[i]) == 1, 'Monomial row')
        j, coefficient = next(iter(matrix[i].items()))
        p.need(j in ports and coefficient in (-1, 1), 'Signed closed monomial')
        if i != j:
            p.need(matrix[j] == {i: coefficient}, 'Involutory signed pair')
            word += swap_word(i, j)
            if coefficient == -1:
                word += [gauge.scalar('scale', i, F(-1)), gauge.scalar('scale', j, F(-1))]
        elif coefficient == -1:
            word.append(gauge.scalar('scale', i, F(-1)))
        seen.update((i, j))
    return word


def factor(matrix, ports):
    """Reduce a dyadic-unit matrix with dyadic ADDs and unit SCALEs."""
    size = len(ports)
    rows = [[matrix[i].get(j, F(0)) for j in range(size)] for i in range(size)]
    word = []

    def add(target, source_index, coefficient):
        if not coefficient:
            return
        p.need(dyadic(coefficient), 'Dyadic ADD coefficient')
        rows[target] = [a + coefficient * b for a, b in zip(rows[target], rows[source_index])]
        word.append(gauge.scalar('add', ports[target], ports[source_index], coefficient))

    def scale(target, coefficient):
        if coefficient == 1:
            return
        p.need(unit(coefficient), 'Dyadic-unit SCALE coefficient')
        rows[target] = [coefficient * a for a in rows[target]]
        word.append(gauge.scalar('scale', ports[target], coefficient))

    def swap(left, right):
        if left == right:
            return
        add(left, right, F(1))
        add(right, left, F(-1))
        add(left, right, F(1))
        scale(right, F(-1))

    for column in range(size):
        nonzero = [i for i in range(column, size) if rows[i][column]]
        p.need(nonzero, ('Nonsingular gauge', column))
        cheap = [i for i in nonzero if unit(rows[i][column])]
        swap(column, min(cheap or nonzero, key=lambda i: abs(rows[i][column])))
        if not unit(rows[column][column]):
            for other in range(column + 1, size):
                while rows[other][column]:
                    quotient = rows[other][column] // rows[column][column]
                    add(other, column, F(-quotient))
                    if rows[other][column]:
                        swap(column, other)
        p.need(unit(rows[column][column]), 'Unit pivot after exact row gcd')
        scale(column, 1 / rows[column][column])
        for other in range(size):
            if other != column:
                add(other, column, -rows[other][column])
    p.need(rows == [[F(i == j) for j in range(size)] for i in range(size)], 'Exact elimination')
    inverse = gauge.replay(word)
    forward_word = inverse_word(word)
    forward = gauge.replay(forward_word)
    p.need(restrict(forward, ports) == matrix, 'Forward scalar factor')
    identity = [{i: F(1)} for i in range(112)]
    p.need(p.product(forward, inverse) == p.product(inverse, forward) == identity, 'Both scalar inverse orders')
    return forward_word, word, restrict(inverse, ports)


def main():
    geometry = source.pin_json(source.PARTIAL / 'SYMMETRIC-FAMILY.json', source.GEOMETRY_PIN)
    symmetric = source.pin_json(p.SOURCE / 'SYMMETRIC-RESPONSE-SEARCH.json', source.SYMMETRIC_PIN)
    space = p.read('RESPONSE-SPACE.json')
    large, small = geometry['large_ports'], geometry['small_ports']
    ordinary = sorted(set(large) - set(SELECTED))
    response = [{} for _ in range(112)]
    mode_weights = {}
    for i, direction in enumerate(symmetric['symmetric_directions'][:40]):
        if i < 32:
            weight = F(-2 if i % 4 in (2, 3) else -1)
        else:
            weight = -F(SIGNS[i - 32], 2) if i in (32, 37) else F(SIGNS[i - 32])
        for pair, value in direction['effect'].items():
            row, column = ast.literal_eval(pair)
            p.add(response[row], {column: p.lift(value)}, weight)
        for mode, value in direction['recipe'].items():
            mode = int(mode)
            mode_weights[mode] = mode_weights.get(mode, F(0)) + weight * p.lift(value)
    mode_weights = {i: value for i, value in mode_weights.items() if value}
    event_weights = {}
    independent = [{} for _ in range(112)]
    for mode, coefficient in mode_weights.items():
        for pair, value in space['directions'][mode]['effect'].items():
            row, column = ast.literal_eval(pair)
            p.add(independent[row], {column: p.lift(value)}, coefficient)
        for position, value in space['directions'][mode]['events'].items():
            position = int(position)
            event_weights[position] = event_weights.get(position, F(0)) + coefficient * p.lift(value)
    event_weights = {i: value for i, value in event_weights.items() if value}
    p.need(response == independent == p.transpose(response), 'Exact symmetric source recipe')

    centres, signed_monomial = [], [{} for _ in range(112)]
    inverse = [{} for _ in range(112)]
    formula = [{} for _ in range(112)]
    for v, vertex in enumerate(geometry['vertices']):
        row = {}
        for column in vertex['pair_columns']:
            column = {int(i): F(value) for i, value in column.items()}
            p.add(row, column)
            for i, value in column.items():
                for target in (signed_monomial, inverse, formula):
                    p.add(target[i], column, F(SIGNS[v]) * value / 2)
        centres.append(row)
        for i, value in row.items():
            p.add(inverse[i], row, -F(SIGNS[v]) * value / 10)
            p.add(formula[i], row, -F(SIGNS[v]) * value / 2)
    for i in small:
        formula[i] = dict(response[i])
        inverse[i] = {j: value / 4 for j, value in response[i].items()}
    previous_raw = gzip.decompress((STRUCTURED / 'STRUCTURED-CENTRES-PROGRAM.json.gz').read_bytes())
    p.need(sha256(previous_raw).hexdigest() == gauge.PIN, 'Pinned preceding native response')
    previous = json.loads(previous_raw)
    p.need(all(response[i] == {int(j): -F(value) for j, value in previous['response'][i].items()}
               for i in small), 'Unchanged negative Hadamard 64-port response')
    p.need(formula == response, 'Signed projector and centre formula')
    p.need(all(len(signed_monomial[i]) == 1 and next(iter(signed_monomial[i].values())) in (-1, 1)
               for i in large), 'Signed physical port permutation')
    identity = [{i: F(1)} for i in range(112)]
    p.need(p.product(response, inverse) == p.product(inverse, response) == identity, 'Both full inverse orders')
    p.need(all(not signed_monomial[i].get(j) for i in SELECTED for j in SELECTED), 'Selected set crosses sign partition')
    selected_block = restrict(response, SELECTED)
    selected_inverse_block = restrict(inverse, SELECTED)
    p.need(selected_inverse_block == [{j: value / 5 for j, value in row.items()} for row in selected_block],
           'Inverse selected compression is one fifth')
    h = restrict(response, ordinary)
    determinants = {'selected': p.determinant(selected_block), 'ordinary': p.determinant(h),
                    'large_response': p.determinant(restrict(response, large)), 'full_response': p.determinant(response)}
    p.need(determinants['selected'] == determinants['ordinary'] == F(1, 16), 'Both principal determinants are dyadic units')
    p.need(determinants['large_response'] == 5**8, 'Full 48-port response retains odd determinant')
    h_word, hi_word, hi = factor(h, ordinary)
    elimination_h_word, elimination_hi_word = h_word, hi_word
    partners = sorted(next(iter(signed_monomial[i])) for i in SELECTED)
    residual = sorted(set(ordinary) - set(partners))
    p.need(len(partners) == 8 and not set(partners) & set(SELECTED), 'Eight disjoint physical partners')
    kt = [{j: row.get(port, F(0)) for j, port in enumerate(partners) if row.get(port)} for row in centres]
    ks = [{j: row.get(port, F(0)) for j, port in enumerate(SELECTED) if row.get(port)} for row in centres]
    kt_word, _, _ = factor(kt, partners)
    ktt_word, _, _ = factor(p.transpose(kt), partners)
    h_word = kt_word
    for i, row in enumerate(centres):
        h_word += [gauge.scalar('add', partners[i], j, row[j]) for j in residual if j in row]
    h_word += [gauge.scalar('scale', partners[i], -F(SIGNS[i], 2)) for i in range(8)]
    h_word += monomial_word(signed_monomial, residual)
    for i, row in enumerate(centres):
        h_word += [gauge.scalar('add', j, partners[i], row[j]) for j in residual if j in row]
    h_word += ktt_word
    hi_word = inverse_word(h_word)
    p.need(restrict(gauge.replay(h_word), ordinary) == h, 'Structured ordinary gauge')
    p.need(restrict(gauge.replay(hi_word), ordinary) == hi, 'Structured inverse ordinary gauge')

    si, ui = {port: i for i, port in enumerate(SELECTED)}, {port: i for i, port in enumerate(ordinary)}
    j_su = [{ui[j]: value for j, value in response[i].items() if j in ui} for i in SELECTED]
    j_us = [{si[j]: value for j, value in response[i].items() if j in si} for i in ordinary]
    su_hi, hi_us = p.product(j_su, hi), p.product(hi, j_us)
    cross = p.product(su_hi, j_us)
    data = [{} for _ in range(112)]
    for port in small:
        data[port] = {port: F(1)}
    for i, port in enumerate(SELECTED):
        for j, column in enumerate(SELECTED):
            value = -selected_block[i].get(j, F(0)) + cross[i].get(j, F(0))
            if value:
                data[port][column] = value
        p.add(data[port], {ordinary[j]: value for j, value in su_hi[i].items()}, -1)
    for i, port in enumerate(ordinary):
        data[port] = {ordinary[j]: value for j, value in hi[i].items()}
        p.add(data[port], {SELECTED[j]: value for j, value in hi_us[i].items()}, -1)
    a = restrict(data, large)
    a_word, ai_word, ai = factor(a, large)
    elimination_a_word, elimination_ai_word = a_word, ai_word
    negative_l = [{j: -value for j, value in row.items()} for row in selected_block]
    negative_l_word, _, _ = factor(negative_l, SELECTED)
    a_word = [gauge.scalar('add', port, SELECTED[j], -value)
              for i, port in enumerate(ordinary) for j, value in sorted(j_us[i].items())]
    a_word += negative_l_word + hi_word
    a_word += [gauge.scalar('add', port, ordinary[j], -value)
               for i, port in enumerate(SELECTED) for j, value in sorted(j_su[i].items())]
    ai_word = inverse_word(a_word)
    p.need(restrict(gauge.replay(a_word), large) == a, 'Structured data gauge')
    p.need(restrict(gauge.replay(ai_word), large) == ai, 'Structured inverse data gauge')
    determinants['data'] = p.determinant(a)
    p.need(determinants['data'] == 1, 'Unit data determinant')
    programs = {'ordinary': h_word, 'ordinary_inverse': hi_word, 'data': a_word, 'data_inverse': ai_word}
    maps = {'ordinary': h, 'ordinary_inverse': hi, 'data': a, 'data_inverse': ai}
    p.need(all(dyadic(value) for rows in maps.values() for row in rows for value in row.values()), 'All gauge entries are dyadic')

    spec = importlib.util.spec_from_file_location('bipartite_probe', p.SOURCE / 'probe_readiness.py')
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    reports = {name: {'scalar_real_primitives': probe.e.core_price(word), 'native_children': 0,
                      'owned_fields': 0, 'all_input_columns': 112, 'gates': len(word)}
               for name, word in programs.items()}
    payload = {'schema': 'bipartite-eight-native-v1', 'response': p.encode(response),
               'inverse': p.encode(inverse), 'selected_ports': SELECTED, 'ordinary_centre_ports': ordinary,
               'large_ports': large, 'small_ports': small, 'component_signs': SIGNS,
               'centre_rows': p.encode(centres), 'signed_monomial': p.encode(signed_monomial),
               'partner_ports': partners, 'residual_ports': residual,
               'gauge_maps': {name: p.encode(rows) for name, rows in maps.items()},
               'gauge_programs': programs, 'providers': {}}
    receipt = {'status': 'PASS_BIPARTITE_EIGHT_NATIVE_AND_GAUGES',
               'geometry_sha256': source.GEOMETRY_PIN, 'symmetric_source_sha256': source.SYMMETRIC_PIN,
               'response_space_sha256': p.PINS['RESPONSE-SPACE.json'], 'source_core_sha256': probe.PIN,
               'selected_ports': SELECTED, 'component_signs': SIGNS,
               'partner_ports': partners, 'residual_ports': residual,
               'selected_centre_minor_determinant': str(p.determinant(ks)),
               'partner_centre_minor_determinant': str(p.determinant(kt)),
               'determinants': {name: str(value) for name, value in determinants.items()},
               'gauge_reports': reports,
               'independent_elimination_prices': {
                   'ordinary': probe.e.core_price(elimination_h_word),
                   'ordinary_inverse': probe.e.core_price(elimination_hi_word),
                   'data': probe.e.core_price(elimination_a_word),
                   'data_inverse': probe.e.core_price(elimination_ai_word)}, 'providers': {}}
    for provider, item in probe.core['providers'].items():
        canonical = item['canonical']
        n = len(canonical['start'])
        initial = {i: {(i, ()): F(1)} for i in range(n + 8)}
        split = item['programs']['forward'].index(['phase', 'zero_frame_precondition'])
        native_programs, native_reports = {}, {}
        for direction in ('forward', 'backward'):
            backward = direction == 'backward'
            program = [['phase', 'bipartite_eight_response']] + [['scalar', ['clear', ['C', i]], 0] for i in range(8)]
            for position in range(split, len(item['programs'][direction])):
                event = deepcopy(item['programs'][direction][position])
                forward = item['programs']['forward'][position]
                if forward[0] == 'scalar' and forward[1][0] == 'add':
                    target, source_slot = forward[1][1:3]
                    is_y = lambda slot: slot[0] == 'L' and 112 <= slot[1] < 224
                    if is_y(target) and not is_y(source_slot):
                        coefficient = event_weights.get(position, F(0))
                        if not coefficient:
                            continue
                        if backward:
                            p.need(event[1][1:3] == [source_slot, target], 'Transpose transfer site')
                            coefficient = -coefficient
                        event[1][3:5] = [coefficient.numerator, coefficient.denominator]
                program.append(event)
            actual = probe.e.core_replay(program, initial, canonical, backward)[0]
            expected = deepcopy(initial)
            for i in range(n, n + 8):
                expected[i] = {}
            for i, row in enumerate(response):
                for j, coefficient in row.items():
                    p.add(expected[j if backward else 112 + i], initial[112 + i if backward else j],
                          -coefficient if backward else coefficient)
            p.need(all(actual[i] == expected[i] for i in range(n + 8)), 'All native input columns and helpers')
            native = lambda event: event[0] in ('climb', 'warp', 'adapter', 'residual_adapter')
            p.need([event for event in program if native(event)] ==
                   [event for event in item['programs'][direction] if native(event)], 'Unchanged native records')
            profile = Counter(event[5] for event in program if event[0] == 'climb')
            native_reports[direction] = {'all_input_columns': n + 8, 'borrowed_helpers_restored': n - 224,
                                         'private_zero_buffers_restored': len(canonical['zero_buffers']),
                                         'owned_outputs_zero': 8, 'scalar_real_primitives': probe.e.core_price(program),
                                         'native_profile': dict(sorted(profile.items())),
                                         'native_rank_mass': sum(k*v for k, v in profile.items()),
                                         'native_children': sum(profile.values()), 'native_records_identical': True}
            native_programs[direction] = program
        payload['providers'][provider] = {'canonical': canonical, 'programs': native_programs}
        receipt['providers'][provider] = native_reports
        print(provider, native_reports, flush=True)
    raw = (json.dumps(payload, sort_keys=True, separators=(',', ':')) + '\n').encode()
    (HERE / 'BIPARTITE-EIGHT-PROGRAM.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    receipt['payload_decompressed_sha256'] = sha256(raw).hexdigest()
    receipt['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    receipt['scope'] = ('Native core and exact common-frame gauges. The structured gauge words agree with independent exact elimination. '
                        'Physical selected boundaries, inter-stage views, supplier decoder, and recursive pricing remain separate.')
    (HERE / 'BIPARTITE-EIGHT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(receipt['status'], reports, receipt['payload_decompressed_sha256'], flush=True)


if __name__ == '__main__':
    main()
