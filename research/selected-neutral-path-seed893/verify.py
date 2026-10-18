#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify one explicit neutral-then-improving path in the selected owner map.

Prepared by OpenAI Codex with substantial OpenAI assistance. This package
reuses, pins and credits the selected-map owner audit and exact moment engine;
it does not replay or admit the complete multiplication supplier.
"""
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
NEUTRAL_INDEX = 47270
STRICT_INDEX = 34306
NEUTRAL_SOURCE = (1, 14, 57)
NEUTRAL_DEST = (13, 15, 14)
STRICT_SOURCE = (11, 8, 103)
STRICT_DEST = NEUTRAL_SOURCE
GRID = Q(1, 10**15)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def check_pins():
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    require(manifest["base_commit"] == BASE, "base pin mismatch")
    for row in manifest["files"]:
        path = row["path"]
        blob = subprocess.check_output(
            ["git", "rev-parse", f"{BASE}:{path}"], cwd=ROOT, text=True
        ).strip()
        raw = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)
        require(blob == row["git_blob"], f"Git blob drift: {path}")
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], f"SHA256 drift: {path}")
        if row["usage"] == "input":
            require((ROOT / path).read_bytes() == raw, f"working input drift: {path}")
    selected = json.loads((ROOT / "certificates/selected-result.json").read_bytes())
    raw = (ROOT / "certificates/selected-result.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SELECTED_SHA256, "selected record drift")
    require(selected["kappa"] == "836330098538459/500000000000000000",
            "selected kappa drift")
    return manifest


def load_fixture():
    one = load_module("pinned_single_relocation", ROOT / "research/frontier1094-single-relocation/verify.py")
    ceiling = load_module("pinned_complex_ceiling", ROOT / "research/complex-local-word-ceiling/ceiling.py")
    f = one.fixture(ROOT)
    return one, ceiling, f


def idle_hist(model, one):
    return Counter({r: len(keys) for r, keys in model.by_remainder.items() if r > 0})


def profile_moment(a, idle, local, ceiling):
    """Certified whole supplier moment per 896/9 families per call.

    The selected local profile is charged 144 times, and the complete idle
    histogram is charged once. Outward rational intervals come from the
    pinned complex-local-word-ceiling child_cost implementation.
    """
    lower = upper = Q(0)
    for rank, count in local.items():
        lo, hi = ceiling.child_cost(rank, 73, a)
        lower += 144 * count * lo
        upper += 144 * count * hi
    for rank, count in idle.items():
        lo, hi = ceiling.child_cost(rank, 73, a)
        lower += count * lo
        upper += count * hi
    denominator = 144 * Q(896, 9)
    return lower / denominator, upper / denominator


def root_bracket(idle, local, ceiling):
    lo, hi = Q(0), Q(1, 100)
    require(profile_moment(lo, idle, local, ceiling)[1] < 1, "zero-saving moment not below one")
    require(profile_moment(hi, idle, local, ceiling)[0] > 1, "root search upper bound too small")
    while hi - lo > GRID:
        mid = (lo + hi) / 2
        lower, upper = profile_moment(mid, idle, local, ceiling)
        if upper < 1:
            lo = mid
        elif lower > 1:
            hi = mid
        else:
            raise ValueError("outward interval did not separate at the requested grid point")
    require(profile_moment(lo, idle, local, ceiling)[1] < 1, "lower endpoint not certified")
    require(profile_moment(hi, idle, local, ceiling)[0] > 1, "upper endpoint not certified")
    return lo, hi


def fraction_pair(value):
    return [str(value[0]), str(value[1])]


def build():
    one, ceiling, f = load_fixture()
    base = f["model"]
    neutral_role = base.roles[NEUTRAL_INDEX]
    strict_role = base.roles[STRICT_INDEX]
    require((neutral_role["stage"], neutral_role["replica"], neutral_role["helper"])
            == (7, 2, 230), "neutral role identity drift")
    require((strict_role["stage"], strict_role["replica"], strict_role["helper"])
            == (1, 15, 226), "strict role identity drift")
    require(one.bin_key(neutral_role) == NEUTRAL_SOURCE, "neutral source drift")
    require(one.bin_key(strict_role) == STRICT_SOURCE, "strict source drift")
    require(neutral_role["width"] == strict_role["width"] == 7, "role width drift")

    initial_idle = idle_hist(base, one)
    require(initial_idle == Counter({1: 2276, 3: 377, 7: 7, 48: 4866}),
            "selected idle profile drift")
    first = one.relocate(base, NEUTRAL_INDEX, NEUTRAL_DEST)
    neutral_idle = idle_hist(first, one)
    require(neutral_idle == initial_idle, "first move was not moment neutral")
    require(first.bins[NEUTRAL_SOURCE].remainder == 7
            and first.bins[NEUTRAL_DEST].remainder == 0,
            "first remainder exchange mismatch")

    # The second move is window/family legal from the original map, but its
    # destination has zero free rank and therefore cannot be used until step 1.
    require(base.rejection(strict_role, STRICT_DEST) is None,
            "strict destination event/family rule changed")
    require(base.bins[STRICT_DEST].remainder == 0, "expected original destination to be full")
    try:
        one.relocate(base, STRICT_INDEX, STRICT_DEST)
    except ValueError as exc:
        require("destination capacity" in str(exc), "direct-move negative control failed incorrectly")
    else:
        raise ValueError("direct strict move unexpectedly fit before the neutral move")

    require(first.rejection(first.roles[STRICT_INDEX], STRICT_DEST) is None,
            "second move is not legal after the neutral step")
    final = one.relocate(first, STRICT_INDEX, STRICT_DEST)
    final_idle = idle_hist(final, one)
    expected_idle = Counter({1: 2275, 3: 377, 7: 6, 8: 1, 48: 4866})
    require(final_idle == expected_idle, "final idle histogram mismatch")

    # Retained baseline and final full owner ledgers: call/time order, all roles,
    # source-event windows, active data pair, physical family uniqueness,
    # occupied prefixes, idle histogram, rank mass and halving guard.
    baseline_audit = f["baseline"]
    final_audit = f["audit"].audit(
        base.geo, f["widths"], f["local"], final.roles, f["plan"], final_idle, 16
    )
    require(final_audit["rank_mass"] == baseline_audit["rank_mass"] == 1041408,
            "rank mass changed")
    require(final_audit["deficit"] == baseline_audit["deficit"] == 5120,
            "rank deficit changed")
    require(final_audit["roles"] == 69120 and final_audit["windows"] == 288,
            "owner audit coverage mismatch")
    require(one.compare(0, 7, 7) == 0, "neutral majorization sign mismatch")
    require(one.compare(1, 7, 7) == -1, "strict majorization sign mismatch")

    old_root = root_bracket(initial_idle, f["local"], ceiling)
    new_root = root_bracket(final_idle, f["local"], ceiling)
    require(new_root[0] > old_root[1], "new paid moment root is not strictly higher")
    cap = ceiling.ceiling(f["local"], 73, 896, 9, 64)
    bit_saving = Q(1733427039589844234749, 10**24)
    require(new_root[1] < bit_saving, "complex supplier no longer binds in the retained comparison")
    endpoint_ratio = (new_root[0] / cap[1], new_root[1] / cap[0])
    gap_closed = (
        (new_root[0] - old_root[1]) / (cap[1] - old_root[0]),
        (new_root[1] - old_root[0]) / (cap[0] - old_root[1]),
    )
    return {
        "schema_version": 1,
        "status": "PASS_SELECTED_NEUTRAL_PATH_WITNESS",
        "base_commit": BASE,
        "selected_record_sha256": SELECTED_SHA256,
        "selected_kappa_unchanged": "836330098538459/500000000000000000",
        "construction": {
            "path_length": 2,
            "role_moves": [
                {
                    "role_index": NEUTRAL_INDEX,
                    "role": [7, 2, 230],
                    "time": 98,
                    "width": 7,
                    "source": list(NEUTRAL_SOURCE),
                    "destination": list(NEUTRAL_DEST),
                    "source_event_position": 268,
                    "destination_window": [255, 430],
                    "remainders_before_after": [[0, 7], [7, 0]],
                    "moment_change": "exactly zero",
                },
                {
                    "role_index": STRICT_INDEX,
                    "role": [1, 15, 226],
                    "time": 71,
                    "width": 7,
                    "source": list(STRICT_SOURCE),
                    "destination": list(STRICT_DEST),
                    "source_event_position": 181,
                    "destination_window": [92, 272],
                    "remainders_before_after": [[1, 7], [8, 0]],
                    "moment_change": "strict decrease for every real 0 < a < 1",
                },
            ],
            "why_sequential": "The second role's landing is source-event and family legal initially, but its destination has remainder 0; after the neutral move it has remainder 7 and accepts the width-7 role.",
            "majorization": {
                "neutral_pair": "(0,7) -> (7,0)",
                "strict_pair": "(1,7) -> (8,0)",
                "proof": "For p=1-a in (0,1), t^p is strictly concave. The equal-sum pair (8,0) strictly majorizes (7,1), so 8^p+0^p < 7^p+1^p. The first step only permutes (0,7).",
            },
        },
        "owner_audit": {
            "baseline": {k: baseline_audit[k] for k in ("roles", "windows", "rank_mass", "deficit", "cross_replica_roles")},
            "final": {k: final_audit[k] for k in ("roles", "windows", "rank_mass", "deficit", "cross_replica_roles")},
            "all_owner_rules_replayed": True,
            "inherited_mutation_controls": len(f["owner_controls"]),
        },
        "idle_profile_before": dict(sorted(initial_idle.items())),
        "idle_profile_after": dict(sorted(final_idle.items())),
        "pricing": {
            "local_profile_per_call": dict(sorted(f["local"].items())),
            "calls": 144,
            "families_per_call": "896/9",
            "moment_root_before": fraction_pair(old_root),
            "moment_root_after": fraction_pair(new_root),
            "root_gain_certified_lower": str(new_root[0] - old_root[1]),
            "supplier_comparison": {
                "complex_before_endpoint": fraction_pair(old_root),
                "complex_after_endpoint": fraction_pair(new_root),
                "bit_endpoint_unchanged": str(bit_saving),
                "bit_minus_complex_after_lower": str(bit_saving - new_root[1]),
                "binding_primitive_after": "complex",
                "source": "Selected-record research baseline exact supplier arithmetic; bit word and all its charges are unchanged.",
            },
            "fixed_word_packing_cap": fraction_pair(cap),
            "candidate_endpoint_fraction_of_cap": fraction_pair(endpoint_ratio),
            "remaining_cap_gap_closed_fraction": fraction_pair(gap_closed),
            "method": "Exact rational child-cost intervals with outward rounding at 2^-256 and bisection to a 10^-15 grid.",
        },
        "interpretation": {
            "result": "A concrete legal two-step owner-map packing improvement, conditional on the retained local-word and coverage model.",
            "new_supplier_or_kappa": False,
            "full_source_rebuild_controller_invoice_or_selected_replay": False,
            "not_claimed": ["complete two-step census", "global packing optimum", "supplier admission", "new selected kappa", "multiplication theorem change"],
        },
    }


def canonical(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def main():
    check_pins()
    result = canonical(build())
    if "--write" in sys.argv[1:]:
        (HERE / "CERTIFICATE.json").write_bytes(result)
    else:
        require((HERE / "CERTIFICATE.json").read_bytes() == result,
                "certificate differs; regenerate with --write")
    print("PASS_SELECTED_NEUTRAL_PATH_WITNESS path=neutral_then_strict two_role_map_audit=PASS new_kappa=NO")


if __name__ == "__main__":
    main()
