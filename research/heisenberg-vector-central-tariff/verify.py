#!/usr/bin/env python3
"""Exact corroboration of the vector-label central tariff; stdlib only."""

import argparse
import hashlib
import itertools
import json
from collections import deque
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def outer(u, v, m, n):
    return sum(((u >> i) & 1) * ((v >> j) & 1) << (i * n + j)
               for i in range(m) for j in range(n))


def multiply(a, b, m, n):
    u, v, z = a
    p, q, w = b
    return u ^ p, v ^ q, z ^ w ^ outer(u, q, m, n)


def decompose(z, m, n):
    """Row-pivot elimination as a sum of independent rank-one matrices."""
    require(1 <= m <= 4 and 1 <= n <= 4, "matrix dimensions out of bounds")
    require(0 <= z < (1 << (m * n)), "matrix bits out of bounds")
    residual = z
    terms = []
    for _ in range(min(m, n)):
        if not residual:
            break
        pivot = next(i for i in range(m) if (residual >> (i * n)) & ((1 << n) - 1))
        v = (residual >> (pivot * n)) & ((1 << n) - 1)
        column = (v & -v).bit_length() - 1
        u = sum(((residual >> (i * n + column)) & 1) << i for i in range(m))
        terms.append((u, v))
        residual ^= outer(u, v, m, n)
    require(residual == 0, "rank decomposition incomplete")
    return terms


def minor_rank(z, m, n):
    """Independent rank oracle: largest nonsingular binary minor."""
    for k in range(min(m, n), 0, -1):
        for rows in itertools.combinations(range(m), k):
            for cols in itertools.combinations(range(n), k):
                determinant = 0
                for permutation in itertools.permutations(range(k)):
                    product = 1
                    for i in range(k):
                        product &= (z >> (rows[i] * n + cols[permutation[i]])) & 1
                    determinant ^= product
                if determinant:
                    return k
    return 0


def central_word(z, m, n):
    terms = decompose(z, m, n)
    if not terms:
        return []
    word = []
    previous = 0
    total_v = 0
    for u, v in terms:
        word.extend([(u ^ previous, 0, 0), (0, v, 0)])
        previous = u
        total_v ^= v
    word.extend([(previous, 0, 0), (0, total_v, 0)])
    require(all(u or v for u, v, _ in word), "zero vector in constructed word")
    return word


def endpoint(word, m, n):
    state = (0, 0, 0)
    for label in word:
        state = multiply(state, label, m, n)
    return state


def scalar_distances(m, n):
    """Complete one-role Cayley BFS, including all central targets."""
    generators = [(u, 0, 0) for u in range(1, 1 << m)]
    generators += [(0, v, 0) for v in range(1, 1 << n)]
    capacity = 1 << (m + n + m * n)
    distances = {(0, 0, 0): 0}
    queue = deque([(0, 0, 0)])
    for _ in range(capacity):
        if not queue:
            break
        state = queue.popleft()
        for label in generators:
            image = multiply(state, label, m, n)
            if image not in distances:
                distances[image] = distances[state] + 1
                queue.append(image)
    require(not queue and len(distances) == capacity, "incomplete Cayley BFS")
    return distances


def matrix_census():
    cases = 0
    states = 0
    ranks = {}
    for m, n in itertools.product(range(1, 4), repeat=2):
        distances = scalar_distances(m, n)
        states += len(distances)
        for z in range(1 << (m * n)):
            k = minor_rank(z, m, n)
            require(len(decompose(z, m, n)) == k, "rank oracles disagree")
            word = central_word(z, m, n)
            require(endpoint(word, m, n) == (0, 0, z), "wrong central endpoint")
            tariff = 2 * (k + 1) if z else 0
            require(len(word) == tariff, "wrong construction length")
            require(distances[(0, 0, z)] == tariff, "Cayley minimum differs")
            cases += 1
            ranks[k] = ranks.get(k, 0) + 1
    return {"central_matrices": cases, "cayley_states": states, "rank_counts": ranks}


def group_index(g, m, n):
    u, v, z = g
    return u | (v << m) | (z << (m + n))


def group_element(index, m, n):
    return index & ((1 << m) - 1), (index >> m) & ((1 << n) - 1), index >> (m + n)


def translate(bits, label, m, n, left):
    result = 0
    for _ in range(1 << (m + n + m * n)):
        if not bits:
            break
        low = bits & -bits
        g = group_element(low.bit_length() - 1, m, n)
        h = multiply(label, g, m, n) if left else multiply(g, label, m, n)
        result ^= 1 << group_index(h, m, n)
        bits ^= low
    require(bits == 0, "group support exceeded capacity")
    return result


def formal_call(state, label, a, b, r, m, n):
    """Right multiply the full formal matrix by I+([label]+1)ab^T."""
    result = list(state)
    for i in range(r):
        column = 0
        for j in range(r):
            if (a >> j) & 1:
                column ^= state[i * r + j]
        delta = column ^ translate(column, label, m, n, False)
        for j in range(r):
            if (b >> j) & 1:
                result[i * r + j] ^= delta
    return tuple(result)


def identity(r):
    return tuple(int(i == j) for i in range(r) for j in range(r))


def formal_word(words, r, m, n):
    state = identity(r)
    for t, word in enumerate(words):
        for label in word:
            state = formal_call(state, label, 1 << t, 1 << t, r, m, n)
    return state


def formal_target(targets, r, m, n):
    return tuple((1 << group_index((0, 0, targets[i]), m, n) if i < len(targets) else 1)
                 if i == j else 0 for i in range(r) for j in range(r))


def formal_fixtures():
    count = 0
    omissions = 0
    for m, n in [(2, 2), (2, 3), (3, 2), (3, 3), (4, 4)]:
        full = sum(1 << (i * n + i) for i in range(min(m, n)))
        targets = [full, 1, 0]
        words = [central_word(z, m, n) for z in targets]
        expected = formal_target(targets, 4, m, n)
        require(formal_word(words, 4, m, n) == expected, "dirty endpoint mismatch")
        count += 1
        for t, word in enumerate(words):
            for j in range(len(word)):
                changed = list(words)
                changed[t] = word[:j] + word[j + 1:]
                require(formal_word(changed, 4, m, n) != expected, "omission escaped")
                omissions += 1
    return {"formal_dirty_fixtures": count, "omission_rejections": omissions}


def mixed_short_word_exclusion():
    """All normalized two-role words of length <=5, for rank-two Z=I2."""
    m = n = r = 2
    labels = [(u, 0, 0) for u in range(1, 4)] + [(0, v, 0) for v in range(1, 4)]
    generators = list(itertools.product(labels, range(1, 4), range(1, 4)))
    base = identity(r)
    balls = {base: 0}
    frontier = [base]
    layers = [1]
    ball2 = None
    for depth in range(1, 4):
        next_frontier = []
        for state in frontier:
            for label, a, b in generators:
                image = formal_call(state, label, a, b, r, m, n)
                if image not in balls:
                    balls[image] = depth
                    next_frontier.append(image)
        frontier = next_frontier
        layers.append(len(frontier))
        if depth == 2:
            ball2 = tuple(balls)
    require(ball2 is not None, "missing short ball")
    z = 1 | (1 << 3)
    target = formal_target([z], r, m, n)
    hits = 0
    for state in ball2:
        image = tuple(translate(bits, (0, 0, z), m, n, True) if i < r else bits
                      for i, bits in enumerate(state))
        hits += int(image in balls)
    require(hits == 0, "short dirty-workspace saving found")
    word = central_word(z, m, n)
    require(len(word) == 6 and formal_word([word], r, m, n) == target, "six-call witness failed")
    suffix = identity(r)
    for label in reversed(word[3:]):
        suffix = formal_call(suffix, label, 1, 1, r, m, n)
    joined = tuple(translate(bits, (0, 0, z), m, n, True) if i < r else bits
                   for i, bits in enumerate(suffix))
    require(joined == formal_word([word[:3]], r, m, n), "join adapter is wrong")
    require(suffix in balls and joined in balls, "positive 3+3 join missing")
    return {"mixed_generators": len(generators), "mixed_ball_layers": layers,
            "mixed_join_queries": len(ball2), "mixed_short_hits": hits,
            "mixed_minimum": 6, "mixed_positive_join": True}


def controls():
    rejected = 0
    for args in [(1, 0, 2), (1, 2, 5), (16, 2, 2), (-1, 2, 2)]:
        try:
            decompose(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid matrix accepted")
    word = central_word(9, 2, 2)
    require(endpoint(list(reversed(word)), 2, 2) == (0, 0, 9), "reverse control failed")
    require(endpoint(sorted(word), 2, 2) != (0, 0, 9), "chronology control failed")
    require(len(word) == 6 and len(word) < 4 * minor_rank(9, 2, 2), "changed-alphabet gain missing")
    return {"invalid_inputs_rejected": rejected, "chronology_controls": 2,
            "rank_two_cost": len(word), "separate_rank_one_commutators": 8}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-mixed", action="store_true", help="omit the finite dirty-workspace search")
    args = parser.parse_args()
    result = {"claim_type": "scoped proof with finite corroboration", "no_new_kappa": True}
    result.update(matrix_census())
    result.update(formal_fixtures())
    result.update(controls())
    if not args.skip_mixed:
        result.update(mixed_short_word_exclusion())
    package = Path(__file__).resolve().parent
    result["source_sha256"] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                               for name in ["verify.py", "PROOF.md"]}
    print(json.dumps(result, sort_keys=True))
    print("PASS_HEISENBERG_VECTOR_CENTRAL_TARIFF")


if __name__ == "__main__":
    main()
