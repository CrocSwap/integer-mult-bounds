#!/usr/bin/env python3
"""Exact cold-basis inverse-support obstruction; Python standard library only.

Apache-2.0. Substantial OpenAI Codex assistance. The commuting-ADD
coalescer is adapted, with credit, from Cinna Davis's
research/scalar-trace-compression/verify.py (PR4692). Its crossed
instructions are independently checked here before each merge.

The source matrix, quotient, annihilator and suffix graphs are rebuilt
from the integrated combined word. No discovery compiler, matrix fixture,
numerical optimizer, native-suite execution or network access is used.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'productive-helper-fusion-certificate/COMBINED-WORD.json.gz'
SOURCE_SHA256 = 'aa4a8241da76abd2c06e6576a3ac09e77781321deaac3ad7d3ce4519342a36e6'
LO, HI = 9961, 10111
PAIRED = (417, 419)
TARGETS = (78, 99, 431)
EXPECTED_CAPS = {78: [25, 45, 462], 99: [45, 76, 411], 431: [45, 76]}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def read_source(path=SOURCE):
    return json.loads(gzip.decompress(Path(path).read_bytes()))


def span(vectors):
    values = {0}
    for vector in vectors:
        values |= {x ^ vector for x in tuple(values)}
    return frozenset(values)


def basis(values):
    result, seen = [], {0}
    for vector in sorted(values):
        if vector not in seen:
            result.append(vector)
            seen |= {x ^ vector for x in tuple(seen)}
    return result


def ident(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def mul(a, b):
    return [[sum(x * b[k][j] for k, x in enumerate(row) if x)
             for j in range(len(b[0]))] for row in a]


def inverse(a):
    n = len(a)
    rows = [list(row) + unit for row, unit in zip(a, ident(n))]
    for column in range(n):
        pivot = next((r for r in range(column, n) if rows[r][column]), None)
        need(pivot is not None, 'singular rational matrix')
        rows[pivot], rows[column] = rows[column], rows[pivot]
        scale = rows[column][column]
        rows[column] = [x / scale for x in rows[column]]
        for r in range(n):
            if r != column:
                scale = rows[r][column]
                rows[r] = [x - scale * y for x, y in zip(rows[r], rows[column])]
    result = [row[n:] for row in rows]
    need(mul(a, result) == mul(result, a) == ident(n), 'two-sided rational inverse')
    return result


def refs(event):
    if event[0] == 'scalar':
        g = event[1]
        return g[1:3] if g[0] in ('add', 'copy') else g[1:2]
    if event[0] == 'warp':
        return [event[1]]
    return []


def add(dst, src, coefficient, frame):
    coefficient = Q(coefficient)
    return ['scalar', ['add', list(dst), list(src), coefficient.numerator, coefficient.denominator], frame]


def scale(dst, coefficient, frame):
    coefficient = Q(coefficient)
    return ['scalar', ['scale', list(dst), coefficient.numerator, coefficient.denominator], frame]


def scalar_matrix(events, roles):
    index = {r: i for i, r in enumerate(roles)}
    rows = ident(len(roles))
    for event in events:
        need(event[0] == 'scalar' and all(t == 'L' and r in index for t, r in refs(event)),
             'pure persistent local scalar circuit')
        g = event[1]
        i = index[g[1][1]]
        if g[0] == 'add':
            j, c = index[g[2][1]], Q(*g[3:5])
            need(i != j, 'distinct ADD roles')
            rows[i] = [x + c * y for x, y in zip(rows[i], rows[j])]
        elif g[0] == 'scale':
            c = Q(*g[2:4])
            need(bool(c), 'invertible scalar SCALE')
            rows[i] = [c * x for x in rows[i]]
        else:
            raise ValueError('noninvertible local scalar operation')
    return rows


def local_boundaries(payload, program):
    current = payload['canonical']['start'][:]
    entrance = None
    for ordinal, event in enumerate(program):
        if ordinal == LO:
            entrance = current[:]
        if ordinal == HI:
            need(entrance is not None, 'local source boundaries')
            return entrance, current
        if event[0] == 'scalar':
            for typ, role in refs(event):
                if typ == 'L':
                    current[role] = event[2]
        elif event[0] == 'warp':
            current[event[1][1]] = event[4]
    raise ValueError('missing local source interval')


def annihilator(alpha, dinv, index, cold, terms=((78, Q(-1)), (431, Q(1, 2)))):
    need(any(alpha.values()), 'nonzero compensation vector')
    for role in cold:
        need(alpha[role] == sum(coef * dinv[index[role]][index[column]] for column, coef in terms),
             'cold-projected annihilator identity')


def local_model(payload):
    program = [e for e in payload['programs']['forward'] if e[0] != 'climb']
    need(program[6262] == ['phase', 'A'] and program[10315] == ['phase', 'centers'], 'source phase bounds')
    segment = program[LO:HI]
    roles = sorted({r for e in segment for t, r in refs(e)})
    need(roles == [13, 16, 43, 44, 51, 78, 99, 104] + list(range(416, 432)), 'exact24 local roles')
    n, index = len(roles), {r: i for i, r in enumerate(roles)}
    matrix = scalar_matrix(segment, roles)
    transformed = deepcopy(matrix)
    a, b = matrix[index[417]], matrix[index[419]]
    transformed[index[417]] = [x / 2 - y for x, y in zip(a, b)]
    transformed[index[419]] = [x / 2 + y for x, y in zip(a, b)]
    transformed[index[416]], transformed[index[417]] = transformed[index[417]], transformed[index[416]]
    need(transformed[index[416]] == [Q(r in (13, 416)) for r in roles], 'reserved row is entry13 plus dirty entry416')
    # S=P*T*M*E^-1, E:416+=13. Right multiplication subtracts
    # column416 from column13, and makes row416 an identity row.
    schur = deepcopy(transformed)
    for row in schur:
        row[index[13]] -= row[index[416]]
    need(schur[index[416]] == ident(n)[index[416]], 'S fixes reserved carrier')
    sinv = inverse(schur)
    alpha = {r: -sinv[index[r]][index[416]] for r in roles if r != 416}
    dbase = deepcopy(schur)
    for i in range(n):
        dbase[i][index[416]] = Q(i == index[416])
    dinv = inverse(dbase)
    lower = ident(n)
    for r, c in alpha.items():
        lower[index[r]][index[416]] = c
    need(mul(dbase, lower) == schur, 'exact block-LU factorization')
    entrance, exits = local_boundaries(payload, program)
    frames = payload['canonical']['frames']
    cold = [r for r in roles if r != 416 and entrance[r] == 0]
    need(cold == list(range(417, 432)), 'fifteen cold outside inputs')
    need(frames[entrance[416]] == [] and frames[entrance[13]] == [73], 'E prefix availability')
    need(all(not c for r, c in alpha.items() if r not in cold), 'all compensation supported on cold inputs')
    annihilator(alpha, dinv, index, cold)
    need(all(payload['canonical']['start'][r] == 0 and payload['canonical']['final'][r] == 1
             for r in (416, 417, 419)), 'nominated helper endpoint contracts')
    return {'roles': roles, 'index': index, 'cold': cold, 'alpha': alpha,
            'D_inverse': dinv, 'entrance': entrance, 'exits': exits,
            'matrix_hash': digest([[str(x) for x in row] for row in matrix]),
            'quotient_hash': digest([[str(x) for x in row] for row in dbase])}


def native_binding(payload):
    maps = {w['op']: w['G_columns'] for w in payload['canonical']['warps']}
    need(maps[34] == maps[35], 'paired full native maps equal')
    result = {}
    for direction, raw in payload['programs'].items():
        program = [e for e in raw if e[0] != 'climb']
        uses = [(i, e) for i, e in enumerate(program) if e[0] == 'warp' and e[1][1] in (416, 417, 419)]
        need([i for i, e in uses] == [11491, 11492, 13455, 13456], 'complete paired native census')
        need([e[2] for i, e in uses] == [34, 35, -35, -34], 'paired positive/inverse operator order')
        for (i, e), (j, f) in (uses[:2], uses[2:]):
            need(j == i + 1 and e[3:] == f[3:], 'adjacent equal-chart native block')
        need(not any(e[0] == 'adapter' and e[2] in (416, 417, 419) for e in program), 'no nominated helper adapter')
        result[direction] = [{'source_ordinal': i, 'op': e[2], 'role': e[1][1]} for i, e in uses]
    return result


def emit_two(matrix, frame):
    """Deterministic two-row Gaussian factorization, checked exactly."""
    a, operations = deepcopy(matrix), []

    def row_add(i, j, c):
        if c:
            operations.append(('add', i, j, c))
            a[i] = [x + c * y for x, y in zip(a[i], a[j])]

    def row_scale(i, c):
        if c != 1:
            operations.append(('scale', i, c))
            a[i] = [c * x for x in a[i]]

    if not a[0][0]:
        row_add(0, 1, Q(1))
    need(bool(a[0][0]), 'two-row first pivot')
    row_scale(0, 1 / a[0][0])
    row_add(1, 0, -a[1][0])
    need(bool(a[1][1]), 'two-row second pivot')
    row_scale(1, 1 / a[1][1])
    row_add(0, 1, -a[0][1])
    need(a == ident(2), 'two-row elimination')
    events = []
    for operation in reversed(operations):
        if operation[0] == 'add':
            _, i, j, c = operation
            events.append(add(['L', PAIRED[i]], ['L', PAIRED[j]], -c, frame))
        else:
            _, i, c = operation
            events.append(scale(['L', PAIRED[i]], 1 / c, frame))
    need(scalar_matrix(events, PAIRED) == matrix, 'exact emitted two-row matrix')
    return events


def conjugate(event, a, ai):
    if event[0] != 'scalar' or not any(t == 'L' and r in PAIRED for t, r in refs(event)):
        return [deepcopy(event)]
    g, frame = event[1:]
    pair = [['L', r] for r in PAIRED]
    if g[0] == 'add':
        dst, src, c = g[1], g[2], Q(*g[3:5])
        if dst in pair and src in pair:
            elementary = ident(2)
            elementary[pair.index(dst)][pair.index(src)] += c
            return emit_two(mul(mul(a, elementary), ai), frame)
        if dst in pair:
            j = pair.index(dst)
            return [add(pair[i], src, c * a[i][j], frame) for i in range(2) if a[i][j]]
        j = pair.index(src)
        return [add(dst, pair[i], c * ai[j][i], frame) for i in range(2) if ai[j][i]]
    need(g[0] == 'scale', 'invertible conjugated helper scalar')
    elementary = ident(2)
    elementary[pair.index(g[1])][pair.index(g[1])] = Q(*g[2:4])
    return emit_two(mul(mul(a, elementary), ai), frame)


def check_conjugation(event, emitted, a, ai):
    """Check each changed scalar transfer on all its arbitrary input rows."""
    need(event[0] == 'scalar' and all(t == 'L' for t, r in refs(event)), 'paired helper has no owned scalar contact')
    roles = sorted(set(PAIRED) | {r for t, r in refs(event)})
    index = {r: i for i, r in enumerate(roles)}
    embedded, embedded_inverse = ident(len(roles)), ident(len(roles))
    for i, r in enumerate(PAIRED):
        for j, s in enumerate(PAIRED):
            embedded[index[r]][index[s]] = a[i][j]
            embedded_inverse[index[r]][index[s]] = ai[i][j]
    expected = mul(mul(embedded, scalar_matrix([event], roles)), embedded_inverse)
    need(scalar_matrix(emitted, roles) == expected, 'exact conjugated scalar transfer')


def rename(event):
    event = deepcopy(event)
    for ref in refs(event):
        if ref[0] == 'L' and ref[1] in (416, 417):
            ref[1] = 833 - ref[1]
    if event[0] == 'adapter' and event[2] in (416, 417):
        event[2] = 833 - event[2]
    return event


def dual(event):
    event = deepcopy(event)
    g = event[1]
    if g[0] == 'add':
        g[1], g[2], g[3] = g[2], g[1], -g[3]
    else:
        need(g[0] == 'scale', 'dual scalar kind')
        g[2], g[3] = g[3], g[2]
    return event


def make_suffix(payload, direction, cut=HI):
    t = [[Q(1, 2), Q(-1)], [Q(1, 2), Q(1)]]
    ti = inverse(t)
    a, ai = (t, ti) if direction == 'forward' else (list(map(list, zip(*ti))), list(map(list, zip(*t))))
    program = [e for e in payload['programs'][direction] if e[0] != 'climb']
    events, provenance = [], []
    for ordinal in range(cut, len(program)):
        emitted = conjugate(program[ordinal], a, ai)
        if program[ordinal][0] == 'scalar' and any(t == 'L' and r in PAIRED for t, r in refs(program[ordinal])):
            check_conjugation(program[ordinal], emitted, a, ai)
        emitted = [rename(e) for e in emitted]
        events.extend(emitted)
        provenance.extend([ordinal] * len(emitted))
    # Undo B=P*T at the common full endpoint: P, then T^-1.
    tail = [add(['L', 416], ['L', 417], 1, 1), add(['L', 417], ['L', 416], -1, 1),
            add(['L', 416], ['L', 417], 1, 1), scale(['L', 417], -1, 1)]
    tail += [add(['L', 417], ['L', 419], 1, 1), add(['L', 419], ['L', 417], Q(-1, 2), 1)]
    if direction == 'backward':
        tail = [dual(e) for e in tail]
    binding = ident(3)
    for i in range(2):
        for j in range(2):
            binding[i + 1][j + 1] = a[i][j]
    binding[0], binding[1] = binding[1], binding[0]
    need(mul(scalar_matrix(tail, (416, 417, 419)), binding) == ident(3), 'exact final B inverse')
    events.extend(tail)
    provenance.extend([None] * len(tail))
    return events, provenance


def live_add(event):
    return event[0] == 'scalar' and event[1][0] == 'add' and all(t == 'L' for t, r in refs(event))


def commute(add_event, other):
    if other[0] == 'phase':
        return False
    a, b = map(tuple, add_event[1][1:3])
    if other[0] == 'scalar' and other[1][0] == 'add':
        x, y = map(tuple, other[1][1:3])
        return a != y and b != x
    if other[0] in ('scalar', 'warp'):
        return not ({a, b} & set(map(tuple, refs(other))))
    need(other[0] in ('center', 'adapter'), 'known crossed marker')
    return True


def combine(events, provenance):
    """Credited PR4692 coalescer plus independent crossed-event checks."""
    out, origins, previous, writes, reads, barriers = [], [], {}, {}, {}, {}
    phase, merges, cancellations, crossed = -1, 0, 0, 0
    for event, origin in zip(events, provenance):
        index = len(out)
        if live_add(event):
            a, b = map(tuple, event[1][1:3])
            prior = previous.get((a, b), -1)
            barrier = max(phase, writes.get(b, -1), reads.get(a, -1), barriers.get(a, -1), barriers.get(b, -1))
            if prior > barrier:
                need(out[prior] is not None and out[prior][1][1:3] == event[1][1:3], 'merge endpoints')
                for intermediate in out[prior + 1:]:
                    if intermediate is not None:
                        need(commute(event, intermediate), 'noncommuting merge crossing')
                        crossed += 1
                value = Q(*out[prior][1][3:5]) + Q(*event[1][3:5])
                merges += 1
                if value:
                    out[prior] = add(a, b, value, out[prior][2])
                else:
                    out[prior] = None
                    previous.pop((a, b))
                    cancellations += 1
                continue
            previous[a, b] = index
        if event[0] == 'scalar' and event[1][0] == 'add':
            a, b = map(tuple, event[1][1:3])
            writes[a], reads[b] = index, index
        else:
            for ref in refs(event):
                barriers[tuple(ref)] = index
        if event[0] == 'phase':
            phase = index
        out.append(deepcopy(event))
        origins.append(origin)
    kept = [(e, o) for e, o in zip(out, origins) if e is not None]
    return [e for e, o in kept], [o for e, o in kept], {'merges': merges, 'cancellations': cancellations, 'crossed_checks': crossed}


def suffix_graph(payload, events, provenance):
    frames = list(map(span, payload['canonical']['frames']))
    nodes = [{'pin': None, 'kind': 'local_exit', 'role': r} for r in range(632)]
    current, outgoing, edges = list(range(632)), [[] for _ in nodes], []

    def node(pin, kind, role=None):
        index = len(nodes)
        nodes.append({'pin': pin, 'kind': kind, 'role': role})
        outgoing.append([])
        return index

    def move(role, target, ordinal):
        edge = {'a': current[role], 'b': target, 'role': role, 'suffix_ordinal': ordinal}
        outgoing[edge['a']].append(len(edges))
        edges.append(edge)
        current[role] = target

    dropped = 0
    for ordinal, event in enumerate(events):
        if event[0] == 'scalar':
            references = refs(event)
            owned = any(t != 'L' for t, r in references)
            target = node(event[2] if owned else None, 'owned_contact' if owned else 'scalar')
            for typ, role in references:
                if typ == 'L':
                    move(role, target, ordinal)
        elif event[0] == 'warp':
            role = event[1][1]
            move(role, node(None, 'native_input', role), ordinal)
            current[role] = node(None, 'native_output', role)
            dropped += 1
        else:
            need(event[0] in ('phase', 'center', 'adapter'), 'known suffix event')
    # All helper final charts are released. Only intrinsic main finals and
    # actual owned contacts constrain this optimistic suffix relaxation.
    for role, label in enumerate(payload['canonical']['final']):
        move(role, node(label if role < 224 else None, 'main_final' if role < 224 else 'free_helper_final', role), len(events))
    full = frozenset(range(512))
    upper = [frames[n['pin']] if n['pin'] is not None else full for n in nodes]
    distance = [0 if n['pin'] is not None and 73 not in frames[n['pin']] else float('inf') for n in nodes]
    for edge in reversed(edges):
        upper[edge['a']] &= upper[edge['b']]
        distance[edge['a']] = min(distance[edge['a']], 1 + distance[edge['b']])
    return {'nodes': nodes, 'edges': edges, 'outgoing': outgoing, 'upper': upper,
            'distance': distance, 'frames': frames, 'events': events, 'provenance': provenance,
            'omitted_native_occurrences': dropped}


def witness(graph, role):
    at, path = role, []
    while graph['nodes'][at]['pin'] is None or 73 in graph['frames'][graph['nodes'][at]['pin']]:
        options = [i for i in graph['outgoing'][at] if 73 not in graph['upper'][graph['edges'][i]['b']]]
        need(bool(options), 'excluded vector has a fixed suffix descendant')
        chosen = min(options, key=lambda i: graph['distance'][graph['edges'][i]['b']])
        path.append(chosen)
        at = graph['edges'][chosen]['b']
    result = {'local_exit_role': role, 'edge_ids': path, 'terminal_node': at}
    validate_witness(graph, result)
    return result


def validate_witness(graph, certificate):
    at = certificate['local_exit_role']
    need(at in TARGETS and certificate['edge_ids'], 'nonempty nominated suffix witness')
    for edge_id in certificate['edge_ids']:
        need(type(edge_id) is int and 0 <= edge_id < len(graph['edges']), 'suffix edge range')
        edge = graph['edges'][edge_id]
        need(edge['a'] == at, 'continuous suffix paid path')
        at = edge['b']
    need(at == certificate['terminal_node'], 'suffix terminal node')
    terminal = graph['nodes'][at]
    need(terminal['pin'] is not None and 73 not in graph['frames'][terminal['pin']], 'fixed suffix terminal excludes73')


def compact_witness(graph, certificate):
    terminal = graph['nodes'][certificate['terminal_node']]
    path = [graph['edges'][i] for i in certificate['edge_ids']]
    return {'length': len(path), 'roles': [e['role'] for e in path],
            'suffix_ordinals': [e['suffix_ordinal'] for e in path],
            'source_ordinals': [graph['provenance'][e['suffix_ordinal']] if e['suffix_ordinal'] < len(graph['events']) else None for e in path],
            'terminal_kind': terminal['kind'], 'terminal_role': terminal['role'],
            'terminal_frame': terminal['pin'], 'terminal_basis': basis(graph['frames'][terminal['pin']])}


def check_suffix(payload, direction):
    raw, origins = make_suffix(payload, direction)
    coalesced, coalesced_origins, counts = combine(raw, origins)
    graphs = {'uncoalesced': suffix_graph(payload, raw, origins),
              'coalesced': suffix_graph(payload, coalesced, coalesced_origins)}
    result = {'coalescing': counts, 'variants': {}}
    for name, graph in graphs.items():
        caps = {}
        for role in TARGETS:
            need(graph['upper'][role] == span(EXPECTED_CAPS[role]), 'exact greatest suffix cap')
            need(73 not in graph['upper'][role], 'suffix cap excludes73')
            certificate = witness(graph, role)
            caps[str(role)] = {'basis': basis(graph['upper'][role]),
                               'witness': compact_witness(graph, certificate)}
        result['variants'][name] = {'scalar_event_count': sum(e[0] == 'scalar' for e in graph['events']),
                                    'suffix_event_count': len(graph['events']),
                                    'suffix_sha256': digest(graph['events']),
                                    'paid_incidences': len(graph['edges']),
                                    'omitted_native_occurrences': graph['omitted_native_occurrences'],
                                    'caps': caps}
    return result, graphs


def verify(payload=None):
    payload = read_source() if payload is None else payload
    need(digest(payload) == SOURCE_SHA256, 'pinned combined source payload')
    need(payload['canonical']['h'] == 9 and len(payload['canonical']['start']) == 632, 'source dimensions')
    local = local_model(payload)
    natives = native_binding(payload)
    directions = {direction: check_suffix(payload, direction)[0] for direction in ('forward', 'backward')}
    return {'status': 'PASS_SCOPED_INVERSE_SUPPORT_OBSTRUCTION', 'source_sha256': SOURCE_SHA256,
            'source_interval': [LO, HI], 'local_roles': local['roles'],
            'source_local_matrix_sha256': local['matrix_hash'], 'quotient_matrix_sha256': local['quotient_hash'],
            'cold_roles': local['cold'], 'alpha': {str(r): str(c) for r, c in local['alpha'].items() if c},
            'annihilator': {'identity': 'alpha = -D^-1[:,78] + (1/2)D^-1[:,431] on cold coordinates',
                            'columns': [78, 431], 'coefficients': ['-1', '1/2']},
            'native_source_bindings': natives, 'directions': directions,
            'relaxations': ['all suffix native edges removed', 'all helper final pins removed', 'intermediate adapter pins omitted'],
            'scope': 'No invertible cold-helper basis Q with all beta=Q*alpha compensation performed as a prefix can be followed by a pure-scalar realization of DQ^-1 and either declared retained suffix whose paid canonical chart spaces only grow by inclusion. Distributed prefix compensation is included. Interleaved compensation, changed suffix contacts, nonmonotone paid transports and new multiplication bounds are not claimed.'}


def controls(payload=None):
    payload = read_source() if payload is None else payload
    local = local_model(payload)
    _, graphs = check_suffix(payload, 'forward')
    graph = graphs['coalesced']
    certificate = witness(graph, 78)
    passed = []

    def rejected(name, operation):
        try:
            operation()
        except ValueError:
            passed.append(name)
        else:
            raise ValueError('corruption control accepted: ' + name)

    bad = deepcopy(payload)
    bad['canonical']['start'][0] = 0
    rejected('source_payload_changed', lambda: verify(bad))
    bad = deepcopy(payload)
    program = [e for e in bad['programs']['forward'] if e[0] != 'climb']
    program[LO][1][3] *= -1
    rejected('source_local_coefficient_changed', lambda: local_model(bad))
    rejected('annihilator_sign_changed', lambda: annihilator(local['alpha'], local['D_inverse'], local['index'], local['cold'], ((78, Q(1)), (431, Q(1, 2)))))
    bad_alpha = dict(local['alpha'])
    bad_alpha[418] += 1
    rejected('compensation_coefficient_changed', lambda: annihilator(bad_alpha, local['D_inverse'], local['index'], local['cold']))
    bad = deepcopy(payload)
    next(w for w in bad['canonical']['warps'] if w['op'] == 35)['G_columns'][0] ^= 2
    rejected('paired_native_map_changed', lambda: native_binding(bad))
    bad_certificate = deepcopy(certificate)
    bad_certificate['edge_ids'] = bad_certificate['edge_ids'][1:]
    rejected('suffix_path_edge_deleted', lambda: validate_witness(graph, bad_certificate))
    bad_graph = dict(graph)
    bad_graph['nodes'] = deepcopy(graph['nodes'])
    bad_graph['nodes'][certificate['terminal_node']]['pin'] = None
    rejected('suffix_terminal_pin_removed', lambda: validate_witness(bad_graph, certificate))
    bad_graph = dict(graph)
    bad_graph['frames'] = list(graph['frames'])
    pin = graph['nodes'][certificate['terminal_node']]['pin']
    bad_graph['frames'][pin] = frozenset(range(512))
    rejected('suffix_terminal_contains73', lambda: validate_witness(bad_graph, certificate))
    return {'passed': passed, 'count': len(passed)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--write', action='store_true', help='explicitly write CHECK-RESULT.json beside this checker')
    args = parser.parse_args()
    data = read_source(args.source)
    result = verify(data)
    result['controls'] = controls(data)
    if args.write:
        (HERE / 'CHECK-RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2, sort_keys=True))
