#!/usr/bin/env python3
"""Independent finite checks for the separated digit and raw-bit package."""

from collections import defaultdict
from itertools import combinations, combinations_with_replacement, product
import json
from math import comb


def pack(bits):
    return sum(bit << i for i, bit in enumerate(bits))


def binary_rank(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            low_bit = vector & -vector
            if low_bit not in pivots:
                pivots[low_bit] = vector
                break
            vector ^= pivots[low_bit]
    return len(pivots)


def operand_slots(length, opposite_length, order):
    slots = defaultdict(list)
    for indices in combinations(range(length), order):
        if indices[-1] - indices[0] < opposite_length:
            gaps = tuple(b - a for a, b in zip(indices, indices[1:]))
            slots[gaps].append((indices[0], pack(i in indices for i in range(length))))
    return slots


def separated_planes():
    domains = pairs_by_digit = digit_checks = ranks = 0
    for m, n, j in product(range(6), range(6), range(4)):
        domains += 1
        order = 1 << j
        left_slots = operand_slots(m, n, order)
        right_slots = operand_slots(n, m, order)
        width = sum(min(len(left), len(right_slots[gaps[::-1]]))
                    for gaps, left in left_slots.items())
        assert width == comb(min(m, n), order), (m, n, j, width)

        position_count = m + n - 1 if m and n else 0
        spectra = [[] for _ in range(position_count)]
        for gaps, left in left_slots.items():
            for (a_start, a_mask), (b_start, b_mask) in product(left, right_slots[gaps[::-1]]):
                spectra[a_start + b_start + sum(gaps)].append((a_mask, b_mask))

        left_columns_for_rank = []
        right_columns_for_rank = []
        for k, terms in enumerate(spectra):
            diagonals = [(i, k - i) for i in range(m) if 0 <= k - i < n]
            matrix = []
            for a in range(1 << m):
                row = []
                a_terms = [b_mask for a_mask, b_mask in terms if a & a_mask == a_mask]
                y_mask = pack(any((a >> i) & 1 and h == y for i, h in diagonals)
                              for y in range(n))
                for b in range(1 << n):
                    want = ((y_mask & b).bit_count() >> j) & 1
                    got = sum(b & b_mask == b_mask for b_mask in a_terms) & 1
                    assert want == got, (m, n, j, k, a, b)
                    row.append(want)
                    digit_checks += 1
                matrix.append(row)
            assert binary_rank(map(pack, matrix)) == comb(len(diagonals), order)
            left_columns_for_rank.extend(map(pack, zip(*matrix)))
            right_columns_for_rank.extend(map(pack, matrix))
            ranks += 1
        assert binary_rank(left_columns_for_rank) == sum(map(len, left_slots.values()))
        assert binary_rank(right_columns_for_rank) == sum(map(len, right_slots.values()))
        pairs_by_digit += 1 << (m + n)

    return {"domains": domains, "pairs_by_digit": pairs_by_digit,
            "digit_checks": digit_checks, "output_ranks": ranks,
            "pooled_operand_ranks": 2 * domains}


def product_bit_table(domain, width):
    shift = width - 1
    return [pack(((a * b) >> shift) & 1 for b in domain) for a in domain]


def raw_ranks():
    result = []
    for m in range(1, 11):
        unsigned = list(range(1 << m))
        signed = [r if r < (1 << (m - 1)) else r - (1 << m) for r in unsigned]
        rows = product_bit_table(unsigned, m)
        rank = binary_rank(rows)
        assert rows == product_bit_table(signed, m)
        assert rank == (1 if m == 1 else (1 << (m - 1)) // 3 + 3 * m // 2 - 1)

        odd = unsigned[1::2]
        odd_rows = product_bit_table(odd, m)
        odd_rank = binary_rank(odd_rows)
        complement = (1 << len(odd)) - 1
        odd_affine_rank = binary_rank(row ^ complement for row in odd_rows)
        assert odd_rank == (m if m < 3 else (1 << (m - 3)) + 1)
        # The odd matrix at m=1 consists of the single entry 1.
        assert odd_affine_rank == (0 if m == 1 else odd_rank)
        result.append({"m": m, "full_rank": rank, "odd_rank": odd_rank,
                       "odd_affine_offset_rank": odd_affine_rank})
    return result


def encoded_residue(word):
    x1, x2, x3, x4 = ((word >> i) & 1 for i in range(1, 5))
    p = x2 ^ x3
    a = p ^ x4
    b = x1 ^ x4 ^ (x1 & a) ^ (x2 & (x3 ^ x4))
    c = x1 ^ x3 ^ (x4 & p)
    return pack((1, a, b, c))


def schoolbook_mask(a, b):
    return pack(sum(((a >> i) & (b >> (k - i)) & 1)
                    for i in range(4) if 0 <= k - i < 4) & 1
                for k in range(7))


def decode(z):
    z1, z2, z3, z4, z5, z6 = ((z >> i) & 1 for i in range(1, 7))
    return (z2 ^ z3 ^ z4 ^ z5 ^ z6
            ^ (z3 & (z1 ^ z4 ^ z5 ^ z6)) ^ (z4 & z5)
            ^ (z6 & (z1 ^ z2 ^ z5)))


def independently_scheduled_decoder(z):
    z1, z2, z3, z4, z5, z6 = ((z >> i) & 1 for i in range(1, 7))
    a = z1 ^ z5
    b = z4 ^ z6
    c = z2 ^ z3
    return c ^ b ^ z5 ^ (z3 & (a ^ b)) ^ (z4 & z5) ^ (z6 & (a ^ z2))


def at_most_two_and_controls(received):
    """Enumerate actual functions of the received wires, with no quotient reduction."""
    words = sorted(received)
    target = pack(received[z] for z in words)
    one = (1 << len(words)) - 1
    columns = [pack((z >> j) & 1 for z in words) for j in range(1, 7)]
    affine_set = {0, one}
    for column in columns:
        affine_set |= {v ^ column for v in affine_set}
    affine = tuple(sorted(affine_set))
    first_functions = {a & b for a, b in combinations_with_replacement(affine, 2)}
    represent_final = {target ^ a for a in affine}
    assert 0 not in represent_final
    assert first_functions.isdisjoint(represent_final)
    second_checks = 0
    for first in sorted(first_functions):
        # Either or both factors may include the first gate. The final XOR
        # can include either gate with either coefficient.
        second_inputs = affine_set | {a ^ first for a in affine}
        finals = represent_final | {a ^ first for a in represent_final}
        for a, b in combinations_with_replacement(second_inputs, 2):
            assert a & b not in finals, (first, a, b)
            second_checks += 1
    return {"affine_forms": len(affine), "first_gate_functions": len(first_functions),
            "second_gate_factor_pairs": second_checks, "minimum_ANDs": 3}


def odd_five_bit():
    masks = (1, 3, 5, 15, 7, 9, 11, 13)
    classes = {(-1)**s * pow(5, t, 32) % 32: (t + 4 * s) % 8
               for s, t in product(range(2), range(8))}
    domain = tuple(range(1, 32, 2))
    assert sorted(classes) == list(domain)
    by_received_word = {}
    input_pairs_received = {}
    for x, y in product(domain, repeat=2):
        a = masks[classes[x]]
        b = masks[classes[y]]
        assert a == encoded_residue(x) and b == encoded_residue(y)
        z = schoolbook_mask(a, b)
        wanted = (x * y >> 4) & 1
        assert decode(z) == independently_scheduled_decoder(z) == wanted
        assert by_received_word.setdefault(z, wanted) == wanted
        input_pairs_received[x, y] = z

    matrix_rows = product_bit_table(domain, 5)
    all_ones = (1 << len(domain)) - 1
    assert binary_rank(matrix_rows) == binary_rank(row ^ all_ones for row in matrix_rows) == 5
    assert len(set(matrix_rows)) == 8 and all(row not in (0, all_ones) for row in matrix_rows)
    anchored = [row ^ matrix_rows[0] ^ (all_ones if row & 1 else 0) for row in matrix_rows]
    assert binary_rank(anchored) == 3

    assert input_pairs_received[1, 1] == input_pairs_received[15, 1]
    assert input_pairs_received[1, 25] == input_pairs_received[5, 5]
    assert schoolbook_mask(3, 3) == schoolbook_mask(1, 5) == 5
    assert (3 * 3 >> 2) & 1 != (1 * 5 >> 2) & 1
    assert 3 * 3 == 1 * 9
    assert len(by_received_word) == 30
    return {"pairs": len(domain)**2, "distinct_returns": len(by_received_word),
            "distinct_matrix_rows": len(set(matrix_rows)), "constant_target_rows": 0,
            "minimum_widths_with_no_side_output": [4, 4],
            "minimum_pure_affine_widths": [5, 5], "additive_side_mixed_difference_rank": 3,
            "fixed_encoding_AND_minimum": at_most_two_and_controls(by_received_word)}


def main():
    print(json.dumps({"status": "passed", "separated_planes": separated_planes(),
                      "raw_ranks": raw_ranks(), "odd_five_bit": odd_five_bit()},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
