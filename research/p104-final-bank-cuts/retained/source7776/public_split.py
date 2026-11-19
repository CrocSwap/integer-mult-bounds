"""Replay public-cohort and paid-cohort bank splits with rational arithmetic."""
from fractions import Fraction
from graphlib import TopologicalSorter
from bank_split import add, rewrite, rotation


def transposed(net):
    first = net.first_output
    def rev(i):
        return first+~i if i < 0 else ~(i-first) if i >= first else i
    rows = {i: {} for i in [*net.moves, *range(first, first+len(net.initial))]}
    for i, row in net.forms.items():
        for j, q in row.items():
            rows[rev(j)][rev(i)] = q
    return type(net)(first, net.final[:], net.initial[:], {k:(b,a) for k,(a,b) in net.moves.items()}, rows)


def rotate_all(net, changes):
    forward, backward = {}, {}
    first = net.first_output
    for c in changes:
        slots = c['slots']
        if c['public']:
            assert len({(net.initial[i], net.final[i]) for i in slots}) == 1
            receive = lambda i: ~i
            emit = lambda i: first+i
        else:
            assert len({net.moves[i] for i in slots}) == 1
            receive = emit = lambda i:i
        f, b = rotation(slots, c['rows'])
        for i in slots:
            forward[emit(i)] = {emit(j):q for j,q in f[i].items()}
            backward[receive(i)] = {receive(j):q for j,q in b[i].items()}
    rows = {}
    for j, row in net.forms.items():
        if j in forward:
            row = {}
            for i, q in forward[j].items():
                add(row, net.forms[i], q)
        rows[j] = rewrite(row, backward)
    return rows


def reduced(row, bank):
    remainder = row.copy()
    weights = {}
    while remainder:
        i = max(remainder)
        if i not in bank:
            break
        v, exp = bank[i]
        q = remainder[i]
        add(remainder, v, -q)
        add(weights, exp, q)
    return remainder, weights


def split(net, e):
    if e['transposed']:
        net = transposed(net)
    if e.get('helper_birth'):
        from birth_event import apply_split
        fresh = apply_split(net, e['helper_birth'])
        return transposed(fresh) if e['transposed'] else fresh
    first, old, new = net.first_output, e['old'], e['new']
    row = rotate_all(net, e['rotations'])
    initial, final, moves = net.initial[:], net.final[:], net.moves.copy()
    received, sent = set(e['arrivals']), set(e['sends'])
    for i in received:
        if i < 0:
            assert initial[~i] == old
            initial[~i] = new
        else:
            a, b = moves[i]
            assert b == old
            moves[i] = a, new
    for j in sent:
        if j >= first:
            assert final[j-first] == old
            final[j-first] = new
        else:
            a, b = moves[j]
            assert a == old
            moves[j] = new, b
    def crossing(j):
        return {i:q for i,q in row[j].items() if (i in received) != (j in sent)}
    banks = [{}, {}]
    added = {}
    for event in e['generators']:
        k, j = event['slot'], event['row']
        assert k not in moves
        side = j in sent
        v = crossing(j)
        remainder, weights = reduced(v, banks[side])
        assert remainder
        i = max(remainder)
        q = remainder[i]
        expr = {k: Fraction(1)}
        add(expr, weights, -1)
        banks[side][i] = ({h:c/q for h,c in remainder.items()}, {h:c/q for h,c in expr.items()})
        added[k] = v
        moves[k] = (old, new) if side else (new, old)
    for j, full in list(row.items()):
        original = net.moves[j][0] if j < first else net.final[j-first]
        if original != old:
            continue
        c = crossing(j)
        if c:
            remainder, weights = reduced(c, banks[j in sent])
            assert not remainder
            row[j] = {i:q for i,q in full.items() if i not in c} | weights
    row.update(added)
    gone = set(e['removed_paid'])
    assert gone == {k for k,(a,b) in moves.items() if a==b}
    order = TopologicalSorter({k: [i for i in r if i>=0] for k,r in row.items()}).static_order()
    collapsed, result = {}, {}
    for j in order:
        value = rewrite(row[j], collapsed)
        if j in gone:
            collapsed[j] = value
        else:
            result[j] = value
    out = type(net)(first, initial, final, {k:ep for k,ep in moves.items() if k not in gone}, result)
    return transposed(out) if e['transposed'] else out
