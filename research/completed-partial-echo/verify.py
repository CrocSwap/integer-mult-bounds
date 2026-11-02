#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact completed-observation echo words; all checks survive Python -O."""
from __future__ import annotations

import hashlib
import heapq
import itertools
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_BLOCKS = 64
MAX_WORD = 384


def need(condition, message):
    if not condition:
        raise ValueError(message)


def size(n):
    need(type(n) is int and 1 <= n <= MAX_BLOCKS, "invalid block count")


def price(value):
    need(type(value) in (int, Fraction), "price must be exact")
    q = Fraction(value)
    need(0 < q <= 4096 and q.denominator <= 4096, "price out of range")
    return q


def optimum(forward, inverse, up, down):
    size(len(forward))
    need(len(inverse) == len(forward), "price dimensions")
    f = tuple(price(x) for x in forward)
    r = tuple(price(x) for x in inverse)
    return sum(f) + sum(r) + ((len(f) + 1) // 2) * (price(up) + price(down))


def schedule(n, eager=False):
    size(n)
    word = []
    for i in range(n):
        sign = 1 if eager or i % 2 == 0 else -1
        word.extend((("H", i, -sign), ("J", -1, sign), ("H", i, sign)))
        if eager:
            word.append(("J", -1, -1))
        word.append(("O", i, 0))
    if not eager and n % 2:
        word.append(("J", -1, -1))
    need(len(word) <= MAX_WORD, "word capacity")
    return tuple(word)


def parse_word(word, n):
    size(n)
    need(type(word) is tuple and len(word) <= MAX_WORD, "word capacity/type")
    for op in word:
        need(type(op) is tuple and len(op) == 3, "instruction shape")
        tag, i, sign = op
        need(type(i) is int and type(sign) is int, "instruction integer type")
        if tag == "H":
            need(0 <= i < n and sign in (-1, 1), "child instruction")
        elif tag == "J":
            need(i == -1 and sign in (-1, 1), "injection instruction")
        elif tag == "O":
            need(0 <= i < n and sign == 0, "observation instruction")
        else:
            raise ValueError("unknown instruction")


def formal(word, n, canonical=False):
    """Track coefficients of independent L_i W_initial and L_i X."""
    parse_word(word, n)
    e, observed = 0, 0
    dirt, source = [0] * n, [0] * n
    counts = [0, 0, 0, 0]
    for tag, i, sign in word:
        if tag == "H":
            dirt[i] += sign
            source[i] += sign * e
            counts[sign == -1] += 1
        elif tag == "J":
            e += sign
            counts[2 + (sign == -1)] += 1
        else:
            need(i == observed, "observation order")
            need(dirt == [0] * n, "dirty output at observation")
            need(source == [int(j <= i) for j in range(n)], "wrong partial output")
            need(not canonical or e == 0, "noncanonical observed workspace")
            observed += 1
    need(observed == n, "missing observations")
    need(e == 0, "workspace not restored")
    need(dirt == [0] * n and source == [1] * n, "wrong returned output")
    return tuple(counts)


def literal(word, maps):
    """Separate payload execution on every X/W/D input basis column."""
    n, rows, cols = len(maps), len(maps[0]), len(maps[0][0])
    need(1 <= n <= 8 and 1 <= rows <= 3 and 1 <= cols <= 3, "fixture capacity")
    need(all(len(m) == rows and all(len(r) == cols for r in m) for m in maps),
         "literal matrix dimensions")
    parse_word(word, n)
    probes, cuts = 0, 0
    for column in range(2 * cols + rows):
        x = [int(column == j) for j in range(cols)]
        w = [int(column == cols + j) for j in range(cols)]
        d = [int(column == 2 * cols + j) for j in range(rows)]
        incoming_w, incoming_d = tuple(w), tuple(d)
        for tag, i, sign in word:
            if tag == "J":
                w = [a + sign * b for a, b in zip(w, x, strict=True)]
            elif tag == "H":
                d = [d[r] + sign * sum(maps[i][r][c] * w[c] for c in range(cols))
                     for r in range(rows)]
            else:
                want = [incoming_d[r] + sum(maps[j][r][c] * x[c]
                        for j in range(i + 1) for c in range(cols)) for r in range(rows)]
                need(d == want, "literal partial output")
                cuts += 1
        need(tuple(w) == incoming_w, "literal dirty return")
        need(x == [int(column == j) for j in range(cols)], "literal source return")
        want = [incoming_d[r] + sum(matrix[r][c] * x[c] for matrix in maps
                for c in range(cols)) for r in range(rows)]
        need(d == want, "literal returned output")
        probes += 1
    return probes, cuts


def advance(state, n):
    e, a, b, observed = state
    if observed < n and not any(a) and b == tuple(int(i <= observed) for i in range(n)):
        observed += 1
    return e, a, b, observed


def shortest(n, forward, inverse, up, down, limit):
    """Unrestricted repeated-label shortest words, within a finite cost bound."""
    need(n in (1, 2) and 1 <= limit <= 18, "search capacity")
    start = (0, (0,) * n, (0,) * n, 0)
    queue, distances = [(0, start)], {start: 0}
    expanded, generated = 0, 0
    # Every edge costs >=1, so at most sum_(j=0)^limit (2n+2)^j words exist.
    for _ in range(1_000_000):
        if not queue:
            return None, expanded, generated
        cost, state = heapq.heappop(queue)
        if cost != distances[state]:
            continue
        e, a, b, observed = state
        if observed == n and e == 0 and not any(a) and b == (1,) * n:
            return cost, expanded, generated
        expanded += 1
        moves = [(up, (e + 1, a, b, observed)), (down, (e - 1, a, b, observed))]
        for i in range(n):
            for sign, charge in ((1, forward[i]), (-1, inverse[i])):
                aa, bb = list(a), list(b)
                aa[i] += sign
                bb[i] += sign * e
                moves.append((charge, (e, tuple(aa), tuple(bb), observed)))
        for charge, target in moves:
            generated += 1
            target = advance(target, n)
            total = cost + charge
            if total <= limit and total < distances.get(target, limit + 1):
                distances[target] = total
                heapq.heappush(queue, (total, target))
    raise ValueError("search state capacity exhausted")


def finite_searches():
    results = []
    for n in (1, 2):
        fixtures = [(tuple([1] * n), tuple([1] * n), 1, 1),
                    (tuple(range(1, n + 1)), tuple(range(n, 0, -1)), 1, 2),
                    (tuple([2] * n), tuple([1] * n), 2, 1),
                    (tuple([1] * n), tuple([2] * n), 2, 3)]
        for f, r, up, down in fixtures:
            wanted = optimum(f, r, up, down)
            need(wanted.denominator == 1, "integer search budget")
            result, expanded, generated = shortest(n, f, r, up, down, int(wanted))
            need(result == wanted, "shortest-word mismatch")
            results.append({"blocks": n, "forward": f, "inverse": r,
                            "up": up, "down": down, "optimum": result,
                            "expanded": expanded, "generated": generated})
    return results


def check_schedules():
    cases = 0
    prices = (1, 2, 3, Fraction(1, 2), Fraction(2, 3))
    for n in range(1, MAX_BLOCKS + 1):
        word = schedule(n)
        counts = formal(word, n)
        need(counts == (n, n, (n + 1) // 2, (n + 1) // 2), "instruction counts")
        eager_counts = formal(schedule(n, eager=True), n, canonical=True)
        need(eager_counts == (n, n, n, n), "eager counts")
        for up, down in itertools.product(prices, repeat=2):
            f = tuple(Fraction(i + 1, 7) for i in range(n))
            r = tuple(Fraction(n - i, 5) for i in range(n))
            actual = sum(f[i] if s == 1 else r[i] for t, i, s in word if t == "H")
            actual += sum(up if s == 1 else down for t, _, s in word if t == "J")
            need(actual == optimum(f, r, up, down), "weighted tariff")
            cases += 1
    return cases


def check_payloads():
    cases, probes, cuts = 0, 0, 0
    for n in range(1, 5):
        for values in itertools.product((-1, 0, 1), repeat=n):
            maps = tuple(((value,),) for value in values)
            p, c = literal(schedule(n), maps)
            cases, probes, cuts = cases + 1, probes + p, cuts + c
    for entries in itertools.product((0, 1), repeat=8):
        maps = tuple(tuple(tuple(entries[4 * i + 2 * r + c] for c in range(2))
                           for r in range(2)) for i in range(2))
        p, c = literal(schedule(2), maps)
        cases, probes, cuts = cases + 1, probes + p, cuts + c
    for n, rows, cols in itertools.product(range(1, 9), range(1, 4), range(1, 4)):
        maps = tuple(tuple(tuple(Fraction((i + r + 2 * c) % 5 - 2, c + 1)
                                 for c in range(cols)) for r in range(rows)) for i in range(n))
        p, c = literal(schedule(n), maps)
        cases, probes, cuts = cases + 1, probes + p, cuts + c
    return {"fixtures": cases, "basis_columns": probes, "observations": cuts}


def controls():
    word = schedule(3)
    mutants = [word[1:], word[:2] + word[3:], word[:-1],
               tuple((t, i, -s if t == "J" else s) for t, i, s in word),
               tuple(op for op in word if op[0] != "O"),
               tuple((t, 0 if t == "H" else i, s) for t, i, s in word),
               word + (("H", 0, 1),)]
    rejected = 0
    for mutant in mutants:
        try:
            formal(mutant, 3)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("semantic mutant accepted")
    try:
        formal(schedule(2), 2, canonical=True)
    except ValueError:
        rejected += 1
    else:
        raise ValueError("output checkpoint confused with workspace restoration")
    for bad in (True, 0, 65, 1.0):
        try:
            schedule(bad)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid block count accepted")
    for bad in (True, 0, -1, 0.5, Fraction(1, 4097)):
        try:
            optimum((1,), (1,), bad, 1)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid price accepted")
    return rejected


def hashes():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    root = HERE.parent.parent
    pins = {}
    for row in sources["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((root / row["path"]).read_bytes()).hexdigest()
            need(digest == row["sha256"], "changed source bytes: " + row["path"])
            pins[row["path"]] = digest
    files = sorted(HERE.iterdir())
    need(len(files) <= 12, "package file capacity")
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}, pins


def main():
    files, pins = hashes()
    result = {"weighted_schedule_cases": check_schedules(), "payloads": check_payloads(),
              "shortest_words": finite_searches(), "rejections": controls(),
              "package_sha256": files, "input_sha256": pins,
              "scope": "Scoped written proof and exact finite corroboration; no supplier or kappa."}
    print(json.dumps(result, sort_keys=True))
    print("PASS_COMPLETED_PARTIAL_ECHO")


if __name__ == "__main__":
    main()
