"""Emit the complete inverse-adjoint routed reader service."""

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
LANES = HERE.parent.parent
PINS = {
    "forward": (
        "bridge-access-20261017/involution-reader-20261020/"
        "final-normal/INVOLUTION-READER.json.gz",
        "35f3735f1e2f9693c1b65aa292736d927dc38cbf0670af5e469097803187f091",
    ),
    "forward_freeze": (
        "bridge-access-20261017/involution-reader-20261020/FREEZE.json",
        "3ba792d18fbd57122ab4ae3301a3ff74b81751cf03fd2b7e8f9dc632759364e6",
    ),
    "forward_review": (
        "bridge-review-20261017/involution-reader-review-20261020/FREEZE.json",
        "b4770cbd56bc8b115728529ab218d60ca2bd1a385896ba78cfdf374f04370c97",
    ),
    "native_phase_review": (
        "new-native-recipes-20261017/line-entry-reuse-review-20261020/FREEZE.json",
        "cc5ed3b0ecc6eb5cec48f8baead43ec813042c3e83cd68104b7745366c13c55c",
    ),
    "dispatcher_freeze": (
        "bridge-access-20261017/row-capture-access-20261020/INTEGRATION-FREEZE.json",
        "bbc0e4026b1d003dedc55c78cd6300ef429ee2d95712e55bbab896da2840c331",
    ),
    "engine": (
        "new-core-transfer-20261017/low-displacement-20261020/"
        "fixed-reader-reuse-20261020/emit_routed_query.py",
        "78d505f55b4646fff0d1c40b53ad11327874bee6ebd074013c4288197f3fe900",
    ),
    "views": (
        "bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
        "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473",
    ),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def read(name):
    path, pin = PINS[name]
    raw = (LANES / path).read_bytes()
    if path.endswith(".gz"):
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Pinned source: " + name)
    return raw


def load_engine():
    read("engine")
    spec = importlib.util.spec_from_file_location(
        "complete_reader_dual_engine", LANES / PINS["engine"][0])
    result = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = result
    spec.loader.exec_module(result)
    return result


def scalar_dual(gate):
    op, target, source, raw = gate
    value = F(raw)
    if op == "add":
        return [op, source, target, str(-value)]
    need(op == "scale" and value, "Every scalar gate is invertible")
    return [op, target, None, str(1 / value)]


def dual_prefix(original):
    word = deepcopy(original)
    for old, new in zip(original["events"], word["events"]):
        if old[0] == "scalar":
            new[1] = scalar_dual(old[1])
        else:
            need(old[0] == "native" and new == old, "Native events do not change")
    for key in original:
        if key != "events":
            need(word[key] == original[key], "All native records and adapters stay fixed")
    return word


def dual_query(original):
    word = deepcopy(original)
    for index, event in enumerate(original["events"]):
        if event[0] == "scalar":
            word["events"][index] = ["scalar"] + scalar_dual(event[1:])
        else:
            need(event[0] == "map" and word["events"][index] == event,
                 "Every physical field map stays in the same position")
    need(word["maps"] == original["maps"], "All map phases and inverse records stay fixed")
    return word


def unitary_records(engine, word):
    records = []
    for recipe in word["native_recipes"].values():
        need(1 <= recipe["rank"] <= 9, "A normalized native child has positive rank")
        records.extend(recipe[key] for key in ("left", "right") if recipe[key] is not None)
    for view in word["input_views"]:
        need(view["rank"] == 0 and view["right"] is None, "A monomial input adapter")
        records.append(view["left"])
    for view in word["output_views"]:
        recipe = view["recipe"]
        need(recipe["rank"] == 0 and recipe["right"] is None, "A monomial output adapter")
        records.append(recipe["left"])
    for record in records:
        need(len(record["matrix_rows"]) == 9
             and len(engine.base.n.basis(record["matrix_rows"])) == 9,
             "A physical monomial side map is a bijection")
        need(0 <= record["offset"] < 512 and 0 <= record["phase"] < 4,
             "A physical offset and unit-modulus global phase")
        need(len(record["linear_Z4"]) == len(record["quadratic_rows"]) == 9
             and all(0 <= x < 4 for x in record["linear_Z4"])
             and all(0 <= x < 512 for x in record["quadratic_rows"]),
             "The complete unit-modulus quadratic phase record")
    return len(records)


def replay_prefix(engine, word):
    current = list(word["start"])
    state = engine.base.n.r.identity(640)
    profile = Counter()
    maximum, height, price = F(1), 0, 0
    for event in word["events"]:
        if event[0] == "native":
            _, target, old, new, rank, key = event
            need(current[target] == old, "The physical native input frame")
            a, b = word["frames"][old], word["frames"][new]
            need(len(engine.base.n.basis(a + b)) == len(b), "Nested native frames")
            need(len(b) - len(a) == rank == word["native_recipes"][key]["rank"],
                 "The physical native rank and recipe")
            current[target] = new
            profile[rank] += 1
            continue
        need(event[0] == "scalar", "The complete native event grammar")
        gate, frame = event[1:]
        op, target, source, raw = gate
        value = F(raw)
        need(current[target] == frame, "The dual scalar target frame")
        if op == "add":
            need(source != target and current[source] == frame,
                 "The dual scalar source has the same physical frame")
            engine.base.n.r.add(state[target], state[source], value)
        else:
            need(op == "scale", "Only ADD and SCALE")
            state[target] = {j: value * x for j, x in state[target].items()}
        price += engine.base.n.r.price([gate])
        maximum = max(maximum, sum(abs(x) for x in state[target].values()))
        for x in state[target].values():
            d = x.denominator
            need(d & (d - 1) == 0, "All scalar coefficients are dyadic")
            height = max(height, d.bit_length() - 1)
    need(current == word["final"], "All 640 final physical frames")
    need(state[224:] == engine.base.n.r.identity(640)[224:],
         "All 416 arbitrary helper fields are restored")
    return state, {
        "input_fields": 640, "restored_helper_fields": 416,
        "native_profile": dict(sorted(profile.items())),
        "native_children": sum(profile.values()),
        "native_mass": sum(k * v for k, v in profile.items()),
        "scalar_primitives": price,
        "coefficient_prefix_row_sum": str(maximum),
        "coefficient_binary_height": height,
        "input_adapter_maps": len(word["input_views"]),
        "output_adapter_maps": len(word["output_views"]),
    }


def phase_bindings(engine, bundle, views):
    records = {(v["stage"], v["port"]): v for v in views["entries"]}
    counts = Counter()
    for stage in bundle["stage_views"]:
        t = stage["service_stage"]
        need(stage["physical_input_level"] == t - 1
             and stage["physical_output_level"] == t, "The adjacent physical levels")
        before = [(v, 1) for v in engine.UNIT[:9 + 8 * (t - 1)]]
        after = [(v, 1) for v in engine.UNIT[:9 + 8 * t]]
        exterior = [(v, 1) for v in engine.UNIT[9:9 + 8 * t]]
        for key in ("DATA_entry", "DATA_exit"):
            need(len(stage[key]) == 224 and {v["field"] for v in stage[key]} == set(range(224)),
                 "The DATA maps cover every field exactly once")
            for view in stage[key]:
                p = view["port"]
                side = view["side"]
                need(view["field"] == p + (112 if side == "Y" else 0),
                     "The physical field and bank are unchanged")
                literal = records[t, p]
                rho = literal["route_columns"]
                q = literal["q"]
                align = literal["literal_stage_alignment"]
                need(view["route_columns"] == rho and view["owner_from_body"] == "h=d*rho",
                     "The exact regular-cover owner view")
                need(engine.compose(tuple(rho), engine.transpose(rho)) == engine.UNIT
                     and engine.act(rho, q) == q, "Orthogonal own-line DATA route")
                full = side == "X" or p in bundle["pivots"]
                if key == "DATA_entry":
                    delta = engine.act(rho, align["entry_" + side])
                    need(view["translation_before_route"] == align["entry_" + side]
                         and view["translation_after_route"] == delta, "The literal entry phase")
                    source = before + ([] if full else [(q, -1)])
                    wanted = exterior + ([(q, 1)] if full else [])
                else:
                    exit_key = "exit_X" if full else "exit_Y"
                    delta = align[exit_key]
                    need(view["translation_after_route"] == delta
                         and view["literal_translation_key"] == exit_key, "The literal exit phase")
                    source = after + ([] if full else [(q, -1)])
                    wanted = source
                actual = engine.phase.add_phase(
                    engine.phase.product([(engine.act(rho, v), n) for v, n in source]),
                    engine.phase.line(delta, 2))
                need(actual == engine.phase.product(wanted), "The complete DATA Z4 identity")
                counts[key] += 1
    return dict(counts)


def identity(engine):
    return [{(i, engine.UNIT): F(1)} for i in range(640)]


def adjoint(engine, rows):
    result = [{} for _ in rows]
    for target, row in enumerate(rows):
        for (source, route), value in row.items():
            engine.add(result[source], {(target, engine.transpose(route)): value})
    return result


def lift_prefix(engine, local, stage):
    rho = {v["field"]: tuple(v["route_columns"]) for v in stage["DATA_exit"]}
    result = []
    for target, row in enumerate(local):
        if target >= 224:
            need(row == {target: F(1)}, "The helper endpoint is the actual identity")
            result.append({(target, engine.UNIT): F(1)})
            continue
        need(all(source < 224 for source in row), "No borrowed helper enters a data output")
        result.append({
            (source, engine.compose(engine.transpose(rho[target]), rho[source])): value
            for source, value in row.items()
        })
    return result


def check_query_maps(engine, word):
    t = word["service_stage"]
    full_axes = engine.UNIT[:9 + 8 * t]
    full = engine.phase.product([(v, 1) for v in full_axes])
    for record in word["maps"]:
        route, inverse = tuple(record["columns"]), tuple(record["inverse_columns"])
        need(engine.compose(route, inverse) == engine.compose(inverse, route) == engine.UNIT,
             "The late map and its inverse are exact")
        need(inverse == engine.transpose(route), "The late route is orthogonal")
        need(route[9 + 8 * t:] == engine.UNIT[9 + 8 * t:], "Future axes stay fixed")
        need(record["inverse_translation"] == engine.act(inverse, record["translation"]),
             "The inverse translation is exact")
        actual = engine.phase.add_phase(
            engine.phase.product([(engine.act(route, v), 1) for v in full_axes]),
            engine.phase.line(record["translation"], 2))
        need(actual == full, "The complete late FULL phase identity")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sources = {name: read(name) for name in PINS}
    forward = json.loads(sources["forward"])
    views = json.loads(sources["views"])
    engine = load_engine()
    selected = set(forward["pivots"])
    response = engine.base.n.rows(forward["response"])
    phase_report = phase_bindings(engine, forward, views)
    prefixes, prefix_states, prefix_reports = {}, {}, {}
    expected_local = engine.base.n.r.identity(640)
    for target, row in enumerate(response):
        if target not in selected:
            for source, value in row.items():
                engine.base.n.r.add(expected_local[source], {112 + target: -value})
    for provider, original in forward["native_prefixes"].items():
        word = dual_prefix(original)
        unitary_count = unitary_records(engine, word)
        state, report = replay_prefix(engine, word)
        need(state == expected_local, "All 640 local inverse-adjoint columns")
        need(report["native_mass"] == 1792 and report["native_children"] == 1520
             and report["scalar_primitives"] == 6456, "The complete native dual invoice")
        need(dual_prefix(word) == original, "The gatewise operation is an involution")
        bad = deepcopy(word)
        index = next(i for i, event in enumerate(bad["events"])
                     if event[0] == "scalar" and event[1][0] == "add")
        bad["events"][index][1][3] = str(-F(bad["events"][index][1][3]))
        altered, _ = replay_prefix(engine, bad)
        need(altered != expected_local, "A wrong native-prefix dual sign fails")
        report["unitary_monomial_records_checked"] = unitary_count
        report["negative_control_wrong_native_prefix_sign"] = True
        prefixes[provider], prefix_states[provider], prefix_reports[provider] = word, state, report
    query_words, reports, complete_states = {}, {}, {}
    unit = identity(engine)
    for key, original in forward["queries"].items():
        word = dual_query(original)
        need(dual_query(word) == original, "The late gatewise operation is an involution")
        check_query_maps(engine, word)
        query_forward, _ = engine.replay(original["events"], original["maps"], unit, selected)
        query_expected = adjoint(engine, [
            {term: (2 * value if term == (i, engine.UNIT) else F(0)) - value
             for term, value in row.items()}
            for i, row in enumerate(query_forward)
        ])
        actual_query, query_report = engine.replay(word["events"], word["maps"], unit, selected)
        need(actual_query == query_expected, "All 640 independent late dual columns")
        need(query_report["scalar_primitives"] == 8440 and query_report["monomial_maps"] == 672,
             "The exact late dual invoice")
        t = word["service_stage"]
        stage = forward["stage_views"][t - 1]
        per_provider = {}
        for provider, local in prefix_states.items():
            initial = lift_prefix(engine, local, stage)
            actual, report = engine.replay(word["events"], word["maps"], initial, selected)
            local_forward = engine.base.n.r.identity(640)
            for p in range(112):
                if p not in selected:
                    engine.base.n.r.add(local_forward[112 + p], response[p])
            forward_initial = lift_prefix(engine, local_forward, stage)
            forward_complete, _ = engine.replay(
                original["events"], original["maps"], forward_initial, selected)
            inverse_forward = [dict(row) for row in unit]
            for target in range(112, 224):
                for term, value in forward_complete[target].items():
                    if term != (target, engine.UNIT):
                        engine.add(inverse_forward[target], {term: -value})
            expected = adjoint(engine, inverse_forward)
            need(actual == expected, "All 640 complete routed inverse-adjoint columns")
            complete_states[key, provider] = actual
            need(actual[112:] == unit[112:], "All target records and 416 helper fields are restored")
            forward_star = adjoint(engine, forward_complete)
            need(engine.product(actual, forward_star) == engine.product(forward_star, actual) == unit,
                 "Both complete content inverse-adjoint products")
            need(engine.product(forward_complete, inverse_forward)
                 == engine.product(inverse_forward, forward_complete) == unit,
                 "Both complete forward inverse products")
            per_provider[provider] = report
        bad = deepcopy(word)
        index = next(i for i, e in enumerate(bad["events"])
                     if e[0] == "scalar" and e[1] == "add" and e[3] >= 112)
        bad["events"][index][4] = str(-F(bad["events"][index][4]))
        altered, _ = engine.replay(bad["events"], bad["maps"], unit, selected)
        need(altered != actual_query, "A wrong transferred source sign fails")
        query_words[key] = word
        reports[key] = {"late_query": query_report, "complete_word": per_provider,
                        "all_640_columns": True, "both_inverse_products": True,
                        "negative_control_wrong_transferred_source_sign": True}
    invocations = deepcopy(forward["invocations"])
    expected_order = ["DATA_entry", "native_input_adapters",
                      "complete_native_carrier_cover_sweep", "ordinary_output_adapters",
                      "DATA_exit", "complete_cover_barrier", "fixed_past_reader_query"]
    for call in invocations:
        need([b["op"] for b in call["ordered_blocks"]] == expected_order,
             "The complete physical block order stays fixed")
        need(call["physical_input_level"] == call["service_stage"] - 1,
             "The physical entry level is separate from the old reader label")
        need(call["query_key"] in query_words and call["provider"] in prefixes,
             "Every invocation resolves to complete emitted words")
        call["ordered_blocks"][-1]["op"] = "inverse_adjoint_fixed_past_reader_query"
    payload = {
        "schema": "complete-inverse-adjoint-involution-reader-v1",
        "source_pins": PINS, "pivots": forward["pivots"], "response": forward["response"],
        "native_prefixes": prefixes, "queries": query_words,
        "stage_views": forward["stage_views"], "invocations": invocations,
        "helper_hosting": forward["helper_hosting"],
        "physical_contract": {
            "input": "(Fprev*x, Fprev*diag(I_P,q_R)*w)",
            "output": "(Fnew*(x-D_st^*w), Fnew*diag(I_P,q_R)*w)",
            "D_st_rows_P": "L_s*A_t", "D_st_rows_R": "(A_t)_R",
            "physical_input_level": "t-1, independent of reader stage s",
            "arbitrary_inputs": "All 640 fields; no zero selected baseline.",
        },
        "scope": "Complete typed inverse-adjoint service for three D25 pairs and two providers. "
                 "No complete caller, new helper host, finite map cost, or exponent claim.",
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(raw)
    need(saved["stage_views"] == forward["stage_views"]
         and saved["helper_hosting"] == forward["helper_hosting"],
         "Serialized DATA phase records and helper contract are unchanged")
    for provider, word in saved["native_prefixes"].items():
        state, report = replay_prefix(engine, word)
        need(state == prefix_states[provider]
             and all(value == prefix_reports[provider][key] for key, value in report.items()),
             "The serialized complete native dual passes")
    for key, word in saved["queries"].items():
        stage = saved["stage_views"][word["service_stage"] - 1]
        for provider in prefixes:
            actual, report = engine.replay(word["events"], word["maps"],
                lift_prefix(engine, prefix_states[provider], stage), selected)
            need(actual == complete_states[key, provider]
                 and report == reports[key]["complete_word"][provider],
                 "The serialized complete routed dual passes")
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "COMPLETE-DUAL.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {
        "status": "PASS_COMPLETE_TYPED_INVERSE_ADJOINT_READER",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(raw).hexdigest(),
        "prefix_reports": prefix_reports, "query_reports": reports,
        "DATA_phase_equations": phase_report,
        "all_native_and_endpoint_phase_records_unchanged": True,
        "all_late_map_fields_phases_and_positions_unchanged": True,
        "all_640_columns_and_416_helpers_checked": True,
        "complete_scalar_primitives": 14896, "complete_native_rank": 1792,
        "complete_native_children": 1520, "own_word_map_call_bound": 4384,
        "scope": payload["scope"],
    }
    (args.output / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
