"""Seven-query even-subset readout floor for the five-source mutable-source alphabet.

Self-contained relative to PR1898 / PR2455 / the path-lowered 789q invoice /
the seven-query XOR floor (#2643). Prepared by Wentao Li with substantial AI
assistance. Apache-2.0.
"""
from __future__ import annotations

import itertools
from collections import Counter
from itertools import combinations, permutations


def need(ok, message):
    if not ok:
        raise ValueError(message)


def min_even_subset_R(slots):
    """Minimum total even-subset readout count on connector prefix slots.

    ``slots[0]`` must be 0. The final restored 0 is identified with slot 0, so
    ``slots`` lists the Q connector states before the closing query edge.
    """
    need(type(slots) is tuple and slots and slots[0] == 0, "slots must start at 0")
    n = len(slots)
    best = [99] * 32
    for bits in range(1 << n):
        if bits.bit_count() % 2:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        size = bits.bit_count()
        if size < best[value]:
            best[value] = size
    if any(best[mask] >= 99 for mask in range(1, 32)):
        return None
    return sum(best[1:])


def even_subset_image(slots):
    n = len(slots)
    image = set()
    for bits in range(1 << n):
        if bits.bit_count() % 2:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        image.add(value)
    return image


def even_subset_reads(slots):
    n = len(slots)
    reads = {}
    for mask in range(1, 32):
        found = None
        for size in range(2, n + 1, 2):
            for subset in combinations(range(n), size):
                value = 0
                for i in subset:
                    value ^= slots[i]
                if value == mask:
                    found = subset
                    break
            if found is not None:
                break
        need(found is not None, f"mask {mask} uncovered")
        reads[mask] = found
    return reads


def path_X(closed):
    """Paid source-XOR count under path-local compute/uncompute lowering."""
    total = 0
    for a, b in zip(closed, closed[1:]):
        delta = a ^ b
        need(delta != 0, "zero query edge")
        total += 2 * (delta.bit_count() - 1)
    return total


def rank_f2(vectors, dim=5):
    mat = list(vectors)
    rank = 0
    for bit in range(dim):
        pivot = next((i for i in range(rank, len(mat)) if mat[i] >> bit & 1), None)
        if pivot is None:
            continue
        mat[rank], mat[pivot] = mat[pivot], mat[rank]
        for i in range(len(mat)):
            if i != rank and mat[i] >> bit & 1:
                mat[i] ^= mat[rank]
        rank += 1
    return rank


def rank_increments(closed):
    return rank_f2([closed[i] ^ closed[i + 1] for i in range(len(closed) - 1)])


def valid_walk_slots(slots):
    """Closed Q=7 walk: start at 0, no zero edges, return edge to 0 present."""
    if type(slots) is not tuple or len(slots) != 7 or slots[0] != 0:
        return False
    if slots[-1] == 0:
        return False
    if any(slots[i] == slots[i + 1] for i in range(6)):
        return False
    return True


def path_word(closed):
    need(closed[0] == closed[-1] == 0, "path is not closed")
    slots = tuple(closed[:-1])
    reads = even_subset_reads(slots)
    word = []
    for step, point in enumerate(closed):
        word += [["R", mask] for mask, subset in reads.items() if step in subset]
        if step + 1 >= len(closed):
            break
        delta = point ^ closed[step + 1]
        need(delta != 0, "zero query edge")
        target = (delta & -delta).bit_length() - 1
        donors = [j for j in range(5) if j != target and delta >> j & 1]
        word += [["X", j, target] for j in donors]
        word.append(["Q", target])
        word += [["X", j, target] for j in reversed(donors)]
    return word


def root_ops(word, n=5):
    out = []
    for event in word:
        kind = event[0]
        if kind == "Q":
            out.append(["B", f"x{event[1]}", "z"])
        elif kind == "R":
            out.append([f"A{event[1]}", "z", f"y{event[1]}"])
        elif kind == "X":
            out.append(["", f"x{event[1]}", f"x{event[2]}"])
        else:
            raise ValueError("unknown root operation")
    return out


def roles(n=5):
    return [f"x{j}" for j in range(n)] + [f"y{m}" for m in range(1, 1 << n)] + ["z"] + [
        f"w{j}" for j in range(3)
    ]


def interpret(operations, names, initial=None):
    state = {r: {(r,)} for r in names} if initial is None else {r: set(p) for r, p in initial.items()}
    for coefficient, source, target in operations:
        need(source in state and target in state and source != target, "invalid port")
        terms = state[source] if coefficient == "" else {(coefficient,) + term for term in state[source]}
        state[target].symmetric_difference_update(terms)
    return state


def expected(n=5):
    state = {r: {(r,)} for r in roles(n)}
    for mask in range(1, 1 << n):
        for j in range(n):
            if mask >> j & 1:
                state[f"y{mask}"].symmetric_difference_update({(f"A{mask}", "B", f"x{j}")})
    return state


def check_identity(word, n=5):
    ops = root_ops(word, n)
    result = interpret(ops, roles(n))
    need(result == expected(n), "dirty root map or restoration failed")
    need(
        interpret(ops[::-1], roles(n), result) == {r: {(r,)} for r in roles(n)},
        "root inverse failed",
    )
    return Counter(event[0] for event in word)


def invoice(word):
    counts = Counter(event[0] for event in word)
    leaves = 28 * counts["Q"] + counts["R"]
    nodes = 9 * counts["Q"]
    dispatch = len(word)
    return {
        "Q": counts["Q"],
        "R": counts["R"],
        "X": counts["X"],
        "map_leaves": leaves,
        "echo_nodes": nodes,
        "root_dispatches": dispatch,
        "borrowed_dirty_rows": 4,
        "tariff": leaves + nodes + counts["X"] + dispatch,
        "complete_prices": {"b": 38, "a": 2, "x": 2},
    }


def tariff_qrx(q, r, x):
    """Abstract complete-call tariff at (b,a,x)=(38,2,2)."""
    leaves = 28 * q + r
    nodes = 9 * q
    dispatch = q + r + x
    return leaves + nodes + x + dispatch


def enumerate_distinct6_R_spectrum():
    """Exhaust all distinct nonzero 6-slot sets; return covering R spectrum."""
    histogram = Counter()
    covering = 0
    witnesses = {}
    for nonzero in combinations(range(1, 32), 6):
        slots = (0,) + nonzero
        total = min_even_subset_R(slots)
        if total is None:
            continue
        covering += 1
        histogram[total] += 1
        witnesses.setdefault(total, slots)
    attainable = sorted(histogram)
    return {
        "covering_sets": covering,
        "attainable_R": attainable,
        "histogram": {str(r): histogram[r] for r in attainable},
        "first_witnesses": {str(r): list(witnesses[r]) for r in attainable},
        "min_R": attainable[0] if attainable else None,
    }


def repeat_layer_basis_census():
    """Valid Q=7 walks on the standard basis with exactly one repeated vertex.

    Any covering walk whose distinct nonzero slots form a spanning 5-set is
    GL(5)-equivalent to a walk on {0,1,2,4,8,16} with the same multiplicity
    pattern; even-subset total R is GL-invariant. Dependent 5-sets cannot
    span F2^5, so their even-subset image misses masks.
    """
    labels = (1, 2, 4, 8, 16)
    hist = Counter()
    covering = 0
    best = None
    witness = None

    # Extra visit to 0 (second 0 in slots[1..5]); each basis vector once.
    for j in range(1, 6):
        rest = [i for i in range(1, 7) if i != j]
        for perm in permutations(labels):
            slots = [0] * 7
            slots[j] = 0
            for pos, val in zip(rest, perm):
                slots[pos] = val
            slots_t = tuple(slots)
            if not valid_walk_slots(slots_t):
                continue
            total = min_even_subset_R(slots_t)
            if total is None:
                continue
            covering += 1
            hist[total] += 1
            if best is None or total < best:
                best = total
                witness = slots_t

    # One basis vector doubled; others once; 0 only at the start.
    for dbl_idx in range(5):
        others = [labels[i] for i in range(5) if i != dbl_idx]
        for p1, p2 in combinations(range(1, 7), 2):
            rest_pos = [i for i in range(1, 7) if i not in (p1, p2)]
            for perm in permutations(others):
                slots = [0] * 7
                slots[p1] = slots[p2] = labels[dbl_idx]
                for pos, val in zip(rest_pos, perm):
                    slots[pos] = val
                slots_t = tuple(slots)
                if not valid_walk_slots(slots_t):
                    continue
                total = min_even_subset_R(slots_t)
                if total is None:
                    continue
                covering += 1
                hist[total] += 1
                if best is None or total < best:
                    best = total
                    witness = slots_t

    attainable = sorted(hist)
    return {
        "kind": "one_repeat_on_standard_basis",
        "covering_walks": covering,
        "attainable_R": attainable,
        "histogram": {str(r): hist[r] for r in attainable},
        "min_R": best,
        "first_witness": list(witness) if witness is not None else None,
        "argument": (
            "GL(5) reduces every spanning 5-set one-repeat covering walk to this "
            "basis census; R totals are invariant. Only R=96 occurs."
        ),
    }


def span_obstruction_samples():
    """Dependent nonzero sets cannot cover: even-subset image stays in a proper subspace."""
    samples = []
    # Rank-4 (omit one basis vector) and a rank-3 dependent 5-set.
    for labels, note in (
        ((1, 2, 4, 8), "rank4_omit_16"),
        ((1, 2, 3, 4, 5), "rank3_dependent_five"),
        ((1, 2, 4, 8, 3), "rank4_five_with_sum"),
    ):
        best_image = 0
        alphabet = (0,) + tuple(labels)
        for multi in itertools.combinations_with_replacement(alphabet, 6):
            image = even_subset_image((0,) + multi)
            best_image = max(best_image, len(image))
        samples.append(
            {
                "labels": list(labels),
                "rank": rank_f2(labels),
                "best_even_subset_image_size": best_image,
                "covers_all_31": best_image >= 32,
                "note": note,
            }
        )
    return samples


# Credited path-lowered champion from the 789q / #2643 lineage.
CHAMPION_7 = (0, 1, 2, 6, 12, 24, 16, 0)
