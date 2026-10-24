"""Exact monotone UT3 pricing and full dirty-input construction controls."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations_with_replacement
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def optimum(w, k, prices):
    """Return the exact per-letter price and an attaining rank partition."""
    need(type(w) is int and 1 <= w <= 32, "target bound")
    need(type(k) is int and 1 <= k <= 35, "rank-cap bound")
    need(len(prices) == k + 1 and prices[0] == 0, "price domain")
    need(all(0 <= prices[d - 1] <= prices[d] for d in range(1, k + 1)),
         "nonnegative monotone prices required")
    cap = min(w, k)
    best = [(Fraction(0), ())]
    for mass in range(1, 2 * w + 1):
        choices = []
        for d in range(1, min(mass, cap) + 1):
            cost, parts = best[mass - d]
            choices.append((cost + prices[d], tuple(sorted(parts + (d,)))))
        best.append(min(choices))
    cost, parts = best[-1]
    need(sum(parts) == 2 * w and max(parts) <= cap, "partition contract")
    return cost, parts


def partitions(total, cap):
    """Enumerate every nonincreasing partition in a bounded probe domain."""
    need(1 <= total <= 16 and 1 <= cap <= 9, "partition probe bound")
    stack = [((), total, cap)]
    for _ in range(1 << total):
        if not stack:
            return
        prefix, remaining, largest = stack.pop()
        if remaining == 0:
            yield prefix
        else:
            for d in range(1, min(remaining, largest) + 1):
                stack.append((prefix + (d,), remaining - d, d))
    need(not stack, "partition work budget exhausted")


def truncate(parts, w):
    """The new lower-bound reduction, applied to a feasible rank list."""
    total = sum(parts)
    need(parts and min(parts) >= 1 and total >= 2 * w, "rank mass")
    need(2 * max(parts) <= total, "zero-sum rank triangle")
    clipped = [min(d, w) for d in parts]
    need(sum(clipped) >= 2 * w, "clipping lemma")
    excess = sum(clipped) - 2 * w
    for i, d in enumerate(clipped):
        removed = min(d, excess)
        clipped[i] -= removed
        excess -= removed
    answer = tuple(d for d in clipped if d)
    need(excess == 0 and sum(answer) == 2 * w, "exact truncation mass")
    return answer


def supports(parts, w):
    """The credited loopless-incidence construction, with explicit invariants."""
    need(parts and sum(parts) == 2 * w and max(parts) <= w, "graph degrees")
    remaining = list(parts)
    rows = [0] * len(parts)
    for coordinate in range(w):
        order = sorted(range(len(parts)), key=lambda i: (-remaining[i], i))
        left, right = order[:2]
        need(remaining[right] > 0, "two distinct incident vertices")
        for vertex in (left, right):
            remaining[vertex] -= 1
            rows[vertex] |= 1 << coordinate
        edges_left = w - coordinate - 1
        need(sum(remaining) == 2 * edges_left, "remaining graph degree mass")
        need(max(remaining) <= edges_left, "remaining graph degree maximum")
    need(tuple(row.bit_count() for row in rows) == parts, "support ranks")
    return tuple(rows)


def group_product(left, right):
    """Triple UT3 law, used only by the formal endpoint engine."""
    u, v, z = left
    a, b, c = right
    return u ^ a, v ^ b, z ^ c ^ (u & b)


def formal_endpoint(rows, roles):
    endpoint = [(0, 0, 0)] * roles
    for support in rows:
        for label in ((1, 0, 0), (0, 1, 0)):
            for role in range(roles):
                if support >> role & 1:
                    endpoint[role] = group_product(label, endpoint[role])
    return tuple(endpoint)


def literal_call(state, support, letter):
    """Independent faithful regular action on every address of every role.

    Encode a unitriangular 3 by 3 matrix by address = 4*u + 2*v + z.
    Left a changes u and z by 1 and v; left b changes v. The triple-law
    helper is deliberately not used in this endpoint oracle.
    """
    output = [0] * len(state)
    for role in range(len(state) // 8):
        for address in range(8):
            destination = address
            if support >> role & 1:
                if letter == "a":
                    destination = address ^ 4 ^ ((address >> 1) & 1)
                else:
                    need(letter == "b", "letter domain")
                    destination = address ^ 2
            output[8 * role + destination] ^= state[8 * role + address]
    return tuple(output)


def regular_check(rows, w, roles, omitted=None, leak=False):
    calls = [(row, letter) for row in rows for letter in ("a", "b")]
    if omitted is not None:
        calls = calls[:omitted] + calls[omitted + 1:]
    if leak:
        calls.append((1 << w, "a"))
    columns = 0
    for source in range(8 * roles):
        basis = tuple(int(i == source) for i in range(8 * roles))
        state = basis
        for row, letter in calls:
            state = literal_call(state, row, letter)
        role, address = divmod(source, 8)
        target = 8 * role + (address ^ int(role < w))
        need(state == tuple(int(i == target) for i in range(8 * roles)),
             "full dirty endpoint")
        for row, letter in reversed(calls):
            state = literal_call(state, row, letter)
        need(state == basis, "inverse dirty endpoint")
        columns += 1
    return columns


def price_families(k):
    return (
        tuple(Fraction(0) if d == 0 else Fraction(5 + d * d)
              for d in range(k + 1)),
        tuple(Fraction(d, d + 1) for d in range(k + 1)),
        tuple(Fraction(0) if d == 0 else Fraction(2 + (d + 2) // 3)
              for d in range(k + 1)),
        tuple(Fraction(d) + Fraction(d >= 3, 2) + Fraction(d >= 5, 3)
              for d in range(k + 1)),
    )


def construction_checks():
    fixtures = columns = 0
    digest = sha256()
    for w in range(1, 17):
        for k in range(1, w + 4):
            for prices in price_families(k):
                cost, parts = optimum(w, k, prices)
                rows = supports(parts, w)
                expected = ((0, 0, 1),) * w + ((0, 0, 0),) * 2
                need(formal_endpoint(rows, w + 2) == expected, "formal endpoint")
                need(sum(prices[row.bit_count()] for row in rows) == cost,
                     "literal rank price")
                digest.update(repr((w, k, cost, parts, rows)).encode())
                fixtures += 1
                if w <= 6 and k <= w + 2:
                    columns += regular_check(rows, w, w + 2)
    return {"formal_fixtures": fixtures, "regular_basis_columns": columns,
            "construction_digest": digest.hexdigest()}


def partition_checks():
    cases = lists = 0
    for w in range(1, 6):
        for k in range(1, w + 3):
            exact = tuple(partitions(2 * w, min(w, k)))
            relaxed = tuple(parts for mass in range(2 * w, 2 * w + 5)
                            for parts in partitions(mass, k)
                            if 2 * max(parts) <= mass)
            lists += len(relaxed)
            for values in combinations_with_replacement(range(4), k):
                prices = (0,) + values
                cost, _ = optimum(w, k, prices)
                need(cost == min(sum(prices[d] for d in p) for p in exact),
                     "independent exhaustive integer-partition optimum")
                for parts in relaxed:
                    smaller = truncate(parts, w)
                    old_price = sum(prices[d] for d in parts)
                    new_price = sum(prices[d] for d in smaller)
                    need(cost <= new_price <= old_price, "tariff reduction")
                cases += 1
    return {"monotone_price_tables": cases, "relaxed_rank_lists": lists}


def rejects(action, message):
    try:
        action()
    except ValueError:
        return
    raise ValueError("control did not reject: " + message)


def controls():
    prices = tuple(0 if d == 0 else 5 + d * d for d in range(5))
    cost, parts = optimum(5, 4, prices)
    need(cost == 45 and parts == (2, 2, 2, 2, 2), "first new fixture")
    need(sum(prices[d] for d in (4, 3, 3)) == 49, "balanced comparison")
    need(sum(prices[d] for d in (4, 4, 2)) == 51, "concentrated comparison")
    rows = supports(parts, 5)
    rejected = 0
    for call in range(2 * len(rows)):
        rejects(lambda: regular_check(rows, 5, 7, omitted=call), "omitted call")
        rejected += 1
    rejects(lambda: regular_check(rows, 5, 7, leak=True), "dirty leakage")
    rejects(lambda: optimum(2, 3, (0, 2, 1, 3)), "decreasing tariff")
    rejects(lambda: optimum(2, 2, (0, -1, 2)), "negative tariff")
    rejects(lambda: supports((3, 1), 2), "non-graphical rank list")
    rejects(lambda: truncate((4,), 2), "missing zero-sum triangle")
    rejects(lambda: optimum(33, 1, (0, 1)), "target capacity")
    rejects(lambda: optimum(2, 0, (0,)), "rank capacity")
    rejects(lambda: optimum(2, 2, (1, 2, 3)), "charged identity entry")
    return {"complete_price": str(2 * cost), "ranks_per_letter": parts,
            "balanced_price": 98, "concentrated_price": 102,
            "rejection_controls": rejected + 8}


def main():
    result = {"claim_type": "scoped proof with exact finite corroboration",
              "construction": construction_checks(),
              "partition": partition_checks(), "first_fixture": controls()}
    package = Path(__file__).resolve().parent
    result["source_sha256"] = {
        path.name: sha256(path.read_bytes()).hexdigest()
        for path in sorted(package.iterdir()) if path.is_file()
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_UT3_MONOTONE_RANK_TARIFF no_new_kappa")


if __name__ == "__main__":
    main()
