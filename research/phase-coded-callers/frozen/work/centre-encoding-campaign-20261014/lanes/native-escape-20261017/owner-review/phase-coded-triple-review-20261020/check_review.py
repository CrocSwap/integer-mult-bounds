"""Check the phase-coded triple from separate content and frame proofs."""

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import shutil


HERE = Path(__file__).resolve().parent
LANE = HERE.parents[1]
LANES = LANE.parent
PRODUCER = LANE / "phase-coded-triple-20261020"
CONTROLLER = LANES / "controller-followthrough-20261017/phase-coded-clean-20261020"
ENGINE = HERE.parent / "no-reset-triple-review-20261020/check_review.py"
ENGINE_PIN = "daef106365651360926f41e82cfa5bac291433ea87ba154c1d75e6fe4ce04186"
PINS = {
    "views": (LANES / "bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
              "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473"),
    "row_code": (LANES / "new-core-transfer-20261017/low-displacement-20261020/"
                 "row-only-capture-20261020/run-normal/PRODUCTIVE-CAPTURE.json.gz",
                 "7c3b8343ec04c65f98b7170c7f37c9f80605e28c95df00bcf2a189908461c8b2"),
    "local": (CONTROLLER / "final-normal/PHASE-CODED.json.gz",
              "ffdbe1c84af50e58ee0ab3a9ada15571476146caad1119f55e17d655934f0874"),
    "local_freeze": (CONTROLLER / "FREEZE.json",
                     "284e6239ae3287bb139497fe610e67def239ad50697f230b61ac7c7280fb4b75"),
    "local_checks": (CONTROLLER / "final-normal/CHECKS.json",
                     "6d81db224b91bcc053abf7614f03b2e9dcc27e58a18e714ff6dd038508d52456"),
    "producer_freeze": (PRODUCER / "FREEZE.json",
                        "0ee32fe22f42cffce2a9673f0dc95496a4b4bb8b11a534f77a11f5fe9c7aeb4b"),
    "producer_checks": (PRODUCER / "run-normal/CHECKS.json",
                        "44a1c03836ba47af92965dc7d2bb716d0f94d03dd54cb3122eeaa9f1d08a3cc3"),
    "producer_proof": (PRODUCER / "PHYSICAL-ENDPOINT.md",
                       "5eb5eba5d3bed38faf9e411ca4a9a6f8e67765966011e93dec96f2300613756f"),
    "producer_checker": (PRODUCER / "check_phase_coded_triple.py",
                         "82a36b9f258d1aa2d95830502b336eb8aae9e7beff643b1f854c3d87451098f6"),
    "natural_freeze": (LANE / "no-reset-triple-20261020/FREEZE.json",
                       "089425bdf431d81456e1c988a1fd21a837baca43e510bc92dee98dc2ee571791"),
    "independent_engine": (ENGINE, ENGINE_PIN),
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def digest(raw):
    return sha256(raw).hexdigest()


need(digest(ENGINE.read_bytes()) == ENGINE_PIN, "Pinned independent phase engine")
spec = importlib.util.spec_from_file_location("independent_natural_review", ENGINE)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
plus, linear, sparse = engine.plus, engine.linear, engine.sparse
normal, route, line, fourier = engine.normal, engine.route, engine.line, engine.fourier


def write_json(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(raw)
    return digest(raw)


def local_rows(local, p, r, h, d):
    basis = engine.eye(224)
    a, u = [basis[x] for x in p], [basis[x] for x in r]
    z, v = [basis[112 + x] for x in p], [basis[112 + x] for x in r]

    def join(ap, ur, zp, vr):
        result = [None] * 224
        for ports, rows, offset in ((p, ap, 0), (r, ur, 0), (p, zp, 112), (r, vr, 112)):
            for port, row in zip(ports, rows):
                result[offset + port] = row
        return result

    alpha = [plus((1, x), (1, y)) for x, y in zip(a, linear(h, u))]
    zero_f = join([plus((-1, row)) for row in z], u, alpha, v)
    zero_b = join(z, [plus((1, x), (1, y)) for x, y in zip(u, linear(d, z))],
                  [plus((-1, row)) for row in a], v)
    need(zero_f == sparse(local["zero_response_content"]), "Every zero-forward data column")
    need(zero_b == sparse(local["zero_response_dual_content"]), "Every zero-backward data column")
    inverse = join([plus((1, x), (-1, y)) for x, y in zip(z, linear(h, u))],
                   u, [plus((-1, row)) for row in a], v)
    need(linear(zero_f, inverse) == basis and linear(inverse, zero_f) == basis,
         "Zero-forward inverse in both orders")
    adjoint = engine.transpose(inverse, 224)
    perm = list(range(224))
    for port in p:
        perm[port], perm[112 + port] = 112 + port, port
    swapped = [{perm[j]: c for j, c in adjoint[perm[i]].items()} for i in range(224)]
    need(swapped == zero_b, "Selected-wire conjugate of the actual inverse adjoint")
    operator_basis = [{(j, 0): F(1)} for j in range(224)]
    fprefix, bprefix = list(operator_basis), list(operator_basis)
    for port in r:
        fprefix[112 + port] = plus((1, fprefix[112 + port]), (1, {(port, 1): F(1)}))
        bprefix[port] = plus((1, bprefix[port]), (-1, {(112 + port, 3): F(1)}))
    forward, backward = linear(zero_f, fprefix), linear(zero_b, bprefix)

    def decoded(rows):
        result = []
        for row in rows:
            terms = {}
            for j, power, coefficient in row:
                need(0 <= j < 224 and power in (-1, 0, 1), "Source-indexed local line power")
                terms = plus((1, terms), (F(coefficient), {(j, power % 4): F(1)}))
            result.append(terms)
        return result

    need(decoded(local["phase_coded_forward"]) == forward, "All stored F_Q data columns")
    need(decoded(local["phase_coded_backward"]) == backward, "All stored B_Q data columns")
    return {"local_columns": 224, "zero_forward_inverse_orders": 2,
            "zero_backward_inverse_adjoint": True,
            "forward_source_line_terms": sum(power != 0 for row in forward for _, power in row),
            "backward_source_line_terms": sum(power != 0 for row in backward for _, power in row)}


def block_proof():
    a, u, z, v = [{(j, ()): F(1)} for j in range(4)]

    def reduced(word):
        result = []
        for name in word:
            if name[0] == "Q" and result and result[-1][0] == "Q":
                power = (result.pop()[1] + name[1]) % 4
                if power:
                    result.append(("Q", power))
            else:
                result.append(name)
        return tuple(result)

    def op(name, row):
        result = {}
        for (source, word), coefficient in row.items():
            key = source, reduced((name,) + word)
            result = plus((1, result), (coefficient, {key: F(1)}))
        return result

    def read(name, row):
        return op((name, 0), row)

    def q(power, row):
        return op(("Q", power % 4), row)

    def forward(s, state):
        ap, ur, zp, vr = state
        return [plus((-1, zp)), ur, plus((1, ap), (1, read("H" + str(s), ur))),
                plus((1, vr), (1, q(1, ur)))]

    def backward(state):
        ap, ur, zp, vr = state
        return [zp, plus((1, ur), (1, read("D1", zp)), (-1, q(-1, vr))),
                plus((-1, ap)), vr]

    first = forward(0, [a, u, z, v])
    second = backward(first)
    alpha = plus((1, a), (1, read("H0", u)))
    residual = plus((1, read("D1", alpha)), (-1, q(-1, v)))
    need(first == [plus((-1, z)), u, alpha, plus((1, v), (1, q(1, u)))], "First block stage")
    need(second == [alpha, residual, z, first[3]], "Second block stage")
    endpoint = forward(2, second)
    physical = list(endpoint)
    physical[3] = q(-1, physical[3])
    need(physical == [plus((-1, z)), residual, plus((1, alpha), (1, read("H2", residual))),
                      plus((1, u), (1, read("D1", alpha)))], "Unmodified endpoint under common F25")
    middle = list(second)
    middle[1] = plus((1, middle[1]), (-1, read("D1", middle[0])))
    need(middle[1] == plus((-1, q(-1, v))), "Middle FULL correction")
    final = forward(2, middle)
    final[3] = q(-1, final[3])
    before_final_shears = list(final)
    need(final == [plus((-1, z)), plus((-1, q(-1, v))),
                   plus((1, alpha), (-1, read("H2", q(-1, v)))), u],
         "Last q cancels Q without crossing D1 or H2")
    final[2] = plus((1, final[2]), (-1, read("H2", final[1])))
    final[2] = plus((1, final[2]), (-1, read("H0", final[3])))
    need(final == [plus((-1, z)), plus((-1, q(-1, v))), a, u], "Three-shear endpoint")
    wrong = list(second)
    wrong[1] = plus((1, wrong[1]), (1, read("D1", wrong[0])))
    need(forward(2, wrong) != forward(2, middle), "Wrong middle sign fails")
    need(read("H2", q(1, u)) != q(1, read("H2", u)), "Q is not commuted through a reader")

    def encoded(rows):
        return [[{"source_group": source, "word": [list(x) for x in word], "coefficient": str(c)}
                 for (source, word), c in sorted(row.items())] for row in rows]

    return {"input_groups": ["a", "u", "z", "v"], "first": encoded(first), "second": encoded(second),
            "unmodified_physical_under_F25": encoded(physical), "middle": encoded(middle),
            "before_final_shears_under_F25": encoded(before_final_shears),
            "shortened_under_F25": encoded(final),
            "relations": "Only adjacent powers of the same ordinary Q are reduced modulo 4.",
            "wrong_middle_sign_rejected": True, "Q_reader_commutation_not_used": True}


def frame_proof(source, p, r):
    records = {(row["stage"], row["port"]): row for row in source["entries"]}
    need(len(source["entries"]) == 336 and
         set(records) == {(s, a) for s in range(3) for a in range(112)}, "Complete actual D25 view set")
    q = [records[0, a]["q"] for a in range(112)]
    need(all(0 < vector < 512 for vector in q), "All local lines lie in the root nine axes")
    views, certificates, counts = {}, [], Counter()
    for s in range(3):
        for a in range(112):
            row = records[s, a]
            rho = tuple(row["route_columns"])
            need(row["q"] == q[a] and engine.act(rho, q[a]) == q[a], "Own line is fixed")
            need(engine.compose(rho, rho) == engine.UNIT and
                 all(engine.transposed(rho, rho[j]) == 1 << j for j in range(25)),
                 "Actual route is an orthogonal involution")
            if s == 0:
                need(rho == engine.UNIT, "Stage-zero identity")
                continue
            alignment = row["literal_stage_alignment"]
            need(alignment["entry_X"] == alignment["entry_Y"] and
                 alignment["exit_X"] == alignment["exit_Y"], "Paired literal bank views")
            delta = engine.act(rho, alignment["entry_X"])
            entry = line(delta, 2) + route(rho)
            out = line(alignment["exit_X"], 2) + route(rho)
            prev, nex = fourier(0, 9 + 8 * (s - 1)), fourier(0, 9 + 8 * s)
            ext, full = fourier(9, 9 + 8 * s), fourier(0, 25)
            pairs = [
                (entry + prev, ext + line(q[a], 1) + route(rho)),
                (entry + prev + line(q[a], -1), ext + route(rho)),
                (out + nex, nex + route(rho)),
                (out + nex + line(q[a], -1), nex + line(q[a], -1) + route(rho)),
                (out + full, full + route(rho)),
                (out + out, []),
            ]
            for left, right in pairs:
                need(normal(left) == normal(right), "Literal D25 phase identity")
                counts["phase_identities"] += 1
            need(normal(out + line(q[a], 1)) == normal(line(q[a], 1) + out),
                 "FULL view commutes with its own line")
            counts["own_Q_view_commutation"] += 1
            counts["missing_entry_translation_rejected"] += normal(route(rho) + prev) != normal(pairs[0][1])
            if a in r:
                counts["wrong_ordinary_entry_FULL_rejected"] += normal(entry + prev) != normal(ext + route(rho))
            views[s, a] = rho, alignment["exit_X"]
            certificates.append({"stage": s, "port": a, "route_columns": list(rho),
                                 "entry_translation_after_route": delta,
                                 "FULL_translation_after_route": alignment["exit_X"],
                                 "input_character_normal_FULL_exit": normal(out + nex)})
    full = fourier(0, 25)
    terminal = {}
    for variant in ("I", "Q"):
        signed_rows = []
        line_fields = list(range(112, 224)) + r + (p if variant == "Q" else [])
        for field in range(224):
            port = field % 112
            hole = field >= 112 or port in r or variant == "Q"
            row = full + (line(q[port], -1) if hole else [])
            corrected = (line(q[port], 1) if field in line_fields else []) + row
            need(normal(corrected) == normal(full), "Every terminal physical phase")
            if hole:
                need(normal(row) != normal(full), "Remaining q is not a free identity")
            signed_rows.append({"output": field, "input": (field + 112) % 224,
                                "sign": -1 if field < 112 else 1, "has_q": hole})
        need(len(line_fields) == (208 if variant == "I" else 224), "Terminal positive-line count")
        terminal[variant] = {"positive_line_fields": line_fields, "shortened_physical_rows": signed_rows}
    return q, views, certificates, dict(counts), terminal


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    need(shutil.disk_usage(HERE).free >= 3 * 1024**3, "At least 3 GiB free")
    args.out.mkdir(parents=True, exist_ok=False)
    source, manifest = {}, {}
    for name, (path, pin) in PINS.items():
        raw = path.read_bytes()
        payload = gzip.decompress(raw) if path.suffix == ".gz" else raw
        need(digest(payload) == pin, "Pinned " + name)
        manifest[name] = {"path": str(path), "sha256": digest(raw), "payload_sha256": pin}
        if path.suffix in (".json", ".gz"):
            source[name] = json.loads(payload)
    for key, directory in (("local_freeze", CONTROLLER), ("producer_freeze", PRODUCER)):
        for relative, pin in source[key]["files"].items():
            path = directory / relative
            need(digest(path.read_bytes()) == pin, "Every frozen file " + relative)
            manifest[key + ":" + relative] = {"path": str(path), "sha256": pin}
    code, local = source["row_code"], source["local"]
    p, r = code["selected_ports"], code["ordinary_ports"]
    need(p == [0, 27, 36, 111, 20, 7, 57, 46, 1, 3, 6, 8, 17, 18, 24, 23] and
         r == sorted(set(range(112)) - set(p)), "Actual ordered partition")
    need(p == local["selected_ports"] and r == local["ordinary_ports"] and local["code"] == code["code"],
         "Native row-code source equality")
    c, e = sparse(code["code"]), sparse(code["response"])
    h = [{j: c[a][b] for j, b in enumerate(r) if b in c[a]} for a in p]
    d = [{j: e[a][b] for j, b in enumerate(p) if b in e[a]} for a in r]
    expected = engine.eye(112)
    for i, a in enumerate(p):
        expected[a].update({r[j]: value for j, value in h[i].items()})
    need(c == expected and d == [{i: -value for i, value in row.items()}
                                 for row in engine.transpose(h, 96)], "Actual H and D=-H transpose")
    local_result = local_rows(local, p, r, h, d)
    invoices = {}
    for provider, variants in local["providers"].items():
        for variant, item in variants.items():
            bill = engine.local_invoice(item["body"])
            prefix = ([["add", a, 112 + a, "-1"] for a in r] if variant == "backward_Q" else
                      [["add", 112 + a, a, "1"] for a in r])
            need(item["physical_prefix"] == prefix, "All physical entry ADDs")
            need(item["prefix_location"] == "Before every inherited input adapter.", "Physical prefix position")
            expected_profile = {1: 1392, 2: 64, 3: 48, 9 if variant == "forward_I" else 8: 16}
            need(bill["profile"] == expected_profile and bill["native_children"] == 1520 and
                 bill["real_scalar_primitives"] == 3864, "Literal local invoice")
            bill["physical_prefix_scalar_units"] = sum(engine.add_price(F(gate[3])) for gate in prefix)
            bill["complete_scalar_units"] = bill["real_scalar_primitives"] + bill["physical_prefix_scalar_units"]
            need(bill["complete_scalar_units"] == 4632, "Complete scalar invoice")
            bill["explicit_input_views"] = len(item["body"]["input_views"])
            bill["explicit_output_views"] = len(item["body"]["output_views"])
            need(bill["explicit_input_views"] == (112 if variant == "forward_I" else 128) and
                 bill["explicit_output_views"] == 96, "Literal endpoint adapter count")
            report = source["local_checks"]["reports"][provider][variant]
            need(bill["native_mass"] == report["native_mass"] and
                 bill["complete_scalar_units"] == report["complete_scalar_primitives"] and
                 bill["explicit_input_views"] == report["explicit_input_monomial_views"] and
                 bill["explicit_output_views"] == report["explicit_output_monomial_views"],
                 "Local receipt agrees")
            need(report["unchanged_arbitrary_helpers"] == 416 and report["all_independent_input_fields"] == 640,
                 "Inherited native replay contract")
            if variant != "backward_Q":
                need(len(item["removed_transfers"]) == 592, "Deleted transfer count")
            invoices[provider + ":" + variant] = bill
    q, views, certificate, phase_counts, terminal = frame_proof(source["views"], p, r)
    need(q == code["ports"], "Actual phase labels and row-code ports agree")
    blocks = block_proof()
    specs = [
        ("middle_D1_after_complete_stage1_sweep", d, p, r, 1, 17),
        ("final_H2", h, r, [112 + a for a in p], 2, 25),
        ("final_H0", h, [112 + a for a in r], [112 + a for a in p], 0, 25),
    ]
    shears, shear_counts = [], Counter()
    for name, matrix, sources, targets, stage, full_dimension in specs:
        events, bill = engine.terminal_shear(matrix, sources, targets, stage, F(-1), views)
        need(bill["ADD"] == 216 and bill["scalar_units"] == 2048, "Exact direct coefficient cost")
        shear_counts.update(bill)
        shears.append({"name": name, "input_and_output_frame": "F" + str(full_dimension),
                       "source_fields": sources, "target_fields": targets, "events": events,
                       "checked_arbitrary_columns": 224, "invoice": bill})
    need(shear_counts == {"ADD": 648, "MAP": 448, "scalar_units": 6144}, "Three-shear total")
    producer = source["producer_checks"]
    need(producer["status"] == "PASS_ACTUAL_D25_PHASE_CODED_TRIPLE" and
         producer["phase_identities"] == phase_counts["phase_identities"] == 1344,
         "Completed physical producer receipt")
    variants = {}
    for kind in ("I", "Q"):
        keys = ["forward_" + kind, "backward_Q", "forward_Q"]
        selected = [invoices["base:" + key] for key in keys]
        profile = Counter()
        for bill in selected:
            profile.update(bill["profile"])
        mass = sum(rank * count for rank, count in profile.items())
        positive_lines = len(terminal[kind]["positive_line_fields"])
        profile[1] += positive_lines
        need(mass + positive_lines == sum(rank * count for rank, count in profile.items()) == 5600,
             "Complete direct-terminal native mass")
        need(producer["variants"][kind]["native_mass_before_terminal"] == mass and
             producer["variants"][kind]["direct_terminal_positive_lines"] == positive_lines and
             producer["variants"][kind]["native_mass_with_direct_terminal"] == 5600,
             "Producer native invoice agrees")
        variants[kind] = {"native_mass_before_terminal": mass, "positive_terminal_lines": positive_lines,
                          "complete_native_mass": 5600, "complete_native_profile": dict(sorted(profile.items())),
                          "local_scalar_units": sum(bill["complete_scalar_units"] for bill in selected),
                          "local_explicit_endpoint_views": sum(bill["explicit_input_views"] +
                                                               bill["explicit_output_views"] for bill in selected),
                          "added_shear_affine_maps": shear_counts["MAP"],
                          "scalar_units_with_three_shears": 20040,
                          "extra_scalar_units_for_unsigned_X": 224}
        need(variants[kind]["local_scalar_units"] + shear_counts["scalar_units"] == 20040,
             "Scalar subtotal before terminal wrappers")
    need(all(digest(Path(item["path"]).read_bytes()) == item["sha256"] for item in manifest.values()),
         "Every source remains unchanged")
    outputs = {
        "SOURCE-MANIFEST.json": manifest,
        "FRAME-CERTIFICATE.json": certificate,
        "BLOCK-PROOF.json": blocks,
        "FULL-SHEARS.json": shears,
        "TERMINAL-PHASES.json": terminal,
    }
    pins = {name: write_json(args.out / name, value) for name, value in outputs.items()}
    receipt = {"status": "PASS_INDEPENDENT_PHASE_CODED_TRIPLE_REVIEW", "output_sha256": pins,
               "phase_checks": phase_counts, "local_rows": local_result,
               "literal_local_invoices": invoices, "three_FULL_shears": dict(shear_counts),
               "variants": variants, "native_640_column_replay_repeated": False,
               "producer_sparse_global_replay_repeated": False,
               "middle_boundary": "After the full stage-1 sweep and all local helper returns.",
               "remaining_obligations": ["global owner hosting", "map stream and address cost",
                                          "terminal line hosting and wrappers", "recursive common-q matching",
                                          "complete numerical precision proof"],
               "new_owned_fields": 0, "odd_divisions": 0, "kappa_claim": False}
    write_json(args.out / "CHECKS.json", receipt)
    print(receipt["status"])
    print(json.dumps({"phases": phase_counts, "shears": dict(shear_counts), "variants": variants}, sort_keys=True))


if __name__ == "__main__":
    main()
