#!/usr/bin/env python3
"""Emit a clean 24-coordinate unitary centre interface."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
LANES = PARENT.parents[1]
PINS = {
    "code_helper": (PARENT / "metric-completion-20261020/check_twenty_four.py",
                    "5eb67764619b90a4dc2dbcf80466823dfe0a81f7872a0a334193f101249018ee"),
    "code": (PARENT / "metric-completion-20261020/twenty-four-v2-normal/UNITARY-24.json.gz",
             "9be7deb70acfc20d98408c84d59a24dbd6e2eddaea408958ec64b6003eb75f8c"),
    "code_freeze": (PARENT / "metric-completion-20261020/TWENTY-FOUR-FREEZE.json",
                    "3fda436c0390fb8ef2ee72b4d9fe6ccbfc0ea994208f4d962bb9f43960af7a82"),
    "native_helper": (PARENT / "emit_native.py",
                      "599987ddfe2fdb8fd4be533d783e24bf40a95b6c69118ec1552a10b06f1d5745"),
    "native": (PARENT / "odd16-normal-v2/EXTENSION-PROGRAM.json.gz",
               "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4"),
    "formation": (PARENT / "row-only-capture-20261020/direct-normal/DIRECT-FULL-CAPTURE.json.gz",
                  "fa3342f8b4ddf286f6f67922f4184486ec0162610e4de6a457de3eed0750504c"),
    "line_prefix": (PARENT / "fixed-reader-reuse-20261020/prefix-normal/CARRIER-PREFIX.json.gz",
                    "54c561cfc49ad3fe1258ba5a8760eeadaa11784272cf458e2a6e54403a0e655e"),
    "native_review": (LANES / "new-native-recipes-20261017/low-displacement-review-20261020/EXTENSIONS-REVIEW-FREEZE.json",
                      "c8fccfbe49ddd8747095a43aa1c1c59b0270bbbf73d94a317a79113191e4e34c"),
    "formation_review": (LANES / "new-native-recipes-20261017/row-capture-native-review-20261020/FREEZE.json",
                         "488dc693d6e7d48e8024455c9c3f2f899f94a8e9058aef28ad38f7c46c7d8532"),
    "line_review": (LANES / "new-native-recipes-20261017/line-entry-reuse-review-20261020/FREEZE.json",
                    "cc5ed3b0ecc6eb5cec48f8baead43ec813042c3e83cd68104b7745366c13c55c"),
}


def need(value, message):
    if not value:
        raise ValueError(message)


def read(name):
    path, pin = PINS[name]
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Pinned input " + name)
    return raw


def module(name, key):
    read(key)
    spec = importlib.util.spec_from_file_location(name, PINS[key][0])
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


c = module("clean_unitary_code", "code_helper")
n = module("clean_unitary_native", "native_helper")
g = c.g
ZERO, ONE = g.ZERO, g.ONE
MACRO_CACHE = {}


def component_adjoint(word, permutation):
    result = []
    for op, target, source, coefficient in word:
        value = F(coefficient)
        def remap(component):
            return 2 * permutation[component // 2] + component % 2
        if op == "add":
            result.append([op, remap(source), remap(target), str(-value)])
        else:
            need(op == "scale" and value, "An invertible component scale")
            result.append([op, remap(target), None, str(1 / value)])
    return result


def gaussian_add(target, source, coefficient, frame):
    a, b = coefficient
    components = []
    for t, s, value in ((2 * target, 2 * source, a),
                        (2 * target, 2 * source + 1, -b),
                        (2 * target + 1, 2 * source, b),
                        (2 * target + 1, 2 * source + 1, a)):
        if value:
            components.append(["add", t, s, str(value)])
    return ["gaussian_add", target, source, [str(a), str(b)], frame, components]


def check_component_block(fields, instructions, expected):
    positions = {p: i for i, p in enumerate(fields)}
    local = []
    for op, target, source, coefficient in instructions:
        need(target // 2 in positions and (source is None or source // 2 in positions),
             "Every component stays inside its complete macro")
        local.append([op, 2 * positions[target // 2] + target % 2,
                      None if source is None else 2 * positions[source // 2] + source % 2,
                      coefficient])
    key = json.dumps([local, g.serialize(expected)], separators=(",", ":"))
    if key not in MACRO_CACHE:
        actual, report = c.b.replay(local, 2 * len(fields))
        need(actual == c.u.realify(expected, len(fields)), "The complete component macro is complex-linear")
        need(report["scalar"] % 2 == 0, "The real component tariff is integral")
        report["scalar"] //= 2
        MACRO_CACHE[key] = report
    return MACRO_CACHE[key]


def event_price(event):
    if event[0] == "native":
        return 0
    if event[0] == "scalar":
        return n.r.price([event[1]])
    instructions = event[5] if event[0] == "gaussian_add" else event[2]
    cost = n.r.price(instructions)
    need(cost % 2 == 0, "An integral real scalar invoice")
    return cost // 2


def verify(word, expected):
    current = list(word["start"])
    state = g.eye(640)
    maximum = F(1)
    macro_maximum = F(1)
    for event in word["events"]:
        kind = event[0]
        if kind == "native":
            _, field, old, new, rank, key = event
            need(current[field] == old, "The native input frame")
            need(len(n.basis(word["frames"][old] + word["frames"][new]))
                 == len(word["frames"][new]), "The native frame inclusion")
            need(rank == len(word["frames"][new]) - len(word["frames"][old])
                 == word["native_recipes"][key]["rank"], "The exact native rank")
            current[field] = new
            continue
        if kind == "scalar":
            op, target, source, coefficient = event[1]
            frame = event[2]
            need(current[target] == frame, "The real-complex scalar target frame")
            value = g.real(coefficient)
            if op == "add":
                need(target != source and current[source] == frame, "The real-complex scalar source frame")
                for j, x in state[source].items():
                    g.put(state[target], j, g.times(value, x))
            else:
                need(op == "scale", "The scalar grammar")
                state[target] = {j: g.times(value, x) for j, x in state[target].items()}
            changed = [target]
        elif kind == "gaussian_add":
            _, target, source, raw, frame, components = event
            need(target != source and current[target] == current[source] == frame,
                 "The complete Gaussian macro has one common complex frame")
            value = F(raw[0]), F(raw[1])
            report = check_component_block([target, source], components,
                                            [{0: ONE, 1: value}, {1: ONE}])
            macro_maximum = max(macro_maximum, F(report["prefix_row_one_norm"]))
            for j, x in state[source].items():
                g.put(state[target], j, g.times(value, x))
            changed = [target]
        else:
            need(kind == "component_code", "The complete event grammar")
            _, fields, components, raw_matrix, frame = event
            need(len(fields) == len(set(fields)) and all(current[p] == frame for p in fields),
                 "The complete code macro has one common complex frame")
            matrix = c.rows(raw_matrix)
            report = check_component_block(fields, components, matrix)
            macro_maximum = max(macro_maximum, F(report["prefix_row_one_norm"]))
            result = g.multiply(matrix, [state[p] for p in fields])
            for p, row in zip(fields, result):
                state[p] = row
            changed = fields
        for p in changed:
            maximum = max(maximum, sum(abs(a) + abs(b) for a, b in state[p].values()))
    need(current == word["final"], "All640 final frames")
    need(state == expected, "All640 independent complex input columns")
    need(state[224:] == g.eye(640)[224:], "All416 arbitrary helper fields")
    profile = Counter(e[4] for e in word["events"] if e[0] == "native")
    full = sum(e[0] == "native" and e[5] == "direct-full" for e in word["events"])
    return {
        "all_complex_input_columns": 640, "all_real_input_columns": 1280,
        "unchanged_arbitrary_helpers": 416, "owned_fields": 0, "private_fields": 0,
        "native_profile": dict(sorted(profile.items())), "native_mass": sum(k * v for k, v in profile.items()),
        "native_children": sum(profile.values()),
        "native_side_map_upper_bound": 2 * (sum(profile.values()) - full),
        "direct_full_identity_wrapper_children": full,
        "explicit_input_views": len(word["input_views"]), "explicit_output_views": len(word["output_views"]),
        "scalar": sum(event_price(e) for e in word["events"]),
        "scalar_stage_prices": {name: sum(event_price(e) for e in word["events"][start:end])
                               for name, (start, end) in word["stage_ranges"].items()},
        "complete_macro_content_component_l1": str(maximum),
        "local_macro_prefix_component_l1": str(macro_maximum),
        "prefix_scope": "Macro endpoints have the complex frame. Atomic component bounds refer only to that macro's physical input fields.",
        "odd_divisions": 0,
    }


def maps(code, selected):
    direct = g.eye(224)
    for p in range(112):
        if p in selected:
            direct[p] = {112 + p: g.real(-1)}
            direct[112 + p] = dict(code[p])
        else:
            direct[p] = dict(code[p])
            direct[112 + p] = dict(code[p])
            g.put(direct[112 + p], 112 + p, ONE)
    w = [{112 + p if p in selected else p: ONE} for p in range(112)]
    inverse = g.multiply(g.adjoint(code, 112), w)
    for p in range(112):
        inverse.append({p: g.real(-1)} if p in selected else
                       {112 + p: ONE, p: g.real(-1)})
    need(g.multiply(direct, inverse) == g.multiply(inverse, direct) == g.eye(224),
         "Both forward content inverse orders")
    return direct, inverse


def conjugate(matrix, permutation):
    result = [{} for _ in matrix]
    for p, row in enumerate(matrix):
        result[permutation[p]] = {permutation[j]: value for j, value in row.items()}
    return result


def lower_dual(original, permutation):
    word = deepcopy(original)
    events = []
    for event in original["events"]:
        kind = event[0]
        if kind == "native":
            changed = deepcopy(event)
            changed[1] = permutation[event[1]]
        elif kind == "scalar":
            op, target, source, coefficient = event[1]
            value = F(coefficient)
            gate = ([op, permutation[source], permutation[target], str(-value)] if op == "add" else
                    [op, permutation[target], None, str(1 / value)])
            changed = ["scalar", gate, event[2]]
        elif kind == "gaussian_add":
            _, target, source, raw, frame, components = event
            value = g.neg(g.conjugate((F(raw[0]), F(raw[1]))))
            changed = ["gaussian_add", permutation[source], permutation[target],
                       [str(x) for x in value], frame, component_adjoint(components, permutation)]
        else:
            need(kind == "component_code", "The dual macro grammar")
            _, fields, components, matrix, frame = event
            unitary = c.rows(matrix)
            need(g.multiply(unitary, g.adjoint(unitary, len(fields))) == g.eye(len(fields)),
                 "The complete source code is unitary")
            changed = ["component_code", [permutation[p] for p in fields],
                       component_adjoint(components, permutation), deepcopy(matrix), frame]
        events.append(changed)
    word["events"] = events
    for key in ("start", "final"):
        word[key] = [original[key][permutation[p]] for p in range(640)]
        need(word[key] == original[key], "The selected endpoint types are symmetric")
    for view in word["input_views"]:
        view["field"] = permutation[view["field"]]
    word["input_views"].sort(key=lambda v: v["field"])
    old = {v["field"]: v for v in original["input_views"]}
    for view in word["input_views"]:
        need(all(view[k] == old[view["field"]][k] for k in ("port", "frame", "left", "right", "rank")),
             "The full same-port input monomial is invariant")
    need(all(permutation[112 + view["port"]] == 112 + view["port"] for view in word["output_views"]),
         "All ordinary output views keep their field")
    word["wire_permutation"] = {str(p): q for p, q in enumerate(permutation) if p != q}
    return word


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    for name in PINS:
        read(name)
    code_source = json.loads(read("code"))
    native = json.loads(read("native"))
    formation = json.loads(read("formation"))
    prefix = json.loads(read("line_prefix"))
    cyclic = json.loads(c.b.read("cyclic"))
    code = c.rows(code_source["code"])
    mode = c.rows(code_source["mode_code"])
    old_mode = n.rows(native["model"]["mode_response"])
    old_physical = n.rows(native["model"]["response"])
    selected = set(code_source["selected_full_ports"])
    selected_fields = {112 + p for p in selected}
    parameters = {x["id"]: x for x in cyclic["parameters"]}
    forward, inverse = maps(code, selected)
    dual = g.adjoint(inverse, 224)
    dual_inverse = g.adjoint(forward, 224)
    permutation = list(range(640))
    for p in selected:
        permutation[p], permutation[112 + p] = 112 + p, p
    swap = conjugate(dual, permutation[:224])
    swap_inverse = conjugate(dual_inverse, permutation[:224])
    need(g.multiply(swap, swap_inverse) == g.multiply(swap_inverse, swap) == g.eye(224),
         "Both selected-conjugate content inverse orders")
    formula = g.eye(224)
    for p in range(112):
        formula[p] = {112 + j if j in selected else j: z for j, z in code[p].items()}
        if p in selected:
            formula[112 + p] = {p: g.real(-1)}
        else:
            g.put(formula[p], 112 + p, g.real(-1))
    need(formula == swap, "The direct unitary Bswap formula")
    providers, reports, fresh_phases = {}, {}, []
    for provider, source_directions in native["providers"].items():
        original = source_directions["forward"]
        old_formation = formation["providers"][provider]
        old_prefix = prefix["providers"][provider]
        transfers = {x["event"]: x for x in original["transfer_records"]}
        kept, retained, retunings = [], [], []
        for index, event in enumerate(original["events"]):
            target = event[1] if event[0] == "native" else event[1][1]
            if target in selected_fields:
                continue
            if event[0] == "scalar" and event[1][0] == "add":
                need(event[1][2] not in selected_fields, "No retained read of a removed target")
            retained.append(index)
            if index not in transfers:
                kept.append(deepcopy(event))
                continue
            record = transfers[index]
            if record["part"] == "large48":
                parameter = parameters[record["parameter"]]
                ports = cyclic["cyclic_carriers"][parameter["vertex"]]
                p, j = ports[parameter["row"]], ports[parameter["column"]]
                old_coefficient = old_mode[p][j]
            else:
                p, j = record["target_port"], record["source_port"]
                old_coefficient = old_physical[p][j]
            op, target, source, coefficient = event[1]
            need(op == "add" and p not in selected, "An ordinary transfer slot")
            ratio = F(coefficient) / old_coefficient
            value = tuple(ratio * z for z in mode[p].get(j, ZERO))
            retunings.append({"original_event": index, "mode_target": p, "mode_source": j,
                              "coefficient": [str(x) for x in value]})
            if value != ZERO:
                kept.append(gaussian_add(target, source, value, event[2]))
        used = {e[5] for e in kept if e[0] == "native"}
        recipes = {k: deepcopy(original["native_recipes"][k]) for k in used}
        source_views = {v["port"]: v for v in old_formation["input_views"]}
        output_views = [deepcopy(v) for v in old_formation["output_views"] if v["port"] not in selected]
        need(len(output_views) == 88, "All ordinary output views are inherited")
        providers[provider], reports[provider] = {}, {}
        for entry in ("I", "Q"):
            word = {
                "frames": deepcopy(original["frames"]), "start": list(original["start"]),
                "final": list(original["final"]), "events": deepcopy(kept),
                "native_recipes": deepcopy(recipes),
                "input_views": [{**deepcopy(v), "field": p} for p, v in sorted(source_views.items())],
                "output_views": deepcopy(output_views),
                "retained_original_event_indices": retained, "transfer_retunings": retunings,
                "stage_ranges": {"retained_retuned_core": [0, len(kept)]},
            }
            begin = len(word["events"])
            for p in sorted(selected):
                if entry == "I":
                    key, old, rank = "direct-full", 0, 9
                    word["native_recipes"][key] = deepcopy(old_formation["native_recipes"]["capture-full"])
                else:
                    key, old, rank = "unitary-line:" + str(p), original["start"][p], 8
                    word["start"][112 + p] = old
                    old_key = "capture-line:" + str(p)
                    if old_key in old_prefix["native_recipes"]:
                        recipe = deepcopy(old_prefix["native_recipes"][old_key])
                    else:
                        before = n.compiler.canonical_frame(9, tuple(word["frames"][old]))
                        after = n.compiler.canonical_frame(9, tuple(word["frames"][1]))
                        recipe, _ = n.compiler.lower_child(before.adjoint().then(after))
                        circuit = n.phase.adjoint(n.phase.frame(word["frames"][old], 9)) + n.phase.frame(word["frames"][1], 9)
                        n.phase.equal(n.phase.recipe(recipe), circuit, "Fresh selected Q-to-FULL child")
                        fresh_phases.append({"provider": provider, "port": p, "recipe": recipe, "circuit": circuit})
                    need(recipe["rank"] == 8, "The exact selected line progress")
                    word["native_recipes"][key] = recipe
                    word["input_views"].append({**deepcopy(source_views[p]), "field": 112 + p,
                                                "role": "selected_target", "source_entry_port": p})
                word["events"].append(["native", 112 + p, old, 1, rank, key])
                word["final"][112 + p] = 1
            word["stage_ranges"]["selected_progress"] = [begin, len(word["events"])]
            begin = len(word["events"])
            word["events"].append(["component_code", list(range(112)),
                                   deepcopy(code_source["component_words"]["code"]),
                                   deepcopy(code_source["code"]), 1])
            word["stage_ranges"]["source_unitary_code"] = [begin, len(word["events"])]
            begin = len(word["events"])
            for p in sorted(selected):
                word["events"].extend([
                    ["scalar", ["add", 112 + p, p, "1"], 1],
                    ["scalar", ["add", p, 112 + p, "-1"], 1],
                    ["scalar", ["add", 112 + p, p, "1"], 1],
                ])
            word["stage_ranges"]["signed_selected_exchanges"] = [begin, len(word["events"])]
            word["input_views"].sort(key=lambda v: v["field"])
            report = verify(word, forward + g.eye(640)[224:])
            need(report["native_profile"] == {1: 1328, 2: 64, 3: 48, 9 if entry == "I" else 8: 24},
                 "The complete24-coordinate native profile")
            need(report["scalar_stage_prices"]["source_unitary_code"] == 8052
                 and report["scalar_stage_prices"]["signed_selected_exchanges"] == 576,
                 "The complete paid code and exchanges")
            providers[provider]["forward_" + entry] = word
            reports[provider]["forward_" + entry] = report
        for name, perm, expected in (
                ("inverse_adjoint_Q", list(range(640)), dual),
                ("selected_conjugate_Q", permutation, swap)):
            word = lower_dual(providers[provider]["forward_Q"], perm)
            providers[provider][name] = word
            reports[provider][name] = verify(word, expected + g.eye(640)[224:])
        print(json.dumps({"provider": provider, "reports": reports[provider]}), flush=True)
    content_maps = {"forward_I": forward, "forward_Q": forward,
                    "inverse_adjoint_Q": dual, "selected_conjugate_Q": swap}
    inverse_maps = {"forward_I": inverse, "forward_Q": inverse,
                    "inverse_adjoint_Q": dual_inverse, "selected_conjugate_Q": swap_inverse}
    payload = {
        "schema": "clean-unitary-24-centre-native-v1",
        "source_pins": {name: {"path": str(path), "sha256": pin} for name, (path, pin) in PINS.items()},
        "ports": native["model"]["ports"], "selected_ports": sorted(selected),
        "code": code_source["code"], "inverse_and_adjoint_code": code_source["inverse_and_adjoint"],
        "content_maps": {name: g.serialize(value) for name, value in content_maps.items()},
        "inverse_content_maps": {name: g.serialize(value) for name, value in inverse_maps.items()},
        "providers": providers, "fresh_phase_records": fresh_phases,
        "component_contract": "Component operations occur only inside a complete contiguous complex-linear macro. There is no native or map interleaving. Only the macro endpoints have the common complex frame.",
        "physical_contract": {
            "input_I": "X=Q x; Y_P=z; Y_R=v.",
            "input_Q": "X=Q x; Y_P=Q_P z; Y_R=v.",
            "forward_content": "Put w=Cx. X_P=-z; X_R=w_R; Y_P=w_P; Y_R=v+w_R.",
            "conjugate_content": "Put w=C(z,u), where x=(a,u). X_P=w_P; X_R=w_R-v; Y_P=-a; Y_R=v.",
            "output_frames": "All X and selectedY have F9. OrdinaryY has F9 q_R.",
            "scope": "Complete local native clean unitary interface and its literal inverse-adjoint. Routed composition, recursive hosting, precision and complete supplier cost remain separate.",
        },
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(raw)
    for provider, words in saved["providers"].items():
        for name, word in words.items():
            expected = c.rows(saved["content_maps"][name]) + g.eye(640)[224:]
            need(verify(word, expected) == reports[provider][name], "The complete serialized word")
            bad = deepcopy(word)
            macro = next(e for e in bad["events"] if e[0] == "gaussian_add" and F(e[3][1]))
            macro[5][0][3] = str(-F(macro[5][0][3]))
            try:
                verify(bad, expected)
            except ValueError:
                pass
            else:
                raise ValueError("A wrong complex component ADD was accepted")
    (args.out / "UNITARY-CLEAN.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {
        "status": "PASS_COMPLETE_UNITARY_24_CLEAN_NATIVE_WORDS",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(raw).hexdigest(), "reports": reports,
        "fresh_phase_checks": len(fresh_phases), "all_content_inverse_orders": True,
        "negative_control": "A wrong atomic component ADD is rejected in every complete word.",
        "scope": payload["physical_contract"]["scope"],
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "payload": receipt["payload_decompressed_sha256"],
                      "fresh_phase_checks": len(fresh_phases)}), flush=True)


if __name__ == "__main__":
    main()
