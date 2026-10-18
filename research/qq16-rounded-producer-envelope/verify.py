#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Positive, noise-aware completed-operation ledger for the two QQ16 stages.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
Native isometry semantics are inherited; no native operator is replaced by
identity in a signed physical-state calculation. This is a norm majorant.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CATEGORIES = ("add", "scale", "child", "adapter", "map")
WIDTH = 712
PERSISTENT = 704
CERT = "research/joint-query/certificate.json.gz"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read_json(path, limit=2_000_000):
    raw = path.read_bytes()
    require(len(raw) <= limit, "oversize JSON: " + str(path))
    return json.loads(raw)


def load():
    sources = read_json(HERE / "SOURCES.json")
    for item in sources["files"]:
        if item["usage"] == "input":
            raw = (ROOT / item["path"]).read_bytes()
            require(len(raw) <= 16_000_000, "oversize source")
            require(hashlib.sha256(raw).hexdigest() == item["sha256"],
                    "source hash: " + item["path"])
    with gzip.open(ROOT / CERT, "rb") as stream:
        raw = stream.read(16_000_001)
    require(len(raw) <= 16_000_000, "oversize certificate payload")
    packet = json.loads(raw)
    require(packet["schema"] == "conserved-qq16-full-cover-native-words-v1",
            "source schema")
    return packet


def wire(token):
    require(isinstance(token, list) and len(token) == 2, "register token")
    kind, index = token
    require(type(index) is int and kind in ("L", "C"), "register type")
    require(0 <= index < (704 if kind == "L" else 8), "register index")
    return index + (704 if kind == "C" else 0)


def expand(packet, name):
    result = []
    for event in packet["programs"][name]:
        if event[0] == "retained_core":
            expected = "forward" if name == "F_0" else "backward"
            require(event[1] == expected, "core orientation")
            result.extend(packet["core_words"][expected])
        elif event[0] == "private_sweep":
            body = event[2]
            require(body and all(e[0] in ("scalar", "native_line") for e in body),
                    "private sweep must be owner-local")
            require(body[0][0] == body[-1][0] == "scalar" and
                    body[0][1] == body[-1][1] == ["clear", ["C", 0]],
                    "private sweep needs first/last C0 CLEAR")
            result.extend(body)
        elif event[0] == "cover_sweep":
            result.extend(event[2])
        else:
            result.append(event)
    require(len(result) <= 28_000, "event bound")
    return result


def operation(event):
    """Return kind, target, source, absolute coefficient, defect category."""
    kind = event[0]
    if kind == "phase":
        return ("marker", -1, -1, Q(0), None)
    if kind == "scalar":
        gate = event[1]
        d = wire(gate[1])
        if gate[0] == "clear":
            require(len(gate) == 2 and d >= 704, "owned CLEAR only")
            return ("clear", d, -1, Q(0), None)
        if gate[0] == "scale":
            require(len(gate) == 4 and gate[2] != 0, "SCALE syntax")
            return ("scale", d, -1, abs(Q(gate[2], gate[3])), "scale")
        require(gate[0] == "add" and len(gate) == 5, "ADD syntax")
        s = wire(gate[2])
        require(s != d and gate[3] != 0, "nonzero distinct-source ADD")
        return ("add", d, s, abs(Q(gate[3], gate[4])), "add")
    if kind in ("native_line", "cover_map"):
        return ("isometry", wire(event[1]), -1, Q(1),
                "child" if kind == "native_line" else "map")
    require(kind in ("climb", "adapter", "residual_adapter"), "unknown event")
    d = event[2]
    require(type(d) is int and 0 <= d < 704, "native target")
    return ("isometry", d, -1, Q(1), "child" if kind == "climb" else "adapter")


def row_record(index, d, p, j, degree):
    return {"event": index, "wire": d, "P": str(p[d]),
            "J": str(sum(j[d])), "degree": degree[d],
            "J_by_category": dict(zip(CATEGORIES, map(str, j[d])))}


def stage(events, trace=None):
    """At z=1 compute each positive path polynomial and its derivatives."""
    p = [Q(1)] * 704 + [Q(0)] * 8
    j = [[Q(0) for _ in CATEGORIES] for _ in range(WIDTH)]
    degree = [0] * WIDTH
    initialized = [True] * 704 + [False] * 8
    maxima = {"P": row_record(-1, 0, p, j, degree),
              "J": row_record(-1, 0, p, j, degree)}
    counts, categories = Counter(), Counter()
    digest, simple_digest = hashlib.sha256(), hashlib.sha256()
    changed, degree_max = 0, 0
    for index, event in enumerate(events):
        kind, d, s, c, category = operation(event)
        counts[event[0]] += 1
        if kind == "marker":
            continue
        changed += 1
        if kind == "clear":
            p[d], j[d], degree[d], initialized[d] = Q(0), [Q(0)] * 5, 0, True
        else:
            require(initialized[d] and (s < 0 or initialized[s]), "uninitialized read")
            categories[category] += 1
            if kind == "add":
                p[d] += c * p[s]
                j[d] = [a + c * b for a, b in zip(j[d], j[s])]
                degree[d] = max(degree[d], degree[s])
            elif kind == "scale":
                p[d] *= c
                j[d] = [c * a for a in j[d]]
            j[d][CATEGORIES.index(category)] += p[d]
            degree[d] = degree[d] + 1 if p[d] else 0
        record = row_record(index, d, p, j, degree)
        if trace is not None:
            trace.append(record)
        digest.update(encoded(record) + b"\n")
        simple_digest.update(encoded([index, d, record["P"], record["J"]]) + b"\n")
        for label in ("P", "J"):
            if Q(record[label]) > Q(maxima[label][label]):
                maxima[label] = record
        degree_max = max(degree_max, degree[d])
    require(all(initialized), "private initialization coverage")
    require(all(p[d] == 0 and sum(j[d]) == 0 for d in range(704, 712)),
            "private fields must finish at exact zero")
    terminals = {}
    for name, lo, hi in (("data", 0, 224), ("helpers", 224, 704)):
        d = max(range(lo, hi), key=lambda i: sum(j[i]))
        terminals[name] = row_record(len(events) - 1, d, p, j, degree)
    return {"events": len(events), "changed_cuts": changed, "event_counts": dict(counts),
            "defect_category_counts": dict(categories),
            "defect_sites": changed - sum(
                e[0] == "scalar" and e[1][0] == "clear" for e in events),
            "clear_sites": sum(e[0] == "scalar" and e[1][0] == "clear" for e in events),
            "event_sha256": hashlib.sha256(encoded(events)).hexdigest(),
            "cut_table_sha256": digest.hexdigest(), "degree_max": degree_max,
            "P_J_cut_table_sha256": simple_digest.hexdigest(),
            "all_cut": maxima, "terminal": terminals}


def ceil_log2(value):
    value = Q(value)
    require(value > 0, "positive logarithm argument")
    k = value.numerator.bit_length() - value.denominator.bit_length()
    power = Q(2) ** k
    return k if power >= value else k + 1


def endpoint_calibration(packet):
    """Check the geometry used by the inherited ideal F0 endpoint bound 58."""
    a, t, ordinary = packet["A_ports"], packet["T_ports"], packet["U_ports"]
    require(len(a) == len(t) == 8 and len(ordinary) == 96, "port class sizes")
    require(sorted(a + t + ordinary) == list(range(112)), "port partition")
    r = [{int(i): Q(v) for i, v in row.items()} for row in packet["R_rows"]]
    k = [{int(i): Q(v) for i, v in row.items()} for row in packet["K_rows"]]
    require(len(r) == 8 and len(k) == 112, "R/K dimensions")
    for port, row in enumerate(k):
        require(row == {i: r[i][port] / 4 for i in range(8) if port in r[i]}, "K=R*/4")
        require(sum(map(abs, row.values())) == 1, "K absolute row sum")
    for section in (a, t):
        for i in range(8):
            require(sum(abs(r[i].get(p, 0)) for p in section) == 4, "selected row sum")
            for j in range(8):
                require(sum(r[i].get(p, 0) * r[j].get(p, 0) for p in section)
                        == (4 if i == j else 0), "section identity")
    query = [sum(map(abs, row.values())) for row in r]
    require(query == [56] * 8, "full query row sums")
    x = [sum(abs(c) * (4 if p in a else query[i]) for i, c in row.items())
         + (1 if p in ordinary else 0) for p, row in enumerate(k)]
    y = [value + (1 if p in ordinary else 2) for p, value in enumerate(x)]
    require(max(x + y) == 58, "inherited F0 endpoint majorant")
    return {"F_data_norm_over_H": "58", "K_row_sum": "1", "R_row_sum": "56",
            "X_A_T_U": ["4", "56", "57"], "Y_A_T_U": ["6", "58", "58"]}


def result(packet):
    cases = {name: stage(expand(packet, name)) for name in ("F_0", "B_1_2")}
    j = {name: max(Q(r["J"]) for r in case["terminal"].values())
         for name, case in cases.items()}
    f_offset, b_offset = 9 + ceil_log2(j["F_0"]), 20 + ceil_log2(j["B_1_2"])
    count_guard = ceil_log2(2 * max(c["defect_sites"] for c in cases.values()))
    return {"schema": "qq16-rounded-producer-envelope-v1", "cases": cases,
            "ideal_endpoint_calibration": endpoint_calibration(packet),
            "composition": {"F_persistent_J": str(j["F_0"]),
                            "B_persistent_J": str(j["B_1_2"]),
                            "F_tolerance_offset": f_offset, "B_tolerance_offset": b_offset,
                            "count_guard": count_guard,
                            "common_relative_offset": max(f_offset, b_offset, count_guard),
                            "F_entry_bound": "2^delta H", "B_entry_bound": "2^(delta+6) H",
                            "decoded_error_ratio": str(Q(49, 256) + Q(1923, 8192) + Q(1, 2))}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="create a new receipt, never overwrite")
    args = parser.parse_args()
    report = result(load())
    if args.write:
        with args.write.open("x") as stream:
            stream.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        require(encoded(report) == encoded(read_json(HERE / "RESULT.json")), "receipt mismatch")
    cuts = sum(case["changed_cuts"] for case in report["cases"].values())
    print("PASS_QQ16_ROUNDED_PRODUCER_ENVELOPE",
          "stages=2", "cuts=" + str(cuts), "offset=" + str(report["composition"]["common_relative_offset"]),
          "conditional_completed_operations no_new_kappa")


if __name__ == "__main__":
    main()
