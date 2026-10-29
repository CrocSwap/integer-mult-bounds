#!/usr/bin/env python3
"""Source-bound boundary map for PR2013's four-end attaining assignment.

This checks local native cone obligations and a prior two-end recipe match.
It deliberately does not claim phase, wrapper, owner-map, or outer-call admission.
"""

from collections import Counter
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_PACKAGE = ROOT / "research/selected-k8-unrestricted-ends"
sys.path.insert(0, str(SOURCE_PACKAGE))

import common as U  # noqa: E402
import model as X  # noqa: E402


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def frame_for(node, raw, base):
    if node in raw:
        return raw[node]
    return base.frame_of(node, base.baseline())


def run():
    word = U.word()
    expected = U.parse((SOURCE_PACKAGE / "EXPECTED.json").read_bytes())
    primal = U.primal_data()
    recipe = U.parse(
        (SOURCE_PACKAGE / "references/END-RECIPE.json").read_bytes()
    )
    need(U.digest(primal) == expected["primal_sha256"], "primal source binding")

    raw = {tuple(json.loads(k)): tuple(v) for k, v in primal["assignment"].items()}
    base = X.M.Model(word)
    profile = {int(r): int(n) for r, n in primal["profile"].items()}
    need(profile == {int(r): n for r, n in expected["profile"].items()},
         "candidate profile binding")
    local_mass = sum(r * n for r, n in profile.items())
    total_paid_mass = 72 * 896 // 9 + 64
    idle_mass = total_paid_mass - local_mass
    need((local_mass, idle_mass) == (5582, 1650), "full idle recharge")
    need(total_paid_mass == 7232, "coverage identity")
    need(idle_mass != 1646, "negative control: stale selected idle mass")

    changed = [574, 575, 580, 581]
    need(expected["attaining_changed_ends"] == changed, "four-end inventory")
    old_caps = {int(q): X.M.basis(U) for q, U in word["helper_final"].items()}
    supports = X.cone_supports(word, base.n, base.v)

    boundary = {}
    for k, chain in base.chains.items():
        before_tail = [
            node for node in chain
            if node[0] in ("S", "P")
            or (node[0] == "G" and node[1] < base.nA + base.nB)
        ]
        boundary[k] = before_tail[-1]

    expected_sources = {574: 412, 575: 414, 580: 424, 581: 86}
    interface_rows = []
    for q in changed:
        end = raw[("E", q)]
        need(len(old_caps[q]) == 8 and len(end) == 7, "rank-one end change")
        ks = sorted(supports[q])
        need(ks == [expected_sources[q]], "source-support map")
        k = ks[0]
        b = boundary[k]
        need(b[0] == "G" and b[1] >= base.nA, "source last-use gate")
        gate_index = b[1]
        gate = base.gates[gate_index][1]
        need(k in base.regs[gate_index], "source register at gate")
        boundary_frame = frame_for(b, raw, base)
        need(X.M.contained(boundary_frame, end), "native cone containment")
        need(not X.M.contained(boundary_frame, ()),
             "negative control: missing end must fail the source containment")
        interface_rows.append({
            "changed_helper": q,
            "old_end": list(old_caps[q]),
            "candidate_end": list(end),
            "source_register": k,
            "last_use_gate": ["B", gate_index - base.nA],
            "last_use_operation": gate,
            "required_boundary_frame": list(boundary_frame),
            "containment_pass": True,
        })

    recipe_ends = {row[0]: tuple(row[2]) for row in recipe["ends"]}
    prior_end_matches = {
        str(q): raw[("E", q)] == recipe_ends[q]
        for q in (574, 575)
    }
    need(all(prior_end_matches.values()), "prior two-end endpoint match")
    prior_b_matches = []
    for i, old_frame, new_frame in recipe["B_frames"]:
        gate_index = base.nA + i
        candidate_frame = frame_for(("G", gate_index), raw, base)
        prior_b_matches.append(candidate_frame == tuple(new_frame))
    need(len(prior_b_matches) == 8 and all(prior_b_matches),
         "prior two-end B-frame match")
    tail_index_to_gate = {
        cleanup_index: base.nA + base.nB + j
        for j, (cleanup_index, _frame) in enumerate(word["early_cleanup"])
    }
    prior_tail_matches = []
    for cleanup_index, _helper, _old_frame, new_frame in recipe["early_cleanup"]:
        gate_index = tail_index_to_gate[cleanup_index]
        candidate_frame = frame_for(("G", gate_index), raw, base)
        prior_tail_matches.append(candidate_frame == tuple(new_frame))
    need(len(prior_tail_matches) == 2 and all(prior_tail_matches),
         "prior two-end cleanup-frame match")

    frame_changes = Counter()
    for i, (kind, event) in enumerate(base.gates):
        candidate_frame = frame_for(("G", i), raw, base)
        if candidate_frame != tuple(event[-1]):
            frame_changes[{"A": "A", "B": "B", "T": "early_cleanup"}[kind]] += 1
    need(dict(frame_changes) == {"A": 61, "B": 94, "early_cleanup": 4},
         "candidate frame-change inventory")
    extra_frame_changes = {
        "A": frame_changes["A"],
        "B": frame_changes["B"] - len(prior_b_matches),
        "early_cleanup": frame_changes["early_cleanup"] - len(prior_tail_matches),
    }
    need(extra_frame_changes == {"A": 61, "B": 86, "early_cleanup": 2},
         "frame changes beyond prior physical recipe")
    need(sum(extra_frame_changes.values()) == 149, "extra frame-change count")

    baseline_profile = {
        int(r): int(n) for r, n in word["report"]["local_profile"].items()
    }
    profile_delta = {
        str(r): profile.get(r, 0) - baseline_profile.get(r, 0)
        for r in sorted(set(profile) | set(baseline_profile))
        if profile.get(r, 0) != baseline_profile.get(r, 0)
    }
    need(profile_delta == {"1": -12, "2": 28, "3": -16}, "rank profile delta")
    need(sum(r * n for r, n in baseline_profile.items()) == 5586,
         "selected profile mass")
    need(total_paid_mass - sum(r * n for r, n in baseline_profile.items()) == 1646,
         "selected idle mass")

    return {
        "schema": "complex-four-end-caller-map-v1",
        "status": "PASS_FOUR_END_CALLER_MAP_LOCAL_ONLY",
        "word_sha256": U.WORD_SHA,
        "candidate_ends": interface_rows,
        "profile_delta": profile_delta,
        "local_mass": local_mass,
        "idle_mass": idle_mass,
        "total_paid_mass": total_paid_mass,
        "controls": {
            "empty_endpoint_rejected": 4,
            "stale_idle_mass_1646_rejected": True,
        },
        "prior_two_end_recipe": {
            "endpoint_matches": prior_end_matches,
            "b_frame_matches": sum(prior_b_matches),
            "cleanup_frame_matches": sum(prior_tail_matches),
            "candidate_frame_changes": dict(sorted(frame_changes.items())),
            "additional_frame_changes": extra_frame_changes,
        },
        "outer_call_admission": "UNRESOLVED",
        "outer_call_reason": (
            "The pinned PR2013 proof records no phase/wrapper admission, new complete "
            "physical owner allocation, or outer invoice for this four-end assignment. "
            "Its two-end predecessor matches only two of four ends and 10 of the "
            "candidate's 159 changed frame annotations."
        ),
        "scope": (
            "The four q-to-register native cone containments and local mass recharge "
            "are checked. Owner lifetimes, helper copies, source windows, restoration, "
            "phase/wrapper admission, and the outer invoice are not checked."
        ),
    }


def main():
    out = run()
    expected_path = HERE / "RESULT.json"
    if "--write" in sys.argv[1:]:
        expected_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    else:
        need(U.parse(expected_path.read_bytes()) == out, "receipt mismatch")
    print(out["status"], "changed_ends=4", "native_cones=4/4",
          "additional_frame_changes=149", "outer_call_admission=UNRESOLVED")


if __name__ == "__main__":
    main()
