#!/usr/bin/env python3
"""Exact classical selector-memory certificates; standard library only."""

import hashlib
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def capacity(m):
    need(type(m) is int and 1 <= m <= 72, "dimension outside 1..72")
    return m * (m + 3) // 2


def edges(m):
    return tuple((i, j) for i in range(m) for j in range(i + 1, m))


def validate_state(m, state):
    bits = capacity(m)
    need(type(state) is int and 0 <= state < (1 << bits), "invalid state")


def update(m, state, column):
    """Read one n=m+1 bit column and retain only its quotient signature."""
    validate_state(m, state)
    need(type(column) is int and 0 <= column < (1 << (m + 1)), "invalid column")
    epsilon = column >> m
    y = (column & ((1 << m) - 1)) ^ (((1 << m) - 1) * epsilon)
    sign = 1 - 2 * epsilon
    answer = state & ~((1 << (2 * m)) - 1)
    for i in range(m):
        value = ((state >> (2 * i)) + sign * ((y >> i) & 1)) % 4
        answer |= value << (2 * i)
    for k, (i, j) in enumerate(edges(m)):
        if ((y >> i) & 1) and ((y >> j) & 1):
            answer ^= 1 << (2 * m + k)
    need(0 <= answer < (1 << capacity(m)), "state escaped its capacity")
    return answer


def canonical_word(m, state):
    """Represent every quotient state using exactly capacity(m) columns."""
    validate_state(m, state)
    word = []
    degrees = [0] * m
    for k, (i, j) in enumerate(edges(m)):
        if (state >> (2 * m + k)) & 1:
            word.append((1 << i) | (1 << j))
            degrees[i] += 1
            degrees[j] += 1
    complement = (1 << (m + 1)) - 1
    for i in range(m):
        residual = (((state >> (2 * i)) & 3) - degrees[i]) % 4
        if residual == 3:
            word.append(complement ^ (1 << i))
        else:
            word.extend([1 << i] * residual)
    need(len(word) <= capacity(m), "canonical word exceeds its bound")
    return tuple(word + [0] * (capacity(m) - len(word)))


def inverse_word(m, word):
    need(len(word) <= capacity(m), "word too long")
    complement = (1 << (m + 1)) - 1
    return tuple(complement ^ x for x in reversed(word))


def run(m, word):
    need(len(word) <= 2 * capacity(m) + 1, "word too long")
    state = 0
    for column in word:
        state = update(m, state, column)
    return state


def odd_phase_differences(m, word):
    """Independent literal phases, with no signature-coordinate arithmetic."""
    need(1 <= m <= 3, "literal oracle restricted to m=1..3")
    reference = 1 << m
    answer = []
    for v in range(1 << (m + 1)):
        if v.bit_count() % 2:
            value = sum((x & v).bit_count() % 2 for x in word)
            baseline = sum((x & reference).bit_count() % 2 for x in word)
            answer.append((value - baseline) % 4)
    return tuple(answer)


def signature_values(m, state):
    """Evaluate the stored quadratic on the odd affine hyperplane."""
    need(1 <= m <= 3, "finite signature table restricted to m=1..3")
    answer = []
    for v in range(1 << (m + 1)):
        if v.bit_count() % 2:
            value = sum(((state >> (2 * i)) & 3) * ((v >> i) & 1)
                        for i in range(m))
            value += 2 * sum(((state >> (2 * m + k)) & 1)
                             * ((v >> i) & 1) * ((v >> j) & 1)
                             for k, (i, j) in enumerate(edges(m)))
            answer.append(value % 4)
    return tuple(answer)


def certify_dimension(m):
    count = 1 << capacity(m)
    need(count <= 512, "exhaustive certificate too large")
    words = tuple(canonical_word(m, s) for s in range(count))
    phases = tuple(odd_phase_differences(m, w) for w in words)
    suffixes = tuple(inverse_word(m, w) for w in words)
    tails = tuple(odd_phase_differences(m, w) for w in suffixes)
    transitions = 0
    for state, word in enumerate(words):
        need(len(word) == capacity(m) == len(suffixes[state]), "fixed word length failed")
        need(run(m, word) == state, "canonical reachability failed")
        need(phases[state] == signature_values(m, state), "literal realization failed")
        need(run(m, word + suffixes[state]) == 0, "inverse suffix failed")
        for column in range(1 << (m + 1)):
            target = update(m, state, column)
            literal = odd_phase_differences(m, word + (column,))
            need(literal == phases[target], "letter transition failed")
            restored = update(m, target, column ^ ((1 << (m + 1)) - 1))
            need(restored == state, "letter is not reversible")
            transitions += 1
    pairs = 0
    for p in range(count):
        for q in range(count):
            accepted = all((a + b) % 4 == 0 for a, b in zip(phases[p], tails[q]))
            need(accepted == (p == q), "distinguishing suffix failed")
            pairs += 1
    need(len(set(phases)) == count, "literal phase classes collide")
    return {"n": m + 1, "bits": capacity(m), "states": count,
            "transitions": transitions, "prefix_suffix_pairs": pairs,
            "prefix_length": capacity(m), "suffix_length": capacity(m)}


def reject(call, *arguments):
    try:
        call(*arguments)
    except ValueError:
        return 1
    raise ValueError("invalid domain was accepted")


def controls():
    count = 0
    for m, state, column in ((0, 0, 0), (73, 0, 0), (True, 0, 0),
                             (2, -1, 0), (2, 32, 0), (2, True, 0),
                             (2, 0, -1), (2, 0, 8), (2, 0, True)):
        count += reject(update, m, state, column)
    # Dropping the mixed bit identifies this rejected word with the empty word.
    mixed = canonical_word(2, 1 << 4)
    need(run(2, mixed) == 16 and any(odd_phase_differences(2, mixed)),
         "mixed-coordinate omission control failed")
    # Retaining only coefficient parity identifies a=2 with zero.
    even = canonical_word(1, 2)
    need(run(1, even) == 2 and any(odd_phase_differences(1, even)),
         "high coefficient bit control failed")
    # A positive letter is not generally its own inverse.
    need(run(1, (1, 1)) == 2 and run(1, (1, 2)) == 0,
         "wrong inverse-letter control failed")
    # A last-coordinate-one column needs the negative step.
    need(update(2, 0, 4) == 31, "negative-step control failed")
    return count + 4


def large_instances():
    rows = []
    for m in (4, 8, 16, 32, 72):
        bits = capacity(m)
        for state in (0, 1, (1 << bits) - 1, (1 << (2 * m)) - 1):
            word = canonical_word(m, state)
            need(run(m, word) == state, "large realization failed")
            need(run(m, word + inverse_word(m, word)) == 0, "large return failed")
        rows.append({"n": m + 1, "bits": bits, "sufficient_known_width": 2 * bits,
                     "encoded_fixtures": 4})
    return rows


def file_hashes():
    folder = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    answer = {}
    for name in names:
        data = (folder / name).read_bytes()
        need(len(data) <= 131072, "package file exceeds receipt bound")
        answer[name] = hashlib.sha256(data).hexdigest()
    return answer


def main():
    rows = [certify_dimension(m) for m in range(1, 4)]
    result = {"status": "PASS_ALL_ODD_SELECTOR_MEMORY", "finite_domains": rows,
              "states_enumerated": sum(r["states"] for r in rows),
              "transitions_checked": sum(r["transitions"] for r in rows),
              "prefix_suffix_pairs": sum(r["prefix_suffix_pairs"] for r in rows),
              "controls": controls(), "large_encoded_instances": large_instances(),
              "errors": 0, "files_sha256": file_hashes()}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
