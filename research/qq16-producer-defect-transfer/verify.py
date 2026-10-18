#!/usr/bin/env python3
"""Certify QQ16 endpoint sensitivity. Nick Petalas; Apache-2.0.

Native semantics are inherited. No predecessor executable is imported.
"""

import argparse
import gzip
import hashlib
import io
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_PIN = "d9e1681b7c7163cf302aa9bb56b71ab963404cc9bcf99a0b0bb597180fcc2f43"
PORTS = 112
MAX_ROW = 50_000
MAX_STATE = 600_000
INPUTS = tuple(f"{c}{p}" for c in "XY" for p in range(PORTS))
OUTPUTS = tuple(f"{c}{p}" for c in "ZW" for p in range(PORTS))
SCRATCH = tuple(f"{c}{p}" for c in "FG" for p in range(8))
SHAPES = {"clear": 3, "add": 4, "line": 4, "map": 5,
          "begin": 3, "end": 3, "checkpoint": 2}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path, maximum):
    need(path.is_file() and not path.is_symlink(), f"not a plain file: {path}")
    with path.open("rb") as stream:
        raw = stream.read(maximum + 1)
    need(len(raw) <= maximum, f"input capacity: {path}")
    return raw


def unique(pairs):
    need(len(pairs) <= 4096, "JSON object capacity")
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sources():
    raw = read(HERE / "SOURCES.json", 16_384)
    need(hashlib.sha256(raw).hexdigest() == SOURCE_PIN, "source inventory drift")
    payloads = {}
    for item in decode(raw)["files"]:  # Digest fixes the inventory size.
        if item["usage"] != "input":
            continue
        data = read(ROOT / item["path"], 1_048_576)
        need(hashlib.sha256(data).hexdigest() == item["sha256"], "source drift")
        header = f"blob {len(data)}\0".encode()
        need(hashlib.sha1(header + data).hexdigest() == item["git_blob"], "blob drift")
        payloads[item["path"]] = data
    with gzip.GzipFile(fileobj=io.BytesIO(
            payloads["research/joint-query/certificate.json.gz"])) as stream:
        data = stream.read(12_582_913)
    need(len(data) <= 12_582_912, "decoded certificate capacity")
    packet = decode(data)
    word = decode(payloads["research/qq16-line-normalized-decoder/WORD.json"])
    need(type(word) is list and len(word) == 3823, "literal word size")
    return packet, word


def geometry(packet):
    a, t, u = (packet[k] for k in ("A_ports", "T_ports", "U_ports"))
    need(len(a) == len(t) == 8 and len(u) == 96, "partition sizes")
    need(sorted(a + t + u) == list(range(PORTS)), "partition coverage")
    r = [{int(j): Q(c) for j, c in row.items()} for row in packet["R_rows"]]
    k = [{int(j): Q(c) for j, c in row.items()} for row in packet["K_rows"]]
    need(len(r) == 8 and len(k) == PORTS, "R/K shapes")
    for row in r:
        need(set(row) <= set(range(PORTS)), "R coordinates")
        need(all(c in (-1, 1) for c in row.values()), "R signs")
        need([sum(j in row for j in part) for part in (a, t, u)] == [4, 4, 48],
             "query support by partition")
    for j, row in enumerate(k):
        need(row == {i: r[i][j] / 4 for i in range(8) if j in r[i]}, "K=R*/4")
        need(sum(abs(c) for c in row.values()) == 1, "section norm")
    for part in (a, t):
        for i in range(8):
            for j in range(8):
                need(sum(r[i].get(p, 0) * r[j].get(p, 0) for p in part)
                     == (4 if i == j else 0), "orthogonal selected minor")
    return {"A": a, "T": t, "U": u, "R_support": [4, 4, 48],
            "section_l1": 1, "F0_forward_bound": 58, "B1_forward_bound": 312}


def add(dest, source, coefficient):
    for key, value in source.items():
        updated = dest.get(key, Q(0)) + coefficient * value
        need(abs(updated.numerator) <= 2**32 and updated.denominator <= 256,
             "coefficient capacity")
        if updated:
            dest[key] = updated
        else:
            dest.pop(key, None)
    need(len(dest) <= MAX_ROW, "polynomial row capacity")


def mapped(row, token):
    result = {}
    for (source, path), value in row.items():
        route = path[1:] if path and path[0] == token else (token,) + path
        need(len(route) <= 4, "operator degree capacity")
        key = (source, route)
        need(key not in result, "involution must permute reduced words")
        result[key] = value
    return result


def validate(event, state, active):
    need(type(event) is list and bool(event), "invalid event")
    op = event[0]
    need(type(op) is str and op in SHAPES, "event opcode")
    need(len(event) == SHAPES[op] and type(event[1]) is str, "event shape")
    if op in ("begin", "end"):
        need(type(event[2]) is int and event[2] in (8, 16), "scope capacity")
        if op == "begin":
            need(active is None, "overlapping scope")
            return (event[1], event[2])
        need(active == (event[1], event[2]), "scope mismatch")
        need(all(not state.get(name) for name in SCRATCH), "scratch leak")
        for name in SCRATCH:
            state.pop(name, None)
        return None
    if op == "checkpoint":
        need(active is None and event[1] == "original_F0_outputs", "checkpoint")
        return active
    dest = event[1]
    need(dest in OUTPUTS or (dest in SCRATCH and active), "borrowed/illegal write")
    need(op == "clear" or dest in state, "dirty destination read")
    if op == "clear":
        need(type(event[2]) is str, "clear frame")
    elif op == "add":
        need(type(event[2]) is str and event[2] in state and event[2] != dest,
             "invalid ADD source")
        need(event[3] in ("1", "-1", "1/4", "-1/4"), "ADD coefficient")
    elif op == "line":
        need(type(event[2]) is int and 0 <= event[2] < PORTS, "line port")
        need(type(event[3]) is int and event[3] in (-1, 1), "line sign")
    elif op == "map":
        need(type(event[2]) is int and event[2] in (1, 2), "map stage")
        need(type(event[3]) is int and 0 <= event[3] < PORTS, "map port")
        need(type(event[4]) is bool, "map inverse flag")
    return active


def replay(word, names):
    need(len(word) <= 3823 and len(names) == 224, "replay capacity")
    state = {name: {(i, ()): Q(1)} for i, name in enumerate(names)}
    active, peak = None, 224
    for event in word:
        active = validate(event, state, active)
        op = event[0]
        if op == "clear":
            state[event[1]] = {}
        elif op == "add":
            add(state[event[1]], state[event[2]], Q(event[3]))
        elif op == "map":
            token = (event[2] - 1) * PORTS + event[3]
            state[event[1]] = mapped(state[event[1]], token)
        # Native lines change physical chart, preserving represented logical value.
        live = sum(len(row) for row in state.values())
        need(live <= MAX_STATE, "live term capacity")
        peak = max(peak, live)
    need(active is None and all(name in state for name in OUTPUTS), "final state")
    return [state[name] for name in OUTPUTS], peak


def summaries(rows):
    result = []
    for i, row in enumerate(rows):
        terms = [[source, list(path), str(c)] for (source, path), c in sorted(row.items())]
        result.append({"row": i, "l1": str(sum(abs(c) for c in row.values())),
                       "terms": len(row), "sha256": hashlib.sha256(canonical(terms)).hexdigest()})
    return result


def controls(rows):
    sample = {(0, ()): Q(1), (1, (0,)): Q(-2)}
    need(mapped(mapped(sample, 0), 0) == sample, "double involution control")
    need(mapped(mapped(sample, 1), 0) != mapped(mapped(sample, 0), 1),
         "noncommuting route control")
    cancelled = sample.copy()
    add(cancelled, sample, Q(-1))
    need(cancelled == {}, "exact cancellation control")
    peak = max(rows, key=lambda row: sum(abs(c) for c in row.values()))
    need(all(not path for _, path in peak), "F0 is owner-local")
    # A common unit payload with these input signs attains the maximum row norm.
    witness = {source: 1 if c > 0 else -1 for (source, _), c in peak.items()}
    attained = sum(c * witness[source] for (source, _), c in peak.items())
    need(attained == 49, "sharp F0 coherent-error witness")
    need(Q(49, 256) + Q(1923, 8192) + Q(1, 2) == Q(7587, 8192), "budget")
    need(18096 + Q(312, 256) + Q(1, 8192) < 2**15, "actual entry bound")
    return {"F0_sharp_witness": str(attained), "normalized_error_bound": "7587/8192",
            "route_order": "distinguished", "cancellation": "exact"}


def compute(packet, word):
    geom = geometry(packet)
    checkpoints = [i for i, event in enumerate(word) if event[0] == "checkpoint"]
    need(checkpoints == [2740], "inverse-B1 cut")
    f0, fpeak = replay(word[2741:], OUTPUTS)
    full, dpeak = replay(word, INPUTS)
    operators = {"F0": summaries(f0), "D": summaries(full)}
    need(max(Q(row["l1"]) for row in operators["F0"]) == 49, "F0 norm")
    need(max(Q(row["l1"]) for row in operators["D"]) == 1923, "decoder norm")
    return {"schema_version": 1, "geometry": geom, "events": len(word),
            "operators": operators, "peak_terms": {"F0": fpeak, "D": dpeak},
            "controls": controls(f0), "scope": "Conditional endpoint bounds; no physical producer implementation."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="create an absent receipt")
    args = parser.parse_args()
    packet, word = sources()
    result = compute(packet, word)
    path = HERE / "RESULT.json"
    if args.write:
        with path.open("x", encoding="utf-8") as output:
            written = output.write(json.dumps(result, indent=2) + "\n")
        need(written > 0, "empty receipt write")
    else:
        need(canonical(decode(read(path, 1_048_576))) == canonical(result), "receipt drift")
    print("PASS_QQ16_PRODUCER_DEFECT_TRANSFER F0=49 D<=1923 budget=7587/8192")


if __name__ == "__main__":
    main()
