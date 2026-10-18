#!/usr/bin/env python3
"""Exact F_2 port-frame census and optimistic selected-profile screen."""
import gzip
import hashlib
import importlib.util
import json
from collections import Counter
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD_PATH = (
    "research/complex-sw4-frame8/vendor/main/research/community-k492-audit/"
    "pr622/replay/baseline558/complex-global/base/split-centres/CANONICAL-WORD.json.gz"
)
TEMPLATE_PATH = "research/gauge44-slots-t16/evidence/global/GLOBAL-TEMPLATE.json.gz"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_gzip_json(path):
    return json.loads(gzip.decompress((ROOT / path).read_bytes()))


def rank(vectors):
    """Rank of bit-packed vectors over F_2."""
    pivots = {}
    for x in vectors:
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return len(pivots)


def shear(x, i, j):
    """Apply I + E_ij to a column vector, with i the destination bit."""
    return x ^ (((x >> j) & 1) << i)


def frame_census(word, template):
    require(len(word["frames"]) == 999, "canonical word frame inventory changed")
    require(len(word["start"]) == 728 and len(word["final"]) == 728, "word endpoint lengths changed")
    require(len(word["ports"]) == 112, "port count changed")

    calls = [
        (i, c) for i, c in enumerate(template["calls"])
        if c.get("pair") == 0 and c.get("replica") == 0 and c.get("stage") in (0, 1)
    ]
    require([(i, c.get("orientation"), c.get("time")) for i, c in calls] == [
        (0, "forward", 0), (2, "backward", 2)
    ], "pair-0 consecutive call identity changed")
    events = [
        (i, e) for i, e in enumerate(template["execution_schedule"])
        if e.get("kind") == "local_cover_sweep" and e.get("replica") == 0 and e.get("stage") in (0, 1)
    ]
    require([(i, e.get("stage"), e.get("time")) for i, e in events] == [
        (0, 0, 0), (2, 1, 2)
    ], "pair-0 call schedule changed")

    universe = [(i, j) for i in range(9) for j in range(9) if i != j]
    require(len(universe) == 72, "directed transvection inventory is not 72")
    for i, j in universe:
        for v in range(512):
            require(shear(shear(v, i, j), i, j) == v,
                    f"T({i},{j}) is not an involution on F_2^9")
    common = set(universe)
    per_port = []
    port_candidates = []
    baseline_dimensions = set()
    for p in range(112):
        out_frame_id = word["final"][112 + p]
        in_frame_id = word["start"][p]
        out_basis = word["frames"][out_frame_id]
        in_basis = word["frames"][in_frame_id]
        require(len(out_basis) == 8 and rank(out_basis) == 8, f"port {p}: output plane is not rank 8")
        require(len(in_basis) == 1 and rank(in_basis) == 1, f"port {p}: input is not a rank-one line")
        require(all(0 < x < 512 for x in out_basis + in_basis), f"port {p}: vector outside F_2^9")
        u = in_basis[0]
        require(rank(out_basis + [u]) == 9, f"port {p}: baseline frames unexpectedly intersect")
        baseline_dimensions.add((rank(out_basis), rank(in_basis), rank(out_basis + [u])))

        accepted = set()
        for i, j in universe:
            moved = [shear(x, i, j) for x in out_basis]
            require(rank(moved) == 8, f"port {p}, T({i},{j}): shear lost invertibility")
            if rank(moved + [u]) == 8:
                accepted.add((i, j))
        require(accepted, f"port {p}: no coordinate transvection aligns the line")
        per_port.append(accepted)
        port_candidates.append({
            "port": p,
            "output_frame_id": out_frame_id,
            "input_frame_id": in_frame_id,
            "candidates": [list(pair) for pair in sorted(accepted)],
        })
        common &= accepted

    counts = sorted({len(x) for x in per_port})
    count_frequency = dict(sorted(Counter(map(len, per_port)).items()))
    total = sum(map(len, per_port))
    require(baseline_dimensions == {(8, 1, 9)}, "baseline dimension/intersection census changed")
    require(counts == [6, 42] and count_frequency == {6: 77, 42: 35} and total == 1932,
            "per-port transvection census changed")
    require(not common, "one directed transvection unexpectedly works at every port")
    require((0, 1) in per_port[0], "positive control T(0,1) no longer aligns port 0")
    rejected = next(pair for pair in universe if pair not in per_port[0])
    require(rejected not in per_port[0], "negative control unexpectedly accepted")

    return dict(
        status="PASS_PORTWISE_F2_TRANSVECTION_CENSUS",
        ports=112,
        directed_transvections_per_port=72,
        baseline_dimensions={"output_plane": 8, "input_line": 1, "sum": 9},
        per_port_candidate_counts=counts,
        candidate_count_frequency={str(k): v for k, v in count_frequency.items()},
        candidate_port_incidences=total,
        common_transvections=[],
        port_candidates=port_candidates,
        controls={"port0_T_0_1": "accepted", "port0_first_rejected": list(rejected),
                  "all_accepted_maps_involutions": True},
        interpretation="A port-specific coordinate shear aligns each tested frame pair; no one shear aligns all ports.",
    )


def selected_profile_screen():
    rec = json.loads((ROOT / "certificates/selected-result.json").read_text())
    require(hashlib.sha256((ROOT / "certificates/selected-result.json").read_bytes()).hexdigest()
            == "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
            "selected record pin changed")
    asm = json.loads((ROOT / rec["certificate"]).read_text())
    ind = json.loads((ROOT / "research/community-frontier1094-audit/INDEPENDENT1094.json").read_text())
    H = {int(r): n for r, n in asm["complex_profile"].items()}
    require(H == {int(r): n for r, n in ind["owner"]["profile"].items()}, "selected profiles disagree")
    idle = {int(r): n for r, n in ind["owner"]["idle"].items()}
    calls = ind["price"]["calls"]
    require(calls == 144 and ind["price"]["live"] == 14336, "selected schedule price changed")
    local = {}
    for r in sorted(set(H) | set(idle)):
        k = H.get(r, 0) - idle.get(r, 0)
        require(k >= 0 and k % calls == 0, f"rank {r}: local paid count is not uniform per call")
        if k:
            local[r] = Q(k, calls)
    expected = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
    require(local == {r: Q(n) for r, n in expected.items()}, "selected local profile changed")

    spec = importlib.util.spec_from_file_location(
        "pinned_complex_local_ceiling", ROOT / "research/complex-local-word-ceiling/ceiling.py")
    C = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(C)
    base = C.ceiling(local, 73, 2 * 4 * 112, 9, 64)

    # Optimistic accounting hypothesis only: 112 shears are paid, while 224
    # rank-one boundary transitions disappear. Thus the paid rank-one profile
    # falls by 112 / 144 = 7/9 per call. No scalar endpoint or supplier replay
    # is inferred from the frame census.
    paid = dict(local)
    paid[1] -= Q(112, calls)
    require(paid[1] == Q(21701, 9), "rank-one shear invoice changed")
    charged = C.ceiling(paid, 73, 2 * 4 * 112, 9, 64)

    # Cost-direction control: omitting all 112 shear charges would remove 224
    # rank-one calls, but does not improve this lower-bound ceiling either.
    undercharged = dict(local)
    undercharged[1] -= Q(224, calls)
    free_shear = C.ceiling(undercharged, 73, 2 * 4 * 112, 9, 64)
    require(free_shear[1] > charged[1], "undercharging did not worsen the ceiling as expected")

    require(base == (Q(52814190909, 31250000000000), Q(1690054109089, 10**15)),
            "baseline ceiling interval changed")
    require(charged == (Q(211287502113, 125000000000000), Q(338060003381, 200000000000000)),
            "charged optimistic ceiling interval changed")
    require(charged[1] > base[1], "paid shear profile unexpectedly improves this ceiling")
    inflation = Q(100) * (charged[1] / base[1] - 1)
    require(inflation == Q(24590781600, 1690054109089), "relative ceiling comparison changed")
    return dict(
        status="PASS_OPTIMISTIC_PROFILE_SCREEN",
        selected_local_profile={str(r): str(n) for r, n in local.items()},
        accounting_hypothesis={"ports": 112, "paid_rank_one_shears": 112,
                               "assumed_removed_rank_one_transitions": 224,
                               "net_rank_one_change_across_calls": -112,
                               "calls": calls, "per_call_rank_one_change": str(-Q(112, calls))},
        baseline_a_ceiling=[str(x) for x in base],
        charged_optimistic_a_ceiling=[str(x) for x in charged],
        relative_ceiling_increase_percent=str(inflation),
        conclusion="The most favorable profile-only invoice raises the selected ceiling; it does not improve it.",
        controls={"free_shear_undercharge_raises_ceiling_further": True},
        unverified=["full scalar endpoint preservation", "transition deletion at both calls",
                    "owner and schedule legality after frame changes", "supplier integration", "new kappa"],
    )


def main():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    checked = []
    for item in pins["files"]:
        if item["usage"] == "input":
            actual = hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest()
            require(actual == item["sha256"], f"source pin mismatch: {item['path']}")
            checked.append(item["path"])
    word = load_gzip_json(WORD_PATH)
    template = load_gzip_json(TEMPLATE_PATH)
    geometry = frame_census(word, template)
    screen = selected_profile_screen()
    result = dict(
        schema_version=1,
        seed="0410adea86dfbb7cdf86b46ba736e993",
        base_commit="e112d71c8d7bb32435debcc54df932593dd8223a",
        selected_record_sha256="10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
        source_pins_checked=checked,
        geometry=geometry,
        profile_screen=screen,
    )
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    result_path = HERE / "RESULT.json"
    if sys.argv[1:] == ["--write"]:
        result_path.write_text(rendered)
    else:
        require(sys.argv[1:] == [], "usage: verify.py [--write]")
        require(result_path.read_text() == rendered, "RESULT.json differs from exact replay")
    print(geometry["status"], "counts", geometry["per_port_candidate_counts"],
          "incidences", geometry["candidate_port_incidences"], "common", geometry["common_transvections"])
    print(screen["status"], "baseline", screen["baseline_a_ceiling"][-1],
          "charged", screen["charged_optimistic_a_ceiling"][-1],
          "relative_increase_percent", screen["relative_ceiling_increase_percent"])
    print("PASS_RANK1_TRANSVECTION_BOUNDARY_SEED0410", "source_pins", len(checked))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        print("FAIL:", exc)
        raise SystemExit(1)
