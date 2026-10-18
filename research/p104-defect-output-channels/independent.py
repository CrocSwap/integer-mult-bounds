#!/usr/bin/env python3
"""Independent exact output-defect span check; no predecessor imports.

Interleaved signed integer Re/Im coordinates, stages in increasing bit order.
Integer defects are 2**rank * literal_lift - ideal_integer_numerator.
Nonzero pivots modulo the prime 65521 prove independence over Q and R.
"""

from hashlib import sha256
import json
from itertools import product
import sys


PRIME = 65521


def need(condition, message):
    if not condition:
        raise ValueError(message)


def literal_and_numerator(value, rank):
    size = 1 << rank
    need(len(value) == 2 * size and all(type(x) is int for x in value),
         "interleaved integer input shape")
    literal, numerator = list(value), list(value)
    for bit in range(rank):
        for a in range(size):
            if (a >> bit) & 1:
                continue
            b = a ^ (1 << bit)
            ar, ai, br, bi = (literal[t] for t in (2*a, 2*a+1, 2*b, 2*b+1))
            dr, di = ar-br, ai-bi
            sr, si = br + dr//2, bi + di//2
            nr, ni = -di, dr
            cr, ci = sr - nr//2, si - ni//2
            literal[2*a:2*a+2] = [cr+nr, ci+ni]
            literal[2*b:2*b+2] = [cr, ci]
            ar, ai, br, bi = (numerator[t] for t in (2*a, 2*a+1, 2*b, 2*b+1))
            numerator[2*a:2*a+2] = [ar-ai+br+bi, ar+ai-br+bi]
            numerator[2*b:2*b+2] = [ar+ai+br-bi, -ar+ai+br+bi]
    return literal, numerator


def defect(value, rank):
    literal, numerator = literal_and_numerator(value, rank)
    return [(1 << rank)*x-y for x, y in zip(literal, numerator)]


def walsh(value, rank):
    result = list(value)
    for bit in range(rank):
        for a in range(1 << rank):
            if (a >> bit) & 1:
                continue
            b = a ^ (1 << bit)
            for component in range(2):
                ia, ib = 2*a+component, 2*b+component
                x, y = result[ia], result[ib]
                result[ia], result[ib] = x+y, x-y
    return result


def phases(mode, rank):
    return {(mode >> (j+1)).bit_count() % 2
            for j in range(rank) if not ((mode >> j) & 1)}


def check_annihilators(value, rank):
    check_mode_annihilators(walsh(value, rank), rank)


def check_mode_annihilators(transformed, rank):
    for mode in range(1 << rank):
        possible = phases(mode, rank)
        re, im = transformed[2*mode:2*mode+2]
        if not possible:
            need(re == im == 0, "forbidden all-one Walsh mode")
        elif len(possible) == 1:
            parity = next(iter(possible))
            need(re + (-1)**parity * im == 0, "one-dimensional Walsh phase line")


def encoded(value, rank):
    literal, _ = literal_and_numerator(value, rank)
    first, second = walsh(literal, rank), walsh(value, rank)
    output = []
    for mode in range(1 << rank):
        re, im = second[2*mode:2*mode+2]
        for _ in range(mode.bit_count() % 4):
            re, im = -im, re
        output.extend([first[2*mode]-re, first[2*mode+1]-im])
    return output


def bank_bounds(rank):
    size = 1 << rank
    encoded_bits = sum(len(phases(mode, rank)) *
                       (1+((size//2)*(rank-mode.bit_count())).bit_length())
                       for mode in range(size))
    full_radius = (size//2)*sum(1 << (k//2) for k in range(rank))
    return {"encoded_bank_bits": encoded_bits,
            "full_defect_uniform_radius": full_radius,
            "full_defect_uniform_bank_bits": (2*size)*(1+full_radius.bit_length()),
            "walsh_real_additions": 2*size*rank}


def add_independent(value, basis):
    remainder = [x % PRIME for x in value]
    for pivot, row in basis:
        multiplier = remainder[pivot]
        if multiplier:
            remainder = [(x-multiplier*y) % PRIME
                         for x, y in zip(remainder, row)]
    pivot = next((i for i, x in enumerate(remainder) if x), None)
    if pivot is None:
        return None
    inverse = pow(remainder[pivot], -1, PRIME)
    basis.append((pivot, [(x*inverse) % PRIME for x in remainder]))
    return pivot


def fibonacci(index):
    a, b = 0, 1
    for _ in range(index):
        a, b = b, a+b
    return a


def candidates(rank):
    dimension = 2 << rank
    for amplitude in (1, 2, 3, 4, 5, 7, 8, 15):
        for coordinate in range(dimension):
            value = [0]*dimension
            value[coordinate] = amplitude
            yield ["impulse", amplitude, coordinate], value
    # Fully specified 32-bit LCG, so witness input generation has no dependency
    # on the host library's random-number implementation.
    state = 291837 + rank
    for sample in range(500):
        value = []
        for _ in range(dimension):
            state = (1664525*state+1013904223) % (1 << 32)
            value.append(state % 17 - 8)
        yield ["signed_sample", 291837 + rank, sample], value


def check(rank):
    upper = (2 << rank) - fibonacci(rank+3)
    census = [sum(len(phases(mode, rank)) == k for mode in range(1 << rank))
              for k in range(3)]
    need(census == [1, fibonacci(rank+3)-2, (1 << rank)+1-fibonacci(rank+3)],
         "Fibonacci mode census")
    need(sum(k*census[k] for k in range(3)) == upper, "Fibonacci real dimension")
    basis, witnesses, witness_values = [], [], []
    candidate_count = 0
    for description, value in candidates(rank):
        candidate_count += 1
        output = defect(value, rank)
        check_annihilators(output, rank)
        code = encoded(value, rank)
        need(walsh(code, rank) == output, "integral encoded decoding identity")
        check_mode_annihilators(code, rank)
        for mode in range(1 << rank):
            bound = (1 << (rank-1))*(rank-mode.bit_count())
            need(all(abs(x) <= bound for x in code[2*mode:2*mode+2]),
                 "encoded mode component bound")
        need(max(map(abs, output), default=0) <= bank_bounds(rank)["full_defect_uniform_radius"],
             "full defect uniform component bound")
        pivot = add_independent(output, basis)
        if pivot is not None:
            witnesses.append([description, pivot])
            witness_values.append(value)
        if len(basis) == upper:
            break
    need(len(basis) == upper, "witnesses attain all-rank upper dimension")
    # Mutation controls: both a forbidden all-one mode and a forbidden
    # direction in the constant mode must be rejected by the checker.
    for mode, component in (((1 << rank)-1, 0), (0, 0)):
        mutation = [0]*(2 << rank)
        for address in range(1 << rank):
            mutation[2*address+component] = (-1)**((address & mode).bit_count())
        try:
            check_annihilators(mutation, rank)
        except ValueError:
            pass
        else:
            raise ValueError("annihilator mutation survived")
    need(defect([0]*(2 << rank), rank) == [0]*(2 << rank), "zero input defect")
    witness_hash = sha256(json.dumps(witness_values, separators=(",", ":")).encode()).hexdigest()
    return {"rank": rank, "mode_dimensions_0_1_2": census,
            "real_span_dimension": len(basis), "codimension": fibonacci(rank+3),
            "candidates_checked": candidate_count, "prime": PRIME,
            "witness_input_sha256": witness_hash, "witnesses_and_pivots": witnesses,
            **bank_bounds(rank)}


if __name__ == "__main__":
    # This is an arithmetic check, not a primality assumption in the proof.
    need(all(PRIME % divisor for divisor in range(2, int(PRIME**0.5)+1)),
         "trial-division modulus primality")
    for ar, ai, br, bi in product(range(-2, 3), repeat=4):
        q = (ai-bi) % 2 - (ar-br) % 2
        need(defect([ar, ai, br, bi], 1) == [q, -q, q, -q],
             "signed local floor error identity")
    results = [check(rank) for rank in range(1, 8)]
    if "--summary" in sys.argv:
        for result in results:
            result["last_witness_and_pivot"] = result["witnesses_and_pivots"][-1]
            del result["witnesses_and_pivots"]
    if "--json" in sys.argv or "--summary" in sys.argv:
        print(json.dumps(results, indent=2))
    else:
        print("PASS_INDEPENDENT_DEFECT_SPAN_RANKS_1_TO_7 " + str([r["real_span_dimension"] for r in results]))
