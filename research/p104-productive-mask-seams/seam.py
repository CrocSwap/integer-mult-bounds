"""Exact finite-field witness for a fresh independent positive field at a fixed word cut."""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache

P = 65537
I = 256
assert I * I % P == P - 1


@cache
def gaussian(real, imag):
    def residue(q):
        f = Fraction(q)
        return f.numerator * pow(f.denominator, -1, P) % P
    return (residue(real) + I * residue(imag)) % P


def combine(terms, square):
    """Sum (row, coefficient, head shift, body XOR) terms in the character algebra."""
    result = {}
    for row, scale, head, body in terms:
        for (owner, phase, mask), coeff in row.items():
            total_phase = phase + head
            factor = square if (total_phase // 2) % 2 else 1
            key = (owner, total_phase % 2, mask ^ body)
            value = (result.get(key, 0) + coeff * scale * factor) % P
            if value:
                result[key] = value
            else:
                result.pop(key, None)
    return result


def apply(rows, event, square, transpose):
    op, *args = event
    if op.startswith("HOST_"):
        stage, *wires = args
        body = 1 << stage
        if op == "HOST_A":
            x, y, u, v = wires
            if transpose:
                y, x, v, u = wires
            rows[y] = combine([(rows[y], 1, 0, 0), (rows[x], 1, -1, 0)], square)
            rows[u] = combine([(rows[u], 1, 0, 0), (rows[v], -1, 1, 0)], square)
        elif op == "HOST_B":
            x, y = wires
            a, b = rows[x], rows[y]
            half = (P + 1) // 2
            if transpose:
                rows[x] = combine([(a, 1, 0, 0), (b, half, -1, 0)], square)
                rows[y] = combine([(b, half, 0, 0), (a, -1, 1, 0)], square)
            else:
                rows[x] = combine([(a, 1, 0, 0), (b, -1, 1, 0)], square)
                rows[y] = combine([(b, half, 0, 0), (a, half, -1, 0)], square)
        else:
            raise ValueError(op)
        for reg in wires:
            rows[reg] = combine([(rows[reg], 1, 0, body)], square)
        return
    reg, *data = args
    if op == "SWAP":
        other, = data
        rows[reg], rows[other] = rows[other], rows[reg]
    elif op in {"ADD", "QUERY"}:
        other, coefficient = data
        if transpose:
            reg, other = other, reg
        scale, head = (gaussian(*coefficient), 0) if op == "ADD" else (1, coefficient)
        rows[reg] = combine([(rows[reg], 1, 0, 0), (rows[other], scale, head, 0)], square)
    elif op == "SCALE":
        rows[reg] = combine([(rows[reg], gaussian(*data[0]), 0, 0)], square)
    elif op == "LAMBDA":
        # ((1+i*s)+(1-i*s)h^2)/2 at the chosen value of h^2.
        rows[reg] = combine([(rows[reg], 1 if square == 1 else I * data[0], 0, 0)], square)
    elif op in {"IDLE_ONE", "IDLE_ODD"}:
        mask = sum(1 << i for i in data[0])
        rows[reg] = combine([(rows[reg], 1, data[1] if op == "IDLE_ODD" else 0, mask)], square)
    else:
        raise ValueError(op)


def character_spaces(rows, group_by_owner, group_count):
    """For each duplicate pair and character, span the corresponding two-column row vectors."""
    spaces = [{} for _ in range(group_count)]
    for row in rows:
        entries = {}
        for (owner, phase, mask), value in row.items():
            group, idx = group_by_owner[owner]
            entries.setdefault((group, phase, mask), [0, 0])[idx] = value
        for (group, phase, mask), vec in entries.items():
            signature = (phase, mask)
            space = spaces[group]
            if signature not in space:
                space[signature] = tuple(vec)
            elif space[signature] is not None and determinant(space[signature], vec):
                space[signature] = None  # full two-dimensional row span
    return spaces


def determinant(a, b):
    return (a[0] * b[1] - a[1] * b[0]) % P


def support_directions(spaces):
    """A surviving input direction must kill coefficients of every unwanted character."""
    result = []
    for space in spaces:
        # Full stacked rank covers signatures that do not occur in this reduction.
        directions = list(space.values())
        assert None in directions or any(determinant(directions[0], v) for v in directions)
        eligible = {}
        for signature in space:
            first = None
            for other, vec in space.items():
                if other == signature:
                    continue
                if vec is None or (first is not None and determinant(first, vec)):
                    break
                first = vec
            else:
                eligible[signature] = None if first is None else (first[1], -first[0])
        result.append(eligible)
    return result


def trace(events, targets, group_by_owner, group_count, square, transpose):
    rows = [{(i, 0, 0): 1} for i in range(len(targets))]
    events = reversed(events) if transpose else events
    cuts = []
    for event in events:
        cuts.append(support_directions(character_spaces(rows, group_by_owner, group_count)))
        apply(rows, event, square, transpose)
    cuts.append(support_directions(character_spaces(rows, group_by_owner, group_count)))
    for owner, (phase, stages) in enumerate(targets):
        mask = sum(1 << j for j in stages)
        coeff = square if (phase // 2) % 2 else 1
        assert rows[owner] == {(owner, phase % 2, mask): coeff % P}, (owner, transpose, square)
    return cuts[::-1] if transpose else cuts


def paired_scan(events, targets, square):
    bags = defaultdict(list)
    for owner, (head, stages) in enumerate(targets):
        bags[head % 2, sum(1 << j for j in stages)].append(owner)
    groups = list(bags)
    assert all(len(pair) == 2 for pair in bags.values())
    index = {o: (g, i) for g, signature in enumerate(groups) for i, o in enumerate(bags[signature])}
    pre = trace(events, targets, index, len(groups), square, False)
    post = trace(events, targets, index, len(groups), square, True)
    eligible = []
    joint = 0
    for cut, (before, after) in enumerate(zip(pre, post, strict=True)):
        for group, (parity, full) in enumerate(groups):
            for (head, body), v in before[group].items():
                other = (parity ^ head, full ^ body)
                if other not in after[group]:
                    continue
                left = head + 8 * body.bit_count()
                right = other[0] + 8 * other[1].bit_count()
                if min(left, right) == 0:
                    continue
                joint += 1
                w = after[group][other]
                if v is None or w is None or sum(x*y for x, y in zip(v, w)) % P:
                    eligible.append([cut, group, left, right])
    return {"cuts": len(pre), "duplicate_target_pairs": len(groups), "cut_pair_tests": len(pre)*len(groups),
            "compatible_before_pairing": joint, "eligible": eligible}


def control():
    basis = [["ADD", 0, 1, ["1", "0"]], ["SCALE", 1, ["-2", "0"]], ["ADD", 1, 0, ["1", "0"]]]
    events = basis + [["IDLE_ODD", 0, [0], -1], ["IDLE_ODD", 1, [1], -1],
                      ["IDLE_ONE", 0, [1]], ["IDLE_ONE", 1, [0]]] + basis + [
                      ["SCALE", 0, ["1/2", "0"]], ["SCALE", 1, ["1/2", "0"]]]
    targets = [[-1, [0, 1]], [-1, [0, 1]]]
    at = len(basis) + 2
    run = paired_scan(events, targets, 1)
    assert run["eligible"].count([at, 0, 9, 8]) == 2
    faulty = events.copy()
    faulty[at] = ["IDLE_ONE", 0, [0]]
    try:
        paired_scan(faulty, targets, 1)
    except AssertionError:
        pass
    else:
        raise AssertionError("wrong complement passed")
    return {"basis_hidden_positive_at_cut": at, "accepted_rank_pairs": [[9, 8], [9, 8]],
            "wrong_complement_rejected": True}
