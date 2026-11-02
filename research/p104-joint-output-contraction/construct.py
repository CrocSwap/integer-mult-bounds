"""Construct nine native output contractions with two helper bases.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The source word and native transpose retain the credits in NOTICE.
"""
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction as Q
import json

from support import need

ZERO, FULL, PUBLIC = 3, 127, 770
B0 = [
    ('SWAP', 393, 395), ('SWAP', 297, 296), ('SWAP', 226, 449), ('SWAP', 361, 367),
    ('SCALE', 395, Q(4)), ('SCALE', 449, Q(-1)), ('ADD', 704, 703, Q(-1)),
    ('ADD', 707, 484, Q(4)), ('ADD', 707, 449, Q(-4)),
    ('ADD', 288, 296, Q(-1)), ('ADD', 292, 296, Q(-1)), ('ADD', 299, 296, Q(2)),
    ('ADD', 302, 296, Q(-1)), ('ADD', 303, 296, Q(2)),
    ('ADD', 352, 367, Q(-1)), ('ADD', 356, 367, Q(-1)), ('ADD', 366, 367, Q(-1)),
]
C = {
    244: [('SCALE', 176, Q(-1)), ('SWAP', 393, 176), ('ADD', 208, 393, Q(-1))],
    234: [('SCALE', 152, Q(-1)), ('SWAP', 297, 152)],
    242: [('SCALE', 142, Q(-2)), ('SWAP', 361, 142), ('ADD', 171, 361, Q(1, 2))],
}


def span(basis):
    values = {0}
    for x in basis:
        values |= {y ^ x for y in tuple(values)}
    return values


def basis(values):
    out, space = [], {0}
    for x in sorted(values):
        if x not in space:
            out.append(x)
            space |= {y ^ x for y in tuple(space)}
    return out


def complement(frame):
    return basis(x for x in range(512) if all((x & y).bit_count() % 2 == 0 for y in frame))


def transpose(word):
    """Reverse the word and take orthogonal native frames."""
    out = deepcopy(word)
    frame_id = lambda f: {ZERO: FULL, FULL: ZERO}.get(f, f)
    role = dict(enumerate(range(word['public'] + word['owned_fields'])))
    for r in word['live']:
        role[r], role[r + 112] = r + 112, r
    for f, bs in enumerate(word['frames']):
        out['frames'][frame_id(f)] = complement(bs)
    for r in range(word['public']):
        out['initial'][role[r]] = frame_id(word['final'][r])
        out['final'][role[r]] = frame_id(word['initial'][r])
    program = []
    for event in reversed(word['program']):
        op, r = event[:2]
        r = role[r]
        if op == 'MOVE':
            program.append(['MOVE', r, frame_id(event[3]), frame_id(event[2]), event[4]])
        elif op in ('INIT', 'CLEAR'):
            program.append(['CLEAR' if op == 'INIT' else 'INIT', r, frame_id(event[2])])
        elif op in ('ADD', 'COPY'):
            program.append(['ADD', role[event[2]], r, event[3], frame_id(event[4])])
        elif op == 'SCALE':
            program.append(['SCALE', r, event[2], frame_id(event[3])])
        else:
            raise ValueError('Unsupported source event: ' + op)
    out['program'] = program
    return out


def add(target, source, coefficient):
    for k, value in source.items():
        result = target.get(k, Q(0)) + coefficient * value
        if result:
            target[k] = result
        else:
            target.pop(k, None)


def expand(operations):
    out = []
    for event in operations:
        if event[0] == 'SWAP':
            _, r, s = event
            out.extend([('ADD', r, s, Q(1)), ('ADD', s, r, Q(-1)),
                        ('ADD', r, s, Q(1)), ('SCALE', s, Q(-1))])
        else:
            out.append(event)
    return out


def apply(rows, operations):
    for event in expand(operations):
        if event[0] == 'ADD':
            add(rows[event[1]], rows[event[2]], Q(event[3]))
        else:
            need(event[0] == 'SCALE', 'Only reversible scalar basis operations')
            rows[event[1]] = {k: Q(event[2]) * v for k, v in rows[event[1]].items()}


def inverse(operations):
    out = []
    for event in reversed(operations):
        if event[0] == 'SWAP':
            out.append(event)
        elif event[0] == 'ADD':
            out.append(('ADD', event[1], event[2], -Q(event[3])))
        else:
            out.append(('SCALE', event[1], 1 / Q(event[2])))
    return out


def emit(operations, frame, rename=None):
    rename, out = rename or {}, []
    for event in expand(operations):
        if event[0] == 'ADD':
            out.append(['ADD', rename.get(event[1], event[1]), rename.get(event[2], event[2]),
                        str(event[3]), frame])
        else:
            out.append(['SCALE', rename.get(event[1], event[1]), str(event[2]), frame])
    return out


def construct(source):
    need(source['public'] == PUBLIC and source['owned_fields'] == 29, 'Exact source inventory')
    word = transpose(source)
    out = deepcopy(word)
    new_frame = len(word['frames'])
    out['frames'].append(basis(span(word['frames'][712]) & span(word['frames'][714])))
    entries = {703: new_frame, 393: 246, 707: 246, 484: 246, 297: 246,
               485: 246, 226: 246, 361: 245, 451: 245}
    anchors = list(entries)
    shadow = dict(zip(anchors, range(PUBLIC, PUBLIC + len(anchors))))
    first = {}
    for i, event in enumerate(word['program']):
        if event[0] == 'MOVE' and event[2] == ZERO and event[1] < PUBLIC:
            need(event[1] not in first, 'One public departure from the zero frame')
            first[event[1]] = (i, event[3])
    zero = [e for e in word['program'] if e[0] in ('ADD', 'COPY', 'SCALE') and e[-1] == ZERO]
    need(all(e[0] in ('ADD', 'SCALE') and e[1] < PUBLIC and
             (e[0] == 'SCALE' or e[2] < PUBLIC) for e in zero), 'Public zero-frame preparation')
    prep_operations = [tuple(e[:-1]) for e in zero]
    A = [{r: Q(1)} for r in range(PUBLIC)]
    apply(A, prep_operations)
    for operations in C.values():
        apply(A, operations)
    B = [{r: Q(1)} for r in range(PUBLIC)]
    apply(B, B0)
    main = set(word['live']) | {r + 112 for r in word['live']}
    helpers = {r for r in range(PUBLIC) if r not in main and
               word['initial'][r] == ZERO and word['final'][r] == FULL}
    used = {e[1] for e in B0} | {e[2] for e in B0 if e[0] in ('ADD', 'SWAP')}
    need(used <= helpers and set(anchors) <= helpers, 'Only independent full helpers in the input basis')
    off_anchor, responses, directions = {}, defaultdict(dict), {}
    for a in anchors:
        need(set(A[a]) <= helpers, 'Helper-only departure functional')
        row = {}
        for k, coefficient in A[a].items():
            add(row, B[k], coefficient)
        need({r: row.get(r, Q(0)) for r in anchors} ==
             {r: Q(int(r == a)) for r in anchors}, 'Exact unit anchor pairing')
        row.pop(a)
        off_anchor[a] = row
        need(set(row) <= helpers - set(anchors), 'Unit off-anchor input correction')
        directions[a] = {r: B[r][a] for r in range(PUBLIC) if a in B[r]}
        for r in range(PUBLIC):
            value = sum(c * B[k].get(a, Q(0)) for k, c in A[r].items())
            if value:
                responses[r][a] = value
    B2 = [('ADD', a, r, -c) for a, row in off_anchor.items() for r, c in row.items()]
    # Execute the preparation with zero anchor inputs. These rows must clear to zero.
    prepared = [{} if r in anchors else {r: Q(1)} for r in range(PUBLIC)]
    for operations in [B2, B0, prep_operations, *C.values()]:
        apply(prepared, operations)
    need(all(not prepared[a] for a in anchors), 'All nine temporary rows are exactly zero at CLEAR')
    prep = [['INIT', s, ZERO] for s in shadow.values()]
    dual_controls = {'input_basis': len(prep)}
    prep += emit(B2, ZERO, shadow) + emit(B0, ZERO, shadow)
    prep += emit(prep_operations, ZERO, shadow)
    for operations in C.values():
        prep += emit(operations, ZERO, shadow)
    prep += [['CLEAR', s, ZERO] for s in reversed(tuple(shadow.values()))]
    for a, f in entries.items():
        out['initial'][a] = f
    groups = defaultdict(list)
    for r in responses:
        need(r in first, 'Every response has a first departure')
        groups[first[r][1]].append(r)
    early, moved = [], set()

    def move(r, destination, origin=ZERO):
        need(span(out['frames'][origin]) <= span(out['frames'][destination]),
             'Native entrance is a subspace of its destination')
        early.append(['MOVE', r, origin, destination, False])
        if origin == ZERO:
            moved.add(r)

    for g, registers in sorted(groups.items()):
        primary = [r for r in registers if r in anchors]
        if primary:
            need(len(registers) == len(primary) and all(responses[r] == {r: Q(1)} for r in primary),
                 'Isolated unit primary responses')
            continue
        frames = {entries[a] for r in registers for a in responses[r]}
        need(len(frames) == 1, 'One entrance frame per response group')
        f = frames.pop()
        if g == f:
            for r in registers:
                move(r, g)
                early += [['ADD', r, a, str(c), f] for a, c in responses[r].items()]
        else:
            carrier = min(registers, key=lambda r: (len(responses[r]), r))
            response = responses[carrier]
            pivot, multipliers = next(iter(response)), {}
            for r in registers:
                if r == carrier:
                    continue
                ratio = responses[r].get(pivot, Q(0)) / response[pivot]
                need(responses[r] == {a: ratio * c for a, c in response.items()}, 'Rank-one response group')
                multipliers[r] = ratio
                dual_controls.setdefault('dirty_carrier_subtraction', len(prep) + len(early))
                early.append(['ADD', r, carrier, str(-ratio), ZERO])
                move(r, g)
            move(carrier, f)
            early += [['ADD', carrier, a, str(c), f] for a, c in response.items()]
            move(carrier, g, f)
            early += [['ADD', r, carrier, str(c), g] for r, c in multipliers.items()]
    # Keep all primary inputs at their entrance until every response is delivered.
    for a, f in entries.items():
        move(a, first[a][1], f)
        moved.add(a)
    for g, operations in C.items():
        involved = {e[1] for e in operations} | {e[2] for e in operations if e[0] in ('ADD', 'SWAP')}
        for r in sorted(involved):
            need(first[r][1] == g, 'Common departure group for each basis block')
            if r not in moved:
                move(r, g)
        dual_controls.setdefault('departure_basis_inverse', len(prep) + len(early))
        early += emit(inverse(operations), g)
    rest, omitted = [], set()
    for i, event in enumerate(word['program']):
        if event[0] in ('ADD', 'COPY', 'SCALE') and event[-1] == ZERO:
            continue
        if event[0] == 'MOVE' and event[2] == ZERO and event[1] in moved:
            need(i == first[event[1]][0] and event[1] not in omitted, 'Exact eager departure')
            omitted.add(event[1])
            continue
        rest.append(deepcopy(event))
    need(omitted == moved, 'Every eager departure replaces one source departure')
    dual_controls['output_basis_inverse'] = len(prep) + len(early) + len(rest)
    out['program'] = prep + early + rest + emit(inverse(B0), FULL) + emit(inverse(B2), FULL)
    forward = transpose(out)
    # Restore the original frame coordinates. The final native replay checks their phases.
    for f, bs in enumerate(source['frames']):
        need(span(forward['frames'][f]) == span(bs), 'Exact original native subspace')
    forward['frames'][:len(source['frames'])] = deepcopy(source['frames'])
    witness = {'B0': B0, 'B2': B2, 'C': C, 'directions': directions, 'entries': entries,
               'responses': dict(responses), 'shadow_roles': shadow, 'zero_rows_at_clear': len(anchors),
               'early_events': len(early), 'replaced_departures': sorted(moved),
               'control_indices': {label: len(out['program']) - 1 - i for label, i in dual_controls.items()}}
    return forward, witness


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def payload(value):
    return (json.dumps(encode(value), sort_keys=True, separators=(',', ':')) + '\n').encode()
