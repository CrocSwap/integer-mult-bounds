"""Exact GF(8) connector construction, produced by Nick Petalas. Apache-2.0."""

import hashlib
import json
import platform
from pathlib import Path


# Group bits 0,1,2 and 3,4,5 of Aaron Wang's PR2128 word separately.
STEPS = (2, 16, 8, 16, 1, 4, 48, 4, 3, 4, 32, 8, 4, 16)
PACKAGE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(a, b):
    """Polynomial basis 1,t,t^2, with t^3=t+1; inputs are field encodings."""
    need(0 <= a < 8 and 0 <= b < 8, "invalid field element")
    result = 0
    for _ in range(3):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 8:
            a ^= 11
    return result


def reference_multiply(a, b):
    result = 0
    for i in range(3):
        for j in range(3):
            result ^= ((a >> i & 1) & (b >> j & 1)) << (i + j)
    for degree in (4, 3):
        if result >> degree & 1:
            result ^= 11 << (degree - 3)
    return result


def field_checks():
    for a in range(8):
        for b in range(8):
            need(multiply(a, b) == reference_multiply(a, b), "field product")
            for c in range(8):
                need(multiply(multiply(a, b), c) == multiply(a, multiply(b, c)),
                     "field associativity")
                need(multiply(a, b ^ c) == multiply(a, b) ^ multiply(a, c),
                     "field distributivity")
    for a in range(1, 8):
        need(sum(multiply(a, b) == 1 for b in range(1, 8)) == 1, "field inverse")
    return 64, 1024, 7


def source_events(steps):
    need(len(steps) <= 16, "source word limit")
    events = []
    for step in steps:
        need(0 < step < 64, "invalid source step")
        low, high = step & 7, step >> 3
        need(bool(low) != bool(high), "a source call changes two coordinates")
        events.append(("B", int(bool(high)), high or low))
    return events


def compile_word(steps):
    sources = source_events(steps)
    prefixes = [0]
    for step in steps:
        prefixes.append(prefixes[-1] ^ step)
    need(prefixes[-1] == 0, "connector not restored")
    pairs = {}
    for s in range(len(steps)):
        for t in range(s + 1, len(steps)):
            mask = prefixes[s] ^ prefixes[t]
            if mask:
                pairs.setdefault(mask, (s, t))
    need(set(pairs) == set(range(1, 64)), "missing coefficient row")
    program = []
    for boundary in range(len(steps) + 1):
        for mask in range(1, 64):
            if boundary in pairs[mask]:
                program.append(("A", mask, 1))
        if boundary < len(sources):
            program.append(sources[boundary])
    need(len(program) <= 142, "program limit")
    return tuple(program), prefixes, pairs


def add_expression(target, source, coefficient, operator):
    for (word, origin), value in source.items():
        key = ((operator,) + word, origin)
        new = target.get(key, 0) ^ multiply(coefficient, value)
        if new:
            target[key] = new
        else:
            target.pop(key, None)


def symbolic_endpoint(program):
    """Free, noncommutative map words on 66 independent incoming roles."""
    need(len(program) <= 142, "symbolic program limit")
    state = [{((), role): 1} for role in range(66)]
    for kind, role, coefficient in program:
        if kind == "B":
            add_expression(state[2], state[role], coefficient, ("B", role))
        else:
            need(kind == "A" and 1 <= role <= 63, "invalid readout")
            add_expression(state[role + 2], state[2], coefficient, ("A", role))
    expected = [{((), role): 1} for role in range(66)]
    for mask in range(1, 64):
        for source, coefficient in enumerate((mask & 7, mask >> 3)):
            if coefficient:
                key = ((("A", mask), ("B", source)), source)
                expected[mask + 2][key] = coefficient
    return state == expected


def apply_matrix(matrix, vector):
    result = []
    for row in matrix:
        value = 0
        for coefficient, entry in zip(row, vector, strict=True):
            value ^= reference_multiply(coefficient, entry)
        result.append(value)
    return result


def dense_program(program, initial, sources, readers):
    state = [row[:] for row in initial]
    for kind, role, coefficient in program:
        if kind == "B":
            value = apply_matrix(sources[role], state[role])
            destination = 2
        else:
            value = apply_matrix(readers[role - 1], state[2])
            destination = role + 2
        for i in range(len(value)):
            state[destination][i] ^= reference_multiply(coefficient, value[i])
    return state


def dense_expected(initial, sources, readers):
    result = [row[:] for row in initial]
    values = [apply_matrix(sources[j], initial[j]) for j in range(2)]
    for mask in range(1, 64):
        combination = [reference_multiply(mask & 7, a)
                       ^ reference_multiply(mask >> 3, b)
                       for a, b in zip(*values, strict=True)]
        update = apply_matrix(readers[mask - 1], combination)
        result[mask + 2] = [a ^ b for a, b in
                            zip(initial[mask + 2], update, strict=True)]
    return result


def dense_checks(program):
    count = 0
    for dimension in (1, 2, 3):
        sources = [[[int(i == j) ^ int(i == 0 and j == dimension - 1)
                     for j in range(dimension)] for i in range(dimension)],
                   [[int(i == j) ^ int(i == dimension - 1 and j == 0)
                     for j in range(dimension)] for i in range(dimension)]]
        readers = [[[(mask * (i + 1) + j * j + 3 * j) % 8
                     for j in range(dimension)] for i in range(dimension)]
                   for mask in range(1, 64)]
        for column in range(66 * dimension + 1):
            initial = [[0] * dimension for _ in range(66)]
            if column < 66 * dimension:
                initial[column // dimension][column % dimension] = 1
            else:
                initial = [[(role * 5 + i * 3 + 7) % 8
                            for i in range(dimension)] for role in range(66)]
            expected = dense_expected(initial, sources, readers)
            actual = dense_program(program, initial, sources, readers)
            need(actual == expected, "dense forward endpoint")
            need(dense_program(tuple(reversed(program)), actual, sources, readers)
                 == initial, "dense inverse endpoint")
            count += 1
    return count


def mutation_checks(program):
    count = 0
    for index, (kind, role, coefficient) in enumerate(program):
        need(not symbolic_endpoint(program[:index] + program[index + 1:]),
             "undetected omitted call")
        count += 1
        replacement = ((kind, role, coefficient % 7 + 1) if kind == "B"
                       else (kind, role % 63 + 1, coefficient))
        mutant = program[:index] + (replacement,) + program[index + 1:]
        need(not symbolic_endpoint(mutant), "undetected changed call")
        count += 1
    for steps in (STEPS[:-1], STEPS + (9,), (1,) * 14):
        try:
            compile_word(steps)
        except ValueError:
            count += 1
        else:
            raise ValueError("undetected malformed source word")
    return count


def hashes():
    result = {}
    for name in ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"):
        with (PACKAGE / name).open("rb") as stream:
            data = stream.read(200_001)
        need(len(data) <= 200_000, "package file size limit")
        result[name] = hashlib.sha256(data).hexdigest()
    return result


def main():
    products, laws, inverses = field_checks()
    program, prefixes, pairs = compile_word(STEPS)
    need(len(program) == 140 and len(set(prefixes[:-1])) == 14, "word shape")
    need(symbolic_endpoint(program), "free-map endpoint")
    need(symbolic_endpoint(tuple(reversed(program))), "free-map inverse")
    gray = (1, 2, 1, 4, 1, 2, 1, 4)
    baseline, _, _ = compile_word(gray + tuple(8 * step for step in gray))
    need(len(baseline) == 142 and symbolic_endpoint(baseline), "axis comparator")
    # Transfer PR2156/PR2249's counting argument to the field contract.
    # PR4651's no-12/no-13 theorem is CITED; its census is not executed.
    short_bounds = [b + 126 + 2 * max(0, 63 - b * (b - 1) // 2)
                    for b in range(12)]
    need(min(short_bounds) == 153, "short-word arithmetic")
    need(12 + 126 + 2 == 140 and 13 + 126 + 2 == 141, "cited-bound arithmetic")
    receipt = {"claim_type": "scoped proof with finite construction",
               "dependency": "PR4651 difference-basis exclusion, cited only",
               "field_products": products, "field_laws": laws,
               "field_inverses": inverses, "source_calls": 14,
               "source_calls_by_role": [sum(e[:2] == ("B", j) for e in program)
                                        for j in range(2)],
               "readouts": 126, "complete_calls": len(program),
               "axis_comparator_calls": len(baseline),
               "descriptor_bits": sum(5 if e[0] == "B" else 7 for e in program),
               "axis_descriptor_bits": sum(5 if e[0] == "B" else 7
                                           for e in baseline),
               "prefixes": prefixes, "pairs": pairs,
               "dense_forward_inverse_cases": dense_checks(program),
               "rejected_mutations": mutation_checks(program),
               "python": platform.python_version(), "sha256": hashes()}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_GF8_TWO_SOURCE_OPTIMUM calls=140 sources=14 readouts=126 "
          f"dense={receipt['dense_forward_inverse_cases']} "
          f"controls={receipt['rejected_mutations']} cited_lower_bound=PR4651")


if __name__ == "__main__":
    main()
