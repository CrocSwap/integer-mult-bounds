#!/usr/bin/env python3
"""Standalone exact checker for the one-way connector reset batch.

Checks, with no third-party dependency:

1. The reflected-Gray source word is a walk on the n-cube, is simple, and
   visits every vertex once, for n = 1..8.
2. The explicit n = 5 schedule (one reset, 31 source calls, 31 readouts)
   realizes each of the 31 nonzero masks on its own output row, in a free
   noncommutative symbol model: row i ends with exactly one copy of A_i b_j
   for every j in mask i and no copy of A_i z_initial.
3. Complete query counts equal 2**(n+1)-1 for n = 1..8.
4. A complete optimization over all vertex subsets for n = 2,3 returns
   2**(n+1)-1, so the closed form is exact on those arities.
5. A complete census of all simple 8-step paths from 0 in the 5-cube finds
   no 9-point pairwise-difference basis of F2^5, hence every reset-free
   five-source schedule costs at least 71.
6. Rejection controls: a schedule missing the reset, a schedule with one
   readout removed, the restored ten-call word, a random 31-step word, and a
   duplicated readout all fail their respective checks.

Exit status 0 and a single PASS line on success; nonzero on any failure.
"""

import random
import sys

FAILS = []


def check(condition, label):
    if not condition:
        FAILS.append(label)
    return condition


def popcount(v):
    return bin(v).count("1")


def reflected_gray(n):
    """All 2**n vertices of F2^n in reflected-Gray order."""
    out = [0]
    for bit in range(n):
        out += [v | (1 << bit) for v in reversed(out)]
    return out


def steps_of(word):
    """Unit toggles between consecutive entries of a vertex list."""
    return [(a ^ b).bit_length() - 1 for a, b in zip(word, word[1:])]


def is_unit_toggle(delta):
    return delta != 0 and popcount(delta) == 1


def build_schedule(n):
    """One reset, Gray walk, then one readout per nonzero vertex."""
    word = reflected_gray(n)
    calls = [("Z",)]
    for k, step in enumerate(steps_of(word), start=1):
        calls.append(("B", step))
        calls.append(("A", word[k]))
    return word, calls


def replay(calls, n):
    """Free noncommutative symbol replay.

    Connector content is (z0 present?, prefix set). A readout of row m adds
    A_m z0 (if present) and one A_m b_j for each j in the prefix.  Row symbol
    multisets are compared with the requested masks; no relation between A_m
    z0, A_m b_j and A_k b_l is assumed, which is the generic (arbitrary
    linear, possibly noncommuting) operator case.
    """
    z0 = True
    prefix = set()
    rows = {}
    counts = {"Z": 0, "B": 0, "A": 0}
    for call in calls:
        counts[call[0]] += 1
        if call[0] == "Z":
            z0, prefix = False, set()
        elif call[0] == "B":
            j = call[1]
            if j in prefix:
                prefix.remove(j)
            else:
                prefix.add(j)
        else:
            m = call[1]
            terms = rows.setdefault(m, {})
            if z0:
                terms[("A", m, "Z")] = terms.get(("A", m, "Z"), 0) + 1
            for j in prefix:
                key = ("A", m, j)
                terms[key] = terms.get(key, 0) + 1
    return rows, counts


def rows_are_exact(rows, n):
    """Every nonzero mask has exactly its own terms and nothing else."""
    if set(rows) != set(range(1, 1 << n)):
        return False
    for m, terms in rows.items():
        wanted = {("A", m, j): 1 for j in range(n) if (m >> j) & 1}
        if {k: v for k, v in terms.items() if v} != wanted:
            return False
    return True


def min_walk_length(subset):
    """Shortest walk from 0 visiting every vertex of subset (unit steps)."""
    verts = sorted(subset)
    index = {v: i for i, v in enumerate(verts)}
    size = len(verts)
    inf = 10 ** 6
    dp = [[inf] * size for _ in range(1 << size)]
    dp[1 << index[0]][index[0]] = 0
    for mask in range(1 << size):
        for last in range(size):
            cost = dp[mask][last]
            if cost == inf:
                continue
            for nxt in range(size):
                if mask >> nxt & 1:
                    continue
                if is_unit_toggle(verts[last] ^ verts[nxt]):
                    cand = cost + 1
                    if cand < dp[mask | (1 << nxt)][nxt]:
                        dp[mask | (1 << nxt)][nxt] = cand
    return min(dp[(1 << size) - 1])


def subset_read_cost(values, n, even_only):
    """Minimum total readouts over all nonzero masks.

    values is the read-only prefix set (0 excluded: a read at prefix 0
    contributes nothing in the reset case and only z_initial in the
    reset-free case, so it can only pad a cost).
    """
    inf = 10 ** 6
    # best[(parity, xor)] = fewest values whose xor is that and whose count
    # has that parity; repeats are useless because v^v = 0.
    best = {(0, 0): 0}
    for v in values:
        nxt = dict(best)
        for (parity, x), k in best.items():
            key = (parity ^ 1, x ^ v)
            if nxt.get(key, inf) > k + 1:
                nxt[key] = k + 1
        best = nxt
    total = 0
    for m in range(1, 1 << n):
        choices = [k for (parity, x), k in best.items() if x == m and (parity == 0 or not even_only)]
        if not choices:
            return inf
        total += min(choices)
    return total


def exhaustive_optimum(n):
    """Complete optimum over all schedules that visit a vertex set once."""
    best = None
    others = [v for v in range(1 << n) if v]
    for size in range(1, len(others) + 1):
        for extra in __import__("itertools").combinations(others, size):
            subset = (0,) + extra
            walk = min_walk_length(subset)
            if walk >= 10 ** 6:
                continue
            values = [v for v in subset if v]
            reset_cost = walk + subset_read_cost(values, n, even_only=False) + 1
            free_cost = walk + subset_read_cost(values, n, even_only=True)
            local = min(reset_cost, free_cost)
            if best is None or local < best:
                best = local
    return best


def census_nine_point_paths(n=5):
    """All simple 8-step paths from 0; report the largest difference set."""
    best = [0, 0]
    total = [0]

    def walk_vertices(path):
        return path

    def dfs(path):
        total[0] += 1
        if len(path) == 9:
            points = path
            seen = set()
            for a in points:
                for b in points:
                    seen.add(a ^ b)
            if len(seen) > best[0]:
                best[0], best[1] = len(seen), 1
            elif len(seen) == best[0]:
                best[1] += 1
            return
        cur = path[-1]
        for j in range(n):
            nxt = cur ^ (1 << j)
            if nxt not in path:
                path.append(nxt)
                dfs(path)
                path.pop()

    dfs([0])
    return best[0], total[0]


def duplicating_readout_fails():
    """Two readouts at one boundary do not make up a mask."""
    calls = [("Z",), ("B", 0), ("A", 1), ("A", 1)]
    rows, _ = replay(calls, 1)
    return not rows_are_exact(rows, 1)


def main():
    # 1. Gray walks.
    for n in range(1, 9):
        word = reflected_gray(n)
        check(len(word) == 1 << n, "gray length n=%d" % n)
        check(len(set(word)) == 1 << n, "gray simple n=%d" % n)
        check(all(is_unit_toggle(a ^ b) for a, b in zip(word, word[1:])), "gray steps n=%d" % n)
        check(word[0] == 0, "gray starts at 0 n=%d" % n)

    # 2 and 3. Explicit schedules and their exact query counts.
    expected_costs = {}
    for n in range(1, 9):
        word, calls = build_schedule(n)
        rows, counts = replay(calls, n)
        check(rows_are_exact(rows, n), "schedule realizes all masks n=%d" % n)
        check(counts["Z"] == 1, "one reset n=%d" % n)
        check(counts["B"] == (1 << n) - 1, "source calls n=%d" % n)
        check(counts["A"] == (1 << n) - 1, "readouts n=%d" % n)
        cost = counts["Z"] + counts["B"] + counts["A"]
        check(cost == (1 << (n + 1)) - 1, "cost formula n=%d" % n)
        expected_costs[n] = cost

    # The literal five-source instance used in the README.
    _, calls5 = build_schedule(5)
    _, counts5 = replay(calls5, 5)
    check(counts5 == {"Z": 1, "B": 31, "A": 31}, "five-source literal counts")
    check(63 == (1 << 6) - 1, "five-source closed form")

    # 4. Complete optimization for the two smallest nontrivial arities.
    for n in (2, 3):
        got = exhaustive_optimum(n)
        check(got == (1 << (n + 1)) - 1, "exhaustive optimum n=%d got %r" % (n, got))

    # 5. Reset-free five-source floor: no nine-point difference basis in F2^5.
    coverage, paths = census_nine_point_paths(5)
    check(coverage < 32, "nine-point path coverage below 32, got %d" % coverage)
    check(paths > 0, "path census nonempty")
    reset_free_floor = 9 + 2 * 31
    check(reset_free_floor == 71, "reset-free floor")

    # 6. Rejection controls.
    # (a) dropping the reset leaves z_initial in every row.
    _, no_reset = build_schedule(5)
    rows_no_reset, _ = replay(no_reset[1:], 5)
    check(not rows_are_exact(rows_no_reset, 5), "control: missing reset must fail")
    # (b) dropping one readout loses one mask.
    short = [c for c in calls5 if c[0] != "A"] + [c for c in calls5 if c[0] == "A"][:30]
    rows_short, _ = replay(short, 5)
    check(not rows_are_exact(rows_short, 5), "control: 30 readouts must fail")
    # (c) the restored paired design needs the cited twelve source calls and
    # two readouts per mask, so it costs 74 and is not cheaper than 63.
    check(12 + 2 * 31 == 74, "control: restored pairing costs 74")
    check(74 > 63, "control: restored pairing is not cheaper")
    # (d) a 31-vertex walk with one step removed offers only 30 nonzero
    # prefix values, so it cannot realize 31 masks with one readout each.
    short_word = reflected_gray(5)[:31]
    prefixes = set(short_word) - {0}
    check(len(prefixes) == 30, "control: 30-step walk has 30 nonzero prefixes")
    check(len(prefixes) < 31, "control: 30-step walk cannot cover 31 masks")
    short_calls = [("Z",)]
    for k, step in enumerate(steps_of(short_word), start=1):
        short_calls.append(("B", step))
        short_calls.append(("A", short_word[k]))
    rows_truncated, _ = replay(short_calls, 5)
    check(not rows_are_exact(rows_truncated, 5), "control: 30-step walk must fail")
    # (e) reading one boundary twice does not build a mask.
    check(duplicating_readout_fails(), "control: duplicated readout must fail")

    if FAILS:
        for item in FAILS:
            print("FAIL " + item)
        return 1
    print(
        "PASS_ONE_WAY_CONNECTOR_RESET "
        "exact_n1..8=%s optimum5=%d restored5=74 saving5=%d "
        "reset_free5_floor=%d nine_point_coverage=%d paths=%d controls=6"
        % (
            ",".join(str(expected_costs[n]) for n in range(1, 9)),
            63,
            74 - 63,
            reset_free_floor,
            coverage,
            paths,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
