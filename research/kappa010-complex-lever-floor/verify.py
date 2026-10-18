#!/usr/bin/env python3
"""Exact target screen for a joint complex-side lever bundle.

At kappa=1/10 the retained transfer needs primitive saving a=1/9.  We
evaluate the existing certified interval moment engine on the selected local
profile and on one explicitly hypothetical bundle: seven two-output anchors,
zero centre charge, and fractional repacking of all remaining local rank mass
into rank-16 children.  We vary only the unpaid-coordinate count u.

This is a budget screen, not a supplier construction.  All source alignment,
the changed coverage identity, centre deletion, and the rank-16 consumer are
granted for free or represented by an optimistic tariff.
"""
from __future__ import annotations

import importlib.util
import hashlib
import io
import json
import sys
import tarfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CEILING_PATH = ROOT / "research/complex-local-word-ceiling/ceiling.py"
SPEC = importlib.util.spec_from_file_location("complex_ceiling", CEILING_PATH)
assert SPEC and SPEC.loader
C = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = C
SPEC.loader.exec_module(C)


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def moment(local: dict[int, Q | int], centre: int, unpaid: int) -> tuple[Q, Q]:
    return C.relax(local, 73, 896, 9, centre, Q(1, 9), unpaid=unpaid)


def local_only_moment(local: dict[int, Q | int]) -> tuple[Q, Q]:
    """Lower bound from paid local children alone; idle mass is nonnegative."""
    lo = hi = Q(0)
    for r, n in local.items():
        child_lo, child_hi = C.child_cost(r, 73, Q(1, 9))
        lo += Q(n) * child_lo
        hi += Q(n) * child_hi
    return C.down(lo / Q(896, 9)), C.up(hi / Q(896, 9))


def max_feasible_unpaid(local: dict[int, Q | int], centre: int) -> int:
    valid = []
    for u in range(1, 73):
        try:
            C.model(local, 73, 896, 9, centre, unpaid=u)
        except ValueError:
            continue
        valid.append(u)
    assert valid
    return max(valid)


def result_case(local: dict[int, Q | int], centre: int, unpaid: int) -> dict:
    lo, hi = moment(local, centre, unpaid)
    return {
        "unpaid_coordinates": unpaid,
        "centre_mass_per_call": centre,
        "moment_interval_at_a_1_over_9": [str(lo), str(hi)],
        "moment_approx": format(float((lo + hi) / 2), ".12f"),
        "below_one": hi < 1,
    }


def first_passing_unpaid(local: dict[int, Q | int], centre: int) -> int | None:
    for u in range(1, 73):
        try:
            lo, hi = moment(local, centre, u)
        except ValueError:
            continue
        if hi < 1:
            return u
    return None


def first_passing_local_rank(local_mass: int, unpaid: int, centre: int) -> int | None:
    """Smallest uniform local child rank that passes; idle children keep R=51."""
    for r in range(1, 52):
        try:
            lo, hi = C.relax({r: Q(local_mass, r)}, 73, 896, 9, centre,
                             Q(1, 9), R=51, unpaid=unpaid)
        except ValueError:
            continue
        if hi < 1:
            return r
    return None


def unpaid_frontier(local_mass: int, local_rank: int, centre: int) -> dict:
    local = {local_rank: Q(local_mass, local_rank)}
    u = first_passing_unpaid(local, centre)
    assert u is not None and u > 1
    return {
        "uniform_local_rank": local_rank,
        "centre_mass_per_call": centre,
        "previous_unpaid": result_case(local, centre, u - 1),
        "first_passing_unpaid": result_case(local, centre, u),
    }


def fee_case(base_mass: int, blocks: int, fee_per_block: int,
             unpaid: int, centre: int) -> dict:
    local_mass = base_mass + blocks * fee_per_block
    lo, hi = C.relax({16: Q(local_mass, 16)}, 73, 896, 9, centre,
                     Q(1, 9), R=51, unpaid=unpaid)
    return {
        "rank_one_equivalent_fee_per_block": fee_per_block,
        "total_local_mass": local_mass,
        "unpaid_coordinates": unpaid,
        "centre_mass_per_call": centre,
        "moment_interval_at_a_1_over_9": [str(lo), str(hi)],
        "moment_approx": format(float((lo + hi) / 2), ".12f"),
        "below_one": hi < 1,
    }


def maximum_passing_fee(base_mass: int, blocks: int,
                        unpaid: int, centre: int) -> tuple[int, int]:
    """Largest integer fee e passing, followed by the first failing e."""
    def passes(e: int) -> bool:
        try:
            return fee_case(base_mass, blocks, e, unpaid, centre)["below_one"]
        except ValueError:
            return False

    lo, hi = 0, 1000
    assert passes(lo) and not passes(hi)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if passes(mid):
            lo = mid
        else:
            hi = mid
    return lo, hi


def rank_mod2(matrix: list[list[int]]) -> int:
    rows = [sum((value & 1) << j for j, value in enumerate(row)) for row in matrix]
    width = len(matrix[0]) if matrix else 0
    pivot = 0
    for col in range(width):
        row = next((r for r in range(pivot, len(rows)) if (rows[r] >> col) & 1), None)
        if row is None:
            continue
        rows[pivot], rows[row] = rows[row], rows[pivot]
        for r in range(len(rows)):
            if r != pivot and ((rows[r] >> col) & 1):
                rows[r] ^= rows[pivot]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def paired_plane_port_charge() -> dict:
    """Reprice the pinned 49-support fit under full port-space pairing ranks."""
    cert_path = "research/paired-plane-minrank-bracket-audit/CERTIFICATE.json"
    matching_path = "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json"
    block_result_path = "research/paired-plane-block-rank/RESULT.json"
    archive_path = "research/community-frontier1094-audit/selected-replay.tar.gz"
    cert_raw = (ROOT / cert_path).read_bytes()
    matching_raw = (ROOT / matching_path).read_bytes()
    block_result_raw = (ROOT / block_result_path).read_bytes()
    assert hashlib.sha256(cert_raw).hexdigest() == "6f5d3478290156c4fe703104572cc3aa593ad50079476ae08c942833714e3179"
    assert hashlib.sha256(matching_raw).hexdigest() == "4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1"
    assert hashlib.sha256(block_result_raw).hexdigest() == "8b78968378d7ed824ac2418fe40b36db04d9522c117349778655191b4ee10d6d"
    cert = json.loads(cert_raw)
    matching = json.loads(matching_raw)
    block_result = json.loads(block_result_raw)
    assert cert["result"]["min_scalar_fitting_rank"] == 49
    assert block_result["status"] == "PASS_PAIRED_PLANE_BLOCK_RANK"
    assert block_result["theorem"].startswith("minimum rank is 49*d")
    archive = (ROOT / archive_path).read_bytes()
    member_name = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        member = tar.extractfile(member_name)
        assert member is not None
        payload = member.read()
    assert hashlib.sha256(payload).hexdigest() == "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
    labels_by_port = {row["port"]: row["q"] for row in json.loads(payload)["recipes"]}
    assert sorted(labels_by_port) == list(range(112))
    labels = [labels_by_port[i] for i in range(112)]
    pairs = matching["matching"]
    assert len(pairs) == 56 and sorted(i for pair in pairs for i in pair) == list(range(112))
    owner = [-1] * 112
    planes = []
    for plane_id, (left, right) in enumerate(pairs):
        a, b = labels[left], labels[right]
        dot = lambda x, y: (x & y).bit_count() & 1
        assert dot(a, a) == dot(b, b) == 1 and dot(a, b) == 0
        owner[left] = owner[right] = plane_id
        planes.append((a, b))
    supports = cert["rank49_supports"]
    assert len(supports) == 49 and sorted(i for support in supports for i in support) == list(range(112))
    profile: Counter[int] = Counter()
    for support in supports:
        plane_ids = [owner[port] for port in support]
        assert len(set(plane_ids)) == len(plane_ids)
        for i, plane_i in enumerate(plane_ids):
            for plane_j in plane_ids[i + 1:]:
                assert all(dot(x, y) == 0
                           for x in planes[plane_i] for y in planes[plane_j])
        vectors = [v for plane_id in plane_ids for v in planes[plane_id]]
        gram = [[dot(x, y) for y in vectors] for x in vectors]
        # A permitted support consists of mutually orthogonal nondegenerate
        # planes, so its complete port-space charge is the rank of this Gram
        # matrix, exactly twice the support size.
        assert rank_mod2(gram) == 2 * len(support)
        profile[2 * len(support)] += 1
    assert dict(sorted(profile.items())) == {2: 2, 4: 31, 6: 16}
    assert sum(rank * count for rank, count in profile.items()) == 224
    return {
        "scalar_factor_count": 49,
        "support_size_histogram": {str(k // 2): n for k, n in sorted(profile.items())},
        "port_space_copy_profile": {str(k): n for k, n in sorted(profile.items())},
        "port_space_mass_per_payload_copy": 224,
        "scope": "Pinned disjoint-support fit, priced by full port-space Gram ranks; not a lower bound on every decoder or a native schedule.",
    }


def block_anchor_case(base_mass: int, blocks: int, fee_per_block: int,
                      copies: int, centre: int) -> dict:
    """Target moment under an explicit rank-one-equivalent fee sensitivity.

    Scalar ADDs are not part of the exponent profile.  This fee parameter is
    retained only to show how a separately established interface cost would
    affect the moment if it were translated to rank-one-equivalent units.
    """
    unpaid = 2 * copies
    local: dict[int, Q | int] = {51: Q(base_mass, 51)}
    if fee_per_block:
        local[1] = blocks * fee_per_block
    if centre:
        # Retaining the centre also retains its eight rank-8 children.
        local[8] = 8
    for rank, count in ((2, 2 * copies), (4, 31 * copies), (6, 16 * copies)):
        local[rank] = count
    return result_case(local, centre, unpaid)


def block_mass_excess(base_mass: int, copies: int) -> Q:
    """Paid rank mass minus coverage capacity, with scalar ADDs separate."""
    unpaid = 2 * copies
    local_mass = Q(base_mass + 224 * copies)
    coverage = Q(73 - unpaid) * Q(896, 9)
    return local_mass - coverage


def maximum_block_anchor_fee(base_mass: int, blocks: int,
                             copies: int, centre: int) -> tuple[int, int] | None:
    """Largest integer per-block ADD fee after the d-fold plane decoder."""
    def passes(fee: int) -> bool:
        try:
            return block_anchor_case(base_mass, blocks, fee, copies, centre)["below_one"]
        except ValueError:
            return False

    if not passes(0):
        return None
    lo, hi = 0, 1000
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if passes(mid):
            lo = mid
        else:
            hi = mid
    return lo, hi


def main() -> None:
    selected = read_json("certificates/selected-result.json")
    ceiling = read_json("research/complex-local-word-ceiling/RESULT.json")
    anchor = read_json("research/complex-two-output-sum-anchor-seed65ce19/RESULT.json")
    dirty_anchor = read_json("research/complex-dirty-output-temporary-sum-anchor/RESULT.json")
    five_plane = read_json("research/five-plane-port-p112-seed1f7fdfe4/RESULT.json")
    five_plane_sources = read_json("research/five-plane-port-p112-seed1f7fdfe4/SOURCES.json")
    assert selected["decimal"] == "0.001672660197076918"
    assert ceiling["status"] == "PASS_COMPLEX_LOCAL_WORD_CEILING"
    assert anchor["status"] == "PASS_TWO_OUTPUT_TEMPORARY_SUM_ANCHOR"
    assert dirty_anchor["status"] == "PASS_DIRTY_OUTPUT_TEMPORARY_SUM_ANCHOR"
    assert five_plane["status"] == "completed_local_algebraic_construction"

    m = ceiling["model"]["m"]
    families = Q(ceiling["model"]["live_families_per_call"])
    stages = ceiling["model"]["stages"]
    centre = ceiling["model"]["centre_per_call"]
    assert (m, families, stages, centre) == (73, Q(896, 9), 9, 64)
    assert anchor["cost_screen"]["block_width_q"] == 112
    assert anchor["cost_screen"]["direct_rank_one_children_per_block"] == 332
    assert anchor["cost_screen"]["anchored_rank_one_children_per_block"] == 112
    assert anchor["cost_screen"]["max_direct_blocks_in_rank_one_profile"] == 7
    archive_path = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
    archive_sha = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    archive_source = next(
        x for x in five_plane_sources["files"]
        if x["path"] == "research/community-frontier1094-audit/selected-replay.tar.gz"
    )
    assert archive_sha == archive_source["sha256"] == "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"

    # The predecessor's selected profile is source-bound in its result. Seven
    # q=112 blocks replace 332 rank-one children by 112 each. Keep e=112 only
    # as a rank-one-equivalent tariff sensitivity; scalar ADDs are screened
    # separately below.
    selected_profile = {int(r): int(n) for r, n in anchor["cost_screen"]["selected_profile"].items()}
    blocks = anchor["cost_screen"]["max_direct_blocks_in_rank_one_profile"]
    affine_fee = anchor["cost_screen"]["affine_additions_per_block"]
    direct = anchor["cost_screen"]["direct_rank_one_children_per_block"]
    replacement = anchor["cost_screen"]["anchored_rank_one_children_per_block"]
    anchored = dict(selected_profile)
    anchored[1] = anchored[1] - blocks * direct + blocks * (replacement + affine_fee)
    assert anchored == {1: 1656, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}

    # Grant complete centre deletion: remove the eight rank-8 centre copies
    # and its separate 64-unit call charge.  Then grant a still more favorable
    # consumer by fractionally moving every remaining unit of rank mass to 16.
    anchor_centre_free = {r: n for r, n in anchored.items() if r != 8}
    anchor_mass = sum(r * n for r, n in anchor_centre_free.items())
    assert anchor_mass == 4766
    rank16 = {16: Q(anchor_mass, 16)}
    base_rank1 = anchored[1] - blocks * affine_fee
    base_mass = sum(r * n for r, n in {**anchored, 1: base_rank1}.items() if r != 8)
    assert base_mass == 3982
    dirty_budget = dirty_anchor["budget"]
    dirty_profile = {int(r): int(n) for r, n in
                     dirty_budget["hypothetical_profile_after_seven_blocks"].items()}
    assert dirty_profile == {1: 872, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
    assert sum(r * n for r, n in dirty_profile.items() if r != 8) == base_mass
    scalar_invoice = dirty_budget["separate_scalar_invoice"]
    assert scalar_invoice["added_unit_addition_macros_per_call"] == 1568
    assert int(scalar_invoice["new_local_primitive_bound_upper"]) < int(scalar_invoice["guard"])
    unchanged_bit_a = Q(dirty_budget["local_complex_ceiling"]["unchanged_bit_endpoint"])
    unchanged_bit_kappa = unchanged_bit_a / (1 + unchanged_bit_a)
    assert str(unchanged_bit_a) == "1733427039589844234749/1000000000000000000000000"

    # Compare the existing five-plane P112 algebraic port decoder, whose
    # RESULT/SOURCES bind it to the exact same selected replay archive.  This
    # screen imports its recorded profile; the old decoder verifier is not
    # represented as independently replayed here.
    p112 = five_plane["decoder"]
    p112_profile = {int(r): int(n) for r, n in p112["local_profile"].items()}
    assert p112["local_mass"] == 5640
    assert sum(r * n for r, n in p112_profile.items()) == 5640
    assert five_plane["local_screen"]["law"] == "unpaid=5"
    assert five_plane["local_screen"]["max_total_rank1_equivalent_charge"] == 275
    p112_actual = result_case(p112_profile, 64, 5)
    p112_local_only = local_only_moment(p112_profile)
    p112_any_unpaid = first_passing_unpaid(p112_profile, 0)
    p112_rank16 = {16: Q(5640, 16)}
    p112_rank16_u5_free = result_case(p112_rank16, 0, 5)
    p112_rank16_u5_centre = result_case(p112_rank16, 64, 5)
    p112_rank16_first_free = first_passing_unpaid(p112_rank16, 0)
    p112_rank16_first_centre = first_passing_unpaid(p112_rank16, 64)
    p112_rank_u5_free = first_passing_local_rank(5640, 5, 0)
    p112_rank_u5_centre = first_passing_local_rank(5640, 5, 64)
    assert not p112_actual["below_one"] and not p112_rank16_u5_free["below_one"]
    assert p112_local_only[0] > 1 and p112_any_unpaid is None
    assert not p112_rank16_u5_centre["below_one"]
    assert (p112_rank16_first_free, p112_rank16_first_centre) == (11, 12)
    assert (p112_rank_u5_free, p112_rank_u5_centre) == (37, 41)

    # Baseline has no passing unpaid count even after deleting its centre while
    # keeping the local word fixed; check the most permissive valid u.
    baseline_centre_free = {r: n for r, n in selected_profile.items() if r != 8}
    baseline_max_u = max_feasible_unpaid(baseline_centre_free, 0)
    baseline_at_max = result_case(baseline_centre_free, 0, baseline_max_u)
    assert baseline_max_u == 17
    assert not baseline_at_max["below_one"]

    # Boundary checks for the anchor-only and anchor+rank16 models.
    anchor_u23 = result_case(anchor_centre_free, 0, 23)
    anchor_u24 = result_case(anchor_centre_free, 0, 24)
    assert not anchor_u23["below_one"] and anchor_u24["below_one"]
    rank16_u9 = result_case(rank16, 0, 9)
    rank16_u10 = result_case(rank16, 0, 10)
    rank16_u10_centre = result_case(rank16, 64, 10)
    rank16_u11_centre = result_case(rank16, 64, 11)
    assert not rank16_u9["below_one"] and rank16_u10["below_one"]
    assert not rank16_u10_centre["below_one"] and rank16_u11_centre["below_one"]

    # A small discrete frontier shows the tradeoff between how much the
    # unpaid coverage law changes and how high the local consumer can raise
    # all 4,766 units of mass.  Idle remainder remains at the legal cap 51.
    frontier = [
        unpaid_frontier(anchor_mass, rank, c)
        for rank in (16, 32, 48, 51)
        for c in (0, 64)
    ]
    assert [x["first_passing_unpaid"]["unpaid_coordinates"] for x in frontier] == [
        10, 11, 6, 7, 4, 4, 3, 4
    ]
    rank_thresholds = {
        "u4_centre_free": first_passing_local_rank(anchor_mass, 4, 0),
        "u4_centre_retained": first_passing_local_rank(anchor_mass, 4, 64),
        "u10_centre_free": first_passing_local_rank(anchor_mass, 10, 0),
        "u10_centre_retained": first_passing_local_rank(anchor_mass, 10, 64),
    }
    assert rank_thresholds == {
        "u4_centre_free": 42,
        "u4_centre_retained": 47,
        "u10_centre_free": 15,
        "u10_centre_retained": 17,
    }
    e10_free = maximum_passing_fee(base_mass, blocks, 10, 0)
    e11_centre = maximum_passing_fee(base_mass, blocks, 11, 64)
    fee_boundaries = {
        "u10_centre_free": {
            "passing": fee_case(base_mass, blocks, e10_free[0], 10, 0),
            "first_failing": fee_case(base_mass, blocks, e10_free[1], 10, 0),
            "extra_allowance_after_112_affine_units": e10_free[0] - affine_fee,
        },
        "u11_centre_retained": {
            "passing": fee_case(base_mass, blocks, e11_centre[0], 11, 64),
            "first_failing": fee_case(base_mass, blocks, e11_centre[1], 11, 64),
            "extra_allowance_after_112_affine_units": e11_centre[0] - affine_fee,
        },
    }
    assert e10_free == (170, 171)
    assert e11_centre == (207, 208)
    assert fee_boundaries["u10_centre_free"]["extra_allowance_after_112_affine_units"] == 58
    assert fee_boundaries["u11_centre_retained"]["extra_allowance_after_112_affine_units"] == 95

    # Try the explicit block-valued endpoint: tensor d copies of the pinned
    # 49-support paired-plane fit. The 110-update dirty-target floor and the
    # anchor's 224-add schedule are scalar operations, not rank-one-equivalent
    # exponent costs. The known anchor scalar invoice is screened separately;
    # the decoder's own linear setup/cleanup remains unpriced.
    plane_decoder = paired_plane_port_charge()
    assert plane_decoder["port_space_copy_profile"] == {"2": 2, "4": 31, "6": 16}
    assert plane_decoder["port_space_mass_per_payload_copy"] == 224
    min_dirty_updates = anchor["cost_screen"]["block_width_q"] - 2
    assert min_dirty_updates == 110
    assert dirty_anchor["q112"]["affine_additions"] == 224
    assert scalar_invoice["added_unit_addition_macros_per_call"] == blocks * 224

    zero_fee_endpoint = []
    for copies in range(1, 8):
        centre_rows = {
            str(centre): block_anchor_case(base_mass, blocks, 0, copies, centre)
            for centre in (0, 64)
        }
        zero_fee_endpoint.append({
            "payload_copies": copies,
            "unpaid_coordinates": 2 * copies,
            "scalar_dirty_update_floor_per_block": min_dirty_updates,
            "zero_rank_one_equivalent_fee_moments": centre_rows,
            "rank_one_equivalent_fee_frontier_per_block": {
                str(centre): maximum_block_anchor_fee(base_mass, blocks,
                                                       copies, centre)
                for centre in (0, 64)
            },
        })
    assert [x["zero_rank_one_equivalent_fee_moments"]["0"]["below_one"]
            for x in zero_fee_endpoint] == [False, False, True, True, True, True, True]
    assert [x["zero_rank_one_equivalent_fee_moments"]["64"]["below_one"]
            for x in zero_fee_endpoint] == [False, False, True, True, True, True, True]
    assert [x["rank_one_equivalent_fee_frontier_per_block"] for x in zero_fee_endpoint[:5]] == [
        {"0": None, "64": None},
        {"0": None, "64": None},
        {"0": (28, 29), "64": (8, 9)},
        {"0": (62, 63), "64": (42, 43)},
        {"0": (96, 97), "64": (76, 77)},
    ]
    d3_centre_free = zero_fee_endpoint[2]["zero_rank_one_equivalent_fee_moments"]["0"]
    d3_centre_retained = zero_fee_endpoint[2]["zero_rank_one_equivalent_fee_moments"]["64"]
    assert Q(d3_centre_free["moment_interval_at_a_1_over_9"][1]) < 1
    assert Q(d3_centre_retained["moment_interval_at_a_1_over_9"][1]) < 1

    # Preserve the old e=110 result only as an intentionally pessimistic
    # rank-one-equivalent tariff sensitivity; it is not the project's scalar
    # operation cost model.
    stacked_endpoint = []
    for copies in range(1, 6):
        centre_rows = {
            str(centre): block_anchor_case(base_mass, blocks, min_dirty_updates,
                                           copies, centre)
            for centre in (0, 64)
        }
        assert all(Q(row["moment_interval_at_a_1_over_9"][0]) > 1
                   for row in centre_rows.values())
        stacked_endpoint.append({
            "payload_copies": copies,
            "unpaid_coordinates": 2 * copies,
            "scalar_dirty_update_floor_per_block": min_dirty_updates,
            "if_mispriced_as_rank_one_equivalent_fee_110_per_block": centre_rows,
        })
    assert [x["rank_one_equivalent_fee_frontier_per_block"] for x in zero_fee_endpoint[:5]] == [
        {"0": None, "64": None},
        {"0": None, "64": None},
        {"0": (28, 29), "64": (8, 9)},
        {"0": (62, 63), "64": (42, 43)},
        {"0": (96, 97), "64": (76, 77)},
    ]
    # With scalar ADDs separate, the exponent profile remains mass-feasible
    # through d=7; at d=8 even its zero-tariff profile exceeds capacity.
    d8_excess = block_mass_excess(base_mass, 8)
    per_copy_excess = Q(224) + 2 * families
    assert d8_excess == Q(298, 3) and per_copy_excess == Q(3808, 9) > 0

    # Positive control: the same highly optimistic rank-16 profile does pass
    # the repository's much smaller planning target a=1/99 with only one
    # unpaid coordinate when the centre is free.
    planning = C.relax(rank16, 73, 896, 9, 0, Q(1, 99), unpaid=1)
    assert planning[1] < 1

    result = {
        "status": "PASS_KAPPA010_COMPLEX_LEVER_FLOOR; scoped budget screen only",
        "selected_kappa": selected["decimal"],
        "target_kappa": "1/10",
        "target_primitive_saving_a": "1/9",
        "model": {
            "m": 73,
            "families_per_call": str(families),
            "stages": stages,
            "rank_cap": 51,
            "selected_centre_charge": centre,
            "target_moment_engine": "exact outward rational intervals from complex-local-word-ceiling/ceiling.py",
        },
        "baseline_local_profile": {str(r): n for r, n in sorted(selected_profile.items())},
        "baseline_centre_free_max_feasible_unpaid": baseline_max_u,
        "baseline_at_max_unpaid": baseline_at_max,
        "seven_anchor_hypothesis": {
            "blocks": blocks,
            "rank_one_additions_per_block": affine_fee,
            "affine_charge_assumption": "112 additions are charged as 112 rank-one-equivalent units per block",
            "profile_before_centre_deletion": {str(r): n for r, n in sorted(anchored.items())},
            "centre_free_profile": {str(r): n for r, n in sorted(anchor_centre_free.items())},
            "centre_free_rank_mass": anchor_mass,
            "rank16_fractional_profile": {"16": str(rank16[16])},
            "anchor_only_boundary": {"u23": anchor_u23, "u24": anchor_u24},
            "rank16_boundary_centre_free": {"u9": rank16_u9, "u10": rank16_u10},
            "rank16_boundary_centre_retained": {"u10": rank16_u10_centre, "u11": rank16_u11_centre},
            "first_passing_unpaid_centre_free": first_passing_unpaid(rank16, 0),
            "first_passing_unpaid_centre_retained": first_passing_unpaid(rank16, 64),
            "uniform_rank_frontier_at_target": frontier,
            "minimum_uniform_local_rank_at_fixed_unpaid": rank_thresholds,
            "fee_boundaries_with_fractional_rank16_consumer": fee_boundaries,
        },
        "five_plane_p112_predecessor_screen": {
            "source_result": "research/five-plane-port-p112-seed1f7fdfe4/RESULT.json",
            "source_replay_archive_sha256": archive_sha,
            "local_profile": {str(r): n for r, n in sorted(p112_profile.items())},
            "reported_local_unpaid_count": 5,
            "actual_profile_at_a_1_over_9": p112_actual,
            "local_children_only_lower_bound_interval": [str(p112_local_only[0]), str(p112_local_only[1])],
            "local_children_only_moment_approx": format(float((p112_local_only[0] + p112_local_only[1]) / 2), ".12f"),
            "passes_for_any_integer_unpaid_with_original_local_profile": p112_any_unpaid is not None,
            "fractional_rank16_all_mass_u5_centre_free": p112_rank16_u5_free,
            "fractional_rank16_all_mass_u5_centre_retained": p112_rank16_u5_centre,
            "first_passing_unpaid_at_rank16": {
                "centre_free": p112_rank16_first_free,
                "centre_retained": p112_rank16_first_centre,
            },
            "minimum_uniform_local_rank_at_u5": {
                "centre_free": p112_rank_u5_free,
                "centre_retained": p112_rank_u5_centre,
            },
            "scope": "The predecessor RESULT is screened as a pinned profile; its algebraic decoder is not replayed by this package.",
        },
        "planning_target_positive_control": {
            "a": "1/99",
            "rank16_profile_unpaid": 1,
            "centre_mass": 0,
            "moment_interval": [str(planning[0]), str(planning[1])],
            "below_one": planning[1] < 1,
        },
        "tensorized_paired_plane_anchor_screen": {
            "predecessor_support_fit": plane_decoder,
            "payload_copy_to_unpaid_rule": "u=2d",
            "base_mass_repacked_at_rank": 51,
            "base_mass_before_endpoint_and_dirty_updates": base_mass,
            "anchor_blocks": blocks,
            "dirty_output_anchor_source_result": "research/complex-dirty-output-temporary-sum-anchor/RESULT.json",
            "dirty_output_anchor_scalar_invoice": scalar_invoice,
            "unchanged_bit_side_primitive_endpoint_a": str(unchanged_bit_a),
            "unchanged_bit_side_kappa_cap": str(unchanged_bit_kappa),
            "unchanged_bit_side_kappa_cap_decimal": format(float(unchanged_bit_kappa), ".15f"),
            "one_target_dirty_update_floor_per_block_scalar_additions": min_dirty_updates,
            "actual_dirty_anchor_additions_per_block": 224,
            "separate_scalar_cost_model": {
                "rank_one_equivalent_fee_in_exponent_profile": 0,
                "known_seven_block_anchor_additions_are_within_selected_scalar_guard": True,
                "decoder_linear_setup_cleanup_cost": "unknown; not in the anchor scalar invoice",
                "interpretation": "ADDs are screened in the scalar compiler envelope; they are not automatically rank-one-equivalent child costs.",
            },
            "d_1_through_7_zero_fee_target_moments": zero_fee_endpoint,
            "first_passing_d_centre_free": 3,
            "first_passing_d_centre_retained": 3,
            "d_1_through_5_if_charged_110_rank_one_equivalent_units_per_block": stacked_endpoint,
            "d8_zero_fee_mass_excess": str(d8_excess),
            "mass_excess_growth_per_extra_copy": str(per_copy_excess),
            "conclusion": "Under the corrected separated-scalar model, the zero-rank-one-fee exponent relaxation first passes a=1/9 at d=3 (moment 0.984346 centre-free, 0.995605 with centre); d=1,2 fail and d=8 is mass-infeasible. This is only a relaxed profile result. The earlier d=1..5 failure used a hypothetical rank-one-equivalent ADD tariff and is retained as sensitivity, not as the selected scalar cost model.",
            "scope": "The exact paired-plane factorization and dirty-output anchor are not composed into a selected-provider source block. Decoder linear setup/cleanup, frames, precision, tape, restoration and whole-supplier transfer remain unpriced; no new kappa is established.",
        },
        "scope": [
            "A failure rejects only the stated selected-profile or seven-anchor budget models; it is not a barrier for other algorithms.",
            "The passing u=10 case places all 4,766 units of paid local rank mass into fractional rank-16 children and grants centre removal and a changed coverage law for free.",
            "No source alignment, full dirty endpoint, rank-16 decoder, restoration schedule, physical invoice, supplier transfer, or new kappa is constructed.",
            "The hypothetical 112-unit block fee prices affine additions only; all other interface charges are waived.",
            "The d-fold screen separates scalar ADD guard costs from the exponent rank profile; the rank-one-equivalent fee rows are tariff sensitivities only.",
            "The d=3 moment pass uses a fractional rank-51 repacking of the remaining 3,982 rank mass and waives decoder linear setup/cleanup and source placement; it is not an implementation or kappa improvement.",
            "The existing bit-side endpoint remains unchanged and still caps the selected complete construction far below 0.1.",
        ],
    }
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"])
    print("  selected word, centre-free at its largest feasible u:", baseline_at_max["moment_approx"])
    print("  anchor-only boundary: u=23 fails at", anchor_u23["moment_approx"], "; u=24 passes at", anchor_u24["moment_approx"])
    print("  rank-16 centre-free boundary: u=9 fails at", rank16_u9["moment_approx"], "; u=10 passes at", rank16_u10["moment_approx"])
    print("  retaining centre shifts rank-16 boundary to u=", first_passing_unpaid(rank16, 64))
    print("  with u=4, minimum uniform local rank:", rank_thresholds["u4_centre_free"], "centre-free,", rank_thresholds["u4_centre_retained"], "with centre")
    print("  max rank-one-equivalent fee per block: e=", e10_free[0], "at u=10/centre-free; e=", e11_centre[0], "at u=11/centre-retained")
    print("  five-plane u=5 decoder profile at a=1/9:", p112_actual["moment_approx"], "; rank-16 requires u=", p112_rank16_first_free, "centre-free or", p112_rank16_first_centre, "with centre")
    print("  five-plane paid local terms alone:", format(float((p112_local_only[0] + p112_local_only[1]) / 2), ".12f"), ">1")
    print("  paired-plane d=3 with separate scalar ADD invoice:", d3_centre_free["moment_approx"], "centre-free;", d3_centre_retained["moment_approx"], "with centre")


if __name__ == "__main__":
    main()
