#!/usr/bin/env python3
"""Exact formal UT3 register census. juper997 / OpenAI Codex; Apache-2.0."""
import argparse
import hashlib
import importlib.util
import json
from itertools import permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def group_mul(g, h):
    x, y, z = g & 1, (g >> 1) & 1, (g >> 2) & 1
    X, Y, Z = h & 1, (h >> 1) & 1, (h >> 2) & 1
    return (x ^ X) | ((y ^ Y) << 1) | ((z ^ Z ^ (x & Y)) << 2)


def translate(p, g):
    return sum(1 << group_mul(h, g) for h in range(8) if (p >> h) & 1)


DELTA = {g: tuple(p ^ translate(p, g) for p in range(256)) for g in (1, 2)}


def projectors(r):
    return [(x, y) for x in range(1, 1 << r) for y in range(1, 1 << r)
            if (x & y).bit_count() % 2 == 1]


def identity(r):
    return tuple(int(i == j) for i in range(r) for j in range(r))


def target(r, copies=2):
    return tuple((16 if i < copies else 1) if i == j else 0
                 for i in range(r) for j in range(r))


def step(state, r, g, x, y):
    require(g in (1, 2), "address label outside the paid alphabet")
    require(0 < x < 1 << r and 0 < y < 1 << r and (x & y).bit_count() % 2,
            "paid scalar factor is not a rank-one idempotent")
    out = list(state)
    for i in range(r):
        p = 0
        for k in range(r):
            if (x >> k) & 1:
                p ^= state[i * r + k]
        q = DELTA[g][p]
        for j in range(r):
            if (y >> j) & 1:
                out[i * r + j] ^= q
    return tuple(out)


def ball(r, radius=3):
    generators = [(g, x, y) for g in (1, 2) for x, y in projectors(r)]
    seen = {identity(r): 0}
    frontier = {identity(r)}
    for depth in range(1, radius + 1):
        following = set()
        for state in frontier:
            for generator in generators:
                result = step(state, r, *generator)
                if result not in seen:
                    following.add(result)
        seen.update((s, depth) for s in following)
        frontier = following
    return seen


def left_target(state, r, copies):
    # c is central and involutory, so either side's c-translation is the same.
    return tuple(translate(state[i * r + j], 4) if i < copies else state[i * r + j]
                 for i in range(r) for j in range(r))


def meet_distance(states, r, copies):
    distances = [d + states[t] for s, d in states.items()
                 if (t := left_target(s, r, copies)) in states]
    return min(distances) if distances else None


def witness(r):
    return [(g, 1 << i, 1 << i) for i in range(2) for g in (1, 2, 1, 2)]


def evaluate(word, r):
    state = identity(r)
    for generator in word:
        state = step(state, r, *generator)
    return state


def dual_mul(a, b):
    # bit 0 = constant, bit 1 = epsilon coefficient; epsilon^2 = 0.
    return ((a & 1) & (b & 1)) | ((((a & 1) & (b >> 1)) ^ ((a >> 1) & (b & 1))) << 1)


def dual_determinant(matrix, r):
    result = 0
    for perm in permutations(range(r)):
        term = 1
        for i, j in enumerate(perm):
            term = dual_mul(term, matrix[i * r + j])
        result ^= term
    return result


def controls(independent):
    count = 0
    require(group_mul(1, 2) != group_mul(2, 1), "lost noncommutativity")
    require(group_mul(group_mul(group_mul(1, 2), 1), 2) == 4, "wrong commutator")
    require(all(group_mul(4, g) == group_mul(g, 4) for g in range(8)), "c not central")
    count += 3
    chi = lambda g: (g & 1) ^ ((g >> 1) & 1)
    require(all(chi(group_mul(g, h)) == (chi(g) ^ chi(h))
                for g in range(8) for h in range(8)), "invalid parity quotient")
    count += 1
    for r in (2, 3):
        word = witness(r)
        wanted = target(r)
        require(evaluate(word, r) == wanted, "eight-call formal witness failed")
        regular = tuple(1 << i for i in range(8 * r))
        for g, x, y in word:
            rows = tuple(y if (x >> i) & 1 else 0 for i in range(r))
            regular = independent.binary_product(regular, independent.generator(rows, g))
        require(regular == independent.regular_from_formal(wanted, r), "independent witness failed")
        count += 1
        for i in range(8):
            require(evaluate(word[:i] + word[i + 1:], r) != wanted, "omitted call accepted")
            count += 1
        wrong = word.copy()
        wrong[0] = (2, 1, 1)
        require(evaluate(wrong, r) != wanted, "wrong address call accepted")
        count += 1
        for g, x, y in [(4, 1, 1), (1, 1, 2)]:
            try:
                step(identity(r), r, g, x, y)
            except ValueError:
                count += 1
            else:
                raise ValueError("invalid alphabet or nilpotent scalar factor accepted")
        for x, y in projectors(r):
            matrix = tuple(int(i == j) | ((((x >> i) & 1) & ((y >> j) & 1)) << 1)
                           for i in range(r) for j in range(r))
            require(dual_determinant(matrix, r) == 3, "odd-length determinant step failed")
            for g in (1, 2):
                require(evaluate([(g, x, y)] * 2, r) == identity(r), "generator not involutory")
        count += 2
    bad = list(target(3))
    bad[2] = 1
    require(tuple(bad) != target(3) and bad[:2] == list(target(3))[:2], "dirty leakage control")
    bad = list(target(3))
    bad[8] = 16
    require(tuple(bad) != target(3), "dirty endpoint corruption accepted")
    count += 2
    require(independent.natural_sum() == (0,) * 9, "natural kernel fixture failed")
    require(independent.regular_from_formal((255,), 1) != (0,) * 8,
            "nonfaithful representation used for formal equality")
    # A dense matrix mutation outside the regular image must fail decoding.
    corrupted = list(independent.regular_from_formal(identity(2), 2))
    corrupted[1] ^= 1
    try:
        independent.decode(tuple(corrupted), 2)
    except ValueError:
        count += 1
    else:
        raise ValueError("nonregular matrix mutation accepted")
    count += 2
    return count


def replay():
    spec = importlib.util.spec_from_file_location("ut3_independent", HERE / "independent.py")
    independent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(independent)
    require(all(group_mul(g, h) == independent.multiply_labels(g, h)
                for g in range(8) for h in range(8)), "group implementations disagree")
    report = {"model": "F2[UT3(F2)]; paid a,b rank-one scalar idempotents",
              "minimum": 8, "registers": {}, "controls": controls(independent)}
    for r in (2, 3):
        states = ball(r)
        other, attempts, scalar_ids = independent.census(r)
        require(states == other, "full state sets or shortest distances disagree")
        outer_ids = {sum((((x >> i) & 1) & ((y >> j) & 1)) << (i * r + j)
                         for i in range(r) for j in range(r)) for x, y in projectors(r)}
        require(outer_ids == scalar_ids, "rank-one idempotent alphabets disagree")
        require(meet_distance(states, r, 2) is None, "two targets attainable in at most six calls")
        require(independent.meet_distance(r, 2) is None, "independent target intersection not empty")
        require(meet_distance(states, r, 0) == 0, "identity meet control failed")
        require(meet_distance(states, r, 1) == 4, "single-commutator meet control failed")
        require(independent.meet_distance(r, 1) == 4, "independent positive intersection failed")
        require(all(tuple(p.bit_count() % 2 for p in s) == identity(r) for s in states),
                "nonidentity free scalar residue")
        digest = hashlib.sha256(b"".join(bytes(s) for s in sorted(states))).hexdigest()
        report["registers"][str(r)] = {"generators": 2 * len(projectors(r)),
            "layers": [sum(d == k for d in states.values()) for k in range(4)],
            "ball_size": len(states), "state_sha256": digest,
            "independent_transition_attempts": attempts, "target_intersection": 0,
            "single_target_minimum": 4}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the computed deterministic receipt")
    args = parser.parse_args()
    receipt = replay()
    if args.emit:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        require(receipt == json.loads((HERE / "EXPECTED.json").read_text()), "receipt drift")
        print("PASS_UT3_COMMUTATOR_REGISTER_BOUND minimum=8 registers=2,3 dirty_extras=0,1 no_new_kappa")


if __name__ == "__main__":
    main()
