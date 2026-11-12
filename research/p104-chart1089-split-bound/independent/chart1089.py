"""Independent reverse bank inventory, modular prefix and exact pairing audit."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import isqrt
from pathlib import Path
from time import monotonic

P = 1000003
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PRICE = "3659931ae9d38e58629ad111c21a97e1e41175bf2e181c7084ed5645892cb146"
COHORT = "4c349e06b22bfebb431fab1c9ae04f0e798f398acc6fdd99591b49b1c95ef6ca"
CHART, PIVOT = 1089, 1081
CUTS = tuple(range(44588, 44600))


class Capped(Exception):
    pass


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def safe(deadline):
    if monotonic() >= deadline:
        raise Capped


def pinned(path, digest):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == digest, "changed pinned input " + path.name)
    return raw


def reverse_banks(word, deadline):
    n = word["public"]
    stock = word["final"].copy() + [None] * word["owned_fields"]
    out = {}
    events = word["program"]
    for t in range(len(events), CUTS[0] - 1, -1):
        if t % 128 == 0:
            safe(deadline)
        if t in CUTS:
            public = [r for r in range(n) if stock[r] == CHART]
            owned = [r for r in range(n, len(stock)) if stock[r] == CHART]
            require(PIVOT in public and 319 in public, "sealed affected bank does not match")
            out[t] = {"public": public, "owned": owned}
        if t == CUTS[0]:
            break
        op, r, *a = events[t - 1]
        if op == "MOVE":
            require(stock[r] == a[1] and a[2] == (r >= n), "reverse move chart or owner mismatch")
            stock[r] = a[0]
        elif op == "INIT":
            require(r >= n and stock[r] == a[0], "reverse INIT chart mismatch")
            stock[r] = None
        elif op == "CLEAR":
            require(r >= n and stock[r] is None, "reverse CLEAR chart mismatch")
            stock[r] = a[0]
        else:
            require(op in ("ADD", "SCALE", "COPY"), "unknown native op")
    return out


@cache
def rational(value):
    return Q(value)


@cache
def mod_coeff(value):
    q = rational(value)
    require(q.denominator % P, "observed nonunit denominator")
    return q.numerator * pow(q.denominator, -1, P) % P


def axpy(dst, src, c, mod):
    for j, x in src.items():
        value = dst.get(j, 0) + c * x
        if mod:
            value %= P
        if value:
            dst[j] = value
        else:
            dst.pop(j, None)


def scaled(row, c, mod):
    if mod:
        return {i: z for i, x in row.items() if (z := c * x % P)}
    return {i: z for i, x in row.items() if (z := c * x)}


def sparse_states(word, banks, deadline, reverse, mod):
    n = word["public"]
    one = 1 if mod else Q(1)
    rows = [{i: one} for i in range(n)] + [{} for _ in range(word["owned_fields"])]
    last, first = max(banks), min(banks)
    events = word["program"]
    cuts = range(len(events), first - 1, -1) if reverse else range(last + 1)
    saved = {}
    convert = mod_coeff if mod else rational
    for t in cuts:
        if t % 128 == 0:
            safe(deadline)
        if t in banks:
            saved[t] = [rows[r].copy() for r in banks[t]["public"]]
        if (reverse and t == first) or (not reverse and t == last):
            break
        op, d, *a = events[t - 1 if reverse else t]
        if op == "MOVE":
            continue
        if op in ("INIT", "CLEAR"):
            rows[d] = {}
            continue
        coeff = convert(a[-2])
        if op == "SCALE":
            rows[d] = scaled(rows[d], coeff, mod)
        elif reverse:
            axpy(rows[a[0]], rows[d], coeff, mod)
            if op == "COPY":
                rows[d] = {}
        elif op == "COPY":
            rows[d] = scaled(rows[a[0]], coeff, mod)
        else:
            require(op == "ADD", "unknown scalar operation")
            axpy(rows[d], rows[a[0]], coeff, mod)
    return saved


def modulo_witness(rows, allowed):
    pivots = {}
    for original in rows:
        row = {i: x for i, x in original.items() if i not in allowed}
        while row:
            j = max(row)
            if j not in pivots:
                pivots[j] = scaled(row, pow(row[j], -1, P), True)
                break
            axpy(row, pivots[j], -row[j], True)
    columns = sorted(pivots)
    if len(columns) != len(rows):
        return len(columns), columns, None
    dense = [[row.get(j, 0) for j in columns] for row in rows]
    det = 1
    for j in range(len(dense)):
        r = next(i for i in range(j, len(dense)) if dense[i][j])
        if r != j:
            dense[r], dense[j] = dense[j], dense[r]
            det = -det
        value = dense[j][j]
        det = (det * value) % P
        inverse = pow(value, -1, P)
        for k in range(j + 1, len(dense)):
            multiplier = dense[k][j] * inverse % P
            dense[k] = [(a - multiplier * b) % P for a, b in zip(dense[k], dense[j], strict=True)]
    require(det, "zero modular minor")
    return len(columns), columns, det


def kernel(matrix, n):
    """Dense rational RREF on transposed exterior constraints."""
    matrix = [r.copy() for r in matrix if any(r)]
    pivots = []
    for j in range(n):
        head = len(pivots)
        pivot = next((i for i in range(head, len(matrix)) if matrix[i][j]), None)
        if pivot is None:
            continue
        matrix[head], matrix[pivot] = matrix[pivot], matrix[head]
        a = matrix[head][j]
        matrix[head] = [x / a for x in matrix[head]]
        for i, row in enumerate(matrix):
            if i != head and row[j]:
                a = row[j]
                matrix[i] = [x - a * y for x, y in zip(row, matrix[head], strict=True)]
        pivots.append(j)
    basis = []
    for j in range(n):
        if j not in pivots:
            v = [Q(i == j) for i in range(n)]
            for i, col in enumerate(pivots):
                v[col] = -matrix[i][j]
            basis.append(v)
    return basis


def linear(rows, weights):
    target = {}
    for row, a in zip(rows, weights, strict=True):
        if a:
            axpy(target, row, a, False)
    return target


def pure(rows, allowed):
    outside = sorted(set().union(*(row.keys() for row in rows)) - allowed)
    exterior = [[row.get(j, Q(0)) for row in rows] for j in outside]
    basis = kernel(exterior, len(rows))
    return [(v, linear(rows, v)) for v in basis]


def dot(a, b):
    return sum((x * y for x, y in zip(a, b, strict=True)), Q(0))


def dot_sparse(a, b):
    return sum((x * b.get(i, 0) for i, x in a.items()), Q(0))


def bilinear(A, D):
    """Exact witness for xAy=1, xDy=0, or proof none exists."""
    n, m = len(A), len(A[0])
    choices = [[Q(i == j) for i in range(n)] for j in range(n)]
    candidates = choices + [[a + b for a, b in zip(choices[i], choices[j], strict=True)]
                            for i in range(n) for j in range(i)]
    candidates += kernel([[row[j] for row in D] for j in range(m)], n)
    for x in candidates:
        c = [dot(x, [r[j] for r in A]) for j in range(m)]
        d = [dot(x, [r[j] for r in D]) for j in range(m)]
        y = [Q(0)] * m
        if not any(d):
            j = next((j for j, a in enumerate(c) if a), None)
            if j is None:
                continue
            y[j] = 1 / c[j]
        else:
            i = next(j for j, a in enumerate(d) if a)
            j = next((j for j in range(m) if c[i] * d[j] != c[j] * d[i]), None)
            if j is None:
                continue
            det = c[i] * d[j] - c[j] * d[i]
            y[i], y[j] = d[j] / det, -d[i] / det
        require(dot(c, y) == 1 and not dot(d, y), "invalid bilinear certificate")
        return x, y
    return None


def pairing(before, after, allowed, bank):
    F, R = pure(before, allowed), pure(after, allowed)
    outcome = {"prefix_nullity": len(F), "suffix_nullity": len(R)}
    if not any(c for _, c in F):
        return outcome | {"status": "no_nonzero_pure_prefix_exact"}
    if not any(d for _, d in R):
        return outcome | {"status": "no_nonzero_pure_suffix"}
    A = [[dot_sparse(c, d) for _, d in R] for _, c in F]
    D = [[dot(a, b) - dot_sparse(c, d) for b, d in R] for a, c in F]
    pair = bilinear(A, D)
    if pair is None:
        return outcome | {"status": "no_unit_pairing", "image_pairing": [[str(x) for x in row] for row in A],
                          "local_minus_image": [[str(x) for x in row] for row in D]}
    x, y = pair
    a = linear([dict(zip(bank, row, strict=True)) for row, _ in F], x)
    b = linear([dict(zip(bank, row, strict=True)) for row, _ in R], y)
    c = linear([r for _, r in F], x)
    d = linear([r for _, r in R], y)
    require(dot_sparse(a, b) == dot_sparse(c, d) == 1, "wrong final unit pair")
    return outcome | {"status": "exact_paired_support", "witness": {
        k: {r: str(v) for r, v in row.items()} for k, row in zip("abcd", [a, b, c, d], strict=True)}}


def controls():
    require(P > 2 and all(P % i for i in range(2, isqrt(P) + 1)), "nonprime modulus")
    require(modulo_witness([{2: 1, 3: 2}, {2: 4, 3: 5}], set())[-1] == P - 3, "minor control")
    require(modulo_witness([{2: 1}, {2: 4}], set())[-1] is None, "modular loss control")
    yes = pairing([{1: Q(1)}], [{1: Q(1)}], {1}, [0])
    no = pairing([{1: Q(1)}], [{2: Q(1)}], {1, 2}, [0])
    require(yes["status"] == "exact_paired_support" and no["status"] == "no_unit_pairing", "unit controls")
    return ["full exterior modular minor", "modular loss requires exact fallback", "true unit pair", "pure unpaired rows"]


def main(args):
    tests = controls()
    price = loads(pinned(args.price, PRICE))
    cohort = loads(pinned(args.cohort, COHORT))
    keys = [[t, CHART, PIVOT] for t in CUTS]
    require(price["stock"] == keys and price["head"] == cohort["head"] == HEAD, "wrong frozen stock")
    allowed = set(cohort["endpoint_cohort"])
    require(len(allowed) == 615 and PIVOT in allowed and 319 not in allowed, "wrong endpoint cohort")
    start = monotonic()
    word = loads(decompress(pinned(args.word, WORD)))
    outcomes = {}
    try:
        bank = reverse_banks(word, start + 20)
        prefix = sparse_states(word, bank, start + 20, reverse=False, mod=True)
        for t in CUTS:
            safe(start + 20)
            rank, columns, det = modulo_witness(prefix[t], allowed)
            status = "no_nonzero_pure_prefix_modular_minor" if det is not None else "exact_pairing_needed"
            outcomes[t] = {"key": [t, CHART, PIVOT], "bank": bank[t], "prefix_modular_rank": rank,
                           "exterior_minor_columns": columns, "exterior_minor_det_mod_p": det, "status": status}
    except Capped:
        pass
    exact = {t: r["bank"] for t, r in outcomes.items() if r["status"] == "exact_pairing_needed"}
    if exact:
        deadline = monotonic() + 35
        try:
            a = sparse_states(word, exact, deadline, reverse=False, mod=False)
            b = sparse_states(word, exact, deadline, reverse=True, mod=False)
            for t in sorted(exact):
                safe(deadline)
                outcomes[t].update(pairing(a[t], b[t], allowed, exact[t]["public"]))
        except Capped:
            pass
    rows = [outcomes[t] for t in sorted(outcomes)]
    unvisited = [k for k in keys if k[0] not in outcomes or outcomes[k[0]]["status"] == "exact_pairing_needed"]
    print(dumps({
        "head": HEAD, "word_sha256": WORD, "price_sha256": PRICE, "cohort_sha256": COHORT,
        "stock": len(keys), "prime": P, "prefix_seconds": 20, "paired_seconds": 35,
        "observed_scalar_denominators_invertible": True, "allowed_boundary_count": len(allowed),
        "controls": tests, "rows": rows, "unvisited": unvisited,
        "survivors": [r for r in rows if r["status"] == "exact_paired_support"],
        "dispositions": dict(Counter(r["status"] for r in rows)),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = ArgumentParser()
    for name in ("price", "cohort", "word"):
        parser.add_argument("--" + name, type=Path, required=True)
    main(parser.parse_args())
