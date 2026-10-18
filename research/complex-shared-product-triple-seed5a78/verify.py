#!/usr/bin/env python3
"""Verify a reversible three-call shared-product helper and its exact screen."""

from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import tarfile
from collections import Counter
from fractions import Fraction as Q
from io import BytesIO
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def source_bytes(path: str) -> bytes:
    p = ROOT / path
    need(p.is_file(), f"missing source {path}")
    return p.read_bytes()


def pins() -> dict[str, str]:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    task = json.loads((PACKAGE / "TASK.json").read_text(encoding="utf-8"))
    need(manifest["base_commit"] == task["base_commit"], "base commit mismatch")
    need(hashlib.sha256(source_bytes("certificates/selected-result.json")).hexdigest()
         == task["selected_record_sha256"], "selected record hash mismatch")
    hashes = {}
    for row in manifest["files"]:
        digest = hashlib.sha256(source_bytes(row["path"])).hexdigest()
        need(digest == row["sha256"], f"pinned source SHA mismatch: {row['path']}")
        hashes[row["path"]] = digest
    return hashes


def load_ceiling():
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("pinned_complex_ceiling", path)
    need(spec is not None and spec.loader is not None, "cannot load pinned ceiling engine")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def zero_tensor() -> list[list[list[Q]]]:
    return [[[Q(0) for _ in range(4)] for _ in range(4)] for _ in range(3)]


def tensor() -> list[list[list[Q]]]:
    # F_i=x0*y0+x_(i+1)*y_(i+1), i=0,1,2.
    t = zero_tensor()
    for o in range(3):
        t[o][0][0] = Q(1)
        t[o][o + 1][o + 1] = Q(1)
    return t


def outer(x: list[Q], y: list[Q]) -> list[list[Q]]:
    return [[a * b for b in y] for a in x]


def reconstruct(atoms: list[tuple[list[Q], list[Q], list[Q]]]):
    out = zero_tensor()
    for left, right, output in atoms:
        mat = outer(left, right)
        for o, coefficient in enumerate(output):
            for i in range(4):
                for j in range(4):
                    out[o][i][j] += coefficient * mat[i][j]
    return out


def atoms(shared: bool):
    e = [[Q(int(i == j)) for i in range(3)] for j in range(3)]
    common = [Q(1), Q(0), Q(0), Q(0)]
    private = [[Q(int(i == j)) for i in range(4)] for j in range(4)]
    if shared:
        result = [(common, common, [Q(1)] * 3)]
    else:
        result = [(common, common, e[o]) for o in range(3)]
    result.extend((private[i + 1], private[i + 1], e[i]) for i in range(3))
    return result


def rank_q(rows: list[list[Q]]) -> int:
    a = [list(row) for row in rows]
    if not a:
        return 0
    pivot = 0
    for col in range(len(a[0])):
        found = next((r for r in range(pivot, len(a)) if a[r][col]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        d = a[pivot][col]
        a[pivot] = [x / d for x in a[pivot]]
        for r in range(len(a)):
            if r != pivot and a[r][col]:
                c = a[r][col]
                a[r] = [x - c * y for x, y in zip(a[r], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def tensor_checks() -> dict:
    t = tensor()
    shared_atoms = atoms(True)
    separate_atoms = atoms(False)
    need(reconstruct(shared_atoms) == t, "shared four-atom identity failed")
    need(reconstruct(separate_atoms) == t, "separate six-atom identity failed")
    # X-mode flattening rank is a lower bound on tensor rank.
    flattening = [[t[o][i][j] for o in range(3) for j in range(4)] for i in range(4)]
    flattening_rank = rank_q(flattening)
    need(flattening_rank == 4, "X-mode flattening rank changed")
    need(len(shared_atoms) == 4 and len(separate_atoms) == 6,
         "wrong joint/separate atom counts")
    # Omitting one common output or changing a shared coefficient is rejected.
    e0 = [Q(1), Q(0), Q(0)]
    wrong_common = [(shared_atoms[0][0], shared_atoms[0][1], e0), *shared_atoms[1:]]
    need(reconstruct(wrong_common) != t, "missing fanout target was not detected")
    return {
        "outputs": ["x0*y0+x1*y1", "x0*y0+x2*y2", "x0*y0+x3*y3"],
        "joint_tensor_rank": 4,
        "separate_call_atom_count": 6,
        "shared_joint_atom_count": 4,
        "x_mode_flattening_rank_lower_bound": flattening_rank,
        "positive_reconstruction": True,
        "negative_control_missing_one_fanout_rejected": True,
    }


def dirty_schedule_checks() -> dict:
    vals = [Q(-2), Q(-1), Q(0), Q(1), Q(3, 2)]
    fixtures = []
    for n in range(15):
        x = [vals[(n + 2 * j) % 5] for j in range(4)]
        y = [vals[(3 * n + j) % 5] for j in range(4)]
        dirty = [vals[(n + i + 1) % 5] for i in range(3)]
        h = Q(0)
        original_h = h
        out = list(dirty)
        common = x[0] * y[0]
        # One forward common child, three fanout ADDs, three private children,
        # then the inverse common child restores the clean shared slot.
        h += common
        for i in range(3):
            out[i] += h
            out[i] += x[i + 1] * y[i + 1]
        h -= common
        expected = [dirty[i] + common + x[i + 1] * y[i + 1] for i in range(3)]
        need(out == expected and h == original_h == 0,
             f"dirty-target forward or helper restoration failed at fixture {n}")

        # Exact reverse schedule: undo cleanup, private children, fanout, compute.
        inv_h = h + common
        inv = list(out)
        for i in reversed(range(3)):
            inv[i] -= x[i + 1] * y[i + 1]
        for i in reversed(range(3)):
            inv[i] -= inv_h
        inv_h -= common
        need(inv == dirty and inv_h == 0,
             f"dirty-target inverse failed at fixture {n}")

        # The clean helper is a real interface condition, not silently assumed:
        # a nonzero initial value changes every fanout by that dirt.
        dirty_h = Q(2)
        bad_out = [Q(0), Q(0), Q(0)]
        dirty_h += common
        for i in range(3):
            bad_out[i] += dirty_h
        need(bad_out != [common] * 3, "nonzero helper dirt negative control failed")
        fixtures.append({"index": n, "inputs": [str(z) for z in x + y],
                         "dirty_outputs": [str(z) for z in dirty],
                         "outputs_after": [str(z) for z in out]})
    return {
        "fixtures": fixtures,
        "arbitrary_dirty_outputs_preserved_by_inverse": True,
        "sources_unchanged": True,
        "helper_contract": "one clean width-one slot per three-call batch, returned clean",
        "shared_child_calls_forward": 2,
        "private_child_calls_forward": 3,
        "separate_baseline_rank1_child_calls_forward": 6,
        "shared_rank1_child_calls_forward": 5,
        "extra_fanout_adds_forward": 3,
        "extra_fanout_subtracts_inverse": 3,
        "additional_clean_helper_slots_per_batch": 1,
        "common_source_pair_reads_forward": {"separate": 3, "shared_compute_plus_cleanup": 2},
        "same_frame_transitions": 0,
        "copies": 0,
        "precision": "exact rational coefficients; no finite-precision transfer claim",
    }


def profile(s: int, e: int, base: dict[int, Q]) -> dict[int, Q]:
    need(0 <= s <= 2412 and 0 <= e <= 2, "profile parameters outside the screened domain")
    out = dict(base)
    # Three callers each used the common product once. Sharing saves one
    # rank-one child per triple; e is further rank-one-equivalent overhead.
    out[1] = base[1] + Q(e - s, 3)
    return out


def profile_screen() -> dict:
    c = load_ceiling()
    selected = json.loads(source_bytes("research/complex-local-word-ceiling/RESULT.json"))
    base = {int(r): Q(n) for r, n in selected["selected"]["local_profile_per_call"].items()}
    need(base == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8},
         "selected local profile drift")
    a0 = Q(selected["ceiling"]["a_ceiling"])
    target = a0 * Q(105, 100)
    base_ceiling = c.ceiling(base, 73, 896, 9, 64)
    need(base_ceiling[1] == a0, "selected ceiling positive control drift")
    R = c.max_idle_rank(73)
    need(R == 51, "idle-rank cap drift")

    # A shared slot moves 1/3 rank-one child per call into the rank-51 idle
    # pool. At a>0, rank-51 idle cost per unit mass is strictly below rank-1
    # child cost, so the exact relaxation decreases monotonically in s.
    c1 = c.child_cost(1, 73, target)
    cR = c.child_cost(R, 73, target)
    slope_hi = (cR[1] / R - c1[0]) / (3 * Q(896, 9))
    need(slope_hi < 0, "shared-slot relaxation is not certified decreasing")

    thresholds = {}
    for e in (0, 1, 2):
        maximum = c.relax(profile(2412, e, base), 73, 896, 9, 64, target)
        need(maximum[1] < 1, f"full share domain misses target for overhead {e}")
        lo, hi = 0, 2412
        while lo < hi:
            mid = (lo + hi) // 2
            if c.relax(profile(mid, e, base), 73, 896, 9, 64, target)[1] < 1:
                hi = mid
            else:
                lo = mid + 1
        k = lo
        previous = c.relax(profile(k - 1, e, base), 73, 896, 9, 64, target)
        passing = c.relax(profile(k, e, base), 73, 896, 9, 64, target)
        need(previous[0] > 1, f"previous integer is not certified failing for overhead {e}")
        need(passing[1] < 1, f"threshold integer is not certified passing for overhead {e}")
        thresholds[str(e)] = {
            "minimum_shared_slots": k,
            "previous_relaxation_interval": [str(x) for x in previous],
            "passing_relaxation_interval": [str(x) for x in passing],
            "full_domain_relaxation_interval": [str(x) for x in maximum],
        }
    need([thresholds[str(e)]["minimum_shared_slots"] for e in (0, 1, 2)]
         == [764, 765, 766], "exact 5-percent thresholds changed")
    # No-sharing and overhead-only controls do not pass the target.
    no_share = c.relax(profile(0, 0, base), 73, 896, 9, 64, target)
    need(no_share[0] > 1, "zero-sharing negative control unexpectedly passes")
    need(profile(1, 1, base) == base, "one slot and one equivalent overhead should cancel")
    one_share_ceiling = c.ceiling(profile(1, 0, base), 73, 896, 9, 64)
    need(one_share_ceiling[0] > base_ceiling[1], "one exact shared slot does not improve the local ceiling")
    return {
        "selected_profile_per_call": {str(r): str(n) for r, n in base.items()},
        "selected_a_upper": str(a0),
        "target_a_5pct": str(target),
        "domain": {"shared_rank1_slots_per_three_call_batch": "0..2412",
                   "extra_rank1_equivalents_per_batch": [0, 1, 2]},
        "profile_delta_per_shared_slot_at_e0": {"rank1_per_call": "-1/3", "rank_mass_per_call": "-1/3"},
        "profile_delta_per_extra_equivalent": {"rank1_per_call": "+1/3", "rank_mass_per_call": "+1/3"},
        "thresholds": thresholds,
        "one_shared_slot_zero_extra_ceiling": [str(x) for x in one_share_ceiling],
        "no_sharing_relaxation_at_target": [str(x) for x in no_share],
        "assumptions": [
            "The existing m=73, families=896, stages=9, centre=64 and one-unpaid-coordinate coverage law hold for the three-call average profile.",
            "Each shared product appears once in each of the three call roles and uses the same frame.",
            "The forward and inverse rank-one child calls used to restore the clean helper are included in the 3-to-2 saving.",
            "One width-one clean helper slot is available per batch; the exact screen does not prove source hosting or that occurrence count.",
            "The e parameter is additional rank-one-equivalent cost beyond the counted compute/cleanup pair, not a measured physical invoice.",
        ],
        "no_selected_source_or_kappa_claim": True,
    }


def phase_a_schema_screen() -> dict:
    archive_path = "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"
    with tarfile.open(fileobj=BytesIO(source_bytes(archive_path)), mode="r:gz") as archive:
        member = archive.extractfile("evidence/local/LOCAL-PROGRAMS.json.gz")
        need(member is not None, "pinned provider archive lacks local-program stream")
        local = json.loads(gzip.decompress(member.read()))
    events = local["forward"]
    markers = [(i, event[1]) for i, event in enumerate(events) if event[0] == "phase"]
    j = next((i for i, (_offset, name) in enumerate(markers) if name == "A"), None)
    need(j is not None and j + 1 < len(markers), "phase-A boundaries missing")
    phase = events[markers[j][0] + 1:markers[j + 1][0]]
    kinds = Counter(event[0] for event in phase)
    climbs = [event for event in phase if event[0] == "climb"]
    scalars = [event for event in phase if event[0] == "scalar"]
    need(len(phase) == 4730 and kinds == {"scalar": 3738, "climb": 992},
         "pinned phase-A event schema/count drift")
    need(all(len(e) == 6 for e in climbs) and all(len(e) == 3 for e in scalars),
         "phase-A event arity drift")
    scalar_kinds = Counter(e[1][0] for e in scalars)
    need(scalar_kinds == {"add": 3252, "scale": 486}, "phase-A scalar operations changed")
    need(not any(e[0] in ("product", "bilinear_child") for e in phase),
         "phase A now exposes bilinear child labels; re-open source mapping")
    return {
        "archive": archive_path,
        "phase": "A",
        "events": len(phase),
        "event_types": dict(kinds),
        "scalar_gate_types": dict(scalar_kinds),
        "climb_record_arity": 6,
        "scalar_record_arity": 3,
        "explicit_bilinear_operand_pairs": False,
        "result": "This event stream alone cannot identify repeated exact bilinear operand pairs; no selected-provider occurrence is established."
    }


def certificate() -> dict:
    task = json.loads((PACKAGE / "TASK.json").read_text(encoding="utf-8"))
    return {
        "status": "PASS_TRIPLE_SHARED_PRODUCT_LOCAL_CONSTRUCTION",
        "seed": task["seed"],
        "track": task["track"],
        "task_id": task["task_id"],
        "base_commit": task["base_commit"],
        "selected_record_sha256": task["selected_record_sha256"],
        "source_sha256": pins(),
        "tensor": tensor_checks(),
        "reversible_schedule": dirty_schedule_checks(),
        "profile_screen": profile_screen(),
        "selected_phase_a_schema": phase_a_schema_screen(),
        "selected_occurrence_identified": False,
        "new_supplier_or_kappa_claim": False,
    }


def main() -> None:
    expected = certificate()
    import sys
    if "--emit-certificate" in sys.argv[1:]:
        print(json.dumps(expected, indent=2, sort_keys=True))
        return
    actual = json.loads((PACKAGE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    need(actual == expected, "certificate differs from exact replay")
    print("PASS_TRIPLE_SHARED_PRODUCT_LOCAL_CONSTRUCTION rank=4 children=6->5 thresholds=764,765,766")


if __name__ == "__main__":
    main()
