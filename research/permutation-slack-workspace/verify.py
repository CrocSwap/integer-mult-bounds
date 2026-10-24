#!/usr/bin/env python3
"""Exact finite controls for the permutation spectator-slack proof.

Nick Petalas. Apache-2.0.
"""
import argparse
from hashlib import sha256
from itertools import permutations, product
import json
from math import factorial
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rank(rows, q):
    if not rows:
        return 0
    a, r = [list(row) for row in rows], 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][col] % q), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        z = pow(a[r][col] % q, -1, q)
        a[r] = [(z * x) % q for x in a[r]]
        for i in range(r + 1, len(a)):
            if a[i][col] % q:
                z = a[i][col] % q
                a[i] = [(x - z * y) % q for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def mul(a, b, q):
    out = [[0] * len(b[0]) for _ in a]
    for i, row in enumerate(a):
        for k, z in enumerate(row):
            if z:
                out[i] = [(x + z * y) % q for x, y in zip(out[i], b[k])]
    return out


def inv(a, q):
    n = len(a)
    b = [list(row) + tail for row, tail in zip(a, eye(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if b[i][j] % q), None)
        require(pivot is not None, "singular scalar basis")
        b[j], b[pivot] = b[pivot], b[j]
        z = pow(b[j][j] % q, -1, q)
        b[j] = [(z*x) % q for x in b[j]]
        for i in range(n):
            if i != j:
                z = b[i][j]
                b[i] = [(x-z*y) % q for x, y in zip(b[i], b[j])]
    return [row[n:] for row in b]


def matvec(a, u, q):
    return tuple(sum(x*y for x, y in zip(row, u)) % q for row in a)


def inverse_perm(g):
    return tuple(g.index(i) for i in range(len(g)))


def compose(g, h):
    return tuple(g[h[i]] for i in range(len(g)))


def inversions(g):
    return sum(g[i] > g[j] for i in range(len(g)) for j in range(i + 1, len(g)))


def projectors(r, q):
    out = []
    for u in product(range(q), repeat=r):
        if not any(u) or next(x for x in u if x) != 1:
            continue
        for v in product(range(q), repeat=r):
            if sum(x * y for x, y in zip(u, v)) % q == 1:
                out.append((u, v))
    return out


def pairs(n):
    return [(i, j) for i in range(n) for j in range(n) if i != j]


def gate(g, u, v, q, regular=False):
    n, r = len(g), len(u)
    require(2 <= n <= 5 and 1 <= r <= 6 and len(v) == r, "gate dimensions")
    require(q in (2, 3, 5), "unsupported finite field")
    require(sorted(g) == list(range(n)), "illegal permutation")
    require(sum(x * y for x, y in zip(u, v)) % q == 1, "not an idempotent")
    domain = list(permutations(range(n))) if regular else pairs(n)
    index, d = {a: i for i, a in enumerate(domain)}, len(domain)
    a = eye(r * d)
    for j in range(r):
        for k, address in enumerate(domain):
            target = compose(g, address) if regular else (g[address[0]], g[address[1]])
            t = index[target]
            for i in range(r):
                z = u[i] * v[j]
                a[i*d+t][j*d+k] = (a[i*d+t][j*d+k] + z) % q
                a[i*d+k][j*d+k] = (a[i*d+k][j*d+k] - z) % q
    return a


def crossing(a, n, r, q):
    domain = pairs(n)
    h = [i for i, (x, y) in enumerate(domain) if x < y]
    k = [i for i, (x, y) in enumerate(domain) if x > y]
    d = len(domain)
    return rank([[a[i*d+x][j*d+y] for j in range(r) for y in h]
                 for i in range(r) for x in k], q)


def active_map(d, seed, q):
    a, rng = eye(d), random.Random(seed)
    for _ in range(3 * d):
        i, j = rng.sample(range(d), 2)
        a[i] = [(x + y) % q for x, y in zip(a[i], a[j])]
    require(rank(a, q) == d, "active map must be invertible")
    return a


def local_controls():
    counts, hist = {}, {}
    domains = [(2, 3, 2, 4), (3, 3, 2, 4), (4, 3, 2, 3),
               (3, 3, 3, 3), (4, 2, 3, 2), (5, 2, 2, 1)]
    for n, r, q, samples in domains:
        d, total = n * (n - 1), 0
        active = [active_map(d, 100*n+s, q) for s in range(samples)]
        for g in permutations(range(n)):
            length = inversions(g)
            if not length:
                continue
            for u, v in projectors(r, q):
                peel = gate(inverse_perm(g), u, v, q)
                for a in active:
                    p = eye(r * d)
                    for i in range(d):
                        p[i][:d] = a[i]
                    before, after = crossing(p, n, r, q), crossing(mul(p, peel, q), n, r, q)
                    eta = int(any(u[1:])) + int(any(v[1:]))
                    require(length * eta <= length + after - before, "local charge")
                    key = f"d={length},eta={eta},delta={after-before}"
                    hist[key] = hist.get(key, 0) + 1
                    total += 1
        require(total == (factorial(n)-1)*((q**r-1)//(q-1))*q**(r-1)*samples,
                "local domain coverage")
        counts[f"S{n}/F{q}/roles{r}"] = total
    return {"domains": counts, "peels": sum(counts.values()), "histogram": hist}


def decomposition(g, u, v, q):
    n, r = len(g), len(u)
    domain, h = pairs(n), [(i, j) for i in range(n) for j in range(i+1, n)]
    index, d = {x: i for i, x in enumerate(domain)}, len(domain)
    image = {(g[x], g[y]) for x, y in h}
    common, cross_h, cross_k = sorted(set(h) & image), sorted(set(h)-image), sorted(image-set(h))
    require(len(cross_h) == len(cross_k) == inversions(g), "crossing sets")
    a = gate(g, u, v, q)
    actual = [[a[i][j*d+index[x]] for i in range(r*d)] for j in range(r) for x in h]
    expected = [[int(i == j*d+index[x]) for i in range(r*d)]
                for j in range(r) for x in common]
    pivot = next(i for i in range(r) if v[i])
    for j in range(r):
        if j == pivot:
            continue
        z = (-v[j] * pow(v[pivot], -1, q)) % q
        for x in cross_h:
            expected.append([(int(i == j*d+index[x]) + z*int(i == pivot*d+index[x])) % q
                             for i in range(r*d)])
    for x in cross_k:
        expected.append([u[i//d] * int(i % d == index[x]) for i in range(r*d)])
    target = r * len(h)
    require(rank(expected, q) == target, "decomposition dimension")
    require(rank(actual + expected, q) == target, "literal GH decomposition")


def subspace_controls():
    count = 0
    for n, r, q in [(3, 3, 2), (4, 2, 3), (5, 1, 5)]:
        for g in permutations(range(n)):
            for u, v in projectors(r, q):
                decomposition(g, u, v, q)
                count += 1
    return count


def formal_product(word, n, r, q):
    result = {tuple(range(n)): eye(r)}
    for g, u, v in word:
        nxt = {}
        for h, a in result.items():
            au = [sum(a[i][j] * u[j] for j in range(r)) % q for i in range(r)]
            for label, sign in ((h, -1), (compose(h, g), 1)):
                out = nxt.setdefault(label, [[0] * r for _ in range(r)])
                for i in range(r):
                    for j in range(r):
                        out[i][j] = (out[i][j] + sign * au[i] * v[j]) % q
            out = nxt.setdefault(h, [[0] * r for _ in range(r)])
            for i in range(r):
                for j in range(r):
                    out[i][j] = (out[i][j] + a[i][j]) % q
        result = {g: a for g, a in nxt.items() if any(any(row) for row in a)}
    return result


def split_basis(a, b, q):
    s, kept = len(a), []
    if any(a):
        kept.append(a)
    if any(b) and (not any(a) or sum(x*y for x, y in zip(a, b)) % q == 0):
        j = next(i for i in range(s) if b[i])
        kept.append(tuple(int(i == j) for i in range(s)))
    columns = list(kept)
    for x in product(range(q), repeat=s):
        if sum(z*y for z, y in zip(x, b)) % q == 0 and rank(columns+[x], q) > len(columns):
            columns.append(x)
    require(len(columns) == s, "spectator split spans")
    return [list(row) for row in zip(*columns)], len(kept)


def transform(word, basis, q):
    bi = inv(basis, q)
    return [(g, matvec(bi, u, q), matvec(list(zip(*basis)), v, q)) for g, u, v in word]


def represented_word(word, n, r, q):
    result = eye(r*n*(n-1))
    for g, u, v in word:
        result = mul(result, gate(g, u, v, q), q)
    return result


def compress(word, n, w, q):
    r, original_w = len(word[0][1]), w
    basis, work, charges = eye(r), word, []
    endpoint_rank = crossing(represented_word(word, n, r, q), n, r, q)
    for end in range(len(word), 0, -1):
        g, u, v = work[end-1]
        residual = formal_product(work[:end], n, r, q)
        for h, matrix in residual.items():
            for i in range(r):
                for j in range(r):
                    if i >= w or j >= w:
                        require(matrix[i][j] == int(h == tuple(range(n)) and i == j),
                                "residual must restore every current spectator")
        before = crossing(represented_word(work[:end], n, r, q), n, r, q)
        after = crossing(represented_word(work[:end-1], n, r, q), n, r, q)
        eta, d = int(any(u[w:]))+int(any(v[w:])), inversions(g)
        require(d*eta <= d+after-before, "global peel charge")
        change, added = split_basis(u[w:], v[w:], q)
        full = eye(r)
        for i in range(r-w):
            full[w+i][w:] = change[i]
        basis = mul(basis, full, q)
        work = transform(work, full, q)
        charges.append({"d": d, "delta": after-before, "eta": eta, "added": added})
        w += added
    slack = sum(inversions(g) for g, _, _ in word)-endpoint_rank
    bound = slack // min(inversions(g) for g, _, _ in word)
    require(w-original_w <= bound, "global inversion-slack bound")
    for (g, u, v), (h, x, y) in zip(word, work):
        require(g == h and not any(x[w:]) and not any(y[w:]), "discarded factor support")
        require(matvec(basis, x, q) == u, "column intertwiner")
        require(matvec(list(zip(*basis)), v, q) == y, "row intertwiner")
    reduced = [(g, u[:w], v[:w]) for g, u, v in work]
    small = formal_product(reduced, n, w, q)
    full = formal_product(work, n, r, q)
    require(small == {g: [row[:w] for row in a[:w]] for g, a in full.items()}, "reduced endpoint")
    return {"retained": w, "bound_dirty": bound, "endpoint_rank": endpoint_rank,
            "charges": charges, "basis": basis}


def nested_controls():
    records = []
    for q in (2, 3):
        e = (1, 0, 0, 0, 0, 0)
        u, v = (1, 1, 1, 0, 0, 0), (1, 0, 0, 1, 1, 0)
        x, y = (1, 0, 1, 1, 0, 0), (1, 1, 0, 0, 1, 0)
        a, b, c = (3, 2, 1, 0), (1, 2, 0, 3), (2, 1, 0, 3)
        word = [(a, e, e), (b, u, v), (c, x, y),
                (inverse_perm(c), x, y), (inverse_perm(b), u, v)]
        spectator_basis = eye(6)
        spectator_basis[2][1] = spectator_basis[3][2] = spectator_basis[4][3] = 1
        spectator_basis[5][4] = 1
        mixed = transform(word, spectator_basis, q)
        record = compress(mixed, 4, 1, q)
        record["q"] = q
        records.append(record)
    return records


def word_controls():
    records = []
    for n, q, g in [(3, 2, (1, 2, 0)), (3, 3, (2, 1, 0)),
                     (4, 2, (3, 2, 1, 0)), (4, 3, (1, 3, 0, 2))]:
        r, axis = 5, (1, 0, 0, 0, 0)
        u, v = (1, 1, 0, 0, 0), (1, 0, 1, 0, 0)
        word = [(g, axis, axis), (g, u, v), (inverse_perm(g), u, v)]
        formal = formal_product(word, n, r, q)
        target = {tuple(range(n)): [[int(i == j and i > 0) for j in range(r)] for i in range(r)],
                  g: [[int(i == j == 0) for j in range(r)] for i in range(r)]}
        require(formal == target, "full formal dirty endpoint")
        represented, basis = eye(r*n*(n-1)), list(permutations(range(n)))
        regular = eye(r * len(basis))
        for label, x, y in word:
            represented = mul(represented, gate(label, x, y, q), q)
            regular = mul(regular, gate(label, x, y, q, True), q)
        length = inversions(g)
        require(crossing(represented, n, r, q) == length, "endpoint crossing rank")
        small = formal_product([(h, x[:3], y[:3]) for h, x, y in word], n, 3, q)
        require(small == {h: [row[:3] for row in a[:3]] for h, a in target.items()},
                "restricted full endpoint")
        for j in range(len(regular)):
            role, addr = divmod(j, len(basis))
            address = basis.index(compose(g, basis[addr])) if role == 0 else addr
            expected = role * len(basis) + address
            require(all(regular[i][j] == int(i == expected) for i in range(len(regular))),
                    "literal regular-action dirty basis column")
        records.append({"n": n, "q": q, "label": list(g), "d": length,
                        "weighted_slack": 2*length, "bound_dirty": 2,
                        "required_dirty": 2, "regular_basis_columns": len(regular),
                        "formal_sha256": sha256(json.dumps(sorted(formal.items())).encode()).hexdigest()})
    return records


def negative_controls():
    count = 0
    for g, u, v, q in [((0, 0, 2), (1,), (1,), 2),
                         ((1, 0), (1, 0), (0, 1), 2), ((1, 0), (1,), (1,), 4)]:
        try:
            gate(g, u, v, q)
        except ValueError:
            count += 1
        else:
            raise ValueError("illegal gate accepted")
    g, u, v = (1, 2, 0), (1, 1, 0), (1, 0, 1)
    require(formal_product([(g, u, v)], 3, 3, 2) !=
            formal_product([(g, (1, 0, 0), (1, 0, 0))], 3, 3, 2), "dirty leak control")
    require(formal_product([(g, u, v), (g, u, v)], 3, 3, 2) !=
            {tuple(range(3)): eye(3)}, "forward-for-inverse control")
    require(inversions((2, 1, 0)) == 3 and inversions(g) == 2, "unit undercharge")
    require(all(a*b % q != 0 for q in (2, 3, 5) for a in range(1, q)
                for b in range(1, q)), "sharpness pairing")
    return count + 4


def compute():
    return {"claim_type": "scoped proof with finite corroboration", "local": local_controls(),
            "decompositions": subspace_controls(), "words": word_controls(),
            "nested_compressions": nested_controls(),
            "negative_controls": negative_controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--emit", type=Path)
    mode.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    hashes = {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.iterdir())
              if p.is_file()}
    result = {"sources": hashes, "result": compute()}
    if args.emit:
        with args.emit.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    elif args.receipt:
        require(result == json.loads(args.receipt.read_text()), "receipt differs")
    print("PASS_PERMUTATION_SLACK_WORKSPACE", result["result"]["local"]["peels"],
          "peels;", result["result"]["decompositions"], "decompositions;",
          len(result["result"]["words"]), "formal words")


if __name__ == "__main__":
    main()
