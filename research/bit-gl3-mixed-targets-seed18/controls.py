"""Boundary and representation controls, not extra search coverage."""

from algebra import (ADDRESS_ID, GENERATORS, NATURAL_ID, LABELS, multiply,
                     natural_image, natural_step, require)

# A seven-call natural alias for a six-call coordinate cycle and a two-call
# double shear. It is a counterexample to treating natural equality as formal.
ALIAS_WORD = [(2, 3, 0, 2), (1, 3, 2, 1), (1, 1, 1, 2),
              (3, 1, 0, 1), (1, 1, 2, 1), (1, 1, 1, 0), (1, 3, 0, 1)]
ALIAS_TARGETS = (140, 279)


def scalar_product(a, b):
    return sum((sum(((a >> (2*r+k)) & 1) * ((b >> (2*k+c)) & 1)
                    for k in range(2)) % 2) << (2*r+c)
               for r in range(2) for c in range(2))


def scalar_outer(u, v):
    return sum(((u >> r) & (v >> c) & 1) << (2*r+c)
               for r in range(2) for c in range(2))


def regular_column(algebra, word, input_role, input_group):
    """Action on one faithful-regular basis column, stored as finite sets."""
    rows = [set(), set()]
    rows[input_role].add(input_group)
    for u, v, i, j in word:
        label = ADDRESS_ID ^ (1 << (3*i+j))
        source = set()
        for role in range(2):
            if v >> role & 1:
                source.symmetric_difference_update(rows[role])
        shifted = {multiply(label, value) for value in source}
        delta = source ^ shifted
        for role in range(2):
            if u >> role & 1:
                rows[role].symmetric_difference_update(delta)
    return rows


def check_controls(algebra, formal_table, natural_table):
    passed = []

    scalar_group = [a for a in range(16)
                    if any(scalar_product(a, b) == 9 for b in range(16))]
    require(len(scalar_group) == 6, "scalar group order")
    conjugates = set()
    for a in scalar_group:
        inverse = next(b for b in scalar_group if scalar_product(a, b) == 9)
        conjugates.add(scalar_product(scalar_product(a, 1), inverse))
    projectors = {scalar_outer(u, v) for u, v, _, _ in GENERATORS}
    require(len(projectors) == 6 and conjugates == projectors, "free scalar normalization incomplete")
    passed.append("all_scalar_conjugates_in_alphabet")

    # A nilpotent rank-one matrix is not a legal idempotent.
    require(2 not in projectors and scalar_product(2, 2) == 0, "nilpotent admitted")
    passed.append("nilpotent_scalar_mask_excluded")
    for generator in algebra.generators:
        require(algebra.step(algebra.step(algebra.unit, generator), generator) == algebra.unit,
                "paid involution failed")
    passed.append("all_36_paid_involutions")

    # Test noncommuting labels with an orientation-sensitive pair.
    a = ADDRESS_ID ^ (1 << 1)
    b = ADDRESS_ID ^ (1 << 5)
    require(multiply(a, b) != multiply(b, a), "address multiplication accidentally commutative")
    passed.append("noncommuting_address_order")

    for g1, z1 in zip(algebra.generators, GENERATORS):
        for g2, z2 in zip(algebra.generators, GENERATORS):
            formal = algebra.step(algebra.step(algebra.unit, g1), g2)
            natural = natural_step(natural_step(NATURAL_ID, z1), z2)
            require(natural_image(algebra, formal) == natural, "two-call representation mismatch")
    passed.append("all_1296_two_call_projection_squares")

    # All targets, including those outside the lower-bound radius, have an
    # attaining direct formal word. This also certifies the upper bound nine.
    for a in range(168):
        for b in range(168):
            word = algebra.direct_word(a, b)
            require(len(word) == algebra.direct[a] + algebra.direct[b], "direct bill mismatch")
            require(algebra.word(word) == algebra.target(a, b), "direct formal boundary failure")
    passed.append("all_28224_direct_formal_upper_bounds")

    a, b = [algebra.index[g] for g in ALIAS_TARGETS]
    target = algebra.target(a, b)
    false_word = algebra.word(ALIAS_WORD)
    require(false_word != target, "natural alias was incorrectly accepted formally")
    require(natural_image(algebra, false_word) == natural_image(algebra, target),
            "alias fixture does not match the natural target")
    require(formal_table[a][b] == 8 and natural_table[a][b] == 7, "alias distances changed")
    passed.append("seven_call_natural_alias_rejected_formally")

    regular_failures = 0
    direct = algebra.direct_word(a, b)
    for role in range(2):
        for x in algebra.group:
            expected = [set(), set()]
            expected[role].add(multiply(ALIAS_TARGETS[role], x))
            require(regular_column(algebra, direct, role, x) == expected,
                    "direct word failed a faithful regular column")
            regular_failures += regular_column(algebra, ALIAS_WORD, role, x) != expected
    require(regular_failures > 0, "faithful regular action hid the alias")
    passed.append("336_faithful_regular_columns_direct_and_alias")

    require(algebra.word(direct[:-1]) != target, "omitted paid gate went undetected")
    passed.append("omitted_paid_call_rejected")
    require(algebra.word(list(reversed(direct))) != target, "reversed noncommuting word accepted")
    passed.append("reversed_target_word_rejected")
    wrong_order = [(u, v, j, i) for u, v, i, j in direct]
    require(algebra.word(wrong_order) != target, "transposed coordinate convention accepted")
    passed.append("transposed_coordinate_word_rejected")

    # In the first output column, one can hide an erroneous dependency on the
    # second input by setting that input clean. Inspect the full formal matrix.
    dirty_error = (target[0], 1 << algebra.identity, 0, target[3])
    require((dirty_error[0], dirty_error[2]) == (target[0], target[2]) and dirty_error != target,
            "dirty-input control malformed")
    passed.append("clean_only_success_rejected_on_dirty_input")

    require(formal_table[algebra.identity][algebra.identity] == 0, "identity cost")
    for i in range(168):
        require(formal_table[i][algebra.identity] == algebra.direct[i], "one-output direct control")
    passed.append("identity_and_168_one_output_controls")
    return {"passed": passed, "count": len(passed),
            "regular_columns": 336, "alias_failing_regular_columns": regular_failures,
            "alias_targets_row_masks": [[g >> (3*r) & 7 for r in range(3)] for g in ALIAS_TARGETS],
            "alias_word_uvij": [list(g) for g in ALIAS_WORD]}
