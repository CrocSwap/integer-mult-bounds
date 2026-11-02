"""Build a joint lift in the former fixed-contact helper block.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The source, basis construction, native maps and caller retain their credits.
"""
from copy import deepcopy
from fractions import Fraction as Q
from collections import defaultdict
from legacy_basis import transpose, add, apply, inverse, emit, span
from support import need
ZERO, FULL = (3, 127)

def construct(source):
    w = transpose(source)
    out = deepcopy(w)
    N = w['public']
    a, b = (224, 227)
    anchors = [a, b]
    entries = {a: 245, b: 245}
    shadow = {a: N + 9, b: N + 10}
    helpers = {r for r in range(N) if r not in set(w['live']) | {s + 112 for s in w['live']} and w['initial'][r] == ZERO and (w['final'][r] == FULL)}
    zero = [e for e in w['program'] if e[0] in ('ADD', 'COPY', 'SCALE', 'INIT', 'CLEAR') and e[-1] == ZERO]
    need(not any((e[0] == 'MOVE' and e[1] >= N and (e[2] == ZERO or e[3] == ZERO) for e in w['program'])), 'No owned transport through the preparation frame')
    old_zero_owned = {e[1] for e in zero if e[0] == 'INIT'}
    need(not old_zero_owned.intersection(shadow.values()), 'Disjoint zero-register lifetimes')
    first = {e[1]: (i, e[3]) for i, e in enumerate(w['program']) if e[0] == 'MOVE' and e[1] < N and (e[2] == ZERO)}
    groups = defaultdict(list)
    for r, (i, g) in first.items():
        groups[g].append(r)

    def execute(rows, program):
        for e in program:
            op, r = e[:2]
            if op in ('INIT', 'CLEAR'):
                if op == 'CLEAR':
                    need(not rows[r], 'Every preparation CLEAR is zero')
                rows[r] = {}
            elif op == 'SCALE':
                rows[r] = {k: Q(e[2]) * v for k, v in rows[r].items()}
            elif op == 'COPY':
                need(not rows[r], 'Preparation COPY is zero')
                rows[r] = {k: Q(e[3]) * v for k, v in rows[e[2]].items()}
            elif op == 'ADD':
                add(rows[r], rows[e[2]], Q(e[3]))
            else:
                raise ValueError('Preparation opcode')
    A = [{r: Q(1)} for r in range(N + w['owned_fields'])]
    execute(A, zero)
    B0 = [('ADD', a, b, Q(1)), ('SCALE', b, Q(-2)), ('ADD', b, a, Q(1)), ('SCALE', a, Q(2))]
    extra = {228: 1, 229: -1, 232: -1, 233: 1, 238: -1, 239: 1, 449: -1}
    B0 += [('ADD', r, b, Q(c)) for r, c in extra.items()]
    used = {e[1] for e in B0} | {e[2] for e in B0 if e[0] == 'ADD'}
    need(used <= helpers, 'Input basis uses full independent helpers')
    B = [{r: Q(1)} for r in range(N + w['owned_fields'])]
    apply(B, B0)
    C = [('ADD', 193, 742, Q(1, 2)), ('ADD', 169, 742, Q(1, 2)), ('SWAP', a, 193), ('SWAP', b, 169)]
    g = 1091
    need(all((first[r][1] == g for r in [193, 742, 169, a, b])), 'One native departure block')
    apply(A, C)

    def response(r, anchor):
        return sum((c * B[k].get(anchor, Q(0)) for k, c in A[r].items()))
    need([[response(r, x) for x in anchors] for r in anchors] == [[1, 0], [0, 1]], 'Unit primary responses')
    for r in groups[g]:
        if r in anchors:
            continue
        ops = [('ADD', r, x, -response(r, x)) for x in anchors if response(r, x)]
        C += ops
        apply(A, ops)
    B2 = []
    off = {}
    for r in anchors:
        row = {}
        for k, c in A[r].items():
            add(row, B[k], c)
        need({x: row.get(x, 0) for x in anchors} == {x: Q(x == r) for x in anchors}, 'Exact anchor input pairing')
        row.pop(r)
        need(set(row) <= helpers - set(anchors), 'Helper-only off-anchor correction')
        off[r] = row
        B2 += [('ADD', r, s, -c) for s, c in row.items()]
    response_rows = {r: {x: response(r, x) for x in anchors if response(r, x)} for r in range(N)}
    response_rows = {r: row for r, row in response_rows.items() if row}
    need(set(response_rows) <= set(first), 'All responses have native departures')
    need(all((first[r][1] == 245 for r in response_rows if r not in anchors)), 'Only the entrance block needs nonprimary responses')
    prep = [['INIT', s, ZERO] for s in shadow.values()]
    controls = {'input_correction': len(prep)}
    prep += emit(B2, ZERO, shadow)
    controls['input_basis'] = len(prep)
    prep += emit(B0, ZERO, shadow)
    for e in zero:
        e = list(e)
        e[1] = shadow.get(e[1], e[1])
        if e[0] in ('ADD', 'COPY'):
            e[2] = shadow.get(e[2], e[2])
        prep.append(e)
    controls['departure_basis'] = len(prep)
    prep += emit(C, ZERO, shadow)
    prepared = [{r: Q(1)} for r in range(N + w['owned_fields'])]
    execute(prepared, prep)
    need(all((not prepared[s] for s in shadow.values())), 'Both new preparation rows are exactly zero')
    controls['temporary_clear'] = len(prep)
    prep += [['CLEAR', s, ZERO] for s in reversed(tuple(shadow.values()))]
    for r, f in entries.items():
        out['initial'][r] = f
    early = []
    moved = set()
    for r, row in response_rows.items():
        if r in anchors:
            continue
        early.append(['MOVE', r, ZERO, 245, False])
        moved.add(r)
        controls.setdefault('response', len(prep) + len(early))
        early += [['ADD', r, x, str(c), 245] for x, c in row.items()]
    for r in anchors:
        controls.setdefault('native_move', len(prep) + len(early))
        early.append(['MOVE', r, 245, g, False])
        moved.add(r)
    for r in groups[g]:
        if r not in moved:
            early.append(['MOVE', r, ZERO, g, False])
            moved.add(r)
    controls['departure_inverse'] = len(prep) + len(early)
    early += emit(inverse(C), g)
    rest = []
    omitted = set()
    for i, e in enumerate(w['program']):
        if e[0] in ('ADD', 'COPY', 'SCALE', 'INIT', 'CLEAR') and e[-1] == ZERO:
            continue
        if e[0] == 'MOVE' and e[1] in moved and (e[2] == ZERO):
            need(first[e[1]][0] == i and e[1] not in omitted, 'Exact eager departure replacement')
            omitted.add(e[1])
            continue
        rest.append(deepcopy(e))
    need(omitted == moved, 'All replaced departures are present')
    controls['output_basis'] = len(prep) + len(early) + len(rest)
    out['program'] = prep + early + rest + emit(inverse(B0), FULL)
    controls['output_correction'] = len(out['program'])
    out['program'] += emit(inverse(B2), FULL)
    forward = transpose(out)
    need(all(span(a) == span(b) for a, b in zip(forward['frames'], source['frames'])),
         'Double transpose preserves every native subspace')
    forward['frames'] = deepcopy(source['frames'])
    witness = dict(anchors=anchors, entries=entries, shadow=shadow, B0=B0, B2=B2, C=C, responses=response_rows, off_anchor=off, prep_length=len(prep), early_length=len(early), moved=sorted(moved), zero_rows=2, control_indices={key: len(out['program']) - 1 - i for key, i in controls.items()})
    return (forward, witness)
