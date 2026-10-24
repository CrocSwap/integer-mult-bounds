#!/usr/bin/env python3
"""Check two response extensions on the frozen cyclic native paths."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
EMITTER = HERE / "emit_native.py"
EMITTER_PIN = "599987ddfe2fdb8fd4be533d783e24bf40a95b6c69118ec1552a10b06f1d5745"
SOURCE = HERE / "native-normal-v2/NATIVE-PROGRAM.json.gz"
SOURCE_PIN = "e387b082422f085efc8122497cdda0b5211a86b0418af4b9fdbc1da15ac71558"
EIGHT_CLIQUES = [
    [1, 5, 19, 54, 64, 73, 82, 83], [3, 4, 22, 50, 60, 69, 80, 84],
    [6, 35, 38, 39, 40, 77, 85, 86], [8, 12, 45, 88, 103, 107, 108, 109],
    [17, 29, 30, 56, 58, 67, 93, 95], [18, 32, 34, 49, 65, 68, 98, 101],
    [24, 26, 28, 48, 66, 75, 96, 97], [23, 31, 33, 55, 59, 74, 100, 102],
]
if sha256(EMITTER.read_bytes()).hexdigest() != EMITTER_PIN:
    raise ValueError("Frozen native emitter pin")
spec = importlib.util.spec_from_file_location("low_native", EMITTER)
n = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = n
spec.loader.exec_module(n)
r, need = n.r, n.need


def make_model(old, cyclic, kind):
    model = {key: old[key] for key in (
        "ports", "large_ports", "small_ports", "selected_ports", "ordinary_ports",
        "selected_block", "selected_inverse", "vertex_assignments", "small_cliques")}
    large, small = old["large_ports"], old["small_ports"]
    response, inverse = n.rows(old["response"]), n.rows(old["response_inverse"])
    if kind == "reciprocal-large":
        mt = r.transpose(n.rows(old["mode_inverse"]), 112)
        et, eit = r.transpose(inverse, 112), r.transpose(response, 112)
        model["mode_response"] = r.encoded(mt)
        model["mode_inverse"] = r.encoded(r.transpose(n.rows(old["mode_response"]), 112))
        for p in large:
            response[p], inverse[p] = et[p], eit[p]
        word_large = [gate for gate in old["common_frame_words"]["inverse_transpose_E"]
                      if gate[1] in set(large)]
        word_small = [gate for gate in old["common_frame_words"]["E"] if gate[1] in set(small)]
        word = word_large + word_small
        need(r.replay(word)[0] == response, "Partial reciprocal common-frame code")
        model["common_frame_words"] = {
            "E": word, "inverse_E": r.inverse_word(word),
            "transpose_E": r.transpose_word(word),
            "inverse_transpose_E": r.transpose_word(r.inverse_word(word)),
        }
        expected = {"E": response, "inverse_E": inverse,
                    "transpose_E": r.transpose(response, 112),
                    "inverse_transpose_E": r.transpose(inverse, 112)}
        for name, gates in model["common_frame_words"].items():
            need(r.replay(gates)[0] == expected[name] and r.price(gates) == 3210,
                 "Complete reciprocal scalar code and invoice " + name)
        model["extension_scope"] = "Raw backward gives the old E48 inverse, with the old C64 transpose."
    else:
        need(kind == "odd-grid-rank16", "Extension kind")
        h = r.identity(112)
        for pair in cyclic["pair_codes"]:
            for i, p in enumerate(pair["ports"]):
                h[p] = {q: F(pair["matrix"][i][j]) for j, q in enumerate(pair["ports"])}
        hi = r.transpose(h, 112)
        for p in large:
            hi[p] = {q: c / 2 for q, c in hi[p].items()}
        mode, mi = r.identity(112), r.identity(112)
        u, v = [{} for _ in range(112)], []
        for record in old["vertex_assignments"]:
            group, signs = record["ordered_carriers_a_b_c"], record["signs"]
            for i, p in enumerate(group):
                mode[p] = {q: F(int(i == j) - signs[i] * signs[j])
                           for j, q in enumerate(group) if i != j}
                mi[p] = {q: F(int(i == j)) - F(signs[i] * signs[j], 5)
                         for j, q in enumerate(group)}
                u[p] = {len(v): F(-signs[i])}
            v.append({q: F(signs[j]) for j, q in enumerate(group)})
        response, inverse = r.product(hi, r.product(mode, h)), r.product(hi, r.product(mi, h))
        u, v = r.product(hi, u), r.product(v, h)
        need(sorted(p for group in EIGHT_CLIQUES for p in group) == sorted(small),
             "Eight disjoint eight-cliques cover the actual64 ports")
        for group in EIGHT_CLIQUES:
            need(all((old["ports"][p] & old["ports"][q]).bit_count() % 2 == int(p == q)
                     for p in group for q in group), "Actual orthonormal eight-clique")
            for p in group:
                response[p] = {q: F(-1) for q in group if q != p}
                inverse[p] = {q: F(int(p == q)) - F(1, 7) for q in group}
                u[p] = {len(v): F(-1)}
            v.append({p: F(1) for p in group})
        correction = [dict(row) for row in response]
        for p in range(112):
            r.add(correction[p], {p: F(-1)})
        need(r.product(u, v) == correction and r.rank(u, 16) == r.rank(v, 112) == 16,
             "Exact rank16 correction factor")
        model.update(mode_response=r.encoded(mode), mode_inverse=r.encoded(mi),
                     small_cliques=EIGHT_CLIQUES, correction_U=r.encoded(u), correction_V=r.encoded(v))
        model["extension_scope"] = "Integer native response; inverse requires retained-grid denominators5 and7."
    model["response"], model["response_inverse"] = r.encoded(response), r.encoded(inverse)
    need(r.product(response, inverse) == r.product(inverse, response) == r.identity(112),
         "Both full response inverse orders")
    need(all(p not in row for p, row in enumerate(response)), "Physical zero diagonal")
    correction = [dict(row) for row in response]
    for p in range(112):
        r.add(correction[p], {p: F(-1)})
    model["correction_rank"] = r.rank(correction, 112)
    model["full_determinant"] = str(r.determinant(response))
    selected = old["selected_ports"]
    selected_block = r.restrict(response, selected)
    need(selected_block == n.rows(old["selected_block"]), "The selected block stays L")
    model["selected_inverse_block"] = r.encoded(r.restrict(inverse, selected))
    model["ordinary_determinant"] = str(r.determinant(r.restrict(response, old["ordinary_ports"])))
    if kind == "odd-grid-rank16":
        want = [{j: (F(4 if i == j else 0) + selected_block[i].get(j, F(0))) / 5
                 for j in range(8) if i == j or selected_block[i].get(j)} for i in range(8)]
        need(r.restrict(inverse, selected) == want, "The new inverse principal block is (4I+L)/5")
        need(r.determinant(response) == 35 ** 8
             and F(model["ordinary_determinant"]) == F(7 ** 8 * 31 ** 4, 16),
             "Exact odd-grid principal determinants")
        principal_inverse = [
            {j: F(40 if i == j else 0, 31) - F(10, 31) * selected_block[i].get(j, F(0))
             for j in range(8) if i == j or selected_block[i].get(j)}
            for i in range(8)]
    else:
        principal_inverse = n.rows(old["selected_inverse"])
    need(r.product(r.restrict(inverse, selected), principal_inverse) == r.identity(8),
         "Inverse response selected principal inverse")
    ordinary = old["ordinary_ports"]
    p = [{j: inverse[row][s] for j, s in enumerate(selected) if inverse[row].get(s)}
         for row in ordinary]
    t = [{j: inverse[row][s] for j, s in enumerate(ordinary) if inverse[row].get(s)}
         for row in selected]
    ordinary_inverse = r.restrict(inverse, ordinary)
    for row, correction in zip(ordinary_inverse, r.product(r.product(p, principal_inverse), t)):
        r.add(row, correction, -1)
    ordinary_response = r.restrict(response, ordinary)
    need(r.product(ordinary_response, ordinary_inverse) == r.product(ordinary_inverse, ordinary_response)
         == r.identity(104), "Both new ordinary principal inverse orders")
    model["ordinary_inverse"] = r.encoded(ordinary_inverse)
    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("reciprocal-large", "odd-grid-rank16"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    raw = gzip.decompress(SOURCE.read_bytes())
    need(sha256(raw).hexdigest() == SOURCE_PIN, "Frozen native payload pin")
    source = json.loads(raw)
    old = json.loads(n.read("new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json"))
    cyclic = json.loads(n.read("independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json"))
    model = make_model(old, cyclic, args.kind)
    words = {direction: n.make_word(cyclic, model, direction) for direction in ("forward", "backward")}
    base = source["providers"]["base"]["forward"]
    inherited = {}
    for key, record in base["native_recipes"].items():
        old_frame, new_frame = map(int, key.split(":"))
        inherited[tuple(base["frames"][old_frame]), tuple(base["frames"][new_frame])] = record
    frames = words["forward"]["frames"]
    need(frames == words["backward"]["frames"], "Shared native paths")
    edge_pairs = sorted({(event[2], event[3]) for word in words.values()
                         for event in word["events"] if event[0] == "native"})
    recipes, fresh, reused = {}, 0, 0
    for old_frame, new_frame in edge_pairs:
        pair = tuple(frames[old_frame]), tuple(frames[new_frame])
        if pair in inherited:
            record = inherited[pair]
            reused += 1
        else:
            operation = n.compiler.canonical_frame(9, pair[0]).adjoint().then(
                n.compiler.canonical_frame(9, pair[1]))
            record, _ = n.compiler.lower_child(operation)
            need(record["rank"] == len(pair[1]) - len(pair[0]), "Fresh extension native rank")
            n.phase.equal(n.phase.recipe(record), n.phase.adjoint(n.phase.frame(pair[0], 9))
                          + n.phase.frame(pair[1], 9), "Fresh extension native phase")
            fresh += 1
            if fresh % 100 == 0:
                print("Fresh extension phases", fresh, flush=True)
        recipes[str(old_frame) + ":" + str(new_frame)] = record
    reports = {}
    for direction, word in words.items():
        word["native_recipes"] = recipes
        word["endpoint_adapters"] = base["endpoint_adapters"]
        need(word["start"] == base["start"] and word["final"] == base["final"],
             "The inherited endpoint adapters have identical exact frames")
        for i in set(word["start"] + word["final"]):
            need(word["frames"][i] == base["frames"][i], "Exact endpoint frame basis")
        reports[direction] = n.verify_word(word, n.rows(model["response"]), direction)
    expected_profile = ({1: 1036, 3: 48, 4: 55, 5: 55, 6: 9, 7: 9}
                        if args.kind == "reciprocal-large" else {1: 1520, 2: 64, 3: 48})
    expected_scalar = 5288 if args.kind == "reciprocal-large" else 7384
    for report in reports.values():
        need(report["native_profile"] == expected_profile and report["native_mass"] == 1792
             and report["real_scalar_primitives"] == expected_scalar, "Complete extension invoice")
    payload = {"schema": "low-displacement-native-extension-v1", "kind": args.kind,
               "model": model, "providers": {provider: words for provider in source["providers"]}}
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(raw)
    for provider, directions in saved["providers"].items():
        for direction, word in directions.items():
            need(n.verify_word(word, n.rows(saved["model"]["response"]), direction) == reports[direction],
                 "Serialized extension replay " + provider)
    (args.out / "EXTENSION-PROGRAM.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    checks = {"status": "PASS_" + args.kind.upper().replace("-", "_"),
              "kind": args.kind, "source_native_decompressed_sha256": SOURCE_PIN,
              "source_emitter_sha256": EMITTER_PIN,
              "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "payload_decompressed_sha256": sha256(raw).hexdigest(),
              "fresh_native_phases": fresh, "inherited_native_phases": reused,
              "inherited_endpoint_phases": 224, "reports": reports,
              "full_correction_rank": model["correction_rank"],
              "full_determinant": model["full_determinant"],
              "ordinary_determinant": model["ordinary_determinant"],
              "scope": "Exact local data word. Odd-grid code admission, terminal, helper progress and recursive supplier duties are separate."}
    (args.out / "EXTENSION-CHECKS.json").write_text(json.dumps(checks, indent=2, sort_keys=True) + "\n")
    print(json.dumps(checks, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
