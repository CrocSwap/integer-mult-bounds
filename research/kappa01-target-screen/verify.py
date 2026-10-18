#!/usr/bin/env python3
"""Exact target-scale screen for the selected complex and bit local words.

At kappa = 1/10 the retained planning transfer requires primitive saving
a = 1/9. This checker lower-bounds both selected local-word moments at that
point using integer ninth-root inequalities only. It also prices ideal
zero-overhead reblockings of the selected bit local rank mass.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SCALE = 10**30
TARGET_A = Q(1, 9)
EXPECTED_WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
EXPECTED_BIT_WORD = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}


def require(ok: bool, label: str) -> None:
    if not ok:
        raise ValueError(label)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ast_assignments(path: Path) -> dict[str, object]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        value = ast.literal_eval(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):
                found[target.id] = value
            elif isinstance(target, ast.Tuple):
                names = [x.id for x in target.elts if isinstance(x, ast.Name)]
                if len(names) == len(target.elts) and isinstance(value, tuple):
                    found.update(zip(names, value))
    return found


def source_profile() -> tuple[int, int, int, dict[int, int]]:
    source = ROOT / "research/complex-local-word-ceiling/levers.py"
    values = ast_assignments(source)
    require((values.get("M"), values.get("FAM"), values.get("ST")) == (73, 896, 9),
            "selected local-word dimensions drifted")
    word = values.get("WORD")
    require(isinstance(word, dict), "selected local word is missing")
    word = {int(r): int(n) for r, n in word.items()}
    require(word == EXPECTED_WORD, "selected local profile differs from the audited source")
    return 73, 896, 9, word


def root_enclosure(rank: int, width: int) -> tuple[int, int, bool]:
    """Enclose (rank/width)^(8/9) in multiples of 1/SCALE.

    The comparison k/SCALE <= y is equivalent to
    k^9 * width^8 <= rank^8 * SCALE^9, so every step is integer arithmetic.
    """
    require(0 < rank < width, "rank must lie strictly inside the width")
    rhs = rank**8 * SCALE**9
    width_factor = width**8
    lo, hi = 0, SCALE
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid**9 * width_factor <= rhs:
            lo = mid
        else:
            hi = mid - 1
    exact = lo**9 * width_factor == rhs
    upper = lo if exact else lo + 1
    require(lo**9 * width_factor <= rhs, "root lower endpoint failed")
    require(upper**9 * width_factor >= rhs, "root upper endpoint failed")
    return lo, upper, exact


def moment_interval(word: dict[int, int | Q], width: int, families: Q):
    """Enclose sum_r n_r (r/width)^(8/9) / families exactly."""
    lower = upper = Q(0)
    terms = []
    for rank, count in sorted(word.items()):
        lo, hi, exact = root_enclosure(rank, width)
        lower += count * Q(lo, SCALE)
        upper += count * Q(hi, SCALE)
        terms.append({
            "rank": rank,
            "count": str(count),
            "root_lower_numerator": str(lo),
            "root_upper_numerator": str(hi),
            "exact_root": exact,
        })
    return lower / families, upper / families, terms


def bit_profile() -> tuple[dict[int, int], dict[str, object]]:
    """Bind the selected bit histogram through its audited receipt to the word."""
    selected_path = ROOT / "certificates/selected-result.json"
    assembly_path = ROOT / "research/community-frontier1094-audit/ASSEMBLY.json"
    receipt_path = ROOT / "research/bit-revision3-levers-seed03/RESULT.json"
    expected_path = ROOT / "research/e8-bit-p111-tuned/tune/EXPECTED.json"
    word_path = ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"

    selected = read_json(selected_path)
    assembly = read_json(assembly_path)
    receipt = read_json(receipt_path)
    expected = read_json(expected_path)
    binding = receipt["binding"]
    replay = receipt["replay"]
    word_record = expected["word"]
    require(receipt["status"] == "PASS_BIT_REVISION3_LEVERS",
            "selected bit receipt is not a successful audited replay")
    require(selected["kappa"] == assembly["kappa"],
            "selected bit and complex records no longer share the selected kappa")
    require(assembly["binding"] == "complex", "selected assembly is no longer complex-bound")
    require(binding["record"] == "certificates/selected-result.json"
            and binding["assembly"] == "research/community-frontier1094-audit/ASSEMBLY.json",
            "bit receipt no longer binds the selected record and assembly")
    require(binding["expected"] == "research/e8-bit-p111-tuned/tune/EXPECTED.json"
            and binding["word"] == "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz",
            "bit receipt no longer binds the selected bit word inputs")
    require(binding["assembly_sha256"] == sha256(assembly_path),
            "bit receipt assembly hash drifted")
    require(binding["expected_sha256"] == sha256(expected_path)
            and binding["word_sha256"] == sha256(word_path)
            and word_record["file_sha256"] == sha256(word_path),
            "bit receipt expected-record or selected-word hash drifted")
    local = {int(r): int(n) for r, n in replay["local_histogram"].items()}
    expected_local = {int(r): int(n) for r, n in word_record["local_histogram"].items()}
    require(local == expected_local == EXPECTED_BIT_WORD,
            "selected bit local histogram differs from its expected record")
    require(replay["local_mass"] == 5129 and replay["w"] == "296/3"
            and replay["stages"] == 9 and replay["record_idle_cap"] == 45
            and replay["copy_charge_per_call"] == 63,
            "selected bit dimensions or coverage-law inputs drifted")
    return local, {
        "receipt_sha256": sha256(receipt_path),
        "expected_sha256": sha256(expected_path),
        "selected_word_sha256": sha256(word_path),
        "local_mass": replay["local_mass"],
        "live_families_per_call": replay["w"],
        "stages": replay["stages"],
        "unpaid_coordinates": 1,
        "centre_mass": replay["copy_charge_per_call"],
        "maximum_child_rank": replay["record_idle_cap"],
    }


def bit_total_mass_bill_interval(unpaid: int, centre: Q, width: int,
                                 families: Q, rank_cap: int):
    """Most favorable bill for fixed coverage mass under a rank cap."""
    total_mass = (width - unpaid) * families + centre
    lo, hi, _ = root_enclosure(rank_cap, width)
    lower = total_mass * Q(lo, SCALE) / (rank_cap * families)
    upper = total_mass * Q(hi, SCALE) / (rank_cap * families)
    return lower, upper


def bit_block_profile(rank_mass: int, block_cap: int) -> dict[int, int]:
    """Cost-minimizing integer partition of rank mass with a maximum block rank."""
    blocks, remainder = divmod(rank_mass, block_cap)
    profile = {block_cap: blocks} if blocks else {}
    if remainder:
        profile[remainder] = profile.get(remainder, 0) + 1
    return profile


def bit_reblocked_bill_interval(rank_mass: int, unpaid: int, centre: Q,
                                width: int, families: Q, rank_cap: int,
                                block_cap: int, extra_rank1: int = 0):
    """Ideal integer reblocking plus fractional idle mass at the rank cap."""
    total_mass = (width - unpaid) * families + centre
    idle_mass = total_mass - rank_mass
    require(idle_mass >= 0, "bit local word exceeds the proposed coverage budget")
    profile = bit_block_profile(rank_mass, block_cap)
    lower = upper = Q(0)
    for rank, count in profile.items():
        lo, hi, _ = root_enclosure(rank, width)
        lower += count * Q(lo, SCALE)
        upper += count * Q(hi, SCALE)
    idle_lo, idle_hi, _ = root_enclosure(rank_cap, width)
    lower += idle_mass / rank_cap * Q(idle_lo, SCALE)
    upper += idle_mass / rank_cap * Q(idle_hi, SCALE)
    one_lo, one_hi, _ = root_enclosure(1, width)
    lower += extra_rank1 * Q(one_lo, SCALE)
    upper += extra_rank1 * Q(one_hi, SCALE)
    return lower / families, upper / families, profile


def ideal_bit_blocking_threshold(rank_mass: int, unpaid: int, centre: Q,
                                 width: int, families: Q, rank_cap: int):
    """Find the first strict pass and its adjacent block/extra-call limits."""
    rows = []
    for cap in range(1, rank_cap + 1):
        lower, upper, profile = bit_reblocked_bill_interval(
            rank_mass, unpaid, centre, width, families, rank_cap, cap
        )
        rows.append((cap, lower, upper, profile))
    passing = [row for row in rows if row[2] < 1]
    require(bool(passing), "no bit reblocking through the selected rank cap passes")
    cap, lower, upper, profile = passing[0]
    require(all(row[1] > 1 for row in rows if row[0] < cap),
            "a smaller integer bit block cap is not strictly rejected")
    max_extra = 0
    while True:
        next_lo, next_hi, _ = bit_reblocked_bill_interval(
            rank_mass, unpaid, centre, width, families, rank_cap, cap, max_extra + 1
        )
        if next_lo > 1:
            break
        require(next_hi < 1, "bit extra-call boundary interval is undecided")
        max_extra += 1
    accepted_lo, accepted_hi, _ = bit_reblocked_bill_interval(
        rank_mass, unpaid, centre, width, families, rank_cap, cap, max_extra
    )
    rejected_lo, _, _ = bit_reblocked_bill_interval(
        rank_mass, unpaid, centre, width, families, rank_cap, cap, max_extra + 1
    )
    return {
        "unpaid_coordinates": unpaid,
        "centre_mass": str(centre),
        "maximum_child_rank": rank_cap,
        "smallest_passing_local_block_cap": cap,
        "all_smaller_caps_fail": True,
        "local_block_profile": {str(r): n for r, n in sorted(profile.items())},
        "bill_lower": str(lower),
        "bill_upper": str(upper),
        "bill_upper_decimal": f"{float(upper):.15f}",
        "max_extra_rank1_calls": max_extra,
        "bill_with_max_extra_lower": str(accepted_lo),
        "bill_with_max_extra_upper": str(accepted_hi),
        "bill_with_next_extra_lower": str(rejected_lo),
        "scope": "zero-cost idealization: arbitrary integer reblocking of all selected local rank mass; idle mass fractional at the cap; no gathering, chronology, frame, copy, dirty-restoration, surcharge or physical costs",
    }


def local_bill_interval(word: dict[int, int], width: int, families: int, stages: int):
    per_call_families = Q(families, stages)
    lower = upper = Q(0)
    terms = []
    for rank, count in sorted(word.items()):
        lo, hi, exact = root_enclosure(rank, width)
        lower += count * Q(lo, SCALE)
        upper += count * Q(hi, SCALE)
        terms.append({
            "rank": rank,
            "count": count,
            "root_lower_numerator": str(lo),
            "root_upper_numerator": str(hi),
            "exact_root": exact,
        })
    return lower / per_call_families, upper / per_call_families, terms


def rank_mass_bill_interval(unpaid: int, centre: Q, width: int, families: int, stages: int, cap: int):
    """Most favorable moment for a fixed total rank mass and cap: put all at cap."""
    per_call_families = Q(families, stages)
    total_mass = (width - unpaid) * per_call_families + centre
    lo, hi, _ = root_enclosure(cap, width)
    lower = total_mass * Q(lo, SCALE) / (cap * per_call_families)
    upper = total_mass * Q(hi, SCALE) / (cap * per_call_families)
    return lower, upper


def first_rank_cap_below_one(unpaid: int, centre: Q, width: int, families: int, stages: int):
    """Return the first integer rank cap whose ideal rank-mass bill is < 1."""
    for cap in range(1, width):
        lower, upper = rank_mass_bill_interval(unpaid, centre, width, families, stages, cap)
        if upper < 1:
            previous = rank_mass_bill_interval(unpaid, centre, width, families, stages, cap - 1)
            require(previous[0] > 1, "rank-cap threshold is not adjacent and strict")
            return {
                "minimum_rank_cap": cap,
                "previous_rank_cap_bill_lower": str(previous[0]),
                "minimum_rank_cap_bill_upper": str(upper),
                "strict_adjacent_threshold": True,
                "allowed_by_selected_halving_guard": cap <= 51,
            }
    raise ValueError("no rank cap below the width passes the ideal moment")


def block_profile(rank_mass: int, block_cap: int) -> dict[int, int]:
    """Concavity-optimal integer partition into blocks no larger than block_cap."""
    blocks, remainder = divmod(rank_mass, block_cap)
    profile = {block_cap: blocks} if blocks else {}
    if remainder:
        profile[remainder] = profile.get(remainder, 0) + 1
    return profile


def reblocked_bill_interval(
    word: dict[int, int], unpaid: int, centre: Q, width: int,
    families: int, stages: int, idle_cap: int, block_cap: int,
    extra_rank1: int = 0,
):
    """Idealize the whole local rank mass as integer blocks plus rank-cap idle."""
    per_call_families = Q(families, stages)
    local_mass = sum(rank * count for rank, count in word.items())
    total_mass = (width - unpaid) * per_call_families + centre
    idle_mass = total_mass - local_mass
    require(idle_mass >= 0, "local word exceeds the selected coverage budget")
    profile = block_profile(local_mass, block_cap)
    lower = upper = Q(0)
    for rank, count in profile.items():
        lo, hi, _ = root_enclosure(rank, width)
        lower += count * Q(lo, SCALE)
        upper += count * Q(hi, SCALE)
    idle_lo, idle_hi, _ = root_enclosure(idle_cap, width)
    lower += idle_mass / idle_cap * Q(idle_lo, SCALE)
    upper += idle_mass / idle_cap * Q(idle_hi, SCALE)
    one_lo, one_hi, _ = root_enclosure(1, width)
    lower += extra_rank1 * Q(one_lo, SCALE)
    upper += extra_rank1 * Q(one_hi, SCALE)
    return lower / per_call_families, upper / per_call_families, profile


def ideal_blocking_threshold(word: dict[int, int], unpaid: int, centre: Q,
                             width: int, families: int, stages: int, idle_cap: int):
    """Find the smallest local block cap that passes the fully idealized bill."""
    local_mass = sum(rank * count for rank, count in word.items())
    total_mass = (width - unpaid) * Q(families, stages) + centre
    require(total_mass >= local_mass, "coverage budget cannot host the current local rank mass")
    rows = []
    passing = []
    for cap in range(1, idle_cap + 1):
        lower, upper, profile = reblocked_bill_interval(
            word, unpaid, centre, width, families, stages, idle_cap, cap
        )
        row = {
            "block_cap": cap,
            "local_block_profile": {str(r): n for r, n in sorted(profile.items())},
            "bill_lower": str(lower),
            "bill_upper": str(upper),
            "bill_upper_decimal": f"{float(upper):.15f}",
            "strictly_below_one": upper < 1,
        }
        rows.append(row)
        if upper < 1:
            passing.append(row)
    require(bool(passing), "no local block cap up to the selected rank cap passes")
    first = min(passing, key=lambda row: row["block_cap"])
    cap = first["block_cap"]
    require(all(not row["strictly_below_one"] for row in rows if row["block_cap"] < cap),
            "a smaller block cap unexpectedly passes")
    max_extra = 0
    while True:
        next_lower, next_upper, _ = reblocked_bill_interval(
            word, unpaid, centre, width, families, stages, idle_cap, cap, max_extra + 1
        )
        if next_lower > 1:
            break
        require(next_upper < 1, "extra rank-one boundary interval is undecided")
        max_extra += 1
    extra_lower, _, _ = reblocked_bill_interval(
        word, unpaid, centre, width, families, stages, idle_cap, cap, max_extra
    )
    next_lower, next_upper, _ = reblocked_bill_interval(
        word, unpaid, centre, width, families, stages, idle_cap, cap, max_extra + 1
    )
    require(extra_lower < 1 < next_lower, "extra rank-one budget boundary is not strict")
    return {
        "unpaid_coordinates": unpaid,
        "centre_mass": str(centre),
        "idle_rank_cap": idle_cap,
        "smallest_passing_local_block_cap": cap,
        "all_smaller_caps_fail": True,
        "local_block_profile": first["local_block_profile"],
        "bill_lower": first["bill_lower"],
        "bill_upper": first["bill_upper"],
        "bill_upper_decimal": first["bill_upper_decimal"],
        "max_extra_rank1_calls": max_extra,
        "bill_with_max_extra_lower": str(extra_lower),
        "bill_with_next_extra_lower": str(next_lower),
        "scope": "zero-cost idealization: arbitrary reblocking of all current local rank mass; no gathering, chronology, frame, copy, dirty-restoration or physical costs",
    }


def result_record() -> dict[str, object]:
    selected_path = ROOT / "certificates/selected-result.json"
    assembly_path = ROOT / "research/community-frontier1094-audit/ASSEMBLY.json"
    word_path = ROOT / "research/complex-local-word-ceiling/levers.py"
    selected = read_json(selected_path)
    assembly = read_json(assembly_path)
    width, families, stages, word = source_profile()
    bit_word, bit_binding = bit_profile()

    selected_kappa = str(selected["kappa"])
    require(selected_kappa == str(assembly["kappa"]), "selected record and assembly kappa differ")
    require(assembly["binding"] == "complex", "source assembly is no longer complex-bound")

    local_mass = sum(rank * count for rank, count in word.items())
    lower, upper, terms = local_bill_interval(word, width, families, stages)
    rank_cap = 51
    require(2 * rank_cap**2 < width**2 <= 2 * (rank_cap + 1) ** 2,
            "rank cap is no longer the largest rank allowed by the selected halving guard")
    # Positive control: at a=0 this local bill is exactly rank mass/(m W).
    zero_saving_bill = Q(local_mass * stages, width * families)
    require(zero_saving_bill < 1, "positive control at a=0 failed")
    require(lower > 1, "the selected local word does not exclude a=1/9")

    coverage_cases = []
    for label, unpaid, centre in (
        ("selected_coverage", 1, Q(64)),
        ("two_unpaid_centre_free", 2, Q(0)),
        ("three_unpaid_centre_free", 3, Q(0)),
        ("three_unpaid_selected_centre", 3, Q(64)),
        ("four_unpaid_selected_centre", 4, Q(64)),
    ):
        b_lo, b_hi = rank_mass_bill_interval(unpaid, centre, width, families, stages, rank_cap)
        coverage_cases.append({
            "label": label,
            "unpaid_coordinates": unpaid,
            "centre_mass": str(centre),
            "all_mass_at_rank_cap": rank_cap,
            "bill_lower": str(b_lo),
            "bill_upper": str(b_hi),
            "bill_upper_decimal": f"{float(b_hi):.15f}",
            "strictly_below_one": b_hi < 1,
        })
    rank_cap_cases = []
    for label, unpaid, centre in (
        ("selected_coverage", 1, Q(64)),
        ("one_unpaid_centre_free", 1, Q(0)),
        ("two_unpaid_centre_free", 2, Q(0)),
        ("three_unpaid_centre_free", 3, Q(0)),
        ("three_unpaid_selected_centre", 3, Q(64)),
        ("four_unpaid_selected_centre", 4, Q(64)),
    ):
        rank_cap_cases.append({
            "label": label,
            "unpaid_coordinates": unpaid,
            "centre_mass": str(centre),
            **first_rank_cap_below_one(unpaid, centre, width, families, stages),
        })
    case = {item["label"]: item for item in coverage_cases}
    require(Q(case["selected_coverage"]["bill_lower"]) > 1,
            "selected coverage does not fail even under ideal rank-cap repacking")
    require(Q(case["two_unpaid_centre_free"]["bill_lower"]) > 1,
            "two-unpaid centre-free necessity control failed")
    require(case["three_unpaid_centre_free"]["strictly_below_one"],
            "three-unpaid centre-free ideal positive control failed")
    require(Q(case["three_unpaid_selected_centre"]["bill_lower"]) > 1,
            "three-unpaid selected-centre necessity control failed")
    require(case["four_unpaid_selected_centre"]["strictly_below_one"],
            "four-unpaid selected-centre ideal positive control failed")
    cap_case = {item["label"]: item for item in rank_cap_cases}
    require(cap_case["selected_coverage"]["minimum_rank_cap"] == 70,
            "selected-law rank-cap threshold drifted")
    require(cap_case["one_unpaid_centre_free"]["minimum_rank_cap"] == 65,
            "centre-free rank-cap threshold drifted")
    require(cap_case["two_unpaid_centre_free"]["minimum_rank_cap"] == 57,
            "two-unpaid rank-cap threshold drifted")
    require(cap_case["three_unpaid_centre_free"]["minimum_rank_cap"] == 51,
            "three-unpaid rank-cap threshold drifted")
    require(cap_case["three_unpaid_selected_centre"]["minimum_rank_cap"] == 55,
            "selected-centre rank-cap threshold drifted")
    require(cap_case["four_unpaid_selected_centre"]["minimum_rank_cap"] == 48,
            "four-unpaid selected-centre rank-cap threshold drifted")
    block_cases = [
        ideal_blocking_threshold(word, 3, Q(0), width, families, stages, rank_cap),
        ideal_blocking_threshold(word, 4, Q(64), width, families, stages, rank_cap),
    ]
    require(block_cases[0]["smallest_passing_local_block_cap"] == 50
            and block_cases[0]["local_block_profile"] == {"36": 1, "50": 111}
            and block_cases[0]["max_extra_rank1_calls"] == 0,
            "three-unpaid block budget drifted")
    require(block_cases[1]["smallest_passing_local_block_cap"] == 48
            and block_cases[1]["local_block_profile"] == {"18": 1, "48": 116}
            and block_cases[1]["max_extra_rank1_calls"] == 6,
            "four-unpaid block budget drifted")

    bit_width = 64
    bit_families = Q(296, 3)
    bit_stages = 9
    bit_rank_cap = 45
    bit_mass = sum(rank * count for rank, count in bit_word.items())
    bit_lower, bit_upper, bit_terms = moment_interval(bit_word, bit_width, bit_families)
    bit_zero_saving = Q(bit_mass, 1) / (bit_width * bit_families)
    require(bit_mass == 5129 and bit_zero_saving < 1,
            "bit local mass or a=0 positive control drifted")
    require(bit_lower > 1, "the selected bit local word does not exclude a=1/9")
    bit_coverage_lower, bit_coverage_upper = bit_total_mass_bill_interval(
        1, Q(63), bit_width, bit_families, bit_rank_cap
    )
    require(bit_coverage_lower > 1,
            "selected bit coverage still passes with all mass ideally at rank 45")
    bit_blocks = [
        ideal_bit_blocking_threshold(bit_mass, 3, Q(0), bit_width, bit_families, bit_rank_cap),
        ideal_bit_blocking_threshold(bit_mass, 4, Q(63), bit_width, bit_families, bit_rank_cap),
    ]
    require(bit_blocks[0]["smallest_passing_local_block_cap"] == 42
            and bit_blocks[0]["local_block_profile"] == {"5": 1, "42": 122}
            and bit_blocks[0]["max_extra_rank1_calls"] == 8,
            "three-unpaid bit block budget drifted")
    require(bit_blocks[1]["smallest_passing_local_block_cap"] == 39
            and bit_blocks[1]["local_block_profile"] == {"20": 1, "39": 131}
            and bit_blocks[1]["max_extra_rank1_calls"] == 3,
            "four-unpaid bit block budget drifted")

    # At a=1/9, kappa=a/(1+a)=1/10.  The retained outer transfer has strict
    # reservations, so any kappa>1/10 needs a primitive a>1/9.
    return {
        "status": "PASS_KAPPA01_TWO_SIDED_TARGET_SCREEN",
        "scope": "selected complex and bit local words plus independent ideal coverage/reblocking relaxations; no realizable replacement supplier",
        "target": {"kappa": "1/10", "primitive_saving": "1/9"},
        "selected": {
            "kappa": selected_kappa,
            "binding": assembly["binding"],
            "selected_record_sha256": sha256(selected_path),
            "assembly_sha256": sha256(assembly_path),
            "local_word_source_sha256": sha256(word_path),
            "bit_binding": bit_binding,
        },
        "model": {
            "width": width,
            "live_families_per_replica": families,
            "stages": stages,
            "live_families_per_call": f"{families}/{stages}",
            "local_profile": {str(r): n for r, n in sorted(word.items())},
            "local_rank_mass": local_mass,
            "idle_mass_assumed": 0,
            "centre_charge_assumed": 0,
            "maximum_child_rank": rank_cap,
            "root_scale": str(SCALE),
        },
        "bit_model": {
            "width": bit_width,
            "live_families_per_call": str(bit_families),
            "stages": bit_stages,
            "local_profile": {str(r): n for r, n in sorted(bit_word.items())},
            "local_rank_mass": bit_mass,
            "idle_mass_assumed_for_local_floor": 0,
            "surcharge_assumed_for_local_floor": 0,
            "copy_charge": 63,
            "maximum_child_rank": bit_rank_cap,
            "root_scale": str(SCALE),
        },
        "certificate": {
            "rank_terms": terms,
            "bill_lower": str(lower),
            "bill_upper": str(upper),
            "bill_lower_decimal": f"{float(lower):.15f}",
            "bill_upper_decimal": f"{float(upper):.15f}",
            "margin_lower": str(lower - 1),
            "positive_control_a_zero_bill": str(zero_saving_bill),
            "strict_rejection": lower > 1,
            "coverage_relaxations": coverage_cases,
            "rank_cap_thresholds": rank_cap_cases,
            "ideal_local_blocking": block_cases,
            "necessary_unpaid_coordinates_at_target": {
                "with_centre_fully_removed": 3,
                "with_selected_centre_charge_64": 4,
                "scope": "uniform coverage law, fixed width 73, nine stages, and rank cap 51; idealized rank-mass distribution only",
            },
            "bit_local_word": {
                "rank_terms": bit_terms,
                "bill_lower": str(bit_lower),
                "bill_upper": str(bit_upper),
                "bill_lower_decimal": f"{float(bit_lower):.15f}",
                "bill_upper_decimal": f"{float(bit_upper):.15f}",
                "margin_lower": str(bit_lower - 1),
                "strict_rejection": bit_lower > 1,
                "positive_control_a_zero_bill": str(bit_zero_saving),
                "surcharge_omitted": True,
            },
            "bit_selected_coverage": {
                "unpaid_coordinates": 1,
                "centre_mass": "63",
                "all_mass_at_rank_cap": bit_rank_cap,
                "bill_lower": str(bit_coverage_lower),
                "bill_upper": str(bit_coverage_upper),
                "bill_upper_decimal": f"{float(bit_coverage_upper):.15f}",
                "strict_rejection": bit_coverage_lower > 1,
            },
            "bit_ideal_local_blocking": bit_blocks,
        },
        "interpretation": (
            "Both selected local words alone cost more than one normalized unit at a=1/9, "
            "even with all idle, hosting, centre and surcharge costs omitted. The selected "
            "coverage laws also fail under separate ideal rank-cap relaxations. Passing "
            "reblocking cases are zero-overhead necessary budgets for each supplier, not "
            "decoders or a joint construction."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    record = result_record()
    rendered = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.write_text(rendered, encoding="utf-8")
    else:
        expected = read_json(PACKAGE / "RESULT.json")
        require(record == expected, "RESULT.json differs from exact replay")
    print("PASS_KAPPA01_TWO_SIDED_TARGET_SCREEN complex_local_lower="
          + record["certificate"]["bill_lower_decimal"]
          + " bit_local_lower="
          + record["certificate"]["bit_local_word"]["bill_lower_decimal"])


if __name__ == "__main__":
    main()
