"""Exact bounded checks, produced by Nick Petalas. Apache-2.0."""

import hashlib
import itertools
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from compiler import compile_chain


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    basis = [0] * len(rows)
    result = 0
    for row in rows:
        value = row
        for column in range(len(rows) - 1, -1, -1):
            if (value >> column) & 1:
                if basis[column]:
                    value ^= basis[column]
                else:
                    basis[column] = value
                    result += 1
                    break
    return result


def formal(program, roles):
    """Propagate every dirty input in the basis 1,g of the full F2[C2]."""
    ordinary = [1 << index for index in range(roles)]
    reflected = [0] * roles
    for operation, target_role, source in program:
        require(0 <= target_role < roles and 0 <= source < roles, "bad role")
        if operation == "xor":
            require(target_role != source, "noninvertible scalar addition")
            ordinary[target_role] ^= ordinary[source]
            reflected[target_role] ^= reflected[source]
        else:
            require(operation == "reflect" and target_role == source, "bad opcode")
            ordinary[target_role], reflected[target_role] = reflected[target_role], ordinary[target_role]
    return tuple(ordinary), tuple(reflected)


def target(length, roles):
    ordinary = [1 << index for index in range(roles)]
    reflected = [0] * roles
    for index in range(length - 1):
        ordinary[index] ^= 1 << (index + 1)
        reflected[index] = 1 << (index + 1)
    return tuple(ordinary), tuple(reflected)


def projectors(length, roles):
    """Construct the proof's summands independently of the primitive stream."""
    result = []
    for first in range(0, length - 2, 2):
        middle, last = first + 1, first + 2
        left, right = [0] * roles, [0] * roles
        left[first] = left[middle] = 1 << middle
        right[middle] = (1 << middle) | (1 << last)
        result.extend((tuple(left), tuple(right)))
    if length % 2 == 0:
        first, last = length - 2, length - 1
        left, right = [0] * roles, [0] * roles
        left[first] = left[last] = right[last] = 1 << last
        result.extend((tuple(left), tuple(right)))
    return result


def matrix_product(left, right):
    result = []
    for row in left:
        value = 0
        for column, other in enumerate(right):
            if (row >> column) & 1:
                value ^= other
        result.append(value)
    return tuple(result)


def formal_checks():
    summands = 0
    for length in range(1, 65):
        roles = min(64, length + 3)
        program = compile_chain(length, roles)
        require(formal(program, roles) == target(length, roles), "formal endpoint")
        require(formal(program[::-1], roles) == target(length, roles), "inverse endpoint")
        turns = sum(operation == "reflect" for operation, _, _ in program)
        scalar = sum(operation == "xor" for operation, _, _ in program)
        require(turns == 2 * (length // 2), "reflection tariff")
        require(scalar == 2 * (length - 1), "scalar invoice")
        total = [0] * roles
        factors = projectors(length, roles)
        require(len(factors) == turns, "summand invoice")
        for factor in factors:
            require(rank(factor) == 1, "summand rank")
            require(matrix_product(factor, factor) == factor, "idempotence")
            require(sum((row >> i) & 1 for i, row in enumerate(factor)) % 2 == 1,
                    "summand trace")
            total = [a ^ b for a, b in zip(total, factor, strict=True)]
            summands += 1
        require(tuple(total) == target(length, roles)[1], "projector sum")
        require(rank(total) == length - 1, "chain rank")
    return {"formal_chain_lengths": 64, "projector_summands": summands}


def literal(program, values, permutation):
    """Execute whole bit arrays, independently of formal matrix coefficients."""
    state = list(values)
    for operation, destination, source in program:
        if operation == "xor":
            state[destination] ^= state[source]
        elif operation == "reflect":
            image = 0
            for address, moved in enumerate(permutation):
                image |= ((state[destination] >> address) & 1) << moved
            state[destination] = image
        else:
            raise ValueError("unknown literal primitive")
    return tuple(state)


def expected(values, length, permutation):
    result = list(values)
    for destination in range(length - 1):
        source = values[destination + 1]
        image = sum(((source >> i) & 1) << moved
                    for i, moved in enumerate(permutation))
        result[destination] ^= source ^ image
    return tuple(result)


def exhaustive_states():
    counts = {"two_address_states": 0, "dirty_spectator_states": 0}
    domains = [(n, n, "two_address_states") for n in range(1, 9)]
    domains += [(n, n + 2, "dirty_spectator_states") for n in range(3, 6)]
    for length, roles, key in domains:
        program = compile_chain(length, roles)
        for code in range(1 << (2 * roles)):
            values = tuple((code >> (2 * i)) & 3 for i in range(roles))
            result = literal(program, values, (1, 0))
            require(result == expected(values, length, (1, 0)), "dirty state")
            counts[key] += 1
    return counts


def basis_checks():
    columns = permutations = 0
    for size in range(1, 7):
        for permutation in itertools.permutations(range(size)):
            if any(permutation[permutation[i]] != i for i in range(size)):
                continue
            permutations += 1
            for length in (3, 4, 5, 8, 17, 32):
                roles = length + 2
                program = compile_chain(length, roles)
                for column in range(roles * size):
                    values = [0] * roles
                    values[column // size] = 1 << (column % size)
                    result = literal(program, values, permutation)
                    require(result == expected(values, length, permutation), "literal column")
                    columns += 1
    return {"involutory_permutations": permutations, "literal_basis_columns": columns}


def pair_census():
    """Check the new rank-two chain's complete shortest two-call domain."""
    counts = []
    for roles in (3, 4):
        factors = []
        for vector in range(1, 1 << roles):
            for functional in range(1, 1 << roles):
                if (vector & functional).bit_count() % 2:
                    factors.append(tuple(functional if (vector >> i) & 1 else 0
                                         for i in range(roles)))
        goal = target(3, roles)[1]
        require(goal not in factors, "unexpected one-call endpoint")
        hits = 0
        for left in factors:
            for right in factors:
                hits += tuple(a ^ b for a, b in zip(left, right, strict=True)) == goal
        require(hits > 0, "complete two-call domain has no witness")
        counts.append({"roles": roles, "ordered_pairs": len(factors) ** 2, "hits": hits})
    return {"rank_two_chain_pair_censuses": counts}


def rejection_checks():
    omissions = 0
    for length in range(3, 9):
        program = compile_chain(length)
        for index in range(len(program)):
            mutant = program[:index] + program[index + 1:]
            require(formal(mutant, length) != target(length, length), "unrejected omission")
            omissions += 1
    failures = 0
    for args in ((True,), (0,), (65,), (3, 2), (3, True), (3, 65)):
        try:
            compile_chain(*args)
        except ValueError:
            failures += 1
        else:
            raise ValueError("invalid compiler boundary admitted")
    program = compile_chain(3)
    bad_label = any(literal(program, (0, 1 << i, 0), (1, 2, 0)) !=
                    expected((0, 1 << i, 0), 3, (1, 2, 0)) for i in range(3))
    require(bad_label, "noninvolutory-label control")
    wrong = tuple((op, 0, 0) if op == "reflect" else (op, a, b)
                  for op, a, b in program)
    require(formal(wrong, 3) != target(3, 3), "wrong reflection role")
    return {"primitive_omissions_rejected": omissions, "invalid_boundaries_rejected": failures,
            "semantic_controls_rejected": 2}


def main():
    report = {"marker": "PASS_NILPOTENT_CHAIN_REFLECTION_COMPILER",
              "claim_type": "scoped proof with exact finite corroboration",
              "python": sys.version.split()[0], "no_new_kappa": True}
    report.update(formal_checks())
    report.update(exhaustive_states())
    report.update(basis_checks())
    report.update(pair_census())
    report.update(rejection_checks())
    files = sorted(PACKAGE.iterdir())
    report["sha256"] = {}
    for path in files:
        if path.is_file():
            require(path.stat().st_size <= 1_048_576, "oversized package file")
            report["sha256"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
