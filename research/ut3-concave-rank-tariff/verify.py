#!/usr/bin/env python3
"""Exact finite checks for the written UT3 concave-tariff theorem. Apache-2.0."""

from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_W = 32
MAX_PARTITION_SUM = 14


def require(condition, message):
    if not condition:
        raise ValueError(message)


def packed_ranks(w, k):
    require(type(w) is int and type(k) is int and 1 <= w <= MAX_W and k >= 1,
            "fixture requires integer 1 <= w <= 32 and k >= 1")
    cap = min(w, k)
    copies, remainder = divmod(2 * w, cap)
    return (cap,) * copies + ((remainder,) if remainder else ())


def supports(w, k):
    """Realize the extremal degree sequence by pairing its largest two stubs."""
    remaining = list(packed_ranks(w, k))
    masks = [0] * len(remaining)
    for coordinate in range(w):
        order = sorted((-degree, j) for j, degree in enumerate(remaining))
        first, second = order[0][1], order[1][1]
        require(remaining[second] > 0, "degree sequence cannot be paired")
        for j in (first, second):
            masks[j] |= 1 << coordinate
            remaining[j] -= 1
        assert sum(remaining) == 2 * (w - coordinate - 1)
        assert max(remaining) <= w - coordinate - 1
    require(not any(remaining), "unpaired degree stubs")
    require(tuple(mask.bit_count() for mask in masks) == packed_ranks(w, k),
            "construction changed its rank profile")
    return tuple(masks)


def balanced_supports(w, k):
    """Reproduce only the predecessor's stated cyclic incidence formula."""
    count = max(2, (2 * w + k - 1) // k)
    masks = [0] * count
    for i in range(w):
        masks[2 * i % count] |= 1 << i
        masks[(2 * i + 1) % count] |= 1 << i
    return tuple(masks)


def word_from_supports(masks):
    return tuple((letter, mask) for mask in masks for letter in (1, 2))


def group_product(g, h):
    u, v, z = g & 1, (g >> 1) & 1, (g >> 2) & 1
    U, V, Z = h & 1, (h >> 1) & 1, (h >> 2) & 1
    return (u ^ U) | ((v ^ V) << 1) | ((z ^ Z ^ (u & V)) << 2)


def formal_endpoint(word, roles):
    """Full diagonal group-algebra operator, not a quotient or sampled input."""
    endpoint = [0] * roles
    for letter, mask in word:
        for i in range(roles):
            if mask & (1 << i):
                endpoint[i] = group_product(letter, endpoint[i])
    return tuple(endpoint)


def literal_address(g):
    return (1 | ((g & 1) << 1) | (((g >> 2) & 1) << 2),
            2 | (((g >> 1) & 1) << 2), 4)


def literal_product(left, right):
    rows = []
    for row in left:
        value = 0
        for j in range(3):
            if row & (1 << j):
                value ^= right[j]
        rows.append(value)
    return tuple(rows)


def regular_endpoint(word, roles):
    """Independent faithful address action, using literal binary 3-by-3 matrices."""
    addresses = tuple(literal_address(g) for g in range(8))
    columns = []
    for i in range(roles):
        for original in addresses:
            current = original
            for letter, mask in word:
                if mask & (1 << i):
                    current = literal_product(literal_address(letter), current)
            columns.append((i, addresses.index(current)))
    return tuple(columns)


def invoice(word, roles, k):
    require(1 <= roles <= MAX_W + 2, "fixture role bound")
    require(len(word) <= 4 * MAX_W, "fixture call bound")
    profiles = [[], []]
    for letter, mask in word:
        require(letter in (1, 2), "unpaid address letter")
        require(type(mask) is int and 0 < mask < 1 << roles, "invalid support")
        rank = mask.bit_count()
        require(rank <= k, "rank cap violated")
        profiles[letter - 1].append(rank)
    return tuple(tuple(p) for p in profiles)


def check_word(word, w, k, claimed):
    roles = w + 2
    require(invoice(word, roles, k) == claimed, "undercharged profile")
    expected = (4,) * w + (0,) * 2
    require(formal_endpoint(word, roles) == expected, "formal dirty boundary")
    actual = regular_endpoint(word, roles)
    target = tuple((i, group_product(expected[i], g))
                   for i in range(roles) for g in range(8))
    require(actual == target, "faithful dirty boundary")
    require(regular_endpoint(tuple(reversed(word)), roles) == target,
            "inverse dirty boundary")
    return len(actual)


def partitions(total, cap):
    """All decreasing positive integer partitions, with a finite work bound."""
    require(1 <= total <= MAX_PARTITION_SUM and 1 <= cap <= 7, "partition domain")
    stack = [(total, cap, ())]
    # All ordered composition prefixes of total number at most 2**total.
    for _ in range(1 << total):
        if not stack:
            return
        left, largest, prefix = stack.pop()
        if left == 0:
            yield prefix
        else:
            for value in range(1, min(left, largest) + 1):
                stack.append((left - value, value, prefix + (value,)))
    require(not stack, "partition work bound exhausted")


def costs(ranks, cap):
    # Count is a separate overhead. The rest are exact concave rank tariffs.
    return (Fraction(len(ranks)), sum((Fraction(d, d + 1) for d in ranks), Fraction()),
            *(Fraction(sum(min(d, c) for d in ranks)) for c in range(1, cap + 1)))


def check_relaxation():
    checked = 0
    for w in range(1, 6):
        for k in range(1, 8):
            optimum = costs(packed_ranks(w, k), k)
            for mass in range(2 * w, 2 * w + 5):
                for ranks in partitions(mass, k):
                    if 2 * ranks[0] > mass:
                        continue
                    require(all(a >= b for a, b in zip(costs(ranks, k), optimum)),
                            "relaxed rank list beats the claimed tariff")
                    checked += 1
    # A non-zero-sum one-call relaxation is not evidence for the theorem.
    require(costs((10,), 10)[1] < costs((5, 5), 10)[1], "zero-sum countercontrol")
    # Concavity is material: convex pricing favors the predecessor's balance.
    require(sum(d * d for d in (4, 3, 3)) < sum(d * d for d in (4, 4, 2)),
            "convex-price countercontrol")
    return checked


def expect_rejection(word, w, k, claimed):
    try:
        check_word(word, w, k, claimed)
    except ValueError:
        return
    raise ValueError("failure control accepted")


def check_controls():
    w, k = 5, 4
    word = word_from_supports(supports(w, k))
    claimed = (packed_ranks(w, k),) * 2
    count = 0
    for i in range(len(word)):
        # Reprice before testing: endpoint, rather than a stale invoice, rejects.
        mutant = word[:i] + word[i + 1:]
        expect_rejection(mutant, w, k, invoice(mutant, w + 2, k))
        count += 1
    expect_rejection(word, w, k, ((4, 3, 2), claimed[1]))
    expect_rejection(word, w, 3, claimed)
    expect_rejection(((4, word[0][1]),) + word[1:], w, k, claimed)
    dirty_word = word + ((1, 1 << w), (2, 1 << w)) * 2
    expect_rejection(dirty_word, w, k, invoice(dirty_word, w + 2, k))
    # Same invoice, legal supports, wrong incidence.
    mutant = ((word[0][0], word[0][1] ^ 1 ^ (1 << 4)),) + word[1:]
    require(mutant[0][1].bit_count() == word[0][1].bit_count(), "control rank")
    expect_rejection(mutant, w, k, claimed)
    return count + 5


def receipt():
    fixtures, columns = 0, 0
    transcript = hashlib.sha256()
    for w in range(1, MAX_W + 1):
        for k in range(1, w + 4):
            masks = supports(w, k)
            word = word_from_supports(masks)
            profile = packed_ranks(w, k)
            columns += check_word(word, w, k, (profile,) * 2)
            transcript.update(json.dumps([w, k, masks, profile]).encode())
            fixtures += 1
    old = tuple(mask.bit_count() for mask in balanced_supports(5, 4))
    new = packed_ranks(5, 4)
    require(old == (4, 3, 3) and new == (4, 4, 2), "pilot profiles")
    old_cost, new_cost = costs(old, 4)[1], costs(new, 4)[1]
    require(old_cost == Fraction(23, 10) and new_cost == Fraction(34, 15), "pilot bill")
    return {
        "status": "PASS_UT3_CONCAVE_RANK_TARIFF",
        "fixtures": fixtures,
        "faithful_basis_columns": columns,
        "profile_digest": transcript.hexdigest(),
        "relaxed_rank_lists": check_relaxation(),
        "rejection_controls": check_controls(),
        "pilot": {"w": 5, "k": 4, "old_profile": old, "new_profile": new,
                  "old_per_letter_cost": str(old_cost), "new_per_letter_cost": str(new_cost),
                  "two_letter_saving": str(2 * (old_cost - new_cost))},
        "scope": "Written arbitrary-size tariff proof; finite exact corroboration. No supplier or kappa claim."
    }


def main():
    actual = receipt()
    # Canonicalize tuple/list differences introduced by JSON.
    actual = json.loads(json.dumps(actual))
    with (HERE / "RESULT.json").open("rb") as source:
        payload = source.read(4097)
    require(len(payload) <= 4096, "receipt capacity exceeded")
    expected = json.loads(payload)
    require(actual == expected, "receipt differs from RESULT.json")
    print(json.dumps(actual, sort_keys=True))


if __name__ == "__main__":
    main()
