#!/usr/bin/env python3
"""Check the all-n one-clean theorem without executing predecessor code.

Produced by Nick Petalas. Apache-2.0.
"""

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIMIT = 256
CAP = 10


def require(condition, message):
    if not condition:
        raise ValueError(message)


def positive_integer(n):
    require(type(n) is int and 1 <= n < (1 << 1024), "invalid factor count")


def dirty(n):
    positive_integer(n)
    p = 1 << (n.bit_length() - 1)
    return p * (3 * n - 2 * p)


def optimum(n):
    positive_integer(n)
    if n <= 2:
        return 2 * n - 1
    q = 1 << ((n // 3).bit_length() - 1)
    require(3 * q <= n < 6 * q, "wrong dyadic interval")
    return 6 * q * (n - 2 * q)


def root_split(n):
    require(type(n) is int and 2 <= n <= LIMIT, "invalid emitted size")
    if n == 2:
        return 1
    q = 1 << ((n // 3).bit_length() - 1)
    return min(2 * q, n - 2 * q)


def minima(values):
    return min(values) if values else None


def dynamic_program():
    """Exhaust every split and clean/dirty root, with exact scratch caps."""
    ds = [[None] * (LIMIT + 1) for _ in range(CAP + 1)]
    cs = [[None] * (LIMIT + 1) for _ in range(CAP + 1)]
    ds[0][1] = 1
    for s in range(1, CAP + 1):
        ds[s][1] = cs[s][1] = 1
        for n in range(2, min(LIMIT, 1 << s) + 1):
            dv, cv = [], []
            for k in range(1, n):
                a, b = ds[s - 1][k], ds[s - 1][n - k]
                if a is not None and b is not None:
                    dv.append(2 * a + 2 * b)
                    cv.append(2 * a + b)
                a, b = cs[s - 1][k], cs[s - 1][n - k]
                if s >= 2 and a is not None and b is not None:
                    cv.append(2 * a + 2 * b)
            ds[s][n], cs[s][n] = minima(dv), minima(cv)
    return ds, cs


def check_recurrences():
    ds, cs = dynamic_program()
    admitted, excluded = 0, 0
    for s in range(1, CAP + 1):
        for n in range(1, LIMIT + 1):
            if n <= 1 << s:
                require(ds[s][n] == dirty(n), "all-dirty minimum mismatch")
                require(cs[s][n] == optimum(n), "one-clean minimum mismatch")
                admitted += 1
            else:
                require(ds[s][n] is None and cs[s][n] is None, "capacity leak")
                excluded += 1
    splits = 0
    for n in range(2, LIMIT + 1):
        for k in range(1, n):
            require(2 * dirty(k) + dirty(n - k) >= optimum(n), "clean-root bound")
            require(2 * optimum(k) + 2 * optimum(n - k) >= optimum(n),
                    "dirty-root bound")
            splits += 1
        k = root_split(n)
        require(2 * dirty(k) + dirty(n - k) == optimum(n), "unattained optimum")
        require(max(k, n - k) <= 1 << ((n - 1).bit_length() - 1),
                "attainer exceeds minimum scratch cap")
    return {"admitted_n_cap_pairs": admitted, "excluded_n_cap_pairs": excluded,
            "all_root_splits": splits}


def check_large_identities():
    cases = 0
    for h in range(1, 257):
        q = 1 << h
        for n in (3 * q - 1, 3 * q, 3 * q + 1, 4 * q, 6 * q - 1):
            require(optimum(2 * n) == 4 * optimum(n), "scaling identity")
            m = n // 2
            require(optimum(n) == 2 * optimum(m) + 2 * optimum(n - m),
                    "balanced dirty-root identity")
            require(optimum(n + 1) - optimum(n) >= optimum(n) - optimum(n - 1),
                    "convexity identity")
            cases += 1
    return cases


def emit(n):
    """Emit a clean root and balanced dirty children using an explicit stack."""
    require(type(n) is int and 2 <= n <= LIMIT, "invalid emitted size")
    s = (n - 1).bit_length()
    # Tasks are (first factor, count, source, target, available roles, sign, clean).
    stack = [(0, n, 0, 1, tuple(range(2, s + 2)), 1, True)]
    word = []
    for _ in range(2 * optimum(n)):
        if not stack:
            require(len(word) == optimum(n), "wrong emitted call count")
            return word, s + 2
        first, size, source, target, pool, sign, clean = stack.pop()
        if size == 1:
            word.append((first, source, target, sign))
            continue
        require(bool(pool), "emitter exhausted scratch")
        connector, rest = pool[0], pool[1:]
        k = root_split(size) if clean else size // 2
        left = (first, k, source, connector, rest)
        right = (first + k, size - k, connector, target, rest)
        calls = [(left, 1), (right, 1), (left, -1)]
        if not clean:
            calls.append((right, -1))
        if sign == -1:
            calls = [(task, -direction) for task, direction in reversed(calls)]
        stack.extend((*task, direction, False) for task, direction in reversed(calls))
    raise ValueError("emitter exceeded its node bound")


def factor(j):
    # The two orientations fail to commute, so order errors are observable.
    a = j % 3 + 1
    return ((1, a), (0, 1)) if j % 2 == 0 else ((1, 0), (a, 1))


def multiply(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2))
                       for j in range(2)) for i in range(2))


def initial_state(roles, clean=True):
    width = 2 * roles
    state = [[[int(j == 2 * r + i) for j in range(width)]
              for i in range(2)] for r in range(roles)]
    if clean:
        state[2] = [[0] * width for _ in range(2)]
    return state


def execute(word, roles, clean=True):
    require(3 <= roles <= CAP + 2, "invalid register inventory")
    state = initial_state(roles, clean)
    require(len(word) <= 2 * optimum(LIMIT), "word too long")
    for j, source, target, sign in word:
        require(0 <= j < LIMIT and 0 <= source < roles and 0 <= target < roles,
                "invalid instruction index")
        require(source != target and sign in (-1, 1), "invalid instruction alias/sign")
        a = factor(j)
        original = state[source]
        state[target] = [[x + sign * sum(a[i][k] * original[k][col] for k in range(2))
                          for col, x in enumerate(state[target][i])] for i in range(2)]
    return state


def endpoint(word, n, roles, sign=1, clean=True):
    state = execute(word, roles, clean)
    expected = initial_state(roles, clean)
    product = ((1, 0), (0, 1))
    for j in range(n):
        product = multiply(factor(j), product)
    for i in range(2):
        for j in range(2):
            expected[1][i][j] += sign * product[i][j]
    return state == expected


def expect_rejection(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise ValueError("invalid input was accepted")


def check_words():
    calls, runs = 0, 0
    sizes = list(range(2, 33)) + [54, 63, 128]
    for n in sizes:
        word, roles = emit(n)
        inverse = [(j, source, target, -sign)
                   for j, source, target, sign in reversed(word)]
        require(endpoint(word, n, roles), "forward endpoint/restoration failure")
        require(endpoint(inverse, n, roles, -1), "inverse endpoint/restoration failure")
        require(execute(word + inverse, roles) == initial_state(roles), "literal inverse")
        calls += len(word)
        runs += 3
    word, roles = emit(6)
    require(not endpoint(word[:-1], 6, roles), "omitted cleanup escaped")
    require(not endpoint(word, 6, roles, clean=False), "dirty clean-slot escaped")
    wrong = [(5 - j, source, target, sign) for j, source, target, sign in word]
    require(not endpoint(wrong, 6, roles), "factor reversal escaped")
    wrong = list(word)
    j, source, target, sign = wrong[0]
    wrong[0] = (j, source, target, -sign)
    require(not endpoint(wrong, 6, roles), "sign corruption escaped")
    expect_rejection(execute, [(0, 0, 0, 1)], 4)
    for n in (0, -1, True, 1.5, 1 << 1024):
        expect_rejection(optimum, n)
    return {"factor_counts": sizes, "basis_word_runs": runs,
            "forward_calls_enumerated": calls, "controls": 10}


def receipt():
    result = {"schema": "one-clean-unit-optimum/1", "claim_type": "scoped proof",
              "recurrences": check_recurrences(),
              "large_identity_cases": check_large_identities(), "words": check_words(),
              "examples": {str(n): optimum(n) for n in (2, 3, 4, 50, 54, 63, 128, 256)}}
    result["source_sha256"] = {
        name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        for name in ("verify.py", "PROOF.md", "README.md", "TASK.json", "SOURCES.json", "VERIFY.json")}
    return result


def main():
    require(len(sys.argv) == 1, "this verifier takes no arguments")
    print(json.dumps(receipt(), indent=2, sort_keys=True))
    print("PASS_ONE_CLEAN_UNIT_OPTIMUM")


if __name__ == "__main__":
    main()
