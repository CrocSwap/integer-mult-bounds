"""Independent finite checks of the formal interface's actual hypotheses.

This is not a substitute for Lean's universal proof. Standard library only.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from itertools import product


def require(ok, message):
    if not ok:
        raise ValueError(message)


def binary_rank(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def gf4_mul(a, b):
    # F2[x]/(x^2+x+1), represented by the two coefficient bits.
    result = 0
    for _ in range(2):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return result


def rank_two_by_three(rows, multiply):
    left, right = rows
    if not any(left):
        return int(any(right))
    if not any(right):
        return 1
    pivot = next(i for i, x in enumerate(left) if x)
    inverse = next(i for i in range(1, 4) if multiply(left[pivot], i) == 1)
    factor = multiply(right[pivot], inverse)
    return 1 if all(y == multiply(factor, x) for x, y in zip(left, right)) else 2


def prime_rank(rows, prime):
    rows = [list(row) for row in rows]
    pivot = 0
    for col in range(len(rows[0])):
        source = next((i for i in range(pivot, len(rows)) if rows[i][col] % prime), None)
        if source is None:
            continue
        rows[pivot], rows[source] = rows[source], rows[pivot]
        inverse = pow(rows[pivot][col], -1, prime)
        rows[pivot] = [x * inverse % prime for x in rows[pivot]]
        for i in range(pivot + 1, len(rows)):
            factor = rows[i][col]
            rows[i] = [(x - factor * y) % prime for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def replay():
    mul = [[gf4_mul(a, b) for b in range(4)] for a in range(4)]
    require(all(mul[a][b] == mul[b][a] for a in range(4) for b in range(4)), "GF4 commutative")
    require(all(mul[mul[a][b]][c] == mul[a][mul[b][c]] and
                mul[a][b ^ c] == mul[a][b] ^ mul[a][c]
                for a, b, c in product(range(4), repeat=3)), "GF4 field laws")
    require(all(any(mul[a][b] == 1 for b in range(1, 4)) for a in range(1, 4)), "GF4 inverses")
    require(all(mul[a][b] == (a * b) % 2 and a ^ b == (a + b) % 2
                for a, b in product(range(2), repeat=2)), "binary field embedding")
    vectors2 = list(product(range(2), repeat=5))
    vectors4 = list(product(range(4), repeat=5))
    histograms = {"binary_two_terms": Counter(), "gf4_one_term": Counter(),
                  "gf4_two_terms_one_fixed": Counter()}
    def support(weights):
        return sum(bool(x) << j for j, x in enumerate(weights[:2])), \
            sum(bool(x) << j for j, x in enumerate(weights[2:]))

    for bits in range(64):
        B = [[(bits >> (3 * i + j)) & 1 for j in range(3)] for i in range(2)]
        block = {(s, u): binary_rank([sum(B[i][j] << j for j in range(3) if u >> j & 1)
                                     for i in range(2) if s >> i & 1])
                 for s in range(4) for u in range(8)}
        for first, second in product(vectors2, repeat=2):
            n = [[B[i][j] & ((first[i] & first[2 + j]) ^
                            (second[i] & second[2 + j])) for j in range(3)] for i in range(2)]
            rank = binary_rank([sum(x << j for j, x in enumerate(row)) for row in n])
            cost = block[support(first)] + block[support(second)]
            require(rank <= cost <= 2 * block[3, 7], "binary rank-to-cost bound")
            histograms["binary_two_terms"][rank, cost] += 1
        for weights in vectors4:
            n = [[mul[weights[i]][weights[2 + j]] if B[i][j] else 0 for j in range(3)] for i in range(2)]
            rank = rank_two_by_three(n, gf4_mul)
            cost = block[support(weights)]
            require(rank == cost, "invertible supported scalings preserve binary block rank")
            histograms["gf4_one_term"][rank, cost] += 1
            # Add the nonzero all-ones term. This genuinely tests rank of a
            # sum over the extension, including cancellation between terms.
            total = [[n[i][j] ^ B[i][j] for j in range(3)] for i in range(2)]
            rank = rank_two_by_three(total, gf4_mul)
            cost += block[3, 7]
            require(rank <= cost <= 2 * block[3, 7], "GF4 two-term bound")
            histograms["gf4_two_terms_one_fixed"][rank, cost] += 1
    counterexample = [[1, 1, 0], [1, 0, 1], [0, 1, 1]]
    changed_characteristic = [prime_rank(counterexample, 2), prime_rank(counterexample, 3)]
    require(changed_characteristic == [2, 3],
            "entrywise change of characteristic is not field extension")
    # Actual 1-by-1 calculations behind the three Lean counterexamples.
    unit_rank = binary_rank([1])
    missing_left = [unit_rank, binary_rank([])]
    missing_right = [unit_rank, binary_rank([0])]
    zero_minor = [1, binary_rank([0])]
    require(all(size > cost for size, cost in (missing_left, missing_right, zero_minor)),
            "support/minor hypotheses cannot be omitted")
    return {"schema": "decoder-rank-interface-finite/1",
            "cases_per_family": {k: sum(v.values()) for k, v in histograms.items()},
            "rank_cost_histograms": {k: {str(a) + "," + str(b): count
                                          for (a, b), count in sorted(v.items())}
                                      for k, v in histograms.items()},
            "wrong_characteristic_ranks": changed_characteristic,
            "missing_left_support_rank_cost": missing_left,
            "missing_right_support_rank_cost": missing_right,
            "zero_minor_size_cost": zero_minor,
            "scope": "Finite hypothesis checks only; no universal proof or Lean execution inferred."}


if __name__ == "__main__":
    import json
    print(json.dumps(replay(), indent=2, sort_keys=True))
