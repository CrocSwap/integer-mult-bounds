#!/usr/bin/env python3
"""Check a native symmetric response with eight centres on 48 ports."""
import ast
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARTIAL = HERE.parent / 'partial-orthogonal'
spec = importlib.util.spec_from_file_location('partial_tools', PARTIAL / 'check_partial_orthogonal.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
SYMMETRIC_PIN = '84e527589ab11fa59136e262c75511d9f71af1ba55504fb59b73ac789a350dff'
GEOMETRY_PIN = '77fc35b5d78f9dd53193ecb38977e31a7cb9d5c23f0e3839d39f6ea4963f04c2'


def pin_json(path, pin):
    raw = path.read_bytes()
    p.need(sha256(raw).hexdigest() == pin, ('Source pin', str(path)))
    return json.loads(raw)


def identity(n):
    return [{i: F(1)} for i in range(n)]


def perfect_matchings(vertices, edges):
    if not vertices:
        yield []
        return
    first = min(vertices)
    for other in sorted(vertices - {first}):
        edge = tuple(sorted((first, other)))
        if edge in edges:
            for rest in perfect_matchings(vertices - {first, other}, edges):
                yield [edge] + rest


def factor_edges(edges):
    if not edges:
        return []
    for matching in perfect_matchings(set(range(8)), edges):
        rest = factor_edges(edges - set(matching))
        if rest is not None:
            return [matching] + rest
    return None


def main():
    geometry = pin_json(PARTIAL / 'SYMMETRIC-FAMILY.json', GEOMETRY_PIN)
    symmetric = pin_json(p.SOURCE / 'SYMMETRIC-RESPONSE-SEARCH.json', SYMMETRIC_PIN)
    space = p.read('RESPONSE-SPACE.json')
    response = [{} for _ in range(112)]
    mode_weights = {}
    for i, direction in enumerate(symmetric['symmetric_directions'][:40]):
        weight = F(2 if i % 4 in (2, 3) else 1) if i < 32 else (F(1, 2) if i in (32, 37) else F(-1))
        for pair, value in direction['effect'].items():
            row, column = ast.literal_eval(pair)
            p.add(response[row], {column: p.lift(value)}, weight)
        for mode, value in direction['recipe'].items():
            mode = int(mode)
            mode_weights[mode] = mode_weights.get(mode, F(0)) + weight * p.lift(value)
    mode_weights = {i: value for i, value in mode_weights.items() if value}
    independent = [{} for _ in range(112)]
    event_weights = {}
    for mode, coefficient in mode_weights.items():
        for pair, value in space['directions'][mode]['effect'].items():
            row, column = ast.literal_eval(pair)
            p.add(independent[row], {column: p.lift(value)}, coefficient)
        for position, value in space['directions'][mode]['events'].items():
            position = int(position)
            event_weights[position] = event_weights.get(position, F(0)) + coefficient * p.lift(value)
    event_weights = {i: value for i, value in event_weights.items() if value}
    p.need(response == independent, 'Exact response recipes')
    p.need(response == p.transpose(response), 'Symmetric response')
    large, small = geometry['large_ports'], geometry['small_ports']
    centres = []
    for vertex in geometry['vertices']:
        row = {}
        for column in vertex['pair_columns']:
            p.add(row, {int(i): F(value) for i, value in column.items()})
        centres.append(row)
    gram = [{j: sum((row.get(k, F(0)) * other.get(k, F(0)) for k in large), F(0))
             for j, other in enumerate(centres)} for row in centres]
    gram = [{j: value for j, value in row.items() if value} for row in gram]
    p.need(gram == [{i: F(12)} for i in range(8)], 'Eight orthogonal centre rows')
    outer = [{} for _ in range(112)]
    for row in centres:
        for i, value in row.items():
            p.add(outer[i], row, value)
    projector = [{j: value / 12 for j, value in row.items()} for row in outer]
    p.need(p.product(projector, projector) == projector, 'Rank-eight centre projector')
    for i in large:
        expected = {j: value / 2 for j, value in outer[i].items()}
        p.add(expected, {i: F(1)}, -1)
        p.need(response[i] == expected, 'Exact rank-eight response formula')
    inverse = [{} for _ in range(112)]
    for i in small:
        inverse[i] = {j: value / 4 for j, value in response[i].items()}
    for i in large:
        inverse[i] = {j: value / 10 for j, value in outer[i].items()}
        p.add(inverse[i], {i: F(1)}, -1)
    p.need(p.product(response, inverse) == p.product(inverse, response) == identity(112),
           'Both exact inverse orders')
    determinant = p.determinant(response)
    p.need(determinant == 2**64 * 5**8, 'Exact determinant')

    edge_ports = {tuple(edge['vertices']): edge['ports'] for edge in geometry['pair_edges']}
    matchings = factor_edges(set(edge_ports))
    p.need(matchings is not None and len(matchings) == 6, 'Six disjoint perfect matchings')
    minor_ports = [sorted(port for edge in matching for port in edge_ports[edge]) for matching in matchings]
    p.need(sorted(port for ports in minor_ports for port in ports) == large, 'Partition of 48 ports')
    for ports in minor_ports:
        actual = [[sum((left.get(j, F(0)) * right.get(j, F(0)) for j in ports), F(0))
                   for right in centres] for left in centres]
        p.need(actual == [[F(2) if i == j else F(0) for j in range(8)] for i in range(8)],
               'Orthogonal eight-port centre minor')
    gauge_reports = {}
    for count in (1, 2, 3, 4):
        selected = sorted(port for ports in minor_ports[:count] for port in ports)
        ordinary = sorted(set(large) - set(selected))
        h = [{j: (F(i == j) - outer[i].get(j, F(0)) / 2) for j in ordinary}
             for i in ordinary]
        hi = [{j: (F(i == j) + outer[i].get(j, F(0)) / (2 * (count - 5))) for j in ordinary}
              for i in ordinary]
        remap = {port: i for i, port in enumerate(ordinary)}
        h = [{remap[j]: value for j, value in row.items() if value} for row in h]
        hi = [{remap[j]: value for j, value in row.items() if value} for row in hi]
        p.need(p.product(h, hi) == p.product(hi, h) == identity(len(ordinary)), 'Ordinary gauge inverse')
        report = {'selected_ports': selected, 'ordinary_ports': ordinary,
                  'selected_centre_compression': count, 'ordinary_centre_compression': 6 - count,
                  'ordinary_inverse_denominator': count - 5}
        if count > 1:
            signs = {i: F(-1) if i in selected else F(1) for i in large}
            a, ai = [], []
            remap = {port: i for i, port in enumerate(large)}
            for i in large:
                row = {j: value / (2 * (count - 5)) for j, value in outer[i].items()}
                p.add(row, {i: signs[i]})
                a.append({remap[j]: value for j, value in row.items() if value})
                row = {j: signs[i] * value * signs[j] / (2 * (count - 1)) for j, value in outer[i].items()}
                p.add(row, {i: signs[i]})
                ai.append({remap[j]: value for j, value in row.items() if value})
            p.need(p.product(a, ai) == p.product(ai, a) == identity(48), 'Data gauge inverse')
            report['data_inverse_denominator'] = count - 1
            report['data_map_determinant'] = str(p.determinant(a))
        gauge_reports[str(count)] = report

    spec = importlib.util.spec_from_file_location('structured_probe', p.SOURCE / 'probe_readiness.py')
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    payload = {'schema': 'native-structured-centres-v1', 'response': p.encode(response),
               'centre_rows': p.encode(centres), 'projector': p.encode(projector),
               'inverse': p.encode(inverse), 'providers': {}}
    receipt = {'status': 'PASS_NATIVE_STRUCTURED_CENTRES', 'source_core_sha256': probe.PIN,
               'symmetric_source_sha256': SYMMETRIC_PIN, 'geometry_sha256': GEOMETRY_PIN,
               'response_space_sha256': p.PINS['RESPONSE-SPACE.json'],
               'determinant': str(determinant), 'centre_rank': 8,
               'centre_support_ports': large, 'centre_row_supports': [sorted(row) for row in centres],
               'perfect_matchings': matchings, 'orthogonal_minor_ports': minor_ports,
               'gauge_identities': gauge_reports, 'providers': {}}
    for provider, item in probe.core['providers'].items():
        word = item['canonical']
        n = len(word['start'])
        initial = {i: {(i, ()): F(1)} for i in range(n + 8)}
        split = item['programs']['forward'].index(['phase', 'zero_frame_precondition'])
        programs, reports = {}, {}
        for direction in ('forward', 'backward'):
            backward = direction == 'backward'
            program = [['phase', 'structured_centres_response']] + [
                ['scalar', ['clear', ['C', i]], 0] for i in range(8)]
            for position in range(split, len(item['programs'][direction])):
                event = deepcopy(item['programs'][direction][position])
                forward = item['programs']['forward'][position]
                if forward[0] == 'scalar' and forward[1][0] == 'add':
                    target, source = forward[1][1:3]
                    is_y = lambda slot: slot[0] == 'L' and 112 <= slot[1] < 224
                    if is_y(target) and not is_y(source):
                        coefficient = event_weights.get(position, F(0))
                        if not coefficient:
                            continue
                        if backward:
                            p.need(event[1][1:3] == [source, target], 'Transpose transfer site')
                            coefficient = -coefficient
                        event[1][3:5] = [coefficient.numerator, coefficient.denominator]
                program.append(event)
            actual = probe.e.core_replay(program, initial, word, backward)[0]
            expected = deepcopy(initial)
            for i in range(n, n + 8):
                expected[i] = {}
            for i, row in enumerate(response):
                for j, coefficient in row.items():
                    p.add(expected[j if backward else 112 + i],
                          initial[112 + i if backward else j], -coefficient if backward else coefficient)
            p.need(all(actual[i] == expected[i] for i in range(n + 8)), 'All native columns and helpers')
            native = lambda event: event[0] in ('climb', 'warp', 'adapter', 'residual_adapter')
            p.need([event for event in program if native(event)] ==
                   [event for event in item['programs'][direction] if native(event)], 'Unchanged native records')
            profile = Counter(event[5] for event in program if event[0] == 'climb')
            reports[direction] = {'all_input_columns': n + 8, 'borrowed_helpers_restored': n - 224,
                                  'private_zero_buffers_restored': len(word['zero_buffers']),
                                  'owned_outputs_zero': 8,
                                  'scalar_real_primitives': probe.e.core_price(program),
                                  'native_profile': dict(sorted(profile.items())),
                                  'native_rank_mass': sum(k*v for k, v in profile.items()),
                                  'native_children': sum(profile.values()), 'native_records_identical': True}
            programs[direction] = program
        payload['providers'][provider] = {'canonical': word, 'programs': programs}
        receipt['providers'][provider] = reports
        print(provider, reports, flush=True)
    raw = (json.dumps(payload, sort_keys=True, separators=(',', ':')) + '\n').encode()
    (HERE / 'STRUCTURED-CENTRES-PROGRAM.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    receipt['payload_decompressed_sha256'] = sha256(raw).hexdigest()
    receipt['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    receipt['scope'] = ('Native forward response and negative transpose, exact rank-eight inverse formula, '
                        'and algebraic gauge identities. Division by five, physical gauge programs, '
                        'supplier code transport, terminal decoding, and recursive pricing are not implemented here.')
    (HERE / 'STRUCTURED-CENTRES.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(receipt['status'], receipt['payload_decompressed_sha256'], flush=True)


if __name__ == '__main__':
    main()
