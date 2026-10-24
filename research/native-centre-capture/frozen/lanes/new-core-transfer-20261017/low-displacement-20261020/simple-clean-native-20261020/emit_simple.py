#!/usr/bin/env python3
"""Emit the direct clean self-response and its selected dual."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / "clean-late-exchange-20261020"
PINS = {
    "helper": (PREVIOUS / "emit_clean_exchange.py",
               "91ee4ce54a5774dfdec7ac0a83f78c5076ef14d0ee30f2dcc7ecf448b869ecbc"),
    "source": (PREVIOUS / "run-normal/CLEAN-LATE-EXCHANGE.json.gz",
               "b0432322c28ad3a03af8da550a0b7c7df048c7ff5a0664acc7f78efffcffd083"),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def read(name):
    path, pin = PINS[name]
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Pinned source " + name)
    return raw


read("helper")
spec = importlib.util.spec_from_file_location("simple_clean_base", PINS["helper"][0])
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
n = base.n


def dual(word, permutation):
    result = deepcopy(word)
    for event in result["events"]:
        if event[0] == "native":
            event[1] = permutation[event[1]]
        else:
            op, target, source, coefficient = event[1]
            if op == "add":
                event[1] = [op, permutation[source], permutation[target], str(-F(coefficient))]
            else:
                need(op == "scale", "The scalar grammar")
                event[1] = [op, permutation[target], None, str(1 / F(coefficient))]
    for key in ("start", "final"):
        result[key] = [word[key][permutation[p]] for p in range(640)]
        need(result[key] == word[key], "The selected physical types agree")
    result["wire_permutation"] = {str(p): q for p, q in enumerate(permutation) if p != q}
    return result


def replay(word, expected, kernels):
    current = list(word["start"])
    state = n.r.identity(640)
    maximum, height = F(1), 0
    for event in word["events"]:
        if event[0] == "native":
            _, field, old, new, rank, key = event
            need(current[field] == old, "The exact native input type")
            need(kernels[key]["rank"] == rank
                 and kernels[key]["edge"] == [old, new], "The exact physical native edge")
            current[field] = new
            continue
        need(event[0] == "scalar", "Every event is priced")
        gate, frame = event[1:]
        op, target, source, coefficient = gate
        coefficient = F(coefficient)
        need(current[target] == frame, "The exact scalar target type")
        if op == "add":
            need(target != source and current[source] == frame, "The exact scalar source type")
            n.r.add(state[target], state[source], coefficient)
        else:
            need(op == "scale" and coefficient, "An invertible real scale")
            state[target] = {j: value * coefficient for j, value in state[target].items()
                             if value * coefficient}
        maximum = max(maximum, sum(abs(value) for value in state[target].values()))
        for value in state[target].values():
            d = value.denominator
            need(d & (d - 1) == 0, "Dyadic content")
            height = max(height, d.bit_length() - 1)
    need(state == expected, "All640 independent input columns")
    need(state[224:] == n.r.identity(640)[224:], "All416 helpers remain unchanged")
    need(current == word["final"], "Every final physical type")
    profile = Counter(event[4] for event in word["events"] if event[0] == "native")
    prices = {name: base.base.price(word["events"][a:b])
              for name, (a, b) in word["stage_ranges"].items()}
    return {
        "all_independent_input_columns": 640, "unchanged_arbitrary_helpers": 416,
        "native_profile": dict(sorted(profile.items())), "native_children": sum(profile.values()),
        "native_mass": sum(rank * count for rank, count in profile.items()),
        "real_scalar_primitives": sum(prices.values()), "scalar_stage_prices": prices,
        "native_side_map_upper_bound": 2 * (sum(profile.values()) - profile[9]),
        "boundary_adapter_calls": 0, "extra_owned_fields": 0, "extra_private_fields": 0,
        "odd_divisions": 0, "content_prefix_row_one_norm": str(maximum),
        "additional_content_binary_height": height,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    source = json.loads(read("source"))
    capture = json.loads(base.read("capture"))
    ports, pivots = source["ports"], source["selected_ports"]
    selected, ordinary = set(pivots), sorted(set(range(112)) - set(pivots))
    code = n.rows(source["code"])
    need(code == n.rows(capture["code"]), "The actual FULL row code")
    frames = [(), n.phase.fourier(9)]
    frames += [(("C", q, 1),) for q in ports]
    frames += [(("C", q, -1),) + n.phase.fourier(9) for q in ports]
    kernels = {}
    full = n.compiler.fourier(9)
    full_recipe = source["providers"]["base"]["I"]["native_recipes"]["capture-full"]
    need(full_recipe == source["providers"]["extra"]["I"]["native_recipes"]["capture-full"],
         "The same exact direct FULL kernel")
    kernels["full"] = {"rank": 9, "edge": [0, 1], "recipe": full_recipe}
    n.phase.equal(n.phase.recipe(full_recipe), frames[1], "Exact direct FULL phase")
    for p, q in enumerate(ports):
        operation = n.compiler.cgate(9, q, -1).then(full)
        recipe, _ = n.compiler.lower_child(operation)
        need(recipe["rank"] == 8, "The direct source rank is eight")
        edge = [2 + p, 1]
        n.phase.equal(n.phase.recipe(recipe), n.phase.adjoint(frames[edge[0]]) + frames[edge[1]],
                      "Exact direct line-to-FULL phase " + str(p))
        kernels["advance:" + str(p)] = {"rank": 8, "edge": edge, "recipe": recipe}
        if p in ordinary:
            recipe, _ = n.compiler.lower_child(n.compiler.cgate(9, q, -1))
            need(recipe["rank"] == 1, "The exact negative line rank")
            edge = [1, 114 + p]
            n.phase.equal(n.phase.recipe(recipe),
                          n.phase.adjoint(frames[edge[0]]) + frames[edge[1]],
                          "Exact ordinary exit and FULL commutation " + str(p))
            kernels["exit:" + str(p)] = {"rank": 1, "edge": edge, "recipe": recipe}
        if (p + 1) % 16 == 0:
            print("Exact port kernels", p + 1, "/112", flush=True)
    start, final = [0] * 640, [0] * 640
    for p in range(112):
        start[p], final[p] = 2 + p, 1
        start[112 + p] = 2 + p if p in selected else 0
        final[112 + p] = 1 if p in selected else 114 + p
    events, ranges = [], {}

    def stage(name, records):
        a = len(events)
        events.extend(records)
        ranges[name] = [a, len(events)]

    stage("source_progress", [["native", p, 2 + p, 1, 8, "advance:" + str(p)]
                              for p in range(112)])
    stage("selected_progress", [["native", 112 + p, 2 + p, 1, 8, "advance:" + str(p)]
                                for p in pivots])
    stage("ordinary_full_progress", [["native", 112 + p, 0, 1, 9, "full"] for p in ordinary])
    stage("ordinary_self_adds", [["scalar", ["add", 112 + p, p, "1"], 1] for p in ordinary])
    stage("ordinary_negative_lines", [["native", 112 + p, 1, 114 + p, 1, "exit:" + str(p)]
                                     for p in ordinary])
    stage("source_row_code", [["scalar", gate, 1] for gate in capture["scalar_word"]])
    rotations = []
    for p in pivots:
        rotations.extend([["scalar", ["add", 112 + p, p, "1"], 1],
                          ["scalar", ["add", p, 112 + p, "-1"], 1],
                          ["scalar", ["add", 112 + p, p, "1"], 1]])
    stage("signed_selected_exchanges", rotations)
    forward = {"start": start, "final": final, "events": events, "stage_ranges": ranges}
    expected_forward = n.r.identity(640)
    expected_custom = n.r.identity(640)
    for p in range(112):
        if p in selected:
            expected_forward[p] = {112 + p: F(-1)}
            expected_forward[112 + p] = dict(code[p])
            expected_custom[p] = {112 + p: F(1)}
            expected_custom[112 + p] = {p: F(-1)}
        else:
            n.r.add(expected_forward[112 + p], {p: F(1)})
            n.r.add(expected_custom[p], {112 + p: F(-1)})
            for j in pivots:
                n.r.add(expected_custom[p], {112 + j: -code[j].get(p, F(0))})
    permutation = list(range(640))
    for p in pivots:
        permutation[p], permutation[112 + p] = 112 + p, p
    custom = dual(forward, permutation)
    words = {"Fsimple": forward, "Bcustom": custom}
    expected = {"Fsimple": expected_forward, "Bcustom": expected_custom}
    reports = {}
    for name, word in words.items():
        report = replay(word, expected[name], kernels)
        need(report["native_profile"] == {1: 96, 8: 128, 9: 96}
             and report["native_mass"] == 1984 and report["native_children"] == 320,
             "The full native profile")
        need(report["real_scalar_primitives"] == 2912
             and report["scalar_stage_prices"]["ordinary_self_adds"] == 768
             and report["scalar_stage_prices"]["source_row_code"] == 1760
             and report["scalar_stage_prices"]["signed_selected_exchanges"] == 384,
             "Every scalar instruction is priced")
        for stage_name in ("ordinary_self_adds", "source_row_code"):
            bad = deepcopy(word)
            i = next(i for i in range(*ranges[stage_name]) if bad["events"][i][1][0] == "add")
            del bad["events"][i]
            try:
                replay(bad, expected[name], kernels)
            except ValueError:
                pass
            else:
                raise ValueError("A missing " + stage_name + " ADD was accepted")
        reports[name] = report
    transpose_custom = n.r.transpose(expected_custom[:224], 224)
    swapped_transpose = [{} for _ in range(224)]
    for target, row in enumerate(transpose_custom):
        swapped_transpose[permutation[target]] = {permutation[j]: v for j, v in row.items()}
    need(n.r.product(expected_forward[:224], swapped_transpose)
         == n.r.product(swapped_transpose, expected_forward[:224]) == n.r.identity(224),
         "Both exact selected-conjugate inverse-adjoint identities")
    payload = {
        "schema": "direct-simple-clean-native-v1",
        "source_pins": {name: {"path": str(path), "sha256": pin}
                        for name, (path, pin) in PINS.items()},
        "native_dependency_pins": n.PINS, "ports": ports, "selected_ports": pivots,
        "code": source["code"], "physical_frame_circuits": frames, "native_kernels": kernels,
        "words": words, "content_maps": {name: n.r.encoded(rows[:224]) for name, rows in expected.items()},
        "provider_scope": "The same complete direct word applies to both pinned providers; their common ports and row code are used.",
        "physical_contract": {
            "input": "X=Q(a,u), selectedY=Q_P z, ordinaryY=v.",
            "Fsimple": "Output content (-z,u,a+Bu,v+u).",
            "Bcustom": "Output content (z,u-B^Tz-v,-a,v).",
            "output": "X and selectedY have F9; ordinaryY has F9 q_U.",
            "scope": "Direct physical local words. No caller, recursive host or complete supplier bound.",
        },
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(raw)
    for name, word in saved["words"].items():
        need(replay(word, expected[name], saved["native_kernels"]) == reports[name],
             "The complete serialized direct word")
    (args.out / "SIMPLE-CLEAN-NATIVE.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {"status": "PASS_DIRECT_SIMPLE_CLEAN_NATIVE",
               "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "payload_decompressed_sha256": sha256(raw).hexdigest(), "reports": reports,
               "fresh_exact_native_phase_checks": len(kernels),
               "phase_method": "Exact Pauli action and one complete512-entry Gaussian state determine each Clifford including global phase.",
               "both_content_inverse_orders": True,
               "negative_controls": "An omitted self-response or reader ADD is rejected in both words.",
               "scope": payload["physical_contract"]["scope"]}
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
