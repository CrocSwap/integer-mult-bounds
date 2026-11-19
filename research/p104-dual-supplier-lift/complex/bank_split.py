"""Rebuild a P104 graph from the published PR 7756 graph and a bank split journal."""
from fractions import Fraction
from graphlib import TopologicalSorter


def add(row, other, scale):
    for key, value in other.items():
        result = row.get(key, 0) + scale * value
        if result:
            row[key] = result
        else:
            row.pop(key, None)


def rewrite(row, replacements):
    changed = row.keys() & replacements.keys()
    if not changed:
        return row
    result = {i: value for i, value in row.items() if i not in changed}
    for i in changed:
        add(result, replacements[i], row[i])
    return result


def rotation(slots, encoded_rows):
    rows = {key: {key: Fraction(1)} for key in slots}
    for key, terms in encoded_rows:
        rows[key] = {i: Fraction(value) for i, value in terms}
    # Apply the same row operations to the unit matrix to get the inverse.
    reduced = {k: row.copy() for k, row in rows.items()}
    inverse = {key: {key: Fraction(1)} for key in slots}
    for i, key in enumerate(slots):
        pivot = next(j for j in slots[i:] if key in reduced[j])
        for matrix in (reduced, inverse):
            matrix[key], matrix[pivot] = matrix[pivot], matrix[key]
        factor = reduced[key][key]
        for matrix in (reduced, inverse):
            matrix[key] = {j: x / factor for j, x in matrix[key].items()}
        for other in slots:
            if other == key or key not in reduced[other]:
                continue
            factor = -reduced[other][key]
            for matrix in (reduced, inverse):
                add(matrix[other], matrix[key], factor)
    assert all(reduced[k] == {k: 1} for k in slots)
    return rows, inverse


def apply(net, event):
    Network = type(net)
    first = net.first_output
    old, new = event['old'], event['new']
    arrivals, sends = set(event['arrivals']), set(event['sends'])
    rotated, inverse = {}, {}
    for block in event['rotations']:
        slots = block['slots']
        assert len({net.moves[k] for k in slots}) == 1
        direct, back = rotation(slots, block['rows'])
        rotated.update(direct)
        inverse.update(back)
    rows = {}
    for j, row in net.forms.items():
        if j in rotated:
            row = {}
            for i, q in rotated[j].items():
                add(row, net.forms[i], q)
        rows[j] = rewrite(row, inverse)
    initial, final, moves = net.initial[:], net.final[:], net.moves.copy()
    for k in arrivals:
        if k < 0:
            assert initial[~k] == old
            initial[~k] = new
        else:
            sender, receiver = moves[k]
            assert receiver == old
            moves[k] = sender, new
    for j in sends:
        if j >= first:
            assert final[j-first] == old
            final[j-first] = new
        else:
            sender, receiver = moves[j]
            assert sender == old
            moves[j] = new, receiver
    generator = event['crossing_generator']
    key = None
    if generator is not None:
        key, = event['new_paid']
        assert key not in moves
        direction = generator in sends
        source = {i: q for i, q in rows[generator].items() if (i in arrivals) != direction}
        assert source
        moves[key] = (old, new) if direction else (new, old)
        pivot = min(source)
    for j, row in list(rows.items()):
        owner = net.moves[j][0] if j < first else net.final[j-first]
        if owner != old:
            continue
        crossing = {i: q for i, q in row.items() if (i in arrivals) != (j in sends)}
        if not crossing:
            continue
        assert key is not None and (j in sends) == direction
        q = crossing[pivot] / source[pivot]
        assert crossing == {i: q * a for i, a in source.items()}
        rows[j] = {i: a for i, a in row.items() if i not in crossing}
        rows[j][key] = q
    if key is not None:
        rows[key] = source
    gone = {k for k, (a, b) in moves.items() if a == b}
    assert gone == set(event['removed_paid'])
    order = TopologicalSorter({k: [i for i in row if i >= 0] for k, row in rows.items()}).static_order()
    collapse, output = {}, {}
    for j in order:
        row = rewrite(rows[j], collapse)
        if j in gone:
            collapse[j] = row
        else:
            output[j] = row
    return Network(first, initial, final, {k: ab for k, ab in moves.items() if k not in gone}, output)
