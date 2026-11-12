"""Independent unit-body rank-two signed correction via transported shears."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from time import monotonic

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
CLOCKS = (1516, 1580, 1659, 1721)
PAIRS = tuple(combinations(CLOCKS, 2))
CAP, SECONDS = 6, 20


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def pinned(path, expected):
    raw = path.read_bytes()
    require(len(expected) == 64 and sha256(raw).hexdigest() == expected, "changed input " + path.name)
    return raw


def unit(n, at):
    return [Q(i == at) for i in range(n)]


def emit(event, q, alpha, even=False):
    family, op, *args = event
    if family == "J":
        u, v, x, y = args[0]
        return [("ADD", v, u, Q(1, q)), ("ADD", x, y, alpha * q)]
    if family == "B":
        return []
    require(family == "A", "unknown event family")
    dst, *tail = args
    if op == "ADD":
        src, value = tail
        return [(op, dst, src, Q(value))]
    if op == "SCALE":
        return [(op, dst, dst, Q(tail[0]))]
    if op == "SWAP":
        return [(op, dst, tail[0], Q(1))]
    if op == "QUERY":
        src, power = tail
        return [("ADD", dst, src, Q(1) if even else Q(q) ** power)]
    if op == "IDLE_ODD":
        return [("SCALE", dst, dst, Q(q) ** tail[1])]
    require(op in ("LAMBDA", "IDLE_ONE"), "unknown Type A event")
    # Body=1 and q²=1 give identity for these two operations.
    return []


def transported(ops, n, dst, src):
    u, v = unit(n, dst), unit(n, src)
    for op, d, s, a in reversed(ops):
        if op == "ADD":
            u[d] -= a * u[s]
            v[s] += a * v[d]
        elif op == "SCALE":
            u[d] /= a
            v[d] *= a
        else:
            require(op == "SWAP", "unknown elementary op")
            u[d], u[s] = u[s], u[d]
            v[d], v[s] = v[s], v[d]
    require(sum(x * y for x, y in zip(u, v, strict=True)) == 0, "transported shear lost square-zero")
    return u, v


def residual(u, v, dst, src, delta):
    # (I+delta*u*v)(I+delta*e_dst*e_src^T)-I.
    rows = {}
    for i, a in enumerate(u):
        row = {j: delta * a * b for j, b in enumerate(v) if delta * a * b}
        extra = delta * (i == dst) + delta * delta * a * v[dst]
        if extra:
            row[src] = row.get(src, Q(0)) + extra
        row = {j: c for j, c in row.items() if c}
        if row:
            rows[i] = row
    return rows


def product(A, B):
    output = {}
    for i, left in A.items():
        row = Counter()
        for k, a in left.items():
            for j, b in B.get(k, {}).items():
                row[j] += a * b
        row = {j: c for j, c in row.items() if c}
        if row:
            output[i] = row
    return output


def rank(rows):
    pivots = {}
    for row in rows.values():
        r = row.copy()
        while r:
            j = max(r)
            if j not in pivots:
                scale = r[j]
                pivots[j] = {k: c / scale for k, c in r.items()}
                break
            multiplier = r[j]
            for k, c in pivots[j].items():
                x = r.get(k, Q(0)) - multiplier * c
                if x:
                    r[k] = x
                else:
                    r.pop(k, None)
    return len(pivots)


def first_nonzero(matrix):
    for i in sorted(matrix):
        for j, value in sorted(matrix[i].items()):
            if value:
                return [i, j, str(value)]
    return None


def analyze(events, start, stop, n, alpha, q):
    d, s = events[start][2:4]
    ops = [row for t in range(start, stop)
           for row in emit(events[t], q, alpha, even=(t == start))]
    u, v = transported(ops, n, d, s)
    N = residual(u, v, d, s, Q(1, q) - 1)
    square = product(N, N)
    return dict(rank=rank(N), square_rank=rank(square), first_square_nonzero=first_nonzero(square),
                trace=str(sum(row.get(i, 0) for i, row in N.items())),
                transport_cross_terms=[str(v[d]), str(u[s])],
                rank_one_directions={"column": {i: str(c) for i, c in enumerate(u) if c},
                                     "row": {i: str(c) for i, c in enumerate(v) if c}})


def controls():
    query = ["A", "QUERY", 0, 1, -1]
    disjoint = [query, ["A", "SWAP", 0, 2], ["A", "SWAP", 1, 3], query]
    linked = [query, ["A", "SWAP", 0, 1], query]
    good = analyze(disjoint, 0, 3, 4, Q(-1), -1)
    bad = analyze(linked, 0, 2, 4, Q(-1), -1)
    even = analyze(linked, 0, 2, 4, Q(-1), 1)
    require(good["rank"] == 2 and good["square_rank"] == 0, "disjoint rank-two control")
    require(bad["rank"] == 2 and bad["square_rank"] > 0, "linked square control")
    require(even["rank"] == even["square_rank"] == 0, "q=+1 control")
    return ["disjoint square-zero rank two", "linked non-square-zero rank two", "q=+1 identity"]


def main(args):
    tests = controls()
    if args.controls_only:
        return {"controls": tests}
    # The lead's explicit launch supplies the sealed price digest. Read it before the caller.
    price = loads(pinned(args.price, args.price_sha))
    require(price["head"] == HEAD and price["caller_sha256"] == CALLER, "wrong comparator price")
    require(price["eligible_pairs_before_support"] == [list(pair) for pair in PAIRS] and
            price["support_pair_cap"] == CAP and price["support_runner_seconds"] == SECONDS,
            "wrong frozen pair scope")
    start = monotonic()
    caller = loads(pinned(args.caller, CALLER))
    data = caller["types"]["A"]
    require((caller["stages"], data["roles"], data["offset"], len(data["ports"])) == (17, 36, 0, 96),
            "wrong exact caller signature")
    events = caller["events"]
    require([i for i, e in enumerate(events) if e[:2] == ["A", "QUERY"]] == list(CLOCKS), "wrong QUERY inventory")
    require(all(events[i] == ["A", "QUERY", 0, 1, -1] for i in CLOCKS), "wrong QUERY source or power")
    outcomes, possible = [], []
    for pair in PAIRS:
        if len(outcomes) == CAP or monotonic() - start >= SECONDS:
            break
        first, second = pair
        probes = [analyze(events, first, second, data["roles"], Q(data["alpha2"]), q) for q in (1, -1)]
        require(probes[0]["rank"] == probes[0]["square_rank"] == 0, "q=+1 correction is not identity")
        odd = probes[1]
        if odd["rank"] <= 2 and odd["square_rank"] == 0:
            possible.append(list(pair))
        outcomes.append({"pair": pair, "q_plus": probes[0], "q_minus": odd})
    return {"head": HEAD, "caller_sha256": CALLER, "price_sha256": args.price_sha, "controls": tests,
            "case_cap": CAP, "runner_cap_seconds": SECONDS, "body": "all 17 body variables equal one",
            "outcomes": outcomes, "unvisited": PAIRS[len(outcomes):], "rank_at_most_two_square_zero_keys": possible,
            "next_gate_if_any": "one exact key/90s formal necessary test only; no physical candidate established"}


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("--controls-only", action="store_true")
    p.add_argument("--price", type=Path)
    p.add_argument("--price-sha")
    p.add_argument("--caller", type=Path)
    args = p.parse_args()
    require(args.controls_only or (args.price and args.price_sha and args.caller), "missing exact launch inputs")
    print(dumps(main(args), indent=2, sort_keys=True))
