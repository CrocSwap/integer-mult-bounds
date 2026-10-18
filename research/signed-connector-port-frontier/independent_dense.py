#!/usr/bin/env python3
"""Independent finite dense replay and physical invoice for port witnesses.

This module deliberately does not import the search, its arithmetic model, or
any predecessor implementation. Its oracle uses ordinary exact integer matrix
multiplication; its candidate executor expands a balanced commutator into
single-factor row updates over the full space of independent dirty inputs.
It is a finite check, not a proof of an arbitrary-dimension identity.
Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
CONNECTOR = ((1, 1, 1), (1, 1, -1), (1, -1, 0))
LENGTHS = (2, 3, 4, 5, 6, 7)  # B0,B1,B2,A0,A1,A2; application order.
ROW_COUNT = 11
FACTOR_IDS = tuple(tuple(range(sum(LENGTHS[:k]), sum(LENGTHS[:k + 1])))
                   for k in range(6))
# (factor or -1 for a root transfer, source row, target row, signed multiplier)
Instruction = tuple[int, int, int, int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def inverse(program: list[Instruction]) -> list[Instruction]:
    return [(f, source, target, -sign)
            for f, source, target, sign in reversed(program)]


def lower(factors: tuple[int, ...], source: int, target: int,
          scratch: tuple[int, ...] = (8, 9, 10)) -> list[Instruction]:
    """Apply f0 first, f1 second, etc.; return private rows exactly restored."""
    require(source != target, "a factor cannot overwrite its own input")
    if len(factors) == 1:
        return [(factors[0], source, target, 1)]
    require(bool(scratch), "insufficient private rows")
    work, remaining = scratch[0], scratch[1:]
    require(work not in (source, target), "aliased scratch")
    split = len(factors) // 2
    early = lower(factors[:split], source, work, remaining)
    late = lower(factors[split:], work, target, remaining)
    return early + late + inverse(early) + inverse(late)


def expand(word: list, factor_ids=FACTOR_IDS) -> list[Instruction]:
    program = []
    for kind, op, sign, port in word:
        if kind == "R":
            program.append((-1, 7, 6, sign))
        else:
            factors = factor_ids[op if kind == "B" else op + 3]
            source, target = ((op, 6 + port) if kind == "B"
                              else (6 + port, 3 + op))
            child = lower(factors, source, target)
            program.extend(child if sign == 1 else inverse(child))
    return program


def validate_word(mask: int, word: list) -> None:
    require(type(mask) is int and 0 <= mask < 64, "invalid six-bit mask")
    require(isinstance(word, list) and len(word) == 16,
            "each witness needs twelve queries and four transfers")
    uses = {(kind, op): [] for kind in ("B", "A") for op in range(3)}
    roots = []
    for item in word:
        require(isinstance(item, list) and len(item) == 4, "bad word record")
        kind, op, sign, port = item
        require(type(sign) is int and sign in (-1, 1), "nonunit sign")
        if kind == "R":
            require(op == 1 and port == 0, "unsupported root transfer")
            roots.append(sign)
        else:
            require(kind in ("B", "A") and type(op) is int and 0 <= op < 3,
                    "bad operator")
            bit = op if kind == "B" else op + 3
            require(type(port) is int and port == ((mask >> bit) & 1),
                    "word disagrees with declared port mask")
            uses[kind, op].append(sign)
    require(len(roots) == 4 and sum(roots) == 0,
            "four balanced root transfers required")
    require(all(sorted(signs) == [-1, 1] for signs in uses.values()),
            "every operator needs one positive and one negative call")


def zero(rows: int, cols: int) -> list[list[int]]:
    return [[0] * cols for _ in range(rows)]


def identity(n: int) -> list[list[int]]:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    # Dot-product implementation is independent of the candidate row executor.
    columns = list(zip(*right))
    return [[sum(a * b for a, b in zip(row, col)) for col in columns]
            for row in left]


def product_in_application_order(ids: tuple[int, ...], matrices, dimension):
    result = identity(dimension)
    for f in ids:
        result = multiply(matrices[f], result)
    return result


def make_matrices(dimension: int, seed: int):
    rng = random.Random(seed)
    while True:
        matrices = [[[rng.randrange(-2, 3) for _ in range(dimension)]
                     for _ in range(dimension)] for _ in range(sum(LENGTHS))]
        # Guarantee the chosen factor-order controls exercise noncommutativity.
        if all(multiply(matrices[ids[0]], matrices[ids[1]]) !=
               multiply(matrices[ids[1]], matrices[ids[0]])
               for ids in FACTOR_IDS):
            return matrices


def expected_map(dimension: int, matrices):
    result = identity(ROW_COUNT * dimension)
    operators = [product_in_application_order(ids, matrices, dimension)
                 for ids in FACTOR_IDS]
    for output in range(3):
        for source in range(3):
            block = multiply(operators[output + 3], operators[source])
            for row in range(dimension):
                for col in range(dimension):
                    result[(3 + output) * dimension + row][source * dimension + col] += (
                        CONNECTOR[output][source] * block[row][col])
    return result


def execute(program: list[Instruction], dimension: int, matrices, initial=None):
    state = identity(ROW_COUNT * dimension) if initial is None else [r[:] for r in initial]
    width = ROW_COUNT * dimension
    for factor, source, target, sign in program:
        if factor == -1:
            for k in range(dimension):
                src = state[source * dimension + k]
                dst = state[target * dimension + k]
                for col in range(width):
                    dst[col] += sign * src[col]
        else:
            for row in range(dimension):
                dst = state[target * dimension + row]
                for k in range(dimension):
                    coefficient = sign * matrices[factor][row][k]
                    if coefficient:
                        src = state[source * dimension + k]
                        for col in range(width):
                            dst[col] += coefficient * src[col]
    return state


def coefficient_invoice(program: list[Instruction]) -> list[int]:
    """Coefficients of L^4,L^3,L^2,L,1, independently summed per primitive."""
    answer = [0] * 5
    for f, p, q, sign in program:
        if f == -1:
            term = (0, 0, 2, 14, -2)
        else:
            term = (2 * f + 1, 21 - 2 * min(p, q), 0, 2 * (q + 1), -2)
        answer = [a + b for a, b in zip(answer, term)]
    return answer


def evaluate(coefficients: list[int], dimension: int) -> int:
    value = 0
    for c in coefficients:
        value = value * dimension + c
    return value


def literal_invoice(program: list[Instruction], dimension: int) -> dict:
    """Trace each physical visit, returning to cell zero after each primitive."""
    counts = dict(head_moves=0, coefficient_reads=0, multiplications=0,
                  source_reads=0, target_read_writes=0, additions=0,
                  work_clears=0, negations=0, factor_dispatches=0,
                  root_dispatches=0, instruction_records=len(program))
    for f, p, q, sign in program:
        head = 0
        counts["root_dispatches" if f == -1 else "factor_dispatches"] += 1
        if f == -1:
            addresses = ((p * dimension + k, q * dimension + k)
                         for k in range(dimension))
        else:
            addresses = ((ROW_COUNT * dimension + f * dimension ** 2 + i * dimension + j,
                          p * dimension + j, q * dimension + i)
                         for i in range(dimension) for j in range(dimension))
        for visits in addresses:
            if f != -1:
                counts["coefficient_reads"] += 1
                counts["multiplications"] += 1
            for field in ("source_reads", "target_read_writes", "additions", "work_clears"):
                counts[field] += 1
            counts["negations"] += int(sign == -1)
            for address in visits:
                counts["head_moves"] += abs(address - head)
                head = address
        counts["head_moves"] += abs(head)
    return counts


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def controls(word: list):
    for index in range(len(word)):
        changed = [item[:] for item in word]
        changed[index][2] *= -1
        yield f"flip_short_sign_{index}", expand(changed)
        yield f"remove_short_instruction_{index}", expand(word[:index] + word[index + 1:])
    for index, original in enumerate(FACTOR_IDS):
        reordered = list(FACTOR_IDS)
        reordered[index] = (original[1], original[0]) + original[2:]
        yield f"swap_first_two_factors_{index}", expand(word, tuple(reordered))
    # A recursive cleanup control below the short-word layer.
    program = expand(word)
    cleanup = next(i for i, item in enumerate(program) if item[0] >= 0 and item[3] == -1)
    yield "remove_recursive_negative_leaf", program[:cleanup] + program[cleanup + 1:]


def build_result(certificate: dict) -> dict:
    witnesses = certificate["witnesses"]
    require(isinstance(witnesses, list) and witnesses, "no witnesses")
    masks = [item["mask"] for item in witnesses]
    require(len(set(masks)) == len(masks), "duplicate witness mask")
    fixtures = []
    for dimension, seed in ((2, 310002), (2, 310003), (3, 310002), (3, 310003)):
        matrices = make_matrices(dimension, seed)
        fixtures.append((dimension, seed, matrices, expected_map(dimension, matrices)))
    records = []
    total_controls = 0
    for witness in sorted(witnesses, key=lambda item: item["mask"]):
        mask, word = witness["mask"], witness["word"]
        validate_word(mask, word)
        program = expand(word)
        factors = sum(f >= 0 for f, _, _, _ in program)
        root_count = sum(f == -1 for f, _, _, _ in program)
        require((factors, root_count) == (300, 4), "wrong expanded call counts")
        fixture_records = []
        for dimension, seed, matrices, expected in fixtures:
            actual = execute(program, dimension, matrices)
            require(actual == expected, f"dense identity failed mask={mask} L={dimension} seed={seed}")
            restored = execute(inverse(program), dimension, matrices, actual)
            require(restored == identity(ROW_COUNT * dimension),
                    f"inverse failed mask={mask} L={dimension} seed={seed}")
            fixture_records.append(dict(dimension=dimension, seed=seed,
                                        independent_columns=ROW_COUNT * dimension,
                                        input_sha256=digest(matrices),
                                        output_sha256=digest(actual), inverse_restored=True))
        mutation_records = []
        for name, mutated in controls(word):
            rejection = None
            for dimension, seed, matrices, expected in fixtures:
                actual = execute(mutated, dimension, matrices)
                if actual != expected:
                    mismatch = next((i, j) for i, (a, b) in enumerate(zip(actual, expected))
                                    for j, (x, y) in enumerate(zip(a, b)) if x != y)
                    i, j = mismatch
                    rejection = dict(name=name, dimension=dimension, seed=seed,
                                     first_mismatch=[i, j], observed=actual[i][j],
                                     expected=expected[i][j])
                    break
            require(rejection is not None, f"undetected mutation mask={mask} {name}")
            mutation_records.append(rejection)
        polynomial = coefficient_invoice(program)
        invoices = []
        for dimension in (1, 2, 3):
            literal = literal_invoice(program, dimension)
            require(literal["head_moves"] == evaluate(polynomial, dimension),
                    f"polynomial disagrees with literal trace mask={mask} L={dimension}")
            require(literal["coefficient_reads"] == 300 * dimension ** 2,
                    "coefficient coverage weakened")
            require(literal["source_reads"] == 300 * dimension ** 2 + 4 * dimension,
                    "source coverage weakened")
            invoices.append(dict(dimension=dimension, **literal))
        records.append(dict(mask=mask, word_sha256=digest(word), factor_calls=factors,
                            root_passes=root_count, private_rows=3,
                            head_move_polynomial_descending=polynomial,
                            fixtures=fixture_records, literal_invoices=invoices,
                            rejected_mutations=mutation_records))
        total_controls += len(mutation_records)
    return dict(schema="signed-connector-port-frontier-independent-dense-v1",
                scope="Finite exact integer matrix fixtures and a declared literal dense tape invoice; no general theorem or supplier realization claim.",
                independent_of="No search model or predecessor implementation imports; matrix-product oracle, recursive lowerer, and literal tape visitor are separate paths.",
                matrix_factor_application_order="f0 then f1 then remaining factors; product f_last ... f1 f0",
                row_order=["x0", "x1", "x2", "y0", "y1", "y2", "z", "w", "private0", "private1", "private2"],
                operator_order=["B0", "B1", "B2", "A0", "A1", "A2"],
                operator_lengths=list(LENGTHS), target=[list(row) for row in CONNECTOR],
                witness_count=len(records), fixtures_per_witness=len(fixtures),
                independent_columns_per_witness=sum(ROW_COUNT * f[0] for f in fixtures),
                rejected_mutation_count=total_controls, witnesses=records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    parser.add_argument("--write", action="store_true", help="write DENSE.json rather than compare it")
    args = parser.parse_args()
    result = build_result(json.loads(args.certificate.read_text()))
    output = HERE / "DENSE.json"
    if args.write:
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(output.read_text()) == result, "DENSE.json differs from independent replay")
    print(f"independent dense replay: {result['witness_count']} masks, "
          f"{result['fixtures_per_witness']} fixtures each, "
          f"{result['rejected_mutation_count']} rejected mutations; exact invoices pass")


if __name__ == "__main__":
    main()
