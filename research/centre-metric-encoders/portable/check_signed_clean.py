#!/usr/bin/env python3
"""Check complete signed-metric words and their physical field types."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parents[1] / "frozen/lanes/new-native-recipes-20261017/signed-clean-native-review-20261020"
HELPER = HERE.parent / "row-capture-native-review-20261020/check.py"
PIN = "5b8f2839db4fd4b0e4b24d5b8f8938c74a15497ae0e58f324896cf431d3ecb84"
if sha256(HELPER.read_bytes()).hexdigest() != PIN:
    raise ValueError("Independent arithmetic helper pin")
spec = importlib.util.spec_from_file_location("independent_signed_arithmetic", HELPER)
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
q.read(HELPER, PIN)
need = q.need
SOURCE = q.RAW / "signed-clean-native-20261020"
CODE = q.RAW / "signed-sixteen-20261020"
FREEZE = "d0d88ff73aa4762e53bce289544a1635c711e4bfeef5f499489199f506509df2"
PAYLOAD = "aa5c064837350c50928c984e03a3d7dffb5ab37da4510dc75607ced6166be797"


def forward(code, selected):
    matrix = q.unit(640)
    for p in range(112):
        matrix[p] = {112+p: F(-1)} if p in selected else dict(code[p])
        matrix[112+p] = dict(code[p])
        if p not in selected:
            q.add(matrix[112+p], {112+p: F(1)})
    return matrix


def inverse(code_inverse, selected):
    z = [{112+p if p in selected else p: F(1)} for p in range(112)]
    matrix = q.unit(640)
    matrix[:112] = q.mul(code_inverse, z)
    for p in range(112):
        matrix[112+p] = {p: F(-1)}
        if p not in selected:
            q.add(matrix[112+p], {112+p: F(1)})
    return matrix


def conjugate(matrix, permutation):
    return [{permutation[j]: v for j, v in matrix[permutation[p]].items()}
            for p in range(len(matrix))]


def selected_dual(code, selected):
    z = [{112+p if p in selected else p: F(1)} for p in range(112)]
    matrix = q.unit(640)
    matrix[:112] = q.mul(code, z)
    for p in range(112):
        if p in selected:
            matrix[112+p] = {p: F(-1)}
        else:
            q.add(matrix[p], {112+p: F(-1)})
    return matrix


def diagonal_word(matrix, offset=0):
    result = []
    for p, row in enumerate(matrix):
        need(set(row) == {p} and row[p], "A nonzero diagonal metric")
        c = row[p]
        need(abs(c.numerator) & (abs(c.numerator)-1) == 0 and
             c.denominator & (c.denominator-1) == 0, "A signed power-of-two metric")
        if c != 1:
            result.append(["scale", offset+p, None, str(c)])
    return result


def scalar_events(word):
    return [e[1] for e in word["events"] if e[0] == "scalar"]


def family_matrices(family, source, payload, selected, permutation):
    raw_c, raw_ci, raw_mode, tape, raw_j, raw_g = source
    for key, value in (("code", raw_c), ("inverse", raw_ci), ("native_code", raw_mode),
                       ("metric_input_inverse", raw_j), ("metric_output", raw_g)):
        need(payload[key] == value, "Exact source matrix: "+family+":"+key)
    c, ci, j, g = map(q.rows, (raw_c, raw_ci, raw_j, raw_g))
    need(q.mul(c, ci) == q.unit(112) and q.mul(ci, c) == q.unit(112),
         "Both actual code inverse orders")
    gi = [{p: 1/row[p]} for p, row in enumerate(g)]
    k = [{p: 1/row[p]} for p, row in enumerate(j)]
    need(q.mul(q.mul(c, k), q.transpose(c, 112)) == g, "Actual signed metric")
    need(q.transpose(ci, 112) == q.mul(q.mul(gi, c), k),
         "Independent inverse-transpose metric formula")
    pre = diagonal_word(j) + diagonal_word(gi, 112)
    post = diagonal_word(g) + diagonal_word(g, 112)
    need(payload["metric_pre_word"] == pre and payload["metric_post_word"] == post,
         "Both banks have the exact input and output metric scales")
    need(q.reverse(tape, 112) == q.transpose(c, 112), "Independent reverse source code")
    f, fi = forward(c, selected), inverse(ci, selected)
    d, di = q.transpose(fi, 640), q.transpose(f, 640)
    b, bi = conjugate(d, permutation), conjugate(di, permutation)
    need(b == selected_dual(q.transpose(ci, 112), selected),
         "Independent arbitrary-baseline raw selected-dual formula")
    pre_matrix = q.transpose(q.reverse(pre, 640), 640)
    post_matrix = q.transpose(q.reverse(post, 640), 640)
    converted = conjugate(q.mul(q.mul(post_matrix, d), pre_matrix), permutation)
    need(converted == selected_dual(c, selected), "Independent complete metric conversion")
    pre_inverse = [{p: 1/row[p]} for p, row in enumerate(pre_matrix)]
    post_inverse = [{p: 1/row[p]} for p, row in enumerate(post_matrix)]
    converted_inverse = conjugate(q.mul(q.mul(pre_inverse, di), post_inverse), permutation)
    maps = {"forward_I": f, "forward_Q": f, "inverse_adjoint_Q": d,
            "selected_conjugate_Q": b, "metric_selected_conjugate_Q": converted}
    inverses = {"forward_I": fi, "forward_Q": fi, "inverse_adjoint_Q": di,
                "selected_conjugate_Q": bi,
                "metric_selected_conjugate_Q": converted_inverse}
    need(set(payload["content_maps"]) == set(maps), "All five serialized endpoint maps")
    for name, matrix in maps.items():
        need(q.rows(payload["content_maps"][name]) == matrix[:224],
             "Independently derived complete endpoint: "+name)
        need(q.mul(matrix[:224], inverses[name][:224]) == q.unit(224) and
             q.mul(inverses[name][:224], matrix[:224]) == q.unit(224),
             "Both complete content inverse orders: "+name)
    return maps, pre, post


def forward_binding(word, old, model, formation, reuse, source, cyclic, selected, entry):
    need(word["frames"] == old["frames"], "Exact ordered source frame table")
    kept, removed = q.select_raw(old, {112+p for p in selected})
    need(word["retained_original_event_indices"] == kept and
         word["removed_original_event_indices"] == removed, "Exact retained and removed event indices")
    need(len(removed) == 250 and
         Counter(old["events"][i][0] for i in removed) == {"native": 128, "scalar": 122} and
         Counter(old["events"][i][4] for i in removed
                 if old["events"][i][0] == "native") == {1: 128},
         "Complete selected-target removal census")
    transfers = {r["event"]: r for r in old["transfer_records"]}
    need(len(transfers) == len(old["transfer_records"]), "Unique source transfer indices")
    parameters = {p["id"]: p for p in cyclic["parameters"]}
    mode = q.rows(source[2])
    core, retunings, active = [], [], 0
    for index in kept:
        event = old["events"][index]
        if index not in transfers:
            core.append(event)
            continue
        record = transfers[index]
        if record["part"] == "large48":
            par = parameters[record["parameter"]]
            ports = cyclic["cyclic_carriers"][par["vertex"]]
            p, j = ports[par["row"]], ports[par["column"]]
            original_value = F(model["mode_response"][p][str(j)])
        else:
            need(record["part"] == "small64", "Actual transfer sector")
            p, j = record["target_port"], record["source_port"]
            original_value = F(model["response"][p][str(j)])
        op, target, origin, raw = event[1]
        need(event[0] == "scalar" and op == "add" and target == 112+p and origin == j and
             p not in selected and F(record["coefficient"]) == F(raw),
             "Actual mode coefficient and physical transfer fields")
        value = mode[p].get(j, F(0))*F(raw)/original_value
        retunings.append({"original_event": index, "mode_target": p, "mode_source": j,
                          "coefficient": str(value)})
        if value:
            core.append(["scalar", ["add", target, origin, str(value)], event[2]])
            active += 1
    need(word["transfer_retunings"] == retunings, "Every ordinary coefficient is explicitly bound")
    sources = {v["port"]: v for v in formation["input_views"]}
    need(set(sources) == set(range(112)), "Every actual source adapter")
    inputs = [{**v, "field": p} for p, v in sorted(sources.items())]
    start, final = list(old["start"]), list(old["final"])
    progress, recipes = [], {}
    for event in core:
        if event[0] == "native":
            recipes[event[5]] = old["native_recipes"][event[5]]
    for p in sorted(selected):
        if entry == "I":
            key, before, rank = "direct-full", 0, 9
            recipes[key] = formation["native_recipes"]["capture-full"]
        else:
            key, before, rank = "capture-line:"+str(p), old["start"][p], 8
            need(reuse["frames"][reuse["start"][112+p]] == old["frames"][before],
                 "Accepted exact ordered line frame")
            recipes[key] = reuse["native_recipes"][key]
            inputs.append({**sources[p], "field": 112+p, "role": "selected_target"})
            start[112+p] = before
        final[112+p] = 1
        progress.append(["native", 112+p, before, 1, rank, key])
    code = [["scalar", gate, 1] for gate in source[3]]
    rotations = []
    for p in sorted(selected):
        rotations += [["scalar", ["add", 112+p, p, "1"], 1],
                      ["scalar", ["add", p, 112+p, "-1"], 1],
                      ["scalar", ["add", 112+p, p, "1"], 1]]
    need(word["events"] == core+progress+code+rotations, "Complete literal forward word")
    need(word["native_recipes"] == recipes, "Every exact phase recipe is inherited")
    need(word["start"] == start and word["final"] == final, "Complete endpoint frame declarations")
    need(word["input_views"] == sorted(inputs, key=lambda v: v["field"]),
         "Every exact input adapter has its physical field")
    need(word["output_views"] == [v for v in formation["output_views"] if v["port"] not in selected],
         "Every ordinary inverse target adapter is inherited")
    at, ranges = 0, {}
    for name, events in (("retained_retuned_core", core), ("selected_progress", progress),
                         ("source_code", code), ("signed_selected_exchanges", rotations)):
        ranges[name] = [at, at+len(events)]
        at += len(events)
    need(word["stage_ranges"] == ranges, "Exact forward stage chronology")
    return {"removed_events": 250, "removed_H1_children": 128,
            "ordinary_transfer_slots": len(retunings), "nonzero_retuned_ADDs": active}


def dual_binding(word, source, permutation):
    for name in ("frames", "start", "final", "native_recipes", "output_views", "stage_ranges"):
        need(word[name] == source[name], "Exact dual record: "+name)
    need(word["wire_permutation"] == {str(p): j for p, j in enumerate(permutation) if p != j},
         "Exact full physical-field permutation")
    need(all(source[k][p] == source[k][permutation[p]]
             for k in ("start", "final") for p in range(640)), "Selected endpoint frame symmetry")
    source_views = {v["field"]: v for v in source["input_views"]}
    expected_views = deepcopy(source["input_views"])
    for v in expected_views:
        v["field"] = permutation[v["field"]]
    need(word["input_views"] == sorted(expected_views, key=lambda v: v["field"]),
         "Every dual adapter is rebound to its physical field")
    for v in word["input_views"]:
        need(all(v[k] == source_views[v["field"]][k]
                 for k in ("port", "frame", "rank", "left", "right")),
             "Same-port Q/Q input phase equality")
    expected = []
    for old in source["events"]:
        if old[0] == "native":
            e = list(old)
            e[1] = permutation[e[1]]
        else:
            op, p, j, raw = old[1]
            value = F(raw)
            gate = (["add", permutation[j], permutation[p], str(-value)] if op == "add"
                    else ["scale", permutation[p], None, str(1/value)])
            e = ["scalar", gate, old[2]]
        expected.append(e)
    need(word["events"] == expected, "Literal same-order inverse-adjoint and field rebind")


def metric_binding(word, source, pre, post, permutation):
    for key in ("frames", "start", "final", "native_recipes", "input_views", "output_views",
                "wire_permutation"):
        need(word[key] == source[key], "Unchanged metric-wrapper physical record: "+key)
    def bind(tape, frames):
        return [["scalar", [op, permutation[p], None, c], frames[permutation[p]]]
                for op, p, _, c in tape]
    prefix, suffix = bind(pre, source["start"]), bind(post, source["final"])
    need(word["events"] == prefix+source["events"]+suffix, "Complete two-bank metric word")
    ranges = {"metric_input": [0, len(prefix)]}
    ranges.update({name: [start+len(prefix), end+len(prefix)]
                   for name, (start, end) in source["stage_ranges"].items()})
    at = len(prefix)+len(source["events"])
    ranges["metric_output"] = [at, at+len(suffix)]
    need(word["stage_ranges"] == ranges, "Exact metric-wrapper placement")


def trace(word, expected, entry):
    current = list(word["start"])
    count, used = Counter(), set()
    for event in word["events"]:
        if event[0] == "native":
            _, p, before, after, rank, key = event
            need(0 <= p < 224 and current[p] == before, "Actual native source frame")
            need(word["native_recipes"][key]["rank"] == rank, "Actual inherited native rank")
            current[p] = after
            count[rank] += 1
            used.add(key)
        else:
            need(event[0] == "scalar", "Only native and real dyadic scalar events")
            _, (op, p, j, value), frame = event
            need(0 <= p < 224 and current[p] == frame, "Actual scalar target frame")
            if op == "add":
                need(0 <= j < 224 and j != p and current[j] == frame, "Actual common scalar frame")
            else:
                need(op == "scale" and j is None and F(value), "Invertible scalar scale")
    need(len(current) == 640 and current == word["final"], "All actual final frames")
    need(current[224:] == word["start"][224:] and used == set(word["native_recipes"]),
         "Complete helper and phase-recipe ledger")
    need(count == {1: 1392, 2: 64, 3: 48, 9 if entry == "I" else 8: 16},
         "Complete child profile")
    gates = scalar_events(word)
    need(q.reverse(gates, 640) == q.transpose(expected, 640),
         "Independent reverse replay on all640 complex input columns")
    rows, bound = q.prefix(gates, 640)
    need(rows == expected and rows[224:] == q.unit(640)[224:],
         "Separate forward rows and416 arbitrary helper outputs")
    at, prices = 0, {}
    for name, (start, end) in sorted(word["stage_ranges"].items(), key=lambda x: x[1][0]):
        need(start == at and end >= start, "Complete disjoint scalar stage ledger")
        prices[name] = q.price([e[1] for e in word["events"][start:end] if e[0] == "scalar"])
        at = end
    need(at == len(word["events"]) and q.price(gates) == sum(prices.values()),
         "The invoice covers every operation")
    return {"complex_input_columns": 640, "unchanged_arbitrary_complex_helpers": 416,
            "native_profile": dict(sorted(count.items())), "native_children": sum(count.values()),
            "native_mass": sum(k*v for k, v in count.items()),
            "scalar_price": sum(prices.values()), "scalar_stage_prices": prices,
            "input_views": len(word["input_views"]), "output_views": len(word["output_views"]),
            "native_side_map_upper_bound": 2*(sum(count.values())-(16 if entry == "I" else 0)),
            "content_prefix_bound": bound, "new_fields": 0, "private_fields": 0,
            "odd_scans": 0, "runtime_boundary_swaps": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    for path, name, pin in (
        (SOURCE, "FREEZE.json", FREEZE),
        (CODE, "FREEZE.json", "8739b5dbba6a5422c9b68035683876931fbf8f6599a43375d10e73eee55b2de2"),
        (CODE, "PAIRED-FREEZE.json", "810508791ea43aecaaf894c3cb50a8170d3e6f1f8e52684e274cda16c2c2db57"),
        (q.LANES/"bridge-review-20261017/signed-metric-review-20261020", "FREEZE.json",
         "b44b5a95c1fa8372bbd979f360fde743df10c16bd07ac4d5015c048982539762"),
        (HERE.parent/"row-capture-native-review-20261020", "FREEZE.json",
         "488dc693d6e7d48e8024455c9c3f2f899f94a8e9058aef28ad38f7c46c7d8532"),
        (HERE.parent/"line-entry-reuse-review-20261020", "FREEZE.json",
         "cc5ed3b0ecc6eb5cec48f8baead43ec813042c3e83cd68104b7745366c13c55c"),
        (q.ACCEPTED, "NATIVE-REVIEW-FREEZE.json",
         "cfdc4fa0361aa79c1d53a59ff48bdde1715ea8e3eb6b9efbc109c97bcc44a976"),
        (q.ACCEPTED, "EXTENSIONS-REVIEW-FREEZE.json",
         "c8fccfbe49ddd8747095a43aa1c1c59b0270bbbf73d94a317a79113191e4e34c")):
        q.frozen(path, name, pin)
    payload = json.loads(q.read(SOURCE/"run-normal/SIGNED-CLEAN.json.gz", PAYLOAD, True))
    need(len(payload["source_pins"]) == 12, "All twelve declared source pins")
    for record in payload["source_pins"].values():
        original_path = Path(record["path"])
        anchor = "centre-encoding-campaign-20261014"
        need(original_path.parts.count(anchor) == 1, "Unique source campaign path")
        relative = original_path.parts[original_path.parts.index(anchor)+1:]
        need(relative and relative[0] == "lanes", "Source stays in the lane archive")
        path = q.LANES.parent.joinpath(*relative)
        q.read(path, record["sha256"], path.suffix == ".gz")
    producer_receipt = json.loads(q.read(SOURCE/"run-normal/CHECKS.json",
                                         "21e5ae1b7757429dac8ecc4c4238f7e7f1296bf3f6cb3b3c67b09166c22a79ca"))
    first = json.loads(q.read(CODE/"run-v2-normal/SIGNED-SIXTEEN.json.gz",
                              "5ba0e042c6f27aa24e230e27a4eca5e1da573d3e39d22dab93886b207f14016c", True))
    paired = json.loads(q.read(CODE/"paired-normal/PAIRED-SIGNED-SIXTEEN.json.gz",
                               "99fad6bbc9e4a463a576fe33c8d2093739e5c696851412b1e9115c78d88daec1", True))
    raw = json.loads(q.read(q.RAW/"odd16-normal-v2/EXTENSION-PROGRAM.json.gz",
                            "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4", True))
    formation = json.loads(q.read(q.NATIVE/"direct-normal/DIRECT-FULL-CAPTURE.json.gz",
                                  "fa3342f8b4ddf286f6f67922f4184486ec0162610e4de6a457de3eed0750504c", True))
    reuse = json.loads(q.read(q.NATIVE/"reuse-normal/LINE-ENTRY-REUSE.json.gz",
                              "efe67a962752f2c36513d84094d215fd0909a5360707938ff99d62743dc72110", True))
    cyclic = json.loads(q.read(q.LANES/"independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json",
                               "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585"))
    selected = set(first["centre_ports"])
    need(len(selected) == 16 and selected == set(q.P) == set(paired["centre_ports"]) and
         payload["selected_ports"] == sorted(selected), "Exact16 selected physical ports")
    need(payload["ports"] == raw["model"]["ports"], "Exact source port labels")
    sources = {
        "individual": (first["code"], first["inverse"], first["native_code"],
                       first["scalar_words"]["code"], first["input_metric_inverse"], first["output_metric"]),
        "paired": (paired["code"], paired["inverse"], paired["native_codes"]["code"],
                   paired["scalar_words"]["code"], paired["input_metric_inverse"], paired["output_metric"]),
        "paired_transpose": (paired["transpose"], paired["inverse_transpose"], paired["native_codes"]["transpose"],
                             paired["scalar_words"]["transpose"], paired["output_metric"], paired["input_metric_inverse"])}
    need(set(payload["families"]) == set(sources) == set(payload["providers"]), "All three code families")
    identity = list(range(640))
    swap = [112+p if p in selected else p-112 if p-112 in selected else p for p in range(640)]
    reports, total = {}, 0
    for family, source in sources.items():
        maps, pre, post = family_matrices(family, source, payload["families"][family], selected, swap)
        need(set(payload["providers"][family]) == {"base", "extra"}, "Both actual provider words")
        reports[family] = {}
        for provider, words in payload["providers"][family].items():
            need(set(words) == set(maps), "Every local variant is present")
            reports[family][provider] = {}
            for name, word in words.items():
                entry = "I" if name == "forward_I" else "Q"
                binding = {}
                if name.startswith("forward_"):
                    binding = forward_binding(word, raw["providers"][provider]["forward"], raw["model"],
                                              formation["providers"][provider], reuse["providers"][provider],
                                              source, cyclic, selected, entry)
                elif name == "metric_selected_conjugate_Q":
                    metric_binding(word, words["selected_conjugate_Q"], pre, post, swap)
                else:
                    dual_binding(word, words["forward_Q"], identity if name == "inverse_adjoint_Q" else swap)
                report = {**trace(word, maps[name], entry), **binding}
                recorded = producer_receipt["reports"][family][provider][name]
                for a, b in (("scalar_price", "scalar"), ("scalar_stage_prices", "scalar_stages"),
                             ("native_profile", "native_profile"), ("native_children", "native_children"),
                             ("native_mass", "native_mass"), ("input_views", "input_views"),
                             ("output_views", "output_views"),
                             ("native_side_map_upper_bound", "native_side_map_upper_bound")):
                    value = report[a]
                    if a == "native_profile":
                        value = {str(k): v for k, v in value.items()}
                    need(value == recorded[b], "Independent invoice agrees with frozen receipt: "+a)
                need(report["content_prefix_bound"] ==
                     {"row_one_norm": recorded["content_row_one_norm"],
                      "binary_height": recorded["binary_height"]},
                     "Independent prefix bound agrees with frozen receipt")
                reports[family][provider][name] = report
                total += 1
            print("PASS", family, provider, flush=True)
    sample = payload["providers"]["individual"]["base"]
    word = sample["metric_selected_conjugate_Q"]
    start, end = word["stage_ranges"]["metric_input"]
    omitted_target_scales = [e[1] for i, e in enumerate(word["events"]) if e[0] == "scalar" and
                             not (start <= i < end and swap[e[1][1]] >= 112)]
    target = q.transpose(q.rows(payload["families"]["individual"]["content_maps"]["metric_selected_conjugate_Q"])
                         + q.unit(640)[224:], 640)
    need(q.reverse(omitted_target_scales, 640) != target, "Omitting target-bank metric scales is rejected")
    gates = scalar_events(word)
    bad = deepcopy(gates)
    bad[0][3] = str(-F(bad[0][3]))
    need(q.reverse(bad, 640) != target, "A wrong metric sign is rejected")
    need(q.reverse(list(reversed(scalar_events(sample["inverse_adjoint_Q"]))), 640) !=
         q.transpose(q.rows(payload["families"]["individual"]["content_maps"]["inverse_adjoint_Q"])
                     + q.unit(640)[224:], 640), "Wrong inverse-adjoint chronology is rejected")
    bad_phase = dict(sample["forward_Q"])
    bad_phase["native_recipes"] = deepcopy(bad_phase["native_recipes"])
    record = next(iter(bad_phase["native_recipes"].values()))
    record["left"]["phase"] = (record["left"]["phase"]+1) % 4
    try:
        forward_binding(bad_phase, raw["providers"]["base"]["forward"], raw["model"],
                        formation["providers"]["base"], reuse["providers"]["base"],
                        sources["individual"], cyclic, selected, "Q")
    except ValueError as error:
        need(str(error) == "Every exact phase recipe is inherited", "The phase control fails at its exact test")
    else:
        raise ValueError("A changed native global phase was accepted")
    result = {
        "status": "PASS_INDEPENDENT_SIGNED_SIXTEEN_NATIVE",
        "producer_freeze_sha256": FREEZE, "payload_decompressed_sha256": PAYLOAD,
        "complete_words": total, "reports": reports, "fresh_native_phase_shapes": 0,
        "phase_scope": "Each ordered native frame, exact recipe and physical endpoint adapter is bound to an accepted source. All changed gates are real scalar operations at a common complex frame.",
        "both_complete_content_inverse_orders": True,
        "negative_controls": ["omitted target-bank metric", "wrong metric sign",
                              "wrong dual chronology", "wrong native global phase"],
        "scope": "Thirty complete local physical words. No routed caller, saved-record restoration, recursive host, finite map cost, rounding bound or complete supplier cost is claimed."}
    args.out.mkdir(parents=True, exist_ok=False)
    for name, value in (("REVIEW.json", result), ("INPUTS.json", q.INPUTS)):
        (args.out/name).write_text(json.dumps(value, indent=2, sort_keys=True)+"\n")
    print(result["status"], flush=True)


if __name__ == "__main__":
    main()
