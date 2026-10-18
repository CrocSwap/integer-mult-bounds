#!/usr/bin/env python3
"""Independent finite audit of the PR1989 -> GL2 SWAP corollary.

Standard library only. Operators are images of every binary basis vector in
the faithful left regular action. No producer or predecessor code is imported.
This verifies the stated finite domains, not an exhaustive circuit search.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "research/symmetric-adjacent-cut-bound/PROOF.md":
        "008be68867a8e85f4e18455d206e03f20aebfc28e9f08efba576180e7e1edc50",
    "research/four-swap-full-occupancy/README.md":
        "82bdfbfb517505ef6783cb82e2718975876276075fe3dba26959df514f984f60",
}

Matrix = tuple[int, int, int, int]
Operator = tuple[int, ...]  # column j is the binary image of basis vector j
E: Matrix = (1, 0, 0, 1)
A: Matrix = (1, 1, 0, 1)
B: Matrix = (1, 0, 1, 1)
SWAP: Matrix = (0, 1, 1, 0)
VECTORS = ((0, 1), (1, 1), (1, 0))
GROUP = tuple(m for m in itertools.product((0, 1), repeat=4)
              if (m[0] * m[3]) ^ (m[1] * m[2]))
INDEX = {g: i for i, g in enumerate(GROUP)}


class Rejected(Exception):
    """An explicitly named failed audit obligation."""

    def __init__(self, obligation: str):
        self.obligation = obligation
        super().__init__(obligation)


def require(ok: bool, obligation: str) -> None:
    if not ok:
        raise Rejected(obligation)


def reject_exactly(obligation: str, action) -> None:
    try:
        action()
    except Rejected as error:
        if error.obligation != obligation:
            raise
    else:
        # Unexpected acceptance is deliberately outside the caught path.
        raise RuntimeError(f"negative control accepted: {obligation}")


def matmul(g: Matrix, h: Matrix) -> Matrix:
    return (
        (g[0] * h[0]) ^ (g[1] * h[2]),
        (g[0] * h[1]) ^ (g[1] * h[3]),
        (g[2] * h[0]) ^ (g[3] * h[2]),
        (g[2] * h[1]) ^ (g[3] * h[3]),
    )


def permutation(g: Matrix, vectors=VECTORS) -> tuple[int, ...]:
    return tuple(vectors.index(((g[0] * x) ^ (g[1] * y),
                                (g[2] * x) ^ (g[3] * y)))
                 for x, y in vectors)


def labels_are_adjacent(labels) -> None:
    require(labels[A] == (1, 0, 2) and labels[B] == (0, 2, 1)
            and labels[SWAP] == (2, 1, 0), "declared_labels")


def bits(value: int):
    while value:
        low = value & -value
        yield low.bit_length() - 1
        value ^= low


def identity(size: int) -> Operator:
    return tuple(1 << i for i in range(size))


def apply(operator: Operator, vector: int) -> int:
    result = 0
    for i in bits(vector):
        result ^= operator[i]
    return result


def compose(left: Operator, right: Operator) -> Operator:
    require(len(left) == len(right), "operator_dimension")
    return tuple(apply(left, column) for column in right)


def rank(columns) -> int:
    pivots: dict[int, int] = {}
    for value in columns:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def projector(roles: int, u: int, v: int) -> Operator:
    return tuple(u if v & (1 << j) else 0 for j in range(roles))


def admit(label: Matrix, n: Operator) -> None:
    require(label in (A, B), "paid_alphabet")
    require(rank(n) == 1 and compose(n, n) == n, "rank_one_idempotent")


def scalar(s: Operator) -> Operator:
    return tuple(sum(1 << (6 * i + h) for i in bits(s[j]))
                 for j in range(len(s)) for h in range(6))


def regular(label: Matrix) -> Operator:
    return tuple(1 << INDEX[matmul(label, h)] for h in GROUP)


def gate(label: Matrix, n: Operator) -> Operator:
    """I + N tensor (L_label + I), on all role/address basis columns."""
    result = []
    for j, column in enumerate(n):
        for h, address in enumerate(GROUP):
            image = 1 << (6 * j + h)
            moved = INDEX[matmul(label, address)]
            for i in bits(column):
                image ^= (1 << (6 * i + h)) ^ (1 << (6 * i + moved))
            result.append(image)
    return tuple(result)


def endpoint(targets: int, roles: int) -> Operator:
    # Direct action of the advertised target, independently of gate products.
    return tuple(1 << (6 * j + INDEX[matmul(SWAP, h)]
                      if j < targets else 6 * j + INDEX[h])
                 for j in range(roles) for h in GROUP)


def complete_endpoint(actual: Operator, expected: Operator) -> None:
    require(actual == expected, "complete_endpoint")


def cut(operator: Operator) -> int:
    roles, remainder = divmod(len(operator), 6)
    require(remainder == 0, "regular_dimension")
    positive = tuple(i for i, h in enumerate(GROUP)
                     if permutation(h)[0] < permutation(h)[1])
    negative = set(range(6)) - set(positive)
    output_mask = sum(1 << (6 * j + h)
                      for j in range(roles) for h in negative)
    return rank(operator[6 * j + h] & output_mask
                for j in range(roles) for h in positive)


def direct_word(targets: int, roles: int, labels=(A, B, A)):
    return [(g, projector(roles, 1 << j, 1 << j))
            for j in range(targets) for g in labels]


def execute(word, roles: int) -> Operator:
    result = identity(6 * roles)
    for label, n in word:
        admit(label, n)
        result = compose(gate(label, n), result)
    return result


def check_sources() -> None:
    for path, digest in PINS.items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest,
                f"source_pin:{path}")


def check_group() -> dict:
    labels = {g: permutation(g) for g in GROUP}
    require(len(GROUP) == 6 and len(set(labels.values())) == 6,
            "six_element_bijection")
    labels_are_adjacent(labels)
    require(matmul(matmul(A, B), A) == SWAP
            and matmul(matmul(B, A), B) == SWAP, "swap_word")
    require(matmul(A, B) != matmul(B, A), "noncommutative_order")
    for g, h in itertools.product(GROUP, repeat=2):
        require(labels[matmul(g, h)] == tuple(labels[g][i] for i in labels[h]),
                "group_product_convention")
        require(compose(regular(g), regular(h)) == regular(matmul(g, h)),
                "left_regular_product")
    for g in GROUP:
        p = labels[g]
        inv = sum(p[i] > p[j] for i in range(3) for j in range(i + 1, 3))
        require(cut(regular(g)) == inv, "inversion_cut")
    coefficient_operators = set()
    for coefficients in range(64):
        operator = tuple(0 for _ in GROUP)
        for i in bits(coefficients):
            operator = tuple(x ^ y for x, y in zip(operator, regular(GROUP[i])))
        # Applying a left-regular algebra element to [e] recovers all coefficients.
        require(operator[INDEX[E]] == coefficients, "coefficient_recovery")
        coefficient_operators.add(operator)
    require(len(coefficient_operators) == 64, "regular_faithfulness")
    # Changing the vector ordering can silently make a paid label nonadjacent.
    wrong_vectors = (VECTORS[1], VECTORS[0], VECTORS[2])
    wrong_labels = {g: permutation(g, wrong_vectors) for g in GROUP}
    reject_exactly("declared_labels", lambda: labels_are_adjacent(wrong_labels))
    return {"elements": 6, "ordered_products": 36, "coefficient_elements": 64,
            "labeling_control": 1}


def check_projectors() -> dict:
    counts = {}
    calls = 0
    for roles in range(1, 8):
        count = 0
        for u in range(1, 1 << roles):
            for v in range(1, 1 << roles):
                if (u & v).bit_count() % 2 == 0:
                    continue
                n = projector(roles, u, v)
                for label in (A, B):
                    admit(label, n)
                    operator = gate(label, n)
                    require(cut(operator) == 1, "one_crossing_per_call")
                    require(compose(operator, operator) == identity(6 * roles),
                            "paid_involution")
                    calls += 1
                count += 1
        require(count == ((1 << roles) - 1) * (1 << (roles - 1)),
                "projector_domain_count")
        counts[str(roles)] = count
    return {"all_projectors_by_roles": counts, "paid_operator_checks": calls}


def check_free_maps() -> dict:
    counts = {}
    for roles in range(4):
        count = 0
        for s in itertools.product(range(1 << roles), repeat=roles):
            if rank(s) != roles:
                continue
            require(cut(scalar(s)) == 0, "free_scalar_zero_cut")
            count += 1
        counts[str(roles)] = count
    require(counts == {"0": 1, "1": 1, "2": 6, "3": 168}, "free_map_domain")
    return {"all_free_maps_by_roles": counts}


def check_endpoints() -> dict:
    cases = []
    omissions = 0
    wrong_labels = 0
    for targets in range(6):
        for roles in range(targets, targets + 3):
            expected = endpoint(targets, roles)
            word = direct_word(targets, roles)
            complete_endpoint(execute(word, roles), expected)
            require(cut(expected) == 3 * targets, "target_cut")
            # Equivalent positive presentation: bab in reverse target-role order.
            equivalent = list(reversed(direct_word(targets, roles, (B, A, B))))
            complete_endpoint(execute(equivalent, roles), expected)
            for omitted in range(len(word)):
                actual = execute(word[:omitted] + word[omitted + 1:], roles)
                reject_exactly("complete_endpoint",
                               lambda: complete_endpoint(actual, expected))
                omissions += 1
            if word:
                actual = execute([(B, word[0][1])] + word[1:], roles)
                reject_exactly("complete_endpoint",
                               lambda: complete_endpoint(actual, expected))
                wrong_labels += 1
            cases.append({"targets": targets, "roles": roles, "paid": len(word)})
    return {"direct_endpoint_cases": cases, "equivalent_presentations": len(cases),
            "omitted_call_controls": omissions, "wrong_call_label_controls": wrong_labels}


def check_interleaved() -> dict:
    cases = 0
    noncommuting_cases = 0
    dirty_coupled_cases = 0
    for targets in range(1, 6):
        for roles in range(max(2, targets), targets + 3):
            actual = identity(6 * roles)
            paid = 0
            conjugates = []
            for index, (label, n) in enumerate(direct_word(targets, roles)):
                active = index // 3
                other = targets if roles > targets else (active + 1) % roles
                s = list(identity(roles))
                # Alternating transvections produce noncommuting paid projectors.
                if index % 2:
                    s[other] ^= 1 << active
                else:
                    s[active] ^= 1 << other
                s = tuple(s)
                require(compose(s, s) == identity(roles), "transvection_inverse")
                conjugate = compose(compose(s, n), s)
                admit(label, conjugate)
                conjugates.append(conjugate)
                # Chronology S, D_(SNS^-1), S^-1 gives exactly D_N.
                for operator, charge in ((scalar(s), 0), (gate(label, conjugate), 1),
                                         (scalar(s), 0)):
                    actual = compose(operator, actual)
                    paid += charge
                    require(cut(actual) <= paid, "interleaved_prefix_invoice")
            complete_endpoint(actual, endpoint(targets, roles))
            require(paid == 3 * targets, "interleaved_paid_count")
            require(any(compose(x, y) != compose(y, x)
                        for x, y in zip(conjugates, conjugates[1:])),
                    "noncommuting_projector_fixture")
            noncommuting_cases += 1
            if roles > targets:
                active_mask = (1 << targets) - 1
                p = tuple((1 << j) & active_mask for j in range(roles))
                require(any(compose(p, n) != compose(n, p) for n in conjugates),
                        "active_dirty_coupling_fixture")
                dirty_coupled_cases += 1
            cases += 1
    return {"interleaved_endpoint_cases": cases,
            "noncommuting_projector_cases": noncommuting_cases,
            "active_dirty_coupled_cases": dirty_coupled_cases}


def check_boundary_controls() -> dict:
    expected = endpoint(1, 2)
    # Target += dirty spectator: invisible if the spectator is initialized to zero.
    coupling = scalar((1, 3))
    contaminated = compose(coupling, expected)
    require(contaminated[:6] == expected[:6], "clean_only_control_passes")
    require(contaminated[6:] != expected[6:], "dirty_basis_detects_contamination")
    reject_exactly("complete_endpoint",
                   lambda: complete_endpoint(contaminated, expected))
    # A unit-priced s call really achieves SWAP, but changes the allowed alphabet.
    n = projector(1, 1, 1)
    shortcut = gate(SWAP, n)
    complete_endpoint(shortcut, endpoint(1, 1))
    require(cut(shortcut) == 3, "extra_label_crossing_price")
    reject_exactly("paid_alphabet", lambda: admit(SWAP, n))
    reject_exactly("unit_price_invoice", lambda: require(cut(shortcut) <= 1,
                                                         "unit_price_invoice"))
    # Higher-rank invocations likewise cannot retain the rank-one tariff.
    reject_exactly("rank_one_idempotent", lambda: admit(A, identity(2)))
    require(cut(gate(A, identity(2))) == 2, "rank_two_price")
    return {"dirty_coupling_control": 1, "extra_label_admission_control": 1,
            "extra_label_unit_price_control": 1, "rank_two_admission_control": 1}


def main() -> None:
    check_sources()
    result = {"scope": "finite_corollary_audit_no_new_kappa",
              "group": check_group(), "projectors": check_projectors(),
              "free_maps": check_free_maps(), "endpoints": check_endpoints(),
              "interleaving": check_interleaved(), "controls": check_boundary_controls()}
    print("PASS_INDEPENDENT_GL2_SWAP_CUT_COROLLARY " +
          json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
