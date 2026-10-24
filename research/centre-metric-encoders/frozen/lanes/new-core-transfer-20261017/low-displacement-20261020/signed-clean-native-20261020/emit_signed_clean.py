#!/usr/bin/env python3
"""Emit complete clean interfaces for the signed sixteen-field codes."""

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
    "helper": (PARENT / "signed-sixteen-20261020/check_signed_sixteen.py",
               "7befca24a7e3fd9afccfda3f494d2a515361fdf7575751d3b690f380a6681b82"),
    "code": (PARENT / "signed-sixteen-20261020/run-v2-normal/SIGNED-SIXTEEN.json.gz",
             "5ba0e042c6f27aa24e230e27a4eca5e1da573d3e39d22dab93886b207f14016c"),
    "code_freeze": (PARENT / "signed-sixteen-20261020/FREEZE.json",
                    "8739b5dbba6a5422c9b68035683876931fbf8f6599a43375d10e73eee55b2de2"),
    "paired": (PARENT / "signed-sixteen-20261020/paired-normal/PAIRED-SIGNED-SIXTEEN.json.gz",
               "99fad6bbc9e4a463a576fe33c8d2093739e5c696851412b1e9115c78d88daec1"),
    "paired_freeze": (PARENT / "signed-sixteen-20261020/PAIRED-FREEZE.json",
                      "810508791ea43aecaaf894c3cb50a8170d3e6f1f8e52684e274cda16c2c2db57"),
    "native_helper": (PARENT / "emit_native.py",
                      "599987ddfe2fdb8fd4be533d783e24bf40a95b6c69118ec1552a10b06f1d5745"),
    "native": (PARENT / "odd16-normal-v2/EXTENSION-PROGRAM.json.gz",
               "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4"),
    "formation": (PARENT / "row-only-capture-20261020/direct-normal/DIRECT-FULL-CAPTURE.json.gz",
                  "fa3342f8b4ddf286f6f67922f4184486ec0162610e4de6a457de3eed0750504c"),
    "prefix": (PARENT / "fixed-reader-reuse-20261020/prefix-normal/CARRIER-PREFIX.json.gz",
               "54c561cfc49ad3fe1258ba5a8760eeadaa11784272cf458e2a6e54403a0e655e"),
    "native_review": (LANES / "new-native-recipes-20261017/low-displacement-review-20261020/EXTENSIONS-REVIEW-FREEZE.json",
                      "c8fccfbe49ddd8747095a43aa1c1c59b0270bbbf73d94a317a79113191e4e34c"),
    "formation_review": (LANES / "new-native-recipes-20261017/row-capture-native-review-20261020/FREEZE.json",
                         "488dc693d6e7d48e8024455c9c3f2f899f94a8e9058aef28ad38f7c46c7d8532"),
    "prefix_review": (LANES / "new-native-recipes-20261017/line-entry-reuse-review-20261020/FREEZE.json",
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
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


m = module("signed_clean_code", "helper")
n = module("signed_clean_native", "native_helper")
b, r = m.b, m.r


def verify(word, expected):
    state, frames = r.identity(640), list(word["start"])
    peak, height = F(1), 0
    for event in word["events"]:
        if event[0] == "native":
            _, p, old, new, rank, key = event
            need(frames[p] == old, "The exact native entrance frame")
            need(len(n.basis(word["frames"][old] + word["frames"][new]))
                 == len(word["frames"][new]), "The native frame inclusion")
            need(rank == len(word["frames"][new]) - len(word["frames"][old])
                 == word["native_recipes"][key]["rank"], "The exact native rank")
            frames[p] = new
            continue
        need(event[0] == "scalar", "Only scalar and native events are used")
        op, p, q, raw = event[1]
        value, frame = F(raw), event[2]
        need(frames[p] == frame, "The scalar target frame")
        if op == "add":
            need(p != q and frames[q] == frame, "The common scalar frame")
            r.add(state[p], state[q], value)
        else:
            need(op == "scale" and b.unit(value), "A signed dyadic-unit scale")
            state[p] = b.scale_row(state[p], value)
        peak = max(peak, sum(abs(v) for v in state[p].values()))
        for v in state[p].values():
            denominator = v.denominator
            need(not denominator & (denominator - 1), "Every content coefficient is dyadic")
            height = max(height, denominator.bit_length() - 1)
    need(frames == word["final"], "Every final frame")
    need(state == expected + r.identity(640)[224:], "All640 independent complex inputs")
    need(state[224:] == r.identity(640)[224:], "All416 arbitrary auxiliary fields")
    profile = Counter(e[4] for e in word["events"] if e[0] == "native")
    direct = sum(e[0] == "native" and e[5] == "direct-full" for e in word["events"])
    price = lambda events: r.price([e[1] for e in events if e[0] == "scalar"])
    return {
        "all_input_columns": 640, "unchanged_arbitrary_auxiliaries": 416,
        "native_profile": dict(sorted(profile.items())),
        "native_mass": sum(k * v for k, v in profile.items()),
        "native_children": sum(profile.values()),
        "native_side_map_upper_bound": 2 * (sum(profile.values()) - direct),
        "input_views": len(word["input_views"]), "output_views": len(word["output_views"]),
        "scalar": price(word["events"]),
        "scalar_stages": {name: price(word["events"][start:end])
                          for name, (start, end) in word["stage_ranges"].items()},
        "content_row_one_norm": str(peak), "binary_height": height,
        "owned_fields": 0, "private_fields": 0, "odd_divisions": 0,
    }


def conjugate(matrix, permutation):
    result = [{} for _ in matrix]
    for p, row in enumerate(matrix):
        result[permutation[p]] = {permutation[j]: v for j, v in row.items()}
    return result


def dual_word(source, permutation):
    result = deepcopy(source)
    for event in result["events"]:
        if event[0] == "native":
            event[1] = permutation[event[1]]
        else:
            op, p, q, c = event[1]
            event[1] = ([op, permutation[q], permutation[p], str(-F(c))] if op == "add"
                        else [op, permutation[p], None, str(1 / F(c))])
    for key in ("start", "final"):
        result[key] = [source[key][permutation[p]] for p in range(640)]
        need(result[key] == source[key], "The selected endpoint frames are symmetric")
    for view in result["input_views"]:
        view["field"] = permutation[view["field"]]
    result["input_views"].sort(key=lambda v: v["field"])
    original = {view["field"]: view for view in source["input_views"]}
    for view in result["input_views"]:
        need(all(view[k] == original[view["field"]][k]
                 for k in ("port", "frame", "left", "right", "rank")),
             "The complete input adapter stays on its actual same-port field")
    need(all(permutation[112 + v["port"]] == 112 + v["port"]
             for v in result["output_views"]), "Every ordinary output view is fixed")
    result["wire_permutation"] = {str(p): q for p, q in enumerate(permutation) if p != q}
    return result


def wrap_metric(word, pre, post, permutation):
    result = deepcopy(word)
    def bind(tape, frames):
        return [["scalar", [op, permutation[p], None, c], frames[permutation[p]]]
                for op, p, q, c in tape]
    prefix, suffix = bind(pre, result["start"]), bind(post, result["final"])
    events = result["events"]
    result["events"] = prefix + events + suffix
    result["stage_ranges"] = {
        "metric_input": [0, len(prefix)],
        **{name: [start + len(prefix), end + len(prefix)]
           for name, (start, end) in result["stage_ranges"].items()},
        "metric_output": [len(prefix) + len(events), len(result["events"])],
    }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    for name in PINS:
        read(name)
    first, paired = json.loads(read("code")), json.loads(read("paired"))
    native, formation, prefix = [json.loads(read(name)) for name in ("native", "formation", "prefix")]
    cyclic = json.loads(b.read("cyclic"))
    parameters = {x["id"]: x for x in cyclic["parameters"]}
    selected = set(first["centre_ports"])
    selected_fields = {112 + p for p in selected}
    old_mode = b.rows(native["model"]["mode_response"])
    old_physical = b.rows(native["model"]["response"])
    identity = list(range(640))
    permutation = list(identity)
    for p in selected:
        permutation[p], permutation[112 + p] = 112 + p, p
    families = {
        "individual": (first["code"], first["inverse"], first["native_code"],
                       first["scalar_words"]["code"], first["input_metric_inverse"], first["output_metric"]),
        "paired": (paired["code"], paired["inverse"], paired["native_codes"]["code"],
                   paired["scalar_words"]["code"], paired["input_metric_inverse"], paired["output_metric"]),
        "paired_transpose": (paired["transpose"], paired["inverse_transpose"], paired["native_codes"]["transpose"],
                             paired["scalar_words"]["transpose"], paired["output_metric"], paired["input_metric_inverse"]),
    }
    providers, reports, family_data = {}, {}, {}
    for family, (raw_code, raw_inverse, raw_mode, tape, raw_J, raw_G) in families.items():
        C, Ci, mode = b.rows(raw_code), b.rows(raw_inverse), b.rows(raw_mode)
        J, G = b.rows(raw_J), b.rows(raw_G)
        Gi = [{p: 1 / row[p]} for p, row in enumerate(G)]
        pre = m.diagonal_word(J) + m.diagonal_word(Gi, 112)
        post = m.diagonal_word(G) + m.diagonal_word(G, 112)
        scalar_forward = m.literal_clean_word(tape, sorted(selected))
        forward = m.clean_map(C, selected)
        inverse = b.replay(r.inverse_word(scalar_forward), 224)[0]
        need(r.product(forward, inverse) == r.product(inverse, forward) == r.identity(224),
             "Both complete content inverse orders")
        literal_dual = r.transpose(inverse, 224)
        converted = b.replay(pre + r.transpose_word(r.inverse_word(scalar_forward)) + post, 224)[0]
        expected = {
            "forward_I": forward, "forward_Q": forward,
            "inverse_adjoint_Q": literal_dual,
            "selected_conjugate_Q": conjugate(literal_dual, permutation[:224]),
            "metric_selected_conjugate_Q": conjugate(converted, permutation[:224]),
        }
        formula = r.identity(224)
        w = r.product(C, [{112 + p if p in selected else p: F(1)} for p in range(112)])
        for p in range(112):
            formula[p] = dict(w[p])
            if p in selected:
                formula[112 + p] = {p: F(-1)}
            else:
                r.add(formula[p], {112 + p: F(1)}, -1)
        need(formula == expected["metric_selected_conjugate_Q"], "The metric-converted Bswap formula")
        family_data[family] = {
            "code": raw_code, "inverse": raw_inverse, "native_code": raw_mode,
            "metric_input_inverse": raw_J, "metric_output": raw_G,
            "metric_pre_word": pre, "metric_post_word": post,
            "content_maps": {name: r.encoded(value) for name, value in expected.items()},
        }
        providers[family], reports[family] = {}, {}
        for provider, directions in native["providers"].items():
            original = directions["forward"]
            prior_formation, prior_prefix = formation["providers"][provider], prefix["providers"][provider]
            transfers = {item["event"]: item for item in original["transfer_records"]}
            kept, retained, removed, retunings = [], [], [], []
            for index, event in enumerate(original["events"]):
                target = event[1] if event[0] == "native" else event[1][1]
                if target in selected_fields:
                    removed.append(index)
                    continue
                if event[0] == "scalar" and event[1][0] == "add":
                    need(event[1][2] not in selected_fields, "No retained read of a removed target")
                retained.append(index)
                changed = deepcopy(event)
                if index in transfers:
                    record = transfers[index]
                    if record["part"] == "large48":
                        parameter = parameters[record["parameter"]]
                        ports = cyclic["cyclic_carriers"][parameter["vertex"]]
                        p, j = ports[parameter["row"]], ports[parameter["column"]]
                        old_coefficient = old_mode[p][j]
                    else:
                        p, j = record["target_port"], record["source_port"]
                        old_coefficient = old_physical[p][j]
                    need(p not in selected and changed[1][0] == "add", "An ordinary transfer slot")
                    value = F(changed[1][3]) * mode[p].get(j, F(0)) / old_coefficient
                    changed[1][3] = str(value)
                    retunings.append({"original_event": index, "mode_target": p, "mode_source": j,
                                      "coefficient": str(value)})
                    if not value:
                        continue
                kept.append(changed)
            removed_profile = Counter(original["events"][i][4] for i in removed
                                      if original["events"][i][0] == "native")
            need(len(removed) == 250 and removed_profile == {1: 128}, "The full sixteen-path removal census")
            used = {e[5] for e in kept if e[0] == "native"}
            recipes = {key: deepcopy(original["native_recipes"][key]) for key in used}
            source_views = {v["port"]: v for v in prior_formation["input_views"]}
            output_views = [deepcopy(v) for v in prior_formation["output_views"] if v["port"] not in selected]
            need(len(output_views) == 96, "Every ordinary output view")
            providers[family][provider], reports[family][provider] = {}, {}
            for entry in ("I", "Q"):
                word = {
                    "frames": deepcopy(original["frames"]), "start": list(original["start"]),
                    "final": list(original["final"]), "events": deepcopy(kept),
                    "native_recipes": deepcopy(recipes),
                    "input_views": [{**deepcopy(v), "field": p} for p, v in sorted(source_views.items())],
                    "output_views": deepcopy(output_views), "retained_original_event_indices": retained,
                    "removed_original_event_indices": removed, "transfer_retunings": retunings,
                    "stage_ranges": {"retained_retuned_core": [0, len(kept)]},
                }
                begin = len(word["events"])
                for p in sorted(selected):
                    if entry == "I":
                        key, old, rank = "direct-full", 0, 9
                        recipe = prior_formation["native_recipes"]["capture-full"]
                    else:
                        key, old, rank = "capture-line:" + str(p), original["start"][p], 8
                        recipe = prior_prefix["native_recipes"][key]
                        word["start"][112 + p] = old
                        word["input_views"].append({**deepcopy(source_views[p]), "field": 112 + p,
                                                    "role": "selected_target"})
                    word["native_recipes"][key] = deepcopy(recipe)
                    word["events"].append(["native", 112 + p, old, 1, rank, key])
                    word["final"][112 + p] = 1
                word["stage_ranges"]["selected_progress"] = [begin, len(word["events"])]
                begin = len(word["events"])
                word["events"].extend([["scalar", deepcopy(gate), 1] for gate in tape])
                word["stage_ranges"]["source_code"] = [begin, len(word["events"])]
                begin = len(word["events"])
                for p in sorted(selected):
                    word["events"].extend([["scalar", ["add", 112 + p, p, "1"], 1],
                                           ["scalar", ["add", p, 112 + p, "-1"], 1],
                                           ["scalar", ["add", 112 + p, p, "1"], 1]])
                word["stage_ranges"]["signed_selected_exchanges"] = [begin, len(word["events"])]
                word["input_views"].sort(key=lambda v: v["field"])
                name = "forward_" + entry
                report = verify(word, expected[name])
                need(report["native_profile"] == {1: 1392, 2: 64, 3: 48, 9 if entry == "I" else 8: 16},
                     "The complete sixteen-field native profile")
                providers[family][provider][name], reports[family][provider][name] = word, report
            for name, perm in (("inverse_adjoint_Q", identity), ("selected_conjugate_Q", permutation)):
                word = dual_word(providers[family][provider]["forward_Q"], perm)
                providers[family][provider][name] = word
                reports[family][provider][name] = verify(word, expected[name])
            name = "metric_selected_conjugate_Q"
            word = wrap_metric(providers[family][provider]["selected_conjugate_Q"], pre, post, permutation)
            providers[family][provider][name] = word
            reports[family][provider][name] = verify(word, expected[name])
            print(json.dumps({"family": family, "provider": provider,
                              "scalar": {name: result["scalar"] for name, result in reports[family][provider].items()}},
                             sort_keys=True), flush=True)
    payload = {
        "schema": "complete-signed-sixteen-clean-native-v1",
        "source_pins": {name: {"path": str(path), "sha256": pin} for name, (path, pin) in PINS.items()},
        "selected_ports": sorted(selected), "ports": native["model"]["ports"],
        "families": family_data, "providers": providers,
        "physical_contract": {
            "input_I": "X=Q x; selectedY=z; ordinaryY=v.",
            "input_Q": "X=Q x; selectedY=Q_P z; ordinaryY=v.",
            "output": "AllX and selectedY have F9; ordinaryY has F9 q_R.",
            "forward": "Put w=Cx. X=(-z,w_R); Y=(w_P,v+w_R).",
            "raw_selected_dual": "Put w=C^-T(z,u). X=(w_P,w_R-v); Y=(-a,v).",
            "metric_selected_dual": "Put w=C(z,u). X=(w_P,w_R-v); Y=(-a,v).",
            "scope": "Complete local native words and local invoices. Routed composition, terminal decoding, recursive hosting, precision and supplier cost remain separate.",
        },
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(raw)
    for family, variants in saved["providers"].items():
        for provider, words in variants.items():
            for name, word in words.items():
                expected = b.rows(saved["families"][family]["content_maps"][name])
                need(verify(word, expected) == reports[family][provider][name], "Every complete serialized word")
    bad = deepcopy(saved["providers"]["individual"]["base"]["metric_selected_conjugate_Q"])
    first_scale = next(e for e in bad["events"] if e[0] == "scalar" and e[1][0] == "scale")
    first_scale[1][3] = str(-F(first_scale[1][3]))
    try:
        verify(bad, b.rows(saved["families"]["individual"]["content_maps"]["metric_selected_conjugate_Q"]))
    except ValueError:
        pass
    else:
        raise ValueError("A wrong metric sign was accepted")
    (args.out / "SIGNED-CLEAN.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {
        "status": "PASS_COMPLETE_SIGNED_SIXTEEN_NATIVE",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(raw).hexdigest(),
        "complete_words": 30, "reports": reports, "fresh_phase_operators": 0,
        "phase_scope": "Every exact native recipe and endpoint adapter is inherited by equality from independently reviewed source records.",
        "negative_control": "A wrong diagonal metric sign is rejected.",
        "scope": payload["physical_contract"]["scope"],
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": receipt["status"], "payload": receipt["payload_decompressed_sha256"]}), flush=True)


if __name__ == "__main__":
    main()
