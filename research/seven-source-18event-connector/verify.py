#!/usr/bin/env python3
"""Exact 144-call connector certificate. Python standard library only.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Apache-2.0. Interface: Ross Richardson's PR943. Seven-source question and
smaller-path lower bounds: Cinna Davis's PR2229/2236. No checker imports.
"""
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MASKS = tuple(m for m in range(1, 128) if 1 <= m.bit_count() <= 3)
SOURCE_LENGTHS = (1, 2, 3, 4, 1, 2, 3)
TARGET_LENGTHS = tuple(m.bit_count() for m in MASKS)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read(path):
    return json.loads(Path(path).read_bytes(), object_pairs_hook=unique_object)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def check_sources():
    count = 0
    for item in read(HERE / "SOURCES.json")["files"]:
        if item["usage"] == "input":
            payload = (ROOT / item["path"]).read_bytes()
            require(hashlib.sha256(payload).hexdigest() == item["sha256"],
                    "source hash mismatch: " + item["path"])
            count += 1
    require(count == 2, "two interface source pins required")
    return count


def validate(certificate):
    require(set(certificate) == {"schema", "source_word", "prefix_states",
                                "target_masks", "readout_pairs", "events"}, "certificate fields")
    require(certificate["schema"] == "seven-source-18event-connector/1", "schema")
    word = certificate["source_word"]
    require(len(word) == 18 and all(type(j) is int and 0 <= j < 7 for j in word),
            "18 singleton source calls")
    counts = [word.count(j) for j in range(7)]
    require(counts == [4, 4, 2, 2, 2, 2, 2], "source multiplicities")
    prefix = [0]
    for j in word:
        prefix.append(prefix[-1] ^ (1 << j))
    require(prefix[-1] == 0, "connector restoration")
    require(certificate["prefix_states"] == prefix and
            all(type(x) is int for x in certificate["prefix_states"]), "prefix states")
    require(certificate["target_masks"] == list(MASKS) and
            all(type(m) is int for m in certificate["target_masks"]), "complete target family")
    pairs = certificate["readout_pairs"]
    require(set(pairs) == {str(m) for m in MASKS}, "readout coverage")
    for m in MASKS:
        pair = pairs[str(m)]
        require(isinstance(pair, list) and len(pair) == 2 and
                all(type(x) is int for x in pair), "readout pair type")
        s, t = pair
        require(0 <= s < t <= len(word), "readout boundary range")
        require(prefix[s] ^ prefix[t] == m, "prefix-difference identity")
        interval_mask = 0
        for j in word[s:t]:
            interval_mask ^= 1 << j
        require(interval_mask == m, "independent interval-XOR identity")
    events = []
    for boundary in range(19):
        for index, m in enumerate(MASKS):
            if boundary in pairs[str(m)]:
                events.append(["A", index])
        if boundary < 18:
            events.append(["B", word[boundary]])
    require(all(isinstance(e, list) and len(e) == 2 and type(e[0]) is str and
                type(e[1]) is int for e in certificate["events"]), "event types")
    require(certificate["events"] == events, "literal chronological program")
    require(len(events) == 144, "144 complete calls")
    return counts, events


def initial_rows():
    names = ["X" + str(j) for j in range(7)] + ["Y" + str(i) for i in range(63)]
    names += ["Z", "W0", "W1"]
    # (input_name, word) means word applied to the arbitrary initial row.
    # Words are outermost-first and noncommuting. Set XOR is addition in F2.
    return {name: {(name, ())} for name in names}


def apply_word(expression, word):
    return {(source, tuple(word) + old) for source, old in expression}


def map_word(kind, index, expanded):
    if not expanded:
        return (kind + str(index),)
    length = SOURCE_LENGTHS[index] if kind == "B" else TARGET_LENGTHS[index]
    return tuple(kind + str(index) + "." + str(k) for k in reversed(range(length)))


def expected_rows(expanded=False):
    result = initial_rows()
    for i, mask in enumerate(MASKS):
        for j in range(7):
            if mask >> j & 1:
                term = ("X" + str(j), map_word("A", i, expanded) + map_word("B", j, expanded))
                result["Y" + str(i)].symmetric_difference_update({term})
    return result


def replay_root(events, state=None):
    state = initial_rows() if state is None else {k: set(v) for k, v in state.items()}
    for kind, index in events:
        require(kind in ("A", "B") and type(index) is int and
                0 <= index < (7 if kind == "B" else 63), "root call type")
        source, target = ("X" + str(index), "Z") if kind == "B" else ("Z", "Y" + str(index))
        state[target].symmetric_difference_update(apply_word(state[source], map_word(kind, index, False)))
    return state


def compile_product(factors, source, target, level=0):
    """Application-order factors; every product uses a dirty four-call echo."""
    require(source != target, "source/target alias")
    if len(factors) == 1:
        return [(factors[0], source, target)]
    require(level < 2, "scratch depth")
    work = "W" + str(level)
    require(work not in (source, target), "scratch aliases active row")
    middle = len(factors) // 2
    first = compile_product(factors[:middle], source, work, level + 1)
    second = compile_product(factors[middle:], work, target, level + 1)
    return first + second + first[::-1] + second[::-1]


def expand(events, reverse_factors=False):
    program = []
    for kind, index in events:
        factors = list(reversed(map_word(kind, index, True)))
        if reverse_factors:
            factors.reverse()
        source, target = ("X" + str(index), "Z") if kind == "B" else ("Z", "Y" + str(index))
        program.extend(compile_product(factors, source, target))
    return program


def replay_leaves(program, state=None):
    state = initial_rows() if state is None else {k: set(v) for k, v in state.items()}
    for operator, source, target in program:
        require(source != target, "aliased leaf call")
        state[target].symmetric_difference_update(apply_word(state[source], (operator,)))
    return state


def check_completed_boundaries(events):
    """Check every returned child, so dirty scratch cannot leak between calls."""
    literal = initial_rows()
    specified = initial_rows()
    for event in events:
        kind, index = event
        literal = replay_leaves(expand([event]), literal)
        source, target = ("X" + str(index), "Z") if kind == "B" else ("Z", "Y" + str(index))
        specified[target].symmetric_difference_update(apply_word(specified[source], map_word(kind, index, True)))
        require(literal == specified, "completed child boundary or private dirt")
    return len(events)


def baseline():
    result = []
    for i, m in enumerate(MASKS):
        sources = [["B", j] for j in range(7) if m >> j & 1]
        result.extend(sources + [["A", i]] + sources[::-1] + [["A", i]])
    return result


@lru_cache(maxsize=None)
def leaf_cost(n):
    return 1 if n == 1 else 2 * (leaf_cost(n // 2) + leaf_cost(n - n // 2))


def invoice(events):
    counts = Counter(tuple(e) for e in events)
    b = [counts["B", j] for j in range(7)]
    a = [counts["A", i] for i in range(63)]
    return {"source_calls_by_map": b, "source_calls": sum(b),
            "target_calls": sum(a), "complete_calls": sum(a) + sum(b),
            "root_descriptor_bits": 4 * sum(b) + 7 * sum(a),
            "primitive_leaf_calls_fixture": sum(b[j] * leaf_cost(n) for j, n in enumerate(SOURCE_LENGTHS))
            + sum(a[i] * leaf_cost(n) for i, n in enumerate(TARGET_LENGTHS))}


def concrete_checks(program):
    """Separate dense interpretation on all basis inputs, dimensions1..3."""
    labels = sorted({op for op, _, _ in program})
    names = list(initial_rows())
    forward_cases = inverse_cases = 0
    for dimension in (1, 2, 3):
        mask = (1 << dimension) - 1
        matrices = {}
        for label in labels:
            digest = hashlib.sha256(label.encode()).digest()
            matrices[label] = [digest[k] & mask for k in range(dimension)]

        def matvec(label, value):
            return sum(((row & value).bit_count() % 2) << k for k, row in enumerate(matrices[label]))

        def evaluate_word(word, value):
            for label in reversed(word):
                value = matvec(label, value)
            return value

        for name in names:
            for bit in range(dimension):
                state = {row: 0 for row in names}
                state[name] = 1 << bit
                original = dict(state)
                for op, source, target in program:
                    state[target] ^= matvec(op, state[source])
                expected = dict(original)
                for i, m in enumerate(MASKS):
                    value = 0
                    for j in range(7):
                        if m >> j & 1:
                            value ^= evaluate_word(map_word("B", j, True), original["X" + str(j)])
                    expected["Y" + str(i)] ^= evaluate_word(map_word("A", i, True), value)
                require(state == expected, "dense matrix forward boundary")
                forward_cases += 1
                for op, source, target in reversed(program):
                    state[target] ^= matvec(op, state[source])
                require(state == original, "dense matrix inverse boundary")
                inverse_cases += 1
    return forward_cases, inverse_cases


def failure_controls(certificate, events, leaves):
    controls = []

    def wrong_program(name, mutant, expanded=False):
        actual = replay_leaves(mutant) if expanded else replay_root(mutant)
        require(actual != expected_rows(expanded), "mutation escaped: " + name)
        controls.append(name)

    last_b = max(i for i, e in enumerate(events) if e[0] == "B")
    wrong_program("omitted_source_restoration", events[:last_b] + events[last_b + 1:])
    first_a = next(i for i, e in enumerate(events) if e[0] == "A")
    wrong_program("omitted_readout_dirty_root", events[:first_a] + events[first_a + 1:])
    changed = [e[:] for e in events]
    changed[first_a] = ["A", (changed[first_a][1] + 1) % 63]
    wrong_program("wrong_target_and_operator", changed)
    changed = [e[:] for e in events]
    changed[last_b] = ["B", (changed[last_b][1] + 1) % 7]
    wrong_program("wrong_source_map", changed)
    wrong_program("reversed_noncommuting_factors", expand(events, reverse_factors=True), True)
    wrong_program("omitted_primitive_cleanup", leaves[:-1], True)
    for name, change in [
        ("invalid_boundary_pair", lambda c: c["readout_pairs"]["1"].__setitem__(1, 0)),
        ("missing_target_mask", lambda c: c["target_masks"].pop()),
        ("wrong_chronological_event", lambda c: c["events"].reverse()),
    ]:
        altered = json.loads(json.dumps(certificate))
        change(altered)
        try:
            validate(altered)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("mutation escaped: " + name)
    try:
        compile_product(["f", "g"], "W0", "Z")
    except ValueError:
        controls.append("scratch_alias")
    else:
        raise ValueError("scratch alias escaped")
    return controls


def run(certificate=None):
    pins = check_sources()
    certificate = read(HERE / "CERTIFICATE.json") if certificate is None else certificate
    counts, events = validate(certificate)
    original = initial_rows()
    result = replay_root(events)
    require(result == expected_rows(), "free noncommutative root boundary")
    require(replay_root(events[::-1], result) == original, "root inverse")
    stars = baseline()
    require(replay_root(stars) == result, "independent-star boundary")
    leaves = expand(events)
    expanded = replay_leaves(leaves)
    require(expanded == expected_rows(True), "expanded arbitrary-dirty boundary")
    require(replay_leaves(leaves[::-1], expanded) == original, "expanded inverse")
    require(replay_leaves(expand(stars)) == expanded, "expanded independent-star boundary")
    child_boundaries = check_completed_boundaries(events)
    actual, reference = invoice(events), invoice(stars)
    require(len(leaves) == actual["primitive_leaf_calls_fixture"], "literal leaf invoice")
    require(actual["complete_calls"] == 144 and reference["complete_calls"] == 434,
            "complete call invoice")
    forward, inverse = concrete_checks(leaves)
    controls = failure_controls(certificate, events, leaves)
    return {"schema": "seven-source-18event-result/1", "status": "PASS_SEVEN_SOURCE_18EVENT",
            "target_masks": len(MASKS), "source_events": len(certificate["source_word"]),
            "source_multiplicities": counts,
            "prefix_pair_checks": len(MASKS), "independent_interval_checks": len(MASKS),
            "formal_rows_checked": len(original), "fixture_private_dirty_rows": 2,
            "completed_child_boundaries_checked": child_boundaries,
            "dense_forward_basis_cases": forward, "dense_inverse_basis_cases": inverse,
            "shared_invoice": actual, "independent_stars_invoice": reference,
            "source_call_savings_by_map": [44 - x for x in counts],
            "root_dispatch_savings": 290, "root_descriptor_bit_savings": 1160,
            "failure_controls": controls, "interface_source_pins": pins,
            "certificate_sha256": hashlib.sha256((HERE / "CERTIFICATE.json").read_bytes()).hexdigest(),
            "program_sha256": hashlib.sha256(canonical(events)).hexdigest(),
            "expanded_program_sha256": hashlib.sha256(canonical(leaves)).hexdigest(),
            "scope": "Constructive upper bound in fixed linear F2 model; lower144 credited to PR2236, not re-enumerated; no supplier or kappa."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write receipt exclusively to a new path")
    args = parser.parse_args()
    require(args.out is None or not args.out.exists(), "output exists")
    result = run()
    if args.out is None:
        require(canonical(result) == canonical(read(HERE / "RESULT.json")), "receipt mismatch")
    else:
        with args.out.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    print(result["status"], "masks=63 source_calls=18 target_calls=126 total=144 controls=10")


if __name__ == "__main__":
    main()
