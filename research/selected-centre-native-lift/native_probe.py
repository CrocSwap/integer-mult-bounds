"""Literal native stream probe using unpacked Gaussian-dyadic statevectors.

This is one exact engineered input, not an all-input native replay. The rank
proof uses the all-column recipe checks and conjugation lemma in verify.py.
Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
import hashlib
import json

DIM = 512
ZERO = ((), (), 0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def reduced(re, im, exponent):
    bits = 0
    for x in re:
        bits |= abs(x)
    for x in im:
        bits |= abs(x)
    if bits == 0:
        return ZERO
    shift = min(exponent, (bits & -bits).bit_length()-1)
    if shift:
        re = [x >> shift for x in re]
        im = [x >> shift for x in im]
    return tuple(re), tuple(im), exponent-shift


def scale(vec, q):
    q = Fraction(q)
    need(q.denominator & (q.denominator-1) == 0, "dyadic coefficient")
    if not vec[0] or not q:
        return ZERO
    return reduced([q.numerator*x for x in vec[0]], [q.numerator*x for x in vec[1]],
                   vec[2]+q.denominator.bit_length()-1)


def add(a, b, q):
    b = scale(b, q)
    if not b[0]:
        return a
    if not a[0]:
        return b
    e = max(a[2], b[2])
    return reduced([(x << (e-a[2]))+(y << (e-b[2])) for x, y in zip(a[0], b[0])],
                   [(x << (e-a[2]))+(y << (e-b[2])) for x, y in zip(a[1], b[1])], e)


def translate_root(vec, q, sign=1):
    if not vec[0]:
        return vec
    a, b, e = vec
    need(sign in (-1, 1), "root orientation")
    re = [a[x]-sign*b[x]+a[x ^ q]+sign*b[x ^ q] for x in range(DIM)]
    im = [b[x]+sign*a[x]+b[x ^ q]-sign*a[x ^ q] for x in range(DIM)]
    return reduced(re, im, e+1)


def fourier(vec, rank):
    for j in range(rank):
        vec = translate_root(vec, 1 << j)
    return vec


def phase(a, b, p):
    return ((a, b), (-b, a), (-a, -b), (b, -a))[p % 4]


def apply_table(vec, table):
    if not vec[0]:
        return vec
    re, im = [0]*DIM, [0]*DIM
    for x, (y, p) in enumerate(table):
        re[y], im[y] = phase(vec[0][x], vec[1][x], p)
    return tuple(re), tuple(im), vec[2]


def monomial_table(rec, inverse=False):
    table = []
    for x in range(DIM):
        y = sum(((row & x).bit_count() % 2) << i for i, row in enumerate(rec["matrix_rows"]))
        p = rec["phase"] + sum(a for i, a in enumerate(rec["linear_Z4"]) if x >> i & 1)
        p += 2*sum((rec["quadratic_rows"][i] >> j) & 1 for i in range(9)
                   for j in range(i+1, 9) if (x >> i & 1) and (x >> j & 1))
        table.append((y ^ rec["offset"], p % 4))
    need(len({y for y, _ in table}) == DIM, "probe monomial invertibility")
    if inverse:
        answer = [None]*DIM
        for x, (y, p) in enumerate(table):
            answer[y] = (x, -p % 4)
        return answer
    return table


def circuit(vec, gates):
    """Independent statevector semantics for the expected canonical centre."""
    for gate in gates:
        tag = gate[0]
        if tag == "C":
            vec = translate_root(vec, gate[1], gate[2])
        elif tag == "P":
            table = [(sum(((r & x).bit_count() % 2) << i for i, r in enumerate(gate[1])), 0)
                     for x in range(DIM)]
            vec = apply_table(vec, table)
        elif tag == "D":
            Q, linear = gate[1:]
            table = []
            for x in range(DIM):
                p = sum(a for i, a in enumerate(linear) if x >> i & 1)
                p += 2*sum((Q[i] >> j) & 1 for i in range(9) for j in range(i+1, 9)
                           if (x >> i & 1) and (x >> j & 1))
                table.append((x, p % 4))
            vec = apply_table(vec, table)
        elif tag == "X":
            vec = apply_table(vec, [(x ^ gate[1], 0) for x in range(DIM)])
        elif tag == "PH":
            vec = apply_table(vec, [(x, gate[1]) for x in range(DIM)])
        else:
            raise ValueError("probe gate")
    return vec


def probe(word, events, recipes, residuals, pivots, pinv, scatter, target_ids, C):
    basis = (tuple([1]+[0]*(DIM-1)), tuple([0]*DIM), 0)
    normalized = {j: scale(basis, pinv[k][0]) for k, j in enumerate(pivots)}
    rows = {("L", i): ZERO for i in range(704)}
    for j in pivots:
        rows["L", j] = translate_root(normalized[j], word["ports"][j])
    source_hash = hashlib.sha256(json.dumps([rows["L", j] for j in pivots]).encode()).hexdigest()
    children = {(r["old"], r["new"]): r for r in recipes["children"]}
    adapters = {(r["role"], r["port"]): r for r in recipes["endpoint_adapters"]}
    tables = {}

    def monomial(vec, rec, inverse=False):
        if not vec[0]:
            return vec
        key = (json.dumps(rec, sort_keys=True), inverse)
        if key not in tables:
            tables[key] = monomial_table(rec, inverse)
        return apply_table(vec, tables[key])

    def child(vec, a, b):
        rec = children[a, b]
        return monomial(fourier(monomial(vec, rec["right"]), rec["rank"]), rec["left"])

    for event in events:
        tag = event[0]
        if tag == "phase":
            if event[1] == "centers":
                for k, carrier in enumerate(word["centers"]):
                    expected = circuit(basis, C.canonical_frame(word["frames"][word["center_frames"][k]])) if k == 0 else ZERO
                    need(rows["L", carrier] == expected, "direct native centre input")
                need(all(rows["L", i] == ZERO for i in range(112, 224)), "direct target pre-cut")
            if event[1] == "B":
                expected = {i: scale(basis, row[0]) for i, row in zip(target_ids, scatter)}
                need(all(rows["L", i] == expected.get(i, ZERO) for i in range(112, 224)),
                     "direct native scatter")
        elif tag == "climb":
            _, _, r, a, b, _ = event
            rows["L", r] = child(rows["L", r], a, b)
        elif tag == "center":
            _, k, a, b, _ = event
            rows["C", k] = child(rows["C", k], a, b)
        elif tag == "adapter":
            _, direction, r, _ = event
            if direction == "old_to_new" and r < 112:
                rows["L", r] = monomial(rows["L", r], adapters["source", r]["left"])
            elif direction == "new_to_old" and 112 <= r < 224:
                rows["L", r] = monomial(rows["L", r], adapters["target", r-112]["left"], True)
        elif tag == "residual_adapter":
            direction, r, a = event[1:4]
            b = event[4] if len(event) == 5 else 1
            rec = residuals["recipes"][str(a) if b == 1 else f"{a}:{b}"]
            rows["L", r] = monomial(rows["L", r], rec["right" if direction == "pre" else "left"], True)
        elif tag == "scalar":
            op = event[1]
            kind, dest = op[0], tuple(op[1])
            if kind == "clear":
                rows[dest] = ZERO
            elif kind == "copy":
                rows[dest] = rows[tuple(op[2])]
            elif kind == "scale":
                rows[dest] = scale(rows[dest], Fraction(op[2], op[3]))
            elif kind == "add":
                rows[dest] = add(rows[dest], rows[tuple(op[2])], Fraction(op[3], op[4]))
            else:
                raise ValueError("probe scalar")
        else:
            raise ValueError("probe event")
    for i in range(704):
        if i < 112:
            expected = fourier(normalized.get(i, ZERO), 9)
        elif i < 224:
            expected = fourier(translate_root(normalized.get(i-112, ZERO), word["ports"][i-112], -1), 9)
        else:
            expected = ZERO
        need(rows["L", i] == expected, "direct native complete endpoint")
    need(all(not vec[0] for role, vec in rows.items() if role[0] == "C"), "direct native private exit")
    return {"engine": "unpacked Gaussian-dyadic literal stream", "events": len(events),
            "inputs": "one encoded centre-basis vector, v=address basis0; every other input zero",
            "source_sha256": source_hash, "ordinary_endpoint_amplitudes": 704*DIM,
            "centre_values_checked": 8*DIM, "scatter_values_checked": 112*DIM,
            "source_to_helper_response": "zero", "private_exit": "zero"}
