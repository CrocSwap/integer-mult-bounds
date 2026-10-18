#!/usr/bin/env python3
"""Exact JP8 diagonal-gauge certificate checker. Apache-2.0.

Prepared for Luis Leon (@mythrilium), with substantial OpenAI Codex assistance.
Uses the credited #622/#626 word and original emitter's primitive convention.
No solver dependency, writes, network, or reliance on Python assertions.
"""
import copy
import gzip
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCAL = "research/community-k492-audit/pr622/replay/jp8-local/"
SPEC = "research/complex-k492-owner-repair/data/SPEC.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_inputs():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for path, pins in sources["files"].items():
        raw = (ROOT / path).read_bytes()
        if path.endswith(".gz"):
            # The compressed bytes are recorded, but equality is payload-based.
            require(hashlib.sha256(gzip.decompress(raw)).hexdigest() == pins["payload_sha256"], path)
        else:
            require(hashlib.sha256(raw).hexdigest() == pins["sha256"], path)
    word = json.loads(gzip.decompress((ROOT / LOCAL / "CANONICAL-WORD.json.gz").read_bytes()))
    programs = json.loads(gzip.decompress((ROOT / LOCAL / "LOCAL-PROGRAMS.json.gz").read_bytes()))
    spec = json.loads((ROOT / SPEC).read_text())["providers"]["jp8"]
    for name, obj in (("CANONICAL-WORD.json.gz", word), ("LOCAL-PROGRAMS.json.gz", programs)):
        require(digest(obj) == spec["artifact_semantic_sha256"][name], "selected SPEC binding: " + name)
    for name, events in programs.items():
        require(digest(events) == spec["program_hashes"][name], "program binding: " + name)
    return word, programs, spec


def power2(e):
    return Q(2 ** e) if e >= 0 else Q(1, 2 ** -e)


def valuation(q):
    require(q != 0 and q.denominator & (q.denominator - 1) == 0, "nonzero dyadic required")
    a = abs(q.numerator)
    return (a & -a).bit_length() - q.denominator.bit_length()


def native_edges(cleanup):
    edges = []
    for op in cleanup:
        require(op[0] in ("add", "scale") and op[-1] == 1, "full-frame add/scale cleanup required")
        if op[0] == "add":
            require(op[1] != op[2], "aliasing addition")
            edges.append((op[1], op[2], valuation(Q(op[3], op[4]))))
    return edges


def check_duality(edges, g, dual):
    require(len(dual) == len(edges), "dual edge count")
    require(all(type(x) is int for x in g), "integer gauge required")
    require(all(type(x) is int and -1 <= x <= 1 for x in dual), "dual box constraint")
    div = [0] * len(g)
    lower = 0
    for f, (t, s, e) in zip(dual, edges):
        div[t] += f
        div[s] -= f
        lower += e * f
    require(all(abs(x) <= 2 for x in div), "dual divergence constraint")
    primal = 2 * sum(map(abs, g)) + sum(abs(e + g[t] - g[s]) for t, s, e in edges)
    require(primal == lower, "primal/dual gap")
    return primal


def native_scale(r, e):
    q = power2(e)
    return ["scale", r, q.numerator, q.denominator, 1]


def transform(cleanup, g):
    pre = [native_scale(r, e) for r, e in enumerate(g) if e]
    middle = copy.deepcopy(cleanup)
    for op in middle:
        if op[0] == "add":
            q = Q(op[3], op[4]) * power2(g[op[1]] - g[op[2]])
            op[3:5] = [q.numerator, q.denominator]
    post = [native_scale(r, -e) for r, e in enumerate(g) if e]
    return pre + middle + post


def scalar(op, backward=False):
    if op[0] == "add":
        t, s, a, b = op[1:5]
        if backward:
            t, s, a = s, t, -a
        return ["add", ["L", t], ["L", s], a, b]
    t, a, b = op[1:4]
    return ["scale", ["L", t], b, a] if backward else ["scale", ["L", t], a, b]


def splice(events, original, candidate, backward):
    start = events.index(["phase", "full_frame_cleanup"]) + 1
    end = start + len(original)
    expected = [["scalar", scalar(op, backward), 1] for op in original]
    require(events[start:end] == expected, "cleanup must be exactly the pinned contiguous block")
    replacement = [["scalar", scalar(op, backward), 1] for op in candidate]
    result = events[:start] + replacement + events[end:]
    require([e for e in result if e[0] != "scalar"] == [e for e in events if e[0] != "scalar"], "non-scalar event change")
    return result


def primitive_cost(op):
    if op[0] in ("clear", "copy"):
        return 1
    q = Q(op[3], op[4]) if op[0] == "add" else Q(op[2], op[3])
    a, b = abs(q.numerator), q.denominator
    valuation(q)
    if op[0] == "scale":
        require(a & (a - 1) == 0, "scale must be signed power of two")
        return abs(a.bit_length() - b.bit_length()) + int(q < 0)
    return 3 + (a.bit_length() - 1) + a.bit_count() + (b.bit_length() - 1)


def replay(events, n, v, backward, endpoint=True):
    """Sparse rational rows simultaneously represent all n arbitrary inputs.

    Positive norm propagation follows the retained audit, including the maximal
    numerator-Horner work value. Private centre inputs start arbitrary, not zero.
    """
    rows = {("L", r): {r: Q(1)} for r in range(n)}
    norms = {r: Q(1) for r in rows}
    for r in range(8):
        rows["C", r] = {n + r: Q(1)}
        norms["C", r] = Q(1)
    prefix = Q(1)
    macros = prims = 0
    for event in events:
        if event[0] != "scalar":
            continue
        op = event[1]
        tag, t = op[0], tuple(op[1])
        prims += 2 * primitive_cost(op)
        macros += 1
        if tag == "clear":
            rows[t], norms[t] = {}, Q(0)
        elif tag == "copy":
            s = tuple(op[2])
            rows[t], norms[t] = dict(rows[s]), norms[s]
        elif tag == "scale":
            q = Q(op[2], op[3])
            rows[t] = {j: q * x for j, x in rows[t].items()}
            norms[t] *= abs(q)
        elif tag == "add":
            s, q = tuple(op[2]), Q(op[3], op[4])
            require(s != t, "aliased replay addition")
            prefix = max(prefix, abs(q.numerator) * norms[s])
            norms[t] += abs(q) * norms[s]
            row = rows[t]
            for j, x in rows[s].items():
                z = row.get(j, Q(0)) + q * x
                if z:
                    row[j] = z
                else:
                    row.pop(j, None)
        else:
            raise ValueError("unknown scalar operation")
        prefix = max(prefix, norms[t])
    if endpoint:
        for r in range(n):
            expected = {r: Q(1)}
            if backward and r < v:
                expected[v + r] = Q(-1)
            elif not backward and v <= r < 2 * v:
                expected[r - v] = Q(1)
            require(rows["L", r] == expected, f"endpoint mismatch: {r}")
        require(all(not row for r, row in rows.items() if r[0] == "C"), "dirty centre not cleared")
    require(prefix < 2 ** 192, "192-bit positive prefix allowance exceeded")
    return {"real_primitives": prims, "scalar_macros": macros,
            "prefix_l1": str(prefix), "prefix_bits": prefix.numerator.bit_length() - prefix.denominator.bit_length() + 1,
            "all_native_columns": n, "arbitrary_private_centre_columns": 8}


def primitive_coefficient_check(q, omit_clear=False):
    """Independent formal (target, source, incoming work) primitive interpreter."""
    a, b = abs(q.numerator), q.denominator
    # State rows in a three-dimensional rational vector space.
    t, s, w = [Q(1), Q(0), Q(0)], [Q(0), Q(1), Q(0)], [Q(0), Q(0), Q(1)]
    count = 0
    w = [Q(0)] * 3
    count += 1
    for i, digit in enumerate(bin(a)[2:]):
        if i:
            w = [2 * x for x in w]
            count += 1
        if digit == "1":
            w = [x + y for x, y in zip(w, s)]
            count += 1
    for _ in range(b.bit_length() - 1):
        w = [x / 2 for x in w]
        count += 1
    t = [x + (1 if q > 0 else -1) * y for x, y in zip(t, w)]
    count += 1
    if not omit_clear:
        w = [Q(0)] * 3
        count += 1
    require(t == [1, q, 0] and s == [0, 1, 0] and w == [0, 0, 0], "primitive coefficient boundary")
    require(count == primitive_cost(["add", ["L", 0], ["L", 1], q.numerator, q.denominator]), "primitive count mismatch")


def main():
    word, programs, spec = load_inputs()
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    n, v = 2 * word["v"] + word["R"], word["v"]
    g, dual = cert["exponents"], cert["edge_dual"]
    require(len(g) == n, "gauge dimension")
    edges = native_edges(word["cleanup"])
    active = {r for t, s, _ in edges for r in (t, s)}
    require(all(not e or (r in active and word["final"][r] == 1) for r, e in enumerate(g)), "illegal gauge register/frame")
    objective = check_duality(edges, g, dual)
    original_objective = sum(abs(e) for _, _, e in edges)
    require(objective == cert["objective"] and original_objective == cert["original_objective"], "certificate objective")
    require(sum(x != 0 for x in g) == cert["nonzero"] and sum(map(abs, g)) == cert["l1_exponents"], "certificate gauge census")
    candidate = transform(word["cleanup"], g)
    coefficients = set()
    report = {"objective": objective, "original_objective": original_objective,
              "saving_per_orientation": 2 * (original_objective - objective),
              "boundary_real_primitives": 4 * sum(map(abs, g)),
              "changed_registers": sum(x != 0 for x in g), "edge_count": len(edges),
              "candidate_cleanup_sha256": digest(candidate), "programs": {}}
    for name, events in programs.items():
        back = name == "backward"
        changed = splice(events, word["cleanup"], candidate, back)
        for stream in (events, changed):
            for event in stream:
                if event[0] == "scalar" and event[1][0] == "add":
                    coefficients.add(Q(event[1][3], event[1][4]))
        before = replay(events, n, v, back)
        after = replay(changed, n, v, back)
        inherited = spec["complete_contract"]["local"][name]
        require(before["real_primitives"] == inherited["real_component_primitives"], "original primitive binding")
        require(before["prefix_l1"] == inherited["prefix_l1"], "original prefix binding")
        require(before["real_primitives"] - after["real_primitives"] == report["saving_per_orientation"], "complete cost delta")
        report["programs"][name] = {"before": before, "after": after, "candidate_sha256": digest(changed)}
        print(f"PASS {name} primitives={before['real_primitives']}->{after['real_primitives']} prefix_bits={after['prefix_bits']}", flush=True)
    for q in coefficients:
        primitive_coefficient_check(q)
    report["distinct_add_coefficients_checked"] = len(coefficients)
    expected = json.loads((HERE / "EXPECTED.json").read_text())
    require(report == expected, "receipt mismatch")
    print(f"PASS_JP8_DIAGONAL_GAUGE optimal_objective={objective} saved={report['saving_per_orientation']}/"
          f"{report['saving_per_orientation']} columns={n}+8 gauge_domain=all_integer_exponents")
    return report


if __name__ == "__main__":
    main()
