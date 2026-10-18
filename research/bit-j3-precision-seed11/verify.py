#!/usr/bin/env python3
"""Exact J3 gate/positive-envelope frontier; standard library only.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
Every word is retained: binary endpoint deduplication loses positive lifts.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATES = tuple((d, s) for d in range(6) for s in range(6) if d != s)
IDENTITY = sum((1 << i) << (6 * i) for i in range(6))
TARGET = IDENTITY ^ sum(7 << (6 * i) for i in range(3, 6))
SEVEN = ((0, 1), (0, 2), (3, 0), (4, 0), (5, 0), (0, 2), (0, 1))
EIGHT = ((0, 1), (3, 0), (4, 0), (5, 0), (0, 1), (3, 2), (4, 2), (5, 2))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encode(gates):
    result = []
    for gate in gates:
        require(isinstance(gate, (tuple, list)) and len(gate) == 2, "invalid gate")
        d, s = gate
        require(type(d) is int and type(s) is int and 0 <= d < 6 and 0 <= s < 6
                and d != s, "gate outside the paid alphabet")
        result.append(GATES.index((d, s)))
    return tuple(result)


def step(state, index):
    d, s = GATES[index]
    return state ^ (((state >> (6 * s)) & 63) << (6 * d))


def endpoint(word):
    state = IDENTITY
    for index in word:
        state = step(state, index)
    return state


def paths(state, depth, prefix=()):
    if depth == 0:
        yield state, prefix
        return
    for index in range(30):
        yield from paths(step(state, index), depth - 1, prefix + (index,))


def envelope(word):
    # For ADD-only words these six nonnegative values are monotone.
    bounds = [1] * 6
    for index in word:
        d, s = GATES[index]
        bounds[d] += bounds[s]
    return max(bounds)


def positive_matrix(word):
    rows = [[int(i == j) for j in range(6)] for i in range(6)]
    for index in word:
        d, s = GATES[index]
        rows[d] = [a + b for a, b in zip(rows[d], rows[s])]
    return rows


def census():
    backward = defaultdict(list)
    level_states, level_paths = [], []
    for depth in range(4):
        states, count = set(), 0
        for state, word in paths(TARGET, depth):
            states.add(state)
            count += 1
            backward[state].append(word)
        level_states.append(len(states))
        level_paths.append(count)
    # Length 0..3 is checked separately; 4..7 has one fixed 4 | (L-4) split.
    counts = [0] * 8
    for depth in range(4):
        counts[depth] = sum(state == TARGET for state, _ in paths(IDENTITY, depth))
    histogram, feedback, words = Counter(), Counter(), []
    prefixes = 0
    for state, prefix in paths(IDENTITY, 4):
        prefixes += 1
        for suffix in backward.get(state, ()):
            word = prefix + suffix[::-1]
            counts[len(word)] += 1
            if len(word) == 7:
                words.append(word)
                f, b = envelope(word), envelope(word[::-1])
                histogram[(f, b)] += 1
                feedback[any(GATES[g][0] < 3 <= GATES[g][1] for g in word)] += 1
    words.sort()
    require(len(words) == len(set(words)), "duplicate split enumeration")
    return {
        "words_by_length_0_through_7": counts,
        "backward_paths_by_length": level_paths,
        "backward_distinct_endpoints_by_length": level_states,
        "backward_distinct_endpoints_total": len(backward),
        "forward_length_four_paths": prefixes,
        "shortest_word_sha256": hashlib.sha256(b"".join(bytes(w) for w in words)).hexdigest(),
        "shortest_positive_histogram": [
            {"forward": f, "reverse": b, "words": n}
            for (f, b), n in sorted(histogram.items())],
        "shortest_words_with_target_to_helper_feedback": feedback[True],
    }


def fixture(gates):
    word = encode(gates)
    require(endpoint(word) == TARGET and endpoint(word[::-1]) == TARGET,
            "dirty boundary mismatch")
    return {"gates": [list(g) for g in gates], "cost": len(word),
            "forward": envelope(word), "reverse": envelope(word[::-1]),
            "positive_forward": positive_matrix(word),
            "positive_reverse": positive_matrix(word[::-1])}


def controls():
    rejected = []

    def reject(name, check):
        try:
            check()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("control did not reject: " + name)

    reject("omitted_helper_restoration", lambda: fixture(EIGHT[:4] + EIGHT[5:]))
    wrong_source = EIGHT[:5] + ((3, 1),) + EIGHT[6:]
    reject("wrong_helper_source", lambda: fixture(wrong_source))
    reject("missing_target_update", lambda: fixture(EIGHT[:-1]))
    reject("self_xor", lambda: encode(((0, 0),)))
    reject("boolean_register", lambda: encode(((False, 1),)))
    reject("out_of_range_register", lambda: encode(((6, 0),)))
    reject("endpoint_only_envelope", lambda: require(envelope(encode(SEVEN)) == 4,
                                                       "F2 endpoint hides restoration growth"))
    chain = ((3, 4), (4, 5), (5, 0), (5, 1), (5, 2), (4, 5), (3, 4))
    require(fixture(chain)["forward"] == 8, "same endpoint, different positive lift")
    reject("one_representative_per_endpoint", lambda: require(
        envelope(encode(chain)) == envelope(encode(SEVEN)), "binary equality is insufficient"))
    # A missing restoration is invisible if helpers start clean.
    broken = endpoint(encode(EIGHT[:4] + EIGHT[5:]))
    target_input_mask = sum(56 << (6 * i) for i in range(6))
    require(broken != TARGET and (broken & target_input_mask) == (TARGET & target_input_mask),
            "clean-helper boundary control")
    # Padding by two self-inverse XORs preserves the endpoint but costs two.
    padded = SEVEN + ((1, 2), (1, 2))
    require(fixture(padded)["cost"] == 9, "paid neutral pair")
    return {"rejected": rejected,
            "positive": ["clean_helpers_hide_missing_restore", "neutral_pair_costs_two",
                         "same_endpoint_has_distinct_positive_lifts"]}


def build_report():
    seven, eight = fixture(SEVEN), fixture(EIGHT)
    improvements = {}
    for direction in ("forward", "reverse"):
        a, b = seven["positive_" + direction], eight["positive_" + direction]
        require(all(b[i][j] <= a[i][j] for i in range(6) for j in range(6)),
                "componentwise positive domination")
        improvements[direction] = [[i, j, a[i][j], b[i][j]]
                                   for i in range(6) for j in range(6) if b[i][j] < a[i][j]]
    support_floor = max(((TARGET >> (6 * i)) & 63).bit_count() for i in range(6))
    return {"schema_version": 1, "model": "six-dirty-register-zero-frame-J3-unit-XOR",
            "census": census(), "seven_gate_witness": seven, "eight_gate_witness": eight,
            "positive_support_lower_bound": support_floor,
            "strict_componentwise_improvements": improvements,
            "pareto_gate_count_bidirectional_peak": [[7, 5], [8, 4]],
            "controls": controls()}


def verify_context_pins():
    root = HERE.parents[1]
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for row in pins["files"]:
        if row["usage"] == "input":
            require(hashlib.sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "context source drift: " + row["path"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    parser.add_argument("--emit", action="store_true", help="write a fresh certificate, never overwrite")
    args = parser.parse_args()
    verify_context_pins()
    report = build_report()
    require(report["census"]["words_by_length_0_through_7"] == [0] * 7 + [216], "word census")
    require(report["positive_support_lower_bound"] == 4, "support floor")
    require(report["seven_gate_witness"]["forward"] == report["seven_gate_witness"]["reverse"] == 5,
            "seven-gate positive peak")
    require(report["eight_gate_witness"]["forward"] == report["eight_gate_witness"]["reverse"] == 4,
            "eight-gate positive peak")
    if args.emit:
        with args.certificate.open("x") as output:
            output.write(json.dumps(report, indent=2) + "\n")
    else:
        require(report == json.loads(args.certificate.read_text()), "certificate does not match replay")
    print("PASS_J3_PRECISION shortest_words=216 peaks=5:108,6:72,8:36 frontier=(7,5),(8,4) controls=8 no_new_kappa")


if __name__ == "__main__":
    main()
