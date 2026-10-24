#!/usr/bin/env python3
"""Bind the native prefix, DATA dispatcher, and routed reader query."""

import argparse
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[2]
PINS = {
    "helper": (HERE / "emit_routed_query.py",
               "78d505f55b4646fff0d1c40b53ad11327874bee6ebd074013c4288197f3fe900"),
    "query": (HERE / "query-normal/ROUTED-QUERY.json.gz",
              "b94f7b8467bdcaf9150045fc5f7a1999640daab742faaaba55993c102be49d4a"),
    "dispatcher": (LANES / "bridge-access-20261017/row-capture-access-20261020/integration-v2-normal/DISPATCHER.json",
                   "35772f75d983661a21f6a6ba69d06fb7bcdcaaaf20ec7ad838863541a8581e24"),
    "dispatcher_freeze": (LANES / "bridge-access-20261017/row-capture-access-20261020/INTEGRATION-FREEZE.json",
                          "bbc0e4026b1d003dedc55c78cd6300ef429ee2d95712e55bbab896da2840c331"),
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
spec = importlib.util.spec_from_file_location("fixed_reader_service_query", PINS["helper"][0])
q = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = q
spec.loader.exec_module(q)


def verify(bundle):
    prefix = json.loads(q.read("prefix"))
    capture = json.loads(q.read("capture"))
    old_query = json.loads(q.read("query"))
    selected = set(bundle["selected_ports"])
    need(bundle["native_prefixes"] == prefix["providers"], "The full native programs are unchanged")
    response = q.base.n.rows(prefix["response"])
    reader = q.base.n.rows(capture["centre_reader"])
    phase_checks = 0
    routed_stage_views = {}
    for stage in bundle["stage_views"]:
        t = stage["service_stage"]
        need(stage["physical_input_level"] == t - 1
             and stage["physical_output_level"] == t, "The adjacent physical level")
        before = [(v, 1) for v in q.UNIT[:9 + 8 * (t - 1)]]
        after = [(v, 1) for v in q.UNIT[:9 + 8 * t]]
        exterior = [(v, 1) for v in stage["common_exterior_axes"]]
        need(exterior == [(v, 1) for v in q.UNIT[9:9 + 8 * t]], "The complete common exterior")
        entries = {item["field"]: item for item in stage["DATA_entry"]}
        exits = {item["field"]: item for item in stage["DATA_exit"]}
        need(set(entries) == set(exits) == set(range(224)), "All data boundary fields")
        for field in range(224):
            entry, out = entries[field], exits[field]
            p = field % 112
            rho = tuple(entry["route_columns"])
            need(rho == tuple(out["route_columns"]), "The same owner partition at both ends")
            need(q.compose(rho, rho) == q.UNIT
                 and q.transpose(rho) == rho, "The orthogonal involutive DATA route")
            line = prefix["ports"][p]
            need(q.act(rho, line) == line, "The intrinsic line is fixed")
            full = field < 112 or p in selected
            physical_before = before + ([] if full else [(line, -1)])
            actual = q.phase.add_phase(
                q.phase.product([(q.act(rho, v), exponent) for v, exponent in physical_before]),
                q.phase.line(entry["translation_after_route"], 2))
            expected = q.phase.product(exterior + ([(line, 1)] if full else []))
            need(actual == expected and entry["intrinsic_input"] == ("Q_p" if full else "I"),
                 "The exact global-to-local input phase")
            need(q.act(rho, entry["translation_before_route"]) == entry["translation_after_route"],
                 "The exact translation order at entry")
            physical_after = after + ([] if full else [(line, -1)])
            actual = q.phase.add_phase(
                q.phase.product([(q.act(rho, v), exponent) for v, exponent in physical_after]),
                q.phase.line(out["translation_after_route"], 2))
            need(actual == q.phase.product(physical_after)
                 and out["global_output"] == ("FULL" if full else "FULL*q_p"),
                 "The exact local-to-global output phase")
            phase_checks += 2
        routed_stage_views[t] = [
            {"port": p, "route_columns": entries[p]["route_columns"],
             "translation": exits[p]["translation_after_route"]} for p in range(112)]
    prefix_reports = {}
    for provider, word in bundle["native_prefixes"].items():
        prefix_reports[provider] = q.base.verify(
            word, q.base.n.r.identity(112), response, [{} for _ in range(112)], selected)
    expected_pairs = {(provider, s, t) for provider in bundle["native_prefixes"]
                      for s, t in ((0, 1), (0, 2), (1, 2))}
    actual_pairs = set()
    reports = []
    for service in bundle["services"]:
        provider, s, t = service["provider"], service["reader_stage"], service["service_stage"]
        actual_pairs.add((provider, s, t))
        key = f"{s}:{t}"
        word = bundle["queries"][key]
        pair = old_query["pairs"][service["query_pair_record"]]
        need((pair["reader_stage"], pair["service_stage"]) == (s, t), "The exact retained reader")
        need(pair["current_code_views"] == routed_stage_views[t],
             "The query current chart is the actual DATA exit chart")
        need(service["physical_input_level"] == t - 1
             and service["physical_output_level"] == t, "The reader label is not the physical level")
        need([part["op"] for part in service["ordered_blocks"]] == [
            "DATA_entry", "native_input_adapters", "complete_native_carrier_cover_sweep",
            "ordinary_output_adapters", "DATA_exit", "complete_cover_barrier",
            "fixed_past_reader_query"], "The complete cover barrier precedes the query")
        prefix_word = bundle["native_prefixes"][provider]
        need(service["ordered_blocks"][2]["event_range"] == [0, len(prefix_word["events"])],
             "No native event is omitted")
        et = q.routed(response, range(112), routed_stage_views[t])
        ls = q.routed(reader, bundle["selected_ports"], pair["old_reader_views"])
        initial = q.initial_prefix(et, selected)
        expected = [dict(row) for row in initial]
        for p, row in zip(bundle["selected_ports"], q.product(ls, et)):
            q.add(expected[112 + p], row)
        actual, query_report = q.replay(word["events"], word["maps"], initial, selected)
        need(actual == expected, "The complete service on all640 formal input fields")
        scalar = prefix_reports[provider]["real_scalar_primitives"] + query_report["scalar_primitives"]
        maps = service["map_call_bound"]
        need(scalar == service["scalar_primitives"] == 17624
             and maps == {"DATA": 448, "late_query": 2064, "local_endpoint_adapters": 224,
                          "native_side_maps": 3040, "total": 5776},
             "The complete service invoice")
        reports.append({"provider": provider, "reader_stage": s, "service_stage": t,
                        "native_mass": 1792, "scalar_primitives": scalar,
                        "monomial_map_call_bound": maps["total"],
                        "all_independent_input_fields": 640,
                        "query_prefix_formal_one_norm": query_report["exact_prefix_content_one_norm"],
                        "query_additional_binary_height": query_report["additional_binary_height"]})
    need(actual_pairs == expected_pairs and len(bundle["services"]) == len(expected_pairs),
         "Both providers and all three actual stage pairs")
    return {"complete_services": reports, "data_boundary_phase_equations": phase_checks,
            "prefix_reports": prefix_reports}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    query = json.loads(read("query"))
    dispatcher = json.loads(read("dispatcher"))
    read("dispatcher_freeze")
    for name, (path, pin) in dispatcher["source_pins"].items():
        raw = (LANES / path).read_bytes()
        if path.endswith(".gz"):
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == pin, "The complete dispatcher source pin " + name)
    bundle = {
        "schema": "six-fixed-reader-forward-services-v1",
        "source_pins": {key: {"path": str(path), "sha256": pin}
                        for key, (path, pin) in PINS.items()},
        "selected_ports": dispatcher["selected_ports"], "contract": dispatcher["contract"],
        "owner_contract": dispatcher["owner_contract"], "stage_views": dispatcher["stage_views"],
        "native_prefixes": query["native_prefixes"], "queries": query["queries"],
        "services": dispatcher["invocations"],
        "scope": "Complete data interfaces on the regular D25 cover, under the inherited416-helper host contract. Recursive hosting and the complete supplier cost remain separate.",
    }
    report = verify(bundle)
    raw = (json.dumps(bundle, sort_keys=True, separators=(",", ":")) + "\n").encode()
    need(verify(json.loads(raw)) == report, "The complete serialized service bundle")
    (args.out / "FIXED-READER-SERVICES.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {"status": "PASS_EXACT_SIX_FIXED_READER_D25_SERVICES",
               "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "payload_decompressed_sha256": sha256(raw).hexdigest(), **report,
               "scope": bundle["scope"]}
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
