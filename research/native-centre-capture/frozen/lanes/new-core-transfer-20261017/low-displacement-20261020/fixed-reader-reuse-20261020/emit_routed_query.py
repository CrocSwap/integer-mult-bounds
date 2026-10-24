#!/usr/bin/env python3
"""Emit and replay the complete old-reader query after the native prefix."""

import argparse
from collections import defaultdict
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[2]
UNIT = tuple(1 << j for j in range(25))
PINS = {
    "prefix": (HERE / "prefix-normal/CARRIER-PREFIX.json.gz",
               "54c561cfc49ad3fe1258ba5a8760eeadaa11784272cf458e2a6e54403a0e655e"),
    "prefix_checker": (HERE / "emit_prefix.py",
                       "657afc180b397e851fbefa16f56ace98129072a6bd2faf5d84dbc2391720698e"),
    "query": (LANES / "bridge-access-20261017/row-capture-access-20261020/reuse-normal/REUSE-PROGRAM.json",
              "eead344f9a3f642056fd29b05a7e24d1a5d3504eec005eedc83e26b7fed8b82b"),
    "capture": (LANES / "controller-followthrough-20261017/row-capture-20261020/run-normal/ROW-CAPTURE.json",
                "4c98af5d7a1437a03f53e84f0f2cbc7cd2ac47d4c6d4ee1523c16bf469692eb7"),
    "phase": (LANES / "bridge-access-20261017/check_bridge_access.py",
              "9510c5624dfb51d98767728084851e4ee75a135e6d7b546569a47fe458485111"),
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


def module(name):
    read(name)
    spec = importlib.util.spec_from_file_location("routed_query_" + name, PINS[name][0])
    result = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = result
    spec.loader.exec_module(result)
    return result


prefix_checker = module("prefix_checker")
base = prefix_checker.base
phase = module("phase")


def act(columns, value):
    result = 0
    while value:
        bit = value & -value
        result ^= columns[bit.bit_length() - 1]
        value ^= bit
    return result


@cache
def compose(left, right):
    return tuple(act(left, value) for value in right)


def transpose(columns):
    return tuple(sum(((columns[j] >> i) & 1) << j for j in range(25))
                 for i in range(25))


def add(target, source, coefficient=F(1)):
    for key, value in source.items():
        target[key] = target.get(key, F(0)) + coefficient * value
        if not target[key]:
            del target[key]


def product(left, right):
    result = []
    for row in left:
        out = {}
        for (j, a), coefficient in row.items():
            for (k, b), value in right[j].items():
                add(out, {(k, compose(a, b)): coefficient * value})
        result.append(out)
    return result


def routed(rows, ports, views):
    rho = {view["port"]: tuple(view["route_columns"]) for view in views}
    return [{(j, compose(rho[p], rho[j])): value for j, value in row.items()}
            for p, row in zip(ports, rows)]


def initial_prefix(response, selected):
    state = [{(i, UNIT): F(1)} for i in range(640)]
    for p in range(112):
        if p not in selected:
            add(state[112 + p], response[p])
    return state


def replay(events, maps, initial, selected):
    state = [dict(row) for row in initial]
    scalar_cost = 0
    map_cost = 0
    maximum = max(sum(abs(value) for value in row.values()) for row in state)
    height = 0
    for event in events:
        if event[0] == "map":
            _, field, index = event
            need(field < 112 or field - 112 in selected, "A query map uses only FULL fields")
            route = tuple(maps[index]["columns"])
            state[field] = {(i, compose(route, a)): value
                            for (i, a), value in state[field].items()}
            map_cost += 1
        else:
            need(event[0] == "scalar", "The literal query event grammar")
            _, op, target, source, raw = event
            value = F(raw)
            need(target < 112 or target - 112 in selected, "A scalar target is FULL")
            if op == "add":
                need(source < 112 or source - 112 in selected, "A scalar source is FULL")
                need(target != source, "Distinct source and target arrays")
                add(state[target], state[source], value)
            else:
                need(op == "scale", "Only ADD and SCALE instructions")
                state[target] = {key: value * other for key, other in state[target].items()}
            scalar_cost += base.n.r.price([[op, target, source, raw]])
            maximum = max(maximum, sum(abs(other) for other in state[target].values()))
            for other in state[target].values():
                d = other.denominator
                need(d & (d - 1) == 0, "Every query coefficient is dyadic")
                height = max(height, d.bit_length() - 1)
    return state, {"scalar_primitives": scalar_cost, "monomial_maps": map_cost,
                   "exact_prefix_content_one_norm": str(maximum),
                   "additional_binary_height": height}


def make_query(pair, capture, pivots):
    maps, indices, events, stages = [], {}, [], {}
    full = phase.product([(v, 1) for v in UNIT[:9 + 8 * pair["service_stage"]]])

    def register(columns, translation):
        columns = tuple(columns)
        key = columns, translation
        if key in indices:
            return indices[key]
        inverse = transpose(columns)
        need(compose(columns, inverse) == compose(inverse, columns) == UNIT,
             "Each actual query route is orthogonal")
        need(columns[9 + 8 * pair["service_stage"]:] == UNIT[9 + 8 * pair["service_stage"]:],
             "Each query route fixes the uncompleted axes")
        transformed = phase.product([(act(columns, v), 1)
                                     for v in UNIT[:9 + 8 * pair["service_stage"]]])
        need(phase.add_phase(transformed, phase.line(translation, 2)) == full,
             "The complete Z4 phase of each FULL view")
        indices[key] = len(maps)
        maps.append({"columns": columns, "translation": translation,
                     "inverse_columns": inverse, "inverse_translation": act(inverse, translation)})
        return indices[key]

    def view(field, record, inverse=False):
        route = tuple(record["route_columns"])
        delta = record["translation"]
        if inverse:
            route = transpose(route)
            delta = act(route, delta)
        events.append(["map", field, register(route, delta)])

    def begin():
        return len(events)

    def end(name, start):
        stages[name] = [start, len(events)]

    old = {view["port"]: view for view in pair["old_reader_views"]}
    current = {view["port"]: view for view in pair["current_code_views"]}
    ordinary = sorted(set(range(112)) - set(pivots))
    old_fields = [(p, p) for p in ordinary] + [(112 + p, p) for p in pivots]
    start = begin()
    for field, p in old_fields:
        view(field, old[p])
    for op, p, r, coefficient in capture["scalar_word"]:
        events.append(["scalar", op, 112 + p, r, coefficient])
    for field, p in reversed(old_fields):
        view(field, old[p], True)
    end("old_reader_complement", start)
    start = begin()
    for p in pivots:
        events.append(["scalar", "add", 112 + p, p, "1"])
    end("first_selected_copy", start)

    def code_stage(name, word):
        start = begin()
        for p in range(112):
            view(p, current[p])
        for op, p, r, coefficient in word:
            events.append(["scalar", op, p, r, coefficient])
        for p in reversed(range(112)):
            view(p, current[p], True)
        end(name, start)

    code_stage("current_code", capture["scalar_word"])
    start = begin()
    for p in pivots:
        events.append(["scalar", "add", 112 + p, p, "-1"])
    end("second_selected_copy", start)
    start = begin()
    for op, p, r, coefficient, route_index in pair["middle_query"]:
        if op == "scale":
            events.append(["scalar", "scale", 112 + p, None, coefficient])
        else:
            need(op == "mapped_add_restore", "The pinned middle-query grammar")
            record = pair["middle_routes"][route_index]
            forward = register(record["columns"], record["FULL_translation"])
            backward = register(record["inverse_columns"], record["inverse_FULL_translation"])
            need(tuple(maps[forward]["inverse_columns"]) == tuple(maps[backward]["columns"])
                 and maps[forward]["inverse_translation"] == maps[backward]["translation"],
                 "The literal source restoration map")
            events.append(["map", r, forward])
            events.append(["scalar", "add", 112 + p, r, coefficient])
            events.append(["map", r, backward])
    end("middle_query", start)
    code_stage("current_inverse_code", capture["inverse_scalar_word"])
    return events, maps, stages


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    prefix = json.loads(read("prefix"))
    query = json.loads(read("query"))
    capture = json.loads(read("capture"))
    pivots = query["pivots"]
    selected = set(pivots)
    need(pivots == prefix["selected_ports"] == capture["pivots"], "One actual pivot set")
    response = base.n.rows(prefix["response"])
    reader = base.n.rows(capture["centre_reader"])
    prefix_reports = {}
    for provider, word in prefix["providers"].items():
        prefix_reports[provider] = base.verify(
            word, base.n.r.identity(112), response, [{} for _ in range(112)], selected)
    reports, words = {}, {}
    for pair in query["pairs"]:
        key = str(pair["reader_stage"]) + ":" + str(pair["service_stage"])
        et = routed(response, range(112), pair["current_code_views"])
        ls = routed(reader, pivots, pair["old_reader_views"])
        direct = product(ls, et)
        need(sum(map(len, direct)) == 3808, "Every direct old-reader owner path")
        initial = initial_prefix(et, selected)
        expected = [dict(row) for row in initial]
        for p, row in zip(pivots, direct):
            add(expected[112 + p], row)
        events, maps, stages = make_query(pair, capture, pivots)
        actual, report = replay(events, maps, initial, selected)
        need(actual == expected, "All640 complete arbitrary fields with exact ordered owner paths")
        need(actual[:112] == initial[:112] and actual[224:] == initial[224:],
             "Every source and arbitrary helper is restored")
        need(report["scalar_primitives"] == 11168 and report["monomial_maps"] == 2064,
             "The complete literal routed-query invoice")
        query_initial = [{(i, UNIT): F(1)} for i in range(640)]
        query_expected = [dict(row) for row in query_initial]
        for p, row in zip(pivots, direct):
            add(query_expected[112 + p], row)
        query_actual, query_bound = replay(events, maps, query_initial, selected)
        need(query_actual == query_expected, "The query is valid on every independent FULL input")
        negative_index = next(i for i in range(*stages["middle_query"]) if events[i][0] == "map")
        bad = events[:negative_index] + events[negative_index + 1:]
        bad_state, _ = replay(bad, maps, initial, selected)
        need(bad_state != expected, "An omitted middle source view is rejected")
        bad = events[:stages["current_inverse_code"][0]]
        bad_state, _ = replay(bad, maps, initial, selected)
        need(bad_state != expected, "An omitted source-code restoration is rejected")
        words[key] = {"reader_stage": pair["reader_stage"], "service_stage": pair["service_stage"],
                      "events": events, "maps": maps, "stage_ranges": stages}
        reports[key] = {**report, "exact_query_entry_unit_bound": query_bound,
                        "complete_local_scalar": 6456 + report["scalar_primitives"],
                        "native_mass": 1792, "native_profile": {"1": 1392, "2": 64, "3": 48, "8": 16},
                        "restored_source_fields": 112, "unchanged_arbitrary_helpers": 416,
                        "direct_owner_path_terms": 3808, "distinct_checked_full_maps": len(maps)}
    payload = {
        "schema": "fixed-reader-literal-global-query-v1",
        "source_pins": {key: {"path": str(path), "sha256": pin}
                        for key, (path, pin) in PINS.items()},
        "pivots": pivots, "native_prefixes": prefix["providers"], "queries": words,
        "physical_contract": {
            "query_entrance": "All X and selected Y fields are in the actual completed global FULL frame.",
            "query": "X is restored; selected Y gains L_s E_t X; ordinary Y and all helpers are unchanged.",
            "complete_content": "The selected record z gains L_s E_t x after the checked native carrier prefix. If z=L_s y, it is L_s(y+E_t x).",
            "scope": "The complete D25 entry/exit dispatcher that puts the local prefix into these global charts is a separate pinned binding.",
        },
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(raw)
    for key, word in saved["queries"].items():
        pair = next(p for p in query["pairs"] if
                    key == str(p["reader_stage"]) + ":" + str(p["service_stage"]))
        et = routed(response, range(112), pair["current_code_views"])
        actual, report = replay(word["events"], word["maps"], initial_prefix(et, selected), selected)
        need(report["scalar_primitives"] == reports[key]["scalar_primitives"]
             and report["monomial_maps"] == reports[key]["monomial_maps"],
             "The serialized query invoice")
        expected = initial_prefix(et, selected)
        for p, row in zip(pivots, product(routed(reader, pivots, pair["old_reader_views"]), et)):
            add(expected[112 + p], row)
        need(actual == expected, "The serialized complete operator map")
    (args.out / "ROUTED-QUERY.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {"status": "PASS_EXACT_LITERAL_ROUTED_QUERY_AND_NATIVE_PREFIX",
               "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "payload_decompressed_sha256": sha256(raw).hexdigest(),
               "prefix_reports": prefix_reports, "query_reports": reports,
               "scope": "Exact local prefix and global FULL query. The actual D25 dispatcher is a separate binding; recursive hosting and the supplier remain open."}
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
