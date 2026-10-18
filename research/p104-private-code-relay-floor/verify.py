#!/usr/bin/env python3
"""P104 private-code quotient: exact finite premises for the written proof.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Apache-2.0. No predecessor executable is imported. Default replay is read-only.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WORD = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
FIXTURE = "research/p104-native-channel/inputs/P104-FIXTURE.json"
PROFILE = {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8}


class Invalid(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Invalid(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def unique_object(pairs):
    out = {}
    for k, v in pairs:
        need(k not in out, "duplicate JSON key")
        out[k] = v
    return out


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def span(generators):
    values = {0}
    for v in generators:
        need(type(v) is int and 0 <= v < 512, "invalid binary generator")
        values |= {u ^ v for u in tuple(values)}
    return frozenset(values)


def rational_basis_indices(rows):
    """Greedy Q row elimination, returning indices in the original list."""
    echelon, chosen = {}, []
    for i, original in enumerate(rows):
        row = list(map(Q, original))
        for pivot in sorted(echelon):
            coefficient = row[pivot]
            if coefficient:
                row = [a - coefficient * b for a, b in zip(row, echelon[pivot])]
        pivot = next((j for j, value in enumerate(row) if value), None)
        if pivot is not None:
            coefficient = row[pivot]
            echelon[pivot] = [a / coefficient for a in row]
            chosen.append(i)
    return chosen


def determinant(matrix):
    """Independent fraction-free determinant of a square integer matrix."""
    a = [list(row) for row in matrix]
    n = len(a)
    need(all(len(row) == n and all(type(x) is int for x in row) for row in a),
         "determinant requires square integer matrix")
    sign, previous = 1, 1
    for k in range(n - 1):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign *= -1
        current = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = current * a[i][j] - a[i][k] * a[k][j]
                need(numerator % previous == 0, "nonexact Bareiss division")
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = current
    return sign * a[-1][-1] if n else 1


def binary_basis_indices(labels, indices):
    generated, chosen = {0}, []
    for s in indices:
        if labels[s] not in generated:
            generated |= {v ^ labels[s] for v in tuple(generated)}
            chosen.append(s)
    return chosen, frozenset(generated)


def root_ports(fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    roots.update((1, *row) for row in product((-1, 1), repeat=7)
                 if row.count(-1) % 2 == 0)
    puncture = fixture["section4_explicit_P104"]
    removed = {tuple(row) for row in puncture["F0"] + puncture["C"]}
    need(len(roots) == 120 and len(removed) == 16 and removed <= roots, "invalid puncture")
    ports = sorted(roots - removed)
    gram = [[sum(ports[s][i] * ports[s][j] for s in range(104))
             for j in range(8)] for i in range(8)]
    need(gram == [[104 * int(i == j) for j in range(8)] for i in range(8)],
         "root code Gram mismatch")
    return ports


def correction_row(ports, t):
    return [Q(t == s) - Q(sum(a * b for a, b in zip(ports[t], ports[s])), 8)
            for s in range(104)]


def code_coefficients(row, ports):
    """Coordinates in col(R), using R^T R = 104 I; reject nonmembers."""
    coefficients = [sum(row[s] * ports[s][j] for s in range(104)) / Q(104)
                    for j in range(8)]
    need(all(row[s] == sum(coefficients[j] * ports[s][j] for j in range(8))
             for s in range(104)), "source row outside root code")
    return coefficients


def add_row(destination, source, coefficient):
    for key, value in tuple(source.items()):
        result = destination.get(key, Q(0)) + coefficient * value
        if result:
            destination[key] = result
        else:
            destination.pop(key, None)


def source_projection(row):
    return [row.get(f"X{s}", Q(0)) for s in range(104)]


def serialize_row(row):
    return {k: str(v) for k, v in sorted(row.items())}


def trace(word, ports):
    """Every event and all 280 formal columns; logical and frame endpoints."""
    names = ([f"X{s}" for s in range(104)] + [f"Y{t}" for t in range(104)]
             + [f"G{i}" for i in range(32)] + [f"Q{i}" for i in range(8)]
             + [f"D{i}" for i in range(32)])
    need(set(word["initial_frames"]) == set(names), "initial register inventory")
    frames = {r: span(word["initial_frames"][r]) for r in names}
    values = {r: {r: Q(1)} for r in names}
    paths = {r: [frames[r]] for r in names if r[0] in "XY"}
    profile, operations, private = Counter(), Counter(), []
    active_private = None
    for index, event in enumerate(word["program"]):
        op = event[0]
        operations[op] += 1
        if op == "add":
            _, dst, src, coefficient, chart = event
            need(dst in values and src in values and dst != src, "invalid ADD roles")
            need(not dst.startswith("X") and not src.startswith("Y"), "data direction mismatch")
            need(frames[dst] == frames[src] == span(chart), "ADD frame mismatch")
            add_row(values[dst], values[src], Q(coefficient))
        elif op == "transport":
            _, register, before, after, rank = event
            a, b = span(before), span(after)
            need(register in frames and frames[register] == a, "transport source frame")
            need(a < b or b < a, "transport is not strict nested")
            need(type(rank) is int and rank == abs(len(a).bit_length() - len(b).bit_length()),
                 "transport rank mismatch")
            profile[rank] += 1
            if register in paths:
                need(a < b, "nonmonotone data path")
                paths[register].append(b)
            if register == "C":
                need(b < a and len(a) == 256 and len(b) == 2 and active_private is not None,
                     "private descent contract")
                need(active_private.get("copy_event") == index - 1, "private copy chronology")
                source = source_projection(values[register])
                coefficients = code_coefficients(source, ports)
                dirt = {k: v for k, v in values[register].items() if not k.startswith("X")}
                need(dirt == {f"Q{len(private)}": Q(1)}, "private dirty coefficient mismatch")
                active_private.update({"descent_event": index, "completed_cut": index + 1,
                                       "frame_generators": list(after),
                                       "code_coefficients": list(map(str, coefficients)),
                                       "dirty_row": serialize_row(dirt),
                                       "source_row": list(map(str, source))})
                private.append(active_private)
            else:
                need(a < b, "unexpected original descending transport")
            frames[register] = b
        elif op == "zero":
            _, register, chart = event
            need(register == "C" and register not in values and active_private is None,
                 "private allocation contract")
            values[register], frames[register] = {}, span(chart)
            active_private = {"allocation_event": index}
        elif op == "copy":
            _, dst, src, chart = event
            need(dst == "C" and not values[dst] and active_private is not None, "private copy contract")
            need(src == f"Q{len(private)}", "private query order")
            need(frames[dst] == frames[src] == span(chart), "COPY frame mismatch")
            values[dst] = dict(values[src])
            active_private["copy_event"] = index
        elif op == "erase":
            _, register, chart = event
            need(register == "C" and active_private is not None
                 and frames[register] == span(chart), "private erase contract")
            expected = {f"X{s}": Q(v) for s, v in enumerate(active_private["source_row"]) if Q(v)}
            expected.update({k: Q(v) for k, v in active_private["dirty_row"].items()})
            need(values[register] == expected, "private value changed after descent")
            active_private["erase_event"] = index
            del values[register], frames[register]
            active_private = None
        else:
            raise Invalid("unknown event")
    need(active_private is None and len(private) == 8, "private lifetime inventory")
    need(frames == {r: span(f) for r, f in word["final_frames"].items()}, "final frame mismatch")
    need(dict(profile) == PROFILE, "paid profile mismatch")
    need(dict(operations) == {"add": 2624, "transport": 1410, "zero": 8, "copy": 8, "erase": 8},
         "event inventory mismatch")
    for register in names:
        expected = {register: Q(1)}
        if register.startswith("Y"):
            t = int(register[1:])
            for s in range(104):
                coefficient = Q(sum(a * b for a, b in zip(ports[t], ports[s])), 8)
                if coefficient:
                    expected[f"X{s}"] = coefficient
        need(values[register] == expected, "logical endpoint mismatch: " + register)
    labels = []
    for s in range(104):
        path = paths[f"X{s}"]
        need(len(path[0]) == 2 and len(path[-1]) == 512, "source endpoint dimensions")
        label = next(x for x in path[0] if x)
        need(all(label in f for f in path), "source label lost")
        labels.append(label)
    need(len(set(labels)) == 104, "duplicate source label")
    need(len(rational_basis_indices([[Q(x) for x in p["code_coefficients"]]
                                    for p in private])) == 8, "private rows do not span code")
    summary = {"events": len(word["program"]), "independent_inputs": len(names),
               "operations": dict(sorted(operations.items())),
               "paid_profile": {str(k): profile[k] for k in sorted(profile)},
               "endpoint_rows_sha256": sha256(canonical({r: serialize_row(values[r])
                                                         for r in sorted(values)}).encode()).hexdigest()}
    return paths, labels, private, summary


def word_basis(subspace):
    generated, basis = {0}, []
    for v in sorted(subspace):
        if v not in generated:
            generated |= {u ^ v for u in tuple(generated)}
            basis.append(v)
    return basis


def target_certificate(t, ports, paths, labels):
    path = paths[f"Y{t}"]
    terminal = path[-1]
    need(path[0] == {0} and len(terminal) == 256, "target endpoint dimensions")
    correction = correction_row(ports, t)
    support = {s for s, coefficient in enumerate(correction) if coefficient}
    inside = {s for s, label in enumerate(labels) if label in terminal}
    need(support == inside and len(support) == 48, "correction support/frame binding")
    early = {s for s in support if any(labels[s] in v for v in path[:-1])}
    direct = {s for s in support if terminal in paths[f"X{s}"]}
    required = sorted(support - early - direct)
    binary_pivots, generated = binary_basis_indices(labels, required)
    need(generated == terminal and len(binary_pivots) == 8, "required support does not span endpoint")
    outside = sorted(set(range(104)) - inside)
    pivots = [outside[i] for i in rational_basis_indices([ports[s] for s in outside])]
    need(len(pivots) == 8, "code restriction outside endpoint is not injective")
    det = determinant([ports[s] for s in pivots])
    need(det != 0, "singular outside-code minor")
    return {"target": t, "terminal_generators": word_basis(terminal),
            "correction_support": sorted(support), "early_sources": sorted(early),
            "direct_sources": sorted(direct), "required_sources": required,
            "required_binary_basis": binary_pivots,
            "outside_code_basis": pivots, "outside_code_determinant": det}


def validate_target_certificate(row, ports, labels):
    """Check witnesses without repeating their greedy selection algorithm."""
    terminal = span(row["terminal_generators"])
    binary = row["required_binary_basis"]
    need(len(binary) == 8 and set(binary) <= set(row["required_sources"])
         and span(labels[s] for s in binary) == terminal, "invalid required binary witness")
    outside = row["outside_code_basis"]
    need(len(outside) == 8 and all(labels[s] not in terminal for s in outside),
         "outside witness uses an inside source")
    det = determinant([ports[s] for s in outside])
    need(det != 0 and det == row["outside_code_determinant"], "invalid outside determinant witness")


def load_inputs():
    manifest = read_json(HERE / "SOURCES.json")
    pins = {p["path"]: p for p in manifest["files"] if p["usage"] == "input"}
    need(set(pins) == {WORD, FIXTURE}, "input inventory changed")
    hashes = {}
    for path, pin in pins.items():
        digest = sha256((ROOT / path).read_bytes()).hexdigest()
        need(digest == pin["sha256"], "source hash mismatch: " + path)
        hashes[path] = digest
    return read_json(ROOT / WORD), read_json(ROOT / FIXTURE), hashes


def reject(operation, expected):
    try:
        operation()
    except Invalid as exc:
        need(str(exc) == expected, "wrong rejection: " + str(exc))
        return
    raise Invalid("control unexpectedly accepted: " + expected)


def controls(word, fixture, ports, paths, labels, private, targets):
    done = []
    bad = deepcopy(fixture)
    bad["section4_explicit_P104"]["C"].pop()
    reject(lambda: root_ports(bad), "invalid puncture")
    done.append("removed-puncture-rejects")

    bad = deepcopy(word)
    next(e for e in bad["program"] if e[0] == "transport")[4] += 1
    reject(lambda: trace(bad, ports), "transport rank mismatch")
    done.append("wrong-transport-rank-rejects")

    bad = deepcopy(word)
    next(e for e in bad["program"] if e[0] == "add" and e[1] == "Q0")[3] = 0
    reject(lambda: trace(bad, ports), "private dirty coefficient mismatch")
    done.append("missing-query-add-rejects")

    bad = deepcopy(word)
    last_add = max(i for i, e in enumerate(bad["program"]) if e[0] == "add")
    bad["program"][last_add][3] = 0
    try:
        trace(bad, ports)
    except Invalid as exc:
        need(str(exc).startswith("logical endpoint mismatch:"), "cleanup control missed endpoint")
    else:
        raise Invalid("missing cleanup accepted")
    done.append("missing-cleanup-rejects")

    row = list(map(Q, private[0]["source_row"]))
    row[0] += 1
    reject(lambda: code_coefficients(row, ports), "source row outside root code")
    done.append("one-coordinate-private-contamination-rejects")

    bad = deepcopy(targets[0])
    bad["outside_code_basis"][-1] = bad["outside_code_basis"][0]
    reject(lambda: validate_target_certificate(bad, ports, labels), "invalid outside determinant witness")
    done.append("dependent-outside-minor-rejects")

    bad = deepcopy(targets[0])
    bad["required_binary_basis"][-1] = bad["required_binary_basis"][0]
    reject(lambda: validate_target_certificate(bad, ports, labels), "invalid required binary witness")
    done.append("dependent-required-support-rejects")

    bad = deepcopy(targets[0])
    bad["outside_code_determinant"] *= -1
    reject(lambda: validate_target_certificate(bad, ports, labels), "invalid outside determinant witness")
    done.append("wrong-determinant-sign-rejects")

    # An invertible change of rational code basis must leave all104 minors intact.
    changed_ports = [(r[0] + r[1], *r[1:]) for r in ports]
    for target in targets:
        need(determinant([changed_ports[s] for s in target["outside_code_basis"]])
             == target["outside_code_determinant"], "code basis invariance")
    done.append("all104-code-basis-change-positive")

    # Ordinary support fails at the predecessor's descent; quotient membership holds.
    p = private[0]
    need(p["descent_event"] == 2463 and p["source_row"][8] == "-2"
         and labels[8] == 408 and labels[8] not in span(p["frame_generators"]),
         "private escape example changed")
    code_coefficients(list(map(Q, p["source_row"])), ports)
    done.append("private-support-escape-quotient-positive")

    # Granting C_0 itself as a free oracle permits its direct zero-arrival write.
    c = correction_row(ports, 0)
    reject(lambda: code_coefficients(c, ports), "source row outside root code")
    need({s for s, x in enumerate(c) if x} == set(targets[0]["correction_support"]),
         "outside-code oracle countermodel support")
    augmented = [[Q(ports[s][j]) for s in range(104)] for j in range(8)] + [c]
    need(len(rational_basis_indices(augmented)) == 9, "oracle countermodel did not enlarge code")
    done.append("outside-code-oracle-zero-arrival-countermodel")

    # A nonzero endpoint-supported codeword destroys unique local representatives.
    toy_code = [Q(1), Q(1), Q(0)]
    need(any(toy_code[:2]) and toy_code[2] == 0, "toy injectivity countermodel")
    need([toy_code[i] - toy_code[i] for i in range(3)] == [0, 0, 0], "toy cancellation")
    done.append("noninjective-code-support-countermodel")
    return done


def compute():
    word, fixture, hashes = load_inputs()
    ports = root_ports(fixture)
    paths, labels, private, summary = trace(word, ports)
    targets = [target_certificate(t, ports, paths, labels) for t in range(104)]
    need(len({span(t["terminal_generators"]) for t in targets}) == 104,
         "target endpoints are not distinct")
    for target in targets:
        validate_target_certificate(target, ports, labels)
    checked_controls = controls(word, fixture, ports, paths, labels, private, targets)
    return {"schema_version": 1, "claim": "208-monotone-lifetimes-with-free-root-code",
            "source_sha256": hashes, "trace": summary, "source_code_dimension": 8,
            "private_source_rank": 8, "private_lifetimes": private, "targets": targets,
            "required_source_count_histogram": dict(sorted(Counter(str(len(t["required_sources"]))
                                                                       for t in targets).items())),
            "helper_lifetime_floor": 208, "controls": checked_controls,
            "scope": "written scoped proof plus exact finite premises; no new kappa"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write verified receipt exclusively to a new file")
    args = parser.parse_args()
    actual = compute()
    need(canonical(actual) == canonical(read_json(HERE / "RESULT.json")), "receipt mismatch")
    if args.out:
        with args.out.open("x", encoding="utf-8") as stream:
            json.dump(actual, stream, indent=2, sort_keys=True)
            stream.write("\n")
    digest = sha256(canonical(actual).encode()).hexdigest()
    print("PASS_P104_PRIVATE_CODE_RELAY_FLOOR targets=104 private=8 code_rank=8"
          f" lifetimes=208 controls={len(actual['controls'])} no_new_kappa receipt_sha256={digest}")


if __name__ == "__main__":
    main()
