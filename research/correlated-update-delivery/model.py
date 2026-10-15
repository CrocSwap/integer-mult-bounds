"""Exact correlated-update delivery model. Adam Gall / OpenAI Codex, Apache-2.0."""
from fractions import Fraction


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def validate(vectors, dimension, b, a, correction):
    k = len(b)
    require(k >= 1 and dimension >= 0, "empty requests or negative dimension")
    require(len(a) == k and len(vectors) == len(correction) == k - 1, "shape")
    require(all(type(v) is int and 0 <= v < 1 << dimension for v in vectors), "update vector")
    require(all(Fraction(c) > 0 for c in (*b, *a, *correction)), "nonpositive complete price")


def optimum(vectors, dimension, b, a, correction):
    """State bit 0 is B parity; higher bits are initial-update coefficients."""
    validate(vectors, dimension, b, a, correction)
    states = {0: (Fraction(0), (), ())}
    prefix = 0
    for i, price in enumerate(b):
        after_query = {}
        for state, (cost, qword, tword) in states.items():
            for q in (0, 1):
                target = state ^ ((1 | (prefix << 1)) if q else 0)
                candidate = (cost + Fraction(price) * (2 - q), qword + (q,), tword)
                if target not in after_query or candidate < after_query[target]:
                    after_query[target] = candidate
        states = after_query
        if i < len(vectors):
            after_cut = {}
            for state, (cost, qword, tword) in states.items():
                for t in (0, 1):
                    target = state ^ ((vectors[i] << 1) if t else 0)
                    candidate = (cost + Fraction(correction[i]) * t, qword, tword + (t,))
                    if target not in after_cut or candidate < after_cut[target]:
                        after_cut[target] = candidate
            states = after_cut
            prefix ^= vectors[i]
    cost, qword, tword = states[0]
    return cost + 2 * sum(map(Fraction, a)), qword, tword


def coherent_optimum(vectors, b, a, correction):
    """Strengthened comparator requiring z=z0+p*B*x at each next request."""
    states = {0: (Fraction(0), (), ())}
    for i, price in enumerate(b):
        nxt = {}
        for p, (cost, qword, tword) in states.items():
            for q in (0, 1):
                outgoing = p ^ q
                t = outgoing if i < len(vectors) and vectors[i] else 0
                candidate = (cost + Fraction(price) * (2 - q)
                             + (Fraction(correction[i]) * t if i < len(vectors) else 0),
                             qword + (q,), tword + ((t,) if i < len(vectors) else ()))
                if outgoing not in nxt or candidate < nxt[outgoing]:
                    nxt[outgoing] = candidate
        states = nxt
    cost, qword, tword = states[0]
    return cost + 2 * sum(map(Fraction, a)), qword, tword


def word(qword, tword):
    require(len(tword) == len(qword) - 1, "parity word shape")
    result = []
    for i, q in enumerate(qword):
        require(q in (0, 1), "query parity")
        result.extend((("A", i), ("B", i), ("A", i)))
        if not q:
            result.append(("B", i))
        result.append(("deliver", i))
        if i < len(tword):
            require(tword[i] in (0, 1), "correction parity")
            result.append(("M", i))
            if tword[i]:
                result.append(("D", i))
    return tuple(result)


def apply(matrix, vector):
    result = []
    for row in matrix:
        value = 0
        for j, entry in enumerate(vector):
            if row >> j & 1:
                value ^= entry
        result.append(value)
    return result


def multiply(left, right):
    return tuple(apply(left, right))


def layout(n, width, m, out_width, dimension, k):
    x = tuple(range(n))
    updates = tuple(tuple(range(n + j * width, n + (j + 1) * width)) for j in range(dimension))
    z_start = n + width * dimension
    z = tuple(range(z_start, z_start + m))
    y_start = z_start + m
    y = tuple(tuple(range(y_start + i * out_width, y_start + (i + 1) * out_width)) for i in range(k))
    return x, updates, z, y, y_start + k * out_width


def replay(events, vectors, dimension, B, C, readers, update_width):
    """Literal formal-column maps; checks every chronological delivery and dirt."""
    n, m, k, out_width = len(C), len(B), len(readers), len(readers[0])
    xids, uids, zids, yids, total = layout(n, update_width, m, out_width, dimension, k)
    initial = [1 << j for j in range(total)]
    rows = initial.copy()
    expected_x = [initial[j] for j in xids]
    epoch, phase = 0, "request"
    gates = []
    cuts = []
    BC = multiply(B, C)

    def emit(matrix, sources, targets):
        for target, mask in zip(targets, matrix):
            for bit, source in enumerate(sources):
                if mask >> bit & 1:
                    rows[target] ^= rows[source]
                    gates.append((source, target))

    for kind, i in events:
        if kind == "D":
            require(phase == "cut" and i == epoch - 1, "correction outside its cut")
            for j, sources in enumerate(uids):
                if vectors[i] >> j & 1:
                    emit(BC, sources, zids)
            continue
        require(i == epoch and epoch < k, "write outside active request")
        if kind in ("A", "B"):
            require(phase in ("request", "cut"), "query before imposed mutation")
            phase = "request"
            if kind == "A":
                emit(readers[i], zids, yids[i])
            else:
                emit(B, xids, zids)
        elif kind == "deliver":
            require(phase == "request", "delivery outside request")
            increment = apply(readers[i], apply(B, expected_x))
            require([rows[j] for j in yids[i]] == [initial[j] ^ v for j, v in zip(yids[i], increment)], "incorrect delivered output")
            require([rows[j] for j in xids] == expected_x, "incorrect source at delivery")
            cuts.append((len(gates), i))
            phase = "finished" if i == k - 1 else "mutation"
            if i == k - 1:
                epoch += 1
        elif kind == "M":
            require(phase == "mutation" and i < k - 1, "misplaced or repeated mutation")
            for j, sources in enumerate(uids):
                if vectors[i] >> j & 1:
                    emit(C, sources, xids)
                    delta = apply(C, [initial[q] for q in sources])
                    expected_x = [x ^ dx for x, dx in zip(expected_x, delta)]
            phase = "cut"
            epoch += 1
        else:
            raise Invalid("unknown operation")
    require(epoch == k and phase == "finished", "missing delivery")
    require([rows[j] for j in zids] == [initial[j] for j in zids], "unrestored dirty connector")
    require(all(rows[q] == initial[q] for group in uids for q in group), "changed update row")
    return {"matrix": rows, "gates": gates, "cuts": cuts, "bits": total,
            "xor": len(gates), "reads": 2 * len(gates), "writes": len(gates),
            "dispatch_records": len(gates),
            "head_steps": sum(2 * (max(s, t) + 1) for s, t in gates)}
