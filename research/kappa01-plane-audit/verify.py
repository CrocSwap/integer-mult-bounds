#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-pinned repair of the paired-plane kappa=0.1 budget screen.

This is a scoped accounting obstruction, not a multiplication theorem.
No predecessor generator is run and no predecessor artifact is rewritten.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
M, W, N, V, H, R = 73, 896, 9, 112, 9, 51
w, A = Q(W, N), Q(1, 9)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reject(call, message):
    try:
        call()
    except ValueError:
        return message
    raise ValueError("negative control accepted: " + message)


def verify_sources():
    data = json.loads((HERE / "SOURCES.json").read_text())
    for record in data["files"]:
        require(hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()
                == record["sha256"], "source SHA256: " + record["path"])
    return data


def gf2_rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            leading = value.bit_length() - 1
            if leading not in pivots:
                pivots[leading] = value
                break
            value ^= pivots[leading]
    return len(pivots)


def reconstruct_support_profile():
    archive = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
    member = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
    with tarfile.open(archive, "r:gz") as stream:
        raw = stream.extractfile(member).read()
    require(hashlib.sha256(raw).hexdigest()
            == "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
            "native port labels")
    labels = {x["port"]: x["q"] for x in json.loads(raw)["recipes"]}
    matching = json.loads((ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_text())["matching"]
    supports = json.loads((ROOT / "research/paired-plane-minrank-bracket-audit/CERTIFICATE.json").read_text())["rank49_supports"]
    require(sorted(labels) == list(range(V)), "port labels")
    require(sorted(x for pair in matching for x in pair) == list(range(V)), "matching partition")
    require(sorted(x for support in supports for x in support) == list(range(V)), "support partition")
    plane_of = {p: i for i, pair in enumerate(matching) for p in pair}
    planes = [[labels[p] for p in pair] for pair in matching]
    dot = lambda x, y: (x & y).bit_count() % 2
    for x, y in planes:
        require((dot(x, x), dot(y, y), dot(x, y)) == (1, 1, 0), "nondegenerate orthonormal plane")
    profile = Counter()
    for support in supports:
        owners = [plane_of[p] for p in support]
        require(len(owners) == len(set(owners)), "same-plane forbidden entry")
        vectors = [x for owner in owners for x in planes[owner]]
        gram = [sum(dot(x, y) << j for j, y in enumerate(vectors)) for x in vectors]
        require(gram == [1 << j for j in range(len(vectors))], "orthogonal complete plane spans")
        require(gf2_rank(gram) == 2 * len(support), "full plane support copy rank")
        profile[2 * len(support)] += 1
    require(profile == {2: 2, 4: 31, 6: 16}, "copy profile")
    require(sum(r * count for r, count in profile.items()) == 224, "copy mass")
    return profile


def validate_private_charge(local, centre, private_copy_mass, base_centre):
    require(centre == base_centre + private_copy_mass,
            "private COPY charge is missing from total paid mass")
    require(sum(r * Q(n) for r, n in local.items()) >= private_copy_mass,
            "private COPY charge is missing from the local occurrence profile")


def validate_payload_replication(d, unpaid, families, local, baseline):
    require(d >= 1 and unpaid == 2,
            "payload replication alone cannot enlarge a geometric plane")
    require(families == d * W, "replicated data families must be counted")
    require(local == {r: d * count for r, count in baseline.items()},
            "all public and private occurrences must replicate")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    sources = verify_sources()
    spec = importlib.util.spec_from_file_location("pinned_ceiling", ROOT / "research/complex-local-word-ceiling/ceiling.py")
    C = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(C)
    copy_profile = reconstruct_support_profile()
    anchor = json.loads((ROOT / "research/complex-two-output-sum-anchor-seed65ce19/RESULT.json").read_text())["cost_screen"]
    selected = {int(rank): count for rank, count in anchor["selected_profile"].items()}
    require(selected == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}, "selected profile")
    require((anchor["max_direct_blocks_in_rank_one_profile"],
             anchor["direct_rank_one_children_per_block"],
             anchor["anchored_rank_one_children_per_block"]) == (7, 332, 112), "anchor hypothesis")
    public_mass = sum(r * n for r, n in selected.items()) - 64 - 7 * (332 - 112)
    require(public_mass == 3982, "anchor public mass, scalar ADDs separate")

    def interval_case(local, families, charge, unpaid):
        lo, hi = C.relax(local, M, families, N, charge, A, unpaid=unpaid)
        model = C.model(local, M, families, N, charge, unpaid=unpaid)
        return {"interval": [str(lo), str(hi)], "decimal": f"{float((lo+hi)/2):.12f}",
                "below_one": hi < 1, "above_one": lo > 1,
                "total_mass": str(model["total_mass"]),
                "local_mass": str(model["local_mass"]), "idle_mass": str(model["idle_mass"])}

    rows = []
    for d in range(1, 8):
        entry = {"d": d, "unpaid_granted_only_for_comparison": 2*d,
                 "private_copy_mass": 224*d, "variants": {}}
        for base_centre in (0, 64):
            local = {R: Q(public_mass, R), **{r: d*n for r, n in copy_profile.items()}}
            if base_centre:
                local[8] = 8
            repaired_charge = base_centre + 224*d
            validate_private_charge(local, repaired_charge, 224*d, base_centre)
            original = interval_case(local, W, base_centre, 2*d)
            corrected = interval_case(local, W, repaired_charge, 2*d)
            require(corrected["above_one"], "corrected target must fail")
            # Inserting private work cannot remove existing public idle work.
            before_private = {R: Q(public_mass, R)}
            if base_centre:
                before_private[8] = 8
            before = C.model(before_private, M, W, N, base_centre, unpaid=2*d)
            require(Q(corrected["idle_mass"]) == before["idle_mass"], "private insertion changes no public idle")
            zero = Q((M - 2*d)*W + (224*d + base_centre)*N, M*W)
            require(zero == 1 + Q(d, 292) + Q(base_centre*N, M*W), "exact zero-saving mass")
            require(zero > 1, "zero-saving obstruction")
            entry["variants"][str(base_centre)] = {"omitted_charge_screen": original,
                        "repaired_charge": repaired_charge,
                        "repaired_screen": corrected, "moment_at_zero": str(zero)}
        rows.append(entry)

    # Correct replication: all arrays and occurrences repeat, geometry does not.
    baseline = {R: Q(public_mass, R), **copy_profile}
    replica = interval_case(baseline, W, 224, 2)
    replication = []
    for d in (1, 2, 3, 7):
        local = {r: d*n for r, n in baseline.items()}
        validate_payload_replication(d, 2, d*W, local, baseline)
        repeated = interval_case(local, d*W, d*224, 2)
        require(repeated["interval"] == replica["interval"], "replication changes normalized moment")
        replication.append({"payload_batches": d, "families": d*W,
                            "unpaid": 2, "moment_interval": repeated["interval"]})

    # Scoped native-leg gate. Other work has only its rank-mass baseline charged;
    # even the R=51 halving guard and all decoder/centre costs are waived here.
    leg_lo, leg_hi = C.child_cost(7, M, A)
    gate_lo = Q(71, 73) + Q(224)/w*(leg_lo - Q(7, 73))
    gate_hi = Q(71, 73) + Q(224)/w*(leg_hi - Q(7, 73))
    require(gate_lo > 1, "unchanged native legs obstruct target")
    # Logarithm-free corroboration: the gate exceeds one exactly when this
    # positive ninth root exceeds 71/63.
    require(Q(71, 63)**9 < Q(73, 7), "independent exact ninth-power gate")

    controls = [
        reject(lambda: validate_private_charge(baseline, 0, 224, 0), "omitted private total-mass charge"),
        reject(lambda: validate_private_charge(baseline, 224, 224, 64), "old centre silently replaced by decoder charge"),
        reject(lambda: validate_payload_replication(3, 6, 3*W,
                        {r: 3*n for r, n in baseline.items()}, baseline), "payload copies misread as unpaid dimensions"),
        reject(lambda: validate_payload_replication(3, 2, W,
                        {r: 3*n for r, n in baseline.items()}, baseline), "replicated family normalization omitted"),
        reject(lambda: require(6*2 <= H, "three orthogonal four-planes cannot fit nine dimensions"), "dimension lift in unchanged nine-dimensional chart"),
    ]
    # Positive controls distinguish errors from the existing, legitimate
    # conditional screen and the legitimate d=1 geometry.
    require(rows[2]["variants"]["64"]["omitted_charge_screen"]["below_one"], "reproduce predecessor numerical pass")
    require(6 <= H, "original three orthogonal two-plane support fits")
    result = {
        "status": "PASS_KAPPA01_PLANE_ACCOUNTING_AUDIT",
        "base": sources["base"], "target_kappa": "1/10", "necessary_primitive_a": "1/9",
        "strict_transfer_note": "A complete kappa=1/10 proof needs a>1/9 under kappa<a/(1+a).",
        "support_copy_profile": {str(r): n for r, n in sorted(copy_profile.items())},
        "rows": rows, "consistent_replication": replication,
        "unchanged_native_legs_gate": {
            "mandatory_profile": {"7": 224}, "unpaid": 2,
            "decoder_and_centre_charge_granted": 0,
            "moment_lower_bound_interval": [str(gate_lo), str(gate_hi)],
            "decimal": f"{float((gate_lo+gate_hi)/2):.12f}",
            "independent_exact_test": "(71/63)^9 < 73/7",
            "scope": "Retains 224 separate rank-seven native legs or within-leg factorizations; excludes a new fused multi-array consumer."
        },
        "negative_controls": controls,
        "scope": "Accounting repair and scoped necessary conditions only; no physical supplier, bit-side repair or new kappa."
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x") as output:
            output.write(encoded)
    elif (HERE / "RESULT.json").exists():
        require(json.loads((HERE / "RESULT.json").read_text()) == result, "stored receipt mismatch")
    print(result["status"], "d3_corrected=" + rows[2]["variants"]["64"]["repaired_screen"]["decimal"],
          "native_gate=" + result["unchanged_native_legs_gate"]["decimal"], "controls=" + str(len(controls)))


if __name__ == "__main__":
    main()
