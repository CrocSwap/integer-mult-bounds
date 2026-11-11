#!/usr/bin/env python3
"""Exact census of normalized length-28 all-ones placements.

The argument is in README.md. This program enumerates every multiplicity
matrix for the 10640 normalized placements and applies the stated rank
tests. It does not search for a universal word.
"""

from __future__ import annotations

import sys
from concurrent.futures import ProcessPoolExecutor


COMP = tuple((a, b, 3 - a - b) for a in range(4) for b in range(4 - a))
BUDGET = {4: 6, 5: 10, 6: 14}
DOMAIN = 8 * 7 * (20 * 19 // 2)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def support_size(counts):
    size = 0
    for value in counts:
        if value:
            size += 1
    return size


def arc_counts(early, late, assignment):
    """Step multisets of the four arcs. assignment maps quad source -> (a, b, c)."""
    forward = [0] * 8
    backward = [0] * 8
    forward_late = [0] * 8
    backward_late = [0] * 8
    for source in range(early + 1, 8):
        forward[source] += 1
    for source in range(early):
        backward[source] += 1
    backward[late] += 1
    for source in range(late + 1, 8):
        forward_late[source] += 1
    forward_late[early] += 1
    for source in range(late):
        backward_late[source] += 1
    for source, (left, middle, right) in assignment:
        forward[source] += left
        backward[source] += middle + right
        forward_late[source] += left + middle
        backward_late[source] += right
    return forward, backward, forward_late, backward_late


def ranks_at_least_four(arcs):
    return all(support_size(arc) >= 4 for arc in arcs)


def budget_ok(forward, backward):
    rank_forward = support_size(forward)
    rank_backward = support_size(backward)
    ordered = (rank_forward, rank_backward)
    if rank_forward > rank_backward:
        ordered = (rank_backward, rank_forward)
    if ordered not in ((4, 7), (5, 7), (6, 7), (7, 7)):
        return False
    small_rank = ordered[0]
    if small_rank == 7:
        return True
    if rank_forward < rank_backward:
        small, large = forward, backward
    else:
        small, large = backward, forward
    covered = 0
    for source in range(8):
        if small[source]:
            covered += large[source]
    return covered >= BUDGET[small_rank]


def both_budgets(arcs):
    return budget_ok(arcs[0], arcs[1]) and budget_ok(arcs[2], arcs[3])


def search(early, late, left, middle, right, accept):
    """Return one accepted assignment, or None. Prunes only infeasible partial sums."""
    quads = [source for source in range(8) if source != early and source != late]
    chosen = [None] * 6

    def walk(index, used_left, used_middle, used_right):
        if used_left > left or used_middle > middle or used_right > right:
            return None
        remaining = 6 - index
        if (left - used_left > 3 * remaining or middle - used_middle > 3 * remaining
                or right - used_right > 3 * remaining):
            return None
        if index == 6:
            if (used_left, used_middle, used_right) != (left, middle, right):
                return None
            assignment = tuple((quads[pos], chosen[pos]) for pos in range(6))
            if accept(arc_counts(early, late, assignment)):
                return assignment
            return None
        room_left = left - used_left
        room_middle = middle - used_middle
        room_right = right - used_right
        for add_left, add_middle, add_right in COMP:
            if add_left > room_left or add_middle > room_middle or add_right > room_right:
                continue
            chosen[index] = (add_left, add_middle, add_right)
            found = walk(index + 1, used_left + add_left, used_middle + add_middle,
                         used_right + add_right)
            if found is not None:
                return found
        return None

    return walk(0, 0, 0, 0)


def forced_short(early, left):
    """Forward rank is at most (7 - early) + left, hence below 4."""
    return left < early - 3


def forced_long(early, left):
    """Source 0 reappears after at least 16 suffix steps, so its back arc has rank at most 3."""
    return early == 0 and left >= 16


def scan_arcs(word, source):
    positions = [index for index, label in enumerate(word) if label == source]
    require(len(positions) == 2, "scan source does not occur twice")
    start, stop = positions
    forward = word[start + 1:stop]
    backward = word[stop + 1:] + word[:start]
    return forward, backward


def word_from_assignment(early, late, left_steps, middle_steps, right_steps):
    suffix = list(left_steps) + [early] + list(middle_steps) + [late] + list(right_steps)
    require(len(suffix) == 20, "suffix length")
    return tuple(range(8)) + tuple(suffix)


def expand(assignment, segment):
    steps = []
    for source, triple in assignment:
        steps.extend([source] * triple[segment])
    return steps


def scan_matches_formula(early, late, assignment):
    arcs = arc_counts(early, late, assignment)
    word = word_from_assignment(
        early, late, expand(assignment, 0), expand(assignment, 1), expand(assignment, 2))
    scanned = scan_arcs(word, early), scan_arcs(word, late)
    formula = (arcs[0], arcs[1]), (arcs[2], arcs[3])
    for (forward, backward), (got_forward, got_backward) in zip(formula, scanned):
        for source in range(8):
            require(forward[source] == got_forward.count(source), "forward multiset mismatch")
            require(backward[source] == got_backward.count(source), "backward multiset mismatch")
    require(support_size(arcs[0]) <= 3, "explicit short-prefix witness was not rank at most 3")
    return word


def brute_rank(early, late, left, middle, right):
    """Independent enumeration used when the first segment is empty."""
    require(left == 0, "brute control is the empty-prefix slice")
    quads = [source for source in range(8) if source != early and source != late]
    found_rank = False
    found_budget = False

    def walk(index, assignment, used_middle, used_right):
        nonlocal found_rank, found_budget
        if found_rank and found_budget:
            return
        if used_middle > middle or used_right > right:
            return
        remaining = 6 - index
        if middle - used_middle > 3 * remaining or right - used_right > 3 * remaining:
            return
        if index == 6:
            if used_middle != middle or used_right != right:
                return
            arcs = arc_counts(early, late, tuple(assignment))
            if ranks_at_least_four(arcs):
                found_rank = True
            if both_budgets(arcs):
                found_budget = True
            return
        for add_middle, add_right in ((0, 3), (1, 2), (2, 1), (3, 0)):
            assignment.append((quads[index], (0, add_middle, add_right)))
            walk(index + 1, assignment, used_middle + add_middle, used_right + add_right)
            assignment.pop()

    walk(0, [], 0, 0)
    return found_rank, found_budget


def classify_slot(early, late, left, middle, right):
    short = forced_short(early, left)
    long = forced_long(early, left)
    if short or long:
        rank_hit = None
        budget_hit = None
    else:
        budget_hit = search(early, late, left, middle, right, both_budgets)
        if budget_hit is not None:
            rank_hit = budget_hit
        else:
            rank_hit = search(early, late, left, middle, right, ranks_at_least_four)
    if left == 0:
        brute_rank_hit, brute_budget_hit = brute_rank(early, late, left, middle, right)
        require((rank_hit is not None) == brute_rank_hit, "empty-prefix rank search disagreed with brute force")
        require((budget_hit is not None) == brute_budget_hit,
                "empty-prefix budget search disagreed with brute force")
        require(not (short or long) or (not brute_rank_hit and not brute_budget_hit),
                "a forced placement survived the brute enumeration")
    return rank_hit is not None, budget_hit is not None, short, long


def census_prefix(first_suffix_index):
    rank_survivors = 0
    budget_survivors = 0
    short_count = 0
    long_count = 0
    rank_pairs = set()
    budget_pairs = set()
    witness = None
    for second in range(first_suffix_index + 1, 20):
        left = first_suffix_index
        middle = second - first_suffix_index - 1
        right = 19 - second
        for early in range(8):
            for late in range(8):
                if early == late:
                    continue
                rank_ok, budget_survives, short, long = classify_slot(
                    early, late, left, middle, right)
                if short:
                    short_count += 1
                    require(not rank_ok and not budget_survives, "short-prefix placement survived")
                if long:
                    long_count += 1
                    require(not rank_ok and not budget_survives, "long-prefix placement survived")
                if rank_ok:
                    rank_survivors += 1
                    rank_pairs.add((early, late) if early < late else (late, early))
                if budget_survives:
                    budget_survivors += 1
                    budget_pairs.add((early, late) if early < late else (late, early))
                    if witness is None:
                        witness = (early, late, left, middle, right)
    return rank_survivors, budget_survivors, short_count, long_count, rank_pairs, budget_pairs, witness


def explicit_controls():
    # early = 7, three identical steps, then the two doubles, then the other quads.
    assignment = (
        (1, (3, 0, 0)),
        (2, (0, 0, 3)),
        (3, (0, 0, 3)),
        (4, (0, 0, 3)),
        (5, (0, 0, 3)),
        (6, (0, 0, 3)),
    )
    word = scan_matches_formula(7, 0, assignment)
    require(word[:8] == tuple(range(8)), "normalized interval")
    require(len(word) == 28, "word length")
    require(forced_short(7, 3) and not forced_short(7, 4), "short-prefix threshold")
    require(forced_long(0, 16) and not forced_long(0, 15), "long-prefix threshold")
    require(not forced_short(3, 0) and not forced_long(1, 18), "lemmas do not fire off their hypotheses")
    # A feasible empty-prefix matrix: every quad uses the final segment.
    feasible = tuple((source, (0, 0, 3)) for source in range(2, 8))
    arcs = arc_counts(0, 1, feasible)
    require(ranks_at_least_four(arcs) and both_budgets(arcs), "explicit (0, 1) matrix failed")
    require(search(0, 1, 0, 0, 18, both_budgets) is not None, "search missed the explicit matrix")
    # The two suffix doubles are adjacent and first. Late source 5 then sees only {0, 6, 7}.
    adjacent = tuple((source, (0, 0, 3)) for source in (1, 2, 3, 4, 6, 7))
    adjacent_arcs = arc_counts(0, 5, adjacent)
    require(support_size(adjacent_arcs[2]) == 3, "adjacent doubles did not have forward rank 3")
    require(not forced_short(0, 0) and not forced_long(0, 0), "adjacent example is outside the length lemmas")
    require(search(0, 5, 0, 0, 18, ranks_at_least_four) is None, "adjacent example survived rank at least 4")


def direct_lemma_counts():
    short = long = 0
    for left in range(20):
        slots = 19 - left
        for early in range(8):
            if forced_short(early, left):
                short += 7 * slots
            if forced_long(early, left):
                long += 7 * slots
    require(short == 1260, "short-prefix family size")
    require(long == 42, "long-prefix family size")
    return short, long


def main():
    explicit_controls()
    lemma_short, lemma_long = direct_lemma_counts()
    with ProcessPoolExecutor(max_workers=4) as pool:
        parts = list(pool.map(census_prefix, range(20)))
    rank_survivors = budget_survivors = short_count = long_count = 0
    rank_pairs = set()
    budget_pairs = set()
    for part in parts:
        rank_survivors += part[0]
        budget_survivors += part[1]
        short_count += part[2]
        long_count += part[3]
        rank_pairs |= part[4]
        budget_pairs |= part[5]
    require(short_count == lemma_short and long_count == lemma_long, "census missed a lemma placement")
    require(0 <= budget_survivors <= rank_survivors <= DOMAIN, "survivor counts are not nested")
    require(len(rank_pairs) == 28, "rank-at-least-4 deleted a label pair")
    require(len(budget_pairs) == 28, "cited budget deleted a label pair")
    # Locked totals from the exhaustive enumeration. short_prefix and long_prefix
    # are the two written families; the rest of the rank obstruction is the census.
    require(rank_survivors == 8130, "rank-at-least-4 survivor count")
    require(budget_survivors == 6171, "cited-budget survivor count")
    impossible_rank = DOMAIN - rank_survivors
    impossible_budget = DOMAIN - budget_survivors
    print(
        "PASS_LENGTH28_ALLONES_PLACEMENT"
        f" domain={DOMAIN}"
        f" rank4_survivors={rank_survivors}"
        f" rank4_impossible={impossible_rank}"
        f" budget_survivors={budget_survivors}"
        f" budget_impossible={impossible_budget}"
        f" pairs=28"
        f" short_prefix={short_count}"
        f" long_prefix={long_count}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
