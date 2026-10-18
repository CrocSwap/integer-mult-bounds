#!/usr/bin/env python3
"""Independent finite premises for the P104 monotone-relay floor.

kumagi, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable is imported. Default replay is read-only.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WITNESS = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
FIXTURE = "research/p104-native-channel/inputs/P104-FIXTURE.json"


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def span(generators):
    out = {0}
    for v in generators:
        require(type(v) is int and 0 <= v < 512, "invalid binary label")
        out |= {w ^ v for w in tuple(out)}
    return frozenset(out)


def independent_indices(labels, indices):
    """An explicit basis witness; no numerical rank or tolerance."""
    generated, chosen = {0}, []
    for s in indices:
        if labels[s] not in generated:
            chosen.append(s)
            generated |= {v ^ labels[s] for v in tuple(generated)}
    return chosen, frozenset(generated)


def read_inputs(root):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    result = {}
    for pin in pins["files"]:
        if pin["usage"] == "input":
            raw = (root / pin["path"]).read_bytes()
            require(sha256(raw).hexdigest() == pin["sha256"], "source drift: " + pin["path"])
            result[pin["path"]] = json.loads(raw)
    require(set(result) == {WITNESS, FIXTURE}, "unexpected input inventory")
    return result[WITNESS], result[FIXTURE]


def correction_support(fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            r = [0] * 8
            r[i], r[j] = 2, 2 * sign
            roots.add(tuple(r))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    data = fixture["section4_explicit_P104"]
    removed = {tuple(r) for r in data["F0"] + data["C"]}
    require(len(roots) == 120 and len(removed) == 16 and removed <= roots,
            "invalid P104 puncture")
    ports = sorted(roots - removed)
    gram = []
    for r in ports:
        row = []
        for s in ports:
            dot = sum(a * b for a, b in zip(r, s))
            require(dot % 4 == 0, "nonintegral root pairing")
            row.append(dot // 4)
        gram.append(row)
    supports = [{s for s in range(104) if 2 * (t == s) - gram[t][s] != 0}
                for t in range(104)]
    require(all(len(s) == 48 for s in supports), "correction support size")
    return supports


def frame_trace(word):
    """Check common frames and X/Y paths; track only the X8 derivative.

    This is not a replay of the full G/2 endpoint or native phases. The one
    scalar derivative supplies an explicit excluded-descent control.
    """
    current = {r: span(f) for r, f in word["initial_frames"].items()}
    histories = {r: [current[r]] for r in current if r.startswith(("X", "Y"))}
    derivative = {r: Fraction(r == "X8") for r in current}
    descending_example = None
    for index, event in enumerate(word["program"]):
        op = event[0]
        if op == "add":
            _, dst, src, coefficient, frame = event
            require(not dst.startswith("X"), "original X is overwritten")
            require(not src.startswith("Y"), "original Y is read")
            require(current[dst] == current[src] == span(frame), "ADD frame mismatch")
            derivative[dst] += Fraction(coefficient) * derivative[src]
        elif op == "transport":
            _, reg, before, after, rank = event
            a, b = span(before), span(after)
            require(current[reg] == a and (a < b or b < a), "transport frame mismatch")
            require(abs(len(a).bit_length() - len(b).bit_length()) == rank,
                    "transport rank mismatch")
            if reg in histories:
                require(a < b, "nonmonotone data path")
                histories[reg].append(b)
            current[reg] = b
            if index == 2463:
                require(reg == "C" and b == span([243]) and derivative[reg] == -2,
                        "excluded-descent witness changed")
                descending_example = {"event_index": index, "completed_cut": index + 1,
                                      "register": reg, "source": "X8", "coefficient": "-2",
                                      "source_label": 408, "frame_generators": [243]}
        elif op == "zero":
            _, reg, frame = event
            require(reg == "C" and reg not in current, "private allocation mismatch")
            current[reg], derivative[reg] = span(frame), Fraction(0)
        elif op == "copy":
            _, dst, src, frame = event
            require(dst == "C" and not src.startswith("Y") and derivative[dst] == 0,
                    "private copy mismatch")
            require(current[dst] == current[src] == span(frame), "COPY frame mismatch")
            derivative[dst] = derivative[src]
        elif op == "erase":
            _, reg, frame = event
            require(reg == "C" and current[reg] == span(frame), "private erase mismatch")
            del current[reg], derivative[reg]
        else:
            raise Invalid("unknown event")
    require(current == {r: span(f) for r, f in word["final_frames"].items()}, "endpoint frames")
    require(descending_example is not None, "missing descent example")
    labels = []
    for s in range(104):
        path = histories[f"X{s}"]
        require(len(path[0]) == 2 and len(path[-1]) == 512, "source boundary")
        q = next(v for v in path[0] if v)
        require(all(q in f for f in path), "source label escapes frame")
        labels.append(q)
    require(labels[8] == 408 and 408 not in span([243]), "descent no longer escapes locality")
    return histories, labels, descending_example


def target_certificate(t, support, histories, labels):
    path = histories[f"Y{t}"]
    terminal = path[-1]
    require(path[0] == {0} and len(terminal) == 256, "target boundary")
    require({s for s, q in enumerate(labels) if q in terminal} == support,
            "root correction / binary frame binding")
    early = {s for s in support if any(labels[s] in f for f in path[:-1])}
    direct = {s for s in support if terminal in histories[f"X{s}"]}
    needed = sorted(support - early - direct)
    basis, generated = independent_indices(labels, needed)
    require(len(basis) == 8 and generated == terminal, "residual labels do not span target")
    # A geometric upper certificate, not a scheduled relay construction.
    hyperplanes = {}
    for normal in range(1, 512):
        kernel = frozenset(v for v in terminal if (v & normal).bit_count() % 2 == 0)
        if len(kernel) == 128:
            hyperplanes.setdefault(kernel, normal)
    require(len(hyperplanes) == 255, "target hyperplane count")
    pair = next(((a, b) for (ka, a), (kb, b) in combinations(hyperplanes.items(), 2)
                 if all(labels[s] in ka or labels[s] in kb for s in needed)), None)
    require(pair is not None, "no two-hyperplane cover")
    return {"target": t, "needed_sources": needed, "basis_sources": basis,
            "early_support_count": len(early), "direct_support_count": len(direct),
            "cover_normals": list(pair)}


def check_certificate(row, terminal, labels):
    needed, basis = row["needed_sources"], row["basis_sources"]
    require(len(basis) == 8 and set(basis) <= set(needed), "invalid basis source list")
    require(len(span(labels[s] for s in basis)) == 256, "basis does not have rank eight")
    kernels = [frozenset(v for v in terminal if (v & n).bit_count() % 2 == 0)
               for n in row["cover_normals"]]
    require(len(kernels) == 2 and all(len(k) == 128 for k in kernels), "not two hyperplanes")
    require(all(any(labels[s] in k for k in kernels) for s in needed), "incomplete cover")


def expect_rejection(operation, message):
    try:
        operation()
    except Invalid as exc:
        require(str(exc) == message, "control rejected for an unexpected reason: " + str(exc))
        return
    raise Invalid("control accepted: " + message)


def controls(word, fixture, histories, labels, rows):
    bad = deepcopy(word)
    e = next(e for e in bad["program"] if e[0] == "transport" and e[1].startswith("X"))
    e[4] += 1
    expect_rejection(lambda: frame_trace(bad), "transport rank mismatch")
    bad = deepcopy(fixture)
    bad["section4_explicit_P104"]["C"].pop()
    expect_rejection(lambda: correction_support(bad), "invalid P104 puncture")
    terminal = histories["Y0"][-1]
    bad = deepcopy(rows[0])
    bad["basis_sources"][-1] = bad["basis_sources"][0]
    expect_rejection(lambda: check_certificate(bad, terminal, labels), "basis does not have rank eight")
    bad = deepcopy(rows[0])
    bad["cover_normals"][1] = bad["cover_normals"][0]
    expect_rejection(lambda: check_certificate(bad, terminal, labels), "incomplete cover")
    support = {s for s, q in enumerate(labels) if q in terminal}
    support.remove(rows[0]["needed_sources"][0])
    expect_rejection(lambda: target_certificate(0, support, histories, labels),
                     "root correction / binary frame binding")
    # Positive relay/cancellation example: two arrivals, one target writer.
    # Helpers arrive from <1> and <2> in F2^2 with x1+d and x2-d.
    h1, h2 = [1, 0, 1], [0, 1, -1]
    merged = [a + b for a, b in zip(h1, h2)]
    require(merged == [1, 1, 0], "dirty relay cancellation")
    require(len(span([1, 2])) == 4, "merged support is not full rank")
    require(2 not in span([1]) and merged[1] != 0, "relay boundary control")
    return ["wrong_transport_rank", "missing_puncture", "dependent_basis",
            "one_hyperplane_claim", "wrong_correction_support",
            "two_arrivals_one_writer_with_dirty_cancellation",
            "retained_private_descent_escapes_support_locality"]


def calculate(root):
    word, fixture = read_inputs(root)
    supports = correction_support(fixture)
    histories, labels, descent = frame_trace(word)
    require(len({histories[f"Y{t}"][-1] for t in range(104)}) == 104,
            "terminal frames are not distinct")
    rows = [target_certificate(t, supports[t], histories, labels) for t in range(104)]
    for row in rows:
        check_certificate(row, histories[f"Y{row['target']}"][-1], labels)
    require(all(row["direct_support_count"] == 0 for row in rows), "unexpected direct source access")
    return {"schema_version": 1, "status": "PASS_P104_MONOTONE_RELAY_FLOOR_AUDIT",
            "scope": "Finite premises for the README's restricted monotone correction-network theorem; no supplier or kappa claim.",
            "target_count": 104, "distinct_terminal_frames": 104, "residual_label_rank": 8,
            "minimum_arrivals_per_target": 2, "minimum_helper_lifetimes": 208,
            "residual_support_sizes": dict(sorted(Counter(len(r["needed_sources"]) for r in rows).items())),
            "excluded_descent": descent, "controls": controls(word, fixture, histories, labels, rows),
            "targets": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="also write the verified receipt exclusively to a new path")
    args = parser.parse_args()
    result = calculate(ROOT)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    require(json.loads(payload) == json.loads((HERE / "RESULT.json").read_text()), "receipt drift")
    if args.out:
        with args.out.open("x", encoding="utf-8") as output:
            output.write(payload)
    print("PASS_P104_MONOTONE_RELAY_FLOOR_AUDIT targets=104 rank=8 arrivals=208 controls=7 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (Invalid, OSError, KeyError, TypeError, ValueError) as exc:
        raise SystemExit("FAIL: " + str(exc)) from exc
