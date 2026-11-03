#!/usr/bin/env python3
"""Five-source dirty connector over every toggle alphabet: exact finite checks.

Standard library only; every loop has an explicit finite bound.  The model is the
five-source, 31-output interface of research/universal-connector-boundary with
every nonempty source subset S available as one complete call T_S priced
o + |S| p.  A source word is a closed walk of toggle vectors in F_2^5; two
readouts at boundaries s, t realize the row q_s XOR q_t.  Lower bounds use only
that reduction (it is the L = 1, identity-map specialization of the interface).

Checks, all exact integer arithmetic:
  1. no set of at most nine points of F_2^5 has P + P = F_2^5 (exhaustive search over
     every nine-point set containing 0, and over the affine-basis normal form);
  2. the 945 label-pairing census of length-ten singleton words (max coverage 31 of 32);
  3. the census of the 115,920 closed words with one weight-5 step and nine singletons;
  4. the DUO word (price (72, 74)) and a word with one weight-5 call (price (72, 78)):
     coverage, generic-operator replay and concrete random-operator replay of each
     72-call schedule;
  5. the inequality tables behind Q >= 72, A >= 74 and A >= 78 with a weight-5 call;
  6. rejection controls and a seeded hill-climb that must not undercut the bounds.
"""

import random
import sys
import time
from itertools import combinations

N = 5
NMASK = (1 << N) - 1          # the 31 nonzero masks 1..31
FULLBITS = ((1 << (NMASK + 1)) - 1) & ~1   # bit m set for every nonzero mask m
READOUT_FLOOR = 2 * NMASK     # two readouts for each of the 31 rows

# Published singleton and DUO words (research/universal-connector-boundary and
# research/duo-toggle-connector).  They are inputs here, not trusted results: every
# property used below is recomputed from the integers.
SINGLETON_12 = [2, 0, 2, 1, 2, 0, 3, 1, 4, 2, 3, 4]      # B2 B0 B2 B1 B2 B0 B3 B1 B4 B2 B3 B4
SINGLETON_10_MISS21 = [0, 1, 2, 0, 3, 1, 4, 2, 3, 4]      # B0 B1 B2 B0 B3 B1 B4 B2 B3 B4
DUO_WALK = [1, 2, 8, 18, 12, 16, 1, 2, 4, 2]              # step masks; 18 and 12 are DUOs
# Found here by exhaustive depth-first search (not taken from a predecessor): ten calls, one
# weight-5 call (31), two DUOs (24 = {3,4}, 10 = {1,3}) and seven singletons; W = 16.
Q5_WALK = [1, 2, 1, 4, 2, 1, 8, 24, 10, 31]

PAIRING_HISTOGRAM = {16: 42, 19: 120, 21: 180, 22: 56, 23: 45, 24: 220, 26: 110, 28: 150, 31: 22}


def wt(x):
    return x.bit_count()


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL " + message)


def prefixes(steps):
    q = 0
    out = [0]
    for s in steps:
        require(1 <= s <= NMASK, "toggle outside the nonzero masks of F_2^5: %r" % (s,))
        q ^= s
        out.append(q)
    return out


def nonzero_differences(points):
    pts = sorted(set(points))
    found = set()
    for i, a in enumerate(pts):
        for b in pts[i + 1:]:
            found.add(a ^ b)
    return found


def missing_count(steps):
    """Number u of nonzero masks that no two boundaries of the closed word realize."""
    pre = prefixes(steps)
    require(pre[-1] == 0, "source word is not closed")
    return NMASK - len(nonzero_differences(pre))


def price_floor(steps):
    """(Q, A) lower bounds for any schedule over this source word (rows read twice, plus
    four readouts for each row that no boundary pair realizes)."""
    u = missing_count(steps)
    readouts = READOUT_FLOOR + 2 * u
    return len(steps) + readouts, sum(wt(s) for s in steps) + readouts


# ---------------------------------------------------------------- 1. cover numbers

def count_covers(size):
    """Number of subsets P of F_2^5 with 0 in P, |P| = size and P + P = F_2^5.

    Exhaustive depth-first search over increasing element choices.  Adding an element to a
    k-point set creates k new pairs; pairs that repeat an earlier difference are 'waste'.
    A cover needs 31 distinct nonzero differences, so waste can never exceed
    C(size, 2) - 31; the cut is exact, not heuristic."""
    allowed = size * (size - 1) // 2 - NMASK
    if allowed < 0:
        return 0
    covers = 0

    def extend(chosen, seen, start, waste):
        nonlocal covers
        k = len(chosen)
        if k == size:
            if seen == FULLBITS:
                covers += 1
            return
        for x in range(start, NMASK + 1):
            fresh = 0
            for p in chosen:
                bit = 1 << (x ^ p)
                if not (seen & bit) and not (fresh & bit):
                    fresh |= bit
            nwaste = waste + k - fresh.bit_count()
            if nwaste <= allowed:
                chosen.append(x)
                extend(chosen, seen | fresh, x + 1, nwaste)
                chosen.pop()

    extend([0], 0, 1, 0)
    return covers


def affine_normal_form_counts():
    """Every cover contains an affine basis, and affine maps preserve P + P = F_2^5, so
    it suffices to take P containing 0, e_0..e_4 and extra points."""
    base = [0] + [1 << j for j in range(N)]
    rest = [x for x in range(1, NMASK + 1) if x not in base]
    out = {}
    for extra in (3, 4):
        count = 0
        for add in combinations(rest, extra):
            pts = base + list(add)
            if len(nonzero_differences(pts)) == NMASK:
                count += 1
        out[len(base) + extra] = count
    return out


def check_cover_numbers():
    for size in range(1, 9):
        require(size * (size - 1) // 2 < NMASK, "counting bound at size %d" % size)
    covers9 = count_covers(9)
    require(covers9 == 0, "a nine-point cover of F_2^5 exists")
    normal = affine_normal_form_counts()
    require(normal[9] == 0, "normal-form search found a nine-point cover")
    require(normal[10] == 80, "normal-form ten-point cover count changed: %r" % (normal[10],))
    pts = prefixes(DUO_WALK)[:-1]
    require(len(set(pts)) == 10 and len(nonzero_differences(pts)) == NMASK,
            "the DUO prefix set is not a ten-point cover")
    # Positive control for the pruned search: the same search finds the 99,200 ten-point
    # covers containing 0 that research/duo-toggle-connector records from a separate scan.
    covers10 = count_covers(10)
    require(covers10 == 99200, "ten-point cover count %d" % covers10)
    return covers9, normal[10], covers10


# ---------------------------------------------------------------- 2. pairing census

def matchings(positions):
    if not positions:
        yield []
        return
    first = positions[0]
    for i in range(1, len(positions)):
        rest = positions[1:i] + positions[i + 1:]
        for tail in matchings(rest):
            yield [(first, positions[i])] + tail


def check_pairing_census():
    histogram = {}
    best_missing = NMASK
    total = 0
    for matching in matchings(list(range(10))):
        word = [0] * 10
        for label, (a, b) in enumerate(matching):
            word[a] = word[b] = 1 << label
        total += 1
        u = missing_count(word)
        coverage = NMASK + 1 - u
        histogram[coverage] = histogram.get(coverage, 0) + 1
        best_missing = min(best_missing, u)
    require(total == 945, "pairing count %d" % total)
    require(histogram == PAIRING_HISTOGRAM, "pairing histogram differs: %r" % (histogram,))
    require(best_missing == 1, "a length-ten singleton word covers every mask")
    return total, best_missing


# ---------------------------------------------------------------- 3. one weight-5 step

def multiset_words(counts):
    """All distinct sequences containing label j exactly counts[j] times."""
    left = list(counts)
    length = sum(left)
    word = []

    def rec():
        if len(word) == length:
            yield tuple(word)
            return
        for j in range(len(left)):
            if left[j]:
                left[j] -= 1
                word.append(j)
                yield from rec()
                word.pop()
                left[j] += 1

    yield from rec()


def check_one_weight5_census():
    """Closed ten-step words with one weight-5 step and nine singleton steps.  Rotating a
    closed word translates its prefix set, so the weight-5 step may be last.  Closure forces
    every singleton count odd, so the counts are (5,1,1,1,1) or (3,3,1,1,1)."""
    patterns = set()
    for a in range(1, 10, 2):
        for b in range(1, 10, 2):
            for c in range(1, 10, 2):
                for d in range(1, 10, 2):
                    for e in range(1, 10, 2):
                        if a + b + c + d + e == 9:
                            patterns.add(tuple(sorted((a, b, c, d, e), reverse=True)))
    require(patterns == {(5, 1, 1, 1, 1), (3, 3, 1, 1, 1)}, "odd count patterns")
    words = 0
    best = 0
    for pattern in sorted(patterns):
        seen = set()
        for perm_counts in {tuple(p) for p in _label_assignments(pattern)}:
            if perm_counts in seen:
                continue
            seen.add(perm_counts)
            for word in multiset_words(perm_counts):
                words += 1
                point = 0
                points = [0]
                for j in word:
                    point ^= 1 << j
                    points.append(point)
                require(point == NMASK, "closure of the weight-5 word")
                count = len(nonzero_differences(points))
                if count > best:
                    best = count
    require(words == 115920, "weight-5 census size %d" % words)
    require(best == 27, "maximum distinct differences %d" % best)
    return words, best


def _label_assignments(pattern):
    # distinct arrangements of the multiset of counts over the five labels
    seen = set()
    stack = [()]
    while stack:
        part = stack.pop()
        if len(part) == len(pattern):
            seen.add(part)
            continue
        remaining = list(pattern)
        for c in part:
            remaining.remove(c)
        for c in set(remaining):
            stack.append(part + (c,))
    return seen


# ---------------------------------------------------------------- 4. schedules

def build_schedule(steps):
    """Readouts at the first boundary pair realizing each row, interleaved with the word.
    Operations: ('T', mask) a toggle call, ('A', row) a readout."""
    pre = prefixes(steps)
    first = {}
    for i in range(len(pre)):
        for j in range(i + 1, len(pre)):
            first.setdefault(pre[i] ^ pre[j], (i, j))
    at = {b: [] for b in range(len(pre))}
    extra = 0
    for m in range(1, NMASK + 1):
        if m in first:
            for b in first[m]:
                at[b].append(m)
        else:
            # four readouts: two boundary pairs whose differences XOR to m
            done = False
            for d1, (i, j) in sorted(first.items()):
                d2 = d1 ^ m
                if d2 in first:
                    k, l = first[d2]
                    if len({i, j, k, l}) == 4:
                        for b in (i, j, k, l):
                            at[b].append(m)
                        done = True
                        extra += 1
                        break
            require(done, "no four-readout repair for mask %d" % m)
    ops = []
    for b in range(len(pre)):
        ops.extend(("A", m) for m in at[b])
        if b < len(steps):
            ops.append(("T", steps[b]))
    return ops


def costs(ops):
    queries = len(ops)
    additions = sum(wt(arg) if kind == "T" else 1 for kind, arg in ops)
    return queries, additions


def evaluate_generic(ops):
    """Exact for arbitrary operators: z is a sum of the formal symbols z0 (bit 0) and
    B_j x_j (bit 1 + j); a readout adds the same formal combination, acted on by A_m, to row m.
    The schedule is correct for every admissible choice of maps and dirty data iff the final
    row m holds exactly the symbols B_j x_j with j in m and z has returned to z0."""
    z = 1
    rows = [0] * (NMASK + 1)
    for kind, arg in ops:
        if kind == "T":
            for j in range(N):
                if arg >> j & 1:
                    z ^= 1 << (1 + j)
        else:
            rows[arg] ^= z
    if z != 1:
        return False
    for m in range(1, NMASK + 1):
        want = 0
        for j in range(N):
            if m >> j & 1:
                want |= 1 << (1 + j)
        if rows[m] != want:
            return False
    return True


def evaluate_concrete(ops, rng, trials, width=3):
    """Run the schedule on random dirty data with random binary linear maps."""
    def apply(matrix, v):
        out = 0
        for i in range(width):
            if v >> i & 1:
                out ^= matrix[i]
        return out

    for _ in range(trials):
        mats_b = [[rng.randrange(1 << width) for _ in range(width)] for _ in range(N)]
        mats_a = [[rng.randrange(1 << width) for _ in range(width)] for _ in range(NMASK + 1)]
        x = [rng.randrange(1 << width) for _ in range(N)]
        z0 = rng.randrange(1 << width)
        y0 = [rng.randrange(1 << width) for _ in range(NMASK + 1)]
        z = z0
        y = list(y0)
        for kind, arg in ops:
            if kind == "T":
                for j in range(N):
                    if arg >> j & 1:
                        z ^= apply(mats_b[j], x[j])
            else:
                y[arg] ^= apply(mats_a[arg], z)
        if z != z0:
            return False
        for m in range(1, NMASK + 1):
            total = 0
            for j in range(N):
                if m >> j & 1:
                    total ^= apply(mats_b[j], x[j])
            if y[m] != y0[m] ^ apply(mats_a[m], total):
                return False
    return True


def check_schedules():
    rng = random.Random(20261103)
    duo = build_schedule(DUO_WALK)
    q, a = costs(duo)
    require((q, a) == (72, 74), "DUO schedule price %r" % ((q, a),))
    require(len(DUO_WALK) == 10 and sum(wt(s) for s in DUO_WALK) == 12, "DUO word profile")
    require(sorted(wt(s) for s in DUO_WALK).count(2) == 2, "DUO word must use two weight-2 calls")
    require(evaluate_generic(duo), "DUO schedule fails the generic-operator replay")
    require(evaluate_concrete(duo, rng, 150), "DUO schedule fails the concrete replay")

    require(prefixes(Q5_WALK)[-1] == 0 and len(Q5_WALK) == 10, "weight-5 word is not a closed ten-step walk")
    require(sorted(wt(t) for t in Q5_WALK) == [1] * 7 + [2, 2, 5], "weight-5 word step weights")
    q5 = build_schedule(Q5_WALK)
    require(costs(q5) == (72, 78), "weight-5 schedule price %r" % (costs(q5),))
    require(price_floor(Q5_WALK) == (72, 78), "weight-5 word floors")
    require(evaluate_generic(q5), "weight-5 schedule fails the generic-operator replay")
    require(evaluate_concrete(q5, rng, 150), "weight-5 schedule fails the concrete replay")

    single = build_schedule([1 << j for j in SINGLETON_12])
    require(costs(single) == (74, 74), "singleton schedule price")
    require(evaluate_generic(single) and evaluate_concrete(single, rng, 60),
            "singleton control fails")

    miss = [1 << j for j in SINGLETON_10_MISS21]
    pre = prefixes(miss)
    absent = set(range(1, NMASK + 1)) - nonzero_differences(pre)
    require(absent == {21}, "ten-call singleton control misses %r" % sorted(absent))
    repaired = build_schedule(miss)
    require(costs(repaired) == (74, 74) and evaluate_generic(repaired),
            "ten-call word with a four-readout repair")
    return q, a


# ---------------------------------------------------------------- 5. inequality tables

def u_floor(s):
    """Least number of uncovered masks when the closed word has s distinct prefix points."""
    pairs = s * (s - 1) // 2
    least = max(NMASK - pairs, 0)
    if s <= 9:
        least = max(least, 1)       # no cover of F_2^5 has at most nine points
    return least


def check_inequalities():
    best = None
    for s in range(1, 41):
        value = s + 2 * u_floor(s)            # lower bound for T + 2u since T >= s
        if best is None or value < best[0]:
            best = (value, s)
        if s != 10:
            require(value >= 11, "T + 2u floor %d at s = %d" % (value, s))
    require(best == (10, 10), "minimum of T + 2u is %r" % (best,))
    # Q >= T + 62 + 2u >= 72, with equality only if T = s = 10 and u = 0.
    # weight-5 step: W >= T + 4 per such step; W is even (closed walk).
    for T in range(1, 41):
        s_max = T
        # least u over s <= T given the table above
        u_least = min(u_floor(s) for s in range(1, s_max + 1))
        w_least = T + 4
        if w_least % 2:
            w_least += 1
        if T == 10 and w_least == 14:
            u_least = max(u_least, 1)         # the weight-5 census: nine singletons never cover
        a_floor = w_least + READOUT_FLOOR + 2 * u_least
        require(a_floor >= 78, "weight-5 addition floor %d at T = %d" % (a_floor, T))
    # two or more weight-5 steps: W >= T + 8 and T + 2u >= 10 give A >= 80
    for T in range(1, 41):
        u_least = min(u_floor(s) for s in range(1, T + 1))
        w_least = T + 8 + (T % 2)
        require(w_least + READOUT_FLOOR + 2 * u_least >= 80, "two weight-5 steps at T = %d" % T)
    return best


# ---------------------------------------------------------------- 6. controls

def hill_climb(rng, rounds, start):
    """Local search over closed words of any alphabet.  The proved floors must hold at every
    visited word; the search is expected to reach (72, 74) from the DUO start."""
    cur = list(start)
    q, a = price_floor(cur)
    best_q, best_a = q, a
    seen_weight5 = []
    for _ in range(rounds):
        cand = list(cur)
        move = rng.randrange(4)
        if move == 0 and len(cand) >= 2:
            i = rng.randrange(len(cand) - 1)
            cand[i] = rng.randrange(1, NMASK + 1)
            x = 0
            for s in cand[:-1]:
                x ^= s
            cand[-1] = x
        elif move == 1 and len(cand) < 14:
            i = rng.randrange(len(cand) + 1)
            t = rng.randrange(1, NMASK + 1)
            cand.insert(i, t)
            x = 0
            for s in cand[:-1]:
                x ^= s
            cand[-1] = x
        elif move == 2 and len(cand) > 3:
            del cand[rng.randrange(len(cand))]
            x = 0
            for s in cand[:-1]:
                x ^= s
            cand[-1] = x
        else:
            i, j = rng.randrange(len(cand)), rng.randrange(len(cand))
            cand[i], cand[j] = cand[j], cand[i]
        if len(cand) < 2 or any(not 1 <= s <= NMASK for s in cand):
            continue
        if prefixes(cand)[-1] != 0:
            continue
        cq, ca = price_floor(cand)
        require(cq >= 72 and ca >= 74, "floor violated by %r -> %r" % (cand, (cq, ca)))
        if 31 in cand:
            require(ca >= 78, "weight-5 floor violated by %r -> %r" % (cand, (cq, ca)))
            seen_weight5.append(ca)
        best_q, best_a = min(best_q, cq), min(best_a, ca)
        if (cq, ca) <= (q, a) or rng.random() < 0.15:
            cur, (q, a) = cand, (cq, ca)
    return best_q, best_a, len(seen_weight5)


def check_random_words(rng, samples):
    seen5 = 0
    low_q = low_a = None
    for _ in range(samples):
        length = rng.randrange(3, 15)
        steps = [rng.randrange(1, NMASK + 1) for _ in range(length - 1)]
        x = 0
        for s in steps:
            x ^= s
        if x == 0:
            continue
        steps.append(x)
        q, a = price_floor(steps)
        require(q >= 72 and a >= 74, "random word undercuts the floors: %r" % (steps,))
        if 31 in steps:
            seen5 += 1
            require(a >= 78, "random weight-5 word undercuts 78: %r" % (steps,))
        low_q = q if low_q is None else min(low_q, q)
        low_a = a if low_a is None else min(low_a, a)
    return seen5, low_q, low_a


def check_rejections():
    duo = build_schedule(DUO_WALK)
    controls = 0
    for i in (0, 7, 30, 71):                      # drop one operation
        broken = duo[:i] + duo[i + 1:]
        require(not evaluate_generic(broken), "generic replay accepted a dropped operation %d" % i)
        controls += 1
    wrong_row = list(duo)
    first_read = next(i for i, op in enumerate(wrong_row) if op[0] == "A")
    row = wrong_row[first_read][1]
    wrong_row[first_read] = ("A", row + 1 if row < NMASK else 1)
    require(not evaluate_generic(wrong_row), "generic replay accepted a wrong row")
    controls += 1
    open_walk = [op for op in duo if op != ("T", DUO_WALK[-1])]
    require(not evaluate_generic(open_walk), "generic replay accepted a word that does not restore z")
    controls += 1
    require(not evaluate_concrete(duo[:-1], random.Random(7), 30),
            "concrete replay accepted a truncated schedule")
    controls += 1
    # a short word cannot reach 72 queries: four steps leave nearly every row uncovered
    require(price_floor([1, 2, 1, 2])[0] > 72, "four-step word cannot reach 72")
    controls += 1
    try:
        prefixes([0])
    except SystemExit:
        controls += 1
    else:
        raise SystemExit("FAIL a zero toggle was accepted")
    return controls


def main():
    t0 = time.time()
    covers9, normal10, covers10 = check_cover_numbers()
    pairings, best_missing = check_pairing_census()
    words5, best5 = check_one_weight5_census()
    q, a = check_schedules()
    floor_value, floor_s = check_inequalities()
    rng = random.Random(20261104)
    seen5, low_q, low_a = check_random_words(rng, 30000)
    require(low_q >= 72 and low_a >= 74, "random floor")
    hq, ha, h5 = hill_climb(random.Random(11), 6000, DUO_WALK)
    require(hq >= 72 and ha >= 74, "hill-climb floor")
    controls = check_rejections()
    print("PASS_FIVE_SOURCE_TOGGLE_FRONTIER nine_point_covers=%d ten_point_covers=%d "
          "affine_ten_covers=%d pairings=%d singleton_min_missing=%d weight5_words=%d "
          "weight5_max_diff=%d witness=(%d,%d) min_T_plus_2u=%d@s=%d random_weight5=%d "
          "hill_floor=(%d,%d) controls=%d weight5_witness=(72,78) no_new_kappa"
          % (covers9, covers10, normal10, pairings, best_missing, words5, best5, q, a,
             floor_value, floor_s, seen5 + h5, hq, ha, controls))
    print("elapsed_seconds=%.1f" % (time.time() - t0), file=sys.stderr)


if __name__ == "__main__":
    main()
