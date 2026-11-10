#!/usr/bin/env python3
"""Independent reverse-functional audit of the literal balanced caller.

The evaluator uses integer Laurent polynomials and imports no source generator,
source checker or separate oracle. Pullback is a transpose, not a Hermitian
adjoint or the inverse of the caller.
"""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha1, sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINNED = {
    "sources/CONTROLLER.json": [
        "6fd67eaabe659956d6694471d3fd7d2824c0a4a79cf3b8f22922f7189b11b91f",
        "1f2e375b24aba5fb25580dfea7fab7a2049f3eb8"
    ],
    "sources/controller-source.py": [
        "8067ade84815b54d539cbaef9885db9fa4d7a23fdde2e683451d317038a8477c",
        "3b4bf82eba05d57ef4bb1fd934e8ca65780425c1"
    ],
    "sources/upstream-PROOF.md": [
        "1fab54bc665bf6882f0bbd772af15fbf69a92eac040951ccd19a5accf02f328e",
        "08dd3e35b0bdd5a6e39f88183b2793c6bb5af6ca"
    ],
    "sources/NOTICE": [
        "c0aec2bb7b305c49c8630a801f0ef2d5286cde81025471cc384990440577ad79",
        "af80ac5d2929d3a3e4ea90c9cf3141d63d358b0c"
    ],
    "sources/module-check-source.py": [
        "a30e70fe1313f125b276ec97e05c779ff80b6d1aa9f6ba918a61bfb9bb5a2eda",
        "f394d40ea2e0777f77910cc5a4b1d151c1228cbc"
    ]
}
ROLES, STAGES = 34, 19
ZERO = (0, ())
EXPECTED_COUNTS = {"SWAP": 103, "ADD": 112, "QUERY": 16, "IDLE": 16,
                   "SCALE": 67, "LOCAL": 19, "Q_POWER": 20}
MAX_ROW_TERMS = 8192
MAX_CELL_TERMS = 2048


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def authenticated_controller():
    raw_files = {}
    for name, (digest, blob) in PINNED.items():
        raw = (HERE / name).read_bytes()
        require(sha256(raw).hexdigest() == digest, "source SHA256: " + name)
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
                "source Git blob: " + name)
        raw_files[name] = raw
    return json.loads(raw_files["sources/CONTROLLER.json"])


def integer(value, lower, upper, message):
    require(type(value) is int and lower <= value < upper, message)


def role(value):
    integer(value, 0, ROLES, "caller role")


def stage_set(values):
    require(type(values) is list and values and len(values) == len(set(values)), "nonempty distinct stage set")
    for value in values:
        integer(value, 1, STAGES + 1, "stage label")


def validate_events(events):
    require(type(events) is list and len(events) <= 353, "bounded literal events")
    for event in events:
        require(type(event) is list and event and type(event[0]) is str, "literal instruction")
        op = event[0]
        if op in ("ADD", "QUERY"):
            require(len(event) == 4, "binary instruction shape")
            role(event[1]); role(event[2])
            require(event[1] != event[2], "distinct binary roles")
            require(type(event[3]) is int and event[3] in (-1, 1), "unit signed coefficient/exponent")
        elif op in ("SCALE", "Q_POWER"):
            require(len(event) == 3, "unary instruction shape")
            role(event[1])
            allowed = (-1, 1) if op == "SCALE" else (-2, 2)
            require(type(event[2]) is int and event[2] in allowed, "ordinary scalar/exponent")
        elif op == "SWAP":
            require(len(event) == 3, "swap shape")
            role(event[1]); role(event[2])
            require(event[1] != event[2], "distinct swap roles")
        elif op == "LOCAL":
            require(len(event) == 4, "local instruction shape")
            integer(event[1], 1, STAGES + 1, "local stage label")
            role(event[2]); role(event[3])
            require(event[2] != event[3], "distinct local roles")
        elif op == "IDLE":
            require(len(event) == 4, "idle instruction shape")
            role(event[1]); role(event[2])
            require(event[1] != event[2], "distinct idle roles")
            stage_set(event[3])
        else:
            raise ValueError("unknown caller opcode")


def validate_controller(word):
    require(type(word) is dict and set(word) ==
            {"schema", "roles", "stages", "ambient_rank", "tree", "nodes", "events", "diagonal"},
            "exact controller schema")
    require(word["schema"] == "binary-query-tree/1", "controller schema version")
    require(type(word["roles"]) is int and word["roles"] == ROLES and
            type(word["stages"]) is int and word["stages"] == STAGES and
            type(word["ambient_rank"]) is int and word["ambient_rank"] == 161, "fixed caller inventory")
    validate_events(word["events"])
    require(len(word["events"]) == 353 and dict(Counter(e[0] for e in word["events"])) == EXPECTED_COUNTS,
            "complete opcode inventory")
    require(sorted(e[1] for e in word["events"] if e[0] == "LOCAL") == list(range(1, STAGES + 1)),
            "nineteen distinct local stages")
    def leaves(tree):
        if type(tree) is int:
            require(tree == 1, "tree leaf")
            return 1
        require(type(tree) is list and len(tree) == 2, "binary subtree")
        return leaves(tree[0]) + leaves(tree[1])
    require(type(word["tree"]) is list and len(word["tree"]) == 3 and
            [leaves(t) for t in word["tree"]] == [4, 7, 8], "fixed root leaf counts")
    require(type(word["nodes"]) is list and len(word["nodes"]) == 16, "sixteen internal nodes")
    target_annotations = {0: (1, list(range(1, 20))), 1: (-1, list(range(1, 20)))}
    expected_idle, expected_query = [], []
    for node in word["nodes"]:
        require(type(node) is dict and set(node) == {"roles", "stages", "exponent"}, "node annotation")
        require(type(node["roles"]) is list and len(node["roles"]) == 2, "node role pair")
        a, b = node["roles"]
        role(a); role(b)
        require(a >= 2 and b >= 2 and a != b and a not in target_annotations and b not in target_annotations,
                "disjoint arbitrary node input pairs")
        stage_set(node["stages"])
        require(type(node["exponent"]) is int and node["exponent"] in (-1, 1), "node orientation")
        target_annotations[a] = (-node["exponent"], node["stages"])
        target_annotations[b] = (node["exponent"], node["stages"])
        expected_idle.append((a, b, tuple(node["stages"])))
        expected_query.append((a, b, -node["exponent"]))
    require(set(target_annotations) == set(range(ROLES)), "every arbitrary field has a target annotation")
    require(sorted((e[1], e[2], tuple(e[3])) for e in word["events"] if e[0] == "IDLE") == sorted(expected_idle),
            "one charged paired idle per node")
    require(sorted(tuple(e[1:]) for e in word["events"] if e[0] == "QUERY") == sorted(expected_query),
            "one oriented thin query per node")
    require(type(word["diagonal"]) is list and len(word["diagonal"]) == ROLES, "target diagonal rows")
    for index, row in enumerate(word["diagonal"]):
        require(type(row) is list and len(row) == 21 and all(type(x) is int for x in row),
                "integer 21-slot target annotation")
        exponent, labels = target_annotations[index]
        expected = [exponent, 0] + [int(stage in labels) for stage in range(1, STAGES + 1)]
        require(row == expected, "literal diagonal matches node target annotations")


def shifted(poly, central=0, stages=()):
    return {(q + central, tuple(sorted(labels + tuple(stages)))): coefficient
            for (q, labels), coefficient in poly.items()}


def plus(left, right, coefficient=1):
    result = dict(left)
    for key, value in right.items():
        updated = result.get(key, 0) + coefficient * value
        if updated:
            result[key] = updated
        else:
            result.pop(key, None)
    return result


def pullback(events, output, statistics):
    weights = [{} for _ in range(ROLES)]
    weights[output] = {ZERO: 1}
    for event in reversed(events):
        op = event[0]
        if op == "ADD":
            _, dst, src, coefficient = event
            weights[src] = plus(weights[src], weights[dst], coefficient)
        elif op == "QUERY":
            _, dst, src, exponent = event
            weights[src] = plus(weights[src], shifted(weights[dst], central=exponent))
        elif op == "SCALE":
            weights[event[1]] = {key: event[2] * value for key, value in weights[event[1]].items()}
        elif op == "SWAP":
            a, b = event[1:]
            weights[a], weights[b] = weights[b], weights[a]
        elif op == "LOCAL":
            _, stage, src, dst = event
            # Preserve both post-event weights. Forward LOCAL first shears,
            # then scales both fields; pullback reverses that chronology.
            old_src, old_dst = weights[src], weights[dst]
            scaled_src = shifted(old_src, stages=(stage,))
            scaled_dst = shifted(old_dst, stages=(stage,))
            weights[src] = plus(scaled_src, shifted(scaled_dst, central=-1))
            weights[dst] = scaled_dst
        elif op == "IDLE":
            _, a, b, labels = event
            weights[a] = shifted(weights[a], stages=labels)
            weights[b] = shifted(weights[b], stages=labels)
        else:
            require(op == "Q_POWER", "known pullback instruction")
            weights[event[1]] = shifted(weights[event[1]], central=event[2])
        total = sum(map(len, weights))
        peak_cell = max(map(len, weights))
        require(total <= MAX_ROW_TERMS and peak_cell <= MAX_CELL_TERMS, "bounded sparse Laurent terms")
        statistics["peak_row_terms"] = max(statistics["peak_row_terms"], total)
        statistics["peak_cell_terms"] = max(statistics["peak_cell_terms"], peak_cell)
    return weights


def endpoint(events):
    validate_events(events)
    statistics = {"peak_row_terms": 0, "peak_cell_terms": 0}
    return [pullback(events, output, statistics) for output in range(ROLES)], statistics


def expected_matrix(word):
    matrix = [[{} for _ in range(ROLES)] for _ in range(ROLES)]
    for role, annotation in enumerate(word["diagonal"]):
        labels = tuple(stage for stage, exponent in enumerate(annotation[2:], 1) for _ in range(exponent))
        matrix[role][role] = {(annotation[0], labels): 1}
    return matrix


def exponents(monomial):
    central, labels = monomial
    return (central,) + tuple(labels.count(stage) for stage in range(1, STAGES + 1))


def encoded_cell(cell):
    return [[coefficient, list(exponent)] for exponent, coefficient in
            sorted((exponents(key), value) for key, value in cell.items())]


def encoded_matrix(matrix):
    return [[encoded_cell(cell) for cell in row] for row in matrix]


def first_difference(actual, expected):
    for output in range(ROLES):
        for input_role in range(ROLES):
            a, b = actual[output][input_role], expected[output][input_role]
            for key in sorted(a.keys() | b.keys(), key=exponents):
                if a.get(key, 0) != b.get(key, 0):
                    return {"output": output, "input": input_role, "exponents": list(exponents(key)),
                            "actual": a.get(key, 0), "expected": b.get(key, 0)}
    return None


def determinant_from_events(events):
    sign, central, stage_powers = 1, 0, [0] * STAGES
    for event in events:
        op = event[0]
        if op == "SWAP":
            sign *= -1
        elif op == "SCALE":
            sign *= event[2]
        elif op == "Q_POWER":
            central += event[2]
        elif op == "LOCAL":
            stage_powers[event[1] - 1] += 2
        elif op == "IDLE":
            for stage in event[3]:
                stage_powers[stage - 1] += 2
    return {"coefficient": sign, "exponents": [central] + stage_powers}


def controls(word, target):
    modifications = [
        ("missing_paid_idle", "IDLE", "remove"),
        ("missing_ordinary_translation", "Q_POWER", "remove"),
        ("missing_thin_query", "QUERY", "remove"),
        ("wrong_query_orientation", "QUERY", "sign"),
        ("wrong_scalar_add_sign", "ADD", "sign"),
        ("changed_idle_stage_set", "IDLE", "stage_set"),
        ("aliased_local_stage", "LOCAL", "stage"),
    ]
    result = {}
    for label, opcode, action in modifications:
        events = deepcopy(word["events"])
        index = next(i for i, event in enumerate(events) if event[0] == opcode)
        original = deepcopy(events[index])
        if action == "remove":
            del events[index]
            replacement = None
        elif action == "sign":
            events[index][-1] *= -1
            replacement = events[index]
        elif action == "stage_set":
            previous = events[index][3]
            other = next(stage for stage in range(1, STAGES + 1) if stage not in previous)
            events[index][3] = sorted(previous[1:] + [other])
            replacement = events[index]
        else:
            events[index][1] = events[index][1] % STAGES + 1
            replacement = events[index]
        # Structural instruction grammar is checked, but original inventory is
        # deliberately not imposed on a changed word. The endpoint itself fails.
        matrix, _ = endpoint(events)
        witness = first_difference(matrix, target)
        require(witness is not None, "semantic coefficient control accepted: " + label)
        result[label] = {"event_index": index, "original": original, "replacement": replacement,
                         "coefficient_witness": witness}
    return result


def run():
    word = authenticated_controller()
    validate_controller(word)
    target = expected_matrix(word)
    actual, statistics = endpoint(word["events"])
    require(first_difference(actual, target) is None, "all1156 exact Laurent endpoint cells")
    determinant = determinant_from_events(word["events"])
    expected_determinant = {"coefficient": 1,
                            "exponents": [sum(row[0] for row in word["diagonal"])] +
                            [sum(row[stage + 1] for row in word["diagonal"]) for stage in range(1, STAGES + 1)]}
    require(determinant == expected_determinant, "event determinant matches target diagonal product")
    matrix = encoded_matrix(actual)
    matrix_sha = sha256((canonical(matrix) + "\n").encode()).hexdigest()
    diagonal = [{"output": role, "input": role, "coefficient": 1,
                 "exponents": list(exponents(next(iter(actual[role][role]))))} for role in range(ROLES)]
    return {"schema_version": 1, "scope": "literal353-instruction34-field formal Laurent endpoint",
            "ring": "Z[Q^+/-1,D1^+/-1,...,D19^+/-1], with no finite-order quotient",
            "roles": ROLES, "stages": STAGES, "events": len(word["events"]),
            "opcode_counts": EXPECTED_COUNTS, "coefficient_cells": ROLES * ROLES,
            "nonzero_cells": ROLES, "nonzero_terms": ROLES, "matrix_sha256": matrix_sha,
            "diagonal": diagonal, "determinant": determinant, "sparsity": statistics,
            "controls": controls(word, target),
            "limits": ["The source full-call, thin-query and idle operator contracts are hypotheses.",
                       "No physical contact, native absolute-phase, spectator, erasure or ordinary-work admission follows.",
                       "No new caller construction, kappa, uniform compiler or multiplication theorem is claimed."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit fresh JSON without retained-result comparison")
    options = parser.parse_args()
    result = run()
    if not options.emit:
        retained = HERE / "RESULT.json"
        require(retained.is_file(), "retained RESULT.json receipt must exist")
        require(canonical(json.loads(retained.read_bytes())) == canonical(result),
                "exact typed retained RESULT.json receipt")
    print(json.dumps(result, sort_keys=True, indent=2))
