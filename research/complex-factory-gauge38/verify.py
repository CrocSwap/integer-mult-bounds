#!/usr/bin/env python3
"""Exact gauge certificate and raw factory replay; no solver needed.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Uses the attributed PR681 constructor observer/native auditors and PR696
lowering in place; neither predecessor source is modified.
"""
import argparse
import copy
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FACTORY = ROOT / "research/complex-factory5-resynthesis"
BASE = "f567884aeb8851b6e794af1184119a3bfbe1e631"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def source_check():
    pins = read(HERE / "SOURCE-PINS.json")
    need(pins["base_commit"] == BASE, "base commit changed")
    for rel, pin in pins["files"].items():
        path = Path(rel)
        need(not path.is_absolute() and ".." not in path.parts, "unsafe source path")
        data = (ROOT / path).read_bytes()
        if pin["representation"] == "gzip-payload":
            data = gzip.decompress(data)
        else:
            need(pin["representation"] == "file-bytes", "unknown source representation")
        need(hashlib.sha256(data).hexdigest() == pin["sha256"], "source pin: " + rel)
    return pins


def exponent(q):
    a, b = abs(q.numerator), q.denominator
    need(a > 0 and a & (a - 1) == 0 and b & (b - 1) == 0,
         "coefficient is not a signed power of two")
    return a.bit_length() - b.bit_length()


def graph(word):
    """One gauge vertex per touched wire at each fixed ordered addition.

    Edges (u,v,e) charge |e + g[v] - g[u]|. Ground is vertex zero.
    Original scales are accumulated only between consecutive uses of one wire.
    """
    edges, last, pending = [], [0] * 8, [0] * 8
    nodes, adds, negations = 1, 0, 0
    for i, op in enumerate(word):
        need(op[0] in ("add", "scale"), "unknown circuit gate")
        if op[0] == "scale":
            q = Q(op[2], op[3])
            pending[op[1]] += exponent(q)
            negations += q < 0
        else:
            adds += 1
            for r in op[1:3]:
                edges.append([last[r], nodes, pending[r], "wire", i, r])
                last[r], pending[r] = nodes, 0
                nodes += 1
            edges.append([last[op[2]], last[op[1]], exponent(Q(op[3], op[4])),
                          "add", i, None])
    for r in range(8):
        edges.append([last[r], 0, pending[r], "wire", len(word), r])
    return nodes, edges, adds, negations


def construct(word, potentials):
    pending, previous, result = [Q(1)] * 8, [0] * 8, []
    node, frame = 1, word[0][-1]

    def scale(r, q):
        if q != 1:
            result.append(["scale", r, q.numerator, q.denominator, frame])

    for op in word:
        if op[0] == "scale":
            pending[op[1]] *= Q(op[2], op[3])
        else:
            t, s = op[1:3]
            for r in (t, s):
                g = potentials[node]
                node += 1
                scale(r, pending[r] * Q(2) ** (g - previous[r]))
                pending[r], previous[r] = Q(1), g
            q = Q(op[3], op[4]) * Q(2) ** (previous[t] - previous[s])
            result.append(["add", t, s, q.numerator, q.denominator, frame])
    for r in range(8):
        scale(r, pending[r] * Q(2) ** (-previous[r]))
    return result


def certificate_check(word, cert):
    nodes, edges, adds, negations = graph(word)
    g, y = cert["potentials"], cert["dual"]
    need(len(g) == nodes and len(y) == len(edges), "certificate dimensions")
    need(all(type(x) is int for x in g + y), "certificate integers required")
    need(g[0] == 0, "ground gauge must be zero")
    need(all(abs(x) <= 1 for x in y), "dual capacity")
    balance = [0] * nodes
    for (u, v, *_), flow in zip(edges, y):
        balance[u] -= flow
        balance[v] += flow
    need(balance == [0] * nodes, "dual flow conservation")
    residues = [e + g[v] - g[u] for u, v, e, *_ in edges]
    primal = sum(map(abs, residues))
    dual = sum(edge[2] * flow for edge, flow in zip(edges, y))
    need(primal == dual == cert["tension_optimum"] == 9, "primal-dual equality")
    need(all(r == 0 for edge, r in zip(edges, residues) if edge[3] == "add"),
         "nonunit candidate addition")
    need(4 * adds + negations + primal == cert["horner_optimum"] == 123,
         "Horner optimum")
    need(2 * adds + negations + primal == cert["pr696_optimum"] == 67,
         "PR696 optimum")
    need(construct(word, g) == cert["replacement"], "replacement not bound to gauge")
    bg = cert["budget_potentials"]
    need(len(bg) == nodes and all(type(x) is int for x in bg) and bg[0] == 0,
         "budget gauge domain")
    # Canonical deferral allows the shipped word to retain all unrelated scale
    # positions: only the two contributing doublings move in that word.
    need(construct(word, bg) == construct(cert["budget_replacement"], [0] * nodes),
         "budget replacement not bound to gauge")
    need(len(cert["budget_replacement"]) == cert["budget_macros"] == 34, "macro budget")
    need(cert["budget_pr696_cost"] == 77 and cert["budget_optimality_claimed"] is False,
         "budget scope")
    return {"vertices": nodes, "edges": len(edges), "fixed_additions": adds,
            "fixed_negations": negations, "integer_primal": primal, "integer_dual": dual,
            "horner_optimum": cert["horner_optimum"], "pr696_optimum": cert["pr696_optimum"],
            "graph_sha256": digest(edges), "unbounded_integer_gauges": True}


def circuit_primitives(lower, word):
    result = []
    for e in word:
        op = (["add", ["L", e[1]], ["L", e[2]], e[3], e[4]] if e[0] == "add"
              else ["scale", ["L", e[1]], e[2], e[3]])
        result.extend(lower.lower(op))
    return result


def primitive_replay(primitives, n, centers=0):
    """All arbitrary data/private columns, exact row norms and dyadic grids."""
    registers = [("L", r) for r in range(n)] + [("C", r) for r in range(centers)] + [("W", 0)]
    rows = {reg: {i: Q(1)} for i, reg in enumerate(registers)}
    peak, depth = Q(1), 0
    for op in primitives:
        tag, t = op[:2]
        need(t in rows, "unknown primitive target")
        if tag == "clear":
            rows[t] = {}
        elif tag == "copy":
            rows[t] = rows[op[2]].copy()
        elif tag in ("double", "halve", "negate"):
            q = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
            rows[t] = {j: q * x for j, x in rows[t].items()}
        elif tag in ("add", "subtract"):
            need(t != op[2], "primitive alias")
            for j, x in rows[op[2]].items():
                z = rows[t].get(j, Q(0)) + (x if tag == "add" else -x)
                if z:
                    rows[t][j] = z
                else:
                    rows[t].pop(j, None)
        else:
            raise ValueError("unknown primitive")
        peak = max(peak, sum(map(abs, rows[t].values()), Q(0)))
        depth = max(depth, max((x.denominator.bit_length() - 1 for x in rows[t].values()), default=0))
    need(all(not rows[r] for r in registers if r[0] != "L"), "private dirt not cleared")
    return rows, {"columns": len(registers), "primitive_count_one_component": len(primitives),
                  "exact_prefix_row_l1": str(peak), "fractional_bits": depth}


def local_check(old, lower, source, candidate, expected_cost=67):
    frame = source[0][-1]
    need(all(e[-1] == frame for e in candidate), "candidate frame changed")
    need(old.columns(source) == old.columns(candidate), "candidate map changed")
    variants = {"main": lambda x: x, "inverse": old.inverse,
                "inverse_transpose": old.dual,
                "transpose": lambda x: old.dual(old.inverse(x))}
    result = {}
    for name, transform in variants.items():
        a, b = transform(source), transform(candidate)
        pa, pb = circuit_primitives(lower, a), circuit_primitives(lower, b)
        ra, ma = primitive_replay(pa, 8)
        rb, mb = primitive_replay(pb, 8)
        need(ra == rb, "primitive boundary differs: " + name)
        need(len(pa) == 81 and len(pb) == expected_cost, "primitive price differs: " + name)
        need(old.columns(a, True) == old.columns(b, True), "positive endpoint differs")
        before, after = old.positive_envelopes(a), old.positive_envelopes(b)
        need(all(any(all(x <= y for x, y in zip(row, cover)) for cover in before)
                 for row in after), "positive prefix containment")
        result[name] = {"before": ma, "after": mb, "positive_endpoint_equal": True,
                        "positive_prefix_contained": True,
                        "original_horner_before": len(old.lowering(a)),
                        "original_horner_after": len(old.lowering(b))}
    return result


def negative_controls(old, lower, word, cert):
    result = []

    def reject(name, reason, fn):
        try:
            fn()
        except ValueError as error:
            need(str(error) == reason, "control failed for another reason: " + name)
            result.append({"name": name, "reason": reason})
        else:
            raise ValueError("accepted negative control: " + name)

    for name, change, reason in [
        ("dual_over_capacity", lambda c: c["dual"].__setitem__(0, 2), "dual capacity"),
        ("dual_unbalanced", lambda c: c["dual"].__setitem__(0, -1 if c["dual"][0] != -1 else 0), "dual flow conservation"),
        ("zero_dual", lambda c: c.__setitem__("dual", [0] * len(c["dual"])), "primal-dual equality"),
        ("fractional_potential", lambda c: c["potentials"].__setitem__(1, 0.5), "certificate integers required"),
        ("boolean_potential", lambda c: c["potentials"].__setitem__(1, False), "certificate integers required"),
        ("unpaid_boundary_gauge", lambda c: c["potentials"].__setitem__(0, 1), "ground gauge must be zero"),
        ("underpriced_optimum", lambda c: c.__setitem__("pr696_optimum", 66), "PR696 optimum")]:
        mutant = copy.deepcopy(cert)
        change(mutant)
        reject(name, reason, lambda m=mutant: certificate_check(word, m))
    candidate = cert["replacement"]
    missing = candidate[:-1]
    reject("missing_final_restoration", "candidate map changed", lambda: local_check(old, lower, word, missing))
    wrong = copy.deepcopy(candidate)
    wrong[0][3] *= -1
    reject("wrong_add_sign", "candidate map changed", lambda: local_check(old, lower, word, wrong))
    wrong_frame = copy.deepcopy(candidate)
    wrong_frame[0][-1][0] ^= 1
    reject("wrong_frame", "candidate frame changed", lambda: local_check(old, lower, word, wrong_frame))
    inflated = candidate + [["scale", 0, 2, 1, candidate[0][-1]],
                             ["scale", 0, 1, 2, candidate[0][-1]]]
    reject("neutral_extra_work", "primitive price differs: main", lambda: local_check(old, lower, word, inflated))
    # Remove ALL work clears: a single omitted clear could be repaired by the next.
    unclean = [p for p in circuit_primitives(lower, candidate) if p != ("clear", ("W", 0))]
    reject("dirty_work_never_cleared", "private dirt not cleared", lambda: primitive_replay(unclean, 8))
    budget = cert["budget_replacement"]
    for i in range(len(budget)):
        mutant = budget[:i] + budget[i + 1:]
        reject("budget_gate_deleted_" + str(i), "candidate map changed",
               lambda m=mutant: local_check(old, lower, word, m, 77))
    return result


def joint_move_controls(old, lower, word, cert):
    """Either one of the two moves is neutral; their composition saves four."""
    _, edges, _, _ = graph(word)
    registers = {v: r for _, v, _, kind, _, r in edges if kind == "wire" and v}
    result = {}
    for r in (0, 1):
        potentials = [x if i and registers[i] == r else 0
                      for i, x in enumerate(cert["budget_potentials"])]
        candidate = construct(word, potentials)
        need(old.columns(candidate) == old.columns(word), "single move map")
        cost = len(circuit_primitives(lower, candidate))
        need(len(candidate) == 34 and cost == 81 and len(old.lowering(candidate)) == 128,
             "single move must be neutral")
        result[str(r)] = {"scalar_macros": 34, "pr696_primitives": cost,
                          "original_horner_primitives": 128}
    return result


def full_replay(old, lower, out, cert):
    """Reconstruct all fourteen physical instances, including inverse cleanup."""
    src = read(FACTORY / "CIRCUIT.json")
    blocks = read(FACTORY / "BLOCKS.json")
    old.run(FACTORY / "extract.py", [out / "original"], out / "constructor.log")
    windows = read(out / "original/WINDOWS.json")
    old.bind_blocks(blocks, windows, src)
    bad_blocks = copy.deepcopy(blocks)
    bad_blocks[38 % 14]["frame"][0] ^= 1
    try:
        old.bind_blocks(bad_blocks, windows, src)
    except ValueError as error:
        need(str(error) == "wrong block boundary frames", "physical control wrong rejection")
    else:
        raise ValueError("seed block frame mutation accepted")
    raw = read(out / "original/FULL-WORD.json.gz")
    versions, results = {}, {}
    templates = (("baseline", src["replacement"]),
                 ("candidate", cert["budget_replacement"]),
                 ("primitive_optimum", cert["replacement"]))
    for name, template in templates:
        word = copy.deepcopy(raw)
        for block in reversed(blocks):
            regs = [r - 16 if r >= 240 else r - 8 for r in block["registers_before_112_port_restriction"]]
            moved = copy.deepcopy(template)
            for e in moved:
                e[1] = regs[e[1]]
                if e[0] == "add":
                    e[2] = regs[e[2]]
                e[-1] = block["frame"]
            start, end = block["A_window_zero_based"]
            word["A"][start:end] = moved
        word["cleanup"] = old.inverse([e for e in word["A"] + word["B"] if not 112 <= e[1] < 224])
        for e in word["cleanup"]:
            e[-1] = [256, 128, 64, 32, 16, 8, 4, 2, 1]
        raw_path = out / (name + "-raw.json.gz")
        raw_path.write_bytes(gzip.compress(canonical(word), mtime=0))
        record, native_word = old.native(raw_path, out / name, out)
        versions[name] = native_word
        programs = read(out / name / "LOCAL-PROGRAMS.json.gz")
        lowered = {}
        for direction, events in programs.items():
            stream, tags, h = [], Counter(), hashlib.sha256()
            for event in events:
                if event[0] == "scalar":
                    for primitive in lower.lower(event[1]):
                        stream.append(primitive)
                        tags[primitive[0]] += 2
                        h.update(canonical([event[2], primitive]) + b"\n")
            rows, metrics = primitive_replay(stream, 716, 8)
            for r in range(716):
                expected = {r: Q(1)}
                if direction == "forward" and 112 <= r < 224:
                    expected[r - 112] = Q(1)
                elif direction == "backward" and r < 112:
                    expected[r + 112] = Q(-1)
                need(rows["L", r] == expected, "full primitive map differs")
            lowered[direction] = {**metrics, "real_primitives": 2 * len(stream),
                                  "primitive_tags": dict(sorted(tags.items())),
                                  "primitive_stream_sha256": h.hexdigest()}
        results[name] = {"native": record, "pr696": lowered}
    for name in ("candidate", "primitive_optimum"):
        for key in ("local_profile", "start", "final", "compensation", "ports", "centers", "center_frames", "frames", "edges"):
            need(versions["baseline"][key] == versions[name][key], "native invariant changed: " + key)
    before, after = results["baseline"], results["candidate"]
    # Bind the reconstruction to the already integrated PR681 and PR696 results.
    need(before["native"] == read(FACTORY / "RESULT.json")["after"], "baseline PR681 replay differs")
    expected_lower = read(ROOT / "research/supplier-circuit-consolidation/EXPECTED.json")["complex"]["raw_factory_with_lowering"]
    for direction in ("forward", "backward"):
        a, b = before["pr696"][direction], after["pr696"][direction]
        need(a["real_primitives"] == expected_lower["after/" + direction]["new_real_primitives"], "baseline PR696 bill differs")
        need(a["real_primitives"] - b["real_primitives"] == 224, "full primitive saving")
        ea, eb = before["native"]["emitted"][direction], after["native"]["emitted"][direction]
        need(eb["scalar_macros"] == ea["scalar_macros"], "full macro count")
        need(ea["real_component_primitive_bound"] - eb["real_component_primitive_bound"] == 112, "original Horner saving")
        need(eb["paid_profile"] == ea["paid_profile"], "recursive profile changed")
        bad = results["primitive_optimum"]
        need(a["real_primitives"] - bad["pr696"][direction]["real_primitives"] == 784,
             "unconstrained primitive saving")
        need(bad["native"]["emitted"][direction]["scalar_macros"] - ea["scalar_macros"] == 112,
             "unconstrained macro increase")
    compiler = 64 * 74**3
    invoice = {"compiler": compiler, "versions": {},
               "scope": "Exact recount under invoice_allcold.py's retained local bound formula; not a global invoice replay."}
    for name, _ in templates:
        data = results[name]
        macros = max(row["scalar_macros"] for row in data["native"]["emitted"].values())
        children = sum(data["native"]["emitted"]["forward"]["paid_profile"].values())
        adapters = 16 * (macros + children + 716 + 8) + 64 * 73
        invoice["versions"][name] = {
            "macros": macros, "children": children, "registers": 716, "centers": 8,
            "adapter_allowance": adapters,
            "original_horner_local_bound": adapters * compiler + max(
                row["real_component_primitive_bound"] for row in data["native"]["emitted"].values()),
            "pr696_recount_local_bound": adapters * compiler + max(
                row["real_primitives"] for row in data["pr696"].values())}
    bills = invoice["versions"]
    need(bills["candidate"]["pr696_recount_local_bound"] - bills["baseline"]["pr696_recount_local_bound"] == -224,
         "budget candidate full local bill")
    need(bills["primitive_optimum"]["pr696_recount_local_bound"] - bills["baseline"]["pr696_recount_local_bound"] == 46474329328,
         "unconstrained candidate full local bill")
    invoice["scalar_only_selection_control"] = {
        "scalar_bill_improves": True, "complete_local_bill_improves": False,
        "complete_local_bill_delta": 46474329328}
    # Native source already runs four semantic controls in each full word.
    results["accounting"] = invoice
    results["blocks"] = 14
    results["seed_block"] = {"index": 38 % 14, "boundary": blocks[38 % 14]}
    results["physical_control"] = {"index": 38 % 14, "rejected": True,
                                   "reason": "wrong block boundary frames"}
    return results


def verify(out, local_only=False):
    pins = source_check()
    src = read(FACTORY / "CIRCUIT.json")
    cert = read(HERE / "CERTIFICATE.json")
    old = module("gauge_predecessor", FACTORY / "verify.py")
    lower = module("gauge_lowering", ROOT / "research/complex-dyadic-lowering/lower.py")
    result = {"status": "PASS_COMPLEX_FACTORY_GAUGE38", "base_commit": BASE,
              "source_files": len(pins["files"]), "certificate": certificate_check(src["replacement"], cert),
              "local": local_check(old, lower, src["replacement"], cert["replacement"]),
              "budget_local": local_check(old, lower, src["replacement"], cert["budget_replacement"], 77),
              "joint_move_controls": joint_move_controls(old, lower, src["replacement"], cert),
              "controls": negative_controls(old, lower, src["replacement"], cert), "new_kappa": False}
    if not local_only:
        result["full"] = full_replay(old, lower, out, cert)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="retain fresh artifacts in a new directory")
    parser.add_argument("--write", type=Path, help="development only: freeze the new receipt")
    parser.add_argument("--local-only", action="store_true", help="check certificate and local controls only")
    args = parser.parse_args()
    if args.out:
        args.out.mkdir(parents=True, exist_ok=False)
        result = verify(args.out.resolve(), args.local_only)
    else:
        with tempfile.TemporaryDirectory(prefix="factory-gauge38-") as tmp:
            result = verify(Path(tmp), args.local_only)
    if args.write:
        write(args.write, result)
    else:
        expected = read(HERE / "EXPECTED.json")
        if args.local_only:
            expected.pop("full")
        need(result == expected, "frozen receipt differs")
    if args.out:
        write(args.out / "RESULT.json", result)
    print("PASS_COMPLEX_FACTORY_GAUGE38 baseline=81 budget=77 class_optimum=67 controls=46 "
          + ("local_only=True" if args.local_only else "blocks=14 saved=224,224 local_bill_delta=-224")
          + " no_new_kappa")


if __name__ == "__main__":
    main()
