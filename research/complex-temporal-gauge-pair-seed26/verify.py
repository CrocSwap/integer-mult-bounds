# SPDX-License-Identifier: Apache-2.0
"""Compose the pinned L248 and L253 temporal gauges on one PR1263 word."""
import copy
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
PR1263 = "5fbaca13028846bddbb001e8e07addc2ab8e5816"
PR1350 = "64b8a55c6933ffb6d9e30fa19f85d05b572d4aa5"
PR1353 = "efc6bfc3302a966ac0e1f5f4656e94b4cabeb9ca"
HELPERS = (248, 253)
# PR1353 replaces L248's constant exponent with an absolute time-varying gauge.
# PR1350 adds a time-varying offset on top of L253's retained constant gauge.
REPLACED_STATIC = {248}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def power_two(exponent):
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2**(-exponent))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "module spec " + name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_inputs():
    sources = json.loads((HERE / "SOURCES.json").read_bytes())
    need(sources["base_commit"] == BASE, "exact base commit")
    records = {row["pr"]: row for row in sources["predecessors"]}
    need(records[1263]["commit"] == PR1263, "PR1263 head")
    need(records[1350]["commit"] == PR1350, "PR1350 head")
    need(records[1353]["commit"] == PR1353, "PR1353 head")
    for pr, row in ((1350, records[1350]), (1353, records[1353])):
        raw = (HERE / row["package_path"]).read_bytes()
        need(sha(raw) == row["sha256"], "pinned PR%d receipt bytes" % pr)
    for path, expected in sources["vendored_files"].items():
        need(sha((HERE / path).read_bytes()) == expected, "vendored predecessor " + path)

    selected = json.loads((ROOT / "certificates/selected-result.json").read_bytes())
    need(selected["kappa"] == "836330098538459/500000000000000000"
         and selected["certificate_sha256"] == "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
         "selected PR1094 result")
    pr248 = json.loads((HERE / "inputs/PR1353-RESULT.json").read_bytes())
    pr253 = json.loads((HERE / "inputs/PR1350-CERTIFICATE.json").read_bytes())
    need(pr248["base"] == BASE and pr248["predecessors"]["pr1263_head"] == PR1263,
         "PR1353 common PR1263 base")
    need(pr253["current_base_commit"] == BASE and pr253["parent"]["head"] == PR1263,
         "PR1350 common PR1263 base")
    need(pr248["status"] == "PASS_SEED22_HELPER248_DYNAMIC_ON_217_STATIC_GAUGES",
         "PR1353 predecessor receipt status")
    need(pr253["status"] == "PASS_L253_TEMPORAL_GAUGE_ON_218_HELPER_WORD",
         "PR1350 predecessor receipt status")
    return sources, selected, pr248, pr253


def indexed_schedule(schedule, expected_ids, label):
    result = {}
    for index, exponent in schedule:
        need(index not in result, label + " duplicate event index")
        result[index] = exponent
    need(set(result) == set(expected_ids), label + " exact incident ADD coverage")
    return result


def require_disjoint(left, right):
    overlap = set(left) & set(right)
    need(not overlap, "dynamic gauges share ADD ids: " + repr(sorted(overlap)))
    return sorted(set(left) | set(right))


def check_invoice(actual, expected, label):
    need(actual == expected,
         label + " complete invoice mismatch: actual=" + str(actual) + " expected=" + str(expected))


def incident_add_ids(events, helper):
    result = []
    register = ["L", helper]
    for index, event in enumerate(events):
        if event[0] == "scalar" and event[1][0] == "add" and register in event[1][1:3]:
            result.append(index)
    return result


def static_to_source_add_ids(source_events, static_events):
    """Map PR1263 static-word ADD event IDs back to source event IDs."""
    source_adds = [(i, e) for i, e in enumerate(source_events)
                   if e[0] == "scalar" and e[1][0] == "add"]
    static_adds = [(i, e) for i, e in enumerate(static_events)
                   if e[0] == "scalar" and e[1][0] == "add"]
    need(len(source_adds) == len(static_adds), "static replay preserves ADD count")
    mapping = {}
    for (source_id, source_event), (static_id, static_event) in zip(source_adds, static_adds):
        need(source_event[1][1:3] == static_event[1][1:3],
             "static replay preserves ordered ADD endpoints")
        mapping[static_id] = source_id
    return mapping


def build_pair_word(events, word, gauges, schedules, dynamic_helpers=HELPERS):
    dynamic = set(dynamic_helpers)
    static = {int(h): int(k) for h, k in gauges.items()
              if int(h) not in (dynamic & REPLACED_STATIC) and int(k)}
    current = {h: 0 for h in dynamic}
    out = [copy.deepcopy(events[0])]
    for helper, exponent in sorted(static.items()):
        q = power_two(exponent)
        out.append(["scalar", ["scale", ["L", helper], q.numerator, q.denominator],
                    word["start"][helper]])

    for index, original in enumerate(events[1:-1], start=1):
        event = copy.deepcopy(original)
        for helper in sorted(dynamic):
            schedule = schedules[helper]
            if index in schedule:
                new = schedule[index]
                if new != current[helper]:
                    q = power_two(new - current[helper])
                    out.append(["scalar", ["scale", ["L", helper], q.numerator, q.denominator],
                                event[2]])
                current[helper] = new
        if event[0] == "scalar" and event[1][0] == "add":
            gate = event[1]
            target, source = gate[1], gate[2]
            shift = 0
            if target[0] == "L":
                h = target[1]
                shift += (current[h] + static.get(h, 0)) if h in dynamic else static.get(h, 0)
            if source[0] == "L":
                h = source[1]
                shift -= (current[h] + static.get(h, 0)) if h in dynamic else static.get(h, 0)
            q = Fraction(gate[3], gate[4]) * power_two(shift)
            gate[3:5] = [q.numerator, q.denominator]
        out.append(event)

    for helper in sorted(dynamic):
        if current[helper]:
            q = power_two(-current[helper])
            out.append(["scalar", ["scale", ["L", helper], q.numerator, q.denominator],
                        word["final"][helper]])
    for helper, exponent in sorted(static.items()):
        q = power_two(-exponent)
        out.append(["scalar", ["scale", ["L", helper], q.numerator, q.denominator],
                    word["final"][helper]])
    out.append(copy.deepcopy(events[-1]))
    need(out[0] == events[0] and out[-1] == events[-1], "word phase boundaries")
    need([e for e in out if e[0] != "scalar"] ==
         [e for e in events if e[0] != "scalar"], "paid/frame event identity")
    return out


def verify_fault_controls(schedules, expected_ids, union_ids, actual_invoice, expected_invoice):
    rejected = []
    try:
        require_disjoint({union_ids[0]: 0}, {union_ids[0]: 0})
    except ValueError:
        rejected.append("shared_add_id")
    try:
        indexed_schedule([[union_ids[0], 0], [union_ids[0], 1]],
                         expected_ids[HELPERS[0]], "mutated")
    except ValueError:
        rejected.append("duplicate_schedule_entry")
    try:
        indexed_schedule(schedules[HELPERS[0]][:-1],
                         expected_ids[HELPERS[0]], "mutated_omission")
    except ValueError:
        rejected.append("omitted_incident_add")
    try:
        check_invoice(actual_invoice + 1, expected_invoice, "mutated")
    except ValueError:
        rejected.append("wrong_combined_invoice")
    need(len(rejected) == 4, "all malformed composition controls reject")
    return rejected


def compute():
    sources, selected, pr248, pr253 = load_inputs()
    parent = load_module("pinned_pr1263_verify", HERE / "vendor/pr1263/verify.py")
    parent.ROOT = ROOT
    parent_result, static_candidates = parent.compute()
    need(parent_result["status"] == "PASS_MANY_HELPER_DYADIC_CONSTRUCTION",
         "rebuild frozen PR1263 word")
    lib = parent.engine()
    word, programs, _, _ = lib.load()
    gauges_json = json.loads((HERE / "vendor/pr1263/GAUGES.json").read_bytes())

    result = {
        "status": "PASS_COMPLEX_L248_L253_TEMPORAL_COMPOSITION",
        "base_commit": BASE,
        "selected_kappa": selected["kappa"],
        "predecessors": {"pr1263": PR1263, "pr1350": PR1350, "pr1353": PR1353},
        "fixed_pair": list(HELPERS),
        "scope": "Exact two-coordinate composition only; all other PR1263 gauges remain frozen.",
        "orientations": {},
    }

    for orientation in ("forward", "backward"):
        row248 = pr248["orientations"][orientation]
        row253 = pr253["orientations"][orientation]
        static_events = static_candidates[orientation]
        static_add_map = static_to_source_add_ids(programs[orientation], static_events)
        schedule248 = indexed_schedule(row248["schedule"],
                                       incident_add_ids(programs[orientation], 248), "L248")
        schedule253_static = indexed_schedule(
            row253["schedule"], incident_add_ids(static_events, 253), "L253 static stream")
        schedule253 = {static_add_map[index]: exponent
                       for index, exponent in schedule253_static.items()}
        need(set(schedule253) == set(incident_add_ids(programs[orientation], 253)),
             orientation + " L253 schedule mapped to source ADDs")
        union = require_disjoint(schedule248, schedule253)
        need(len(schedule248) == 71 and len(schedule253) == 96 and len(union) == 167,
             orientation + " exact disjoint support sizes")
        gauges = {int(h): int(k) for h, k in gauges_json[orientation].items()}
        need(all(helper in gauges for helper in HELPERS), orientation + " static pair membership")

        single248 = build_pair_word(programs[orientation], word, gauges,
                                    {248: schedule248}, (248,))
        single253 = build_pair_word(programs[orientation], word, gauges,
                                    {253: schedule253}, (253,))
        single248_invoice = lib.invoice(single248, "copy-init")
        single253_invoice = lib.invoice(single253, "copy-init")
        need(sha(canonical(single248)) == row248["candidate_sha256"],
             orientation + " exact PR1353 single-word reconstruction")
        need(single248_invoice["complex_primitives"] ==
             row248["candidate_invoice"]["complex_primitives"],
             orientation + " PR1353 single invoice")
        need(single253_invoice["complex_primitives"] ==
             row253["candidate_invoice"]["complex_primitives"],
             orientation + " PR1350 single invoice")
        need(lib.replay(single248, orientation)["formal_input_columns"] == 712
             and lib.replay(single253, orientation)["formal_input_columns"] == 712,
             orientation + " predecessor single-word endpoints")

        candidate = build_pair_word(programs[orientation], word, gauges,
                                    {248: schedule248, 253: schedule253})
        endpoint = lib.replay(candidate, orientation)
        invoice = lib.invoice(candidate, "copy-init")
        baseline = lib.invoice(static_candidates[orientation], "copy-init")
        pred_baseline = row253["baseline_static_invoice"]
        need(baseline["complex_primitives"] == pred_baseline["complex_primitives"],
             orientation + " PR1263 baseline invoice")
        saving248 = row248["saving_vs_pr1263_complex"]
        saving253 = row253["incremental_saving_complex"]
        expected_complex = baseline["complex_primitives"] - saving248 - saving253
        check_invoice(invoice["complex_primitives"], expected_complex,
                      orientation + " additive exact composition")
        check_invoice(invoice["real_primitives"], baseline["real_primitives"] - 45 - 91,
                      orientation + " additive real-primitive composition")
        need(invoice["paid_profile"] == baseline["paid_profile"],
             orientation + " recursive paid profile unchanged")
        need(endpoint["formal_input_columns"] == 712 and endpoint["all_restored"],
             orientation + " exact complete endpoint")
        need(invoice["charged_payload_bits"] == 192 and invoice["prefix_bits"] <= 192,
             orientation + " inherited payload charge")
        need(lib.replay(static_candidates[orientation], orientation)["formal_input_columns"] == 712,
             orientation + " baseline endpoint control")
        controls = verify_fault_controls(
            {248: row248["schedule"], 253: row253["schedule"]},
            {248: incident_add_ids(programs[orientation], 248),
             253: incident_add_ids(programs[orientation], 253)},
            union, invoice["complex_primitives"], expected_complex)
        result["orientations"][orientation] = {
            "L248_incident_adds": len(schedule248),
            "L253_incident_adds": len(schedule253),
            "inserted_scale_macros": (row248["scale_macros_for_helper"]
                                      + row253["scheduled_scale_macros"]),
            "shared_add_ids": 0,
            "combined_schedule_ids": len(union),
            "baseline_complex_primitives": baseline["complex_primitives"],
            "original_complex_primitives": row248["original_complex_primitives"],
            "L248_saving_complex": saving248,
            "L253_saving_complex": saving253,
            "combined_saving_complex": saving248 + saving253,
            "total_saving_vs_original_complex": (
                row248["original_complex_primitives"] - invoice["complex_primitives"]),
            "single_word_replays": {
                "L248": {"candidate_sha256": sha(canonical(single248)),
                         "complex_primitives": single248_invoice["complex_primitives"]},
                "L253": {"candidate_sha256": sha(canonical(single253)),
                         "complex_primitives": single253_invoice["complex_primitives"]},
            },
            "combined_invoice": invoice,
            "formal_endpoint": endpoint,
            "combined_word_sha256": sha(canonical(candidate)),
            "negative_controls": controls,
        }
    return result


def main():
    result = compute()
    path = HERE / "RESULT.json"
    if "--write" in sys.argv:
        need(not path.exists(), "refusing to overwrite RESULT.json")
        path.write_bytes(canonical(result) + b"\n")
    else:
        expected = json.loads(path.read_bytes())
        need(canonical(result) == canonical(expected), "frozen composition receipt")
    print(result["status"])
    for orientation, row in result["orientations"].items():
        print(orientation, "shared_add_ids", row["shared_add_ids"], "complex_primitives",
              row["combined_invoice"]["complex_primitives"], "columns",
              row["formal_endpoint"]["formal_input_columns"], "no_new_kappa")


if __name__ == "__main__":
    main()
