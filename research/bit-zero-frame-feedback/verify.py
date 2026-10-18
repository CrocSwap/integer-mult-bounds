#!/usr/bin/env python3
"""Exact shortest zero-frame XOR compensation circuits; standard library only.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
Matrices use packed binary rows. independent.py uses complete truth tables and
does not import this implementation. Neither checker executes supplier code.
"""
import argparse
from collections import Counter
import hashlib
from itertools import permutations
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


class Reject(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Reject(message)


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    def invalid(value):
        raise Reject("nonfinite JSON: " + value)
    return json.loads(Path(path).read_text(), object_pairs_hook=unique,
                      parse_constant=invalid)


def canonical(value):
    # Comparing encoded JSON also distinguishes true from 1.
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def identity(n):
    return sum(1 << (i * n + i) for i in range(n))


def generators(h, t, feedback):
    return [(d, s) for d in range(h + t) for s in range(h + t)
            if d != s and (feedback or not (d < h <= s))]


def step(matrix, gate, n):
    d, s = gate
    return matrix ^ (((matrix >> (s * n)) & ((1 << n) - 1)) << (d * n))


def target(k, h, t):
    n = h + t
    return identity(n) ^ sum(((k >> (r * h)) & ((1 << h) - 1)) << ((h + r) * n)
                             for r in range(t))


def sphere_ball(h, t, feedback, radius=4):
    """Every word through radius, deduplicated by its complete linear map."""
    n = h + t
    gates = generators(h, t, feedback)
    first = identity(n)
    distances = {first: 0}
    last_gate = {}
    layers = [[first]]
    for depth in range(1, radius + 1):
        layer = []
        for matrix in layers[-1]:
            for index, gate in enumerate(gates):
                reached = step(matrix, gate, n)
                if reached not in distances:
                    distances[reached] = depth
                    last_gate[reached] = index
                    layer.append(reached)
        layers.append(layer)
    return distances, layers, last_gate, gates


def word_for(matrix, h, t, ball):
    distances, _, last_gate, gates = ball
    reverse_word = []
    while distances[matrix]:
        gate = gates[last_gate[matrix]]
        reverse_word.append(list(gate))
        matrix = step(matrix, gate, h + t)
    return list(reversed(reverse_word))


def right_shear(matrix, k, h, t):
    """Return matrix * T_K (not T_K * matrix)."""
    n = h + t
    out = matrix
    column_mask = sum(1 << (r * n) for r in range(n))
    for r in range(t):
        column = matrix & (column_mask << (h + r))
        for c in range(h):
            if k & (1 << (r * h + c)):
                out ^= column >> (h + r - c)
    return out


def shortest(k, h, t, ball):
    """Complete meet-in-the-middle coverage of lengths 0..7.

    If B=A*T_K, then T_K=A^-1*B, so run B followed by reverse(A).
    Every word of length <=7 splits into pieces of length <=4 and <=3.
    Finding an attained minimum <=7 thus certifies a global minimum.
    """
    distances, layers, _, _ = ball
    best = None
    for depth, layer in enumerate(layers[:4]):
        for left in layer:
            right = right_shear(left, k, h, t)
            other = distances.get(right)
            if other is not None and (best is None or depth + other < best[0]):
                best = (depth + other, left, right)
    need(best is not None and best[0] <= 7, "search radius insufficient; no minimum claim")
    length, left, right = best
    word = word_for(right, h, t, ball) + list(reversed(word_for(left, h, t, ball)))
    need(len(word) == length, "witness length")
    check_word(word, k, h, t, True)
    return length, word


def check_word(word, k, h, t, feedback):
    n = h + t
    allowed = set(generators(h, t, feedback))
    matrix = identity(n)
    for gate in word:
        need(isinstance(gate, list) and len(gate) == 2 and
             all(type(x) is int for x in gate), "typed gate")
        need(tuple(gate) in allowed, "forbidden gate")
        matrix = step(matrix, gate, n)
    need(matrix == target(k, h, t), "complete dirty boundary")
    return len(word)


def orbit(k, h, t):
    return {sum(((k >> (r * h + c)) & 1) << (rr * h + cc)
                for rr, r in enumerate(rp) for cc, c in enumerate(cp))
            for rp in permutations(range(t)) for cp in permutations(range(h))}


def census(h, t):
    restricted = sphere_ball(h, t, False)
    unrestricted = sphere_ball(h, t, True)
    remaining = set(range(1 << (h * t)))
    rows = []
    distribution = Counter()
    while remaining:
        k = min(remaining)
        members = orbit(k, h, t)
        need(members <= remaining, "orbit partition")
        remaining -= members
        old, witness = shortest(k, h, t, restricted)
        new, _ = shortest(k, h, t, unrestricted)
        need(old == new, "feedback advantage found; update the stated result")
        check_word(witness, k, h, t, False)
        distribution[str(old)] += len(members)
        rows.append({"k": k, "orbit_size": len(members), "minimum": old,
                     "restricted_witness": witness})
    return {"helpers": h, "targets": t, "maps": 1 << (h * t),
            "restricted_spheres": [len(x) for x in restricted[1]],
            "unrestricted_spheres": [len(x) for x in unrestricted[1]],
            "minimum_histogram": dict(sorted(distribution.items())), "orbits": rows}


def controls():
    rejected = []
    def reject(name, action):
        try:
            action()
        except Reject:
            rejected.append(name)
        else:
            raise Reject("control accepted: " + name)
    # A legal source-free helper-star computes y += h0+h1 and restores dirt.
    star = [[0, 1], [2, 0], [0, 1]]
    need(check_word(star, 3, 2, 1, False) == 3, "star positive control")
    # Complete target feedback is allowed by the new prefix contract. The
    # five-gate word is the one-gate shear, but every one of its gates is paid.
    feedback = [[0, 1], [1, 0], [0, 1], [1, 0], [0, 1]]
    need(check_word(feedback, 1, 1, 1, True) == 5, "feedback positive control")
    reject("feedback_rejected_in_restricted_alphabet",
           lambda: check_word(feedback, 1, 1, 1, False))
    reject("omitted_helper_restoration", lambda: check_word(star[:-1], 3, 2, 1, True))
    reject("wrong_helper_column", lambda: check_word([[2, 0]], 3, 2, 1, True))
    # This passes on y=0 and has the correct helper->target block, but mixes
    # the arbitrary initial targets. A zero-target test would miss the fault.
    reject("residual_target_basis", lambda: check_word([[1, 0], [2, 1]], 3, 1, 2, True))
    reject("wrong_target_map", lambda: check_word([[1, 0]], 0, 1, 1, True))
    reject("self_xor_noninvertible", lambda: check_word([[0, 0]], 0, 1, 1, True))
    reject("boolean_gate_index", lambda: check_word([[True, 0]], 1, 1, 1, True))
    reject("insufficient_radius", lambda: shortest(511, 3, 3, sphere_ball(3, 3, True, 2)))
    return {"positive_star_cost": 3, "positive_feedback_cost": 5,
            "negative_controls": rejected}


def check_source_pins():
    root = PACKAGE.parents[1]
    sources = load(PACKAGE / "SOURCES.json")
    for row in sources["files"]:
        if row["usage"] == "input":
            data = (root / row["path"]).read_bytes()
            need(hashlib.sha256(data).hexdigest() == row["sha256"], "input source pin: " + row["path"])


def build():
    return {"schema_version": 1, "kind": "finite-exact-shortest-circuit-certificate",
            "gate_cost": 1, "ancillas": 0, "all_inputs_arbitrary": True,
            "dimensions": [census(h, t) for h in range(1, 4) for t in range(1, 4)],
            "controls": controls()}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="regenerate the package certificate")
    args = ap.parse_args()
    check_source_pins()
    result = build()
    destination = PACKAGE / "CERTIFICATE.json"
    if args.write:
        destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(canonical(load(destination)) == canonical(result), "certificate differs from exact regeneration")
    rows = result["dimensions"][-1]
    print("PASS_ZERO_FRAME_FEEDBACK maps=682 six_wire_maps=512 orbits=" + str(len(rows["orbits"])) +
          " max_minimum=7 feedback_gains=0 controls=8 no_new_kappa")


if __name__ == "__main__":
    main()
