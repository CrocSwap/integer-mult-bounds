#!/usr/bin/env python3
"""Exact weighted-capacity fanout construction and independent finite checks."""

import hashlib
import json
from itertools import combinations_with_replacement
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def domain(weights, capacity):
    require(type(weights) is tuple and len(weights) <= 10, "weight vector")
    require(type(capacity) is int and 1 <= capacity <= 65536, "capacity")
    require(all(type(w) is int and 1 <= w <= capacity for w in weights),
            "positive fitting weights")


def packing(weights, capacity):
    """Minimum bins by subset DP; the least item fixes each bin's position."""
    domain(weights, capacity)
    size = 1 << len(weights)
    mass = [0] * size
    count = [len(weights) + 1] * size
    chosen = [0] * size
    count[0] = 0
    for mask in range(1, size):
        bit = mask & -mask
        mass[mask] = mass[mask ^ bit] + weights[bit.bit_length() - 1]
        sub = mask
        for _ in range(size):
            if sub & bit and mass[sub] <= capacity:
                candidate = 1 + count[mask ^ sub]
                if candidate < count[mask]:
                    count[mask], chosen[mask] = candidate, sub
            sub = (sub - 1) & mask
            if sub == 0:
                break
        require(chosen[mask] != 0, "fitting singleton must exist")
    bins, mask = [], size - 1
    for _ in range(len(weights)):
        if mask == 0:
            break
        sub = chosen[mask]
        bins.append(tuple(i for i in range(len(weights)) if sub >> i & 1))
        mask ^= sub
    require(mask == 0 and len(bins) == count[-1], "partition reconstruction")
    return tuple(bins)


def emit(weights, capacity, bins):
    domain(weights, capacity)
    require(type(bins) is tuple and len(bins) <= len(weights), "bin list")
    require(all(type(group) is tuple and len(group) <= len(weights)
                for group in bins), "bounded groups")
    flat = tuple(i for group in bins for i in group)
    require(all(type(i) is int and 0 <= i < len(weights) for i in flat),
            "output indices")
    require(sorted(flat) == list(range(len(weights))), "partition coverage")
    require(all(group and sum(weights[i] for i in group) <= capacity
                for group in bins), "bin capacity")
    program = []
    for j, group in enumerate(bins):
        sign = 1 if j % 2 == 0 else -1
        program.extend(("A", i, -sign) for i in group)
        program.append(("B", -1, sign))
        for i in group:
            program.extend((("A", i, sign), ("C", i, 0)))
    if len(bins) % 2:
        program.append(("B", -1, -1))
    require(len(program) <= 4 * len(weights) + 1, "program size")
    return tuple(program)


def independent_bins(weights, capacity):
    """Enumerate all feasible unlabeled bin-load states, at most Bell(6)."""
    require(len(weights) <= 6, "independent enumeration domain")
    states = {()}
    for weight in weights:
        following = set()
        for loads in states:
            following.add(tuple(sorted(loads + (weight,))))
            for j, load in enumerate(loads):
                if load + weight <= capacity:
                    updated = loads[:j] + (load + weight,) + loads[j + 1:]
                    following.add(tuple(sorted(updated)))
        require(len(following) <= 203, "Bell-number state bound")
        states = following
    return min(map(len, states))


def product(left, right):
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(2))
                       for j in range(len(right[0]))) for i in range(2))


def add_to(target, source, sign):
    return tuple(tuple(x + sign * y for x, y in zip(a, b))
                 for a, b in zip(target, source))


def literal(weights, capacity, program):
    """Execute all basis columns together using ordinary integer matrices."""
    domain(weights, capacity)
    n, width = len(weights), 2 * (len(weights) + 2)
    initial = tuple(tuple(tuple(int(2 * p + i == j) for j in range(width))
                          for i in range(2)) for p in range(n + 2))
    rows, life = list(initial), [0] * n
    bmap = ((1, 2), (-1, 1))
    amap = tuple(((i + 1, -1), (2, i)) for i in range(n))
    targets = tuple(add_to(initial[i + 2], product(amap[i],
                         product(bmap, initial[0])), 1) for i in range(n))
    require(type(program) is tuple and len(program) <= 4 * n + 4,
            "literal instruction limit")
    require(all(type(row) is tuple and len(row) == 3 for row in program),
            "instruction shape")
    peak = bcount = acount = 0
    for op, i, sign in program:
        require(op in ("A", "B", "C"), "instruction alphabet")
        if op == "B":
            require(i == -1 and sign in (-1, 1), "B contract")
            rows[1] = add_to(rows[1], product(bmap, rows[0]), sign)
            bcount += 1
        else:
            require(0 <= i < n and life[i] != 2, "committed target touched")
            if op == "C":
                require(sign == 0 and life[i] == 1, "commit lifecycle")
                require(rows[i + 2] == targets[i], "premature commit")
                life[i] = 2
            else:
                require(sign in (-1, 1), "A sign")
                life[i] = 1
                rows[i + 2] = add_to(rows[i + 2], product(amap[i], rows[1]), sign)
                acount += 1
        used = sum(w for w, state in zip(weights, life) if state == 1)
        require(used <= capacity, "unfinished weight exceeds capacity")
        peak = max(peak, used)
    require(rows[:2] == list(initial[:2]), "source or connector not restored")
    require(all(state == 2 for state in life), "missing commit")
    require(tuple(rows[2:]) == targets, "wrong full endpoint")
    return acount, bcount, peak


def canonical(q, rows):
    signs = (q,) + tuple(e for _, e, _ in rows)
    first = next((v for v in signs if v), 0)
    if first < 0:
        return -q, tuple((life, -e, f) for life, e, f in rows)
    return q, rows


def successors(state, weights, capacity):
    q, rows = state
    active = sum(w for w, (life, _, _) in zip(weights, rows) if life == 1)
    answer = []
    for sign in (-1, 1):
        answer.append(canonical(q + sign, rows))
        for i, (life, e, f) in enumerate(rows):
            if life == 2 or (life == 0 and active + weights[i] > capacity):
                continue
            e1, f1 = e + sign, f + sign * q
            life1 = 2 if (e1, f1) == (0, 1) else 1
            changed = rows[:i] + ((life1, e1, f1),) + rows[i + 1:]
            answer.append(canonical(q, changed))
    return answer


def word_minimum(weights, capacity):
    """Breadth-first all-unit-query search, without packing or bill pruning."""
    domain(weights, capacity)
    require(len(weights) <= 3, "word-search output bound")
    start = (0, ((0, 0, 0),) * len(weights))
    layer, seen, sizes = {start}, {start}, []
    for depth in range(11):
        sizes.append(len(layer))
        if any(q == 0 and all(life == 2 for life, _, _ in rows)
               for q, rows in layer):
            return depth, len(seen), sizes
        following = set()
        for state in layer:
            for item in successors(state, weights, capacity):
                if item not in seen:
                    following.add(item)
                    require(len(following) + len(seen) <= 100000,
                            "word-search state bound")
        seen.update(following)
        layer = following
    raise ValueError("word-search depth exhausted")


def family_checks():
    cases = calls = peak_sum = fragmented = 0
    digest = hashlib.sha256()
    for capacity in range(1, 7):
        for n in range(7):
            for weights in combinations_with_replacement(range(1, capacity + 1), n):
                bins = packing(weights, capacity)
                require(len(bins) == independent_bins(weights, capacity),
                        "independent packing disagreement")
                program = emit(weights, capacity, bins)
                acount, bcount, peak = literal(weights, capacity, program)
                require(acount == 2 * n, "readout count")
                require(bcount == 2 * ((len(bins) + 1) // 2), "B count")
                volume = (sum(weights) + capacity - 1) // capacity
                fragmented += bcount > 2 * ((volume + 1) // 2)
                cases, calls, peak_sum = cases + 1, calls + acount + bcount, peak_sum + peak
                digest.update(json.dumps([weights, capacity, bins, program]).encode())
    return dict(cases=cases, literal_calls=calls, peak_sum=peak_sum,
                strict_volume_obstructions=fragmented, trace_sha256=digest.hexdigest())


def rejected(action):
    try:
        action()
    except ValueError:
        return 1
    raise ValueError("negative control accepted")


def controls():
    count = 0
    for weights, cap in [((0,), 2), ((-1,), 2), ((3,), 2), ((True,), 2),
                         ((1,), 0), ((1,), True), ((1,), 65537),
                         ((1,) * 11, 2), ([1], 2), ((1.0,), 2)]:
        count += rejected(lambda w=weights, c=cap: packing(w, c))
    weights, cap = (2, 2, 2), 3
    count += rejected(lambda: emit(weights, cap, ((0, 1), (2,))))
    count += rejected(lambda: emit(weights, cap, ((0,), (1,), (1,))))
    program = emit(weights, cap, packing(weights, cap))
    count += rejected(lambda: literal(weights, cap, program[:-1]))
    count += rejected(lambda: literal(weights, cap, (("C", 0, 0),) + program))
    count += rejected(lambda: literal(weights, cap, program + (("A", 0, 1),)))
    over_capacity = (("A", 0, -1), ("A", 1, -1))
    count += rejected(lambda: literal(weights, cap, over_capacity))
    changed = list(program)
    index = next(j for j, row in enumerate(changed) if row[0] == "B")
    changed[index] = ("B", -1, -changed[index][2])
    count += rejected(lambda: literal(weights, cap, tuple(changed)))
    count += rejected(lambda: literal(weights, cap, (("X", 0, 1),)))
    require(product(((1, -1), (2, 0)), ((1, 2), (-1, 1))) !=
            product(((1, 2), (-1, 1)), ((1, -1), (2, 0))), "noncommuting fixture")
    return count


def main():
    result = family_checks()
    word_cases = []
    for weights, capacity in [((2, 2, 2), 3), ((1, 2, 2), 3),
                              ((1, 1, 2), 3), ((1, 2, 3), 3)]:
        minimum, states, layers = word_minimum(weights, capacity)
        bins = packing(weights, capacity)
        predicted = 2 * len(weights) + 2 * ((len(bins) + 1) // 2)
        require(minimum == predicted, "independent word-search disagreement")
        word_cases.append(dict(weights=weights, capacity=capacity, minimum=minimum,
                               states=states, layers=layers))
    fixture = (3, 3, 3, 3, 3, 1)
    bins = packing(fixture, 5)
    actual = literal(fixture, 5, emit(fixture, 5, bins))
    require(len(bins) == 5 and actual[:2] == (12, 6), "fragmentation witness")
    require(52 * actual[1] + actual[0] == 324, "weighted query bill")
    boundary = (65536,) * 10
    require(literal(boundary, 65536, emit(boundary, 65536,
                    packing(boundary, 65536)))[:2] == (20, 10), "maximum domain")
    result.update(word_searches=word_cases, controls=controls(),
                  witness=dict(weights=fixture, capacity=5, bins=bins,
                               readouts=12, shared_calls=6, price=324))
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"):
        with (package / name).open("rb") as stream:
            data = stream.read(262145)
        require(len(data) <= 262144, "package file-size bound")
        hashes[name] = hashlib.sha256(data).hexdigest()
    print(json.dumps(dict(status="PASS_WEIGHTED_PENDING_FANOUT", result=result,
                          source_sha256=hashes), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
