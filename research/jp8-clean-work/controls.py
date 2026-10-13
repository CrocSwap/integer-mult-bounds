"""Dirty-work and boundary controls, with a separate Fraction interpreter.

faw01, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q


def fraction_step(rows, primitive):
    tag, target = primitive[:2]
    if tag == "clear":
        rows[target] = {}
    elif tag == "copy":
        rows[target] = dict(rows[primitive[2]])
    elif tag in {"double", "halve", "negate"}:
        factor = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
        rows[target] = {j: factor*x for j, x in rows[target].items()}
    elif tag in {"add", "subtract"}:
        left, right = rows[target], rows[primitive[2]]
        sign = 1 if tag == "add" else -1
        rows[target] = {j: left.get(j, 0) + sign*right.get(j, 0) for j in left.keys() | right.keys()}
        rows[target] = {j: x for j, x in rows[target].items() if x}
    else:
        raise ValueError("unknown Fraction primitive")


def run(optimizer, comparator, integer_step, require, coefficients):
    work, t, s, u = optimizer.WORK, ("L", 0), ("L", 1), ("L", 2)
    accepted = []

    def unit(frame=0, sign=1):
        return ["scalar", ["add", list(t), list(s), sign, 1], frame]

    def compare(events, mutation=None):
        """Opaque events/frame changes may dirty W arbitrarily in this test.

        Every macro boundary must still match the original on all columns.
        Also compare individual register prefix states, not just endpoints.
        """
        original = {r: {i: Q(1)} for i, r in enumerate((t, s, u, work))}
        candidate = {r: dict(row) for r, row in original.items()}
        fresh_column = 4
        previous_frame = None
        emitted = list(optimizer.specialize(events, comparator.lower))
        if mutation:
            emitted = mutation(emitted)
        for index, word, witness in emitted:
            event = events[index]
            if event[0] != "scalar" or event[2] != previous_frame:
                original[work] = candidate[work] = {fresh_column: Q(1)}
                fresh_column += 1
                previous_frame = event[2] if event[0] == "scalar" else None
            if event[0] != "scalar":
                continue
            before = {r: dict(row) for r, row in original.items()}
            seen = {r: {tuple(sorted(row.items()))} for r, row in before.items()}
            for primitive in comparator.lower(event[1], work):
                fraction_step(original, primitive)
                for r, row in original.items():
                    seen[r].add(tuple(sorted(row.items())))
            for primitive in word:
                fraction_step(candidate, primitive)
                require(all(tuple(sorted(row.items())) in seen[r] for r, row in candidate.items()), "control prefix containment")
            require(candidate == original, "control complete boundary")
            if event[1][0] == "add":
                require(not candidate[work], "control addition work postcondition")
        return emitted

    def reject(name, operation, expected_message):
        try:
            operation()
        except ValueError as error:
            require(str(error) == expected_message, name + " rejected for wrong reason: " + str(error))
            accepted.append(name)
        else:
            raise ValueError("negative control accepted: " + name)

    def remove_last_clear(index):
        def mutation(emitted):
            i, word, witness = emitted[index]
            require(word[-1] == ("clear", work), "control fixture lacks clear")
            emitted[index] = i, word[:-1], witness
            return emitted
        return mutation

    reject("dirty_first_unit", lambda: compare([unit()], remove_last_clear(0)), "control complete boundary")
    for barrier in sorted(optimizer.BARRIERS):
        events = [unit(), [barrier, "opaque_test_boundary"], unit(sign=-1)]
        good = compare(events)
        require(len(good[2][1]) == 2 and good[2][2] is None, "barrier knowledge retained")
        reject("dirty_after_" + barrier, lambda e=events: compare(e, remove_last_clear(2)), "control complete boundary")
    events = [unit(0), unit(1)]
    compare(events)
    reject("dirty_after_frame_change", lambda: compare(events, remove_last_clear(1)), "control complete boundary")

    # Intervening operations do not inspect or modify W; both unit signs work.
    positive = [unit(), ["scalar", ["scale", list(u), -1, 2], 0],
                ["scalar", ["copy", list(u), list(s)], 0],
                ["scalar", ["clear", list(u)], 0], unit(sign=-1)]
    emitted = compare(positive)
    require(emitted[-1][2] == 0 and len(emitted[-1][1]) == 1, "lost same-frame clean knowledge")

    for name, op in (
        ("private_source_alias", ["add", list(t), list(work), 1, 1]),
        ("private_target_alias", ["clear", list(work)]),
        ("private_copy_alias", ["copy", list(t), list(work)]),
    ):
        reject(name, lambda op=op: list(optimizer.specialize([["scalar", op, 0]], comparator.lower)),
               "scalar operand is not a logical/center register")
    reject("unknown_scalar", lambda: list(optimizer.specialize([["scalar", ["mystery", list(t)], 0]], comparator.lower)), "unknown scalar macro")
    reject("unknown_event", lambda: list(optimizer.specialize([["mystery"]], comparator.lower)), "unknown event")

    def wrong_sign(emitted):
        i, word, witness = emitted[1]
        emitted[1] = i, (("subtract", t, s),), witness
        return emitted
    reject("wrong_unit_sign", lambda: compare([unit(), unit()], wrong_sign), "control prefix containment")

    def neutral_growth(emitted):
        i, word, witness = emitted[1]
        emitted[1] = i, (("double", s), ("halve", s)) + word, witness
        return emitted
    reject("restored_endpoint_excess_prefix", lambda: compare([unit(), unit()], neutral_growth), "control prefix containment")
    nonunit = ["scalar", ["add", list(t), list(s), 3, 4], 0]
    reject("nonunit_cleanup_omitted", lambda: compare([nonunit], remove_last_clear(0)), "control complete boundary")

    # A genuinely separate Fraction implementation checks the integer engine
    # at every primitive for every coefficient in the actual two input words.
    # Unequal starting denominators exercise alignment and normalization.
    primitive_checks = 0
    for q in sorted(coefficients):
        rational = {t: {0: Q(3, 4), 1: Q(-1, 2)}, s: {1: Q(5, 8), 2: Q(-1)}, work: {3: Q(7, 16)}}
        expected_target = {0: Q(3, 4), 1: Q(-1, 2) + q*Q(5, 8), 2: -q}
        expected_target = {j: x for j, x in expected_target.items() if x}
        integer = {t: (2, {0: 3, 1: -2}), s: (3, {1: 5, 2: -8}), work: (4, {3: 7})}
        op = ["add", list(t), list(s), q.numerator, q.denominator]
        for primitive in comparator.lower(op, work):
            fraction_step(rational, primitive)
            integer_step(integer, primitive)
            reconstructed = {r: {j: Q(x, 1 << shift) for j, x in values.items()} for r, (shift, values) in integer.items()}
            require(reconstructed == rational, "integer/Fraction primitive disagreement")
            primitive_checks += 1
        require(rational == {t: expected_target, s: {1: Q(5, 8), 2: Q(-1)}, work: {}}, "coefficient macro identity")
    return {"rejected": accepted, "coefficient_crosschecks": len(coefficients),
            "primitive_crosschecks": primitive_checks,
            "positive_controls": ["same_frame_nonwork_macros", "both_unit_signs", "all_opaque_boundaries"]}
