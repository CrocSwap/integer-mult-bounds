#!/usr/bin/env python3
"""Check the extracted response and native words with separate arithmetic."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from functools import lru_cache
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import time


def need(value, label):
    if not value:
        raise ValueError(label)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def rows(value):
    return [{int(j): F(v) for j, v in row.items() if F(v)} for row in value]


def eye(n):
    return [{i: F(1)} for i in range(n)]


def put(row, j, v):
    value = row.get(j, F(0)) + v
    if value:
        row[j] = value
    else:
        row.pop(j, None)


def plus(a, b, c=1):
    out = deepcopy(a)
    for row, extra in zip(out, b):
        for j, v in extra.items():
            put(row, j, c*v)
    return out


def mul(a, b):
    out = []
    for row in a:
        result = {}
        for j, v in row.items():
            for k, w in b[j].items():
                put(result, k, v*w)
        out.append(result)
    return out


def transpose(a, n):
    out = [{} for _ in range(n)]
    for i, row in enumerate(a):
        for j, v in row.items():
            out[j][i] = v
    return out


def rank(a):
    basis = {}
    for original in a:
        row = dict(original)
        while row:
            j = min(row)
            v = row[j]
            if j not in basis:
                basis[j] = {k: w/v for k, w in row.items()}
                break
            for k, w in basis[j].items():
                put(row, k, -v*w)
    return len(basis)


def family(n):
    u = [F(1)]*(n-2) + [F(n-4), F(0)]
    ell = [F(-1)]*(n-2) + [F(1), F(0)]
    r = plus(eye(n), [{j: a*b for j, b in enumerate(ell) if a*b} for a in u])
    p = eye(n)
    p[-2], p[-1] = p[-1], p[-2]
    return mul(p, r), mul(r, p), p, r


def check_model(model):
    generic = []
    for n in range(3, 25):
        e, ei, p, r = family(n)
        need(mul(e, ei) == mul(ei, e) == eye(n), "Family inverse orders")
        need(all(i not in a[i] for a in (e, ei) for i in range(n)), "Family zero diagonals")
        need(rank(plus(e, eye(n), -1)) == 2, "Family correction rank")
        if n >= 5:
            metric = [{i: F(1) if i < n-2 else F(-1, n-4)} for i in range(n)]
            need(mul(transpose(e, n), mul(metric, e)) == metric, "Family metric identity")
            equations = []
            for i in range(n):
                for j in range(i, n):
                    row = {k: e[k].get(i, 0)*e[k].get(j, 0) for k in range(n)}
                    if i == j:
                        put(row, i, -1)
                    equations.append({k: v for k, v in row.items() if v})
            need(rank(equations) == n-1, "One-dimensional invariant diagonal metric space")
        generic.append(n)

    h, hi = eye(112), eye(112)
    for pair in model["pair_codes"]:
        a, b = pair["ports"]
        local = [[F(x) for x in row] for row in pair["matrix"]]
        for i, target in enumerate((a, b)):
            h[target] = {origin: local[i][j] for j, origin in enumerate((a, b)) if local[i][j]}
            hi[target] = {origin: local[j][i]/2 for j, origin in enumerate((a, b)) if local[j][i]}
    need(mul(h, hi) == eye(112), "Pair inverse from pair records")
    need(h == rows(model["pair_code"]) and hi == rows(model["pair_code_inverse"]), "Serialized pair code")
    mode = {name: eye(112) for name in ("E", "inverse_E", "P", "R", "J")}
    sizes = Counter()
    for block in model["blocks"]:
        ports = block["ports"]
        n = len(ports)
        sizes[n] += 1
        matrices = family(n) + ([{i: F(1) if i < n-2 else F(-1, n-4)} for i in range(n)],)
        for name, matrix in zip(mode, matrices):
            for i, p in enumerate(ports):
                mode[name][p] = {ports[j]: v for j, v in matrix[i].items()}
    need(sizes == {6: 8, 8: 8}, "Actual block census")
    physical = {name: mul(hi, mul(matrix, h)) for name, matrix in mode.items()}
    for name, value in physical.items():
        need(value == rows(model["physical"][name]), "Independent physical reconstruction " + name)
    e, ei, p, r, j = (physical[name] for name in mode)
    need(mul(e, ei) == mul(ei, e) == eye(112), "Physical inverse orders")
    need(mul(p, r) == e and mul(p, p) == mul(r, r) == eye(112), "Physical factors")
    need(rank(plus(e, p, -1)) == 16 and rank(plus(e, eye(112), -1)) == 32, "Physical displacement ranks")
    need(all(i not in a[i] for a in (e, ei) for i in range(112)), "Physical zero diagonals")
    need(mul(transpose(e, 112), mul(j, e)) == j, "Physical metric after pair normalization")
    need(Counter(j[i][i] for i in range(112)) == {F(1): 80, F(-1, 2): 16, F(-1, 4): 16}, "Metric weights")
    need(sum(map(len, p)) == 160 and any(len(row) > 1 for row in p), "P is not a permutation")
    u, ell = rows(model["reflection_U"]), rows(model["reflection_L"])
    ji = [{i: 1/j[i][i]} for i in range(112)]
    need(mul(u, ell) == plus(r, eye(112), -1), "Reflection rank factor")
    need(mul(ell, mul(ji, transpose(ell, 112))) == [{i: F(4 if i < 8 else 2)} for i in range(16)], "Centre Gram normalization")
    for name, word in model["scalar_words"].items():
        state, cost, _, _ = scalar_replay(word, 640)
        wanted = rows(model["physical"][name]) if name in model["physical"] else transpose(ei, 112)
        need(state[:112] == wanted and state[112:] == eye(640)[112:], "Common-frame map and restoration " + name)
        expected = {"P": 728, "R": 2892, "metric_inverse_adjoint_E": 3628}.get(name, 3308)
        need(cost == expected, "Common-frame price " + name)
    return {"family_dimensions": generic, "invariant_diagonal_space_dimensions": list(range(5, 25)),
            "actual_blocks": dict(sizes), "rank_E_minus_P": 16, "rank_E_minus_I": 32,
            "physical_P_nonzeros": 160, "physical_Gram": [4]*8 + [2]*8}


def tariff(gate):
    op, _, _, raw = gate
    c = F(raw)
    a, b = abs(c.numerator), c.denominator
    need(a > 0 and b & (b-1) == 0, "Dyadic coefficient")
    if op == "scale":
        need(a & (a-1) == 0, "Unit scale")
        return 2*(abs(a.bit_length()-b.bit_length()) + (c < 0))
    need(op == "add", "Scalar grammar")
    return 2*(1+a.bit_length()+a.bit_count()+b.bit_length())


def scalar_replay(gates, n):
    state, cost, peak, height = eye(n), 0, F(1), 0
    for gate in gates:
        op, target, origin, raw = gate
        c = F(raw)
        if op == "add":
            need(target != origin, "Distinct fields")
            for j, v in state[origin].items():
                put(state[target], j, c*v)
        else:
            need(op == "scale" and origin is None, "Scale grammar")
            state[target] = {j: c*v for j, v in state[target].items() if c*v}
        cost += tariff(gate)
        peak = max(peak, sum(map(abs, state[target].values()), F(0)))
        for v in state[target].values():
            need(v.denominator & (v.denominator-1) == 0, "Dyadic prefix")
            height = max(height, v.denominator.bit_length()-1)
    return state, cost, peak, height


@lru_cache(None)
def span(vectors):
    values = {0}
    for v in vectors:
        values |= {x ^ v for x in values}
    return frozenset(values)


def word_check(word, expected, profile, scalar):
    current = list(word["start"])
    progress, census, gates = Counter(), Counter(), []
    for event in word["events"]:
        if event[0] == "native":
            _, field, old, new, dimension, key = event
            need(0 <= field < 224 and current[field] == old, "Native entry")
            need(span(tuple(word["frames"][old])) < span(tuple(word["frames"][new])), "Strict nested advance")
            need(dimension == len(word["frames"][new])-len(word["frames"][old]) == word["native_recipes"][key]["rank"], "Native rank")
            need(key == str(old)+":"+str(new), "Ordered recipe")
            current[field] = new
            progress[field] += dimension
            census[dimension] += 1
        else:
            need(event[0] == "scalar", "Event grammar")
            _, gate, frame = event
            _, target, origin, _ = gate
            need(0 <= target < 224 and current[target] == frame, "Scalar target access")
            if origin is not None:
                need(0 <= origin < 224 and current[origin] == frame, "Scalar source access")
            gates.append(gate)
    need(current == word["final"] and census == profile, "Final frames and native census")
    need(all(progress[p] == 8 for p in range(224)), "Data advance mass")
    state, cost, peak, height = scalar_replay(gates, 640)
    need(state == expected, "All 640 arbitrary columns")
    need(state[224:] == eye(640)[224:] and current[224:] == word["start"][224:], "Outside values and frames restored")
    need(cost == scalar, "Native scalar price")
    return {"scalar_real": cost, "prefix_one_norm": str(peak), "binary_height": height,
            "native_profile": dict(census), "native_mass": sum(k*v for k, v in census.items()),
            "native_children": sum(census.values()), "columns": 640, "outside_fields": 416}


def field_projection(word, combine):
    projected = [[] for _ in range(224)]
    scalar_index = 0
    for index, event in enumerate(word["events"]):
        if event[0] == "native":
            _, field, old, new, dimension, _ = event
            seq = projected[field]
            if combine and seq and seq[-1][0] == "native":
                need(seq[-1][2] == old, "Original chain joins")
                seq[-1][2] = new
                seq[-1][3] += dimension
                seq[-1][4].append(index)
            else:
                seq.append(["native", old, new, dimension, [index]])
        else:
            for field in (event[1][1], event[1][2]):
                if field is not None:
                    projected[field].append(["scalar", scalar_index])
            scalar_index += 1
    return projected


def coalescing_check(original, result):
    old_scalars = [e for e in original["events"] if e[0] == "scalar"]
    new_scalars = [e for e in result["events"] if e[0] == "scalar"]
    need(old_scalars == new_scalars, "Every scalar gate and its global order")
    old, new = field_projection(original, True), field_projection(result, False)
    chains = {row["event"]: row for row in result["coalesced_native_chains"]}
    need(len(chains) == sum(e[0] == "native" for e in result["events"]), "One chain record per new native event")
    for field, (a, b) in enumerate(zip(old, new)):
        need(len(a) == len(b), "Same per-field scalar barriers")
        for source, target in zip(a, b):
            if source[0] == "scalar":
                need(source == target, "Same scalar use cut")
                continue
            need(source[:4] == target[:4], "Same total frame map between scalar uses")
            chain = chains[target[4][0]]
            need(chain["source_events"] == source[4], "Independent source-event chain")
            need((chain["field"], chain["old"], chain["new"], chain["rank"]) == (field, *source[1:4]), "Chain metadata")
    for key in ("frames", "start", "final", "endpoint_adapters"):
        need(original[key] == result[key], "Same physical boundary " + key)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    package = args.package.resolve()
    frozen = package / "frozen"
    manifest = read(package / "SOURCES.json")
    for name, entry in manifest["frozen_files"].items():
        need(sha256((frozen/name).read_bytes()).hexdigest() == entry["sha256"], "Frozen input pin " + name)
    directory = frozen / "lanes/oblique-native-20261017/signed-metric-reciprocal-20261020"
    original = read(directory / "native-normal/NATIVE.json.gz")
    coalesced = read(directory / "coalesced-normal/NATIVE.json.gz")
    model = read(directory / "model-normal-v2/RESPONSE.json.gz")
    need(original["model"] == coalesced["model"] == model, "Same model in all payloads")
    model_report = check_model(model)
    word_reports = {}
    for provider in ("base", "extra"):
        for name, old in original["providers"][provider].items():
            response = rows(model["physical"]["E" if name in ("forward_E", "backward_transpose_E") else "inverse_adjoint_E"])
            expected = eye(640)
            for i, row in enumerate(response):
                for j, value in row.items():
                    put(expected[j if name.startswith("backward") else 112+i], 112+i if name.startswith("backward") else j,
                        -value if name.startswith("backward") else value)
            scalar = 7080 if name.endswith("by_metric") else 6440
            old_report = word_check(old, expected, {1: 1520, 2: 64, 3: 48}, scalar)
            new = coalesced["providers"][provider][name]
            new_report = word_check(new, expected, {1: 971, 2: 237, 3: 46, 4: 12, 5: 5, 6: 11, 7: 10}, scalar)
            coalescing_check(old, new)
            need((old_report["prefix_one_norm"], old_report["binary_height"]) ==
                 (new_report["prefix_one_norm"], new_report["binary_height"]), "Unchanged prefix bounds")
            word_reports[provider+"/"+name] = {"original": old_report, "coalesced": new_report}

    phase_path = frozen / "lanes/interface-proof/verify_native_lift.py"
    spec = importlib.util.spec_from_file_location("frozen_exact_phase", phase_path)
    phase = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(phase)
    first = coalesced["providers"]["base"]["forward_E"]
    inherited = original["providers"]["base"]["forward_E"]["native_recipes"]
    fresh = []
    for key, record in first["native_recipes"].items():
        if key in inherited:
            need(record == inherited[key], "Inherited phase record")
            continue
        a, b = map(int, key.split(":"))
        actual = phase.recipe(record)
        target = phase.adjoint(phase.frame(first["frames"][a], 9)) + phase.frame(first["frames"][b], 9)
        phase.equal(actual, target, "Fresh recipe " + key)
        fresh.append(key)
    need(len(fresh) == 206, "Fresh phase census")
    for provider in coalesced["providers"].values():
        for word in provider.values():
            need(word["native_recipes"] == first["native_recipes"], "All words use the checked recipes")

    bad = deepcopy(first["native_recipes"][fresh[0]])
    bad["left"]["phase"] = (bad["left"]["phase"]+1) % 4
    a, b = map(int, fresh[0].split(":"))
    try:
        phase.equal(phase.recipe(bad), phase.adjoint(phase.frame(first["frames"][a], 9)) + phase.frame(first["frames"][b], 9), "Changed phase")
    except ValueError:
        phase_rejected = True
    else:
        raise ValueError("Changed phase accepted")
    bad = deepcopy(first)
    scalar_event = next(e for e in bad["events"] if e[0] == "scalar")
    scalar_event[2] = (scalar_event[2]+1) % len(bad["frames"])
    try:
        coalescing_check(original["providers"]["base"]["forward_E"], bad)
    except ValueError:
        scalar_rejected = True
    else:
        raise ValueError("Changed scalar cut accepted")

    for name, entry in manifest["frozen_files"].items():
        need(sha256((frozen/name).read_bytes()).hexdigest() == entry["sha256"], "Input unchanged " + name)
    result = {"status": "PASS_INDEPENDENT_PUBLICATION_REVIEW", "python": sys.version,
              "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "source_manifest_sha256": sha256((package/"SOURCES.json").read_bytes()).hexdigest(),
              "model": model_report, "words": word_reports, "fresh_phase_checks": len(fresh),
              "phase_engine_sha256": sha256(phase_path.read_bytes()).hexdigest(),
              "phase_engine_scope": "Reused pinned compiler-independent exact Pauli and reference-column engine. No producer interpreter was imported.",
              "negative_controls": {"changed_global_phase_rejected": phase_rejected, "changed_scalar_cut_rejected": scalar_rejected},
              "frozen_inputs_unchanged": len(manifest["frozen_files"]), "elapsed_seconds": round(time.monotonic()-start, 3)}
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(result["status"], flush=True)


if __name__ == "__main__":
    main()
