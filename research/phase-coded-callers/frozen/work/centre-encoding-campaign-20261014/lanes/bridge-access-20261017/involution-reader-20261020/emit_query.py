"""Emit a restored-source query for the actual routed involution."""

from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import argparse
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
PINS = {
    "involution": (
        "controller-followthrough-20261017/row-involution-20261020/"
        "run-normal/ROW-INVOLUTION.json",
        "a25551b3b99b82477fde561a742fabe1114acbfe6c67cd14284747aaac3dd95b",
    ),
    "capture": (
        "controller-followthrough-20261017/row-capture-20261020/"
        "run-normal/ROW-CAPTURE.json",
        "4c98af5d7a1437a03f53e84f0f2cbc7cd2ac47d4c6d4ee1523c16bf469692eb7",
    ),
    "prefix": (
        "new-core-transfer-20261017/low-displacement-20261020/"
        "fixed-reader-reuse-20261020/prefix-normal/CARRIER-PREFIX.json.gz",
        "54c561cfc49ad3fe1258ba5a8760eeadaa11784272cf458e2a6e54403a0e655e",
    ),
    "view_query": (
        "bridge-access-20261017/row-capture-access-20261020/"
        "reuse-normal/REUSE-PROGRAM.json",
        "eead344f9a3f642056fd29b05a7e24d1a5d3504eec005eedc83e26b7fed8b82b",
    ),
    "dispatcher": (
        "bridge-access-20261017/row-capture-access-20261020/"
        "integration-v2-normal/DISPATCHER.json",
        "35772f75d983661a21f6a6ba69d06fb7bcdcaaaf20ec7ad838863541a8581e24",
    ),
    "dispatcher_freeze": (
        "bridge-access-20261017/row-capture-access-20261020/INTEGRATION-FREEZE.json",
        "bbc0e4026b1d003dedc55c78cd6300ef429ee2d95712e55bbab896da2840c331",
    ),
    "operator_engine": (
        "new-core-transfer-20261017/low-displacement-20261020/"
        "fixed-reader-reuse-20261020/emit_routed_query.py",
        "78d505f55b4646fff0d1c40b53ad11327874bee6ebd074013c4288197f3fe900",
    ),
}


def need(test, label):
    if not test:
        raise ValueError(label)


def read(name):
    path, pin = PINS[name]
    raw = (LANES / path).read_bytes()
    if path.endswith(".gz"):
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Pinned source: " + name)
    return raw


def load_engine():
    read("operator_engine")
    spec = importlib.util.spec_from_file_location(
        "involution_reader_engine", LANES / PINS["operator_engine"][0])
    engine = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = engine
    spec.loader.exec_module(engine)
    return engine


def emit_word(engine, pair, involution, capture, pivots):
    events, maps, registry, ranges = [], [], {}, {}
    stage = pair["service_stage"]
    full_axes = engine.UNIT[:9 + 8 * stage]
    full = engine.phase.product([(v, 1) for v in full_axes])

    def register(columns, translation):
        columns = tuple(columns)
        key = columns, translation
        if key not in registry:
            inverse = engine.transpose(columns)
            need(engine.compose(columns, inverse) == engine.compose(inverse, columns)
                 == engine.UNIT, "The route is orthogonal")
            need(columns[9 + 8 * stage:] == engine.UNIT[9 + 8 * stage:],
                 "The route fixes all future axes")
            transformed = engine.phase.product(
                [(engine.act(columns, v), 1) for v in full_axes])
            need(engine.phase.add_phase(transformed, engine.phase.line(translation, 2)) == full,
                 "The complete FULL phase equation")
            registry[key] = len(maps)
            maps.append({
                "columns": columns, "translation": translation,
                "inverse_columns": inverse,
                "inverse_translation": engine.act(inverse, translation),
            })
        return registry[key]

    def view(field, record, inverse=False):
        route, delta = tuple(record["route_columns"]), record["translation"]
        if inverse:
            route = engine.transpose(route)
            delta = engine.act(route, delta)
        events.append(["map", field, register(route, delta)])

    current = {v["port"]: v for v in pair["current_code_views"]}
    old = {v["port"]: v for v in pair["old_reader_views"]}
    ordinary = sorted(set(range(112)) - set(pivots))

    def apply_current(name):
        begin = len(events)
        for p in range(112):
            view(p, current[p])
        for op, target, source, coefficient in involution["common_frame_words"]["A"]:
            events.append(["scalar", op, target, source, coefficient])
        for p in reversed(range(112)):
            view(p, current[p], inverse=True)
        ranges[name] = [begin, len(events)]

    apply_current("apply_current_involution")
    begin = len(events)
    fields = [(p, p) for p in ordinary] + [(112 + p, p) for p in pivots]
    for field, p in fields:
        view(field, old[p])
    for op, target, source, coefficient in capture["scalar_word"]:
        need(target in pivots and (source is None or source in ordinary),
             "The old complement reader is unchanged")
        events.append(["scalar", op, 112 + target, source, coefficient])
    for field, p in reversed(fields):
        view(field, old[p], inverse=True)
    ranges["old_reader_complement"] = [begin, len(events)]
    begin = len(events)
    for p in pivots:
        events.append(["scalar", "add", 112 + p, p, "1"])
    ranges["selected_reader_copy"] = [begin, len(events)]
    apply_current("restore_current_involution")
    return {"reader_stage": pair["reader_stage"], "service_stage": stage,
            "events": events, "maps": maps, "stage_ranges": ranges}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = {name: read(name) for name in PINS}
    inv, capture, prefix, access, dispatch = (
        json.loads(source[name])
        for name in ("involution", "capture", "prefix", "view_query", "dispatcher"))
    engine = load_engine()
    pivots = inv["pivots"]
    selected = set(pivots)
    need(pivots == prefix["selected_ports"] == capture["pivots"] == access["pivots"],
         "All packets use the same physical selected ports")
    matrix = engine.base.n.rows(inv["response"])
    old_response = engine.base.n.rows(prefix["response"])
    reader = engine.base.n.rows(capture["centre_reader"])
    need(all(matrix[p] == old_response[p] for p in range(112) if p not in selected),
         "The retained ordinary native response is exactly A_R")
    need(engine.base.n.r.product(matrix, matrix) == engine.base.n.r.identity(112),
         "The actual physical response is an involution")
    scalar_state = engine.base.n.r.identity(112)
    for op, target, origin, value in inv["common_frame_words"]["A"]:
        coefficient = F(value)
        if op == "add":
            engine.base.n.r.add(scalar_state[target], scalar_state[origin], coefficient)
        else:
            need(op == "scale", "Only scalar ADD and SCALE")
            scalar_state[target] = {j: coefficient * v for j, v in scalar_state[target].items()}
    need(scalar_state == matrix, "The complete 112-column current scalar A word")
    need(engine.base.n.r.price(inv["common_frame_words"]["A"]) == 3276,
         "The exact scalar price of A")
    prefix_reports = {}
    for provider, word in prefix["providers"].items():
        prefix_reports[provider] = engine.base.verify(
            word, engine.base.n.r.identity(112), matrix, [{} for _ in range(112)], selected)
    words, reports = {}, {}
    for pair in access["pairs"]:
        s, t = pair["reader_stage"], pair["service_stage"]
        key = f"{s}:{t}"
        stage_view = dispatch["stage_views"][t - 1]
        data_exits = {v["port"]: v for v in stage_view["DATA_exit"] if v["side"] == "X"}
        for view in pair["current_code_views"]:
            expected = data_exits[view["port"]]
            need(view["route_columns"] == expected["route_columns"]
                 and view["translation"] == expected["translation_after_route"],
                 "Current query views equal the actual DATA exits")
        at = engine.routed(matrix, range(112), pair["current_code_views"])
        ls = engine.routed(reader, pivots, pair["old_reader_views"])
        direct = engine.product(ls, at)
        word = emit_word(engine, pair, inv, capture, pivots)
        initial = engine.initial_prefix(at, selected)
        expected = [dict(row) for row in initial]
        for p, row in zip(pivots, direct):
            engine.add(expected[112 + p], row)
        actual, complete_report = engine.replay(
            word["events"], word["maps"], initial, selected)
        need(actual == expected, "All 640 columns after the complete native prefix")
        query_initial = [{(i, engine.UNIT): F(1)} for i in range(640)]
        query_expected = [dict(row) for row in query_initial]
        for p, row in zip(pivots, direct):
            engine.add(query_expected[112 + p], row)
        query_actual, query_report = engine.replay(
            word["events"], word["maps"], query_initial, selected)
        need(query_actual == query_expected, "All independent FULL query inputs")
        need(query_actual[:112] == query_initial[:112]
             and query_actual[224:] == query_initial[224:],
             "Every source and arbitrary helper is restored")
        need(query_report["scalar_primitives"] == 8440
             and query_report["monomial_maps"] == 672, "The complete query invoice")
        cutoff = word["stage_ranges"]["restore_current_involution"][0]
        bad, _ = engine.replay(word["events"][:cutoff], word["maps"], query_initial, selected)
        need(bad != query_expected, "Omitting the source restoration fails")
        wrong_pair = deepcopy(pair)
        wrong_pair["old_reader_views"] = wrong_pair["current_code_views"]
        wrong_word = emit_word(engine, wrong_pair, inv, capture, pivots)
        bad, _ = engine.replay(wrong_word["events"], wrong_word["maps"], query_initial, selected)
        need(bad != query_expected, "Replacing the old reader by the current reader fails")
        words[key] = word
        reports[key] = {
            "query": query_report, "after_native_prefix": complete_report,
            "direct_owner_paths": sum(map(len, direct)),
            "negative_controls": ["omitted_restore", "current_reader_substitution"],
        }
    invocations = deepcopy(dispatch["invocations"])
    for call in invocations:
        query_block = call["ordered_blocks"][-1]
        need(query_block["op"] == "fixed_past_reader_query",
             "The query follows the full native sweep and DATA exits")
        query_block.update({
            "source": "queries",
            "literal_source": "queries",
            "literal_key": f"{call['reader_stage']}:{call['service_stage']}",
            "map_calls": 672,
        })
        query_block.pop("pair_record")
        call["query_key"] = query_block["literal_key"]
        call.pop("query_pair_record")
        call["scalar_primitives"] = 14896
        call["map_call_bound"]["late_query"] = 672
        call["map_call_bound"]["total"] = 4384
    payload = {
        "schema": "involution-fixed-reader-service-v1", "source_pins": PINS,
        "pivots": pivots, "response": inv["response"],
        "native_prefixes": prefix["providers"], "queries": words,
        "stage_views": dispatch["stage_views"], "invocations": invocations,
        "physical_contract": {
            "input": "(Fprev*x, Fprev*diag(I_P,q_R)*w)",
            "output": "(Fnew*x, Fnew*diag(I_P,q_R)*(w+D_st*x))",
            "response_rows_P": "L_s*A_t",
            "response_rows_R": "(A_t)_R",
            "arbitrary_selected_baselines": True,
            "physical_input_level": "t-1, independent of reader stage s",
        },
        "helper_hosting": dispatch["owner_contract"],
        "backward_or_complete_caller_claimed": False,
    }
    args.output.mkdir(parents=True, exist_ok=False)
    raw = (json.dumps(payload, separators=(",", ":"), sort_keys=True) + "\n").encode()
    (args.output / "INVOLUTION-READER.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {
        "status": "PASS_ACTUAL_INVOLUTION_FIXED_READER_SERVICE",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(raw).hexdigest(),
        "prefix_reports": prefix_reports, "query_reports": reports,
        "query_scalar_primitives": 8440, "query_maps": 672,
        "complete_word_scalar_primitives": 14896,
        "own_word_monomial_call_bound": 4384,
        "native_mass": 1792, "native_children": 1520,
        "backward_or_complete_caller_claimed": False,
    }
    (args.output / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
