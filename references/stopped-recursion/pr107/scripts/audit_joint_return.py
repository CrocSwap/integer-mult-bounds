#!/usr/bin/env python3
"""Early block readout, exact auxiliary repair, and a two-return rank screen.

The rejection concerns two coordinate-complement carry spaces with retained
high frames and outer cuts. It is not an arbitrary-frame/topology lower bound.
"""
from hashlib import sha256
from itertools import combinations
from math import comb
from pathlib import Path
import json

from audit_block_carry import SCHEDULE, block_program, execute
from certify import require, verify_sources
from paired_network import circuit

ROOT = Path(__file__).resolve().parents[1]
INVERSE = tuple({'L': 'Li', 'Li': 'L'}.get(op, op) for op in reversed(SCHEDULE))


def early_program(h, columns, rows, omit=None):
    """Move each deferred Y scatter before the column's second central gather.

    Corrections are expanded as primitive XORs of existing row-center roles.
    Every input, including scratch, remains arbitrary.
    """
    old = block_program(h, columns, rows)
    code = circuit(h).program()
    triples = code['triples']; v = old['v']
    columns = old['columns']; rows = old['rows']; selected = set(rows)

    def column_word(a, word, split=False):
        scratch, center = old['col_aux'][a]
        x = [v*v+a*v+b for b in range(v)]
        y = [a*v+b for b in range(v)]
        result = []
        for op in word:
            if op in ('L', 'Li'):
                gates = code['gates'] if op == 'L' else reversed(code['gates'])
                for ins, outs in gates:
                    local = [(scratch[ins[0]], scratch[s]) for s in ins[1:]]
                    local += [(scratch[s], scratch[ins[0]]) for s in outs[1:]]
                    result.extend(local if op == 'L' else reversed(local))
            elif op == 'V':
                result.extend((scratch[s], x[t]) for t, s in code['sources'])
            elif op == 'J':
                result.extend((y[t], scratch[s]) for t, s in code['outputs'])
            elif op == 'R':
                result.extend((y[t], center[i]) for t in range(v) for i in triples[t])
            elif op == 'G':
                order = (list(t for t in range(v) if t not in selected) + list(rows)) if split else range(v)
                result.extend((center[i], x[t]) for t in order for i in triples[t])
            else:
                raise ValueError(op)
        return result

    # Recover only the already-checked row prefixes; verify the column slice
    # independently so a changed retained schedule cannot silently misalign it.
    old_columns = [op for a in columns for op in column_word(a, INVERSE)]
    tail_length = len(rows)*(9*len(columns)+3*v)
    prefix_length = len(old['operations'])-len(old_columns)-tail_length
    require(old['operations'][prefix_length:prefix_length+len(old_columns)] == old_columns,
            'Retained column word changed')
    ops = list(old['operations'][:prefix_length])
    require(INVERSE[:6] == ('V', 'G', 'L', 'J', 'Li', 'R'), 'Wrong early cut')
    require(INVERSE[6:] == ('G', 'V', 'R', 'L', 'J', 'Li'), 'Wrong suffix')
    repairs = dict(center=0, side=0)
    for a in columns:
        scratch, center = old['col_aux'][a]
        ops.extend(column_word(a, INVERSE[:6]))
        for b in rows:
            row_center = old['row_aux'][b][1]
            ops.extend((v*v+a*v+b, row_center[i]) for i in triples[a])
        ops.extend(column_word(a, INVERSE[6:], split=True))
        # Injecting delta in the source before this suffix propagates to
        # Y, X, column centers G delta, and source scratch B delta.
        # The first two are desired; undo the last two without fresh roles.
        for b in rows:
            row_center = old['row_aux'][b][1]
            correction = [(center[j], row_center[i]) for j in triples[b] for i in triples[a]]
            repairs['center'] += len(correction)
            if omit != 'center_repair': ops.extend(correction)
        for b, s in code['sources']:
            if b in selected:
                correction = [(scratch[s], old['row_aux'][b][1][i]) for i in triples[a]]
                repairs['side'] += len(correction)
                if omit != 'side_repair': ops.extend(correction)
    for b in rows:
        center = old['row_aux'][b][1]
        ops.extend((center[i], a*v+b) for a in range(v) for i in triples[a])
        if omit != 'row_repair':
            ops.extend((center[i], v*v+a*v+b) for a in columns for i in triples[a])
    result = dict(old)
    result.update(operations=ops, column_repairs=repairs)
    return result


def scalar_check(h, columns, rows):
    new = early_program(h, columns, rows)
    original = block_program(h, columns, rows, delayed=False)
    initial = [1 << i for i in range(new['roles'])]
    expected = list(initial); v = new['v']
    for b in rows:
        for a in range(v): expected[v*v+a*v+b] ^= expected[a*v+b]
    for a in columns:
        for b in range(v): expected[a*v+b] ^= expected[v*v+a*v+b]
    actual = execute(new, initial)
    require(actual == expected == execute(original, initial), 'Early map or dirty restoration failed')
    require(execute(new, actual, inverse=True) == initial, 'Early inverse failed')
    require(new['roles'] == original['roles'], 'Extra roles allocated')
    cells = len(columns)*len(rows)
    # The retained compiler has one source slot per triple. Check rather than
    # assume this, since it controls the exact auxiliary correction count.
    require(new['column_repairs'] == dict(center=9*cells, side=3*cells), 'Changed source multiplicity')
    extra = len(new['operations'])-len(original['operations'])
    require(extra == 15*cells, 'Wrong scalar overhead')
    return dict(h=h, columns=len(columns), rows=len(rows), independent_variables=new['roles'],
                additional_roles=0, additional_xors=extra, column_repairs=new['column_repairs'],
                full_map_and_dirty_restoration_exact=True, inverse_exact=True,
                program_sha256=sha256(json.dumps(new['operations'], separators=(',', ':')).encode()).hexdigest())


def selected_count(h, k):
    return comb(h, 3)-comb(h-k, 3)


def return_credit(h, k):
    # Favor the candidate when the outside triples cannot span the outside
    # coordinates; in that case credit the whole central return as free.
    return h*h if h-k <= 3 else h*h-(h-k)**2


def joint_screen(h, k, ell):
    require(h >= 6 and h != 9 and 1 <= k <= h and 1 <= ell <= h, 'Invalid block')
    q, r = selected_count(h, k), selected_count(h, ell)
    row_credit = 2*r*return_credit(h, k)
    column_credit = 2*q*return_credit(h, ell)
    net = q*r-row_credit-column_credit
    return dict(h=h, k=k, ell=ell, columns=q, rows=r,
                global_Y_excess_lower_bound=q*r,
                maximum_row_return_rank_credit=row_credit,
                maximum_column_return_rank_credit=column_credit,
                net_rank_increase_lower_bound=net, excluded=net > 0)


def certificate():
    controls = []
    for h, k, ell in ((6, 1, 1), (6, 2, 1), (6, 6, 1), (8, 1, 1)):
        triples = list(combinations(range(h), 3))
        columns = [i for i, t in enumerate(triples) if any(j < k for j in t)]
        rows = [i for i, t in enumerate(triples) if any(j < ell for j in t)]
        controls.append(scalar_check(h, columns, rows))
    controls += [scalar_check(6, [0, 3, 7], [1, 4]), scalar_check(6, [], [0]), scalar_check(6, [1], [])]
    screens = [joint_screen(50, k, ell) for k, ell in ((1, 1), (1, 5), (5, 5), (10, 25), (25, 25), (48, 49), (50, 50))]
    require(all(x['excluded'] for x in screens), 'Unexpected viable joint screen')
    sources = ('scripts/audit_joint_return.py', 'docs/research/joint-return-audit.md')
    return dict(status='EXACT EARLY READOUT; TWO COORDINATE RETURNS STILL LOSE RANK; NO NEW KAPPA',
                upstream_commit=verify_sources(), scalar_controls=controls, full_size_screens=screens,
                full_frame_certificate_supplied=False,
                all_h_screen='For h>=27, v-1>4h^2 and B(h,k)/q(h,k)<=h^2/(v-1), so every coordinate pair is excluded.',
                scope='Retained row/column high frames, coordinate-complement early gates on outside points, fixed outer data/auxiliary cuts, and readout containing the row carry. Both return credits are allowed simultaneously; all other new costs are ignored.',
                decision='Close this coordinate-carry fusion branch; prefer a different complete finite circuit/frame topology.',
                source_sha256={p: sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__ == '__main__':
    result = certificate()
    (ROOT/'certificates/joint-return-audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS early readout and dirty auxiliary repair; two-coordinate-return budget fails; no new kappa.')
