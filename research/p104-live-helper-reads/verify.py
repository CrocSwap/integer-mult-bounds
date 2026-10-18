#!/usr/bin/env python3
"""Exact premises for actual-frame read-only access to original P104 helpers.

Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
No pending predecessor code is imported. Default execution writes nothing.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WORD = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
FIXTURE = "research/p104-native-channel/inputs/P104-FIXTURE.json"


class Invalid(ValueError):
    pass


def require(ok, why):
    if not ok:
        raise Invalid(why)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def unique(pairs):
    out = {}
    for k, v in pairs:
        require(k not in out, "duplicate JSON key")
        out[k] = v
    return out


def read(path):
    return json.loads(path.read_text(encoding="utf8"), object_pairs_hook=unique)


def span(basis):
    out = {0}
    for v in basis:
        require(type(v) is int and 0 <= v < 512, "invalid binary generator")
        out.update(w ^ v for w in tuple(out))
    return frozenset(out)


def binary_basis(vectors):
    chosen, current = [], frozenset({0})
    for v in vectors:
        if v not in current:
            chosen.append(v)
            current = span(chosen)
    return chosen


def rational_basis(rows):
    pivots, indices = {}, []
    for i, original in enumerate(rows):
        row = list(map(F, original))
        for p in sorted(pivots):
            a = row[p]
            if a:
                row = [x - a*y for x, y in zip(row, pivots[p])]
        p = next((j for j, a in enumerate(row) if a), None)
        if p is not None:
            a = row[p]
            pivots[p] = [x/a for x in row]
            indices.append(i)
    return indices


def determinant(rows):
    """Integer Bareiss check, independent of rational pivot selection."""
    a = [list(row) for row in rows]
    n, sign, previous = len(a), 1, 1
    require(all(len(row) == n for row in a), "nonsquare minor")
    for k in range(n - 1):
        p = next((i for i in range(k, n) if a[i][k]), None)
        if p is None:
            return 0
        if p != k:
            a[k], a[p] = a[p], a[k]
            sign *= -1
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j]*pivot - a[i][k]*a[k][j]
                require(numerator % previous == 0, "inexact minor division")
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = pivot
    return sign*a[-1][-1]


def roots(fixture):
    all_roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            v = [0]*8
            v[i], v[j] = 2, 2*sign
            all_roots.add(tuple(v))
    all_roots.update((1, *v) for v in product((-1, 1), repeat=7)
                     if v.count(-1) % 2 == 0)
    puncture = fixture["section4_explicit_P104"]
    removed = {tuple(v) for v in puncture["F0"] + puncture["C"]}
    require(len(all_roots) == 120 and len(removed) == 16 and removed <= all_roots,
            "invalid root puncture")
    r = sorted(all_roots - removed)
    require([[sum(v[i]*v[j] for v in r) for j in range(8)] for i in range(8)]
            == [[104*int(i == j) for j in range(8)] for i in range(8)], "root Gram")
    return r


def plus(dst, src, a):
    for k, v in tuple(src.items()):
        v = dst.get(k, F(0)) + a*v
        if v:
            dst[k] = v
        else:
            dst.pop(k, None)


def code_coordinates(source, r):
    alpha = [sum(source.get(f"X{s}", F(0))*r[s][j] for s in range(104))/104
             for j in range(8)]
    require(all(source.get(f"X{s}", F(0)) == sum(alpha[j]*r[s][j] for j in range(8))
                for s in range(104)), "source outside K")
    return alpha


def serialized(row):
    return {k: str(v) for k, v in sorted(row.items())}


def trace(word, r):
    names = ([f"X{i}" for i in range(104)] + [f"Y{i}" for i in range(104)]
             + [f"G{i}" for i in range(32)] + [f"Q{i}" for i in range(8)]
             + [f"D{i}" for i in range(32)])
    require(set(word["initial_frames"]) == set(names), "initial inventory")
    frames = {k: span(v) for k, v in word["initial_frames"].items()}
    ends = {f"Y{t}": span(word["final_frames"][f"Y{t}"]) for t in range(104)}
    require(len(set(ends.values())) == 104, "distinct target endpoints")
    labels = [next(iter(frames[f"X{s}"] - {0})) for s in range(104)]
    require(all(len(frames[f"X{s}"]) == 2 for s in range(104)), "source lines")
    values = {k: {k: F(1)} for k in names}
    # Independent certificate representation: source projection = alpha R + local.
    alpha = {k: [F(0)]*8 for k in names}
    local = {k: ({int(k[1:]): F(1)} if k.startswith("X") else {}) for k in names}
    paths = {k: [frames[k]] for k in names}
    states, private, profile, counts = [], [], Counter(), Counter()
    avoided = set()
    example = None
    active = None

    def certify(k, cut):
        nonlocal example
        if k.startswith("Y"):
            return
        require(all(labels[s] in frames[k] for s in local[k]), "local support leaves frame")
        require(all(values[k].get(f"X{s}", F(0)) == local[k].get(s, F(0))
                    + sum(alpha[k][j]*r[s][j] for j in range(8)) for s in range(104)),
                "source decomposition identity")
        state = [cut, k, sorted(frames[k]), list(map(str, alpha[k])),
                 {str(s): str(v) for s, v in sorted(local[k].items())}]
        states.append(state)
        if k[0] in "GQD":
            require(frames[k] not in ends.values(), "original helper reaches target endpoint")
            avoided.add((k, tuple(sorted(frames[k]))))
            if example is None and local[k]:
                compatible = [t for t in range(104) if frames[k] < ends[f"Y{t}"]]
                if compatible:
                    try:
                        code_coordinates(values[k], r)
                    except Invalid:
                        example = {"cut": cut, "register": k, "frame": binary_basis(sorted(frames[k])),
                                   "target": compatible[0], "full_input_row": serialized(values[k]),
                                   "local_source_row": {str(s): str(v) for s, v in local[k].items()},
                                   "code_coefficients": list(map(str, alpha[k]))}

    for k in names:
        certify(k, 0)
    for i, event in enumerate(word["program"]):
        op = event[0]
        counts[op] += 1
        if op == "add":
            _, dst, src, a, chart = event
            require(dst in values and src in values and dst != src, "ADD inventory")
            require(not dst.startswith("X") and not src.startswith("Y"), "data direction")
            require(frames[dst] == frames[src] == span(chart), "ADD frame")
            a = F(a)
            plus(values[dst], values[src], a)
            if not dst.startswith("Y"):
                alpha[dst] = [x+a*y for x, y in zip(alpha[dst], alpha[src])]
                plus(local[dst], local[src], a)
            certify(dst, i+1)
        elif op == "transport":
            _, k, before, after, rank = event
            a, b = span(before), span(after)
            require(frames[k] == a and (a < b or b < a), "nested transport")
            require(type(rank) is int and rank == abs(len(b).bit_length()-len(a).bit_length()), "transport rank")
            profile[rank] += 1
            if k == "C":
                require(active is not None and b < a and len(a) == 256 and len(b) == 2,
                        "private descent")
                require(active["copy_event"] == i-1, "private copy chronology")
                active["descent_event"] = i
            else:
                require(a < b, "original path descends")
                paths[k].append(b)
            frames[k] = b
            certify(k, i+1)
        elif op == "zero":
            _, k, chart = event
            require(k == "C" and k not in values and active is None, "private allocation")
            values[k], frames[k], alpha[k], local[k] = {}, span(chart), [F(0)]*8, {}
            active = {"allocation_event": i}
            certify(k, i+1)
        elif op == "copy":
            _, dst, src, chart = event
            require(dst == "C" and src == f"Q{len(private)}" and active is not None and not values[dst],
                    "private copy")
            require(frames[dst] == frames[src] == span(chart), "COPY frame")
            values[dst] = dict(values[src])
            alpha[dst], local[dst] = code_coordinates(values[src], r), {}
            dirt = {k: v for k, v in values[src].items() if not k.startswith("X")}
            require(dirt == {src: F(1)}, "private dirt")
            active.update(copy_event=i, alpha=list(map(str, alpha[dst])), row=serialized(values[dst]))
            certify(dst, i+1)
        elif op == "erase":
            _, k, chart = event
            require(k == "C" and active is not None and frames[k] == span(chart), "private erase")
            require(serialized(values[k]) == active["row"], "private value changed")
            active["erase_event"] = i
            private.append(active)
            active = None
            for state in (values, frames, alpha, local):
                del state[k]
        else:
            raise Invalid("unknown event")
    require(active is None and len(private) == 8, "private count")
    require(frames == {k: span(v) for k, v in word["final_frames"].items()}, "final frames")
    for k in names:
        expected = {k: F(1)}
        if k.startswith("Y"):
            t = int(k[1:])
            expected.update({f"X{s}": F(sum(a*b for a, b in zip(r[t], r[s])), 8)
                             for s in range(104) if sum(a*b for a, b in zip(r[t], r[s]))})
        require(values[k] == expected, "endpoint row " + k)
    require(example is not None, "missing outside-code example")
    return {"events": len(word["program"]), "independent_inputs": len(names),
            "state_certificates": len(states), "state_certificate_sha256": sha256(canonical(states).encode()).hexdigest(),
            "original_helper_frame_pairs": len(avoided), "target_endpoint_contacts": 0,
            "original_helper_paths": {k: [binary_basis(sorted(v)) for v in paths[k]] for k in paths if k[0] in "GQD"},
            "operations": dict(sorted(counts.items())), "rank_profile": {str(k): v for k, v in sorted(profile.items())},
            "private_lifetimes": private, "outside_code_example": example}, paths, labels


def geometry(paths, labels, r):
    result = []
    for t in range(104):
        h = paths[f"Y{t}"][-1]
        require(len(h) == 256 and paths[f"Y{t}"][0] == {0}, "target dimensions")
        support = {s for s in range(104) if F(s == t)-F(sum(a*b for a, b in zip(r[t], r[s])), 8)}
        require(support == {s for s in range(104) if labels[s] in h}, "correction support")
        early = {s for s in support if any(labels[s] in v for v in paths[f"Y{t}"][:-1])}
        needed = sorted(support-early)
        chosen_labels = binary_basis(labels[s] for s in needed)
        require(span(chosen_labels) == h, "required support rank")
        require(not any(h in paths[f"X{s}"] for s in range(104)), "direct source endpoint")
        outside = [s for s in range(104) if s not in support]
        chosen = [outside[i] for i in rational_basis([r[s] for s in outside])]
        require(len(chosen) == 8 and determinant([r[s] for s in chosen]) != 0, "code quotient injectivity")
        result.append({"target": t, "endpoint": binary_basis(sorted(h)), "support": sorted(support),
                       "early": sorted(early), "required_basis_sources": [labels.index(v) for v in chosen_labels],
                       "outside_minor_columns": chosen, "outside_minor_determinant": determinant([r[s] for s in chosen])})
    return result


def rejects(operation, expected):
    try:
        operation()
    except Invalid as exc:
        require(str(exc) == expected, "wrong rejection: " + str(exc))
        return
    raise Invalid("mutation accepted: " + expected)


def controls(word, r, summary, paths, labels):
    result = []
    bad = deepcopy(word)
    event = next(e for e in bad["program"] if e[0] == "transport")
    event[4] += 1
    rejects(lambda: trace(bad, r), "transport rank")
    result.append("wrong native rank rejected")
    bad = deepcopy(word)
    next(e for e in bad["program"] if e[0] == "add" and e[1] == "Q0")[3] = 0
    rejects(lambda: trace(bad, r), "private dirt")
    result.append("missing query compensation rejected")
    bad = deepcopy(word)
    last = max(i for i, e in enumerate(bad["program"]) if e[0] == "add")
    bad["program"][last][3] = 0
    try:
        trace(bad, r)
    except Invalid as exc:
        require(str(exc).startswith("endpoint row "), "missing cleanup rejection")
    else:
        raise Invalid("missing cleanup accepted")
    result.append("missing dirty cleanup rejected")
    # This actual unfinished row is outside K, but is supported in its actual frame.
    example = summary["outside_code_example"]
    row = {k: F(v) for k, v in example["full_input_row"].items()}
    rejects(lambda: code_coordinates(row, r), "source outside K")
    v = span(example["frame"])
    require(all(labels[int(s)] in v for s in example["local_source_row"]), "example support")
    result.append("actual unfinished outside-K read is quotient-admissible")
    # Moving that value freely to ZERO is a strictly stronger, unclaimed permission.
    require(any(labels[int(s)] != 0 for s in example["local_source_row"]), "free-frame escape missing")
    result.append("free arbitrary-frame access violates local support")
    # A wrong endpoint frame must invalidate the new finite premise.
    bad = deepcopy(word)
    helper_frame = next(e[3] for e in word["program"] if e[0] == "transport" and e[1].startswith("G") and len(span(e[3])) == 256)
    bad["final_frames"]["Y0"] = helper_frame
    rejects(lambda: trace(bad, r), "original helper reaches target endpoint")
    result.append("new endpoint contact rejected")
    # A target-supported oracle at the endpoint removes the entrance conclusion.
    # This is deliberately not an actual-frame original-helper read.
    correction = {f"X{s}": F(s == 0)-F(sum(a*b for a, b in zip(r[0], r[s])), 8)
                  for s in range(104)}
    correction = {k: v for k, v in correction.items() if v}
    rejects(lambda: code_coordinates(correction, r), "source outside K")
    require(len(correction) == 48 and span(labels[int(k[1:])] for k in correction) == paths["Y0"][-1],
            "oracle countermodel target support")
    arbitrary_target = {"Y0": F(1)}
    plus(arbitrary_target, correction, F(1))
    require(arbitrary_target == {"Y0": F(1), **correction}, "zero-entrance oracle write")
    result.append("outside-K endpoint oracle permits zero-entrance correction")
    # Input-independent invertible code-coordinate changes preserve the quotient.
    changed = [tuple([v[0]+v[1], *v[1:]]) for v in r]
    for target in geometry(paths, labels, r):
        cols = target["outside_minor_columns"]
        require(determinant([changed[s] for s in cols]) == target["outside_minor_determinant"], "basis-change minor")
    result.append("all104 invertible code-basis controls")
    return result


def compute():
    sources = read(HERE/"SOURCES.json")
    pins = {p["path"]: p["sha256"] for p in sources["files"] if p["usage"] == "input"}
    require(set(pins) == {WORD, FIXTURE}, "source inventory")
    for path, digest in pins.items():
        require(sha256((ROOT/path).read_bytes()).hexdigest() == digest, "source hash " + path)
    word, fixture = read(ROOT/WORD), read(ROOT/FIXTURE)
    r = roots(fixture)
    summary, paths, labels = trace(word, r)
    targets = geometry(paths, labels, r)
    return {"schema_version": 1, "claim": "actual-frame original helper reads preserve 208 new monotone lifetimes",
            "sources": pins, "trace": summary, "targets": targets, "helper_lifetime_floor": 208,
            "controls": controls(word, r, summary, paths, labels),
            "limits": "read-only original word; no new descending helper, target feedback, arbitrary-frame oracle, supplier or kappa"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = compute()
    require(canonical(result) == canonical(read(HERE/"RESULT.json")), "receipt mismatch")
    if args.out:
        with args.out.open("x", encoding="utf8") as f:
            json.dump(result, f, indent=2, sort_keys=True)
            f.write("\n")
    print(f"PASS_P104_LIVE_HELPER_READS original_helpers=72 endpoint_contacts=0 lifetimes=208 controls={len(result['controls'])} no_new_kappa")


if __name__ == "__main__":
    main()
