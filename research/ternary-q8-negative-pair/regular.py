#!/usr/bin/env python3
"""Separate dense regular-action enumeration, with no producer imports. Apache-2.0."""

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASIS = tuple(tuple(sign if a == b else 0 for a in range(4))
              for b in range(4) for sign in (1, -1))


def check(ok, message):
    if not ok:
        raise ValueError(message)


def hamilton(u, v):
    a, b, c, d = u
    e, f, g, h = v
    return (a*e-b*f-c*g-d*h, a*f+b*e+c*h-d*g,
            a*g-b*h+c*e+d*f, a*h+b*g-c*f+d*e)


def multiply(a, b):
    out = [0] * 256
    for i in range(16):
        for k in range(16):
            value = a[16*i+k]
            if value:
                for j in range(16):
                    out[16*i+j] += value * b[16*k+j]
    return bytes(x % 3 for x in out)


def diagonal(a, b):
    out = [0] * 256
    for role, group in enumerate((a, b)):
        for address in range(8):
            image = BASIS.index(hamilton(BASIS[group], BASIS[address]))
            out[16*(8*role+image)+8*role+address] = 1
    return bytes(out)


def projectors():
    found = set()
    for u, v in itertools.product(itertools.product(range(3), repeat=2), repeat=2):
        if sum(x*y for x, y in zip(u, v)) % 3 == 1:
            found.add(tuple(x*y % 3 for x in u for y in v))
    check(len(found) == 12, "outer-product projector inventory")
    return sorted(found)


def factor(p, group):
    out = [int(i == j) for i in range(16) for j in range(16)]
    for r, s, address in itertools.product(range(2), range(2), range(8)):
        image = BASIS.index(hamilton(BASIS[group], BASIS[address]))
        out[16*(8*r+image)+8*s+address] += p[2*r+s]
        out[16*(8*r+address)+8*s+address] -= p[2*r+s]
    return bytes(x % 3 for x in out)


def search(start, gates):
    seen, frontier = {start}, {start}
    layers, transitions = [1], 0
    for _depth in range(2):
        following = set()
        for value in frontier:
            for gate in gates:
                following.add(multiply(gate, value))
                transitions += 1
        following.difference_update(seen)
        layers.append(len(following))
        seen.update(following)
        frontier = following
    check(len(seen) <= 601, "search capacity")
    return seen, layers, transitions


def coefficient_digest(states):
    # The two identity-input columns recover all formal coefficients.
    payloads = []
    for state in states:
        payloads.append(bytes(state[16*(8*r+h)+8*s]
                              for r in range(2) for s in range(2) for h in range(8)))
    check(len(set(payloads)) == len(states), "regular-action coefficient injectivity")
    return hashlib.sha256(b"".join(sorted(payloads))).hexdigest()


def main():
    certificate = json.loads((ROOT / "RESULT.json").read_text())
    ps = projectors()
    gates = [factor(p, g) for p in ps for g in (2, 4)]
    inverses = [factor(p, g) for p in ps for g in (3, 5)]
    identity, target = diagonal(0, 0), diagonal(3, 5)
    for gate, inverse in zip(gates, inverses):
        check(multiply(gate, inverse) == identity, "literal gate inverse")
    forward, fs, ft = search(identity, gates)
    backward, bs, bt = search(target, inverses)
    check(not forward & backward, "dense shorter word found")
    check(fs == bs == [1, 24, 466], "dense layer counts")
    check(fs == certificate["forward_layers"] and bs == certificate["reverse_layers"],
          "producer layer disagreement")
    check(ft == bt == 600, "dense transition counts")
    check(coefficient_digest(forward) == certificate["forward_sha256"], "forward set")
    check(coefficient_digest(backward) == certificate["reverse_sha256"], "reverse set")
    word = [factor((1, 0, 0, 0), 2)]*3 + [factor((0, 0, 0, 1), 4)]*3
    state = identity
    for gate in word:
        state = multiply(gate, state)
    check(state == target, "dense attaining word")
    for removed in range(6):
        state = identity
        for position, gate in enumerate(word):
            if position != removed:
                state = multiply(gate, state)
        check(state != target, "dense omission")
    planted = identity
    for gate in word[:4]:
        planted = multiply(gate, planted)
    planted_reverse, _, _ = search(planted, inverses)
    check(bool(forward & planted_reverse), "dense planted hit missed")
    check(certificate["exact_minimum"] == 6 and certificate["meet_intersections"] == 0,
          "certificate conclusion")
    print("PASS_TERNARY_Q8_REGULAR_ACTION matrices=982 transitions=1200 "
          "minimum=6 planted_hit=1 omissions=6 no_new_kappa")


if __name__ == "__main__":
    main()
