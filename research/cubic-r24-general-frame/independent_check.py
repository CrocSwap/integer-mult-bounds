#!/usr/bin/env python3
"""Independent exact expansion and literal-program check for the r=24 repair.

This checker imports neither the primary verifier nor its certificate.  Its
hardcoded data are checked by direct polynomial expansion and literal source
updates.  It is an independent implementation, not independent human review.
"""

from fractions import Fraction as F
import json


ARITY = 24
DEFECT_TERMS = (
    (F(-23, 1024), 11, 19),
    (F(1679, 64), 1, 9),
    (F(3749, 1024), 1, 25),
)

# A shear adds coefficient times the other source.  A query adds coefficient
# times the named source cubed to y.  These are the literal appended operations
# after all 24 retained children have run.
PROGRAM = (
    ("shear", "a", F(1)),
    ("query", "a", F(-3749, 1024)),
    ("shear", "b", F(-11, 256)),
    ("query", "b", F(-376832)),
    ("shear", "b", F(11, 256)),
    ("shear", "a", F(-16)),
    ("query", "a", F(-1679, 64)),
    ("shear", "a", F(-9)),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def cube(a, b):
    """Coefficients of (a*A+b*B)^3 in A^3,A^2*B,A*B^2,B^3 order."""
    return (a**3, 3 * a * a * b, 3 * a * b * b, b**3)


def add_scaled(left, right, coefficient):
    return tuple(x + coefficient * y for x, y in zip(left, right))


def check_identity(terms=DEFECT_TERMS, arity=ARITY):
    expected = (F(-arity), F(0), F(0), F(0))
    for i in range(arity):
        expected = add_scaled(expected, cube(F(1), F(i)), F(1))
    actual = (F(0),) * 4
    for weight, a, b in terms:
        require(weight != 0, "zero defect weight")
        require(
            weight.denominator & (weight.denominator - 1) == 0,
            "non-dyadic defect weight",
        )
        actual = add_scaled(actual, cube(F(a), F(b)), weight)
    require(actual == expected, f"defect coefficient mismatch: {actual} != {expected}")
    return actual


def check_symbolic_program(program=PROGRAM, arity=ARITY):
    # The incoming y is a separate untouched additive symbol Y.  output tracks
    # only the polynomial added to it, so this check applies to every dirty Y.
    sources = {"a": (F(1), F(0)), "b": (F(0), F(1))}
    output = (F(0),) * 4
    for _ in range(arity):
        output = add_scaled(output, cube(*sources["a"]), F(1))
        sources["a"] = add_scaled(sources["a"], sources["b"], F(1))
    for kind, source, coefficient in program:
        require(source in sources, "unknown source")
        require(
            coefficient.denominator & (coefficient.denominator - 1) == 0,
            "non-dyadic program coefficient",
        )
        if kind == "shear":
            other = "b" if source == "a" else "a"
            sources[source] = add_scaled(sources[source], sources[other], coefficient)
        elif kind == "query":
            output = add_scaled(output, cube(*sources[source]), coefficient)
        else:
            raise ValueError("unknown operation")
    require(sources["a"] == (F(1), F(0)), "a not restored")
    require(sources["b"] == (F(0), F(1)), "b not restored")
    require(output == (F(arity), F(0), F(0), F(0)), "wrong eager output")


def run_literal(a, b, y, program=PROGRAM, arity=ARITY):
    sources = {"a": F(a), "b": F(b)}
    y = F(y)
    for _ in range(arity):
        y += sources["a"] ** 3
        sources["a"] += sources["b"]
    for kind, source, coefficient in program:
        if kind == "shear":
            other = "b" if source == "a" else "a"
            sources[source] += coefficient * sources[other]
        elif kind == "query":
            y += coefficient * sources[source] ** 3
        else:
            raise ValueError("unknown operation")
    return sources["a"], sources["b"], y


def rejected(label, callback):
    try:
        callback()
    except ValueError:
        return label
    raise ValueError(f"negative control was accepted: {label}")


def replace_operation(index, operation):
    return PROGRAM[:index] + (operation,) + PROGRAM[index + 1 :]


def run_checks():
    coefficients = check_identity()
    check_symbolic_program()
    require(sum(kind == "query" for kind, _, _ in PROGRAM) == 3, "query count")
    require(sum(kind == "shear" for kind, _, _ in PROGRAM) == 5, "shear count")
    # Include dirty sources and output, signs, odd denominators, zero sources,
    # and dyadic values.  These are corroboration of the polynomial identity.
    inputs = (
        (0, 0, 7), (1, 0, -3), (0, 1, 11), (1, 1, 5),
        (-2, 3, 7), (5, -4, -19), (F(1, 3), F(2, 5), F(-7, 11)),
        (F(-13, 7), F(17, 9), F(23, 5)),
        (F(7, 8), F(-9, 16), F(11, 32)),
        (F(101, 13), F(5, 17), F(-29, 19)),
        (F(-2, 3), 0, F(5, 7)), (0, F(-7, 5), F(-1, 3)),
    )
    for a, b, y in inputs:
        expected = (F(a), F(b), F(y) + ARITY * F(a) ** 3)
        require(run_literal(a, b, y) == expected, f"dirty input failed: {(a, b, y)}")

    monic = ((F(-23, 1024), 1, 19),) + DEFECT_TERMS[1:]
    perturbed = replace_operation(3, ("query", "b", F(-376831)))
    wrong_sign = replace_operation(3, ("query", "b", F(376832)))
    wrong_order = (PROGRAM[1], PROGRAM[0]) + PROGRAM[2:]
    controls = [
        rejected("nonmonic form replaced by monic", lambda: check_identity(monic)),
        rejected("omitted final a restoration", lambda: check_symbolic_program(PROGRAM[:-1])),
        rejected("omitted b restoration", lambda: check_symbolic_program(PROGRAM[:4] + PROGRAM[5:])),
        rejected("perturbed query weight", lambda: check_symbolic_program(perturbed)),
        rejected("wrong query sign", lambda: check_symbolic_program(wrong_sign)),
        rejected("query before its source shear", lambda: check_symbolic_program(wrong_order)),
        rejected("wrong retained arity", lambda: check_symbolic_program(arity=23)),
        rejected("omitted b query", lambda: check_symbolic_program(PROGRAM[:3] + PROGRAM[4:])),
    ]
    return {
        "status": "pass",
        "arity": ARITY,
        "defect_coefficients": [str(value) for value in coefficients],
        "cube_queries": 3,
        "source_shears": 5,
        "symbolic_dirty_restoration": "pass",
        "dirty_rational_inputs": len(inputs),
        "rejected_controls": controls,
    }


if __name__ == "__main__":
    print(json.dumps(run_checks(), indent=2))
