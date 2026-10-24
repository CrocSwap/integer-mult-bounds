"""Check the phase-coded triple with the literal D25 views."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
RING_PATH = HERE.parent / "no-reset-triple-20261020/check_no_reset.py"
RING_PIN = "8612732e02b68495d6b0b95cbd216d1d0df43be2ffdd29cc7fc9033518ab1c48"
BASE_RING_PIN = "70ca9ce2dff5256644f35ef65344c7e0dd9f78e3fb48c18436e9e5c20b4f9109"
PINS = {
    "views": (
        "bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
        "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473",
    ),
    "row_code": (
        "new-core-transfer-20261017/low-displacement-20261020/"
        "row-only-capture-20261020/run-normal/PRODUCTIVE-CAPTURE.json.gz",
        "7c3b8343ec04c65f98b7170c7f37c9f80605e28c95df00bcf2a189908461c8b2",
    ),
    "phase_coded": (
        "controller-followthrough-20261017/phase-coded-clean-20261020/"
        "final-normal/PHASE-CODED.json.gz",
        "ffdbe1c84af50e58ee0ab3a9ada15571476146caad1119f55e17d655934f0874",
    ),
    "phase_coded_freeze": (
        "controller-followthrough-20261017/phase-coded-clean-20261020/FREEZE.json",
        "284e6239ae3287bb139497fe610e67def239ad50697f230b61ac7c7280fb4b75",
    ),
}


def need(test, message):
    if not test:
        raise ValueError(message)


need(sha256(RING_PATH.read_bytes()).hexdigest() == RING_PIN, "Exact phase library")
spec = importlib.util.spec_from_file_location("natural_phase_ring", RING_PATH)
ring = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ring)
need(sha256(ring.LIBRARY.read_bytes()).hexdigest() == BASE_RING_PIN,
     "Exact base phase library")
lib = ring.lib
add, linear, zipped = lib.add, lib.linear, lib.zipped
operated, multiply = ring.operated, ring.multiply
phases, route = lib.phases, lib.route


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    source, pins = {}, {}
    for name, (relative, pin) in PINS.items():
        path = LANES / relative
        raw = path.read_bytes()
        if path.suffix == ".gz":
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == pin, "Exact source " + name)
        source[name] = json.loads(raw)
        pins[name] = {"path": str(path), "sha256": pin}
    pins["phase_library"] = {"path": str(RING_PATH), "sha256": RING_PIN}
    pins["base_phase_library"] = {
        "path": str(ring.LIBRARY), "sha256": BASE_RING_PIN,
    }
    records = {(row["stage"], row["port"]): row
               for row in source["views"]["entries"]}
    code = source["row_code"]
    p, r = code["selected_ports"], code["ordinary_ports"]
    need(p == source["phase_coded"]["selected_ports"] and
         r == source["phase_coded"]["ordinary_ports"], "Actual port partition")
    c, e = lib.sparse(code["code"]), lib.sparse(code["response"])
    h = [{j: c[a][b] for j, b in enumerate(r) if b in c[a]} for a in p]
    d = [{j: e[a][b] for j, b in enumerate(p) if b in e[a]} for a in r]
    need(all(d[j].get(i, F(0)) == -h[i].get(j, F(0))
             for i in range(16) for j in range(96)), "D is minus H transpose")
    q = [records[0, a]["q"] for a in range(112)]
    g = {(s, a): tuple(records[s, a]["route_columns"])
         for s in range(3) for a in range(112)}
    forward = source["phase_coded"]["phase_coded_forward"]
    backward = source["phase_coded"]["phase_coded_backward"]
    f9 = phases([(1 << i, 1) for i in range(9)])
    f25 = phases([(1 << i, 1) for i in range(25)])
    units = [{(i, lib.ID): F(1)} for i in range(224)]
    entry, exit_view, exterior = {}, {}, {}
    phase_checks = 0
    for s in (1, 2):
        exterior[s] = phases([(1 << i, 1) for i in range(9, 9 + 8 * s)])
        fprev = phases([(1 << i, 1) for i in range(9 + 8 * (s - 1))])
        fnext = phases([(1 << i, 1) for i in range(9 + 8 * s)])
        for a in range(112):
            alignment = records[s, a]["literal_stage_alignment"]
            need(alignment["entry_X"] == alignment["entry_Y"] and
                 alignment["exit_X"] == alignment["exit_Y"], "Paired views")
            need(lib.act(g[s, a], q[a]) == q[a], "The route fixes its own line")
            entry[s, a] = multiply(
                phases([(lib.act(g[s, a], alignment["entry_X"]), 2)]),
                route(g[s, a]))
            exit_view[s, a] = multiply(
                phases([(alignment["exit_X"], 2)]), route(g[s, a]))
            need(multiply(entry[s, a], fprev) ==
                 multiply(multiply(exterior[s], phases([(q[a], 1)])),
                          route(g[s, a])), "Natural FULL entry")
            need(multiply(multiply(entry[s, a], fprev),
                          phases([(q[a], -1)])) ==
                 multiply(exterior[s], route(g[s, a])), "Natural hole entry")
            need(multiply(exit_view[s, a], fnext) ==
                 multiply(fnext, route(g[s, a])), "Natural FULL exit")
            need(multiply(multiply(exit_view[s, a], fnext),
                          phases([(q[a], -1)])) ==
                 multiply(multiply(fnext, phases([(q[a], -1)])),
                          route(g[s, a])), "Natural hole exit")
            need(multiply(exit_view[s, a], f25) ==
                 multiply(f25, route(g[s, a])), "Final FULL shear view")
            need(multiply(exit_view[s, a], exit_view[s, a]) == lib.ID,
                 "The FULL view is an involution")
            phase_checks += 6

    def input_inverse(rows, selected_type):
        return [operated(phases([(q[i % 112], -1)]), row)
                if i < 112 or selected_type == "Q" and i - 112 in p else row
                for i, row in enumerate(rows)]

    def output_frame(rows):
        return [operated(multiply(f9, phases([(q[i % 112], -1)])), row)
                if i >= 112 and i - 112 in r else operated(f9, row)
                for i, row in enumerate(rows)]

    def local(matrix, rows):
        return [add(*((F(value),
                       operated(phases([(q[j % 112], power)]), rows[j]))
                      for j, power, value in row))
                for row in matrix]

    def hs(s, rows, physical=False):
        view = (lambda a: exit_view[s, a]) if physical and s else (
            lambda a: route(g[s, a]))
        before = [operated(view(a), row) for a, row in zip(r, rows)]
        return [operated(view(a), row) for a, row in zip(p, linear(h, before))]

    def ds(s, rows, physical=False):
        view = (lambda a: exit_view[s, a]) if physical and s else (
            lambda a: route(g[s, a]))
        before = [operated(view(a), row) for a, row in zip(p, rows)]
        return [operated(view(a), row) for a, row in zip(r, linear(d, before))]

    def call(rows, stage, matrix):
        ext_inverse = phases([(1 << i, -1) for i in range(9, 9 + 8 * stage)])
        entered = [operated(multiply(ext_inverse, entry[stage, i % 112]), row)
                   for i, row in enumerate(rows)]
        result = output_frame(local(matrix, input_inverse(entered, "Q")))
        return [operated(multiply(exit_view[stage, i % 112], exterior[stage]), row)
                for i, row in enumerate(result)]

    def field_line(ports, rows, power):
        return [operated(phases([(q[a], power)]), row)
                for a, row in zip(ports, rows)]

    def joined(ap, ur, zp, vr):
        rows = [None] * 224
        for ports, values, offset in ((p, ap, 0), (r, ur, 0),
                                     (p, zp, 112), (r, vr, 112)):
            for a, row in zip(ports, values):
                rows[offset + a] = row
        return rows

    variants = {}
    for selected_type in ("I", "Q"):
        initial = input_inverse(units, selected_type)
        a0, u0 = [initial[a] for a in p], [initial[a] for a in r]
        z0, v0 = [initial[112 + a] for a in p], [initial[112 + a] for a in r]
        alpha = zipped(a0, hs(0, u0))
        residual = zipped(ds(1, alpha), field_line(r, v0, -1), cb=-1)
        beta = zipped(alpha, hs(2, residual))
        final_u = zipped(u0, ds(1, alpha))
        stage0 = output_frame(local(forward, initial))
        stage1 = call(stage0, 1, backward)
        ordinary = call(stage1, 2, forward)
        expected = joined([add((-1, row)) for row in z0], residual, beta, final_u)
        expected = [operated(f25, row) for row in expected]
        need(ordinary == expected, "The actual unmodified F_Q triple endpoint")

        middle = list(stage1)
        correction = ds(1, [middle[a] for a in p], physical=True)
        for a, row in zip(r, correction):
            middle[a] = add((1, middle[a]), (-1, row))
        shortened = call(middle, 2, forward)
        for a, row in zip(p, hs(2, [shortened[a] for a in r], physical=True)):
            shortened[112 + a] = add((1, shortened[112 + a]), (-1, row))
        for a, row in zip(p, hs(0, [shortened[112 + a] for a in r], physical=True)):
            shortened[112 + a] = add((1, shortened[112 + a]), (-1, row))
        expected_short = joined(
            [add((-1, row)) for row in z0],
            [add((-1, row)) for row in field_line(r, v0, -1)], a0, u0)
        expected_short = [operated(f25, row) for row in expected_short]
        need(shortened == expected_short, "Three legal FULL shears give the short endpoint")
        need(all(shortened[a] == operated(
            multiply(f25, phases([(q[a], -1)])),
            add((-1, units[112 + a]))) for a in r), "Ordinary borrowed q type")
        need(all(shortened[112 + a] == operated(
            multiply(f25, phases([(q[a], -1)])), units[a]) for a in range(112)),
            "The data output is F25 q X0")
        if selected_type == "Q":
            need(all(shortened[a] == operated(
                multiply(f25, phases([(q[a], -1)])),
                add((-1, units[112 + a]))) for a in p), "Common q on both banks")
        else:
            need(all(shortened[a] == operated(f25, add((-1, units[112 + a])))
                     for a in p), "I entry restores selected borrowed fields")

        terminal = list(shortened)
        for a in range(112):
            terminal[112 + a] = operated(phases([(q[a], 1)]), terminal[112 + a])
        for a in r + (p if selected_type == "Q" else []):
            terminal[a] = operated(phases([(q[a], 1)]), terminal[a])
        want = [operated(f25, add((-1, units[112 + a]))) for a in range(112)]
        want += [operated(f25, units[a]) for a in range(112)]
        need(terminal == want, "The direct terminal gives the signed physical exchange")
        need(shortened != want, "Omission of the remaining q correction fails")
        wrong = list(stage1)
        for a, row in zip(r, correction):
            wrong[a] = add((1, wrong[a]), (1, row))
        need(call(wrong, 2, forward) != call(middle, 2, forward),
             "The wrong middle correction fails")
        variants[selected_type] = {
            "all_arbitrary_input_columns": 224,
            "all_physical_output_rows": 224,
            "unmodified_endpoint_terms": sum(map(len, ordinary)),
            "shortened_endpoint_terms": sum(map(len, shortened)),
            "shortened_endpoint": (
                "X=-F25 q Y0; Y=F25 q X0" if selected_type == "Q" else
                "X_P=-F25 Y0_P; X_R=-F25 q_R Y0_R; Y=F25 q X0"),
            "new_native_children_for_three_shears": 0,
            "direct_terminal_positive_lines": 224 if selected_type == "Q" else 208,
            "native_mass_before_terminal": 5376 if selected_type == "Q" else 5392,
            "native_mass_with_direct_terminal": 5600,
        }
        print("checked actual D25 phase-coded triple, initial " + selected_type, flush=True)

    scalar_price = sum(
        2 * (3 + abs(value.numerator).bit_length() - 1 +
             abs(value.numerator).bit_count() + value.denominator.bit_length() - 1)
        for row in h for value in row.values())
    need(sum(map(len, h)) == 216 and scalar_price == 2048, "Direct scalar tariff")
    receipt = {
        "status": "PASS_ACTUAL_D25_PHASE_CODED_TRIPLE",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_pins": pins,
        "phase_identities": phase_checks,
        "variants": variants,
        "three_direct_FULL_shears": {
            "scalar_primitives": 3 * scalar_price,
            "affine_map_calls": 448,
            "owned_fields": 0,
            "native_children": 0,
        },
        "scope": (
            "The actual D25 physical endpoint is verified on arbitrary data. "
            "The native local helper contracts are inherited. The direct "
            "remaining line terminal is checked as an operator, not as a "
            "hosted recursive word. Common q is not a free terminal."
        ),
    }
    (args.out / "CHECKS.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": receipt["status"], "phase_identities": phase_checks,
        "variants": variants,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
