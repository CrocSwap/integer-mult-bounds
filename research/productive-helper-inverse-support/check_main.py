#!/usr/bin/env python3
"""One main-input support obstruction for the globally conjugated suffix.

Apache-2.0. Substantial OpenAI Codex assistance. This strengthens the
prefix-only obstruction for the SAME retained B=P*T suffix. It does not
apply to a different suffix which undoes T immediately after the natives.
"""
from collections import deque
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROLE, VECTOR, EXPECTED = 51, 100, Q(1, 2)


@lru_cache(None)
def peer(name):
    spec = importlib.util.spec_from_file_location('productive_main_' + name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def need(condition, message):
    if not condition:
        raise ValueError(message)


def source_column(payload):
    whole = peer('check_whole')
    program = [e for e in payload['programs']['forward'] if e[0] != 'climb']
    column = [Q(0)] * whole.N
    column[ROLE] = 1
    result = whole.apply_vector(column, program[whole.LO:whole.HI])
    need(result[ROLE] == EXPECTED, 'required main51 coefficient is one half')
    frames = whole.entry_frames(payload, program)
    need(payload['canonical']['frames'][frames[ROLE]] == [VECTOR], 'main51 actual entry line100')
    need(ROLE not in (416, 417, 419), 'B fixes nominated output role')
    return program, frames, result[ROLE]


def forward_inverse_violations(matrix, inverse_matrix, entrance_spaces, graph):
    """Every nonzero scalar dependency is checked, not just main51."""
    forward, backward = [], []
    for output, row in enumerate(matrix):
        for input_role, coefficient in row.items():
            if coefficient and not entrance_spaces[input_role] <= graph['upper'][output]:
                forward.append([input_role, output, str(coefficient)])
    for input_role, row in enumerate(inverse_matrix):
        for output, coefficient in row.items():
            if coefficient and not entrance_spaces[input_role] <= graph['upper'][output]:
                backward.append([input_role, output, str(coefficient)])
    return forward, backward


def path_to_excluding_pin(graph, role=ROLE, vector=VECTOR):
    """Ordinary BFS on paid edges; no73-specific core witness is used."""
    queue = deque([role])
    previous = {role: None}
    terminal = None
    while queue:
        node = queue.popleft()
        pin = graph['nodes'][node]['pin']
        if pin is not None and vector not in graph['frames'][pin]:
            terminal = node
            break
        for edge_id in graph['outgoing'][node]:
            edge = graph['edges'][edge_id]
            if edge['b'] not in previous:
                previous[edge['b']] = edge_id
                queue.append(edge['b'])
    need(terminal is not None, 'main support has an excluding fixed descendant')
    at, path = terminal, []
    while at != role:
        edge_id = previous[at]
        need(edge_id is not None, 'nonempty main witness predecessor')
        path.append(edge_id)
        at = graph['edges'][edge_id]['a']
    certificate = {'role': role, 'vector': vector, 'edges': list(reversed(path)), 'terminal': terminal}
    validate_path(graph, certificate)
    return certificate


def validate_path(graph, certificate):
    at = certificate['role']
    need(at == ROLE and certificate['vector'] == VECTOR and certificate['edges'], 'nominated main witness')
    for edge_id in certificate['edges']:
        need(type(edge_id) is int and 0 <= edge_id < len(graph['edges']), 'main witness edge range')
        edge = graph['edges'][edge_id]
        need(edge['a'] == at, 'continuous main paid path')
        at = edge['b']
    need(at == certificate['terminal'], 'main witness terminal identity')
    pin = graph['nodes'][at]['pin']
    need(pin is not None and VECTOR not in graph['frames'][pin], 'main terminal excludes100')


def compact(graph, certificate):
    core = peer('check')
    terminal = graph['nodes'][certificate['terminal']]
    path = [graph['edges'][i] for i in certificate['edges']]
    return {'length': len(path), 'roles': [e['role'] for e in path],
            'suffix_ordinals': [e['suffix_ordinal'] for e in path],
            'source_ordinals': [graph['provenance'][e['suffix_ordinal']] if e['suffix_ordinal'] < len(graph['events']) else None for e in path],
            'terminal_kind': terminal['kind'], 'terminal_role': terminal['role'],
            'terminal_frame': terminal['pin'], 'terminal_basis': core.basis(graph['frames'][terminal['pin']])}


def verify(payload=None):
    core, whole = peer('check'), peer('check_whole')
    payload = core.read_source() if payload is None else payload
    need(core.digest(payload) == core.SOURCE_SHA256, 'pinned main-support source')
    program, entries, coefficient = source_column(payload)
    matrix = whole.sparse_matrix(program[whole.LO:whole.HI])
    inverse_matrix = whole.sparse_matrix(program[whole.LO:whole.HI], True)
    whole.identity_product(matrix, inverse_matrix)
    whole.identity_product(inverse_matrix, matrix)
    need(matrix[ROLE][ROLE] == coefficient, 'independent column/full-row coefficient agreement')
    entrance_spaces = [core.span(payload['canonical']['frames'][label]) for label in entries]

    original = program[whole.HI:]
    original_origins = list(range(whole.HI, len(program)))
    original_graph = core.suffix_graph(payload, original, original_origins)
    fwd, inv = forward_inverse_violations(matrix, inverse_matrix, entrance_spaces, original_graph)
    need(not fwd and not inv, 'original encoder/original suffix positive control')
    result = {'status': 'PASS_MAIN_SUPPORT_RETAINED_SUFFIX_OBSTRUCTION',
              'source_sha256': core.SOURCE_SHA256, 'encoder_interval': [whole.LO, whole.HI],
              'required_coefficient': {'input_role': ROLE, 'output_role': ROLE, 'value': str(coefficient), 'input_basis': [VECTOR]},
              'B_fixes_output51': True,
              'positive_control': {'original_forward_support_checks': sum(map(len, matrix)),
                                   'original_inverse_support_checks': sum(map(len, inverse_matrix)),
                                   'forward_violations': len(fwd), 'inverse_violations': len(inv),
                                   'original_output51_cap': core.basis(original_graph['upper'][ROLE])},
              'directions': {}}
    for direction in ('forward', 'backward'):
        raw, origins = core.make_suffix(payload, direction, cut=whole.HI)
        combined, combined_origins, counts = core.combine(raw, origins)
        variants = {}
        for name, events, provenance in (('uncoalesced', raw, origins), ('coalesced', combined, combined_origins)):
            graph = core.suffix_graph(payload, events, provenance)
            need(graph['upper'][ROLE] == core.span([45, 76]) and VECTOR not in graph['upper'][ROLE],
                 'retained output51 greatest cap excludes100')
            certificate = path_to_excluding_pin(graph)
            variants[name] = {'suffix_sha256': core.digest(events),
                              'output51_cap': core.basis(graph['upper'][ROLE]),
                              'witness100': compact(graph, certificate)}
        result['directions'][direction] = {'coalescing': counts, 'variants': variants}
    result['scope'] = ('With the actual scalar-A input charts, the required transfer H=P*T*M has a nonzero main51-to-main51 coefficient. '
                       'No pure-scalar realization whose paid canonical chart spaces grow by inclusion can feed either declared globally '
                       'B-conjugated suffix. This is independent of cold prefix choices and compensation interleaving. All suffix native '
                       'edges/helper-final/adapter pins are released. It does not cover a changed suffix, including transient T undone '
                       'immediately after the paired natives, or nonmonotone paid transports. No new bound is claimed.')
    return result


def controls(payload=None):
    core, whole = peer('check'), peer('check_whole')
    payload = core.read_source() if payload is None else payload
    raw, origins = core.make_suffix(payload, 'forward', cut=whole.HI)
    events, provenance, _ = core.combine(raw, origins)
    graph = core.suffix_graph(payload, events, provenance)
    certificate = path_to_excluding_pin(graph)
    passed = []

    def rejected(name, operation):
        try:
            operation()
        except ValueError:
            passed.append(name)
        else:
            raise ValueError('main corruption control accepted: ' + name)

    bad = deepcopy(payload)
    pure = [e for e in bad['programs']['forward'] if e[0] != 'climb']
    need(pure[9994] == ['scalar', ['add', ['L', 51], ['L', 13], -1, 2], 581], 'source main51 instruction')
    pure[9994][1][3] *= -1
    rejected('required_main_coefficient_changed', lambda: source_column(bad))
    bad_path = deepcopy(certificate)
    bad_path['edges'] = bad_path['edges'][1:]
    rejected('main_witness_edge_omitted', lambda: validate_path(graph, bad_path))
    bad_graph = dict(graph)
    bad_graph['frames'] = list(graph['frames'])
    pin = graph['nodes'][certificate['terminal']]['pin']
    bad_graph['frames'][pin] = frozenset(range(512))
    rejected('main_terminal_admits100', lambda: validate_path(bad_graph, certificate))
    return {'count': len(passed), 'passed': passed}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = verify()
    result['controls'] = controls()
    if args.write:
        (HERE / 'MAIN-CHECK-RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2, sort_keys=True))
