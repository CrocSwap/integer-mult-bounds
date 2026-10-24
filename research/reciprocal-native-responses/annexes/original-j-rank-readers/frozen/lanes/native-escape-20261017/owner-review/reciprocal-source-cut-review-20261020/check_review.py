"""Check the reciprocal reader types from the fixed source data."""

import argparse
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANE = HERE.parents[1]
LANES = LANE.parent
ENGINE = HERE.parent / "no-reset-triple-review-20261020/check_review.py"
ENGINE_PIN = "daef106365651360926f41e82cfa5bac291433ea87ba154c1d75e6fe4ce04186"
ARITHMETIC = LANES / "new-core-transfer-20261017/low-displacement-20261020/check_response.py"
ARITHMETIC_PIN = "c6d92104e4345816e86163f6c1dea24fbd9b6e9b133ffd2e0c646dca17ca00a8"
PINS = {
    "model": (LANES / "oblique-native-20261017/signed-metric-reciprocal-20261020/"
              "model-normal-v2/RESPONSE.json.gz",
              "df2d2028c99028db3c645b3311d7f31ff96efe72f6f9257f99157ce030ff43d0"),
    "native": (LANES / "oblique-native-20261017/signed-metric-reciprocal-20261020/"
               "native-normal/NATIVE.json.gz",
               "f528752be6222da2b64522f9a124622acab4413e79d403d58b592d2533307d1e"),
    "views": (LANES / "bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
              "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473"),
}


def need(test, name):
    if not test:
        raise ValueError(name)


def digest(data):
    return sha256(data).hexdigest()


need(digest(ENGINE.read_bytes()) == ENGINE_PIN, "Fixed independent phase engine")
spec = importlib.util.spec_from_file_location("independent_phase", ENGINE)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
eye, plus, product, sparse = engine.eye, engine.plus, engine.linear, engine.sparse
route, line, fourier = engine.route, engine.line, engine.fourier


@lru_cache(maxsize=None)
def normalized(word):
    return engine.normal(word)


def same(left, right):
    return normalized(tuple(left)) == normalized(tuple(right))


def write_json(path, value):
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(data)
    return digest(data)


def model_check(model, native):
    need(native["model"] == model, "The native payload uses the exact model")
    blocks = model["blocks"]
    need(Counter(len(b["ports"]) for b in blocks) == {6: 8, 8: 8}, "Actual block sizes")
    need(sorted(p for b in blocks for p in b["ports"]) == list(range(112)), "Complete block partition")
    h, hi = sparse(model["pair_code"]), sparse(model["pair_code_inverse"])
    need(product(h, hi) == product(hi, h) == eye(112), "Actual pair code in both orders")
    u, ell, p_mode = [{} for _ in range(112)], [], eye(112)
    for k, block in enumerate(blocks):
        ports = block["ports"]
        m = len(ports) - 4
        u_values, ell_values = [1] * (len(ports) - 2) + [m, 0], [-1] * (len(ports) - 2) + [1, 0]
        need(list(map(F, block["u"])) == u_values and list(map(F, block["ell"])) == ell_values,
             "The serialized block uses the declared rank-one factors")
        ell.append({a: F(c) for a, c in zip(ports, ell_values) if c})
        for a, c in zip(ports, u_values):
            if c:
                u[a][k] = F(c)
        b, c = ports[-2:]
        need((b, c) == (block["b"], block["c"]), "Actual swap roles")
        p_mode[b], p_mode[c] = {c: F(1)}, {b: F(1)}
    r_mode = [plus((1, a), (1, b)) for a, b in zip(eye(112), product(u, ell))]
    modes = {"P": p_mode, "R": r_mode, "E": product(p_mode, r_mode),
             "inverse_E": product(r_mode, p_mode)}
    physical = {}
    for name, matrix in modes.items():
        need(matrix == sparse(model["mode"][name]), "Reconstructed mode matrix " + name)
        physical[name] = product(hi, product(matrix, h))
        need(physical[name] == sparse(model["physical"][name]), "Physical pair conjugation " + name)
    p, r, e, ei = [physical[name] for name in ("P", "R", "E", "inverse_E")]
    L, U = product(ell, h), product(hi, u)
    need(L == sparse(model["reflection_L"]) and U == sparse(model["reflection_U"]),
         "Exact physical reader and column factors")
    need(product(L, U) == [{j: F(-2)} for j in range(16)], "Centre reflection identity")
    need(product(p, p) == product(r, r) == product(e, ei) == product(ei, e) == eye(112),
         "Physical inverse identities")
    need(product(ei, p) == r, "Backward pre-P gives R without a commutation")
    need(any(len(row) != 1 for row in p), "Physical P is not monomial")
    need(sum(map(len, p)) == 160, "Exact support of physical P")
    need(all(p[a] == {a: F(1)} for a in model["centre_ports"]), "P fixes every chosen anchor row")
    for word_name in ("forward_E", "backward_inverse_E"):
        for provider in native["providers"].values():
            word = provider[word_name]
            need(len(word["start"]) == len(word["final"]) == 640, "Complete native role table")
            need(all(word["frames"][word["start"][a + 112]] == [] for a in range(112)),
                 "Every borrowed native entry field has the current-I body frame")
            need(all(word["frames"][word["final"][a]] == list(reversed([1 << j for j in range(9)]))
                     for a in range(112)), "Every raw native X output has the common FULL frame")
    need(native["contracts"]["input"] == "Physical X=Qx, Y=y. The native adapters are explicit.",
         "Pinned native input contract")
    need(native["contracts"]["forward_E"] == "Physical X=F x, Y=F q(y+E x).", "Pinned F contract")
    need(native["contracts"]["backward_inverse_E"] == "Physical X=F(x-E^-1 y), Y=F q y.",
         "Pinned reciprocal B contract")
    return L, {"reconstructed_mode_and_physical_matrices": list(modes),
               "physical_P_is_monomial": False, "physical_P_nonzeros": 160,
               "native_word_replayed": False, "native_contract_is_an_explicit_premise": True}


def ordered_proof():
    def reduce(word):
        result = []
        for symbol in word:
            if result and result[-1] == symbol and symbol.startswith("P"):
                result.pop()
            else:
                result.append(symbol)
        return tuple(result)

    def op(symbol, row):
        result = {}
        for (source, word), coefficient in row.items():
            result = plus((1, result), (coefficient, {(source, reduce((symbol,) + word)): F(1)}))
        return result

    x, y = [{(s, ()): F(1)} for s in ("x", "y")]
    t = plus((1, y), (1, op("R0", x)))
    f0 = op("P0", x), op("P0", t)
    b1_raw_x = plus((1, f0[0]), (-1, op("R1", f0[1])))
    b1 = op("P1", b1_raw_x), op("P1", f0[1])
    w = plus((1, x), (-1, op("P0", op("R1", op("P0", t)))))
    need(b1[0] == op("P1", op("P0", w)), "Ordered w formula")
    f2_raw_x = b1[0]
    f2 = op("P2", f2_raw_x), op("P2", plus((1, b1[1]), (1, op("R2", b1[0]))))
    queries = [op("ell0", x), op("ell1", f0[1]), op("ell2", f2_raw_x)]
    expected = [op("ell0", x), op("ell1", op("P0", t)),
                op("ell2", op("P1", op("P0", w)))]
    need(queries == expected, "All three exact source-cut readers")
    need(w != plus((1, x), (-1, op("R1", t))), "P0 and R1 are not commuted")

    def encode(row):
        return [{"input": s, "operators_left_to_right": list(wd), "coefficient": str(c)}
                for (s, wd), c in sorted(row.items())]

    return {"relations_used": "Only adjacent equal P_s factors cancel.",
            "t": encode(t), "w": encode(w), "after_F0": list(map(encode, f0)),
            "B1_raw_X": encode(b1_raw_x), "after_B1": list(map(encode, b1)),
            "F2_raw_X": encode(f2_raw_x), "after_F2": list(map(encode, f2)),
            "queries": list(map(encode, queries)), "wrong_P_R_commutation_rejected": True}


def phase_check(views, model):
    records = {(r["stage"], r["port"]): r for r in views["entries"]}
    need(len(records) == len(views["entries"]) == 336 and
         set(records) == {(s, p) for s in range(3) for p in range(112)}, "Complete literal D25 views")
    need(len(set(model["centre_ports"])) == 16, "Sixteen actual centre anchors")
    counts, output = Counter(), []
    for (s, p), row in sorted(records.items()):
        rho, q = tuple(row["route_columns"]), model["ports"][p]
        alignment = row["literal_stage_alignment"]
        need(row["q"] == q and engine.act(rho, q) == q, "Exact label and fixed own line")
        need(engine.compose(rho, rho) == engine.UNIT and
             all(engine.transposed(rho, rho[j]) == 1 << j for j in range(25)), "Orthogonal involution")
        need(alignment["entry_X"] == alignment["entry_Y"] and
             alignment["exit_X"] == alignment["exit_Y"], "Same literal bank alignment")
        if s == 0:
            need(rho == engine.UNIT and set(alignment.values()) == {0}, "Identity initial view")
            continue
        delta_before, epsilon = alignment["entry_X"], alignment["exit_X"]
        delta_after = engine.act(rho, delta_before)
        entry = line(delta_after, 2) + route(rho)
        inverse_entry = route(rho) + line(delta_after, 2)
        exit_view = line(epsilon, 2) + route(rho)
        previous, exterior, nex = fourier(0, 9 + 8 * (s - 1)), fourier(9, 9 + 8 * s), fourier(0, 9 + 8 * s)
        identities = {
            "before_after_entry_translation": (entry, route(rho) + line(delta_before, 2)),
            "FULL_entry": (entry + previous, exterior + line(q, 1) + route(rho)),
            "hole_entry": (entry + previous + line(q, -1), exterior + route(rho)),
            "FULL_exit": (exit_view + nex, nex + route(rho)),
            "hole_exit": (exit_view + nex + line(q, -1), nex + line(q, -1) + route(rho)),
            "inverse_entry_return": (inverse_entry + exterior, previous + line(q, -1) + route(rho)),
            "entry_inverse": (inverse_entry + entry, []),
            "exit_involution": (exit_view + exit_view, []),
        }
        for name, (left, right) in identities.items():
            need(same(left, right), name)
            counts[name] += 1
        counts["missing_entry_translation_rejected"] += not same(route(rho) + previous,
                                                                   exterior + line(q, 1) + route(rho))
        if p in model["centre_ports"]:
            need(not same(inverse_entry + exterior, previous + route(rho)),
                 "A current-I accumulator does not return to global FULL")
            counts["false_FULL_accumulator_return_rejected"] += 1
            output.append({"stage": s, "anchor": p, "q": q, "rho_columns": list(rho),
                           "entry_translation_before_route": delta_before,
                           "entry_translation_after_route": delta_after,
                           "exit_translation_after_route": epsilon,
                           "current_I_return_type": "Fprev q_anchor",
                           "raw_FULL_return_type": "Fnext"})
    return dict(counts), output


def reader_check(L):
    counts = Counter(c for row in L for c in row.values())
    need(counts == {F(-1): 90, F(1): 46}, "Exact signed reader coefficients")
    need(Counter(map(len, L)) == {10: 8, 7: 8}, "Exact reader row lengths")
    state = eye(128)
    instructions = []
    maximum = F(1)
    for i, row in enumerate(L):
        for p, c in sorted(row.items()):
            state[112 + i] = plus((1, state[112 + i]), (c, state[p]))
            instructions.append(["add", 112 + i, p, str(c)])
            maximum = max(maximum, sum(abs(value) for value in state[112 + i].values()))
    need(state[:112] == eye(112), "Every arbitrary source input is unchanged")
    need(state[112:] == [plus((1, {112 + i: F(1)}), (1, row)) for i, row in enumerate(L)],
         "Every arbitrary accumulator baseline is retained")
    scalar = sum(engine.add_price(F(g[3])) for g in instructions)
    need(scalar == 1088 and len(instructions) == 136, "Exact conditional body invoice")
    need(maximum == 11 and all(c.denominator == 1 for row in state for c in row.values()),
         "Exact local prefix norm and integer coefficients")
    return {"complex_ADDs": 136, "real_scalar_units": scalar, "source_fields": 112,
            "reader_source_port_support": len({p for row in L for p in row}),
            "independent_accumulators_required": 16, "arbitrary_columns_checked": 128,
            "source_fields_changed": 0, "accumulator_baseline_retained": True,
            "prefix_row_one_norm": str(maximum), "binary_denominator_height": 0,
            "map_stream_cost_included": False, "storage_or_retention_supplied": False}, instructions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    data, manifest = {}, {}
    for name, (path, expected) in PINS.items():
        stored = path.read_bytes()
        raw = gzip.decompress(stored) if path.suffix == ".gz" else stored
        need(digest(raw) == expected, "Fixed source " + name)
        data[name] = json.loads(raw)
        manifest[str(path)] = {"file_sha256": digest(stored), "content_sha256": expected}
    manifest[str(ENGINE)] = {"file_sha256": ENGINE_PIN, "content_sha256": ENGINE_PIN}
    need(digest(ARITHMETIC.read_bytes()) == ARITHMETIC_PIN, "Fixed scalar tariff source")
    manifest[str(ARITHMETIC)] = {"file_sha256": ARITHMETIC_PIN, "content_sha256": ARITHMETIC_PIN}
    L, model_report = model_check(data["model"], data["native"])
    ordered = ordered_proof()
    phase_report, anchor_types = phase_check(data["views"], data["model"])
    reader_report, instructions = reader_check(L)
    write_json(args.out / "SOURCE-MANIFEST.json", manifest)
    write_json(args.out / "ORDERED-CONTENTS.json", ordered)
    write_json(args.out / "ANCHOR-TYPES.json", anchor_types)
    write_json(args.out / "CONDITIONAL-READER.json", {"scope": "A body reader on supplied typed accumulators.",
                                                        "events": instructions, "report": reader_report})
    report = {"status": "PASS_INDEPENDENT_RECIPROCAL_SOURCE_CUT_TYPES",
              "checker_sha256": digest(Path(__file__).read_bytes()), "model": model_report,
              "phase_checks": phase_report, "reader": reader_report,
              "ordered_contents_verified": True,
              "cut_types": ["F9 ell0 x", "F9 q_anchor ell1 P0 t", "F25 ell2 P1 P0 w"],
              "tensor_extension": "The exact one-copy identities tensor over every positive width.",
              "native_word_replayed": False, "record_retention_claimed": False,
              "complete_supplier_claimed": False}
    write_json(args.out / "CHECKS.json", report)
    print(json.dumps({"status": report["status"], "phase_identities": sum(v for k, v in phase_report.items()
                      if not k.endswith("rejected")), "reader_scalar": reader_report["real_scalar_units"]}))


if __name__ == "__main__":
    main()
