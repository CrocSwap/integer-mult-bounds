"""Check the coupled two-call types with the literal D25 phase maps."""

from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PINS = {
    "views": (
        "bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
        "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473",
    ),
    "row_code": (
        "new-core-transfer-20261017/low-displacement-20261020/row-only-capture-20261020/run-normal/PRODUCTIVE-CAPTURE.json.gz",
        "7c3b8343ec04c65f98b7170c7f37c9f80605e28c95df00bcf2a189908461c8b2",
    ),
    "clean_forward": (
        "new-core-transfer-20261017/low-displacement-20261020/clean-late-exchange-20261020/run-normal/CLEAN-LATE-EXCHANGE.json.gz",
        "b0432322c28ad3a03af8da550a0b7c7df048c7ff5a0664acc7f78efffcffd083",
    ),
    "clean_backward": (
        "new-core-transfer-20261017/low-displacement-20261020/clean-late-exchange-20261020/dual-normal/CLEAN-DUAL.json.gz",
        "6c8869b1c1b45632635805e389899b83fa8348c9fe5b84e3c9c7821bcfd0568c",
    ),
}
UNIT = tuple(1 << i for i in range(25))
ID = (UNIT, ())


def need(ok, label):
    if not ok:
        raise ValueError(label)


def act(matrix, vector):
    out = 0
    while vector:
        low = vector & -vector
        out ^= matrix[low.bit_length() - 1]
        vector ^= low
    return out


def add_line(phase, vector, coefficient):
    bits = [i for i in range(25) if vector >> i & 1]
    for i in bits:
        phase[i, i] = (phase.get((i, i), 0) + coefficient) % 4
    for k, i in enumerate(bits):
        for j in bits[k + 1:]:
            phase[i, j] = (phase.get((i, j), 0) - 2 * coefficient) % 4


def frozen(phase):
    return tuple(sorted((i, j, c % 4) for (i, j), c in phase.items() if c % 4))


def phases(terms):
    phase = {}
    for vector, coefficient in terms:
        add_line(phase, vector, coefficient)
    return UNIT, frozen(phase)


def route(columns):
    return tuple(columns), ()


@lru_cache(maxsize=30000)
def multiply(left, right):
    rho, p = left
    sigma, q = right
    phase = {(i, j): c for i, j, c in p}
    for i, j, c in q:
        if i == j:
            add_line(phase, rho[i], c)
        else:
            need(c == 2, "Even quadratic phase coefficient")
            for a in range(25):
                if rho[i] >> a & 1:
                    for b in range(25):
                        if rho[j] >> b & 1:
                            key = (min(a, b), max(a, b))
                            phase[key] = (phase.get(key, 0) + c) % 4
    return tuple(act(rho, col) for col in sigma), frozen(phase)


def add(*terms):
    out = {}
    for coefficient, row in terms:
        for key, value in row.items():
            out[key] = out.get(key, F(0)) + coefficient * value
    return {key: value for key, value in out.items() if value}


def operated(op, row):
    out = {}
    for (column, old), value in row.items():
        key = (column, multiply(op, old))
        out[key] = out.get(key, F(0)) + value
    return {key: value for key, value in out.items() if value}


def linear(matrix, rows):
    return [add(*((value, rows[j]) for j, value in row.items()))
            for row in matrix]


def zipped(a, b, ca=F(1), cb=F(1)):
    return [add((ca, x), (cb, y)) for x, y in zip(a, b)]


def sparse(matrix):
    return [{int(j): F(c) for j, c in row.items() if F(c)} for row in matrix]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    source = {}
    for name, (relative, expected) in PINS.items():
        path = LANES / relative
        raw = path.read_bytes()
        if path.suffix == ".gz":
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == expected, name + " pin")
        source[name] = json.loads(raw)
    records = {(row["stage"], row["port"]): row for row in source["views"]["entries"]}
    q = [records[0, p]["q"] for p in range(112)]
    rho = [tuple(records[1, p]["route_columns"]) for p in range(112)]
    code = source["row_code"]
    p = code["selected_ports"]
    r = code["ordinary_ports"]
    need(len(p) == 16 and len(r) == 96 and sorted(p + r) == list(range(112)), "Port partition")
    c, e = sparse(code["code"]), sparse(code["response"])
    h = [{j: c[a].get(b, F(0)) for j, b in enumerate(r) if c[a].get(b, F(0))}
         for a in p]
    d = [{j: e[a].get(b, F(0)) for j, b in enumerate(p) if e[a].get(b, F(0))}
         for a in r]
    need(all(d[j].get(i, F(0)) == -h[i].get(j, F(0)) for i in range(16) for j in range(96)),
         "Actual D=-H transpose")
    identity_code = [{a: F(1)} for a in range(112)]
    for i, a in enumerate(p):
        identity_code[a].update({r[j]: value for j, value in h[i].items()})
    need(c == identity_code, "Actual row code fixes all ordinary rows")
    ffresh = phases([(1 << i, 1) for i in range(9, 17)])
    ffresh_inverse = phases([(1 << i, -1) for i in range(9, 17)])
    f9 = phases([(1 << i, 1) for i in range(9)])
    f17 = phases([(1 << i, 1) for i in range(17)])
    entry, exit_view = [], []
    entry_checks = exit_checks = 0
    for a in range(112):
        record = records[1, a]
        alignment = record["literal_stage_alignment"]
        need(alignment["entry_X"] == alignment["entry_Y"] and
             alignment["exit_X"] == alignment["exit_Y"], "Matched X/Y literal views")
        need(tuple(act(rho[a], col) for col in rho[a]) == UNIT and act(rho[a], q[a]) == q[a],
             "Route is an involution and fixes its own line")
        entry.append(multiply(phases([(act(rho[a], alignment["entry_X"]), 2)]), route(rho[a])))
        exit_view.append(multiply(phases([(alignment["exit_X"], 2)]), route(rho[a])))
        need(multiply(entry[-1], f9) ==
             multiply(multiply(ffresh, phases([(q[a], 1)])), route(rho[a])),
             "Literal one-sided entry")
        need(multiply(exit_view[-1], f17) == multiply(f17, route(rho[a])), "Literal FULL exit")
        entry_checks += 1
        exit_checks += 1

    def fields(rows):
        return ([rows[a] for a in p], [rows[a] for a in r],
                [rows[112 + a] for a in p], [rows[112 + a] for a in r])

    def joined(ap, ur, zp, vr):
        rows = [None] * 224
        for ports, values, offset in ((p, ap, 0), (r, ur, 0), (p, zp, 112), (r, vr, 112)):
            for a, value in zip(ports, values):
                rows[offset + a] = value
        return rows

    def local(rows, variant, backward):
        ap, ur, zp, vr = fields(rows)
        if not backward:
            alpha = zipped(ap, linear(h, ur))
            lower = zipped(ur, linear(d, alpha))
            if variant == "clean":
                return joined([add((-1, z)) for z in zp], ur, alpha, zipped(vr, lower))
            return joined(zipped(zp, alpha, cb=-1), lower, alpha, zipped(vr, lower))
        if variant == "clean":
            return joined(zipped(zp, linear(h, vr)), zipped(zipped(ur, linear(d, zp)), vr, cb=-1),
                          [add((-1, a)) for a in ap], vr)
        return joined(zipped(zipped(ap, zp), linear(h, zipped(ur, linear(d, zp)))),
                      zipped(zipped(ur, linear(d, zp)), vr, cb=-1), ap, vr)

    def input_inverse(rows):
        return [operated(phases([(q[a % 112], -1)]), row)
                if a < 112 or a - 112 in p else row for a, row in enumerate(rows)]

    def output_frame(rows):
        return [operated(multiply(f9, phases([(q[a % 112], -1)])), row)
                if a >= 112 and a - 112 in r else operated(f9, row)
                for a, row in enumerate(rows)]

    unit_rows = [{(a, ID): F(1)} for a in range(224)]
    for backward, key, matrix in (
            (False, "clean_forward", source["clean_forward"]["content_map"]),
            (True, "clean_backward", source["clean_backward"]["content_maps"]["selected_swap_conjugate"])):
        expected = [{(j, ID): coefficient for j, coefficient in row.items()} for row in sparse(matrix)]
        need(local(unit_rows, "clean", backward) == expected, key + " exact stored content map")
    initial = input_inverse(unit_rows)
    initial_a, initial_u, initial_z, initial_v = fields(initial)
    initial_alpha = zipped(initial_a, linear(h, initial_u))
    expected_data = [{(a, multiply(f17, phases([(q[a], -1)]))): F(1)} for a in range(112)]

    def replay(variant, omit_entry_translation=False):
        rows = output_frame(local(initial, variant, False))
        rows = [operated(phases([(q[a], 2)]), rows[112 + a]) for a in range(112)] + [
            add((-1, row)) for row in rows[:112]]
        views = [route(g) for g in rho] if omit_entry_translation else entry
        rows = [operated(multiply(ffresh_inverse, views[a % 112]), row)
                for a, row in enumerate(rows)]
        rows = input_inverse(rows)
        rows = output_frame(local(rows, variant, True))
        rows = [operated(multiply(exit_view[a % 112], ffresh), row) for a, row in enumerate(rows)]
        y = rows[112:]
        yp = [operated(phases([(q[a], 2)]), y[a]) for a in p]
        yr = [add((-1, y[a])) for a in r]
        if variant == "clean":
            yp = [add((-1, row)) for row in yp]
        else:
            yr = zipped(yr, linear(d, yp), cb=-1)
        yp = zipped(yp, linear(h, yr), cb=-1)
        decoded = [None] * 112
        for ports, values in ((p, yp), (r, yr)):
            for a, row in zip(ports, values):
                decoded[a] = row
        return rows, decoded

    passes = {}
    for variant in ("original", "clean"):
        rows, decoded = replay(variant)
        need(decoded == expected_data, variant + " decoded physical data on all 224 columns")
        wrong, bad_data = replay(variant, True)
        rejected = sum(a != b for a, b in zip(bad_data, expected_data))
        need(rejected > 0, variant + " omitted-translation control")
        passes[variant] = {
            "arbitrary_input_columns": 224,
            "data_output_rows": 112,
            "omitted_entry_translation_rejected_rows": rejected,
            "full_endpoint_terms": sum(map(len, rows)),
        }
        if variant == "clean":
            gq_u = [operated(multiply(route(rho[a]), phases([(q[a], 1)])), row)
                    for a, row in zip(r, initial_u)]
            h1q_u = [operated(route(rho[a]), row) for a, row in zip(p, linear(h, gq_u))]
            expected_s = zipped(initial_z, h1q_u, cb=-1)
            gz = [operated(route(rho[a]), row) for a, row in zip(p, initial_z)]
            d1z = [operated(route(rho[a]), row) for a, row in zip(r, linear(d, gz))]
            pre_r = zipped(zipped(initial_v, initial_u, cb=2), linear(d, initial_alpha))
            expected_r = zipped([operated(phases([(q[a], 1)]), row) for a, row in zip(r, pre_r)], d1z)
            for ports, values in ((p, expected_s), (r, expected_r)):
                for a, row in zip(ports, values):
                    need(rows[a] == operated(f17, row), "Clean arbitrary source-bank endpoint")
    scalar_price = 0
    for row in h:
        for value in row.values():
            numerator, denominator = abs(value.numerator), value.denominator
            need(denominator & (denominator - 1) == 0, "Dyadic H coefficient")
            scalar_price += 2 * (3 + numerator.bit_length() - 1 + numerator.bit_count() +
                                 denominator.bit_length() - 1)
    receipt = {
        "status": "PASS_ACTUAL_D25_COUPLED_TWO_CALL_TYPES",
        "source_pins": {key: {"path": str(LANES / path), "payload_sha256": digest}
                        for key, (path, digest) in PINS.items()},
        "literal_entry_identities": entry_checks,
        "literal_FULL_exit_identities": exit_checks,
        "variants": passes,
        "clean_data_decoder": {
            "H_nonzero_coefficients": sum(map(len, h)),
            "H_real_scalar_primitives": scalar_price,
            "selected_translation_map_calls": 16,
            "sign_fields": 112,
            "new_native_children": 0,
            "new_fields": 0,
        },
        "physical_decoded_data": "F17 q X0",
        "arbitrary_source_bank_restored": False,
        "local_native_contract_replayed": False,
        "stored_clean_content_maps_bound": True,
        "complete_supplier_claimed": False,
        "scope": "The local coupled F/B types are premises. Literal D25 entry/exit phases and all 224 arbitrary data columns are checked. No final Q cleanup or borrowed restoration is inferred.",
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])
    print(json.dumps(receipt["variants"], sort_keys=True))


if __name__ == "__main__":
    main()
