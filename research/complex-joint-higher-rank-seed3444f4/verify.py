#!/usr/bin/env python3
"""Verify the higher-rank same-gate joint-boundary screen on the pinned word."""
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCAL = ROOT / "research/r480-owner-optimum/inputs/local"
M, FAMILIES, STAGES, CENTRE = 73, 896, 9, 64
GRID = Q(1, 10**12)
EXPECTED_SELECTED = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
EXPECTED_FULL_GZ = "49596aa4ed4fd36cd4582fd0e8ddeb09fd80370a7d8aea1ede52a135b536d289"
EXPECTED_FULL_RAW = "c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8"
EXPECTED_CANONICAL_GZ = "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"
EXPECTED_CANONICAL_RAW = "4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c"
EXPECTED_PROGRAMS_GZ = "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"
EXPECTED_PROGRAMS_RAW = "9f41d53659e9be84e20c661560c5687abbf5cd0660cdecbe01ad5eb29e6b8ee3"
EXPECTED_REVIEW = "7e76d2c38e5fce30587835b7251df1430488ae4dd372611ef69a3f03f476b6cb"
EXPECTED_SOURCE_MANIFEST = "79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b"
EXPECTED_CERTIFICATE = "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045"


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def gf2_basis(values):
    pivots = {}
    for value in values:
        x = int(value)
        for pivot in sorted(pivots, reverse=True):
            if (x >> pivot) & 1:
                x ^= pivots[pivot]
        if x:
            pivot = x.bit_length() - 1
            for q in list(pivots):
                if (pivots[q] >> pivot) & 1:
                    pivots[q] ^= x
            pivots[pivot] = x
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def included(old_frame, new_frame):
    return gf2_basis(list(old_frame) + list(new_frame)) == gf2_basis(new_frame)


def load_inputs():
    selected_bytes = (ROOT / "certificates/selected-result.json").read_bytes()
    need(digest(selected_bytes) == EXPECTED_SELECTED, "selected-record SHA256 changed")
    selected = json.loads(selected_bytes)
    need(selected["proof"] == "docs/research/community-batch1099-review.md", "selected review pointer changed")
    need(selected["source_manifest"] == "research/community-frontier1094-audit/SELECTED-SOURCE.json",
         "selected source-manifest pointer changed")
    need(selected["certificate"] == "research/community-frontier1094-audit/ASSEMBLY.json",
         "selected certificate pointer changed")
    need(selected["reproduce"] == "make frontier1094-verify", "selected reproduction pointer changed")
    need(digest((ROOT / selected["proof"]).read_bytes()) == EXPECTED_REVIEW, "selected review pin changed")
    need(digest((ROOT / selected["source_manifest"]).read_bytes()) == EXPECTED_SOURCE_MANIFEST,
         "selected source-manifest pin changed")
    certificate_bytes = (ROOT / selected["certificate"]).read_bytes()
    need(digest(certificate_bytes) == EXPECTED_CERTIFICATE == selected["certificate_sha256"],
         "selected certificate pin changed")
    certificate = json.loads(certificate_bytes)
    need(certificate["kappa"] == selected["kappa"], "selected certificate kappa mismatch")

    full_gz = (LOCAL / "FULL-WORD.json.gz").read_bytes()
    need(digest(full_gz) == EXPECTED_FULL_GZ, "compressed full-word SHA256 changed")
    full_raw = gzip.decompress(full_gz)
    need(digest(full_raw) == EXPECTED_FULL_RAW, "decompressed full-word SHA256 changed")
    canonical_gz = (LOCAL / "CANONICAL-WORD.json.gz").read_bytes()
    canonical_raw = gzip.decompress(canonical_gz)
    need(digest(canonical_gz) == EXPECTED_CANONICAL_GZ and digest(canonical_raw) == EXPECTED_CANONICAL_RAW,
         "canonical word source pin changed")
    programs_gz = (LOCAL / "LOCAL-PROGRAMS.json.gz").read_bytes()
    programs_raw = gzip.decompress(programs_gz)
    need(digest(programs_gz) == EXPECTED_PROGRAMS_GZ and digest(programs_raw) == EXPECTED_PROGRAMS_RAW,
         "local program source pin changed")
    canonical = json.loads(canonical_raw)
    programs = json.loads(programs_raw)
    return canonical, programs, full_gz, full_raw


GATE_PARTS = ("A", "B", "cleanup_tail")


def validate_pair_row(row, canonical):
    part = row["part"]
    idx = row["gate_index"]
    source_part = "tail" if part == "cleanup_tail" else part
    need(part in GATE_PARTS and 0 <= idx < len(canonical[source_part]), "gate address outside source word")
    gate = canonical[source_part][idx]
    need(gate[0] == "add", "candidate is not a binary ADD")
    regs = [int(gate[1]), int(gate[2])]
    need(row["registers"] == regs, "candidate operand-register mutation")
    need(row["new_frame"] == int(gate[-1]), "candidate target-frame mutation")
    ranks = row["ranks"]
    old_frames = row["old_frames"]
    need(len(ranks) == len(old_frames) == 2, "candidate lane arity")
    need(row["coefficient"] == [int(gate[3]), int(gate[4])], "candidate gate-coefficient mutation")
    frame = canonical["frames"][int(gate[-1])]
    for old_id, rank in zip(old_frames, ranks):
        old = canonical["frames"][int(old_id)]
        need(included(old, frame), "old dirty frame is not contained in gate target")
        exact_rank = len(gf2_basis(frame)) - len(gf2_basis(old))
        need(rank == exact_rank and rank > 0, "candidate quotient-rank mutation")
    c = Q(*row["coefficient"])
    need(c != 0, "zero gate coefficient is outside the selected domain")
    need(max(ranks) > 1, "rank-one pair belongs to the predecessor domain")
    need(row["matrix"] == [["1", str(c)], ["0", "1"]], "exact shear matrix mutation")
    need(row["inverse"] == [["1", str(-c)], ["0", "1"]], "exact inverse shear mutation")
    need(row["determinant"] == "1", "shear determinant mutation")
    need(row["rank_sum"] == sum(ranks), "rank-sum mutation")
    need(0 < row["rank_sum"] < M, "joint child rank is outside the ceiling model")
    return c


def scan_orientation(events, canonical, backward):
    frames = canonical["frames"]
    current = list(canonical["start"])
    phase = None
    gate_index = Counter()
    pending = []
    rows = []
    gate_pairs = Counter()
    final_ranks = Counter()

    for event in events:
        tag = event[0]
        if tag == "phase":
            need(not pending, "unconsumed frame climbs at phase boundary")
            phase = event[1]
            continue

        if tag == "climb":
            _, part, register, old_id, new_id, rank = event
            register, old_id, new_id, rank = map(int, (register, old_id, new_id, rank))
            need(part == phase, "climb in wrong phase")
            need(current[register] == old_id, "frame-chain old endpoint mismatch")
            old, new = frames[old_id], frames[new_id]
            need(included(old, new), "frame climb is not monotone")
            exact_rank = len(gf2_basis(new)) - len(gf2_basis(old))
            need(rank == exact_rank and rank > 0, "frame climb rank mismatch")
            if phase in GATE_PARTS:
                pending.append({"register": register, "old_frame": old_id,
                                "new_frame": new_id, "rank": rank})
            elif phase == "final":
                need(new_id == int(canonical["final"][register]), "wrong terminal frame")
                final_ranks[rank] += 1
            current[register] = new_id
            continue

        if tag == "scalar" and phase in GATE_PARTS:
            op = event[1]
            idx = gate_index[phase]
            gate_index[phase] += 1
            source_part = "tail" if phase == "cleanup_tail" else phase
            gate = canonical[source_part][idx]
            target_frame = int(gate[-1])
            need(int(event[2]) == target_frame, "scalar gate is evaluated outside its target frame")
            pending_regs = [p["register"] for p in pending]
            need(len(pending_regs) == len(set(pending_regs)), "duplicate climb at one gate")
            need(all(p["new_frame"] == target_frame for p in pending), "climb targets disagree at gate")
            if gate[0] == "add":
                need(op[0] == "add", "canonical ADD emitted as a different scalar operation")
                dest, source = int(gate[1]), int(gate[2])
                orig_c = Q(int(gate[3]), int(gate[4]))
                expected_op = (source, dest, -orig_c) if backward else (dest, source, orig_c)
                got = (int(op[1][1]), int(op[2][1]), Q(int(op[3]), int(op[4])))
                need(got == expected_op, "forward/backward scalar shear mismatch")
                need(set(pending_regs) <= {dest, source}, "unrelated register climb attached to gate")
                need(current[dest] == target_frame and current[source] == target_frame,
                     "both operands do not reach the common target frame")
                if len(pending) == 2:
                    need(set(pending_regs) == {dest, source}, "paired climb does not cover both operands")
                    ranks = [p["rank"] for p in pending]
                    old_frames = [p["old_frame"] for p in pending]
                    shape = tuple(sorted(ranks))
                    gate_pairs[shape] += 1
                    if max(ranks) > 1:
                        row = {
                            "part": phase,
                            "gate_index": idx,
                            "registers": [dest, source],
                            "old_frames": old_frames,
                            "new_frame": target_frame,
                            "ranks": ranks,
                            "coefficient": [orig_c.numerator, orig_c.denominator],
                            "matrix": [["1", str(orig_c)], ["0", "1"]],
                            "inverse": [["1", str(-orig_c)], ["0", "1"]],
                            "determinant": "1",
                            "rank_sum": sum(ranks),
                            "boundary_codimension": sum(ranks),
                        }
                        validate_pair_row(row, canonical)
                        rows.append(row)
            elif gate[0] == "scale":
                need(op[0] == "scale", "canonical scale emitted as a different scalar operation")
                register = int(gate[1])
                expected_scale = Q(int(gate[2]), int(gate[3]))
                if backward:
                    expected_scale = 1 / expected_scale
                got_scale = Q(int(op[2]), int(op[3]))
                need(int(op[1][1]) == register and got_scale == expected_scale,
                     "forward/backward scalar scale mismatch")
                need(len(pending) <= 1 and set(pending_regs) <= {register},
                     "scale event has unrelated or duplicated frame climbs")
                need(current[register] == target_frame, "scaled register missed target frame")
            else:
                raise ValueError("unsupported canonical gate in selected A/B/tail schedule")
            pending = []
            continue

        if tag == "scalar":
            need(not pending, "unconsumed climbs before non-gate scalar")
            continue
        if tag == "center":
            need(not pending, "unconsumed climb before center service")
            continue
        if tag in ("adapter", "residual_adapter", "phase"):
            need(not pending, "unconsumed climb before adapter")
            continue
        need(not pending, "unconsumed climb before unrecognized event")

    need(not pending, "unconsumed climbs at end of program")
    for part in GATE_PARTS:
        source_part = "tail" if part == "cleanup_tail" else part
        need(gate_index[part] == len(canonical[source_part]), f"missed source gates in {part}")
    need(current == list(canonical["final"]), "terminal frame replay mismatch")
    return rows, gate_pairs, final_ranks


def reject_mutation(row, canonical, mutate):
    copy = json.loads(json.dumps(row))
    mutate(copy)
    try:
        validate_pair_row(copy, canonical)
    except (ValueError, AssertionError):
        return
    raise ValueError("negative control was accepted")


def main(write=False):
    canonical, programs, full_gz, full_raw = load_inputs()
    need(digest((ROOT / "certificates/selected-result.json").read_bytes()) == EXPECTED_SELECTED,
         "selected result changed during verification")
    need(set(programs) == {"forward", "backward"}, "unexpected program orientations")
    forward, fpairs, ffinal = scan_orientation(programs["forward"], canonical, False)
    backward, bpairs, bfinal = scan_orientation(programs["backward"], canonical, True)
    need(forward == backward, "orientation pair census mismatch")
    need(fpairs == bpairs and ffinal == bfinal, "orientation rank census mismatch")
    need(sum(fpairs.values()) == 949, "unexpected same-gate pair count")
    need(fpairs[(1, 1)] == 590, "rank-one pair predecessor count changed")
    high_pairs = [row for row in forward if max(row["ranks"]) > 1]
    need(len(high_pairs) == 359, "high-rank same-gate census changed")

    shapes = Counter(tuple(sorted(row["ranks"])) for row in high_pairs)
    expected_shapes = {
        (1, 2): 72, (1, 3): 52, (1, 4): 35, (1, 5): 26,
        (2, 2): 14, (2, 3): 5, (2, 4): 19,
        (3, 3): 122, (3, 4): 6, (4, 4): 8,
    }
    need(dict(sorted(shapes.items())) == expected_shapes, "rank-pair shape histogram changed")
    rank_sums = Counter(row["rank_sum"] for row in high_pairs)
    need(dict(sorted(rank_sums.items())) == {3: 72, 4: 66, 5: 40, 6: 167, 7: 6, 8: 8},
         "joint rank histogram changed")
    need(all(row["boundary_codimension"] == row["rank_sum"] for row in high_pairs),
         "boundary codimension mismatch")

    # The baseline word contributes eight rank-eight centre services in addition to frame climbs.
    climb_profile = Counter()
    for event in programs["forward"]:
        if event[0] == "climb":
            climb_profile[int(event[5])] += 1
    centre_count = sum(event[0] == "center" for event in programs["forward"])
    need(centre_count == 8, "centre service count changed")
    baseline = dict(sorted({**climb_profile, 8: climb_profile.get(8, 0) + centre_count}.items()))
    expected_baseline = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
    need(baseline == expected_baseline, "selected local paid profile mismatch")
    rank_mass = sum(r * n for r, n in baseline.items())
    need(rank_mass == 5586, "baseline paid rank mass changed")

    # Reproduce the already proposed J2 candidate: 590 same-gate (1,1) pairs and
    # 163 terminal (1,1) pairs. The latter comes from 326 rank-one terminal climbs.
    need(ffinal[1] == 326, "terminal rank-one count changed")
    j2_pairs = fpairs[(1, 1)] + ffinal[1] // 2
    need(ffinal[1] % 2 == 0 and j2_pairs == 753, "J2 predecessor pairing count changed")
    j2_profile = Counter(baseline)
    j2_profile[1] -= 2 * j2_pairs
    j2_profile[2] += j2_pairs
    need(min(j2_profile.values()) >= 0, "J2 profile underflow")

    extended = Counter(j2_profile)
    for row in high_pairs:
        r, s = row["ranks"]
        extended[r] -= 1
        extended[s] -= 1
        extended[r + s] += 1
    extended = Counter({r: n for r, n in extended.items() if n})
    need(min(extended.values()) >= 0, "higher-rank profile underflow")
    extended = dict(sorted(extended.items()))
    need(extended == {1: 721, 2: 1047, 3: 197, 4: 132, 5: 96, 6: 167, 7: 6, 8: 16},
         "extended profile mismatch")
    need(sum(r * n for r, n in extended.items()) == rank_mass, "extended profile did not conserve mass")
    need(sum(extended.values()) == sum(j2_profile.values()) - 359, "child-call count mismatch")

    sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
    import ceiling as C  # noqa: E402
    base_lo, base_hi = C.ceiling(baseline, M, FAMILIES, STAGES, CENTRE, grid=GRID)
    j2_lo, j2_hi = C.ceiling(dict(j2_profile), M, FAMILIES, STAGES, CENTRE, grid=GRID)
    ext_lo, ext_hi = C.ceiling(extended, M, FAMILIES, STAGES, CENTRE, grid=GRID)
    incremental_gain = ext_lo / j2_hi - 1
    total_gain = ext_lo / base_hi - 1
    need(incremental_gain > Q(5, 100), "ideal higher-rank extension misses the 5% incremental gate")

    target = Q(105, 100) * j2_hi
    moment_lo, moment_hi = C.relax(extended, M, FAMILIES, STAGES, CENTRE, target)
    model = C.model(extended, M, FAMILIES, STAGES, CENTRE)
    c1 = C.child_cost(1, M, target)
    cR = C.child_cost(model["R"], M, target)
    slack_lo = model["w"] * (1 - moment_hi)
    slack_hi = model["w"] * (1 - moment_lo)
    rank1_delta_lo = c1[0] - cR[1] / model["R"]
    rank1_delta_hi = c1[1] - cR[0] / model["R"]
    max_free_rank1 = int(slack_lo // rank1_delta_hi)
    first_fail_rank1 = int(slack_hi // rank1_delta_lo) + 1
    need(max_free_rank1 == 43 and first_fail_rank1 == 44,
         "rank-one-equivalent interface overhead budget changed")
    adapter_profile = dict(extended)
    adapter_profile[1] += len(high_pairs)
    adapter_lo, adapter_hi = C.relax(adapter_profile, M, FAMILIES, STAGES, CENTRE, target)
    need(adapter_lo > 1, "one rank-one-equivalent adapter per pair unexpectedly fits the 5% margin")

    census = {
        "schema_version": 1,
        "source_full_word_sha256_compressed": digest(full_gz),
        "source_full_word_sha256_decompressed": digest(full_raw),
        "forward_event_sha256": digest(canonical_json(programs["forward"])),
        "backward_event_sha256": digest(canonical_json(programs["backward"])),
        "same_gate_pair_shapes": {f"{a}+{b}": n for (a, b), n in sorted(fpairs.items())},
        "high_rank_pair_shapes": {f"{a}+{b}": n for (a, b), n in sorted(shapes.items())},
    }
    census_tsv = [
        "part\tgate_index\tregister0\tregister1\told_frame0\told_frame1\tnew_frame\trank0\trank1\tcoefficient_num\tcoefficient_den\trank_sum"
    ]
    for row in high_pairs:
        census_tsv.append("\t".join(str(value) for value in (
            row["part"], row["gate_index"], *row["registers"], *row["old_frames"],
            row["new_frame"], *row["ranks"], *row["coefficient"], row["rank_sum"])))
    census_text = "\n".join(census_tsv) + "\n"
    result = {
        "schema_version": 1,
        "status": "CONDITIONAL_HIGHER_RANK_JOINT_BOUNDARY_SCREEN_NO_NEW_KAPPA",
        "selected_record_sha256": EXPECTED_SELECTED,
        "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
        "track": "complex-mechanisms",
        "seed": "3444f4b8606069e8d454447c1dc60c12",
        "task_id": "complex-rank-shape-decoder",
        "source_full_word_sha256_compressed": digest(full_gz),
        "source_full_word_sha256_decompressed": digest(full_raw),
        "domain": {
            "operations": "single binary ADD gates in A, B, and scheduled cleanup_tail",
            "predicate": "both operands have positive frame climbs and max(r,s)>1",
            "orientations": ["forward", "backward"],
            "high_rank_pair_count": len(high_pairs),
            "shape_counts": census["high_rank_pair_shapes"],
            "rank_sum_counts": {str(r): n for r, n in sorted(rank_sums.items())},
            "forward_event_sha256": census["forward_event_sha256"],
            "backward_event_sha256": census["backward_event_sha256"],
        },
        "joint_boundary": {
            "map": "T_c(x,y)=(x+c*y,y)",
            "matrix": "[[1,c],[0,1]]",
            "inverse": "[[1,-c],[0,1]]",
            "determinant": "1",
            "codimension": "r+s for U×V -> F×F under invertible T_c",
            "conditional_assumption": "one J_{r,s} recursive child at the ordinary rank-(r+s) price",
        },
        "rank_profiles_per_local_call": {
            "selected_baseline": {str(r): n for r, n in baseline.items()},
            "PR1764_J2_candidate_reconstructed": {str(r): n for r, n in sorted(j2_profile.items()) if n},
            "plus_359_higher_rank_pairs": {str(r): n for r, n in extended.items()},
            "rank_mass": rank_mass,
            "call_counts": {
                "selected_baseline": sum(baseline.values()),
                "PR1764_J2_candidate": sum(j2_profile.values()),
                "higher_rank_extension": sum(extended.values()),
            },
        },
        "exact_fixed_word_ceiling": {
            "grid": str(GRID),
            "selected_baseline": {"lower": str(base_lo), "upper": str(base_hi)},
            "PR1764_J2_candidate": {"lower": str(j2_lo), "upper": str(j2_hi)},
            "higher_rank_extension": {"lower": str(ext_lo), "upper": str(ext_hi)},
            "incremental_gain_lower_fraction": str(incremental_gain),
            "incremental_gain_lower_percent": float(100 * incremental_gain),
            "total_gain_lower_fraction": str(total_gain),
            "total_gain_lower_percent": float(100 * total_gain),
        },
        "overhead_screen": {
            "target_saving": "1.05 times the upper endpoint of the PR1764 J2 candidate ceiling",
            "idle_rank_cap": model["R"],
            "rank1_equivalent_budget_per_local_call": max_free_rank1,
            "first_rank1_equivalent_count_failing_target": first_fail_rank1,
            "one_rank1_equivalent_per_each_of_359_interfaces": {
                "moment_lower": str(adapter_lo),
                "moment_upper": str(adapter_hi),
                "fails_five_percent_incremental_gain": True,
            },
            "meaning": "fractional idle-rank-51 displacement under the retained fixed-word model; not a physical adapter estimate",
        },
        "full_charge_ledger": {
            "native_scalar_gates": "unchanged in the optimistic mechanism screen",
            "recursive_children": "replace 359 pairs of rank r and s by one conditional J_{r,s} child of rank r+s",
            "frame_transitions": "original frames retained; no extra local climb is counted",
            "source_access": "no extra reads assumed; joint-child input contract remains unproved",
            "copies_and_helpers": "zero additional cost in the optimistic screen; actual gathering/copy bill is open",
            "restoration": "local shear has exact inverse; recursive joint-child restoration is open",
            "precision_and_phase": "no extra charge assumed; joint contract is not admitted",
            "hosting": "no extra host occupancy charged; whole-call assignment is not rebuilt",
            "interface_transitions": "unpriced except for the exact 43 rank-one-equivalent total budget; one per pair fails",
        },
        "scope_limit": "finite pinned-word interface screen only; no physical J_{r,s} supplier, global assembly, selected-result change, or new kappa",
    }

    reject_mutation(high_pairs[0], canonical, lambda r: r["coefficient"].__setitem__(0, r["coefficient"][0] + 1))
    reject_mutation(high_pairs[0], canonical,
                    lambda r: r.__setitem__("rank_sum", r["rank_sum"] + 1))
    reject_mutation(high_pairs[0], canonical,
                    lambda r: r.__setitem__("inverse", [["1", "0"], ["0", "1"]]))
    reject_mutation(high_pairs[0], canonical,
                    lambda r: r["old_frames"].__setitem__(0, r["new_frame"]))
    if write:
        (HERE / "CENSUS.tsv").write_text(census_text)
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        stored_census = (HERE / "CENSUS.tsv").read_text()
        stored_result = json.loads((HERE / "RESULT.json").read_text())
        need(stored_census == census_text, "stored gate census differs from source replay")
        need(stored_result == result, "stored result differs from exact replay")

    print("PASS_HIGHER_RANK_TWO_LANE_BOUNDARY pairs=359 rank_sums=3..8")
    print(f"PASS_EXACT_FIXED_WORD_CEILING incremental_gain_lower={float(100 * incremental_gain):.9f}%")
    print(f"PASS_OVERHEAD_BUDGET rank1_equivalents={max_free_rank1} first_fail={first_fail_rank1}")
    print("PASS_NEGATIVE_CONTROLS changed_coefficient,changed_rank_sum,changed_inverse,invalid_old_frame")
    print("LIMIT no physical joint supplier, complete interface price, assembly, or new kappa")


if __name__ == "__main__":
    main(write="--write" in sys.argv[1:])
