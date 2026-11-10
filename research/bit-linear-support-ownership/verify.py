#!/usr/bin/env python3
"""Exact new-domain corroboration of the terminal-owner theorem. Apache-2.0."""

import hashlib
import itertools
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def members(mask, width):
    need(1 <= width <= 26 and 0 <= mask < 1 << width, "invalid support")
    return tuple(a for a in range(width) if mask >> a & 1)


def latest(supports, a):
    need(1 <= len(supports) <= 8 and 0 <= a < 26, "invalid history")
    return max((i for i, mask in enumerate(supports[:-1]) if mask >> a & 1),
               default=-1)


def label(supports, i, a, b):
    need(0 <= i < len(supports) <= 8, "invalid event")
    return sum(1 << k for k in range(i)
               if (supports[k] >> a ^ supports[k] >> b) & 1)


def allowed(supports, a, b):
    owner = latest(supports, a)
    return a == b or owner >= 0 and owner == latest(supports, b)


def toggle(items, item):
    if item in items:
        items.remove(item)
    else:
        items.add(item)


def multiply(left, right, width, stages):
    """Literal sparse matrices over F2[D_i,q]/(D_i^2-1,q^2)."""
    need(1 <= width <= 26 and 1 <= stages <= 8, "matrix capacity")
    need(len(left) <= width * width * (2 << stages), "left capacity")
    need(len(right) <= width * width * (2 << stages), "right capacity")
    answer = set()
    for a, b, g, q in left:
        for c, d, h, r in right:
            if b == c and q + r <= 1:
                toggle(answer, (a, d, g ^ h, q + r))
    return answer


def literal_word(supports, responses, width):
    need(1 <= len(supports) == len(responses) <= 8, "word capacity")
    need(1 <= width <= 26, "width capacity")
    word = {(a, a, 0, 0) for a in range(width)}
    for i, (mask, response) in enumerate(zip(supports, responses)):
        live = members(mask, width)
        need(all(0 <= a < width and b in live for a, b in response),
             "response column outside its support")
        factor = {(a, a, (1 << i) if a in live else 0, 0)
                  for a in range(width)}
        for a, b in response:
            factor.add((a, b, (1 << i) if a in live else 0, 1))
        word = multiply(factor, word, width, len(supports))
    return word


def normalized(word, supports, width):
    masks = [sum(1 << i for i, support in enumerate(supports)
                 if support >> a & 1) for a in range(width)]
    return {(a, b, g ^ masks[a], q) for a, b, g, q in word}


def endpoint(word, width):
    if {(a, b, g, q) for a, b, g, q in word if q == 0} != {
            (a, a, 0, 0) for a in range(width)}:
        return False
    return all(q == 0 or a == b and g == 0 for a, b, g, q in word)


def new_histories(stages):
    need(3 <= stages <= 5, "history census capacity")
    for supports in itertools.product(range(1, 8), repeat=stages):
        if max(sum(mask >> a & 1 for mask in supports) for a in range(3)) >= 3:
            yield supports


def census_labels():
    counts = {"histories": 0, "terminal_offdiagonals": 0,
              "feasible_terminal_offdiagonals": 0, "new_multiowner_fields": 0}
    for stages in range(3, 6):
        for supports in new_histories(stages):
            counts["histories"] += 1
            counts["new_multiowner_fields"] += sum(
                sum(mask >> a & 1 for mask in supports) >= 3 for a in range(3))
            live = members(supports[-1], 3)
            for a, b in itertools.permutations(live, 2):
                terminal = label(supports, stages - 1, a, b)
                repeats = any(mask >> b & 1 and label(supports, i, a, b) == terminal
                              for i, mask in enumerate(supports[:-1]))
                need(repeats == allowed(supports, a, b), "terminal image mismatch")
                counts["terminal_offdiagonals"] += 1
                counts["feasible_terminal_offdiagonals"] += repeats
    return counts


def census_literal_impulses():
    count = 0
    for supports in new_histories(3):
        for i, mask in enumerate(supports):
            for a, b in itertools.product(range(3), members(mask, 3)):
                responses = [set() for _ in supports]
                responses[i].add((a, b))
                actual = normalized(literal_word(supports, responses, 3), supports, 3)
                expected = {(c, c, 0, 0) for c in range(3)}
                expected.add((a, b, label(supports, i, a, b), 1))
                need(actual == expected, "literal impulse coefficient mismatch")
                count += 1
    return count


def completion(supports, terminal):
    """Sufficiency only for the unrestricted linear endpoint relaxation."""
    responses = [set() for _ in supports]
    for a, b in terminal:
        need(allowed(supports, a, b), "forbidden terminal coefficient")
        responses[-1].add((a, b))
        if a != b:
            owner = latest(supports, a)
            responses[owner].add((a, b))
    return responses


def census_attainment():
    count = 0
    for supports in new_histories(3):
        live = members(supports[-1], 3)
        free = tuple((a, b) for a, b in itertools.permutations(live, 2)
                     if allowed(supports, a, b))
        for bits in range(1 << len(free)):
            terminal = {(a, a) for a in live if a != 1}
            terminal.update(pair for j, pair in enumerate(free) if bits >> j & 1)
            responses = completion(supports, terminal)
            actual = normalized(literal_word(supports, responses, 3), supports, 3)
            need(endpoint(actual, 3), "attaining completion missed endpoint")
            need(responses[-1] == terminal, "terminal matrix changed")
            count += 1
    return count


def census_fano():
    lines = tuple(sum(1 << a for a in (x, y, x ^ y))
                  for x in range(1, 8) for y in range(x + 1, 8))
    lines = tuple(sorted(set(lines)))
    need(len(lines) == 7, "Fano line count")
    supports = tuple(mask | 1 << (8 + i) for i, mask in enumerate(lines))
    need(all(mask.bit_count() == 4 for mask in supports), "four-support fixture")
    need(all((a & b).bit_count() == 1
             for a, b in itertools.combinations(supports, 2)), "linear fixture")
    need(all(sum(mask >> a & 1 for mask in supports) == 3 for a in range(1, 8)),
         "three-owner fixture")
    count = 0
    for order in itertools.permutations(supports):
        for a, b in itertools.permutations(members(order[-1], 15), 2):
            need(not allowed(order, a, b), "Fano terminal failed separation")
            terminal = label(order, 6, a, b)
            need(all(not (mask >> b & 1) or label(order, i, a, b) != terminal
                     for i, mask in enumerate(order[:-1])), "Fano cancellation")
        count += 1
    return count


def apply_binary(response, vector):
    answer = 0
    for a, b in response:
        if vector >> b & 1:
            answer ^= 1 << a
    return answer


def boundary_controls():
    supports = (15, 15, 15)
    responses = [{(0, 1)}, {(1, 0)}, {(0, 0), (0, 1), (1, 0), (1, 1)}]
    for response, u, w in zip(responses, (1, 2, 3), (2, 1, 1)):
        need(u != 0 and apply_binary(response, u) == 0
             and apply_binary(response, w) == u, "positive native chain")
    word = normalized(literal_word(supports, responses, 4), supports, 4)
    expected = {(a, a, 0, 0) for a in range(4)} | {(0, 0, 0, 1), (1, 1, 0, 1)}
    need(word == expected, "three-owner positive full word")
    mutated = [responses[0], set(), responses[2]]
    need(not endpoint(normalized(literal_word(supports, mutated, 4), supports, 4), 4),
         "omitted response accepted")
    need(not allowed((1, 2, 7), 0, 1), "unequal last owners accepted")
    need(not allowed((4, 4, 7), 0, 1), "private coordinates coalesced")
    need(allowed((1, 3, 7), 0, 1), "full histories substituted for latest owner")
    try:
        completion((1, 2, 7), {(0, 1)})
    except ValueError:
        pass
    else:
        raise ValueError("forbidden completion did not reject")
    try:
        literal_word((1, 2, 7), [{(0, 1)}, set(), set()], 3)
    except ValueError:
        pass
    else:
        raise ValueError("outside-support source did not reject")
    outside = normalized(literal_word((1, 1, 1), [{(2, 0)}, set(), set()], 3),
                         (1, 1, 1), 3)
    need((2, 0, 0, 1) in outside, "outside-support row incorrectly removed")
    return 8


def main():
    result = census_labels()
    result["literal_impulses"] = census_literal_impulses()
    result["attaining_terminal_matrices"] = census_attainment()
    result["four_support_fano_orders"] = census_fano()
    result["boundary_control_groups"] = boundary_controls()
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result["source_sha256"] = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}
    result["status"] = "PASS_BIT_LINEAR_SUPPORT_OWNERSHIP"
    result["claim_type"] = "scoped proof with finite corroboration"
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
