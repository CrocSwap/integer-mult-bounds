#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact adapter from the selected 112-port set to one E8 P104 decoder."""
import argparse
import gzip
import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rank_f2(values):
    pivots = {}
    for value in values:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def price_profile(manifest):
    """Replay the selected T37 profile and the pinned PR717 P1 P104 knob."""
    pins = manifest["pricing_inputs"]
    for rel, expected in pins.items():
        require(sha(ROOT / rel) == expected, "pricing input pin mismatch: " + rel)
    engines = ROOT / "research/complex-k492-owner-repair/vendor/multicold/engines"
    moment = load_module(engines / "moment.py", "adapter_moment")
    base_two = load_module(engines / "base_two_moment.py", "adapter_base_two")
    outer = load_module(engines / "outer.py", "adapter_outer")
    pricing = load_module(ROOT / "research/complex-t21-owners/vendor/pr870/independent/price_profile_t16.py",
                          "adapter_price_profile")
    bit_record = json.loads((ROOT / "research/complex-t21-owners/vendor/pr870/inputs/PR589-EXPECTED.json").read_text())
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text())
    assembly_path = ROOT / selected["certificate"]
    require(sha(assembly_path) == selected["certificate_sha256"], "selected assembly hash mismatch")
    assembly = json.loads(assembly_path.read_text())
    H0 = Counter({int(r): n for r, n in assembly["complex_profile"].items()})
    width = 73
    mass0 = sum(r * n for r, n in H0.items())
    cell = 8 * 112 - 9 * 64
    replicas = next(t for t in range(1, 1000) if width * 896 * t - mass0 == cell * t)
    calls = 9 * replicas
    W0 = 896 * replicas
    D0 = cell * replicas
    require(replicas == 16 and width * W0 - mass0 == D0 and D0 == 5120, "selected profile coverage identity")

    def scenario(port_drops, copy_units):
        H = Counter(H0)
        H[8] -= copy_units * calls
        H[7] += copy_units * calls
        for _ in range(port_drops):
            for r in (1, 1, 1, 5, 1, 1, 4, 1, 1):
                H[r] -= calls
            H[48] -= 9 * replicas
        H = Counter({r: n for r, n in H.items() if n})
        W = W0 - 8 * port_drops * replicas
        D = replicas * (8 * (112 - port_drops) - 9 * (64 - copy_units))
        require(all(n > 0 for n in H.values()), "nonpositive scenario count")
        require(width * W - sum(r * n for r, n in H.items()) == D, "P104 full-profile coverage identity")
        return H, W, D

    bit_c = Q(bit_record["nine"]["bit_lower"])
    selected_lower = Q(moment.certify(H0, width, W0, False)["lower"])
    H, W, deficit = scenario(8, 8)
    candidate = Q(moment.certify(H, width, W, False)["lower"])
    conservative = Q(moment.certify(H, width, W, True)["lower"])
    checks = pricing.moment_checks(moment, base_two, H, width, W, candidate, deficit, False)
    candidate_outer = pricing.outer47(bit_c, candidate, outer)
    bit_cap = pricing.outer47(bit_c, 2 * bit_c, outer)
    baseline_outer = pricing.outer47(bit_c, selected_lower, outer)
    require(selected_lower == Q(assembly["complex_lower"]), "selected complex moment reproduction")
    require(baseline_outer["kappa"] == selected["kappa"], "selected kappa reproduction")
    require(candidate_outer["binding"] == "bit" and candidate_outer["kappa"] == bit_cap["kappa"],
            "P104 knob must be bit-capped")
    require(len(checks) == 2, "both exact moment engines must agree")
    return {
        "status": "FAVORABLE_P104_KNOB_SCENARIO_NOT_A_COMPLETE_SUPPLIER",
        "replicas": replicas,
        "calls": calls,
        "width": width,
        "P112": {"ports_per_word": 112, "copy_units": 64, "W": W0, "deficit": D0,
                 "complex_profile": {str(r): H0[r] for r in sorted(H0)}},
        "P104": {"ports_per_word": 104, "copy_units": 56, "W": W, "deficit": deficit,
                 "complex_profile": {str(r): H[r] for r in sorted(H)}},
        "selected_complex_lower": str(selected_lower),
        "P104_complex_lower": str(candidate),
        "P104_complex_lower_decimal": pricing.decimal(candidate),
        "P104_conservative_lower_decimal": pricing.decimal(conservative),
        "complex_change_percent": pricing.decimal((candidate / selected_lower - 1) * 100),
        "P104_knob_outer": candidate_outer,
        "bit_cap": bit_cap,
        "two_exact_moment_engines": True,
        "unpriced_obligations": [
            "asymmetric-centre reads and construction",
            "phase-frame legality and restoration for the new local word",
            "PR717 unpaired-centre parity costs and pair-split conflicts",
            "integration into a complete replacement supplier and whole-call hosting",
        ],
    }


def construct():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    selected_record = ROOT / "certificates/selected-result.json"
    require(sha(selected_record) == manifest["selected_record"]["sha256"], "selected-result pin mismatch")
    selected_meta = json.loads(selected_record.read_text())
    require(selected_meta["certificate"] == manifest["selected_record"]["certificate"],
            "selected certificate path mismatch")
    require(selected_meta["certificate_sha256"] == manifest["selected_record"]["certificate_sha256"],
            "selected certificate SHA mismatch")
    require(sha(ROOT / "research/complex-block-rank-optimum/inputs/selected.json.gz") ==
            manifest["selected_ports"]["sha256"], "selected port payload pin mismatch")
    require(sha(ROOT / "research/complex-frame-pair-decoders/verify.py") ==
            manifest["e8_model"]["sha256"], "E8 model pin mismatch")

    e8 = load_module(ROOT / "research/complex-frame-pair-decoders/verify.py", "adapter_e8_model")
    with gzip.open(ROOT / "research/complex-block-rank-optimum/inputs/selected.json.gz", "rt") as stream:
        selected_word = json.load(stream)
    ports = selected_word["ports"]
    require(len(ports) == len(set(ports)) == 112, "selected word port set is not 112 distinct labels")
    target = [e8.PHI[i] for i in e8.P112]
    target_to_root = {e8.PHI[i]: i for i in e8.P112}
    require(len(target_to_root) == 112, "P112 target labels are not distinct")

    # This exact matrix maps selected linear functionals to E8 P112 functionals.
    F_columns = [5, 276, 303, 338, 362, 68, 143, 148, 167]

    def apply_f(v):
        out = 0
        for i, column in enumerate(F_columns):
            if v >> i & 1:
                out ^= column
        return out

    require(len({apply_f(v) for v in range(512)}) == 512, "F is not invertible")
    w_selected = [sum((a & p).bit_count() & 1 for p in ports) for a in range(512)]
    w_target = [sum((a & p).bit_count() & 1 for p in target) for a in range(512)]
    require(all(w_selected[a] == w_target[apply_f(a)] for a in range(512)),
            "linear functional weight identity failed")

    def solve_f(v):
        hits = [x for x in range(512) if apply_f(x) == v]
        require(len(hits) == 1, "F inverse is not unique")
        return hits[0]

    # If w_S(a) = w_T(Fa) for every a, Fourier inversion gives S = F^T T.
    # Thus selected port vectors map to T by F^{-T}.
    inverse_columns = [solve_f(1 << i) for i in range(9)]
    inverse_rows = [sum(((inverse_columns[j] >> i) & 1) << j for j in range(9)) for i in range(9)]
    L_columns = inverse_rows

    def apply_l(v):
        out = 0
        for i, column in enumerate(L_columns):
            if v >> i & 1:
                out ^= column
        return out

    mapped_ports = [apply_l(p) for p in ports]
    require(len(set(mapped_ports)) == 112 and set(mapped_ports) == set(target),
            "F^{-T} does not map the selected ports bijectively to P112")
    source_to_root = {p: target_to_root[apply_l(p)] for p in ports}

    # PR717's P104 frame, expressed by indices within its fixed P112 ordering.
    p104_frame_ordinals = [9, 15, 24, 46, 52, 66, 94, 104]
    frame1 = [e8.P112[q] for q in p104_frame_ordinals]
    removed = [p for p in ports if source_to_root[p] in frame1]
    require(len(removed) == 8, "the selected P104 puncture does not remove eight ports")
    live_ports = [p for p in ports if p not in set(removed)]
    live_roots = [source_to_root[p] for p in live_ports]
    require(len(live_ports) == len(live_roots) == 104, "P104 live set size mismatch")

    solutions = e8.frame_pair_solutions(e8.FRAME0, frame1)
    require(len(solutions) == 8, "selected P104 frame pair must have eight exact decoders")
    pairs = solutions[0]
    row_vectors, column_vectors = e8.build_pairs(pairs)
    exact, term_ranks = e8.decoder_cost(row_vectors, column_vectors, live_roots)
    dual, pair_ranks = e8.pair_decoder(pairs, live_roots)
    require(exact and dual and term_ranks == pair_ranks == [7] * 8, "P104 decoder identity/copy ranks")

    # Failure controls: a corrupted adapter is rejected; corrupting one coefficient breaks exactness;
    # restoring any one punctured line preserves exactness but raises copy cost to 57.
    bad_F_columns = list(F_columns)
    bad_F_columns[0] ^= 1
    def apply_bad_f(v):
        out = 0
        for i, column in enumerate(bad_F_columns):
            if v >> i & 1:
                out ^= column
        return out
    bad_map_rejected = ({apply_bad_f(p) for p in ports} != set(target) or
                        any(w_selected[a] != w_target[apply_bad_f(a)] for a in range(512)))
    bad_columns = list(column_vectors)
    bad_columns[0] = tuple(x + y for x, y in zip(bad_columns[0], e8.LINES[e8.FRAME0[0]]))
    corrupted_decoder_rejected = not e8.decoder_cost(row_vectors, bad_columns, live_roots)[0]
    restored_exact, restored_costs = e8.pair_decoder(pairs, live_roots + [frame1[0]])
    restored_line_rejected = restored_exact and sum(restored_costs) == 57
    require(bad_map_rejected and corrupted_decoder_rejected and restored_line_rejected,
            "one or more failure controls did not reject the mutation/restoration")

    price = price_profile(manifest)
    return {
        "schema_version": 1,
        "seed": "e8aefa5747f8dc1d69ca9c50f361d20c",
        "task_id": "complex-new-helper-inventory",
        "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
        "selected_record_sha256": manifest["selected_record"]["sha256"],
        "adapter": {
            "F_columns": F_columns,
            "F_minus_transpose_columns": L_columns,
            "all_512_weight_identities": True,
            "selected_ports_mapped": 112,
            "P112_target_bijection": True,
            "P104_frame_ordinals": p104_frame_ordinals,
            "P104_frame_root_indices": frame1,
            "removed_selected_port_values": removed,
            "removed_selected_port_positions": [ports.index(p) for p in removed],
            "live_ports": 104,
        },
        "decoder": {
            "frame_pair_solutions": len(solutions),
            "chosen_root_pairs": pairs,
            "exact_D_times_T_transpose_equals_2G": exact,
            "term_copy_ranks": term_ranks,
            "total_copy_cost": sum(term_ranks),
            "copy_ratio": "56/104=7/13",
            "controls": {
                "corrupt_linear_adapter_rejected": bad_map_rejected,
                "corrupt_decoder_coefficient_rejected": corrupted_decoder_rejected,
                "restore_one_punctured_port_costs_57": restored_line_rejected,
            },
        },
        "pricing": price,
        "scope": "Exact P104 decoder adapter on the selected 112-port label set; the per-port knob price is favorable and does not establish a complete replacement supplier or a new kappa.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the exact certificate")
    args = parser.parse_args()
    # Normalize tuples to JSON lists before comparing the computed result to its certificate.
    result = json.loads(json.dumps(construct()))
    cert = HERE / "CERTIFICATE.json"
    if args.write:
        cert.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    else:
        require(json.loads(cert.read_text()) == result, "certificate differs from exact reconstruction")
    print("PASS_SELECTED_P104_PORT_ADAPTER: 512 exact weights; 112-port GL adapter; P104 104 ports; 8 terms rank 7; exact selected-profile knob price; no full supplier or new kappa")


if __name__ == "__main__":
    main()
