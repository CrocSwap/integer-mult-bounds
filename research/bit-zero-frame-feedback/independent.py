#!/usr/bin/env python3
"""Code-disjoint truth-table check of every labeled six-wire endpoint.

No imports from verify.py. Enumerate complete maps on all 64 dirty bit inputs,
using byte translation to compose functions. Apache-2.0; substantial OpenAI
Codex assistance, prepared for commdata2338.
"""
from collections import Counter, deque
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def gate_table(n, destination, source):
    return bytes(x ^ (((x >> source) & 1) << destination) for x in range(256))


def ball(n, helpers, restricted, radius):
    gates = [gate_table(n, d, s) for s in range(n) for d in range(n)
             if d != s and not (restricted and d < helpers <= s)]
    identity = bytes(range(1 << n))
    distances = {identity: 0}
    layers = [[identity]]
    for depth in range(1, radius + 1):
        layer = []
        for mapping in layers[-1]:
            for gate in gates:
                reached = mapping.translate(gate)
                if reached not in distances:
                    distances[reached] = depth
                    layer.append(reached)
        layers.append(layer)
    return distances, layers


def endpoint(k, h, t):
    result = []
    for initial in range(1 << (h + t)):
        final = initial
        for row in range(t):
            parity = 0
            for col in range(h):
                parity ^= ((initial >> col) & 1) & ((k >> (row * h + col)) & 1)
            final ^= parity << (h + row)
        result.append(final)
    return bytes(result)


def complete_small_check(h, t):
    """Ordinary full-group BFS, without meet-in-the-middle or orbit reduction."""
    n = h + t
    wanted = {endpoint(k, h, t): k for k in range(1 << (h * t))}
    answers = []
    for restricted in (False, True):
        tables = [gate_table(n, d, s) for d in range(n) for s in range(n)
                  if d != s and not (restricted and d < h <= s)]
        start = bytes(range(1 << n))
        distance = {start: 0}
        queue = deque([start])
        while queue:
            state = queue.popleft()
            for table in tables:
                after = state.translate(table)
                if after not in distance:
                    distance[after] = distance[state] + 1
                    queue.append(after)
        answers.append({k: distance[state] for state, k in wanted.items()})
        if h == t == 2:
            require(len(distance) == (576 if restricted else 20160), "full GL4/parabolic cardinality")
    require(answers[0] == answers[1], "small feedback gain")
    return answers[0]


def replay_witness(word, wanted, h, t):
    state = bytes(range(1 << (h + t)))
    for d, s in word:
        require(type(d) is int and type(s) is int and 0 <= d < h+t and 0 <= s < h+t and d != s,
                "bad witness gate")
        require(not (d < h <= s), "witness uses target feedback")
        state = state.translate(gate_table(h+t, d, s))
    require(state == wanted, "witness fails on dirty input")


def main():
    package = Path(__file__).resolve().parent
    certificate = json.loads((package / "CERTIFICATE.json").read_text())
    all_checked = 0
    for entry in certificate["dimensions"]:
        h, t = entry["helpers"], entry["targets"]
        # The primary certificate proves upper bounds via restricted words.
        for row in entry["orbits"]:
            replay_witness(row["restricted_witness"], endpoint(row["k"], h, t), h, t)
            require(len(row["restricted_witness"]) == row["minimum"], "upper-bound cost")
        distances, layers = ball(h+t, h, False, 4)
        require([len(x) for x in layers] == entry["unrestricted_spheres"], "independent sphere counts")
        left = [(mapping + bytes(256-len(mapping)), depth)
                for depth, layer in enumerate(layers[:4]) for mapping in layer]
        histogram = Counter()
        minima = {}
        # No use of the primary permutation quotient: every labeled K is checked.
        for k in range(1 << (h*t)):
            goal = endpoint(k, h, t)
            best = 8
            for translation, depth in left:
                other = distances.get(goal.translate(translation))
                if other is not None:
                    best = min(best, depth + other)
            require(best < 8, "insufficient independent search radius")
            minima[k] = best
            histogram[str(best)] += 1
            all_checked += 1
        require(dict(histogram) == entry["minimum_histogram"], "independent minimum distribution")
        # Check orbit coverage separately, by relabeling actual gate witnesses
        # using explicit output-to-input register bijections.
        from itertools import permutations
        covered = {}
        for row in entry["orbits"]:
            local = set()
            for hp in permutations(range(h)):
                for tp in permutations(range(t)):
                    mapping = hp + tuple(h+x for x in tp)
                    word = [[mapping[d], mapping[s]] for d, s in row["restricted_witness"]]
                    endpoint_k = 0
                    for r in range(t):
                        for c in range(h):
                            if row["k"] & (1 << (r*h+c)):
                                endpoint_k |= 1 << (tp[r]*h+hp[c])
                    replay_witness(word, endpoint(endpoint_k, h, t), h, t)
                    require(minima[endpoint_k] == len(word), "labeled upper/lower bounds disagree")
                    local.add(endpoint_k)
                    covered[endpoint_k] = len(word)
            require(len(local) == row["orbit_size"], "orbit cardinality")
        require(covered == minima, "labeled endpoint coverage")
        if h <= 2 and t <= 2:
            require(complete_small_check(h, t) == minima, "full-BFS control")
    require(all_checked == 682, "missing dimensions")
    print("PASS_INDEPENDENT_ZERO_FRAME_FEEDBACK labeled_maps=682 dirty_inputs_per_six_wire_map=64 full_GL4=20160")


if __name__ == "__main__":
    main()
