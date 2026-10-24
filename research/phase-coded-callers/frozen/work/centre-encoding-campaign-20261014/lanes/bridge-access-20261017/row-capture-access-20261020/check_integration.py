"""Bind the native carrier prefix to the actual D25 reuse dispatcher."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import argparse
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
PINS = {
    "prefix": (
        "new-core-transfer-20261017/low-displacement-20261020/"
        "fixed-reader-reuse-20261020/prefix-normal/CARRIER-PREFIX.json.gz",
        "54c561cfc49ad3fe1258ba5a8760eeadaa11784272cf458e2a6e54403a0e655e",
    ),
    "prefix_freeze": (
        "new-core-transfer-20261017/low-displacement-20261020/"
        "fixed-reader-reuse-20261020/PREFIX-FREEZE.json",
        "fc3cef0e499e5bc85c25bb0fc88f5ecd12e44b66799e3d793dac37de8d88d26e",
    ),
    "native_phase_review": (
        "new-native-recipes-20261017/line-entry-reuse-review-20261020/FREEZE.json",
        "cc5ed3b0ecc6eb5cec48f8baead43ec813042c3e83cd68104b7745366c13c55c",
    ),
    "query": (
        "bridge-access-20261017/row-capture-access-20261020/"
        "reuse-normal/REUSE-PROGRAM.json",
        "eead344f9a3f642056fd29b05a7e24d1a5d3504eec005eedc83e26b7fed8b82b",
    ),
    "query_freeze": (
        "bridge-access-20261017/row-capture-access-20261020/REUSE-FREEZE.json",
        "41d689596777344268bca937bb2e7fea302bfff443590aa42e46788409e563bf",
    ),
    "literal_query": (
        "new-core-transfer-20261017/low-displacement-20261020/"
        "fixed-reader-reuse-20261020/query-normal/ROUTED-QUERY.json.gz",
        "b94f7b8467bdcaf9150045fc5f7a1999640daab742faaaba55993c102be49d4a",
    ),
    "literal_query_freeze": (
        "new-core-transfer-20261017/low-displacement-20261020/"
        "fixed-reader-reuse-20261020/QUERY-FREEZE.json",
        "f111a90f7403f93494e9d1f83ae35dbf7dd72eddc8c9f8bf730d677b4a31402d",
    ),
    "views": (
        "bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
        "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473",
    ),
    "phase": (
        "bridge-access-20261017/check_bridge_access.py",
        "9510c5624dfb51d98767728084851e4ee75a135e6d7b546569a47fe458485111",
    ),
}
UNIT = [1 << j for j in range(25)]


def need(test, label):
    if not test:
        raise ValueError(label)


def raw_source(name):
    path, pin = PINS[name]
    raw = (LANES / path).read_bytes()
    if path.endswith(".gz"):
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Pinned source: " + name)
    return raw


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def add(target, source, coefficient):
    for column, value in source.items():
        target[column] = target.get(column, F(0)) + coefficient * value
        if not target[column]:
            del target[column]


def price(op, value):
    n, d = abs(value.numerator), value.denominator
    need(n and d & (d - 1) == 0, "Nonzero dyadic coefficient")
    if op == "scale":
        need(n & (n - 1) == 0, "The scale is a dyadic unit")
        return 2 * (abs(n.bit_length() - d.bit_length()) + (value < 0))
    return 2 * (3 + n.bit_length() - 1 + n.bit_count() + d.bit_length() - 1)


def check_prefix(word, response, selected):
    live = list(word["start"])
    state = [{p: F(1)} for p in range(640)]
    profile = Counter()
    scalar_price = 0
    for index, event in enumerate(word["events"]):
        if event[0] == "native":
            _, target, old, new, mass, key = event
            need(live[target] == old, "Native input frame")
            left, right = word["frames"][old], word["frames"][new]
            need(rank(left + right) == len(right), "Nested native frame")
            need(len(right) - len(left) == mass
                 == word["native_recipes"][key]["rank"], "Native rank")
            live[target] = new
            profile[mass] += 1
        else:
            need(event[0] == "scalar", "Prefix event grammar")
            (_, (op, target, source, coefficient), frame) = event
            value = F(coefficient)
            need(live[target] == frame, "Scalar target frame")
            if op == "add":
                need(source != target and live[source] == frame,
                     "Scalar source frame")
                need(source not in {112 + p for p in selected},
                     "The prefix does not read a selected target")
                add(state[target], state[source], value)
            else:
                need(op == "scale", "Prefix scalar grammar")
                state[target] = {j: value * v for j, v in state[target].items()}
            scalar_price += price(op, value)
        if index == 2389:
            need(all(live[p] == 1 for p in range(112)),
                 "All sources are FULL after the complete retained core")
    expected = [{p: F(1)} for p in range(640)]
    for p in range(112):
        if p not in selected:
            add(expected[112 + p], response[p], F(1))
    need(state == expected, "The full 640-column carrier prefix")
    need(live == word["final"], "The full prefix frame ledger")
    need(all(live[p] == live[112 + p] == 1 for p in selected),
         "Every selected query source and target is FULL")
    need(all(state[p] == {p: F(1)} for p in range(224, 640)),
         "All 416 arbitrary helper fields are restored")
    need(len(word["events"]) == 2406
         and word["stage_ranges"]["retained_core"] == [0, 2390]
         and word["stage_ranges"]["selected_line_progress"] == [2390, 2406]
         and "late_query" not in word["stage_ranges"], "The exact prefix cut")
    need(profile == {1: 1392, 2: 64, 3: 48, 8: 16}
         and scalar_price == 6456, "The complete prefix invoice")
    source_views = {v["port"]: v for v in word["input_views"] if v["role"] == "source"}
    selected_views = [v for v in word["input_views"] if v["role"] == "selected_target"]
    need(set(source_views) == set(range(112)) and len(selected_views) == 16,
         "The complete input adapter stock")
    for view in selected_views:
        source = source_views[view["port"]]
        need(view["field"] == 112 + view["port"] and view["port"] in selected
             and view["source_entry_port"] == view["port"], "Selected input adapter field")
        need(all(view[key] == source[key] for key in ("frame", "rank", "left", "right")),
             "The selected input adapter equals the source adapter")
    need({v["port"] for v in word["output_views"]} == set(range(112)) - selected,
         "Only ordinary target output adapters remain")
    need(len(word["input_views"]) == 128 and len(word["output_views"]) == 96,
         "The exact adapter count")
    return {
        "native_profile": dict(sorted(profile.items())),
        "native_rank": sum(k * v for k, v in profile.items()),
        "native_children": sum(profile.values()),
        "scalar_primitives": scalar_price,
        "arbitrary_input_columns": 640,
        "restored_arbitrary_helper_fields": 416,
        "input_adapters": 128, "ordinary_output_adapters": 96,
        "native_phase_review_is_pinned_dependency": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sources = {key: raw_source(key) for key in PINS}
    prefix, query, views = (json.loads(sources[key]) for key in ("prefix", "query", "views"))
    literal_query = json.loads(sources["literal_query"])
    need(literal_query["native_prefixes"] == prefix["providers"],
         "The literal query uses this exact complete native prefix")
    need(literal_query["source_pins"]["query"]["sha256"] == PINS["query"][1],
         "The literal query uses this exact path program")
    spec = importlib.util.spec_from_file_location("reuse_dispatcher_phase", LANES / PINS["phase"][0])
    phase = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(phase)
    selected = set(prefix["selected_ports"])
    need(prefix["selected_ports"] == query["pivots"], "The exact carried pivot set")
    response = [{int(j): F(v) for j, v in row.items()} for row in prefix["response"]]
    reports = {name: check_prefix(word, response, selected)
               for name, word in prefix["providers"].items()}
    records = {(v["stage"], v["port"]): v for v in views["entries"]}
    stage_programs, counts = [], Counter()
    for t in (1, 2):
        full_before = [(v, 1) for v in UNIT[:9 + 8 * (t - 1)]]
        full_after = [(v, 1) for v in UNIT[:9 + 8 * t]]
        exterior = [(v, 1) for v in UNIT[9:9 + 8 * t]]
        data_entries, data_exits = [], []
        for side, offset in (("X", 0), ("Y", 112)):
            for p in range(112):
                record = records[t, p]
                rho, q, align = (record[key] for key in
                                 ("route_columns", "q", "literal_stage_alignment"))
                need(all((a & b).bit_count() % 2 == int(i == j)
                         for i, a in enumerate(rho) for j, b in enumerate(rho)),
                     "Regular-cover orthogonal route")
                need([phase.act(rho, v) for v in rho] == UNIT
                     and phase.act(rho, q) == q, "The route fixes its intrinsic line")
                need(rho[9 + 8 * t:] == UNIT[9 + 8 * t:], "No future coordinate is changed")
                full_input = side == "X" or p in selected
                before = full_before + ([] if full_input else [(q, -1)])
                entry_delta = phase.act(rho, align["entry_" + side])
                actual = phase.add_phase(
                    phase.product([(phase.act(rho, v), n) for v, n in before]),
                    phase.line(entry_delta, 2))
                expected = phase.product(exterior + ([(q, 1)] if full_input else []))
                need(actual == expected, "Exact adjacent current entry phase")
                counts["entry_phase_equations"] += 1
                after = full_after + ([] if full_input else [(q, -1)])
                exit_key = "exit_X" if full_input else "exit_Y"
                exit_delta = align[exit_key]
                actual = phase.add_phase(
                    phase.product([(phase.act(rho, v), n) for v, n in after]),
                    phase.line(exit_delta, 2))
                need(actual == phase.product(after), "Exact global output phase")
                counts["exit_phase_equations"] += 1
                data_entries.append({
                    "field": offset + p, "port": p, "side": side,
                    "owner_from_body": "h=d*rho",
                    "route_columns": rho,
                    "translation_before_route": align["entry_" + side],
                    "translation_after_route": entry_delta,
                    "intrinsic_input": "Q_p" if full_input else "I",
                })
                data_exits.append({
                    "field": offset + p, "port": p, "side": side,
                    "owner_from_body": "h=d*rho",
                    "route_columns": rho,
                    "translation_after_route": exit_delta,
                    "global_output": "FULL" if full_input else "FULL*q_p",
                    "literal_translation_key": exit_key,
                })
        stage_programs.append({
            "service_stage": t, "physical_input_level": t - 1,
            "physical_output_level": t,
            "common_exterior_axes": [v for v, _ in exterior],
            "DATA_entry": data_entries, "DATA_exit": data_exits,
        })
    invocations = []
    for number, pair in enumerate(query["pairs"]):
        s, t = pair["reader_stage"], pair["service_stage"]
        need((s, t) in ((0, 1), (0, 2), (1, 2)) and s < t,
             "The checked past/current pair")
        need(pair["real_scalar_primitives"] == 11168
             and pair["monomial_map_calls"] == 2064
             and pair["native_children_in_query"] == 0, "The complete routed query invoice")
        literal = literal_query["queries"][f"{s}:{t}"]
        need(literal["reader_stage"] == s and literal["service_stage"] == t,
             "The exact literal query stage labels")
        need(sum(event[0] == "map" for event in literal["events"]) == 2064,
             "All literal query maps are retained")
        need(sum(price(event[1], F(event[4])) for event in literal["events"]
                 if event[0] == "scalar") == 11168, "The literal scalar query price")
        need(all(record["port"] in selected for record in query["carrier_recipes"]),
             "Only selected carrier paths are added")
        for provider in prefix["providers"]:
            invocations.append({
                "provider": provider, "reader_stage": s, "service_stage": t,
                "physical_input_level": t - 1,
                "physical_output_level": t,
                "stage_view_record": t - 1, "query_pair_record": number,
                "ordered_blocks": [
                    {"op": "DATA_entry", "record": t - 1, "map_calls": 224},
                    {"op": "native_input_adapters", "source": "prefix",
                     "provider": provider, "map_calls": 128},
                    {"op": "complete_native_carrier_cover_sweep", "source": "prefix",
                     "provider": provider, "event_range": [0, 2406]},
                    {"op": "ordinary_output_adapters", "source": "prefix",
                     "provider": provider, "map_calls": 96},
                    {"op": "DATA_exit", "record": t - 1, "map_calls": 224},
                    {"op": "complete_cover_barrier"},
                    {"op": "fixed_past_reader_query", "source": "query",
                     "pair_record": number, "literal_source": "literal_query",
                     "literal_key": f"{s}:{t}", "map_calls": 2064},
                ],
                "scalar_primitives": 17624,
                "map_call_bound": {
                    "DATA": 448, "local_endpoint_adapters": 224,
                    "native_side_maps": 3040, "late_query": 2064,
                    "total": 5776,
                },
            })
    need(counts == {"entry_phase_equations": 448, "exit_phase_equations": 448},
         "The complete adjacent D25 boundary census")
    payload = {
        "schema": "fixed-reader-global-dispatcher-v1", "source_pins": PINS,
        "dimension": 25, "selected_ports": prefix["selected_ports"],
        "stage_views": stage_programs, "invocations": invocations,
        "contract": {
            "input": "(Fprev*x, Fprev*diag(I_P,q_R)*w)",
            "output": "(Fnew*x, Fnew*diag(I_P,q_R)*(w+A_st*x))",
            "response_rows_P": "L_s*E_t",
            "response_rows_R": "(E_t)_R",
            "reader_label_is_not_physical_level": True,
            "arbitrary_independent_selected_records": True,
            "full_native_sweep_before_global_query": True,
        },
        "owner_contract": {
            "cover": "Regular O(25,2)",
            "data_partition": "For each field, d -> d*rho_(t,p) is a bijection.",
            "native_helpers": "Use the inherited 416-field helper contract; restore it per body.",
            "helper_hosting_reproved_here": False,
        },
        "native_phase_validation": "Use the pinned independent line-entry review.",
        "complete_supplier_claimed": False,
    }
    args.output.mkdir(parents=True, exist_ok=False)
    raw = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    (args.output / "DISPATCHER.json").write_bytes(raw)
    receipt = {
        "status": "PASS_FIXED_READER_NATIVE_D25_DISPATCHER",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "program_sha256": sha256(raw).hexdigest(), "source_pins": PINS,
        "providers": reports, "boundary_checks": dict(counts),
        "reader_service_pairs": [[0, 1], [0, 2], [1, 2]],
        "scalar_primitives": 17624, "query_map_calls": 2064,
        "total_monomial_call_bound": 5776,
        "inherited_helper_hosting_still_required": True,
        "complete_supplier_claimed": False,
    }
    (args.output / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
