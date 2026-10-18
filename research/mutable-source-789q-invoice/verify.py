#!/usr/bin/env python3
"""Exact 7/8/9-query invoices under the PR1898 path-lowered class. Wentao Li + AI, Apache-2.0."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from model import (  # noqa: E402
    check_identity,
    four_x_ten_q,
    invoice,
    min_even_subset_R,
    minimum_word_6q,
    path_X,
    path_word,
    rank_increments,
)
CERT_PATH = HERE / "CERTIFICATE.json"
CHAMPION_7 = (0, 1, 2, 6, 12, 24, 16, 0)


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def enumerate_R_census(slot_count_nonzero: int) -> dict:
    """Exhaust all distinct nonzero slot sets; return min R, full attainable spectrum, witnesses."""
    best = None
    witnesses = []
    histogram: Counter = Counter()
    covering = 0
    for nonzero in combinations(range(1, 32), slot_count_nonzero):
        slots = (0,) + nonzero
        total = min_even_subset_R(slots)
        if total is None:
            continue
        covering += 1
        histogram[total] += 1
        if best is None or total < best:
            best = total
            witnesses = [slots]
        elif total == best:
            witnesses.append(slots)
    need(best is not None, "no covering slot set")
    attainable = sorted(histogram)
    return {
        "min_R": best,
        "witness_count": len(witnesses),
        "first_witness": list(witnesses[0]),
        "covering_sets": covering,
        "attainable_R": attainable,
        "histogram": {str(r): histogram[r] for r in attainable},
    }


def enumerate_min_R(slot_count_nonzero: int) -> dict:
    """Exhaust all distinct nonzero slot sets of the given size; return min R and witnesses."""
    census = enumerate_R_census(slot_count_nonzero)
    return {
        "min_R": census["min_R"],
        "witness_count": census["witness_count"],
        "first_witness": census["first_witness"],
    }


def min_path_X_for_slots(slots: tuple[int, ...], stop_below: int | None = None) -> int | None:
    """Minimum path-local X over full-rank orders of ``slots`` starting at 0.

    If ``stop_below`` is set, return as soon as a cost strictly below that bound is found.
    """
    need(slots[0] == 0, "slots must start at 0")
    rest = list(slots[1:])
    best = None
    for order_rest in permutations(rest):
        order = (0,) + order_rest
        closed = order + (0,)
        if rank_increments(closed) < 5:
            continue
        cost = path_X(closed)
        if best is None or cost < best:
            best = cost
            if stop_below is not None and best < stop_below:
                return best
    return best


def enumerate_min_X_among_R(target_R: int, nonzero: int = 6) -> dict:
    """Among distinct slot sets with min even-subset R == target_R, find min full-rank path X."""
    # Prove no schedule beats the known champion X=6, and count the X=6 layer.
    covering = 0
    below = 0
    at_champion = 0
    for nonzero_slots in combinations(range(1, 32), nonzero):
        slots = (0,) + nonzero_slots
        if min_even_subset_R(slots) != target_R:
            continue
        covering += 1
        cost = min_path_X_for_slots(slots, stop_below=6)
        if cost is None:
            continue
        if cost < 6:
            below += 1
        elif cost == 6:
            at_champion += 1
    need(below == 0, f"found {below} R={target_R} sets with path X<6")
    need(at_champion > 0, "no R-set attains X=6")
    need(rank_increments(CHAMPION_7) == 5, "champion rank")
    need(path_X(CHAMPION_7) == 6, "champion X")
    need(min_even_subset_R(CHAMPION_7[:-1]) == target_R, "champion R")
    return {
        "target_R": target_R,
        "covering_sets": covering,
        "min_X": 6,
        "sets_with_X_eq_6": at_champion,
        "sets_with_X_below_6": below,
        "champion_path": list(CHAMPION_7),
    }


def build_certificate() -> dict:
    word6 = minimum_word_6q()
    word10 = four_x_ten_q()
    inv6 = invoice(word6)
    inv10 = invoice(word10)
    need(inv6["tariff"] == 436 and inv6["Q"] == 6 and inv6["R"] == 96 and inv6["X"] == 8, "6Q comparator")
    need(inv10["tariff"] == 512 and inv10["Q"] == 10 and inv10["R"] == 62 and inv10["X"] == 4, "10Q comparator")

    # Full even-subset R census: certify attainable R spectrum (not only min R).
    # Under tariff 38Q+2R+2X, beating 436 at Q=7 needs R+X<85; exact min 442 needs R+X>=88.
    census7 = enumerate_R_census(6)
    need(census7["min_R"] == 82, "unexpected Q=7 min R")
    need(census7["attainable_R"] == [82, 88], f"unexpected Q=7 R spectrum {census7['attainable_R']}")
    need(census7["histogram"] == {"82": 97216, "88": 486080}, f"unexpected Q=7 R histogram {census7['histogram']}")
    need(
        all(r not in range(83, 88) for r in census7["attainable_R"]),
        "intermediate R in {83..87} would reopen low-X undercut of 436",
    )
    r7 = {
        "min_R": census7["min_R"],
        "witness_count": census7["witness_count"],
        "first_witness": census7["first_witness"],
    }
    x7 = enumerate_min_X_among_R(82, 6)
    need(x7["min_X"] == 6 and x7["sets_with_X_below_6"] == 0, "unexpected Q=7 min X")
    need(x7["covering_sets"] == census7["histogram"]["82"], "R=82 covering count mismatch")

    word7 = path_word(CHAMPION_7)
    counts7 = check_identity(word7)
    inv7 = invoice(word7)
    need(dict(counts7) == {"Q": 7, "R": 82, "X": 6}, f"champion counts {counts7}")
    need(inv7["tariff"] == 442, f"champion tariff {inv7}")

    # Machine-checked tariff floor from the certified spectrum + min-X layer.
    # R=82 with X>=6 => R+X>=88 => tariff>=442; R=88 with X>=0 => tariff>=442.
    r82_floor = 38 * 7 + 2 * 82 + 2 * x7["min_X"]
    r88_floor = 38 * 7 + 2 * 88 + 2 * 0
    need(r82_floor == 442 and r88_floor == 442, "spectrum floors must both equal 442")
    need(inv7["tariff"] == r82_floor, "champion must attain the spectrum floor")
    need(r82_floor > inv6["tariff"] and r88_floor > inv6["tariff"], "7Q spectrum floors must not beat 6Q")

    r8 = enumerate_min_R(7)
    need(r8["min_R"] == 74, "unexpected Q=8 min R among distinct slots")
    floor8 = 38 * 8 + 2 * r8["min_R"]  # X >= 0
    floor9 = 38 * 9 + 2 * 62  # R >= 62 for 31 masks

    need(inv7["tariff"] > inv6["tariff"], "7Q should not beat 6Q")
    need(floor8 > inv6["tariff"], "8Q floor should not beat 6Q")
    need(floor9 > inv6["tariff"], "9Q floor should not beat 6Q")

    return {
        "schema_version": 1,
        "status": "PASS_MUTABLE_SOURCE_789Q_INVOICE",
        "scope": (
            "Path-lowered even-subset schedules on connector prefixes for the five-source "
            "common-B mutable-source connector; complete-call tariff (b,a,x)=(38,2,2) from PR1898."
        ),
        "comparators": {
            "six_query_endpoint": inv6,
            "ten_query_four_X": inv10,
        },
        "Q7": {
            "R_spectrum_distinct_slots": {
                "covering_sets": census7["covering_sets"],
                "attainable_R": census7["attainable_R"],
                "histogram": census7["histogram"],
                "intermediate_R_83_to_87_count": 0,
                "argument": (
                    "Exhaustive even-subset R over all C(31,6) distinct nonzero 6-slot sets; "
                    "covering sets attain only R in {82,88}. Under tariff 38Q+2R+2X, beating "
                    "436 requires R+X<85, so excluded intermediate R in {83..87} with low X "
                    "cannot undercut; R=88 forces tariff>=442 even at X=0."
                ),
            },
            "min_R_distinct_slots": r7,
            "min_X_among_min_R": x7,
            "tariff_floor_from_spectrum": {
                "beat_436_requires_R_plus_X_lt": 85,
                "exact_min_requires_R_plus_X_ge": 88,
                "R82_min_X": x7["min_X"],
                "R82_tariff_floor": r82_floor,
                "R88_X_ge_0_tariff_floor": r88_floor,
                "min_tariff": 442,
            },
            "champion_invoice": inv7,
            "beats_six_query": False,
        },
        "Q8": {
            "min_R_distinct_slots": r8,
            "tariff_lower_bound_X_ge_0": floor8,
            "beats_six_query": False,
        },
        "Q9": {
            "R_lower_bound": 62,
            "tariff_lower_bound": floor9,
            "beats_six_query": False,
            "argument": "Each of 31 masks needs an even nonempty readout set, so R >= 62.",
        },
        "conclusion": (
            "Under this schedule class and abstract tariff, no path-lowered even-subset word "
            "with Q in {7,8,9} beats the sharp six-query endpoint tariff 436. Q=7 exact "
            "minimum 442 follows from the certified R spectrum {82,88} plus min X=6 on R=82."
        ),
        "new_kappa": False,
    }


def check_pins():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for entry in sources.get("files", []):
        if entry.get("usage") != "input":
            continue
        path = ROOT / entry["path"]
        need(path.is_file(), f"missing input {entry['path']}")
        need(sha256(path) == entry["sha256"], f"sha256 drift {entry['path']}")


def build_quick_checks() -> dict:
    """Champion + comparator invoices without the long R/X censuses."""
    word6 = minimum_word_6q()
    word10 = four_x_ten_q()
    inv6 = invoice(word6)
    inv10 = invoice(word10)
    need(inv6["tariff"] == 436, "6Q comparator")
    need(inv10["tariff"] == 512, "10Q comparator")
    word7 = path_word(CHAMPION_7)
    counts7 = check_identity(word7)
    inv7 = invoice(word7)
    need(dict(counts7) == {"Q": 7, "R": 82, "X": 6}, f"champion counts {counts7}")
    need(inv7["tariff"] == 442, f"champion tariff {inv7}")
    need(path_X(CHAMPION_7) == 6 and rank_increments(CHAMPION_7) == 5, "champion path")
    need(min_even_subset_R(CHAMPION_7[:-1]) == 82, "champion R")
    return {
        "status": "PASS_MUTABLE_SOURCE_789Q_QUICK",
        "Q6": inv6["tariff"],
        "Q7": inv7["tariff"],
        "Q8_floor": 38 * 8 + 2 * 74,
        "Q9_floor": 38 * 9 + 2 * 62,
    }


def main(argv: list[str]) -> int:
    write = "--write" in argv
    quick = "--quick" in argv
    check_pins()
    if quick and not write:
        need(CERT_PATH.is_file(), "missing CERTIFICATE.json")
        cert = json.loads(CERT_PATH.read_text())
        need(cert.get("status") == "PASS_MUTABLE_SOURCE_789Q_INVOICE", "bad certificate status")
        quick_payload = build_quick_checks()
        need(cert["Q7"]["champion_invoice"]["tariff"] == quick_payload["Q7"], "cert/quick Q7")
        need(cert["Q8"]["tariff_lower_bound_X_ge_0"] == quick_payload["Q8_floor"], "cert/quick Q8")
        need(cert["Q9"]["tariff_lower_bound"] == quick_payload["Q9_floor"], "cert/quick Q9")
        need(cert["Q7"]["min_X_among_min_R"]["min_X"] == 6, "cert min X")
        need(cert["Q7"]["min_X_among_min_R"]["sets_with_X_below_6"] == 0, "cert X below")
        spectrum = cert["Q7"]["R_spectrum_distinct_slots"]
        need(spectrum["attainable_R"] == [82, 88], "cert R spectrum")
        need(spectrum["histogram"] == {"82": 97216, "88": 486080}, "cert R histogram")
        need(spectrum["intermediate_R_83_to_87_count"] == 0, "cert intermediate R")
        floor = cert["Q7"]["tariff_floor_from_spectrum"]
        need(floor["min_tariff"] == 442, "cert spectrum tariff floor")
        need(floor["R82_tariff_floor"] == 442 and floor["R88_X_ge_0_tariff_floor"] == 442, "cert layer floors")
        print(
            quick_payload["status"],
            f"Q6={quick_payload['Q6']}",
            f"Q7={quick_payload['Q7']}",
            f"Q8_floor={quick_payload['Q8_floor']}",
            f"Q9_floor={quick_payload['Q9_floor']}",
            "no_new_kappa",
        )
        return 0

    payload = build_certificate()
    text = json.dumps(payload, indent=2) + "\n"
    if write:
        CERT_PATH.write_text(text)
    else:
        need(CERT_PATH.is_file(), "missing CERTIFICATE.json; pass --write once")
        decoder = json.JSONDecoder()
        raw = CERT_PATH.read_text()
        obj, idx = decoder.raw_decode(raw)
        need(idx == len(raw.rstrip("\n")) or raw[idx:].strip() == "", "trailing junk in certificate")
        need(obj == payload, "CERTIFICATE.json drift versus fresh census")
    print(
        payload["status"],
        f"Q6={payload['comparators']['six_query_endpoint']['tariff']}",
        f"Q7={payload['Q7']['champion_invoice']['tariff']}",
        f"Q8_floor={payload['Q8']['tariff_lower_bound_X_ge_0']}",
        f"Q9_floor={payload['Q9']['tariff_lower_bound']}",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
