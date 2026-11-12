#!/usr/bin/env python3
"""Exact price of a weight-4 step on the five-source dirty connector.

Standard library only. No assert statements, so python -O runs the same checks.
Every loop has an explicit finite bound.

The interface is research/universal-connector-boundary: five read-only sources,
one arbitrarily dirty connector z, and all 31 nonzero output rows. Every nonempty
source subset is one toggle, charged one dispatch plus its source additions. A
readout costs one dispatch and one addition. Prices are o >= 0 per dispatch and
p > 0 per addition.

A source word is a closed walk in F_2^5. This file proves that every correct
schedule using at least one weight-4 toggle costs at least 72o + 76p, and
exhibits a schedule attaining it. The proof is the counting case split of the
weight-3 price, plus three exhaustive censuses of the rows where that split
allows addition excess 14.
"""

import random

N = 5
NMASK = (1 << N) - 1
FULL = ((1 << (NMASK + 1)) - 1) - 1  # bits 1..31
READOUTS = 2 * NMASK
DUOS = (3, 5, 6, 9, 10, 12, 17, 18, 20, 24)
QUADS = tuple(NMASK ^ (1 << source) for source in range(N))
BITS = tuple(1 << source for source in range(N))

# One weight-4 (15 = {0,1,2,3}), one DUO (17 = {0,4}) and eight singletons.
WITNESS = [17, 2, 1, 4, 2, 1, 2, 8, 16, 15]
# Ten singletons and one weight-4. Meets the addition bound at 11 steps.
WITNESS_11 = [1, 2, 1, 4, 2, 1, 2, 8, 16, 8, 23]
# Published DUO word. Recomputed here; not trusted as a price.
DUO = [1, 2, 8, 18, 12, 16, 1, 2, 4, 2]

T9_WORDS = 5 ** 8
T11_WORDS = 5 ** 10
T10_FREE = 5 ** 7


def fail(message):
    raise SystemExit("FAIL " + message)


def require(ok, message):
    if not ok:
        fail(message)


def weight(mask):
    return mask.bit_count()


def prefixes(steps):
    state = 0
    out = [0]
    for step in steps:
        require(1 <= step <= NMASK, "toggle outside F_2^5: %r" % (step,))
        state ^= step
        out.append(state)
    return out


def unique_points(points):
    seen = 0
    unique = []
    for point in points:
        if (seen >> point) & 1:
            continue
        seen |= 1 << point
        unique.append(point)
    return unique


def difference_mask(points):
    unique = unique_points(points)
    mask = 0
    for i, left in enumerate(unique):
        for right in unique[i + 1:]:
            mask |= 1 << (left ^ right)
    return mask & FULL


def difference_mask_set(points):
    """Independent difference accumulator. Used only as a census cross-check."""
    unique = unique_points(points)
    mask = 0
    for left in unique:
        for right in unique:
            if left != right:
                mask |= 1 << (left ^ right)
    return mask & FULL


def missing_rows(steps):
    pre = prefixes(steps)
    require(pre[-1] == 0, "word is not closed")
    return NMASK - difference_mask(pre).bit_count()


def weight_min(length):
    """Least even addition count of a length-`length` walk with a weight-4 step."""
    # One weight-4 step and length-1 singletons sum to length+3, which may be odd.
    total = length + 3
    if total & 1:
        total += 1
    return total


def uncovered_floor(size):
    pairs = size * (size - 1) // 2
    least = NMASK - pairs
    if least < 0:
        least = 0
    if size <= 9 and least < 1:
        least = 1
    return least


def build_schedule(steps):
    """Two readouts at the first boundary pair of every nonzero mask."""
    pre = prefixes(steps)
    require(pre[-1] == 0, "schedule word is not closed")
    first = {}
    for i in range(len(pre)):
        for j in range(i + 1, len(pre)):
            first.setdefault(pre[i] ^ pre[j], (i, j))
    at = {boundary: [] for boundary in range(len(pre))}
    for row in range(1, NMASK + 1):
        pair = first.get(row)
        require(pair is not None, "no readout pair for row %d" % row)
        at[pair[0]].append(row)
        at[pair[1]].append(row)
    ops = []
    for boundary in range(len(pre)):
        for row in at[boundary]:
            ops.append(("A", row))
        if boundary < len(steps):
            ops.append(("T", steps[boundary]))
    return ops


def schedule_cost(ops):
    queries = len(ops)
    additions = 0
    for kind, arg in ops:
        additions += weight(arg) if kind == "T" else 1
    return queries, additions


def evaluate_generic(ops):
    """z carries z0 in bit 0 and B_j x_j in bit 1+j. Correctness is exact for every map."""
    connector = 1
    rows = [0] * (NMASK + 1)
    for kind, arg in ops:
        if kind == "T":
            for source in range(N):
                if (arg >> source) & 1:
                    connector ^= 1 << (1 + source)
        else:
            rows[arg] ^= connector
    if connector != 1:
        return False
    for row in range(1, NMASK + 1):
        want = 0
        for source in range(N):
            if (row >> source) & 1:
                want |= 1 << (1 + source)
        if rows[row] != want:
            return False
    return True


def apply_map(matrix, vector, width):
    out = 0
    for bit in range(width):
        if (vector >> bit) & 1:
            out ^= matrix[bit]
    return out


def run_concrete(ops, matrices_b, matrices_a, sources, z0, y0, width):
    connector = z0
    rows = list(y0)
    for kind, arg in ops:
        if kind == "T":
            for source in range(N):
                if (arg >> source) & 1:
                    connector ^= apply_map(matrices_b[source], sources[source], width)
        else:
            rows[arg] ^= apply_map(matrices_a[arg], connector, width)
    if connector != z0:
        return False
    for row in range(1, NMASK + 1):
        total = 0
        for source in range(N):
            if (row >> source) & 1:
                total ^= apply_map(matrices_b[source], sources[source], width)
        if rows[row] != (y0[row] ^ apply_map(matrices_a[row], total, width)):
            return False
    return True


def check_concrete(ops, seed):
    width = 3
    identity = [1 << bit for bit in range(width)]
    sources = [1, 2, 3, 4, 5]
    z0 = 7
    y0 = [((row * 3) + 1) & 7 for row in range(NMASK + 1)]
    mats_b = [list(identity) for _ in range(N)]
    mats_a = [list(identity) for _ in range(NMASK + 1)]
    require(
        run_concrete(ops, mats_b, mats_a, sources, z0, y0, width),
        "fixed dirty identity-map trial failed",
    )
    rng = random.Random(seed)
    for _ in range(40):
        mats_b = [[rng.randrange(1 << width) for _ in range(width)] for _ in range(N)]
        mats_a = [[rng.randrange(1 << width) for _ in range(width)] for _ in range(NMASK + 1)]
        sources = [rng.randrange(1 << width) for _ in range(N)]
        z0 = rng.randrange(1 << width)
        y0 = [rng.randrange(1 << width) for _ in range(NMASK + 1)]
        require(
            run_concrete(ops, mats_b, mats_a, sources, z0, y0, width),
            "random dirty trial failed",
        )


def nine_and_ten_point_counts():
    """Covers containing 0 and the standard basis. Translation and GL(5,2) reduce to this."""
    base = [0] + [1 << source for source in range(N)]
    rest = [point for point in range(1, NMASK + 1) if point not in base]
    counts = {9: 0, 10: 0}
    span = len(rest)
    require(span == 26, "affine complement has size %d" % span)
    for extra in (3, 4):
        chosen = [0] * extra
        for i in range(extra):
            chosen[i] = i
        examined = 0
        limit = 1
        for i in range(extra):
            limit = limit * (span - i) // (i + 1)
        while examined < limit:
            points = list(base)
            for index in chosen:
                points.append(rest[index])
            if difference_mask(points) == FULL:
                counts[len(base) + extra] += 1
            examined += 1
            cursor = extra - 1
            while cursor >= 0 and chosen[cursor] == span - extra + cursor:
                cursor -= 1
            if cursor < 0:
                break
            chosen[cursor] += 1
            for follow in range(cursor + 1, extra):
                chosen[follow] = chosen[follow - 1] + 1
        require(examined == limit, "normal form stopped at %d of %d" % (examined, limit))
    return counts


def check_compositions():
    """The addition-excess-14 rows force a single weight multiset."""
    def solutions(length, total):
        found = []
        for n5 in range(length + 1):
            for n4 in range(length - n5 + 1):
                if n4 < 1:
                    continue
                for n3 in range(length - n5 - n4 + 1):
                    for n2 in range(length - n5 - n4 - n3 + 1):
                        n1 = length - n5 - n4 - n3 - n2
                        weighted = n1 + 2 * n2 + 3 * n3 + 4 * n4 + 5 * n5
                        if weighted == total:
                            found.append((n1, n2, n3, n4, n5))
        return found

    require(solutions(9, 12) == [(8, 0, 0, 1, 0)], "T=9 composition %r" % (solutions(9, 12),))
    require(solutions(10, 14) == [(8, 1, 0, 1, 0)], "T=10 composition %r" % (solutions(10, 14),))
    require(solutions(11, 14) == [(10, 0, 0, 1, 0)], "T=11 composition %r" % (solutions(11, 14),))


def check_corner():
    """Addition excess is at least 14 on every legal (T, s), through the finite table."""
    query_eq = []
    add_eq = []
    minimum_add = None
    for length in range(1, 41):
        for size in range(1, length + 1):
            missing = uncovered_floor(size)
            additions = weight_min(length) + 2 * missing
            queries = length + 2 * missing
            if minimum_add is None or additions < minimum_add:
                minimum_add = additions
            require(queries >= 10, "query floor failed at %r" % ((length, size, queries),))
            require(additions >= 14, "addition floor failed at %r" % ((length, size, additions),))
            if queries == 10:
                query_eq.append((length, size, missing))
            if additions == 14:
                add_eq.append((length, size, missing, weight_min(length)))
    require(query_eq == [(10, 10, 0)], "query equality rows %r" % (query_eq,))
    require(
        add_eq == [(9, 9, 1, 12), (10, 10, 0, 14), (11, 10, 0, 14), (11, 11, 0, 14)],
        "addition equality rows %r" % (add_eq,),
    )
    require(minimum_add == 14, "addition floor is %r" % (minimum_add,))
    for length in range(1, 41):
        expect = length + 4 if length % 2 == 0 else length + 3
        require(weight_min(length) == expect, "weight floor formula at %d" % length)
    require(weight_min(40) == 44 and weight_min(41) == 44, "long-walk floor")


def dp_counts(nsteps):
    counts = [0] * (NMASK + 1)
    counts[0] = 1
    for _ in range(nsteps):
        nxt = [0] * (NMASK + 1)
        for mask in range(NMASK + 1):
            have = counts[mask]
            if have == 0:
                continue
            for source in range(N):
                nxt[mask ^ (1 << source)] += have
        counts = nxt
    return counts


def dp_weight4(nsteps):
    counts = dp_counts(nsteps)
    return sum(counts[mask] for mask in range(NMASK + 1) if weight(mask) == 4)


def dp_t10_matched(target):
    """Labeled 9-step words of eight singletons and one duo whose XOR is `target`."""
    counts = dp_counts(8)
    total = 0
    for duo in DUOS:
        total += counts[target ^ duo]
    return total * 9


def census_t9():
    """Eight singletons closed by their XOR. Equality needs 30 nonzero differences."""
    digits = [0] * 8
    seen_words = 0
    weight4 = 0
    best = 0
    full = 0
    covered30 = 0
    distinct = 0
    while seen_words < T9_WORDS:
        xor = 0
        state = 0
        seen = 1
        repeat = False
        for digit in digits:
            bit = BITS[digit]
            xor ^= bit
            state ^= bit
            if (seen >> state) & 1:
                repeat = True
            seen |= 1 << state
        if weight(xor) == 4:
            weight4 += 1
            if not repeat and seen.bit_count() == 9:
                distinct += 1
                points = [0]
                state = 0
                for digit in digits:
                    state ^= BITS[digit]
                    points.append(state)
                covered = difference_mask(points).bit_count()
                require(difference_mask_set(points) == difference_mask(points), "T=9 cover methods disagree")
                if covered > best:
                    best = covered
                if covered == NMASK:
                    full += 1
                if covered == NMASK - 1:
                    covered30 += 1
        seen_words += 1
        cursor = 7
        while cursor >= 0:
            digits[cursor] += 1
            if digits[cursor] < N:
                break
            digits[cursor] = 0
            cursor -= 1
        else:
            break
    require(seen_words == T9_WORDS, "T=9 census ended at %d" % seen_words)
    return weight4, best, full, covered30, distinct


def census_t11():
    """Ten singletons closed by their XOR. Full covers attain addition excess 14 at Q extra 11."""
    digits = [0] * 10
    seen_words = 0
    weight4 = 0
    full = 0
    by_size = {10: 0, 11: 0}
    saw_witness = False
    while seen_words < T11_WORDS:
        xor = 0
        state = 0
        seen = 1
        for digit in digits:
            bit = BITS[digit]
            xor ^= bit
            state ^= bit
            seen |= 1 << state
        if weight(xor) == 4:
            weight4 += 1
            distinct = seen.bit_count()
            if distinct >= 10:
                points = [0]
                state = 0
                for digit in digits:
                    state ^= BITS[digit]
                    points.append(state)
                covered_mask = difference_mask(points)
                if covered_mask == FULL:
                    require(difference_mask_set(points) == FULL, "T=11 cover methods disagree")
                    full += 1
                    by_size[distinct] = by_size.get(distinct, 0) + 1
                    if digits == [0, 1, 0, 2, 1, 0, 1, 3, 4, 3] and xor == 23:
                        saw_witness = True
        seen_words += 1
        cursor = 9
        while cursor >= 0:
            digits[cursor] += 1
            if digits[cursor] < N:
                break
            digits[cursor] = 0
            cursor -= 1
        else:
            break
    require(seen_words == T11_WORDS, "T=11 census ended at %d" % seen_words)
    require(saw_witness, "T=11 witness was not in the full-cover census")
    return weight4, full, by_size


def census_t10_target(target):
    """Nine-step words with one duo and eight singletons, XOR equal to one weight-4 mask.

    The weight-4 step is placed last by rotation. The last singleton is solved from
    the XOR equation, so each such word is visited once.
    """
    matched = 0
    full = 0
    best = 0
    saw_witness = False
    for duo_pos in range(9):
        singleton_pos = [pos for pos in range(9) if pos != duo_pos]
        solved = singleton_pos[-1]
        free = singleton_pos[:-1]
        require(len(free) == 7, "free singleton count")
        for duo in DUOS:
            digits = [0] * 7
            examined = 0
            while examined < T10_FREE:
                xor = duo
                for digit in digits:
                    xor ^= BITS[digit]
                need = target ^ xor
                if weight(need) == 1:
                    matched += 1
                    steps = [0] * 9
                    steps[duo_pos] = duo
                    for index, pos in enumerate(free):
                        steps[pos] = BITS[digits[index]]
                    steps[solved] = need
                    state = 0
                    seen = 1
                    repeat = False
                    for step in steps:
                        state ^= step
                        if (seen >> state) & 1:
                            repeat = True
                            break
                        seen |= 1 << state
                    if not repeat:
                        points = [0]
                        state = 0
                        for step in steps:
                            state ^= step
                            points.append(state)
                        covered_mask = difference_mask(points)
                        covered = covered_mask.bit_count()
                        if covered > best:
                            best = covered
                        if covered_mask == FULL:
                            require(difference_mask_set(points) == FULL, "T=10 cover methods disagree")
                            full += 1
                            if target == 15 and steps == WITNESS[:-1]:
                                saw_witness = True
                examined += 1
                cursor = 6
                while cursor >= 0:
                    digits[cursor] += 1
                    if digits[cursor] < N:
                        break
                    digits[cursor] = 0
                    cursor -= 1
                else:
                    break
            require(examined == T10_FREE, "T=10 slice ended at %d" % examined)
    return matched, full, best, saw_witness


def check_schedule(steps, expect_cost, seed):
    weights = [weight(step) for step in steps]
    require(missing_rows(steps) == 0, "schedule misses a row: %r" % (steps,))
    require(sum(weights) + READOUTS == expect_cost[1], "addition count")
    ops = build_schedule(steps)
    require(schedule_cost(ops) == expect_cost, "schedule cost %r" % (schedule_cost(ops),))
    require(evaluate_generic(ops), "generic replay failed")
    check_concrete(ops, seed)
    return ops


def check_witnesses():
    weights = [weight(step) for step in WITNESS]
    require(weights.count(4) == 1 and weights.count(2) == 1 and weights.count(1) == 8,
            "witness weights %r" % (weights,))
    require(len(prefixes(WITNESS)) == 11 and len(set(prefixes(WITNESS)[:-1])) == 10,
            "witness prefix count")
    ops = check_schedule(WITNESS, (72, 76), 20261112)
    damaged = [op for op in ops if op != ("A", 1)]
    require(not evaluate_generic(damaged), "dropping row 1 was still accepted")
    broken = list(WITNESS)
    broken[-1] = 1
    pre = prefixes(broken)
    require(pre[-1] != 0 or difference_mask(pre) != FULL, "broken witness still covers")

    weights11 = [weight(step) for step in WITNESS_11]
    require(weights11.count(4) == 1 and weights11.count(1) == 10, "T=11 weights %r" % (weights11,))
    require(all(weight(step) != 2 for step in WITNESS_11), "T=11 witness uses a duo")
    check_schedule(WITNESS_11, (73, 76), 20261113)

    duo_ops = build_schedule(DUO)
    require(schedule_cost(duo_ops) == (72, 74), "DUO control cost %r" % (schedule_cost(duo_ops),))
    require(evaluate_generic(duo_ops), "DUO control fails generic replay")
    require(all(weight(step) != 4 for step in DUO), "DUO control uses a weight-4 step")
    require(missing_rows(DUO) == 0, "DUO control misses a row")


def main():
    require(DUOS == tuple(sorted(a | b for a in BITS for b in BITS if a < b)), "duo list")
    require(tuple(weight(mask) for mask in QUADS) == (4, 4, 4, 4, 4), "quad list")
    counts = nine_and_ten_point_counts()
    require(counts[9] == 0, "nine-point normal form found %d covers" % counts[9])
    require(counts[10] == 80, "ten-point normal form count %d" % counts[10])
    check_compositions()
    check_corner()

    weight4_9, best9, full9, covered30, _distinct9 = census_t9()
    require(weight4_9 == dp_weight4(8), "T=9 DP count disagrees")
    require(weight4_9 == 115920, "T=9 weight-4 count %d" % weight4_9)
    require(best9 == 25 and full9 == 0 and covered30 == 0, "T=9 corner %r" % ((best9, full9, covered30),))

    weight4_11, full11, by_size = census_t11()
    require(weight4_11 == dp_weight4(10), "T=11 DP count disagrees")
    require(weight4_11 == 2996400, "T=11 weight-4 count %d" % weight4_11)
    require(full11 == 5760, "T=11 full covers %d" % full11)
    require(by_size == {10: 0, 11: 5760}, "T=11 size split %r" % (by_size,))

    matched_total = 0
    full_total = 0
    for target in QUADS:
        matched, full, best, saw = census_t10_target(target)
        require(matched == dp_t10_matched(target), "T=10 DP disagrees at target %d" % target)
        require(matched == 2175120, "T=10 matched %d at target %d" % (matched, target))
        require(full == 576 and best == 31, "T=10 target %d gave full=%d best=%d" % (target, full, best))
        if target == 15:
            require(saw, "T=10 witness was not in the target-15 census")
        matched_total += matched
        full_total += full
    require(matched_total == 10875600 and full_total == 2880, "T=10 totals %r" % ((matched_total, full_total),))

    check_witnesses()
    print(
        "PASS_WEIGHT4_TOGGLE_PRICE queries=72 additions=76 duo=(72,74) "
        "nine_point_covers=0 ten_point_normal=80 t9_best=25 t9_weight4=115920 "
        "t10_full=2880 t11_full=5760 t11_s10=%d t11_s11=%d t11_schedule=(73,76) "
        "no_new_kappa" % (by_size[10], by_size[11])
    )


if __name__ == "__main__":
    main()
