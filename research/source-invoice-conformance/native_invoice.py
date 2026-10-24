#!/usr/bin/env python3
"""Independently extract an invoice from the literal retained native-word schema.

No author evaluator, price module, declared paid profile, relation witness or
receipt is executed. Exact sparse rows establish symbolic endpoint and zero-row
conformance; binary subspaces establish the charged ranks and uncharged native
frame transports. Absolute phases, physical precision and supplier admission
remain separate obligations.

The schema and free-word convention come from Cao Yifan's PR4610 word and the
retained Cinna Davis/zxv native lineage. Ali Romman supplied PR5383's changed
word; Dugongue supplied PR5387's successor. Independently implemented with
substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json


Q = Fraction
SCHEMA = 'native-word-source-invoice/v1'
PHASES = ['zero_frame_precondition', 'entry_adapters', 'A', 'centers', 'B',
          'cleanup_tail', 'final', 'exit_adapters', 'full_frame_cleanup', 'done']
MAX_ROW_TERMS = 4096
MAX_WORD_LENGTH = 4096
MAX_COEFFICIENT_BITS = 4096


def _need(ok, why):
    if not ok:
        raise ValueError(why)


def _integer(value, why):
    _need(type(value) is int, why)
    return value


def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                             ensure_ascii=True).encode()).hexdigest()


def _role(value, fields):
    _need(type(value) in (list, tuple) and len(value) == 2, 'role must be [L|C,index]')
    kind, index = value
    _integer(index, 'role index must be an integer')
    _need(kind in ('L', 'C') and 0 <= index <= 1000000, 'unsupported role')
    _need(kind != 'L' or index < fields, 'persistent role outside declared inputs')
    return kind, index


def _span(basis, h):
    _need(type(basis) is list and len(basis) <= h, 'binary frame basis')
    result = {0}
    for vector in basis:
        _integer(vector, 'binary frame coordinate must be an integer')
        _need(0 <= vector < 1 << h and vector not in result, 'dependent or invalid binary frame basis')
        result |= {value ^ vector for value in tuple(result)}
    return frozenset(result)


def _binary_image(value, columns):
    result = 0
    for index, column in enumerate(columns):
        if value >> index & 1:
            result ^= column
    return result


def _add(destination, source, coefficient):
    for key, value in source.items():
        value = destination.get(key, Q(0)) + coefficient * value
        if value:
            destination[key] = value
        else:
            destination.pop(key, None)


def _guard_row(row):
    """Bound this explicit symbolic backend, without rejecting the mathematics."""
    _need(len(row) <= MAX_ROW_TERMS,
          'unsupported symbolic replay domain: row exceeds 4096 terms')
    for (_, word), coefficient in row.items():
        _need(len(word) <= MAX_WORD_LENGTH,
              'unsupported symbolic replay domain: free word exceeds 4096 operators')
        _need(abs(coefficient.numerator).bit_length() <= MAX_COEFFICIENT_BITS
              and coefficient.denominator.bit_length() <= MAX_COEFFICIENT_BITS,
              'unsupported symbolic replay domain: rational coefficient exceeds 4096 bits')


def _coefficient(operation, offset):
    _need(len(operation) == offset + 2, 'scalar coefficient needs numerator and denominator')
    numerator, denominator = operation[offset:]
    _integer(numerator, 'scalar numerator must be integer')
    _integer(denominator, 'scalar denominator must be integer')
    _need(numerator != 0 and denominator != 0, 'nonzero scalar with nonzero denominator')
    coefficient = Q(numerator, denominator)
    denominator = coefficient.denominator
    _need(denominator & (denominator - 1) == 0, 'scalar denominator must be dyadic')
    return coefficient


def _scalar_allowance(opcode, coefficient=None):
    if opcode in ('clear', 'copy'):
        return 2
    numerator, denominator = abs(coefficient.numerator), coefficient.denominator
    if opcode == 'scale':
        _need(numerator & (numerator - 1) == 0, 'SCALE must be an invertible dyadic unit')
        return 2 * (abs(numerator.bit_length() - denominator.bit_length()) + int(coefficient < 0))
    return 2 * (3 + numerator.bit_length() - 1 + numerator.bit_count() + denominator.bit_length() - 1)


def _frames_and_maps(canonical):
    h = _integer(canonical['h'], 'binary width h must be integer')
    _need(1 <= h <= 12, 'extractor supports binary widths 1..12')
    frames = canonical['frames']
    _need(type(frames) is list and 0 < len(frames) <= 20000, 'bounded explicit frame table')
    _need(all(type(frame) is list and len(frame) <= h for frame in frames), 'bounded binary frame bases')
    _need(sum(1 << len(frame) for frame in frames) <= 2000000, 'expanded binary frame table exceeds budget')
    spaces = [_span(frame, h) for frame in frames]
    warps = canonical['warps']
    _need(type(warps) is list and len(warps) <= 10000, 'bounded native-map table')
    _need(len(warps) * (1 << h) <= 2000000, 'expanded binary native maps exceed budget')
    maps = []
    for index, warp in enumerate(warps):
        _need(type(warp) is dict and type(warp.get('op')) is int and warp['op'] == index + 1, 'consecutive declared native operator IDs')
        columns = warp['G_columns']
        _need(type(columns) is list and len(columns) == h, 'native binary-map columns')
        _need(len(_span(columns, h)) == 1 << h, 'invertible native binary map')
        forward = tuple(_binary_image(value, columns) for value in range(1 << h))
        inverse = [0] * (1 << h)
        for value, image in enumerate(forward):
            inverse[image] = value
        maps.append((forward, tuple(inverse)))
    return h, spaces, maps


def _port_boundary(canonical, h, spaces):
    """Bind both native main banks to the target tariff used by the caller."""
    v = canonical['v']
    ports = canonical.get('ports')
    _need(type(ports) is list and len(ports) == v,
          'unsupported native boundary: one explicit port per main pair required')
    _need(all(type(port) is int and 0 < port < 1 << h and port.bit_count() % 2 == 1 for port in ports)
          and len(set(ports)) == v,
          'unsupported native boundary: ports must be distinct odd-parity nonzero binary vectors')
    full = frozenset(range(1 << h))
    for index, port in enumerate(ports):
        _need(spaces[canonical['start'][index]] == frozenset((0, port))
              and spaces[canonical['final'][index]] == full,
              f'unsupported native boundary at main pair {index}: first bank must be port-line to full')
        hyperplane = frozenset(value for value in full if (value & port).bit_count() % 2 == 0)
        _need(spaces[canonical['start'][v + index]] == frozenset((0,))
              and spaces[canonical['final'][v + index]] == hyperplane,
              f'unsupported native boundary at main pair {index}: second bank must be zero to the port-orthogonal hyperplane')


def _extract_direction(word, direction, h, spaces, maps):
    canonical = word['canonical']
    v, fields = canonical['v'], len(canonical['start'])
    program = word['programs'][direction]
    _need(type(program) is list and len(program) <= 200000, direction + ': bounded explicit event list')
    if 'owned' in word:
        _need(type(word['owned']) is dict and set(word['owned']) == {'forward', 'backward'}, 'owned contracts for both orientations')
        declaration = word['owned'][direction]
        _need(type(declaration) is list, direction + ': owned role list')
        owned_list = [_role(role, fields) for role in declaration]
        _need(len(set(owned_list)) == len(owned_list), direction + ': duplicate owned role')
        owned = set(owned_list)
        ownership_origin = 'explicit word owned contract'
    else:
        # Original PR4610's established schema has no owned field. Its sole
        # C0 workspace is admitted as owned; all persistent L fields are borrowed.
        owned = {('C', 0)}
        ownership_origin = 'legacy original schema: C0 owned, every L input borrowed'
    _need(all(kind != 'L' or index >= 2 * v for kind, index in owned), direction + ': main input cannot be owned')
    _need(len(owned) <= 10000, direction + ': bounded owned input list')
    roles = {('L', index) for index in range(fields)} | owned
    rows = {role: {(role, ()): Q(1)} for role in sorted(roles)}
    current = {('L', index): frame for index, frame in enumerate(canonical['start'])}
    current.update({role: None for role in owned if role[0] == 'C'})
    paid, counts = Counter(), Counter()
    paid_events, scalar_events, zero_retags, native_events = [], [], [], []
    scalar_total, maximum_l1, maximum_denominator, maximum_terms = 0, Q(1), 1, 1
    phase_labels, adapters = [], []

    def frame_id(value):
        _integer(value, 'frame identifier must be integer')
        _need(0 <= value < len(spaces), 'frame identifier outside explicit table')
        return value

    for position, event in enumerate(program):
        try:
            _need(type(event) is list and event and type(event[0]) is str, 'event must be a nonempty opcode list')
            kind = event[0]
            counts[kind] += 1
            touched = None
            if kind == 'scalar':
                _need(len(event) == 3 and type(event[1]) is list and event[1], 'scalar event shape')
                operation, frame = event[1], frame_id(event[2])
                opcode = operation[0]
                _need(opcode in ('clear', 'copy', 'add', 'scale') and len(operation) >= 2, 'known scalar instruction')
                target = _role(operation[1], fields)
                _need(target in rows, 'scalar destination is not an input or declared owned role')
                touched = target
                coefficient = None
                if opcode == 'clear':
                    _need(len(operation) == 2 and target in owned, 'CLEAR may erase only declared owned input')
                    rows[target] = {}
                    current[target] = frame
                else:
                    _need(current[target] == frame, 'scalar destination frame mismatch')
                    if opcode in ('add', 'copy'):
                        _need(len(operation) >= 3, 'scalar source operand')
                        source = _role(operation[2], fields)
                        _need(source in rows and source != target, 'distinct declared scalar source')
                        _need(current[source] == frame, 'scalar source frame mismatch')
                        if opcode == 'copy':
                            _need(len(operation) == 3 and target in owned and not rows[target], 'COPY requires a cleared owned destination')
                            rows[target] = dict(rows[source])
                        else:
                            coefficient = _coefficient(operation, 3)
                            _add(rows[target], rows[source], coefficient)
                    else:
                        coefficient = _coefficient(operation, 2)
                        _scalar_allowance(opcode, coefficient)
                        rows[target] = {key: coefficient * value for key, value in rows[target].items()}
                allowance = _scalar_allowance(opcode, coefficient)
                scalar_total += allowance
                scalar_events.append({'event': position, 'opcode': opcode, 'role': list(target),
                                      'frame': frame, 'real_scalar_allowance': allowance})
            elif kind in ('climb', 'center'):
                if kind == 'climb':
                    _need(len(event) == 6 and type(event[1]) is str, 'climb event shape')
                    target = _role(['L', event[2]], fields)
                    old, new, declared = event[3:]
                else:
                    _need(len(event) == 5, 'centre event shape')
                    target = _role(['C', event[1]], fields)
                    old, new, declared = event[2:]
                    _need(target in owned, 'centre workspace must be declared owned')
                old, new = frame_id(old), frame_id(new)
                _integer(declared, 'declared paid rank must be integer')
                _need(target in rows and current[target] == old, 'paid input frame mismatch')
                _need(spaces[old] < spaces[new] if kind == 'climb' else
                      spaces[old] < spaces[new] or spaces[new] < spaces[old], 'paid transport must have nested distinct frames')
                rank = abs(len(canonical['frames'][new]) - len(canonical['frames'][old]))
                _need(rank == declared, 'paid rank differs from independently derived frame rank')
                paid[rank] += 1
                paid_events.append({'event': position, 'kind': kind, 'role': list(target),
                                    'input_frame': old, 'output_frame': new, 'rank': rank})
                current[target] = new
                touched = target
            elif kind == 'zero_retag':
                _need(len(event) == 4, 'zero-retag event shape')
                target = _role(event[1], fields)
                old, new = frame_id(event[2]), frame_id(event[3])
                _need(target in rows and current[target] == old, 'zero-retag input frame mismatch')
                _need(not rows[target], 'uncharged zero-retag requires an identically zero full symbolic row')
                current[target] = new
                zero_retags.append({'event': position, 'role': list(target), 'input_frame': old, 'output_frame': new})
                touched = target
            elif kind == 'warp':
                _need(len(event) == 5, 'native event shape')
                target = _role(event[1], fields)
                operator = _integer(event[2], 'native operator ID must be integer')
                old, new = frame_id(event[3]), frame_id(event[4])
                _need(target in rows and current[target] == old and 1 <= abs(operator) <= len(maps), 'native role, operator or input frame mismatch')
                binary_map = maps[abs(operator) - 1][int(operator < 0)]
                _need(frozenset(binary_map[value] for value in spaces[old]) == spaces[new],
                      'native map has an unpriced residual between its actual input and output frames')
                # The retained backward ABI is primitive-wise conjugation,
                # not adjoint or reversal. It uses an independent formal alphabet.
                symbol = (1 if operator > 0 else -1) * (abs(operator) + (1000000 if direction == 'backward' else 0))
                rows[target] = {(variable, word[1:] if word and word[0] == -symbol else (symbol,) + word): value
                                for (variable, word), value in rows[target].items()}
                current[target] = new
                native_events.append({'event': position, 'role': list(target), 'operator': operator,
                                      'input_frame': old, 'output_frame': new, 'residual_rank': 0})
                touched = target
            elif kind == 'adapter':
                _need(len(event) == 4 and event[1] in ('old_to_new', 'new_to_old'), 'known endpoint adapter marker')
                index = _integer(event[2], 'main adapter index must be integer')
                _need(0 <= index < 2 * v, 'endpoint adapters may touch main roles only')
                frame = frame_id(event[3])
                expected = canonical['start' if event[1] == 'old_to_new' else 'final'][index]
                _need(frame == expected, 'adapter marker disagrees with endpoint frame')
                adapters.append((event[1], index, frame))
            elif kind == 'phase':
                _need(len(event) == 2 and event[1] in PHASES, 'known retained phase annotation')
                phase_labels.append(event[1])
            else:
                raise ValueError('unknown event opcode ' + kind)
            if touched is not None:
                row = rows[touched]
                _guard_row(row)
                maximum_terms = max(maximum_terms, len(row))
                maximum_l1 = max(maximum_l1, sum(map(abs, row.values()), Q(0)))
                maximum_denominator = max(maximum_denominator, max((value.denominator for value in row.values()), default=1))
        except (KeyError, TypeError, IndexError, ZeroDivisionError, ValueError) as error:
            raise ValueError(f'{direction} event {position}: {error}') from None
    _need(phase_labels == PHASES, direction + ': complete retained phase annotation sequence')
    expected_adapters = {(kind, index, canonical[side][index]) for kind, side in
                         [('old_to_new', 'start'), ('new_to_old', 'final')] for index in range(2 * v)}
    _need(len(adapters) == len(expected_adapters) and set(adapters) == expected_adapters,
          direction + ': exactly one entry and exit adapter for each main role')
    _need([current['L', index] for index in range(fields)] == canonical['final'], direction + ': final persistent frame mismatch')
    for role, row in sorted(rows.items()):
        expected = {} if role in owned else {(role, ()): Q(1)}
        if role not in owned and role[0] == 'L':
            index = role[1]
            if direction == 'backward' and index < v:
                expected[(('L', index + v), ())] = Q(-1)
            elif direction == 'forward' and v <= index < 2 * v:
                expected[(('L', index - v), ())] = Q(1)
        _need(row == expected, direction + ': symbolic return mismatch for ' + str(list(role)))
    helpers, helper_targets = Counter(), []
    for index in range(2 * v, fields):
        role = 'L', index
        old, new = canonical['start'][index], current[role]
        rank = len(canonical['frames'][new]) - len(canonical['frames'][old])
        credited = role not in owned
        if credited:
            _need(spaces[old] < spaces[new], direction + ': retained helper has nonascending target contract')
            helpers[rank] += 1
        helper_targets.append({'role': list(role), 'input_frame': old, 'output_frame': new,
                               'target_rank': rank, 'credited': credited,
                               'reason': 'independent symbolic identity return' if credited else 'owned input erased; no productive credit'})
    return {'paid': {str(rank): count for rank, count in sorted(paid.items())},
            'helpers': {str(rank): count for rank, count in sorted(helpers.items())},
            'paid_events': paid_events, 'helper_targets': helper_targets,
            'scalar_allowance': scalar_total, 'scalar_events': scalar_events,
            'zero_retags': zero_retags, 'native_events': native_events,
            'owned': [list(role) for role in sorted(owned)], 'ownership_origin': ownership_origin,
            'independent_owned_entry_columns': len(owned),
            'independent_persistent_columns': fields - sum(kind == 'L' for kind, _ in owned),
            'owned_outputs_zero': True, 'event_counts': dict(sorted(counts.items())),
            'max_formal_prefix_l1': str(maximum_l1), 'max_denominator': maximum_denominator,
            'max_row_terms': maximum_terms,
            'paid_calls': sum(paid.values()), 'productive_helpers': sum(helpers.values())}


def extract(word):
    """Return source-derived JSON-friendly native ledgers, or raise ValueError.

    Input is an already decoded literal native-word dict. The original legacy
    schema and the two explicit-owned successor schemas share this interpreter.
    Every declared paid_profiles/local_profile entry is deliberately ignored.
    The returned hashes identify canonical JSON objects, not compressed bytes.
    """
    try:
        _need(type(word) is dict and type(word.get('canonical')) is dict, 'word and canonical must be objects')
        if 'schema' in word:
            _need(word['schema'] in ('joint-helper-relations-word/1', 'eight-owned-helper-relations/1')
                  and 'owned' in word, 'unsupported explicit native-word schema or missing owned contract')
        else:
            _need('owned' not in word, 'legacy original schema cannot add an implicit owned contract')
        canonical = word['canonical']
        v = _integer(canonical['v'], 'main-port count must be integer')
        _need(1 <= v <= 1000 and type(canonical['start']) is list and type(canonical['final']) is list, 'bounded main ports and explicit endpoints')
        fields = len(canonical['start'])
        _need(2 * v <= fields <= 10000 and len(canonical['final']) == fields, 'persistent endpoint field inventory')
        _need(type(word.get('programs')) is dict and set(word['programs']) == {'forward', 'backward'}, 'literal forward and backward programs required')
        h, spaces, maps = _frames_and_maps(canonical)
        for frame in canonical['start'] + canonical['final']:
            _need(type(frame) is int and 0 <= frame < len(spaces), 'endpoint frame outside explicit table')
        _port_boundary(canonical, h, spaces)
        orientations = {direction: _extract_direction(word, direction, h, spaces, maps)
                        for direction in ('forward', 'backward')}
        return {'schema': SCHEMA, 'word_sha256': _digest(word),
                'canonical_sha256': _digest(canonical), 'v': v, 'h': h,
                'fields': fields, 'orientations': orientations,
                'scope': 'Literal-source symbolic endpoint/ownership and frame-rank conformance only; no absolute phase, precision, physical cost implementation, compiler or supplier admission.'}
    except (KeyError, TypeError, IndexError, ZeroDivisionError) as error:
        raise ValueError('malformed native word: ' + str(error)) from None
