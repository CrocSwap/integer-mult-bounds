#!/usr/bin/env python3
"""Exact meet-in-the-middle search in the paid two-generator Dic_3 model."""

from __future__ import annotations

from collections import deque
from hashlib import sha256
from functools import lru_cache
import itertools
import json


N_GROUP = 12
RING_ONE = 1  # coefficient of e = a^0 b^0
GENERATORS = (1, 6)  # u=a and v=b in the normal form a^i b^j


def group_mul(x: int, y: int) -> int:
    """Multiply a^i b^j, with i in Z/6 and j in {0,1}."""
    i, j = x % 6, x // 6
    k, ell = y % 6, y // 6
    out_i = (i + (-1 if j else 1) * k + (3 if j and ell else 0)) % 6
    return out_i + 6 * ((j + ell) % 2)


GROUP_TABLE = tuple(tuple(group_mul(x, y) for y in range(N_GROUP))
                    for x in range(N_GROUP))
GROUP_INVERSE = tuple(next(y for y in range(N_GROUP)
                           if GROUP_TABLE[x][y] == 0 and GROUP_TABLE[y][x] == 0)
                         for x in range(N_GROUP))


@lru_cache(maxsize=None)
def ring_mul(x: int, y: int) -> int:
    """Multiply coefficient masks in F2[Dic_3]."""
    out = 0
    while x:
        xb = x & -x
        i = xb.bit_length() - 1
        x ^= xb
        yy = y
        while yy:
            yb = yy & -yy
            j = yb.bit_length() - 1
            yy ^= yb
            out ^= 1 << GROUP_TABLE[i][j]
    return out


IDENTITY = (RING_ONE, 0, 0,
            0, RING_ONE, 0,
            0, 0, RING_ONE)


def mat_mul(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    out = []
    for i in range(3):
        for j in range(3):
            z = 0
            for k in range(3):
                z ^= ring_mul(a[3 * i + k], b[3 * k + j])
            out.append(z)
    return tuple(out)


def projector_rows() -> list[tuple[int, ...]]:
    result = []
    for x in range(1, 8):
        for y in range(1, 8):
            if (x & y).bit_count() & 1:
                result.append(tuple(((x >> i) & 1) * ((y >> j) & 1)
                                    for i in range(3) for j in range(3)))
    if len(result) != 28 or len(set(result)) != 28:
        raise RuntimeError("rank-one idempotent census is not 28")
    return result


PROJECTORS = projector_rows()
OPS: list[tuple[str, tuple[int, ...], tuple[int, ...]]] = []


def paid_matrix(g: int, n: tuple[int, ...]) -> tuple[int, ...]:
    delta = (1 << g) ^ RING_ONE
    return tuple((IDENTITY[k] ^ (delta if n[k] else 0)) for k in range(9))


for label, g in zip(("u", "v"), GENERATORS):
    for n in PROJECTORS:
        OPS.append((label, n, paid_matrix(g, n)))

OP_INDEX = {(label, n): i for i, (label, n, _) in enumerate(OPS)}


def make_ops() -> tuple[list[tuple[int, ...]], list[tuple[int, ...]]]:
    mats, invs = [], []
    for label, n, mat in OPS:
        g = GENERATORS[0 if label == "u" else 1]
        mats.append(mat)
        invs.append(paid_matrix(GROUP_INVERSE[g], n))
    return mats, invs


OP_MATS, OP_INVS = make_ops()


def word_product(word: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    out = IDENTITY
    for i in word:
        out = mat_mul(out, OP_MATS[i])
    return out


def inverse_word_product(word: tuple[int, ...]) -> tuple[int, ...]:
    out = IDENTITY
    for i in reversed(word):
        out = mat_mul(out, OP_INVS[i])
    return out


def word_distances() -> tuple[dict[int, int], dict[int, tuple[str, ...]]]:
    # Positive words in exactly {u,v}; inverses are not free letters.
    dist = {0: 0}
    words: dict[int, tuple[str, ...]] = {0: ()}
    queue = deque([0])
    while queue:
        x = queue.popleft()
        for label, g in zip(("u", "v"), GENERATORS):
            y = GROUP_TABLE[x][g]
            if y not in dist:
                dist[y] = dist[x] + 1
                words[y] = words[x] + (label,)
                queue.append(y)
    if len(dist) != N_GROUP:
        raise RuntimeError("positive {u,v} alphabet failed to reach Dic_3")
    return dist, words


DIST, SHORTEST_WORD = word_distances()


def target_matrix(w: tuple[int, int, int]) -> tuple[int, ...]:
    out = [0] * 9
    for i, g in enumerate(w):
        out[3 * i + i] = 1 << g
    return tuple(out)


def right_monomial_shift(mask: int, g: int) -> int:
    out = 0
    while mask:
        b = mask & -mask
        i = b.bit_length() - 1
        mask ^= b
        out ^= 1 << GROUP_TABLE[i][g]
    return out


def all_products(max_depth: int) -> tuple[dict[tuple[int, ...], tuple[int, ...]], list[int]]:
    """Return every distinct product through max_depth, with a shortest word."""
    result: dict[tuple[int, ...], tuple[int, ...]] = {IDENTITY: ()}
    frontier = {IDENTITY: ()}
    by_depth = [1]
    for _depth in range(1, max_depth + 1):
        next_frontier: dict[tuple[int, ...], tuple[int, ...]] = {}
        for mat, word in frontier.items():
            for i, op in enumerate(OP_MATS):
                product = mat_mul(mat, op)
                if product not in result:
                    representative = word + (i,)
                    result[product] = representative
                    next_frontier[product] = representative
        by_depth.append(len(next_frontier))
        frontier = next_frontier
        if not frontier:
            break
    return result, by_depth


def search_domain(max_calls: int, minimum_direct_bill: int,
                  prefixes: dict[tuple[int, ...], tuple[int, ...]],
                  suffixes: dict[tuple[int, ...], tuple[int, ...]]) -> dict:
    prefix_rows = [(p, inverse_word_product(w), w) for p, w in prefixes.items()]
    endpoints = []
    hits = []
    endpoint_count = 0
    best = None
    for w in itertools.product(range(N_GROUP), repeat=3):
        direct = sum(DIST[g] for g in w)
        if direct < minimum_direct_bill:
            continue
        endpoint_count += 1
        t = target_matrix(w)
        shortest_hit = None
        for p, pinv, pword in prefix_rows:
            needed = tuple(right_monomial_shift(pinv[3 * i + j], w[j])
                           for i in range(3) for j in range(3))
            # All entries are right-multiplied by the diagonal monomial in their column.
            qword = suffixes.get(needed)
            if qword is None:
                continue
            full = pword + qword
            if len(full) > max_calls:
                raise RuntimeError("meet-in-the-middle exceeded its declared depth")
            # The exact product check guards the right-shift convention and table order.
            if word_product(full) != t:
                raise RuntimeError("reported meet-in-the-middle word fails exact replay")
            key = (len(full), full)
            if shortest_hit is None or key < shortest_hit[0]:
                shortest_hit = (key, full)
        if shortest_hit:
            full = shortest_hit[1]
            item = {
                "target": list(w),
                "target_names": [f"a^{g % 6}b^{g // 6}" for g in w],
                "direct_generator_bill": direct,
                "word_length": len(full),
                "saving": direct - len(full),
                "word": [[OPS[i][0], list(OPS[i][1])] for i in full],
                "op_indices": list(full),
            }
            hits.append(item)
            candidate = (-item["saving"], item["word_length"], tuple(w), item)
            if best is None or candidate[:3] < best[:3]:
                best = candidate
        else:
            endpoints.append(list(w))

    # Canonical coverage receipt over every eligible endpoint and its outcome.
    coverage = {
        "max_calls": max_calls,
        "minimum_direct_bill": minimum_direct_bill,
        "endpoint_count": endpoint_count,
        "targets_with_word_at_most_cap": len(hits),
        "targets_without_word_at_most_cap": len(endpoints),
        "hit_tuples": [x["target"] for x in hits],
        "miss_tuples": endpoints,
    }
    digest = sha256(json.dumps(coverage, separators=(",", ":")).encode()).hexdigest()
    return {
        "max_calls": max_calls,
        "minimum_direct_bill": minimum_direct_bill,
        "endpoint_count": endpoint_count,
        "eligible_targets_with_word": len(hits),
        "eligible_targets_without_word": len(endpoints),
        "hits": hits,
        "best": None if best is None else best[3],
        "coverage_sha256": digest,
    }


def search() -> dict:
    prefixes, prefix_counts = all_products(2)
    suffixes_three, suffix_counts = all_products(3)
    initial = search_domain(4, 5, prefixes, prefixes)
    pivot = search_domain(5, 6, prefixes, suffixes_three)
    return {
        "group": "Dic_3",
        "presentation": "u^6=e; v^2=u^3; vuv^-1=u^-1",
        "paid_alphabet": ["u", "v"],
        "registers": 3,
        "rank_one_idempotents": len(PROJECTORS),
        "paid_operation_types": len(OPS),
        "group_elements": N_GROUP,
        "positive_generator_distances": {str(i): DIST[i] for i in range(N_GROUP)},
        "positive_generator_words": {str(i): list(SHORTEST_WORD[i]) for i in range(N_GROUP)},
        "raw_ordered_words_by_exact_depth": {str(d): 56 ** d for d in range(6)},
        "distinct_products_by_minimum_depth": {str(i): n for i, n in enumerate(prefix_counts)},
        "distinct_products_by_minimum_depth_through_three": {str(i): n for i, n in enumerate(suffix_counts)},
        "depth_four_stage": initial,
        "depth_five_pivot": pivot,
    }


if __name__ == "__main__":
    print(json.dumps(search(), sort_keys=True, indent=2))
