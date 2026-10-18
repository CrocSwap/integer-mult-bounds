#!/usr/bin/env python3
"""Exact finite search for a two-coordinate frame rail in the pinned SW4 word."""
from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import heapq
import importlib.util
import json
import math
import tarfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
ARCHIVE_REL = Path("research/community-frontier1094-audit/selected-replay.tar.gz")
ARCHIVE_MEMBER = "candidate/strict/global/base/providers/gauge44/FULL-WORD.json.gz"
PROMOTION = ROOT / "research/complex-sw4-frame8/construction/promo/build_promotion.py"
CEILING = ROOT / "research/complex-local-word-ceiling/ceiling.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


bp = load_module("imb_frame_promotion", PROMOTION)
C = load_module("imb_complex_ceiling", CEILING)


def regs(e):
    return [e[1]] + ([e[2]] if e[0] == "add" else [])


def full_frame(word, r):
    v = word["report"]["v"]
    if v <= r < 2 * v:
        port = word["ports"][r - v]
        return bp.span([x for x in range(1, 512) if (x & port).bit_count() % 2 == 0])
    final = {int(k): bp.span(vs) for k, vs in word.get("helper_final", {}).items()}
    return final.get(r, bp.span([1 << i for i in range(9)]))


def events_for(word):
    """Replay the exact climb order used by build_promotion.chain_profile."""
    v, R = word["report"]["v"], word["report"]["R"]
    n = 2 * v + R
    cur = [() for _ in range(n)]
    for i, p in enumerate(word["ports"]):
        cur[i] = bp.span([p])
    for r, f in word.get("start_extra", {}).items():
        cur[int(r)] = bp.span(f)
    events = []

    def add_event(location, participants, frame, is_final=False, is_barrier=False):
        F = bp.span(frame)
        assert len(set(participants)) == len(participants), ("self-add unsupported", location)
        before = tuple(cur[r] for r in participants)
        ranks = tuple(len(F) - len(S) for S in before)
        assert all(x >= 0 for x in ranks), ("nonmonotone base", location)
        events.append({"location": location, "regs": tuple(participants), "frame": F,
                       "before": before, "ranks": ranks, "final": is_final,
                       "barrier": is_barrier})
        for r in participants:
            cur[r] = F

    for section in ("A", "B"):
        for i, e in enumerate(word[section]):
            add_event((section, i), regs(e), e[-1])
        if section == "A":
            # The selected native contract fixes these exact interfaces at the
            # A/B boundary; they are not merely final-endpoint inclusions.
            levels = {int(t): bp.span(U) for t, U in word.get("target_levels", {}).items()}
            for t in range(v):
                add_event(("target_level", t), [v + t], levels.get(t, ()), is_barrier=True)
            for i, (r, U) in enumerate(zip(word["centers"], word["center_frames"])):
                add_event(("center_frame", i), [r], U, is_barrier=True)
    for j, (i, frame) in enumerate(word.get("early_cleanup", [])):
        add_event(("early_cleanup", j), regs(word["cleanup"][i]), frame)
    for r in range(n):
        add_event(("final", r), [r], full_frame(word, r), True)
    chain = Counter(rank for ev in events for rank in ev["ranks"] if rank)
    profile = Counter({int(k): v for k, v in word["report"]["local_profile"].items()})
    fixed = profile - chain
    assert not (chain - profile), ("climb profile exceeds report", dict(chain), dict(profile))
    assert dict(fixed) == {8: 8}, ("unexpected non-chain profile component", dict(fixed))
    return events, profile, chain, fixed


def plane_candidates():
    for i in range(9):
        for j in range(i + 1, 9):
            yield (1 << i, 1 << j)


def aug_span(F, P):
    return bp.span(list(F) + list(P))


def candidate_seeds(word, events):
    helpers = 2 * word["report"]["v"]
    out = []
    for idx, ev in enumerate(events):
        sec, _ = ev["location"]
        if sec in ("A", "B") and len(ev["regs"]) == 2 and all(r >= helpers for r in ev["regs"]):
            out.append(idx)
    return out


def inspect_plane(word, events, base_profile, P, seeds, target_a, exact_costs):
    """Enumerate seed gates for P, returning exact threshold counts and the best float screen."""
    info = []
    for ev in events:
        F = ev["frame"]
        Fa = aug_span(F, P)
        info.append((len(Fa), len(Fa) == len(F), tuple(len(aug_span(S, P)) for S in ev["before"])))

    by_reg = [[] for _ in range(2 * word["report"]["v"] + word["report"]["R"])]
    for idx, ev in enumerate(events):
        for r in ev["regs"]:
            by_reg[r].append(idx)

    baseline = [0] * 10
    for r, count in base_profile.items():
        assert 1 <= r <= 9
        baseline[r] = count
    base_profile_tuple = tuple(baseline)
    best = None
    tested = noop = endpoint_reject = interface_reject = 0
    qualify = reject_below = ambiguous = 0
    first_endpoint_control = None
    seen_profiles = set()

    for seed in seeds:
        if info[seed][1]:
            noop += 1
            continue
        tested += 1
        counts = baseline.copy()
        active = set()
        heap = []

        def change_profile(ev_idx, active_before, new_frame_dim):
            ev = events[ev_idx]
            dims, ranks = ev["before"], ev["ranks"]
            aug_dims = info[ev_idx][2]
            for pos, r in enumerate(ev["regs"]):
                old = ranks[pos]
                if old:
                    counts[old] -= 1
                prior = aug_dims[pos] if r in active_before else len(dims[pos])
                nr = new_frame_dim - prior
                if nr < 0:
                    raise AssertionError(("negative climb", P, seed, ev_idx, r, nr))
                if nr:
                    counts[nr] += 1

        # The seed introduces P into the common frame and both helper registers.
        ev = events[seed]
        change_profile(seed, set(), info[seed][0])
        if info[seed][1]:
            raise AssertionError("no-op seed was not filtered")
        active.update(ev["regs"])
        for r in ev["regs"]:
            q = bisect.bisect_right(by_reg[r], seed)
            if q < len(by_reg[r]):
                heapq.heappush(heap, (by_reg[r][q], r))

        valid = True
        while heap:
            idx = heap[0][0]
            touched_active = set()
            while heap and heap[0][0] == idx:
                _, r = heapq.heappop(heap)
                if r in active:
                    touched_active.add(r)
            if not touched_active:
                continue
            ev = events[idx]
            info_idx = info[idx]
            touched = set(ev["regs"])
            if (ev["final"] or ev["barrier"]) and not info_idx[1]:
                valid = False
                endpoint_reject += 1
                if ev["barrier"]:
                    interface_reject += 1
                if first_endpoint_control is None:
                    first_endpoint_control = {"seed_event": seed, "plane": list(P),
                                              "endpoint_event": idx, "registers": sorted(touched_active),
                                              "endpoint_frame": list(ev["frame"]),
                                              "boundary_kind": ev["location"][0]}
                break
            change_profile(idx, touched_active, info_idx[0])
            if info_idx[1]:
                active.difference_update(touched)
            else:
                active.update(touched)
            for r in touched:
                if r in active:
                    q = bisect.bisect_right(by_reg[r], idx)
                    if q < len(by_reg[r]):
                        heapq.heappush(heap, (by_reg[r][q], r))
        if not valid:
            continue
        if active:
            raise AssertionError(("active plane survived endpoints", seed, P, active))
        mass = sum(r * counts[r] for r in range(1, 10))
        base_mass = sum(r * base_profile[r] for r in base_profile)
        assert mass == base_mass, ("rank mass changed despite fixed endpoints", mass, base_mass, seed, P)
        pt = tuple(counts)
        seen_profiles.add(pt)
        lower_num, upper_num, threshold_num = exact_costs(pt)
        if lower_num > threshold_num:
            reject_below += 1
        elif upper_num < threshold_num:
            qualify += 1
        else:
            ambiguous += 1
        # Fast monotone bisection ranks candidates; exact intervals decide the gate above.
        score = float_ceiling(counts)
        if best is None or score > best[0]:
            best = (score, seed, P, pt)

    return {"tested": tested, "no_op": noop, "endpoint_reject": endpoint_reject,
            "interface_reject": interface_reject,
            "below_5pct": reject_below, "above_5pct": qualify, "ambiguous": ambiguous,
            "unique_profiles": len(seen_profiles), "profiles": [list(x) for x in sorted(seen_profiles)],
            "best": best,
            "first_endpoint_control": first_endpoint_control}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--word", type=Path, help="optional exact extracted selected word; archive is the default")
    ap.add_argument("--archive", type=Path, default=ROOT / ARCHIVE_REL)
    ap.add_argument("--out", type=Path, default=PKG / "SEARCH.json")
    ap.add_argument("--candidate-word", type=Path, default=PKG / "BEST-WORD.json.gz")
    a = ap.parse_args()
    archive_raw = a.archive.read_bytes()
    assert hashlib.sha256(archive_raw).hexdigest() == "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
    if a.word is None:
        import io
        with tarfile.open(fileobj=io.BytesIO(archive_raw), mode="r:gz") as tf:
            raw = tf.extractfile(ARCHIVE_MEMBER).read()
    else:
        raw = a.word.read_bytes()
    word = json.loads(gzip.decompress(raw))
    assert hashlib.sha256(raw).hexdigest() == "49596aa4ed4fd36cd4582fd0e8ddeb09fd80370a7d8aea1ede52a135b536d289"
    events, profile, oldchain, fixed_profile = events_for(word)
    seeds = candidate_seeds(word, events)
    assert len(seeds) > 0
    base_model = C.model(profile, 73, 896, 9, 64)
    base_bracket = C.ceiling(profile, 73, 896, 9, 64, grid=Q(1, 10**12))
    target_a = base_bracket[1] * Q(21, 20)
    scale = 1 << C.PREC
    cost_l, cost_u = {}, {}
    for r in range(1, 10):
        lo, hi = C.child_cost(r, 73, target_a)
        cost_l[r], cost_u[r] = int(lo * scale), int(hi * scale)
    lo51, hi51 = C.child_cost(base_model["R"], 73, target_a)
    cost_l[base_model["R"]], cost_u[base_model["R"]] = int(lo51 * scale), int(hi51 * scale)
    idle = base_model["idle_mass"]
    w = base_model["w"]

    def exact_costs(count_tuple):
        local_lo = sum(Q(count_tuple[r]) * cost_l[r] for r in range(1, 10))
        local_hi = sum(Q(count_tuple[r]) * cost_u[r] for r in range(1, 10))
        local_lo += idle / base_model["R"] * cost_l[base_model["R"]]
        local_hi += idle / base_model["R"] * cost_u[base_model["R"]]
        threshold = w * scale
        return local_lo, local_hi, threshold

    global_best = None
    totals = Counter()
    plane_rows = []
    all_profiles = set()
    for P in plane_candidates():
        print("SEARCH plane", list(P), "candidate seeds", len(seeds), flush=True)
        row = inspect_plane(word, events, profile, P, seeds, target_a, exact_costs)
        plane_rows.append({k: v for k, v in row.items() if k != "best"})
        all_profiles.update(tuple(x) for x in row["profiles"])
        for k in ("tested", "no_op", "endpoint_reject", "interface_reject", "below_5pct", "above_5pct", "ambiguous"):
            totals[k] += row[k]
        if row["best"] and (global_best is None or row["best"][0] > global_best[0]):
            global_best = row["best"]
        print("DONE plane", list(P), "tested", row["tested"], "endpoint rejects", row["endpoint_reject"],
              "best a", row["best"][0] if row["best"] else None, flush=True)

    assert global_best is not None
    approx, seed, P, pt = global_best
    best_profile = {r: pt[r] for r in range(1, 10) if pt[r]}
    best_bracket = C.ceiling(best_profile, 73, 896, 9, 64, grid=Q(1, 10**12))
    threshold_check = C.relax(best_profile, 73, 896, 9, 64, target_a)
    best_events = events
    newword = json.loads(json.dumps(word))
    plane = tuple(P)
    active = set()
    # Reconstruct the globally best minimal closure to serialize it.
    for idx in range(seed, len(events)):
        ev = events[idx]
        changed = idx == seed or bool(active.intersection(ev["regs"]))
        if not changed:
            continue
        oldF = ev["frame"]
        newF = aug_span(oldF, plane)
        if ev["location"][0] == "final":
            assert len(newF) == len(oldF), "best closure changes final endpoint"
        elif ev["barrier"]:
            assert len(newF) == len(oldF), "best closure changes exact A/B interface"
        elif newF != oldF:
            sec, pos = ev["location"]
            if sec in ("A", "B"):
                newword[sec][pos][-1] = list(newF)
            elif sec == "early_cleanup":
                newword["early_cleanup"][pos][1] = list(newF)
        contains = len(newF) == len(oldF)
        if contains:
            active.difference_update(ev["regs"])
        else:
            active.update(ev["regs"])
    assert not active
    newchain = bp.chain_profile(newword)
    assert Counter(newchain) + Counter(fixed_profile) == Counter(best_profile), (
        newchain, fixed_profile, best_profile)
    merged = Counter({int(k): v for k, v in word["report"]["local_profile"].items()})
    merged.subtract(oldchain)
    merged.update(newchain)
    newword["report"]["local_profile"] = {str(r): n for r, n in sorted(merged.items()) if n}
    newword["report"]["local_rank_mass"] = sum(r * n for r, n in merged.items())
    assert merged == Counter(best_profile), (dict(merged), best_profile)
    outbytes = json.dumps(newword, sort_keys=True, separators=(",", ":")).encode()
    a.candidate_word.parent.mkdir(parents=True, exist_ok=True)
    compressed_word = gzip.compress(outbytes, mtime=0)
    a.candidate_word.write_bytes(compressed_word)

    # Exact ceilings for every distinct surviving profile make the reported
    # finite-domain maximum independent of the float ranking shortcut.
    profile_ceilings = []
    for values in sorted(all_profiles):
        prof = {r: values[r] for r in range(1, 10) if values[r]}
        bracket = C.ceiling(prof, 73, 896, 9, 64, grid=Q(1, 10**12))
        profile_ceilings.append({"profile": {str(r): n for r, n in prof.items()},
                                 "bracket": [str(x) for x in bracket]})
    profile_ceilings.sort(key=lambda row: Q(row["bracket"][0]), reverse=True)
    assert profile_ceilings[0]["profile"] == {str(r): n for r, n in best_profile.items()}, (
        "exact ceiling ranking disagrees with float candidate ranking", profile_ceilings[0], best_profile)
    best_lower = Q(profile_ceilings[0]["bracket"][0])
    max_other_upper = max((Q(row["bracket"][1]) for row in profile_ceilings[1:]), default=Q(0))
    assert best_lower > max_other_upper, ("distinct profile ceiling intervals do not separate",
                                          profile_ceilings[0], max_other_upper)

    result = {
        "status": "PASS_TWO_PLANE_FRAME_RAIL_SEARCH",
        "seed": "ca04ccbf3c8c214a13d9c2452e780d32",
        "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
        "selected_record_sha256": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
        "selected_source_archive_sha256": hashlib.sha256(archive_raw).hexdigest(),
        "word_member": ARCHIVE_MEMBER,
        "word_sha256": hashlib.sha256(raw).hexdigest(),
        "search_domain": {"planes": 36, "helper_helper_seed_gates": len(seeds),
                          "seed_plane_pairs": 36 * len(seeds)},
        "totals": dict(totals),
        "best": {"approx_a": approx, "seed_event": seed, "plane": list(P),
                 "profile": {str(r): n for r, n in best_profile.items()},
                 "rank_mass": sum(r * n for r, n in best_profile.items()),
                 "ceiling_bracket": [str(x) for x in best_bracket],
                 "target_a_5pct": str(target_a),
                 "target_relax_interval": [str(x) for x in threshold_check],
                 "profile_sha256": hashlib.sha256(json.dumps(best_profile, sort_keys=True).encode()).hexdigest(),
                 "word_output_sha256": hashlib.sha256(outbytes).hexdigest()},
        "base_profile": {str(r): n for r, n in sorted(profile.items())},
        "base_ceiling_bracket": [str(x) for x in base_bracket],
        "distinct_valid_profiles": len(profile_ceilings),
        "exact_profile_ceilings": profile_ceilings,
        "plane_rows": plane_rows,
        "exact_best_separation": {"best_profile": profile_ceilings[0]["profile"],
                                  "best_lower": str(best_lower),
                                  "max_other_upper": str(max_other_upper),
                                  "strictly_separated": True},
        "negative_control": {"kind": "exact internal interface barrier conflict",
                             "example": plane_rows[0]["first_endpoint_control"],
                             "rejected_seed_plane_pairs": totals["endpoint_reject"],
                             "interface_rejections": totals["interface_reject"]},
        "construction_effect": {"scalar_program_unchanged": True,
                                "start_frames_unchanged": True,
                                "A_B_target_levels_and_centres_exact": True,
                                "terminal_endpoints_unchanged": True,
                                "additional_arrays": 0,
                                "additional_scalar_gates": 0,
                                "all_induced_rank_climbs_charged": True},
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "search_domain", "totals", "best")}, indent=2))


def float_ceiling(counts):
    """Fast ranking only; exact threshold and final ceiling use the pinned interval engine."""
    m, families, stages, centre, R = 73, 896, 9, 64, 51
    w = families / stages
    mass = sum(r * counts[r] for r in range(1, 10))
    idle = (m - 1) * w + centre - mass
    lo, hi = 0.0, 0.05
    for _ in range(35):
        a = (lo + hi) / 2
        moment = sum(counts[r] * (r / m) ** (1 - a) for r in range(1, 10))
        moment += (idle / R) * (R / m) ** (1 - a)
        if moment / w < 1:
            lo = a
        else:
            hi = a
    return lo


if __name__ == "__main__":
    main()
