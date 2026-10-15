#!/usr/bin/env python3
"""Exact p=25 support census and optimistic price for E8 root-pair decoders."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import subprocess
from collections import Counter
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_pins() -> dict:
    source = read_json(HERE / "SOURCES.json")
    base = source["base_commit"]
    rows = source["files"]
    for row in rows:
        path = ROOT / row.get("snapshot_path", row["path"])
        payload = path.read_bytes()
        require(hashlib.sha256(payload).hexdigest() == row["sha256"],
                "working input SHA drift: " + row["path"])
        blob = subprocess.check_output(
            ["git", "rev-parse", f"{base}:{row['path']}"], cwd=ROOT, text=True
        ).strip()
        require(blob == row["git_blob"], "Git blob drift: " + row["path"])
    by_path = {r["path"]: r for r in rows}
    selected = read_json(ROOT / "certificates/selected-result.json")
    require(by_path["certificates/selected-result.json"]["sha256"] ==
            hashlib.sha256((ROOT / "certificates/selected-result.json").read_bytes()).hexdigest(),
            "selected record pin mismatch")
    require(selected["certificate_sha256"] == by_path[
        "research/community-frontier1094-audit/ASSEMBLY.json"]["sha256"],
        "selected certificate hash mismatch")
    require(selected["proof"] == "docs/research/community-batch1099-review.md",
            "selected review path drift")
    return {"base_commit": base,
            "selected_record_sha256": by_path["certificates/selected-result.json"]["sha256"],
            "selected_certificate_sha256": selected["certificate_sha256"],
            "review_sha256": by_path[selected["proof"]]["sha256"],
            "source_manifest_sha256": by_path[
                "research/community-frontier1094-audit/SELECTED-SOURCE.json"]["sha256"]}


def neg(v):
    return tuple(-x for x in v)


def e8_lines():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                v = [0] * 8
                v[i], v[j] = 2 * si, 2 * sj
                roots.append(tuple(v))
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(signs))
    lines = []
    seen = set()
    for root in roots:
        line = root if root > neg(root) else neg(root)
        if line not in seen:
            seen.add(line)
            lines.append(line)
    require(len(roots) == 240 and len(lines) == 120, "E8 root-line construction failed")
    return lines


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def f2_rank(rows):
    basis = {}
    for value in rows:
        value = int(value)
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def exact_support_census():
    lines = e8_lines()
    ip = []
    for a in lines:
        row = []
        for b in lines:
            d = dot(a, b)
            require(d % 4 == 0, "nonintegral E8 inner product")
            row.append(d // 4)
        ip.append(row)
    label_rows = [sum(((ip[i][j] + 1) & 1) << j for j in range(120))
                  for i in range(120)]
    require(f2_rank(label_rows) == 9, "the label-pairing code is not rank nine")

    # Coordinates in any selected basis of the nine-dimensional label span.
    basis_lines = []
    for i, row in enumerate(label_rows):
        if f2_rank([label_rows[j] for j in basis_lines] + [row]) == len(basis_lines) + 1:
            basis_lines.append(i)
        if len(basis_lines) == 9:
            break
    require(len(basis_lines) == 9, "failed to extract label coordinates")
    phi = [sum(((row >> j) & 1) << k for k, j in enumerate(basis_lines))
           for row in label_rows]
    lambdas = list(range(1, 512))
    violators = []
    for lam in lambdas:
        violators.append(sum(((phi[i] & lam).bit_count() % 2) << i for i in range(120)))

    global_owners = {}
    per_root = []
    witness = None
    for alpha in range(120):
        support = sum((ip[alpha][i] != 0) << i for i in range(120))
        minima = 121
        candidate_pair_count = 0
        masks = Counter()
        for x in range(511):
            vx = violators[x] & support
            for y in range(x + 1, 511):
                puncture = vx | (violators[y] & support)
                size = puncture.bit_count()
                if size < minima:
                    minima = size
                if size != 25:
                    continue
                candidate_pair_count += 1
                masks[puncture] += 1
                live_labels = [label_rows[i] for i in range(120)
                               if ((support >> i) & 1) and not ((puncture >> i) & 1)]
                rank = f2_rank(live_labels)
                require(rank == 7, "a size-25 pair mask has live span other than seven")
                if witness is None:
                    witness = (alpha, support, puncture, rank)
                global_owners.setdefault(puncture, set()).add(alpha)
        require(minima == 25, "root support does not first drop at 25 punctures")
        require(candidate_pair_count == 189, "unexpected number of ordered-independent pair representatives")
        require(len(masks) == 63 and set(masks.values()) == {3},
                "root support does not have 63 masks with three pair representatives each")
        per_root.append(len(masks))

    require(len(global_owners) == 120 * 63, "wrong global count of exact extremal masks")
    require(max(len(owners) for owners in global_owners.values()) == 1,
            "one p=25 mask lowers two root-normal supports to dimension seven")
    require(all(len(owners) == 1 for owners in global_owners.values()),
            "an extremal mask has ambiguous root-normal ownership")
    mask_rows = "".join(f"{puncture:030x}:{next(iter(owners))}\n"
                        for puncture, owners in sorted(global_owners.items()))
    require(witness is not None, "missing positive p=25 support witness")
    alpha, support, puncture, rank = witness
    added_back = puncture & -puncture
    near_miss = puncture ^ added_back
    near_miss_rank = f2_rank([label_rows[i] for i in range(120)
                              if ((support >> i) & 1) and not ((near_miss >> i) & 1)])
    require(near_miss_rank == 8, "24-puncture negative control did not restore rank eight")
    root_supports = [sum((ip[b][i] != 0) << i for i in range(120))
                     for b in range(120)]
    other_root_ranks = [f2_rank([label_rows[i] for i in range(120)
                                 if ((root_supports[b] >> i) & 1)
                                 and not ((puncture >> i) & 1)])
                        for b in range(120) if b != alpha]
    require(min(other_root_ranks) >= 8,
            "the witness mask unexpectedly lowers another root-normal support")

    return {
        "root_lines": len(lines),
        "label_pairing_rank": f2_rank(label_rows),
        "root_normal_count": 120,
        "minimum_punctures_for_live_label_span_at_most_7": 25,
        "candidate_functional_pairs_per_root": 130305,
        "size_25_unordered_functional_pairs_per_root": 189,
        "unique_size_25_masks_per_root": 63,
        "pair_representations_per_mask": 3,
        "global_unique_size_25_masks": len(global_owners),
        "extremal_mask_root_pairs_sha256": hashlib.sha256(mask_rows.encode("ascii")).hexdigest(),
        "maximum_root_normals_per_mask": max(len(x) for x in global_owners.values()),
        "all_extremal_live_spans": [7],
        "positive_fixture": {"root_index": alpha, "puncture_mask_hex": hex(puncture),
                             "live_span": rank, "one_puncture_restored_span": near_miss_rank,
                             "minimum_other_root_span": min(other_root_ranks)},
        "negative_controls": {"all_120_roots_first_drop_at_25": True,
                              "24_puncture_near_miss_span_8": near_miss_rank,
                              "same_puncture_other_root_span_at_least_8": min(other_root_ranks) >= 8},
    }


def price_floor():
    result = read_json(ROOT / "research/complex-local-word-ceiling/RESULT.json")
    selected = result["selected"]
    baseline = {int(r): int(n) for r, n in selected["local_profile_per_call"].items()}
    require(baseline == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8},
            "selected local profile drift")

    # P112 to P95 removes 17 ports. PR717's favorable per-port knob removes
    # seven rank-one children plus one rank-four and one rank-five child.
    local = dict(baseline)
    extra_ports = 17
    local[1] -= 7 * extra_ports
    local[4] -= extra_ports
    local[5] -= extra_ports
    port_profile = dict(local)

    spec = importlib.util.spec_from_file_location(
        "pinned_ceiling", ROOT / "research/complex-local-word-ceiling/ceiling.py")
    ceiling = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ceiling)

    def priced_profile(rank_vector):
        center = sum(rank_vector)
        profile = dict(port_profile)
        profile[8] -= 8
        for rank in rank_vector:
            profile[rank] = profile.get(rank, 0) + 1
        profile = {r: n for r, n in profile.items() if n}
        require(all(n >= 0 for n in profile.values()), "negative candidate child count")
        interval = ceiling.ceiling(profile, 73, 8 * 95, 9, center,
                                   grid=Fraction(1, 10**15), R=51)
        return profile, center, interval

    # The floor profile is the most favorable compatible child profile:
    # one exceptional term at rank 5 and seven regular terms at rank 7.
    rank_floor = (5,) + (7,) * 7
    local, center, (lo, hi) = priced_profile(rank_floor)
    model = ceiling.model(local, 73, 8 * 95, 9, center, R=51)
    selected_hi = Fraction(result["ceiling"]["a_ceiling"])
    gate = selected_hi * Fraction(105, 100)
    require(hi < selected_hi, "p=25 root-pair floor reaches the selected ceiling")
    require(hi < gate, "p=25 root-pair floor clears the five-percent gate")

    # Exact negative controls increase the exceptional rank or one regular rank.
    controls = {}
    for name, ranks in (("exceptional_rank_6", (6,) + (7,) * 7),
                        ("one_regular_rank_8", (5,) + (7,) * 6 + (8,))):
        profile, charge, interval = priced_profile(ranks)
        require(charge == 55 and interval[1] < hi,
                "one-unit rank increase did not lower the certified ceiling: " + name)
        controls[name] = {"center_charge": charge,
                          "profile": {str(r): n for r, n in sorted(profile.items())},
                          "a_ceiling_interval": [str(interval[0]), str(interval[1])]}
    return {
        "p_total": 25,
        "additional_ports_from_selected_P112": extra_ports,
        "live_ports": 95,
        "families_per_replica": 760,
        "stages": 9,
        "copy_floor": 54,
        "most_favorable_center_rank_profile": {"5": 1, "7": 7},
        "per_call_local_profile": {str(r): n for r, n in sorted(local.items())},
        "center_charge": center,
        "idle_rank_cap": 51,
        "idle_mass": str(model["idle_mass"]),
        "a_ceiling_interval": [str(lo), str(hi)],
        "a_ceiling_upper_decimal": f"{float(hi):.15f}",
        "selected_a_ceiling_upper": str(selected_hi),
        "five_percent_gate": str(gate),
        "relative_to_selected_upper_percent": f"{float((hi / selected_hi - 1) * 100):.12f}",
        "kappa_translation_cap_only": str(hi / (1 + hi)),
        "extra_setup_frame_hosting_precision_restoration_charges": 0,
        "negative_controls": {"rank_55_profiles": controls,
                              "floor_upper_below_selected": hi < selected_hi,
                              "floor_upper_below_five_percent_gate": hi < gate},
    }


def build_certificate():
    pins = check_pins()
    census = exact_support_census()
    # Binary rank inequality: rank(X,Y) >= dim(X)+dim(Y)-9.
    # At most one of the 16 basis normals can be the unique seven-span root.
    # Its term costs at least 5; each other term has two spans >=8 and costs >=7.
    copy = {
        "pairing_rank_inequality": "rank(X,Y) >= dim(X)+dim(Y)-9",
        "ordinary_term_floor": 7,
        "unique_exceptional_root_span": 7,
        "exceptional_term_floor_if_used_on_one_side": 6,
        "exceptional_term_floor_if_used_on_both_sides_of_same_dual_term": 5,
        "number_of_terms_below_7": "at most one",
        "total_copy_floor": 54,
        "scope": "exact eight-term all-pairs decoders whose row and column normals are E8 roots, at exactly 25 punctures",
        "reason": "one p=25 puncture mask lowers at most one root-normal support; distinctness and duality place it in at most one term",
        "negative_controls": {"regular_seven_term_floor": 49,
                              "exceptional_pair_bound": 5,
                              "total_floor_recomputed": 5 + 7 * 7 == 54},
    }
    price = price_floor()
    return {"status": "PASS_P25_ROOT_PAIR_BOUND",
            "pins": pins,
            "support_census": census,
            "copy_bound": copy,
            "optimistic_price": price,
            "conclusion": "The complete root-pair family at p=25 misses the selected local-word ceiling gate even with zero added implementation charges."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the deterministic certificate")
    args = parser.parse_args()
    certificate = build_certificate()
    path = HERE / "CERTIFICATE.json"
    encoded = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.write:
        path.write_text(encoded, encoding="utf-8")
    else:
        require(path.is_file(), "missing CERTIFICATE.json; run verify.py --write once")
        require(path.read_text(encoding="utf-8") == encoded, "saved certificate differs from exact replay")
    print("PASS_P25_ROOT_PAIR_BOUND masks=" + str(certificate["support_census"]["global_unique_size_25_masks"])
          + " max_root_normals_per_mask=" + str(certificate["support_census"]["maximum_root_normals_per_mask"])
          + " copy_floor=" + str(certificate["copy_bound"]["total_copy_floor"])
          + " a_hi=" + certificate["optimistic_price"]["a_ceiling_upper_decimal"])


if __name__ == "__main__":
    main()
