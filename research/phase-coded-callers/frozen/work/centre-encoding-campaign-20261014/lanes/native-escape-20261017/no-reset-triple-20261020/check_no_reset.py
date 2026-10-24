"""Check the natural three-call word on the actual D25 phase ring."""

from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
LIBRARY = HERE.parent / "coupled-data-split-20261020/check_typed_split.py"
spec = importlib.util.spec_from_file_location("typed_phase_ring", LIBRARY)
lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lib)
need, add, linear, zipped = lib.need, lib.add, lib.linear, lib.zipped
phases, route, sparse = lib.phases, lib.route, lib.sparse


@lru_cache(maxsize=None)
def bits(vector):
    out = []
    while vector:
        low = vector & -vector
        out.append(low.bit_length() - 1)
        vector ^= low
    return tuple(out)


@lru_cache(maxsize=30000)
def mapped_phase(rho, phase):
    out = {}
    for i, j, coefficient in phase:
        if i == j:
            lib.add_line(out, rho[i], coefficient)
        else:
            need(coefficient == 2, "Even quadratic coefficient")
            for a in bits(rho[i]):
                for b in bits(rho[j]):
                    key = (min(a, b), max(a, b))
                    out[key] = (out.get(key, 0) + coefficient) % 4
    return lib.frozen(out)


@lru_cache(maxsize=30000)
def multiply(left, right):
    if left == lib.ID:
        return right
    if right == lib.ID:
        return left
    rho, p = left
    sigma, q = right
    if rho == lib.UNIT:
        phase = {(i, j): c for i, j, c in p}
        for i, j, c in q:
            phase[i, j] = (phase.get((i, j), 0) + c) % 4
        return sigma, lib.frozen(phase)
    if not q:
        return tuple(lib.act(rho, col) for col in sigma), p
    phase = {(i, j): c for i, j, c in p}
    for i, j, coefficient in mapped_phase(rho, q):
        phase[i, j] = (phase.get((i, j), 0) + coefficient) % 4
    return tuple(lib.act(rho, col) for col in sigma), lib.frozen(phase)


def operated(op, row):
    out = {}
    for (column, old), value in row.items():
        key = (column, multiply(op, old))
        out[key] = out.get(key, F(0)) + value
    return {key: value for key, value in out.items() if value}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    sources = {}
    pins = {}
    for name, (relative, expected) in lib.PINS.items():
        path = LANES / relative
        raw = path.read_bytes()
        if path.suffix == ".gz":
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == expected, name + " exact source")
        sources[name] = json.loads(raw)
        pins[name] = {"path": str(path), "sha256": expected}
    pins["phase_library"] = {"path": str(LIBRARY), "sha256": sha256(LIBRARY.read_bytes()).hexdigest()}
    records = {(row["stage"], row["port"]): row for row in sources["views"]["entries"]}
    p = sources["row_code"]["selected_ports"]
    r = sources["row_code"]["ordinary_ports"]
    c, e = sparse(sources["row_code"]["code"]), sparse(sources["row_code"]["response"])
    h = [{j: c[a].get(b, F(0)) for j, b in enumerate(r) if c[a].get(b, F(0))} for a in p]
    d = [{j: e[a].get(b, F(0)) for j, b in enumerate(p) if e[a].get(b, F(0))} for a in r]
    q = [records[0, a]["q"] for a in range(112)]
    g = {(s, a): tuple(records[s, a]["route_columns"]) for s in range(3) for a in range(112)}
    forward = sparse(sources["clean_forward"]["content_map"])
    backward = sparse(sources["clean_backward"]["content_maps"]["selected_swap_conjugate"])
    f9 = phases([(1 << i, 1) for i in range(9)])
    f25 = phases([(1 << i, 1) for i in range(25)])
    unit_rows = [{(i, lib.ID): F(1)} for i in range(224)]
    entry, exit_view, exterior = {}, {}, {}
    route_checks = 0
    for s in (1, 2):
        exterior[s] = phases([(1 << i, 1) for i in range(9, 9 + 8 * s)])
        fprev = phases([(1 << i, 1) for i in range(9 + 8 * (s - 1))])
        fnext = phases([(1 << i, 1) for i in range(9 + 8 * s)])
        for a in range(112):
            alignment = records[s, a]["literal_stage_alignment"]
            need(alignment["entry_X"] == alignment["entry_Y"] and
                 alignment["exit_X"] == alignment["exit_Y"], "Literal paired views")
            entry[s, a] = multiply(phases([(lib.act(g[s, a], alignment["entry_X"]), 2)]), route(g[s, a]))
            exit_view[s, a] = multiply(phases([(alignment["exit_X"], 2)]), route(g[s, a]))
            need(multiply(entry[s, a], fprev) ==
                 multiply(multiply(exterior[s], phases([(q[a], 1)])), route(g[s, a])),
                 "Natural X and selected Y entry")
            need(multiply(multiply(entry[s, a], fprev), phases([(q[a], -1)])) ==
                 multiply(exterior[s], route(g[s, a])), "Natural ordinary Y entry")
            need(multiply(exit_view[s, a], fnext) == multiply(fnext, route(g[s, a])),
                 "Natural FULL exit")
            need(multiply(multiply(exit_view[s, a], fnext), phases([(q[a], -1)])) ==
                 multiply(multiply(fnext, phases([(q[a], -1)])), route(g[s, a])),
                 "Natural hole exit")
            route_checks += 4

    def input_inverse(rows, selected_type):
        return [operated(phases([(q[a % 112], -1)]), row)
                if a < 112 or selected_type == "Q" and a - 112 in p else row
                for a, row in enumerate(rows)]

    def output_frame(rows):
        return [operated(multiply(f9, phases([(q[a % 112], -1)])), row)
                if a >= 112 and a - 112 in r else operated(f9, row)
                for a, row in enumerate(rows)]

    def hs(s, rows):
        before = [operated(route(g[s, a]), row) for a, row in zip(r, rows)]
        return [operated(route(g[s, a]), row) for a, row in zip(p, linear(h, before))]

    def ds(s, rows):
        before = [operated(route(g[s, a]), row) for a, row in zip(p, rows)]
        return [operated(route(g[s, a]), row) for a, row in zip(r, linear(d, before))]

    def full_view(s, a):
        return lib.ID if s == 0 else exit_view[s, a]

    def hs_full(s, rows):
        before = [operated(full_view(s, a), row) for a, row in zip(r, rows)]
        return [operated(full_view(s, a), row) for a, row in zip(p, linear(h, before))]

    def ds_full(s, rows):
        before = [operated(full_view(s, a), row) for a, row in zip(p, rows)]
        return [operated(full_view(s, a), row) for a, row in zip(r, linear(d, before))]

    for s in (1, 2):
        for a in range(112):
            need(multiply(exit_view[s, a], f25) == multiply(f25, route(g[s, a])),
                 "Actual F25 affine view for a terminal shear")
            need(multiply(exit_view[s, a], exit_view[s, a]) == lib.ID, "FULL view involution")
            need(multiply(exit_view[s, a], phases([(q[a], 1)])) ==
                 lib.multiply(exit_view[s, a], phases([(q[a], 1)])),
                 "Independent dense and sparse phase substitutions agree")
    variants = {}
    for selected_type in ("I", "Q"):
        initial = input_inverse(unit_rows, selected_type)
        a0, u0 = [initial[a] for a in p], [initial[a] for a in r]
        z0, v0 = [initial[112 + a] for a in p], [initial[112 + a] for a in r]
        alpha = zipped(a0, hs(0, u0))
        k = zipped(zipped(v0, u0), ds(0, alpha))
        w = zipped(zipped(ds(1, alpha), ds(0, alpha), cb=-1), v0, cb=-1)
        beta = zipped(zipped(alpha, hs(1, k)), hs(2, w))
        final_r = zipped(zipped(u0, ds(1, alpha)), ds(2, beta))
        rows = output_frame(linear(forward, initial))
        print("formed stage 0, initial " + selected_type, flush=True)
        for s, matrix in ((1, backward), (2, forward)):
            exterior_inverse = phases([(1 << i, -1) for i in range(9, 9 + 8 * s)])
            rows = [operated(multiply(exterior_inverse, entry[s, a % 112]), row)
                    for a, row in enumerate(rows)]
            rows = output_frame(linear(matrix, input_inverse(rows, "Q")))
            rows = [operated(multiply(exit_view[s, a % 112], exterior[s]), row)
                    for a, row in enumerate(rows)]
            print("formed stage " + str(s) + ", initial " + selected_type, flush=True)
        expected = [None] * 224
        for ports, values, offset, sign, hole in (
                (p, z0, 0, -1, False), (r, w, 0, 1, False),
                (p, beta, 112, 1, False), (r, final_r, 112, 1, True)):
            for a, row in zip(ports, values):
                op = multiply(f25, phases([(q[a], -1)])) if hole else f25
                expected[offset + a] = operated(op, add((sign, row)))
        need(rows == expected, "Complete actual routed endpoint, initial " + selected_type)
        recovered_k = zipped(zipped(final_r, ds(2, beta), cb=-1), w, cb=-1)
        recovered_alpha = zipped(zipped(beta, hs(1, recovered_k), cb=-1), hs(2, w), cb=-1)
        recovered_u = zipped(zipped(final_r, ds(1, recovered_alpha), cb=-1), ds(2, beta), cb=-1)
        recovered_a = zipped(recovered_alpha, hs(0, recovered_u), cb=-1)
        recovered_v = zipped(zipped(ds(1, recovered_alpha), ds(0, recovered_alpha), cb=-1), w, cb=-1)
        need((recovered_alpha, recovered_u, recovered_a, recovered_v) == (alpha, u0, a0, v0),
             "Exact dyadic content inverse, initial " + selected_type)
        terminal_checked = False
        if selected_type == "I":
            stored_w = [rows[a] for a in r]
            stored_beta = [rows[112 + a] for a in p]
            exposed_r = [operated(phases([(q[a], 1)]), rows[112 + a]) for a in r]
            t = zipped(exposed_r, ds_full(2, stored_beta), cb=-1)
            actual_alpha = zipped(zipped(zipped(stored_beta, hs_full(1, t), cb=-1),
                                        hs_full(1, stored_w)), hs_full(2, stored_w), cb=-1)
            actual_v = zipped(zipped(ds_full(1, actual_alpha), ds_full(0, actual_alpha), cb=-1),
                              stored_w, cb=-1)
            actual_u = zipped(t, ds_full(1, actual_alpha), cb=-1)
            actual_a = zipped(actual_alpha, hs_full(0, actual_u), cb=-1)
            for ports, values in ((p, actual_a), (r, actual_u)):
                for a, row in zip(ports, values):
                    need(operated(phases([(q[a], 1)]), row) == operated(f25, unit_rows[a]),
                         "208-line terminal restores original physical data under F25")
            for a, row in zip(r, actual_v):
                need(row == operated(f25, unit_rows[112 + a]),
                     "208-line terminal restores arbitrary ordinary borrowed input under F25")
            for a in p:
                need(add((-1, rows[a])) == operated(f25, unit_rows[112 + a]),
                     "208-line terminal restores arbitrary selected borrowed input under F25")
            terminal_checked = True
            print("checked 208-line terminal", flush=True)
        variants[selected_type] = {
            "checked_arbitrary_columns": 224,
            "checked_physical_output_rows": 224,
            "complete_endpoint_operator_terms": sum(map(len, rows)),
            "content_inverse": "PASS",
            "208_line_terminal_checked": terminal_checked,
            "initial_selected_original_Y": "z" if selected_type == "I" else "Q_P z",
        }
    shear_price = sum(2 * (3 + abs(c.numerator).bit_length() - 1 +
                             abs(c.numerator).bit_count() + c.denominator.bit_length() - 1)
                      for row in h for c in row.values())
    need(shear_price == 2048, "Direct H and transposed D scalar price")
    need(sum(map(len, h)) == 216, "Actual H coefficient count")
    receipt = {
        "status": "PASS_ACTUAL_D25_NATURAL_CLEAN_TRIPLE",
        "source_pins": pins,
        "literal_route_phase_identities": route_checks,
        "variants": variants,
        "local_profile_initial_I": {"H1": 4176, "H2": 192, "H3": 144, "H8": 32, "H9": 16},
        "local_native_mass_initial_I": 5392,
        "local_scalar_initial_I": 25800,
        "new_owned_fields": 0,
        "remaining_reader": "H_1 r, with physical ordinary Y equal to F25 q_R r",
        "remaining_ordinary_scatter": "Q_R D_1 alpha + Q_R D_2 beta",
        "final_physical_target": "F25 X0 and F25 Y0 under the inherited common-FULL contract, with any stated bank permutation",
        "terminal_operator_word": {
            "positive_line_operations": 208,
            "extra_fields": 0,
            "direct_scalar_upper_bound": 8 * shear_price + 2 * 112,
            "routed_shear_affine_map_calls": 6 * 2 * 112,
            "native_line_side_maps_included": False,
            "final_bank_permutation_included": False,
            "serialized_native_recipes_supplied": False,
        },
        "complete_native_terminal_claimed": False,
        "global_helper_host_replayed": False,
        "scope": "Exact physical composition of the pinned local content contracts and literal D25 views. The terminal, global helper host, recursive invoice and precision proof remain open.",
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])
    print(json.dumps(variants, sort_keys=True))


if __name__ == "__main__":
    main()
