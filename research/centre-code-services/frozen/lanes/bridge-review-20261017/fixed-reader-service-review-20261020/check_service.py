"""Review the complete D25 service from pinned local components."""

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
QUERY_REVIEW = HERE.parent / "fixed-reader-reuse-review-20261020"
DISPATCH = LANES / "bridge-access-20261017/row-capture-access-20261020"
CORE = LANES / "new-core-transfer-20261017/low-displacement-20261020/fixed-reader-reuse-20261020"
PHASE_REVIEW = LANES / "new-native-recipes-20261017/line-entry-reuse-review-20261020"
FREEZES = {
    "independent_query": (QUERY_REVIEW / "FREEZE.json",
                          "d8d782ecc13fdd2d26380fc4b047fc6d6781417ec694fdd3dea910dce04c2e2a"),
    "dispatcher": (DISPATCH / "INTEGRATION-FREEZE.json",
                   "bbc0e4026b1d003dedc55c78cd6300ef429ee2d95712e55bbab896da2840c331"),
    "service": (CORE / "SERVICE-FREEZE.json",
                "177d6ae2f3971deac98e3385dda32e82ddabf0c8176e88ac1255323aed8d688f"),
    "native_phase": (PHASE_REVIEW / "FREEZE.json",
                     "cc5ed3b0ecc6eb5cec48f8baead43ec813042c3e83cd68104b7745366c13c55c"),
    "prefix": (CORE / "PREFIX-FREEZE.json",
               "fc3cef0e499e5bc85c25bb0fc88f5ecd12e44b66799e3d793dac37de8d88d26e"),
    "query": (CORE / "QUERY-FREEZE.json",
              "f111a90f7403f93494e9d1f83ae35dbf7dd72eddc8c9f8bf730d677b4a31402d"),
}
PAYLOADS = {
    "dispatcher": (DISPATCH / "integration-v2-normal/DISPATCHER.json",
                   "35772f75d983661a21f6a6ba69d06fb7bcdcaaaf20ec7ad838863541a8581e24"),
    "service": (CORE / "service-normal/FIXED-READER-SERVICES.json.gz",
                "88d25925705e6657656afb727430ce0d541c5e657426166363694d8b66180d13"),
    "prefix": (CORE / "prefix-normal/CARRIER-PREFIX.json.gz",
               "54c561cfc49ad3fe1258ba5a8760eeadaa11784272cf458e2a6e54403a0e655e"),
    "query": (CORE / "query-normal/ROUTED-QUERY.json.gz",
              "b94f7b8467bdcaf9150045fc5f7a1999640daab742faaaba55993c102be49d4a"),
    "line_entry": (
        CORE.parent / "row-only-capture-20261020/reuse-normal/LINE-ENTRY-REUSE.json.gz",
        "efe67a962752f2c36513d84094d215fd0909a5360707938ff99d62743dc72110"),
}


def need(test, label):
    if not test:
        raise ValueError(label)


def digest(raw):
    return sha256(raw).hexdigest()


def read(path, pin, decode_gzip=False):
    raw = path.read_bytes()
    if decode_gzip:
        raw = gzip.decompress(raw)
    need(digest(raw) == pin, "Source pin: " + str(path))
    return raw


def validate_freeze(path, pin):
    value = json.loads(read(path, pin))
    for name, expected in value["files"].items():
        read(path.parent / name, expected)
    return value


validate_freeze(*FREEZES["independent_query"])
spec = importlib.util.spec_from_file_location("independent_reuse_math", QUERY_REVIEW / "check_review.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def binary_rank(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            bit = vector.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = vector
                break
            vector ^= pivots[bit]
    return len(pivots)


def prefix_replay(word, response):
    state = r.eye(640)
    live = list(word["start"])
    profile = Counter()
    price = 0
    peak = F(1)
    height = 0
    for index, event in enumerate(word["events"]):
        if event[0] == "native":
            _, target, old, new, rank, key = event
            need(live[target] == old, "Prefix native frame")
            left, right = word["frames"][old], word["frames"][new]
            need(binary_rank(left) == len(left) and binary_rank(right) == len(right)
                 and binary_rank(left + right) == len(right)
                 and len(right) - len(left) == rank, "Positive nested native rank")
            need(word["native_recipes"][key]["rank"] == rank, "Bound native recipe")
            live[target] = new
            profile[rank] += 1
        else:
            need(event[0] == "scalar", "Prefix event grammar")
            _, (op, target, origin, coefficient), frame = event
            value = F(coefficient)
            need(live[target] == frame, "Prefix scalar target frame")
            if op == "scale":
                state[target] = {j: value * v for j, v in state[target].items()}
            else:
                need(op == "add" and live[origin] == frame and origin != target,
                     "Prefix scalar source frame")
                for j, v in state[origin].items():
                    r.put(state[target], j, value * v)
            price += r.real_price(op, value)
            peak = max(peak, sum(abs(v) for v in state[target].values()))
            height = max(height, max((v.denominator.bit_length() - 1
                                      for v in state[target].values()), default=0))
        need(target < 224, "No event writes an outside helper")
        if index == 2389:
            need(all(live[p] == 1 for p in range(112)), "The complete source cut")
    expected = r.eye(640)
    for p in range(112):
        if p not in r.PSET:
            for j, value in response[p].items():
                r.put(expected[112 + p], j, value)
    need(state == expected, "Independent complete prefix map on 640 input columns")
    need(live == word["final"], "Complete prefix frame ledger")
    need(all(live[p] == 1 for p in range(112))
         and all(live[112 + p] == 1 for p in r.PIVOTS), "All query fields are FULL")
    need(price == 6456 and profile == {1: 1392, 2: 64, 3: 48, 8: 16}, "Prefix price")
    need(peak == 22 and height == 1, "Prefix content bounds")
    return {"input_columns": 640, "restored_outside_fields": 416,
            "native_profile": dict(profile), "native_mass": sum(k * v for k, v in profile.items()),
            "native_children": sum(profile.values()), "scalar_primitives": price,
            "content_row_sum_peak": str(peak), "content_binary_height": height}


def query_replay(word, initial):
    state = [dict(row) for row in initial]
    scalar, maps = 0, 0
    peak = max(sum(abs(v) for v in row.values()) for row in state)
    height = max(v.denominator.bit_length() - 1 for row in state for v in row.values())
    for event in word["events"]:
        if event[0] == "map":
            _, target, map_index = event
            a = tuple(word["maps"][map_index]["columns"])
            state[target] = {(j, r.product(a, b)): v for (j, b), v in state[target].items()}
            maps += 1
        else:
            need(event[0] == "scalar", "Query event grammar")
            _, op, target, origin, coefficient = event
            value = F(coefficient)
            scalar += r.real_price(op, value)
            if op == "scale":
                state[target] = {j: value * v for j, v in state[target].items()}
            else:
                need(op == "add" and origin != target, "Query ADD")
                need(origin < 112 or origin - 112 in r.PSET, "No ordinary Y source")
                for key, v in state[origin].items():
                    r.put(state[target], key, value * v)
            peak = max(peak, sum(abs(v) for v in state[target].values()))
            height = max(height, max((v.denominator.bit_length() - 1
                                      for v in state[target].values()), default=0))
        need(target < 112 or target - 112 in r.PSET, "Only FULL query fields are changed")
    need(scalar == 11168 and maps == 2064, "Literal query price")
    return state, {"scalar_primitives": scalar, "map_calls": maps,
                   "content_row_sum_peak": str(peak), "content_binary_height": height}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "normal")
    args = parser.parse_args()
    for path, pin in FREEZES.values():
        validate_freeze(path, pin)
    data = {key: json.loads(read(path, pin, path.suffix == ".gz"))
            for key, (path, pin) in PAYLOADS.items()}
    dispatcher, service, prefix, query, old = (data[key] for key in
                                              ("dispatcher", "service", "prefix", "query", "line_entry"))
    for path, pin in dispatcher["source_pins"].values():
        read(LANES / path, pin, path.endswith(".gz"))
    phase_inputs = json.loads((PHASE_REVIEW / "normal/INPUTS.json").read_bytes())
    for path, pins in phase_inputs.items():
        raw = read(LANES / path, pins["sha256"])
        if "decompressed_sha256" in pins:
            need(digest(gzip.decompress(raw)) == pins["decompressed_sha256"], "Phase input payload")
    old_path = str(PAYLOADS["line_entry"][0].relative_to(LANES))
    need(phase_inputs[old_path]["decompressed_sha256"] == PAYLOADS["line_entry"][1],
         "The inherited phase review binds this exact line-entry word")
    need(service["native_prefixes"] == prefix["providers"] == query["native_prefixes"],
         "Exact native bundle")
    need(service["queries"] == query["queries"], "Exact query bundle")
    need(service["services"] == dispatcher["invocations"]
         and service["stage_views"] == dispatcher["stage_views"]
         and service["contract"] == dispatcher["contract"]
         and service["owner_contract"] == dispatcher["owner_contract"], "Exact dispatcher bundle")
    need(tuple(service["selected_ports"]) == tuple(prefix["selected_ports"]) == r.PIVOTS,
         "Unchanged selected fields")
    source = {key: json.loads(read(LANES / path, pin))
              for key, (path, pin) in r.PINS.items() if key in ("capture", "views")}
    capture, views = source["capture"], source["views"]
    response = r.sparse(prefix["response"])
    need(response == r.sparse(capture["response"]) and prefix["ports"] == old["ports"],
         "The actual response and port order")
    reader = r.sparse(capture["centre_reader"])
    views_by_id = {(v["stage"], v["port"]): v for v in views["entries"]}
    source_query = json.loads((DISPATCH / "reuse-normal/REUSE-PROGRAM.json").read_bytes())
    prefix_reports = {}
    for name, word in prefix["providers"].items():
        inherited = old["providers"][name]
        need(word["events"] == inherited["events"][:2406], "Exact reviewed native prefix")
        need(word["stage_ranges"] == {
            "precode": [0, 0], "retained_core": [0, 2390], "selected_line_progress": [2390, 2406]},
            "The prefix has no local late query")
        for key in ("start", "final", "frames", "native_recipes", "input_views",
                    "output_views", "retained_original_event_indices"):
            need(word[key] == inherited[key], "Inherited phase or frame bytes: " + key)
        need(len(word["input_views"]) == 128 and len(word["output_views"]) == 96,
             "Endpoint adapter counts")
        need({v["field"] for v in word["input_views"]} ==
             set(range(112)) | {112 + p for p in r.PIVOTS}, "Every input adapter field")
        need({v["port"] for v in word["output_views"]} == set(range(112)) - r.PSET,
             "Only ordinary output adapters")
        prefix_reports[name] = prefix_replay(word, response)
    routes = {(s, p): r.route(prefix["ports"][p], s) for s in range(3) for p in range(112)}
    phase_count = Counter()
    wrong_entry = 0
    for stage in service["stage_views"]:
        t = stage["service_stage"]
        need(t in (1, 2) and stage["physical_input_level"] == t - 1
             and stage["physical_output_level"] == t, "Adjacent physical stage")
        need(stage["common_exterior_axes"] == list(r.UNIT[9:9 + 8 * t]), "Common exterior")
        entries = {v["field"]: v for v in stage["DATA_entry"]}
        exits = {v["field"]: v for v in stage["DATA_exit"]}
        need(len(stage["DATA_entry"]) == len(stage["DATA_exit"]) == 224
             and set(entries) == set(exits) == set(range(224)), "All DATA fields")
        for field in range(224):
            p = field % 112
            side = "X" if field < 112 else "Y"
            q = prefix["ports"][p]
            rho = routes[t, p]
            actual = views_by_id[t, p]
            align = actual["literal_stage_alignment"]
            entry, out = entries[field], exits[field]
            full = side == "X" or p in r.PSET
            need(tuple(entry["route_columns"]) == tuple(out["route_columns"]) ==
                 tuple(actual["route_columns"]) == rho, "The literal DATA route")
            need(entry["side"] == out["side"] == side
                 and entry["port"] == out["port"] == p, "The boundary field binding")
            need(entry["translation_before_route"] == align["entry_" + side]
                 and entry["translation_after_route"] == r.apply(rho, align["entry_" + side]),
                 "The literal input translation order")
            exit_key = "exit_X" if full else "exit_Y"
            need(out["literal_translation_key"] == exit_key
                 and out["translation_after_route"] == align[exit_key], "The literal output translation")
            before = r.full_phase(t - 1, rho)
            if not full:
                before = r.add_phase(before, r.line_phase(q, -1))
            obtained = r.add_phase(before, r.line_phase(entry["translation_after_route"], 2))
            expected = r.sum_phase((x, 1) for x in r.UNIT[9:9 + 8 * t])
            if full:
                expected = r.add_phase(expected, r.line_phase(q, 1))
            need(obtained == expected and entry["intrinsic_input"] == ("Q_p" if full else "I"),
                 "Exact input Z4 equation")
            wrong_entry += r.add_phase(before, r.line_phase(entry["translation_before_route"], 2)) != expected
            after = r.full_phase(t, rho)
            expected_out = r.full_phase(t)
            if not full:
                after = r.add_phase(after, r.line_phase(q, -1))
                expected_out = r.add_phase(expected_out, r.line_phase(q, -1))
            need(r.add_phase(after, r.line_phase(out["translation_after_route"], 2)) == expected_out
                 and out["global_output"] == ("FULL" if full else "FULL*q_p"), "Exact output Z4 equation")
            phase_count["entry"] += 1
            phase_count["exit"] += 1
    need(phase_count == {"entry": 448, "exit": 448} and wrong_entry > 0, "Boundary completeness and control")
    query_reports = {}
    for key, word in service["queries"].items():
        s, t = word["reader_stage"], word["service_stage"]
        need(key == f"{s}:{t}", "Literal query labels")
        for view in word["maps"]:
            a, ai = tuple(view["columns"]), tuple(view["inverse_columns"])
            need(r.product(a, ai) == r.product(ai, a) == r.UNIT
                 and ai == r.transpose(a), "Literal query map inverse")
            need(a[9 + 8 * t:] == r.UNIT[9 + 8 * t:], "No future query axis")
            delta = r.phase_translation(r.add_phase(r.full_phase(t), r.minus_phase(r.full_phase(t, a))))
            need(view["translation"] == delta and view["inverse_translation"] == r.apply(ai, delta),
                 "Every literal query map phase")
        pair = next(pair for pair in source_query["pairs"]
                    if (pair["reader_stage"], pair["service_stage"]) == (s, t))
        current = [{"port": p, "route_columns": list(routes[t, p]),
                    "translation": views_by_id[t, p]["literal_stage_alignment"]["exit_X"]}
                   for p in range(112)]
        need(pair["current_code_views"] == current, "The query uses the actual DATA output chart")
        et = r.routed_matrix(response, range(112), t, routes)
        ls = r.routed_matrix(reader, r.PIVOTS, s, routes)
        desired = r.multiply_routed(ls, et)
        initial = [{(i, r.UNIT): F(1)} for i in range(640)]
        for p in range(112):
            if p not in r.PSET:
                for term, value in et[p].items():
                    r.put(initial[112 + p], term, value)
        expected = [dict(row) for row in initial]
        for p, row in zip(r.PIVOTS, desired):
            for term, value in row.items():
                r.put(expected[112 + p], term, value)
        result, report = query_replay(word, initial)
        need(result == expected, "The complete service map on all 640 input columns")
        need(report["content_row_sum_peak"] == "448" and report["content_binary_height"] == 2,
             "The complete literal query bounds")
        query_reports[key] = report
    reports = []
    for record in service["services"]:
        name, s, t = record["provider"], record["reader_stage"], record["service_stage"]
        key = f"{s}:{t}"
        blocks = record["ordered_blocks"]
        need([b["op"] for b in blocks] == [
            "DATA_entry", "native_input_adapters", "complete_native_carrier_cover_sweep",
            "ordinary_output_adapters", "DATA_exit", "complete_cover_barrier", "fixed_past_reader_query"],
            "The exact barrier order")
        need(blocks[2]["event_range"] == [0, 2406] and blocks[6]["literal_key"] == key,
             "The complete native and query blocks")
        need(record["stage_view_record"] == blocks[0]["record"] == blocks[4]["record"] == t - 1
             and service["stage_views"][t - 1]["service_stage"] == t,
             "The service selects the actual stage views")
        need(all(blocks[i]["provider"] == name and blocks[i]["source"] == "prefix"
                 for i in (1, 2, 3)), "The service selects one complete native provider")
        pair_index = record["query_pair_record"]
        bound_pair = source_query["pairs"][pair_index]
        need(blocks[6]["pair_record"] == pair_index
             and blocks[6]["source"] == "query" and blocks[6]["literal_source"] == "literal_query"
             and (bound_pair["reader_stage"], bound_pair["service_stage"]) == (s, t),
             "The service selects the actual reader query")
        need(record["physical_input_level"] == t - 1 and record["physical_output_level"] == t,
             "The reader label is not the physical level")
        prefix_report, query_report = prefix_reports[name], query_reports[key]
        map_invoice = {
            "DATA": 448, "local_endpoint_adapters": 128 + 96,
            "native_side_maps": 2 * prefix_report["native_children"],
            "late_query": query_report["map_calls"]}
        map_invoice["total"] = sum(map_invoice.values())
        scalar = prefix_report["scalar_primitives"] + query_report["scalar_primitives"]
        need(scalar == record["scalar_primitives"] == 17624
             and map_invoice == record["map_call_bound"] and map_invoice["total"] == 5776,
             "The full service invoice")
        reports.append({"provider": name, "reader_stage": s, "service_stage": t,
                        "all_input_columns": 640, "native_mass": prefix_report["native_mass"],
                        "scalar_primitives": scalar, "monomial_map_call_bound": map_invoice["total"]})
    need(len(reports) == 6 and {(x["provider"], x["reader_stage"], x["service_stage"]) for x in reports}
         == {(p, s, t) for p in prefix_reports for s, t in ((0, 1), (0, 2), (1, 2))},
         "Both providers and all three pairs")
    receipt = {
        "status": "PASS_INDEPENDENT_SIX_FIXED_READER_D25_SERVICES",
        "checker_sha256": digest(Path(__file__).read_bytes()),
        "frozen_dependencies": {k: {"path": str(p), "sha256": h} for k, (p, h) in FREEZES.items()},
        "payloads": {k: {"path": str(p), "decompressed_sha256": h} for k, (p, h) in PAYLOADS.items()},
        "native_phase_files_rechecked": len(phase_inputs),
        "prefix_reports": prefix_reports, "query_reports": query_reports,
        "boundary_phase_checks": dict(phase_count), "wrong_entry_translation_control_failures": wrong_entry,
        "services": reports, "producer_code_imported": False,
        "native_phase_validation": "Exact bytes of the independently reviewed line-entry components.",
        "helper_hosting_reproved": False, "finite_monomial_price_proved": False,
        "recursive_precision_proved": False, "complete_supplier_claimed": False,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    (args.output / "REVIEW-CHECKS.json").write_bytes(raw)
    print(receipt["status"])
    print(digest(raw))


if __name__ == "__main__":
    main()
