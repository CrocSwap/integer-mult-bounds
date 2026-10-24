"""Check the fixed-reader query at actual completed D25 cuts."""

from collections import defaultdict
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
import argparse
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
ACCESS_PIN = "48baba6e09b787924c496c8d4ce89c9dd3f77585946516f90ff8803d45adb5cd"
UNIT = tuple(1 << j for j in range(25))
IDENTITY = UNIT


def need(value, message):
    if not value:
        raise ValueError(message)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    out = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out


def act(a, value):
    out = 0
    while value:
        bit = value & -value
        out ^= a[bit.bit_length() - 1]
        value ^= bit
    return out


@cache
def compose(a, b):
    return tuple(act(a, value) for value in b)


def transpose(a):
    return tuple(sum(((a[j] >> i) & 1) << j for j in range(25))
                 for i in range(25))


def accumulate(row, key, value):
    row[key] += value
    if not row[key]:
        del row[key]


def compose_rows(left, right):
    out = []
    for row in left:
        acc = defaultdict(F)
        for (j, a), value in row.items():
            for (r, b), other in right[j].items():
                accumulate(acc, (r, compose(a, b)), value * other)
        out.append(dict(acc))
    return out


def price(op, value):
    n, d = abs(value.numerator), value.denominator
    need(n and d & (d - 1) == 0, "Nonzero dyadic coefficient")
    if op == "scale":
        need(n & (n - 1) == 0, "Scale is a dyadic unit")
        return 2 * (abs(n.bit_length() - d.bit_length()) + (value < 0))
    return 2 * (3 + n.bit_length() - 1 + n.bit_count() + d.bit_length() - 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "reuse-normal")
    args = parser.parse_args()
    access_path = HERE / "check_access.py"
    need(sha256(access_path.read_bytes()).hexdigest() == ACCESS_PIN,
         "Frozen formation checker")
    source = module(access_path, "fixed_reader_source")
    capture = json.loads(source.raw_source("capture"))
    native = json.loads(source.raw_source("native"))
    views = json.loads(source.raw_source("views"))
    source.raw_source("phase")
    phase = module(LANES / source.PINS["phase"][0], "fixed_reader_phase")
    pset = set(source.PIVOTS)
    pindex = {p: i for i, p in enumerate(source.PIVOTS)}
    e = source.matrix(capture["response"])
    l = source.matrix(capture["centre_reader"])
    need(all(not (set(e[p]) & pset) for p in pset), "Actual E[P,P] is zero")
    rho = {(v["stage"], v["port"]): tuple(v["route_columns"])
           for v in views["entries"]}
    records = {(v["stage"], v["port"]): v for v in views["entries"]}
    code = capture["scalar_word"]
    inverse = capture["inverse_scalar_word"]
    need(sum(price(g[0], F(g[3])) for g in code) == 1760,
         "Current capture scalar price")
    need(sum(price(g[0], F(g[3])) for g in inverse) == 1760,
         "Current capture inverse scalar price")
    need(all(g[2] not in pset for g in code if g[0] == "add"),
         "Current capture reads only complement")
    for provider in native["providers"].values():
        retained_price = sum(
            price(event[1][0], F(event[1][3]))
            for event in provider["forward"]["events"]
            if event[0] == "scalar" and event[1][1] not in {112 + p for p in pset})
        need(retained_price == 6456, "Retained scalar word invoice")
    carrier_recipes = []
    for p in source.PIVOTS:
        q = records[0, p]["q"]
        chart = phase.chart(q)[:9]
        basis = tuple(chart[1:] + chart[:1]) + UNIT[9:]
        need(compose(transpose(basis), basis) == IDENTITY,
             "Rank-eight carrier basis")
        expected = phase.product([(x, 1) for x in UNIT[:9]] + [(q, -1)])
        head = phase.product([(x, 1) for x in basis[:8]])
        delta = phase.add_phase(expected, phase.negative(head))
        need(delta[0] == delta[2] == 0, "Carrier remainder is a translation")
        need(phase.add_phase(head, phase.line(delta[1], 2)) == expected,
             "Exact F9 q carrier recipe")
        carrier_recipes.append({
            "port": p, "q": q, "rank": 8, "basis_columns": basis,
            "inverse_columns": transpose(basis),
            "output_translation": delta[1],
            "input_frame": "Q_p", "output_frame": "F9",
        })

    def routed(rows, targets, stage):
        return [{
            (r, compose(rho[stage, p], rho[stage, r])): value
            for r, value in row.items()
        } for p, row in zip(targets, rows)]

    def full_view(stage, port, level):
        record = records[stage, port]
        a = rho[stage, port]
        delta = record["literal_stage_alignment"]["exit_X"]
        full = [(x, 1) for x in UNIT[:9 + 8 * level]]
        actual = phase.add_phase(
            phase.product([(act(a, x), n) for x, n in full]),
            phase.line(delta, 2))
        need(actual == phase.product(full), "Literal past/current FULL view")
        return {"port": port, "route_columns": a, "translation": delta}

    all_pairs = []
    for s, t in ((0, 1), (0, 2), (1, 2)):
        ls = routed(l, source.PIVOTS, s)
        lt = routed(l, source.PIVOTS, t)
        et = routed(e, range(112), t)
        direct = compose_rows(ls, et)
        middle = [
            {(r, a): v for (r, a), v in row.items() if r in pset}
            for row in direct
        ]
        need(sum(map(len, direct)) == 3808, "Complete direct query census")
        need(sum(map(len, middle)) == 696, "Selected-source query census")
        lifted_lt = [{} for _ in range(112)]
        for p, row in zip(source.PIVOTS, lt):
            lifted_lt[p] = row
        factored = compose_rows(middle, lifted_lt)
        for i, p in enumerate(source.PIVOTS):
            row = defaultdict(F, factored[i])
            for key, value in ls[i].items():
                if key[0] not in pset:
                    accumulate(row, key, value)
            for key, value in lt[i].items():
                if key[0] not in pset:
                    accumulate(row, key, -value)
            need(dict(row) == direct[i],
                 "Full noncommutative owner-path query identity")
        full = [(x, 1) for x in UNIT[:9 + 8 * t]]
        full_phase = phase.product(full)
        routes = {}
        route_table = []
        query = []
        scalar_bill = 0
        map_count = 0
        for p, row in zip(source.PIVOTS, middle):
            denominator = max(v.denominator for v in row.values())
            if denominator != 1:
                query.append(["scale", p, None, str(denominator), None])
                scalar_bill += price("scale", F(denominator))
            for (r, a), value in sorted(row.items()):
                need(r in pset and a != IDENTITY, "Selected source, actual route")
                need(a[9 + 8 * t:] == UNIT[9 + 8 * t:],
                     "Route fixes every uncompleted axis")
                ai = transpose(a)
                need(compose(ai, a) == compose(a, ai) == IDENTITY,
                     "Composed query route is orthogonal")
                if a not in routes:
                    transformed = phase.product([(act(a, x), n) for x, n in full])
                    difference = phase.add_phase(full_phase, phase.negative(transformed))
                    need(difference[0] == difference[2] == 0,
                         "FULL conjugate is a pure translation and address map")
                    delta = difference[1]
                    reverse = phase.add_phase(
                        full_phase,
                        phase.negative(phase.product([(act(ai, x), n) for x, n in full])))
                    need(reverse == phase.line(act(ai, delta), 2),
                         "Exact inverse source map")
                    routes[a] = len(route_table)
                    route_table.append({
                        "columns": a, "inverse_columns": ai,
                        "FULL_translation": delta,
                        "inverse_FULL_translation": act(ai, delta),
                    })
                integer = denominator * value
                need(integer.denominator == 1, "Normalized query integer")
                query.append(["mapped_add_restore", p, r, str(integer), routes[a]])
                scalar_bill += price("add", integer)
                map_count += 2
            if denominator != 1:
                query.append(["scale", p, None, str(F(1, denominator)), None])
                scalar_bill += price("scale", F(1, denominator))
        need(scalar_bill == 5632 and map_count == 1392, "Middle query invoice")
        old_reader_views = [full_view(s, p, t) for p in range(112)]
        current_code_views = [full_view(t, p, t) for p in range(112)]
        # All view maps preserve row one-norm. Use the triangle inequality
        # at each scalar step to obtain a conservative prefix bound.
        bounds = [F(1) for _ in range(224)]
        grid = [0 for _ in range(224)]
        peak = F(1)
        peak_grid = 0

        def apply_bound(op, target, origin, value):
            nonlocal peak, peak_grid
            if op == "scale":
                bounds[target] *= abs(value)
                grid[target] = max(
                    0, grid[target] + value.denominator.bit_length()
                    - abs(value.numerator).bit_length())
            else:
                bounds[target] += abs(value) * bounds[origin]
                grid[target] = max(grid[target], grid[origin]
                                   + value.denominator.bit_length() - 1)
            peak = max(peak, bounds[target])
            peak_grid = max(peak_grid, grid[target])

        for op, p, r, value in code:
            apply_bound(op, 112 + p, r, F(value))
        for p in source.PIVOTS:
            apply_bound("add", 112 + p, p, F(1))
        for op, p, r, value in code:
            apply_bound(op, p, r, F(value))
        for p in source.PIVOTS:
            apply_bound("add", 112 + p, p, F(-1))
        for op, p, r, value, _ in query:
            apply_bound("add" if op == "mapped_add_restore" else op,
                        112 + p, r, F(value))
        for op, p, r, value in inverse:
            apply_bound(op, p, r, F(value))
        need(peak_grid == 3, "Additional binary grid bound")
        all_pairs.append({
            "reader_stage": s, "service_stage": t,
            "chronology": [
                "Y_P += B_s X_R through old_reader_views",
                "Y_P += X_P",
                "X <- C_t X through current_code_views",
                "Y_P -= X_P",
                "Y_P += (L_s E_t selector_P) X_P through middle_query",
                "X <- C_t^-1 X through current_code_views",
            ],
            "old_reader_views": old_reader_views,
            "old_reader_view_ports": {
                "X": sorted(set(range(112)) - pset), "Y": source.PIVOTS},
            "current_code_views": current_code_views,
            "middle_routes": route_table,
            "middle_query": query,
            "direct_owner_paths_checked": 3808,
            "selected_source_paths": 696,
            "real_scalar_primitives": 11168,
            "monomial_map_calls": 2064,
            "native_children_in_query": 0, "extra_fields": 0,
            "conservative_prefix_one_norm": str(peak),
            "additional_binary_grid_levels_at_most": 3,
            "odd_divisions": 0,
        })
    payload = {
        "schema": "fixed-row-reader-reuse-v1",
        "formation_checker_sha256": ACCESS_PIN, "source_pins": source.PINS,
        "pivots": source.PIVOTS, "carrier_recipes": carrier_recipes,
        "pairs": all_pairs,
        "input_Y": "Selected Q_p L_s y; complement y_R, in the current body.",
        "output_Y": "Selected F9 L_s(y+E_t x); complement F9 q_R(y+E_t x)_R.",
        "restored_source_fields": 112, "unchanged_outside_fields": 416,
        "reuse_native_profile": {"1": 1392, "2": 64, "3": 48, "8": 16},
        "reuse_native_rank": 1792,
        "retained_scalar_primitives": 6456,
        "retained_word_plus_query_scalar_primitives": 17624,
        "complete_local_emitter_bound_here": False,
        "recursive_hosting_bound_here": False,
        "backward_companion_bound_here": False,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode()
    (args.output / "REUSE-PROGRAM.json").write_bytes(raw)
    receipt = {
        "status": "PASS_FIXED_READER_D25_REUSE_QUERY",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "program_sha256": sha256(raw).hexdigest(),
        "source_pins": source.PINS,
        "stage_pairs": [[0, 1], [0, 2], [1, 2]],
        "direct_owner_paths_per_pair": 3808,
        "selected_source_paths_per_pair": 696,
        "query_scalar_primitives": 11168, "query_monomial_maps": 2064,
        "carrier_rank8_phase_recipes": 16,
        "additional_binary_grid_levels_at_most": 3,
        "prefix_one_norm_bounds": [p["conservative_prefix_one_norm"] for p in all_pairs],
        "complete_supplier_claimed": False,
    }
    (args.output / "REUSE-CHECKS.json").write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
