"""Check the routed involution reader with independent matrix algebra."""

import argparse
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
OLD_REVIEW = HERE.parent / "fixed-reader-service-review-20261020"
PRODUCER = LANES / "bridge-access-20261017/involution-reader-20261020"
CONTROLLER = LANES / "controller-followthrough-20261017/row-involution-20261020"
FREEZE_PIN = "3ba792d18fbd57122ab4ae3301a3ff74b81751cf03fd2b7e8f9dc632759364e6"
PAYLOAD_PIN = "35f3735f1e2f9693c1b65aa292736d927dc38cbf0670af5e469097803187f091"
OLD_REVIEW_PIN = "ba06daabfd69759b489f5ae97a75ff68243bd5016a0981508ff529759ac8edd7"
A_PIN = "a25551b3b99b82477fde561a742fabe1114acbfe6c67cd14284747aaac3dd95b"


def need(test, message):
    if not test:
        raise ValueError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def pinned(path, expected, compressed=False):
    raw = path.read_bytes()
    if compressed:
        raw = gzip.decompress(raw)
    need(digest(raw) == expected, "Pin: " + str(path))
    return raw


def freeze(path, expected):
    result = json.loads(pinned(path, expected))
    for name, pin in result["files"].items():
        pinned(path.parent / name, pin)
    return result


freeze(OLD_REVIEW / "FREEZE.json", OLD_REVIEW_PIN)
spec = importlib.util.spec_from_file_location("independent_service_math", OLD_REVIEW / "check_service.py")
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
r = s.r


def complete_matrix(u, v):
    vp = [{j: row[p] for j, p in enumerate(r.PIVOTS) if p in row} for row in v]
    vpi, determinant = r.invert(vp)
    remaining_u = [{} if p in r.PSET else dict(row) for p, row in enumerate(u)]
    residual = r.matmul(v, remaining_u)
    requested = []
    for i, row in enumerate(residual):
        out = {j: -value for j, value in row.items()}
        r.put(out, i, F(-2))
        requested.append(out)
    changed_rows = r.matmul(vpi, requested)
    changed_u = [dict(row) for row in u]
    for p, row in zip(r.PIVOTS, changed_rows):
        changed_u[p] = row
    need(r.matmul(v, changed_u) == [{i: F(-2)} for i in range(16)],
         "Exact rank-sixteen involution certificate")
    a = r.eye(112)
    for row, correction in zip(a, r.matmul(changed_u, v)):
        for j, value in correction.items():
            r.put(row, j, value)
    return a, changed_u, r.matmul(vpi, v), determinant


def to_operations(word, level):
    for record in word["maps"]:
        a, ai = tuple(record["columns"]), tuple(record["inverse_columns"])
        need(r.product(a, ai) == r.product(ai, a) == r.UNIT and ai == r.transpose(a),
             "The literal map is orthogonal")
        need(a[9 + 8 * level:] == r.UNIT[9 + 8 * level:], "Every future axis is fixed")
        delta = r.phase_translation(r.add_phase(r.full_phase(level), r.minus_phase(r.full_phase(level, a))))
        need(record["translation"] == delta
             and record["inverse_translation"] == r.apply(ai, delta), "Literal FULL phase and inverse")
    operations = []
    for event in word["events"]:
        if event[0] == "map":
            _, field, index = event
            operations.append(("map", field, None, tuple(word["maps"][index]["columns"])))
        else:
            need(event[0] == "scalar", "Literal query event grammar")
            _, op, field, source, coefficient = event
            need(op in ("add", "scale"), "Dyadic scalar grammar")
            need(source is None or source < 112, "No target record is used as a source")
            operations.append((op, field, source, F(coefficient)))
        need(field < 112 or field - 112 in r.PSET, "Only FULL query fields are changed")
    return operations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "normal")
    args = parser.parse_args()
    producer_freeze = freeze(PRODUCER / "FREEZE.json", FREEZE_PIN)
    need(producer_freeze["payload_decompressed_sha256"] == PAYLOAD_PIN, "Payload freeze")
    bundle = json.loads(pinned(PRODUCER / "final-normal/INVOLUTION-READER.json.gz", PAYLOAD_PIN, True))
    sources = {}
    for name, (path, pin) in bundle["source_pins"].items():
        raw = pinned(LANES / path, pin, path.endswith(".gz"))
        if path.endswith(".json") or path.endswith(".json.gz"):
            sources[name] = json.loads(raw)
    inv = json.loads(pinned(CONTROLLER / "run-normal/ROW-INVOLUTION.json", A_PIN))
    need(inv == sources["involution"], "Exact controller word source")
    native_path, native_pin = r.PINS["native"]
    native = json.loads(pinned(LANES / native_path, native_pin, True))
    u, v, old_e = (r.sparse(native["model"][key])
                   for key in ("correction_U", "correction_V", "response"))
    a, changed_u, reader, vp_det = complete_matrix(u, v)
    need(a == r.sparse(inv["response"]) == r.sparse(bundle["response"]),
         "The emitted response equals the independently completed actual matrix")
    need(changed_u == r.sparse(inv["correction_U"]), "The changed factor agrees")
    need(r.matmul(a, a) == r.eye(112), "The complete 112-port involution")
    need(all(a[p] == old_e[p] for p in range(112) if p not in r.PSET),
         "Exactly the old ordinary rows are retained")
    need(all(a[p] != old_e[p] for p in r.PIVOTS), "All sixteen selected rows change")
    need(reader == r.sparse(sources["capture"]["centre_reader"]), "The retained old reader")
    need(r.matmul(reader, a) == [{j: -x for j, x in row.items()} for row in reader],
         "The current reader has eigenvalue minus one")
    codeword = inv["common_frame_words"]["A"]
    need(r.scalar_word(r.eye(112), codeword) == a, "Independent complete scalar A word")
    need(sum(r.real_price(op, F(value)) for op, _, _, value in codeword) == 3276,
         "Exact source unit price")
    need(all(dst < 112 and (src is None or src < 112) for _, dst, src, _ in codeword),
         "The source word uses existing X only")
    old_payload = json.loads(s.read(*s.PAYLOADS["service"], True))
    need(bundle["native_prefixes"] == old_payload["native_prefixes"]
         and bundle["stage_views"] == old_payload["stage_views"]
         and bundle["helper_hosting"] == old_payload["owner_contract"],
         "The exact reviewed native and DATA components are retained")
    need(tuple(bundle["pivots"]) == r.PIVOTS, "The exact selected field order")
    prefix_reports = {name: s.prefix_replay(word, a)
                      for name, word in bundle["native_prefixes"].items()}
    ports = native["model"]["ports"]
    routes = {(stage, p): r.route(ports[p], stage) for stage in range(3) for p in range(112)}
    query_reports = {}
    dual_reports = {}
    query_parts = {
        "apply_current_involution": (3276, 224),
        "old_reader_complement": (1760, 224),
        "selected_reader_copy": (128, 0),
        "restore_current_involution": (3276, 224),
    }
    for key, word in bundle["queries"].items():
        old_stage, level = word["reader_stage"], word["service_stage"]
        need(key == f"{old_stage}:{level}", "Reader and service labels")
        operations = to_operations(word, level)
        at = r.routed_matrix(a, range(112), level, routes)
        identity = [{(p, r.UNIT): F(1)} for p in range(112)]
        need(r.multiply_routed(at, at) == identity, "The actual routed source involution")
        ls = r.routed_matrix(reader, r.PIVOTS, old_stage, routes)
        lt = r.routed_matrix(reader, r.PIVOTS, level, routes)
        direct = r.multiply_routed(ls, at)
        need(sum(map(len, direct)) == 3824, "Direct selected owner-path census")
        end = 0
        part_reports = {}
        for label, (expected_scalar, expected_maps) in query_parts.items():
            lo, hi = word["stage_ranges"][label]
            need(lo == end and lo <= hi <= len(operations), "Complete ordered query intervals")
            part = operations[lo:hi]
            price = sum(r.real_price(op, value) for op, _, _, value in part if op != "map")
            maps = sum(op == "map" for op, _, _, _ in part)
            need((price, maps) == (expected_scalar, expected_maps), "Per-part exact invoice")
            if label in ("apply_current_involution", "restore_current_involution"):
                scalars = [[op, dst, src, str(value)] for op, dst, src, value in part if op != "map"]
                need(scalars == codeword, "Both current words are the pinned A program")
                expected_maps_list = (
                    [("map", p, None, routes[level, p]) for p in range(112)]
                    + [("map", p, None, routes[level, p]) for p in reversed(range(112))])
                need([op for op in part if op[0] == "map"] == expected_maps_list,
                     "The current A uses the exact DATA route views")
            part_reports[label] = {"scalar_primitives": price, "maps": maps}
            end = hi
        need(end == len(operations), "No query event lies outside its complete schedule")
        initial = [{(i, r.UNIT): F(1)} for i in range(640)]
        expected = [dict(row) for row in initial]
        for p, row in zip(r.PIVOTS, direct):
            for term, value in row.items():
                r.put(expected[112 + p], term, value)
        actual, bill, triangle, grid, exact = r.replay(operations)
        need(actual == expected, "All 640 arbitrary query input columns")
        need(bill == {"real_scalar": 8440, "maps": 672}
             and exact["coefficient_row_sum_peak"] == "202"
             and exact["coefficient_binary_height"] == 2, "Query invoice and exact prefixes")
        global_prefix = [dict(row) for row in initial]
        for p in range(112):
            if p not in r.PSET:
                for term, value in at[p].items():
                    r.put(global_prefix[112 + p], term, value)
        complete = r.multiply_routed(actual, global_prefix)
        complete_expected = [dict(row) for row in global_prefix]
        for p, row in zip(r.PIVOTS, direct):
            for term, value in row.items():
                r.put(complete_expected[112 + p], term, value)
        need(complete == complete_expected, "All 640 complete service input columns")
        cutoff = word["stage_ranges"]["restore_current_involution"][0]
        wrong, *_ = r.replay(operations[:cutoff])
        need(wrong != expected and wrong[:112] != initial[:112], "No-restore control fails")
        need(r.multiply_routed(lt, at) != direct, "The current reader cannot replace the old reader")
        dual, dual_bill, dual_triangle, dual_grid, dual_exact = r.replay(operations, dual=True)
        dual_expected = [dict(row) for row in initial]
        for p, row in zip(r.PIVOTS, direct):
            for (origin, path), value in row.items():
                r.put(dual_expected[origin], (112 + p, r.transpose(path)), -value)
        need(dual == dual_expected and dual_bill == bill,
             "The literal inverse-adjoint late query on all 640 columns")
        need(dual_exact["coefficient_row_sum_peak"] == "30"
             and dual_exact["coefficient_binary_height"] == 2, "Exact late dual prefix bounds")
        query_reports[key] = {
            "input_columns": 640, "direct_paths": 3824, "parts": part_reports,
            "invoice": bill, "exact_prefix": exact, "triangle_prefix": str(triangle),
            "triangle_binary_height": grid,
            "negative_controls": ["omitted_source_restore", "current_reader_substitution"],
        }
        dual_reports[key] = {"input_columns": 640, "invoice": dual_bill, "exact_prefix": dual_exact,
                             "triangle_prefix": str(dual_triangle), "triangle_binary_height": dual_grid}
    service_reports = []
    for call in bundle["invocations"]:
        provider, old_stage, level = call["provider"], call["reader_stage"], call["service_stage"]
        old_call = next(c for c in old_payload["services"] if
                        (c["provider"], c["reader_stage"], c["service_stage"]) ==
                        (provider, old_stage, level))
        need(call["ordered_blocks"][:-1] == old_call["ordered_blocks"][:-1],
             "The complete native cover barrier is unchanged")
        key = f"{old_stage}:{level}"
        late = call["ordered_blocks"][-1]
        need(late["op"] == "fixed_past_reader_query"
             and late["source"] == late["literal_source"] == "queries"
             and late["literal_key"] == call["query_key"] == key
             and late["map_calls"] == 672, "The exact new query splice")
        need(call["physical_input_level"] == level - 1 and call["physical_output_level"] == level
             and call["stage_view_record"] == level - 1, "The adjacent physical stage")
        prefix_report = prefix_reports[provider]
        scalar = prefix_report["scalar_primitives"] + query_reports[key]["invoice"]["real_scalar"]
        need(scalar == call["scalar_primitives"] == 14896
             and call["map_call_bound"] == {
                 "DATA": 448, "local_endpoint_adapters": 224, "native_side_maps": 3040,
                 "late_query": 672, "total": 4384}, "The complete new response service invoice")
        service_reports.append({"provider": provider, "reader_stage": old_stage, "service_stage": level,
                                "scalar_primitives": scalar, "native_mass": prefix_report["native_mass"],
                                "monomial_map_call_bound": 4384, "input_columns": 640})
    need(len(service_reports) == 6 and len(query_reports) == 3, "All six actual services")
    result = {
        "status": "PASS_INDEPENDENT_ROUTED_INVOLUTION_READER",
        "checker_sha256": digest(Path(__file__).read_bytes()),
        "producer_freeze_sha256": FREEZE_PIN, "payload_decompressed_sha256": PAYLOAD_PIN,
        "inherited_service_review_sha256": OLD_REVIEW_PIN, "actual_A_payload_sha256": A_PIN,
        "pivot_minor_determinant": str(vp_det), "rank_certificate": "V U_tilde = -2 I16",
        "actual_source_scalar_price": 3276, "changed_selected_rows": 16, "unchanged_ordinary_rows": 96,
        "prefix_reports": prefix_reports, "queries": query_reports, "late_dual_queries": dual_reports,
        "services": service_reports, "producer_code_imported": False,
        "new_native_phase_checks": "The exact reviewed components are unchanged.",
        "full_backward_service_emitted": False, "complete_supplier_claimed": False,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
    (args.output / "REVIEW-CHECKS.json").write_bytes(raw)
    print(result["status"])
    print(digest(raw))


if __name__ == "__main__":
    main()
