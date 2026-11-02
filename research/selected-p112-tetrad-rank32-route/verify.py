#!/usr/bin/env python3
"""Bind the exact P112 tetrad decoder to the selected complex port labels."""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import importlib.util
import json
import sys
import tarfile
from fractions import Fraction as Q
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
MEMBER = "candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz"
GEOMETRY_PATH = ROOT / "research/p112-tetrad-local-decoder"
CEILING_PATH = ROOT / "research/complex-local-word-ceiling"
BIT_PATH = ROOT / "research/bit-revision3-levers-seed03"
CENTRE_PATH = ROOT / "research/centre-shared-kcall-charged-seed615415"


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def load_module(name: str, path: Path):
    sys.path.insert(0, str(path))
    spec = importlib.util.spec_from_file_location(name, path / (name + ".py"))
    need(spec is not None and spec.loader is not None, "could not load " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


geom = load_module("verify", GEOMETRY_PATH)
ceiling = load_module("ceiling", CEILING_PATH)
levers = load_module("levers", BIT_PATH)


# Root-index -> selected-provider port-index. This is an explicit finite
# isomorphism witness; the verifier checks every one of its 12,544 pairs.
ROOT_TO_PORT = [
    0, 76, 81, 7, 87, 27, 57, 92, 28, 75, 48, 107, 24, 32, 82, 58,
    86, 1, 98, 45, 35, 85, 6, 93, 46, 110, 29, 74, 49, 108, 23, 33,
    83, 59, 21, 36, 8, 80, 31, 103, 77, 12, 88, 26, 9, 72, 51, 104,
    43, 13, 89, 61, 79, 2, 99, 44, 16, 78, 25, 94, 66, 3, 100, 38,
    17, 56, 67, 95, 10, 71, 52, 105, 42, 14, 90, 62, 97, 69, 54, 19,
    40, 102, 5, 64, 65, 4, 101, 39, 18, 55, 68, 96, 63, 91, 15, 41,
    106, 53, 70, 11, 37, 20, 60, 84, 34, 22, 109, 50, 73, 30, 111, 47,
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def decimal(x: Q, digits: int = 12) -> str:
    return format(float(x), ".%dg" % digits)


def interval_record(value):
    lo, hi = value
    return {"lo": str(lo), "hi": str(hi), "lo_decimal": decimal(lo), "hi_decimal": decimal(hi)}


def load_word():
    with tarfile.open(ARCHIVE, "r:gz") as source:
        member = source.extractfile(MEMBER)
        need(member is not None, "selected provider archive is missing its canonical word")
        compressed = member.read()
    payload = gzip.decompress(compressed)
    word = json.loads(payload)
    need(sha(payload) == "4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c",
         "selected canonical-word payload hash changed")
    need((word["v"], word["h"], word["R"]) == (112, 9, 480),
         "selected provider dimensions changed")
    return word, sha(payload)


def rank2(rows):
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def build_bound_decoder(word):
    roots, frame = geom.roots_and_frame()
    live = sorted(set(roots) - set(frame))
    need(len(live) == 112 and len(ROOT_TO_PORT) == 112,
         "P112 or permutation cardinality changed")
    need(sorted(ROOT_TO_PORT) == list(range(112)), "port map is not a bijection")
    ports = word["ports"]
    need(len(ports) == 112 and len(set(ports)) == 112 and all(0 <= x < 512 for x in ports),
         "selected port labels are not 112 distinct nine-bit addresses")

    gram = [[geom.dot(x, y) // 4 for y in live] for x in live]
    signs = [[geom.dot(x, f) // 4 for f in frame] for x in live]
    labels = [sum(((value + 1) % 2) << j for j, value in enumerate(row))
              for row in gram]
    port_label = [ports[ROOT_TO_PORT[i]] for i in range(112)]
    need(all(((labels[i] >> j) & 1) == ((port_label[i] & port_label[j]).bit_count() % 2)
             for i in range(112) for j in range(112)),
         "the source-bound map fails a P112 parity pairing")

    blocks = collections.defaultdict(list)
    groups = collections.defaultdict(list)
    for i, row in enumerate(signs):
        tetrad = tuple(j for j, value in enumerate(row) if value)
        need(len(tetrad) == 4 and all(row[j] in (-1, 1) for j in tetrad),
             "unexpected P112 tetrad coordinate row")
        blocks[tetrad].append(i)
        groups[tetrad, sum(row[j] < 0 for j in tetrad) % 2].append(i)
    need(len(blocks) == 14 and all(len(x) == 8 for x in blocks.values()),
         "P112 tetrad partition changed")
    need(len(groups) == 28 and all(len(x) == 4 for x in groups.values()),
         "P112 four-frame partition changed")

    terms = []
    mapped_groups = []
    for tetrad, block in sorted(blocks.items()):
        mapped_groups.append(sorted(ROOT_TO_PORT[i] for i in block))
        for coordinate in tetrad:
            d = [signs[i][coordinate] if i in block else 0 for i in range(112)]
            terms.append((d, d[:]))

    matrix = geom.decoder_matrix(terms, 112)
    need(geom.masked_exact(matrix, gram), "the 56-term identity fails on the P112 mask")
    pairing_masks = labels
    profile = collections.Counter()
    for d, t in terms:
        x = [i for i, value in enumerate(d) if value]
        y = [i for i, value in enumerate(t) if value]
        y_mask = sum(1 << i for i in y)
        cost = rank2(pairing_masks[i] & y_mask for i in x)
        profile[cost] += 1
    need(dict(profile) == {2: 56}, "mapped tetrad decoder copy profile changed")
    need(all(matrix[i][j] == 4 * (i == j) for i in range(112) for j in range(112)
             if gram[i][j] == 0 or i == j),
         "diagonal/orthogonal endpoint identity failed")

    return {
        "root_count": len(roots),
        "live_ports": len(live),
        "port_graph_rank_f2": rank2(labels),
        "map_sha256": sha(json.dumps(ROOT_TO_PORT, separators=(",", ":")).encode()),
        "map_checked_pairs": 112 * 112,
        "tetrad_blocks": len(blocks),
        "four_frames": len(groups),
        "mapped_tetrad_port_groups": mapped_groups,
        "masked_identity_entries_checked": sum(row.bit_count() for row in labels),
        "decoder_terms": len(terms),
        "decoder_copy_profile": {str(k): v for k, v in sorted(profile.items())},
        "decoder_copy_mass": sum(k * v for k, v in profile.items()),
        "masked_identity": "PASS: K_ii=4 and K_ij=0 for distinct orthogonal port pairs",
    }


def price_profiles(word):
    selected = read_json(ROOT / "certificates/selected-result.json")
    complex_result = read_json(CEILING_PATH / "RESULT.json")
    complex_word = complex_result["selected"]
    model = complex_result["model"]
    base = {int(r): int(n) for r, n in complex_word["local_profile_per_call"].items()}
    need(base == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8},
         "selected complex local profile changed")
    need(sum(r * n for r, n in base.items()) == 5586,
         "selected complex local mass changed")

    centre_result = read_json(CENTRE_PATH / "RESULT.json")
    centre_readme = (CENTRE_PATH / "README.md").read_text(encoding="utf-8")
    need("184 ADD + 8 scratch CLEAR" in centre_readme,
         "the pinned centre ledger no longer states the literal phase invoice")
    baseline = next(row for row in centre_result["rows"] if int(row["k"]) == 1)
    phase = 184 + int(baseline["restoration_scratch_clear_per_call"])
    old_centre = int(baseline["centre_charge_per_call"])
    need((phase, old_centre, int(baseline["copy_children_r8_per_call"])) == (192, 64, 8),
         "selected phase or centre-copy invoice changed")
    noncentre = sum(r * n for r, n in base.items()) - phase - old_centre
    need(noncentre == 5330, "selected non-centre mass changed")
    large_children, large_remainder = divmod(noncentre, 32)
    need((large_children, large_remainder) == (166, 18),
         "complex rank-32 mass decomposition changed")

    # Replace the non-complete tri-plane copy-only profile by this exact masked
    # tetrad identity, retain the literal phase, and grant two unpaid slots.
    m = int(model["m"])
    families = int(model["ports"]) * int(model["pairs"]) * 2
    stages = int(model["stages"])
    idle_cap = int(model["idle_rank_cap"])
    profile = {1: phase, 2: 56, 32: large_children}
    need((m, families, stages, idle_cap) == (73, 896, 9, 51),
         "complex moment model changed")
    need(sum(r * n for r, n in profile.items()) == 5616,
         "replacement complex profile mass changed")
    c_model = ceiling.model(profile, m, families, stages, 112,
                            R=idle_cap, unpaid=2)
    c_target = ceiling.relax(profile, m, families, stages, 112, Q(1, 99),
                             R=idle_cap, unpaid=2)
    c_one = ceiling.relax(profile, m, families, stages, 112, Q(1, 99),
                          R=idle_cap, unpaid=1)
    need(c_target[1] < 1 and c_one[0] > 1,
         "complex target or one-unpaid failure control changed")
    c_root = ceiling.ceiling(profile, m, families, stages, 112,
                             grid=Q(1, 10**12), R=idle_cap, unpaid=2)
    c_kappa = c_root[1] / (1 + c_root[1])

    # The independent bit-side ideal profile is pinned to its own replay:
    # retain nine rank-7 copies and replace its other mass by rank-32 blocks.
    bit_result = read_json(BIT_PATH / "RESULT.json")
    br = bit_result["replay"]
    bit_base = {int(r): int(n) for r, n in br["local_histogram"].items()}
    bit_copies = {int(r): int(n) for r, n in br["copies"].items()}
    need(bit_base == {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
         and bit_copies == {7: 9}, "bit supplier budget inputs changed")
    bw = Q(br["w"])
    bit_m = 64
    bit_centre = int(br["copy_charge_per_call"])
    bit_idle_cap = int(br["record_idle_cap"])
    noncopy_profile = dict(bit_base)
    noncopy_profile[7] -= 9
    noncopy_mass = sum(r * n for r, n in noncopy_profile.items())
    bit_children, bit_remainder = divmod(noncopy_mass, 32)
    need((noncopy_mass, bit_children, bit_remainder, bit_centre, bit_idle_cap)
         == (5066, 158, 10, 63, 45), "bit rank-32 mass decomposition changed")
    bit_profile = {7: 9, 32: bit_children}
    b_hist = levers.relaxed(bit_profile, bit_m, bw, bit_centre,
                            bit_idle_cap, unpaid=2)
    b_target = levers.bill(b_hist, bit_m, bw, Q(1, 99), surcharge=True)
    b_one_hist = levers.relaxed(bit_profile, bit_m, bw, bit_centre,
                                bit_idle_cap, unpaid=1)
    b_one = levers.bill(b_one_hist, bit_m, bw, Q(1, 99), surcharge=True)
    need(b_target[1] < 1 and b_one[0] > 1,
         "bit target or one-unpaid failure control changed")
    b_root = levers.root(b_hist, bit_m, bw, surcharge=True, tol=Q(1, 10**12))
    b_kappa = b_root[1] / (1 + b_root[1])
    joint_kappa = min(c_kappa, b_kappa)

    need(selected["decimal"] == "0.001672660197076918",
         "selected kappa record changed")
    need(word["local_profile"] == {str(k): v for k, v in base.items()},
         "frozen supplier profile differs from the selected price receipt")

    return {
        "status": "PASS_SELECTED_P112_TETRAD_RANK32_BUDGET",
        "selected_kappa": selected["decimal"],
        "complex": {
            "profile": {str(k): v for k, v in sorted(profile.items())},
            "centre_charge": 112,
            "unpaid_coordinates": 2,
            "local_mass": str(c_model["local_mass"]),
            "idle_mass": str(c_model["idle_mass"]),
            "moment_at_1_over_99": interval_record(c_target),
            "one_unpaid_control_at_1_over_99": interval_record(c_one),
            "a_ceiling": {"lo": str(c_root[0]), "hi": str(c_root[1]),
                          "hi_decimal": decimal(c_root[1])},
            "kappa_cap_hi": str(c_kappa),
            "kappa_cap_hi_decimal": decimal(c_kappa),
        },
        "bit": {
            "profile": {str(k): v for k, v in sorted(bit_profile.items())},
            "centre_charge": bit_centre,
            "unpaid_coordinates": 2,
            "moment_at_1_over_99": interval_record(b_target),
            "one_unpaid_control_at_1_over_99": interval_record(b_one),
            "a_ceiling": {"lo": str(b_root[0]), "hi": str(b_root[1]),
                          "hi_decimal": decimal(b_root[1])},
            "kappa_cap_hi": str(b_kappa),
            "kappa_cap_hi_decimal": decimal(b_kappa),
            "inherited_surcharge": True,
        },
        "joint_ideal_kappa_cap_hi": str(joint_kappa),
        "joint_ideal_kappa_cap_hi_decimal": decimal(joint_kappa),
        "not_a_supplier_or_selected_improvement": True,
    }


def calculate():
    word, payload_hash = load_word()
    decoder = build_bound_decoder(word)
    pricing = price_profiles(word)
    return {
        "source": {
            "selected_archive_sha256": sha(ARCHIVE.read_bytes()),
            "canonical_word_payload_sha256": payload_hash,
            "canonical_word_member": MEMBER,
        },
        "decoder": decoder,
        "budget": pricing,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="write the recomputed RESULT.json")
    args = ap.parse_args()
    result = calculate()
    path = PACKAGE / "RESULT.json"
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        path.write_text(encoded, encoding="utf-8")
    else:
        need(path.exists(), "RESULT.json is absent; run verify.py --write once")
        need(json.loads(path.read_text(encoding="utf-8")) == result,
             "recomputed result differs from RESULT.json")
    print("PASS_SELECTED_P112_TETRAD_RANK32_BUDGET "
          "terms=56 copy=112 complex_kappa_cap="
          + result["budget"]["complex"]["kappa_cap_hi_decimal"]
          + " joint_ideal_cap=" + result["budget"]["joint_ideal_kappa_cap_hi_decimal"]
          + " selected_unchanged")


if __name__ == "__main__":
    main()
