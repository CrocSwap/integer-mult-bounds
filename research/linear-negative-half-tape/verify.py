#!/usr/bin/env python3
"""Literal-row finite corroboration of the marked negative-half contract.

The credited PR6801 positive transition rows are executed as components.
The original PR6092 unary program and all predecessor verifier code are not run.
The universal theorem and resource premises are in PROOF.md, not inferred here.
"""
import hashlib
import json
from pathlib import Path
import sys

P = Path(__file__).resolve().parent
ALPHABET = frozenset(('0', '1', 'P0', 'P1', 'S0', 'S1'))
COLUMNS = ['state', 'read', 'coin', 'next_state', 'write', 'move']
PINNED = {
    'vendor/PR6092-PROOF.md': (7828, '64c9b4b9f58639133f087d77f154b91026a18738bfb0830b93e96d5a30df9932'),
    'vendor/PR6801-PROOF.md': (9149, '63eb48517f39cd0e66b23705939d74d2455a0c6b91f4da333ef768330b14e793'),
    'vendor/PR6801-README.md': (5889, '1db9b4272df0d9a3cbc0e8a0f5cf416f490fef40adefe7bb2a4db6398cdfed3e'),
    'vendor/PR6801-TABLE.json': (2495, '6246c7674743cfa1c08e49cd3d089d0eccfe9b04b9e0bec72a5e7183e39cb849'),
}


class Failure(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Failure(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON object key')
        result[key] = value
    return result


def no_number(value):
    raise Failure('noninteger or nonfinite JSON number: ' + value)


def load_json(raw):
    return json.loads(raw, object_pairs_hook=unique_object,
                      parse_float=no_number, parse_constant=no_number)


def authenticate_sources():
    manifest = load_json((P / 'SOURCE-PINS.json').read_bytes())
    require(type(manifest.get('schema_version')) is int and manifest['schema_version'] == 1,
            'source manifest schema')
    entries = manifest.get('files')
    require(type(entries) is list and len(entries) == 4, 'four source pins required')
    require({e.get('local_path') for e in entries} == set(PINNED), 'source pin paths')
    raw_sources = {}
    for entry in entries:
        name = entry['local_path']
        raw = (P / name).read_bytes()
        size, sha = PINNED[name]
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require((len(raw), hashlib.sha256(raw).hexdigest()) == (size, sha), 'source bytes: ' + name)
        require(entry['bytes'] == size and entry['sha256'] == sha, 'source manifest hash')
        require(entry['git_blob'] == blob and entry['mode'] == '100644', 'source blob/mode')
        raw_sources[name] = raw
    return load_json(raw_sources['vendor/PR6801-TABLE.json'])


def row_schema(rows):
    require(type(rows) is list, 'table rows must be a list')
    seen = set()
    for row in rows:
        require(type(row) is list and len(row) == 6, 'six fields per row')
        state, read, coin, target, write, move = row
        require(type(state) is str and type(target) is str, 'state names')
        require(read in ALPHABET and write in ALPHABET, 'work alphabet')
        require(type(coin) is int and coin in (0, 1), 'coin bit')
        require(type(move) is int and move in (-1, 0, 1), 'unit head movement')
        key = (state, read, coin)
        require(key not in seen, 'nondeterministic source triple')
        seen.add(key)


def local_reversibility(rows):
    row_schema(rows)
    directions, predecessors = {}, set()
    for state, read, coin, target, write, move in rows:
        require(target not in directions or directions[target] == move,
                'incoming_direction: ' + target)
        directions[target] = move
        image = (target, write, coin)
        require(image not in predecessors, 'incoming_collision: ' + target)
        predecessors.add(image)
    return {'rows': len(rows), 'target_states': len(directions),
            'unique_target_write_coin': len(predecessors)}


def negator_rows(prefix, halt):
    # Each tuple is one new structural rule; coin expansion does not alter u.
    rules = {
        'N0': [('P0', 'NZ', 'P0', 1), ('P1', 'NZ', 'P1', 1)],
        'NZ': [('0', 'NZ', '0', 1), ('1', 'NC', 'P1', 1),
               ('S0', 'NB', 'S0', -1), ('S1', 'NB', 'S1', -1)],
        'NC': [('0', 'NC', '1', 1), ('1', 'NC', '0', 1),
               ('S0', 'NR', 'S1', -1), ('S1', 'NR', 'S0', -1)],
        'NR': [('0', 'NR', '0', -1), ('1', 'NR', '1', -1), ('P1', 'NB', '1', -1)],
        'NB': [('0', 'NB', '0', -1), ('P0', 'H', 'P0', 0), ('P1', 'H', 'P1', 0)],
    }
    return [[prefix + state, read, coin, halt if target == 'H' else prefix + target, write, move]
            for state, transitions in rules.items()
            for read, target, write, move in transitions for coin in (0, 1)]


def positive_rows(source, lead, prefix, halt, flip=True):
    return [[prefix + s, a, 1 - u if flip else u,
             halt if t == 'H' else prefix + t, b, d]
            for s, a, u, t, b, d in source if s.startswith(lead)]


def bound_table(source):
    require(source['schema_version'] == 1 and source['columns'] == COLUMNS, 'source table schema')
    require(len(source['rows']) == 66, 'source table row count')
    row_schema(source['rows'])
    table = load_json((P / 'TABLE.json').read_bytes())
    require(set(table) == {'schema_version', 'columns', 'forward_start', 'inverse_start',
                          'forward_halt', 'inverse_halt', 'rows'}, 'candidate table keys')
    require(type(table['schema_version']) is int and table['schema_version'] == 1, 'table version')
    require(table['columns'] == COLUMNS, 'table columns')
    for key, value in [('forward_start', 'PF_F0'), ('inverse_start', 'NI_N0'),
                       ('forward_halt', 'HF'), ('inverse_halt', 'HI')]:
        require(table[key] == value, 'fixed entry/return states')
    expected = positive_rows(source['rows'], 'F', 'PF_', 'NF_N0') + negator_rows('NF_', 'HF')
    expected += negator_rows('NI_', 'PI_I0') + positive_rows(source['rows'], 'I', 'PI_', 'HI')
    require(sorted(table['rows']) == sorted(expected), 'literal component/negator binding')
    require(len(table['rows']) == 130, 'candidate row count')
    rows = table['rows']
    forward = [r for r in rows if r[0].startswith(('PF_', 'NF_'))]
    inverse = [r for r in rows if r[0].startswith(('NI_', 'PI_'))]
    require(len(forward) == len(inverse) == 65, 'directional row count')
    return table, forward, inverse


def machine(rows):
    row_schema(rows)
    return {(s, a, u): (t, b, d) for s, a, u, t, b, d in rows}


def encoding(width, value, parity):
    raw = value % (1 << width)
    return ['P' + str(parity)] + [str((raw >> j) & 1) for j in range(width - 1)] + ['S' + str(raw >> (width - 1))]


def signed_value(word):
    if (word[0] not in ('P0', 'P1') or word[-1] not in ('S0', 'S1')
            or any(s not in ('0', '1') for s in word[1:-1])):
        return None
    bits = [int(s) for s in word[1:-1]] + [int(word[-1][1])]
    value = sum(bit << j for j, bit in enumerate(bits))
    return value - (bits[-1] << len(bits))


def run(code, start, halt, width, value, parity, coin, anchor=0, extra=0,
        exterior=('S1', '0', 'P1', '1')):
    require(type(width) is int and 2 <= width <= 4096, 'instrumentation width cap')
    cells = list(exterior[:2]) + encoding(width, value, parity) + list(exterior[2:])
    before = cells[:]
    head, state, steps, positive = anchor, start, 0, 0
    visited = {head}
    limit = 6 * width + 2 + extra
    while state != halt:
        require(steps < limit, 'instrumentation transition cap')
        index = head - anchor + 2
        require(0 <= index < len(cells), 'instrumentation buffer cap')
        row = code.get((state, cells[index], coin))
        if row is None:
            return dict(accepted=False, state=state, symbol=cells[index], steps=steps,
                        positive_steps=positive, coin=coin, head=head - anchor)
        target, write, move = row
        positive += int(state.startswith(('PF_', 'PI_', 'MP_')))
        cells[index] = write
        head += move
        state, steps = target, steps + 1
        visited.add(head)
    return dict(accepted=True, state=state, steps=steps, positive_steps=positive,
                coin=coin, head=head - anchor, word=cells[2:-2],
                exterior_ok=(cells[:2] == before[:2] and cells[-2:] == before[-2:]),
                visited_min=min(visited) - anchor, visited_max=max(visited) - anchor,
                visited_count=len(visited))


def negative_half(value, coin):
    return divmod(-value, 2)[0] + (divmod(-value, 2)[1] if coin == 0 else 0)


def expected_time(width, value, coin):
    q, p = divmod(value, 2)
    if not p * coin:
        return 4 * width + 2
    bits = q % (1 << width)
    k = 0
    while k < width - 1 and ((bits >> k) & 1):
        k += 1
    return 4 * width + 2 * k + 4


def violation(result, width, value, parity, steps):
    if not result['accepted']:
        return 'undefined_transition'
    if result['head'] != 0:
        return 'head_return'
    if signed_value(result['word']) is None:
        return 'canonical_payload'
    if result['word'] != encoding(width, value, parity):
        return 'endpoint'
    if not result['exterior_ok'] or (result['visited_min'], result['visited_max'],
                                    result['visited_count']) != (0, width, width + 1):
        return 'frame_extent'
    if result['steps'] != steps:
        return 'exact_time'
    return None


def success(result, width, value, parity, steps):
    fault = violation(result, width, value, parity, steps)
    require(fault is None, 'healthy execution failed: ' + str(fault))


def stats_new():
    return dict(calls=0, accepted=0, rejected=0, transitions=0, source_positive_transitions=0)


def account(stats, result):
    stats['calls'] += 1
    stats['accepted' if result['accepted'] else 'rejected'] += 1
    stats['transitions'] += result['steps']
    stats['source_positive_transitions'] += result['positive_steps']


def exhaustive_forward(forward, inverse):
    stats = stats_new()
    maxima = []
    for width in range(2, 13):
        observed = 0
        for x in range(-(1 << (width - 1)), 1 << (width - 1)):
            for coin in (0, 1):
                y, parity = negative_half(x, coin), x % 2
                time = expected_time(width, x, coin)
                first = run(forward, 'PF_F0', 'HF', width, x, 0, coin)
                success(first, width, y, parity, time)
                second = run(inverse, 'NI_N0', 'HI', width, y, parity, coin)
                success(second, width, x, 0, time)
                account(stats, first)
                account(stats, second)
                observed = max(observed, first['steps'], second['steps'])
        require(observed == 6 * width + 2, 'sharp maximum witness')
        maxima.append([width, observed, -1, 1])
    return dict(widths=[2, 12], forward_inputs=stats['calls'] // 2,
                inverse_of_forward_inputs=stats['calls'] // 2, stats=stats, maxima=maxima)


def exhaustive_negator():
    rows = negator_rows('N_', 'NH')
    local = local_reversibility(rows)
    code, stats = machine(rows), stats_new()
    for width in range(2, 13):
        modulus = 1 << width
        for x in range(-(modulus // 2), modulus // 2):
            z = (-x) % modulus
            z -= modulus if z >= modulus // 2 else 0
            for parity in (0, 1):
                for coin in (0, 1):
                    first = run(code, 'N_N0', 'NH', width, x, parity, coin)
                    success(first, width, z, parity, 2 * width + 1)
                    second = run(code, 'N_N0', 'NH', width, z, parity, coin)
                    success(second, width, x, parity, 2 * width + 1)
                    account(stats, first)
                    account(stats, second)
    return dict(widths=[2, 12], inputs=stats['calls'] // 2,
                modular_minimum_included=True, involution_inputs=stats['calls'] // 2,
                local_reversibility=local, stats=stats)


def inverse_boundary(forward, inverse):
    stats, valid, invalid = stats_new(), 0, 0
    for width in range(2, 9):
        lower, upper = -(1 << (width - 1)), 1 << (width - 1)
        for y in range(lower, upper):
            for parity in (0, 1):
                for coin in (0, 1):
                    x = -2 * y + parity * (1 - 2 * coin)
                    result = run(inverse, 'NI_N0', 'HI', width, y, parity, coin)
                    account(stats, result)
                    if lower <= x < upper:
                        success(result, width, x, 0, expected_time(width, x, coin))
                        back = run(forward, 'PF_F0', 'HF', width, x, 0, coin)
                        success(back, width, y, parity, expected_time(width, x, coin))
                        account(stats, back)
                        valid += 1
                    else:
                        require(not result['accepted'], 'inverse nonimage accepted')
                        invalid += 1
    return dict(widths=[2, 8], boundary_inputs=valid + invalid, valid=valid,
                rejected_nonimage=invalid, forward_of_inverse_inputs=valid, stats=stats)


def boundaries(forward, inverse):
    stats, cases = stats_new(), []
    for width in (2, 3, 8, 31, 64, 127, 1024, 4096):
        lower, upper = -(1 << (width - 1)), (1 << (width - 1)) - 1
        for x in sorted(set((lower, lower + 1, -1, 0, 1, upper - 1, upper))):
            for coin in (0, 1):
                for anchor in (-17, 29):
                    y, parity, time = negative_half(x, coin), x % 2, expected_time(width, x, coin)
                    first = run(forward, 'PF_F0', 'HF', width, x, 0, coin, anchor)
                    success(first, width, y, parity, time)
                    second = run(inverse, 'NI_N0', 'HI', width, y, parity, coin, anchor)
                    success(second, width, x, 0, time)
                    account(stats, first)
                    account(stats, second)
                    cases.append([width, 'minimum' if x == lower else 'boundary', coin, anchor])
    return dict(widths=[2, 3, 8, 31, 64, 127, 1024, 4096], translated_calls=stats['calls'],
                tested_exterior_pattern=['S1', '0', 'P1', '1'], stats=stats)


def semantic_control(name, rows, start, halt, width, x, parity, coin,
                     expected_value, expected_parity, expected_steps, reason, extra=0):
    result = run(machine(rows), start, halt, width, x, parity, coin, extra=extra)
    actual = violation(result, width, expected_value, expected_parity, expected_steps)
    require(actual == reason, 'control wrong failure: ' + name + ': ' + str(actual))
    witness = dict(width=width, input=x, parity=parity, coin=coin, expected=expected_value,
                   observed=signed_value(result['word']) if result['accepted'] else None,
                   accepted=result['accepted'], steps=result['steps'], reason=actual)
    if result['accepted']:
        witness.update(word=result['word'], head=result['head'], exterior_ok=result['exterior_ok'],
                       visited=[result['visited_min'], result['visited_max']])
    return dict(name=name, status='REJECTED_FOR_INTENDED_REASON', witness=witness,
                source_positive_transitions=result['positive_steps'])


def structural_control(name, rows, reason):
    try:
        local_reversibility(rows)
    except Failure as error:
        require(str(error).startswith(reason), 'structural control wrong reason')
        return dict(name=name, status='REJECTED_FOR_INTENDED_REASON', witness=str(error),
                    source_positive_transitions=0)
    raise Failure('structural mutation accepted: ' + name)


def controls(source, frows, irows):
    output = []
    wrong_coin = [[s, a, 1-u if s.startswith('PF_') else u, t, b, d]
                  for s, a, u, t, b, d in frows]
    output.append(semantic_control('same_coin_instead_of_complement', wrong_coin, 'PF_F0', 'HF',
                                  3, 1, 0, 0, 0, 1, expected_time(3, 1, 0), 'endpoint'))
    naive = negator_rows('TN_', 'MP_F0') + positive_rows(source, 'F', 'MP_', 'MH', False)
    output.append(semantic_control('negate_input_before_half_overflows_minimum', naive, 'TN_N0', 'MH',
                                  3, -4, 0, 0, 2, 0, expected_time(3, -4, 0), 'endpoint'))
    omit = [[s, a, u, 'HF' if t == 'NF_N0' else t, b, d] for s, a, u, t, b, d in frows]
    output.append(semantic_control('omit_post_half_negator', omit, 'PF_F0', 'HF',
                                  3, 2, 0, 0, -1, 0, expected_time(3, 2, 0), 'endpoint'))
    tag = [[s, a, u, t, 'P1' if s == 'NF_NR' and a == 'P1' else b, d]
           for s, a, u, t, b, d in frows]
    output.append(semantic_control('leave_internal_first_one_tag', tag, 'PF_F0', 'HF',
                                  3, 2, 0, 0, -1, 0, expected_time(3, 2, 0), 'canonical_payload'))
    direction = [[s, a, u, t, b, 0 if s == 'NF_NZ' and a == '0' and u == 0 else d]
                 for s, a, u, t, b, d in frows]
    output.append(structural_control('mixed_incoming_directions', direction, 'incoming_direction:'))
    collision = frows + [['NF_N0', '0', 0, 'NF_NZ', 'P0', 1]]
    output.append(structural_control('duplicate_local_predecessor', collision, 'incoming_collision:'))
    return output


def inverse_and_frame_controls(irows, frows):
    bad = irows + [['PI_IU0', 'S1', u, 'PI_IB', 'S1', -1] for u in (0, 1)]
    result = run(machine(bad), 'NI_N0', 'HI', 2, -2, 0, 0)
    require(result['accepted'], 'bad inverse sign mutation did not accept witness')
    outside = dict(name='remove_inverse_sign_extension_guard', status='REJECTED_FOR_INTENDED_REASON',
                   witness=dict(width=2, input=-2, parity=0, coin=0, inferred_x=4,
                                permitted_x=[-2, 1], accepted=True, reason='inverse_nonimage',
                                observed=signed_value(result['word'])),
                   source_positive_transitions=result['positive_steps'])
    excursion = [[s, a, u, 'EX' if t == 'HF' else t, b, d] for s, a, u, t, b, d in frows]
    for u in (0, 1):
        for p in ('P0', 'P1'):
            excursion += [['EX', p, u, 'XL', p, -1], ['XR', p, u, 'HX', p, 0]]
        excursion += [['XL', '0', u, 'XR', '1', 1]]
    local_reversibility(excursion)
    frame = semantic_control('payload_preserving_exterior_excursion', excursion, 'PF_F0', 'HX',
                             3, 0, 0, 0, 0, 0, expected_time(3, 0, 0) + 3,
                             'frame_extent', extra=3)
    require(frame['witness']['observed'] == 0 and not frame['witness']['exterior_ok'],
            'exterior-only mutation did not preserve payload/change exterior')
    return [outside, frame]


def package_hashes():
    result = {}
    for path in sorted(P.rglob('*')):
        require(not path.is_symlink(), 'package symlink not supported')
        if path.is_file():
            result[path.relative_to(P).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main():
    require(len(sys.argv) == 1, 'no command line arguments supported')
    source = authenticate_sources()  # No semantic use precedes exact four-input authentication.
    table, frows, irows = bound_table(source)
    forward_local, inverse_local = local_reversibility(frows), local_reversibility(irows)
    forward, inverse = machine(frows), machine(irows)
    forward_checks = exhaustive_forward(forward, inverse)
    negator_checks = exhaustive_negator()
    inverse_checks = inverse_boundary(forward, inverse)
    large_checks = boundaries(forward, inverse)
    faults = controls(source['rows'], frows, irows) + inverse_and_frame_controls(irows, frows)
    healthy = [forward_checks['stats'], negator_checks['stats'], inverse_checks['stats'], large_checks['stats']]
    positive_steps = sum(item['source_positive_transitions'] for item in healthy)
    control_steps = sum(item['source_positive_transitions'] for item in faults)
    packet = dict(schema_version=1, status='PASS_LINEAR_NEGATIVE_HALF_TAPE', scope='finite literal negative-half tape corroboration',
                  rows=130, directional_rows=[65, 65], new_structural_negator_rules=16,
                  alphabet=sorted(ALPHABET), local_reversibility=[forward_local, inverse_local],
                  forward=forward_checks, modular_negator=negator_checks,
                  inverse_boundary=inverse_checks, translated_large_boundaries=large_checks,
                  controls=faults, control_count=len(faults),
                  credited_positive_transition_execution=dict(healthy_source_derived=positive_steps,
                      control_positive_phase=control_steps, total_positive_phase=positive_steps + control_steps,
                      healthy_scope='Actual source-derived rows bound to PR6801 after prefix/read-coin substitution.',
                      control_scope='State-prefix phase count includes mutant-added/modified rows; not exact original-row membership.'),
                  predecessor_verifier_imports=0, predecessor_PR6092_unary_transitions=0,
                  package_sha256=package_hashes())
    print(json.dumps(packet, sort_keys=True, separators=(',', ':'),
                     ensure_ascii=True, allow_nan=False))


if __name__ == '__main__':
    try:
        main()
    except (Failure, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        print('FAIL_LINEAR_NEGATIVE_HALF_TAPE: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
