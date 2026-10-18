# SPDX-License-Identifier: Apache-2.0
"""Price the independently optimal L253/L254 schedules including their shared ADD."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
from itertools import product
import argparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PAIR = ROOT / "research/complex-temporal-gauge-pair-seed26"
SINGLE = ROOT / "research/k8-varying-gauge-seed37/search.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pow2(k):
    return Fraction(2**k) if k >= 0 else Fraction(1, 2**(-k))


def price(q):
    a, d = abs(q.numerator), q.denominator
    v = (a & -a).bit_length() - 1
    p = a >> v
    e = v - (d.bit_length() - 1)
    return 1 + p.bit_length() + p.bit_count() + abs(e) - int(p == 1 and e == 0)


def joint_optimize(events, helpers=(253, 254), lo=-4, hi=4):
    """Exact two-coordinate chain DP on the stated per-event exponent box."""
    h0, h1 = helpers
    terms = []
    for i, event in enumerate(events):
        if event[0] != "scalar" or event[1][0] != "add":
            continue
        gate = event[1]
        signs = []
        for h in helpers:
            signs.append(int(gate[1] == ["L", h]) - int(gate[2] == ["L", h]))
        if any(signs):
            terms.append((i, Fraction(gate[3], gate[4]), *signs))
    shared = [i for i, _, s0, s1 in terms if s0 and s1]
    states = list(product(range(lo, hi + 1), repeat=2))
    zero = (0, 0)
    # Values: cost, scale macro count, total variation, lexical path rank.
    dp = {zero: (0, 0, 0, 0)}
    parents = []
    edge_evaluations = 0
    for _, q, s0, s1 in terms:
        next_dp, layer_parent = {}, {}
        for new in states:
            if not s0 and new[0] not in (old[0] for old in dp):
                continue
            if not s1 and new[1] not in (old[1] for old in dp):
                continue
            node = price(q * pow2(s0 * new[0] + s1 * new[1])) - price(q)
            best = None
            best_old = None
            for old, value in dp.items():
                if (not s0 and new[0] != old[0]) or (not s1 and new[1] != old[1]):
                    continue
                edge_evaluations += 1
                d0, d1 = abs(new[0] - old[0]), abs(new[1] - old[1])
                candidate = (value[0] + d0 + d1 + node,
                             value[1] + int(d0 != 0) + int(d1 != 0),
                             value[2] + d0 + d1,
                             value[3])
                if best is None or candidate < best:
                    best, best_old = candidate, old
            if best is not None:
                next_dp[new] = best
                layer_parent[new] = best_old
        # Assign a stable lexicographic rank to the selected paths at this layer.
        ordered = sorted(next_dp, key=lambda state: (next_dp[state][3], state))
        next_dp = {state: (*next_dp[state][:3], rank) for rank, state in enumerate(ordered)}
        parents.append(layer_parent)
        dp = next_dp
    terminal = min((value[0] + abs(state[0]) + abs(state[1]),
                    value[1] + int(state[0] != 0) + int(state[1] != 0),
                    value[2] + abs(state[0]) + abs(state[1]), value[3], state)
                   for state, value in dp.items())
    state = terminal[4]
    path = [None] * len(terms)
    for j in range(len(terms) - 1, -1, -1):
        path[j] = state
        state = parents[j][state]
    schedules = {h0: [], h1: []}
    for (event_id, *_), pair in zip(terms, path):
        schedules[h0].append([event_id, pair[0]])
        schedules[h1].append([event_id, pair[1]])
    return {
        "delta_real": terminal[0],
        "scale_macros": terminal[1],
        "total_variation": terminal[2],
        "domain": [lo, hi],
        "union_events": len(terms),
        "states_per_event": len(states),
        "edge_evaluations": edge_evaluations,
        "shared_add_ids": shared,
        "schedules": schedules,
    }


def apply(events, word, schedules, omit_scale=None):
    """Apply additive offsets to an already frozen PR1263 static word."""
    by_helper = {h: dict(rows) for h, rows in schedules.items()}
    current = {h: 0 for h in by_helper}
    output = [deepcopy(events[0])]
    for i, original in enumerate(events[1:-1], start=1):
        event = deepcopy(original)
        for h in sorted(by_helper):
            if i in by_helper[h]:
                new = by_helper[h][i]
                if new != current[h]:
                    if omit_scale != (h, i):
                        q = pow2(new - current[h])
                        output.append(["scalar", ["scale", ["L", h], q.numerator, q.denominator], event[2]])
                current[h] = new
        if event[0] == "scalar" and event[1][0] == "add":
            gate = event[1]
            shift = 0
            if gate[1][0] == "L" and gate[1][1] in current:
                shift += current[gate[1][1]]
            if gate[2][0] == "L" and gate[2][1] in current:
                shift -= current[gate[2][1]]
            q = Fraction(gate[3], gate[4]) * pow2(shift)
            gate[3:5] = [q.numerator, q.denominator]
        output.append(event)
    for h in sorted(current):
        if current[h]:
            q = pow2(-current[h])
            output.append(["scalar", ["scale", ["L", h], q.numerator, q.denominator], word["final"][h]])
    output.append(deepcopy(events[-1]))
    return output


def must_reject(lib, events, orientation, label):
    try:
        lib.replay(events, orientation)
    except (ValueError, AssertionError):
        return label
    raise ValueError(label + " control unexpectedly accepted")


def compute():
    parent = load("pinned_pr1263_verify", PAIR / "vendor/pr1263/verify.py")
    parent.ROOT = ROOT
    parent_result, static_words = parent.compute()  # validates the pinned source and construction
    selected_bytes = (ROOT / "certificates/selected-result.json").read_bytes()
    selected_sha = hashlib.sha256(selected_bytes).hexdigest()
    if selected_sha != "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32":
        raise ValueError("selected-result pin changed")
    lib = parent.engine()
    word, programs, *_ = lib.load()
    if parent_result["status"] != "PASS_MANY_HELPER_DYADIC_CONSTRUCTION":
        raise ValueError("pinned PR1263 construction status")
    gauge = load("pinned_temporal_optimizer", SINGLE)
    cert = json.loads((PAIR / "inputs/PR1350-CERTIFICATE.json").read_bytes())
    result = {
        "status": "PASS_L253_L254_JOINT_BOX",
        "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
        "selected_record_sha256": selected_sha,
        "selected_kappa_unchanged": "836330098538459/500000000000000000",
        "predecessors": {"pr1263": "5fbaca13028846bddbb001e8e07addc2ab8e5816",
                         "pr1350": "64b8a55c6933ffb6d9e30fa19f85d05b572d4aa5"},
        "scope": "Joint offsets for L253/L254 on the frozen PR1263 word, with each offset in [-4,4] at every union ADD; every other static gauge is fixed.",
        "orientations": {},
    }
    for orientation in ("forward", "backward"):
        events = static_words[orientation]
        terms253 = gauge.incident(events, 253)
        terms254 = gauge.incident(events, 254)
        opt254 = gauge.optimize(terms254)
        schedule253 = cert["orientations"][orientation]["schedule"]
        schedule254 = opt254["schedule"]
        composed = apply(events, word, {253: schedule253, 254: schedule254})
        independent_invoice = lib.invoice(composed, "copy-init")
        joint = joint_optimize(events)
        candidate = apply(events, word, joint["schedules"])
        invoice0 = lib.invoice(events, "copy-init")
        invoice1 = lib.invoice(candidate, "copy-init")
        endpoint = lib.replay(candidate, orientation)
        baseline_endpoint = lib.replay(events, orientation)
        shared = sorted(set(i for i, _, _ in terms253) & set(i for i, _, _ in terms254))
        independent_schedules = {"253": schedule253, "254": schedule254}
        shared_offsets = {
            str(h): dict(joint["schedules"][h]).get(shared[0]) for h in (253, 254)
        }
        incident_ids = {
            253: {i for i, _, _ in terms253},
            254: {i for i, _, _ in terms254},
        }
        joint_matches_independent = {
            "253": [[i, k] for i, k in joint["schedules"][253] if i in incident_ids[253]] == schedule253,
            "254": [[i, k] for i, k in joint["schedules"][254] if i in incident_ids[254]] == schedule254,
        }
        candidate_bytes = json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode()
        controls = []
        shared_mutant = deepcopy(candidate)
        changed_shared = False
        for event in shared_mutant:
            if event[0] != "scalar" or event[1][0] != "add":
                continue
            gate = event[1]
            if {tuple(gate[1]), tuple(gate[2])} >= {("L", 253), ("L", 254)}:
                q = Fraction(gate[3], gate[4]) * 2
                gate[3:5] = [q.numerator, q.denominator]
                changed_shared = True
                break
        need(changed_shared, orientation + " shared ADD mutation target exists")
        controls.append(must_reject(lib, shared_mutant, orientation, "shared_ADD_coefficient"))
        omitted = None
        for h in (253, 254):
            previous = 0
            for event_id, exponent in joint["schedules"][h]:
                if exponent != previous:
                    omitted = (h, event_id)
                    break
                previous = exponent
            if omitted is not None:
                break
        need(omitted is not None, orientation + " nonzero gauge transition exists")
        h, event_id = omitted
        omitted_mutant = apply(events, word, joint["schedules"], omit_scale=(h, event_id))
        controls.append(must_reject(lib, omitted_mutant, orientation, "omitted_transition_scale"))
        row = {
            "baseline_complex": invoice0["complex_primitives"],
            "candidate_complex": invoice1["complex_primitives"],
            "baseline_real": invoice0["real_primitives"],
            "candidate_real": invoice1["real_primitives"],
            "complex_saving": invoice0["complex_primitives"] - invoice1["complex_primitives"],
            "real_saving": invoice0["real_primitives"] - invoice1["real_primitives"],
            "paid_profile_unchanged": invoice0["paid_profile"] == invoice1["paid_profile"],
            "payload_bits": invoice1["charged_payload_bits"],
            "prefix_bits": invoice1["prefix_bits"],
            "formal_columns": endpoint["formal_input_columns"],
            "all_restored": endpoint["all_restored"],
            "shared_add_ids": shared,
            "L253_delta_real": cert["orientations"][orientation]["incremental_delta_real"],
            "L254_delta_real": opt254["delta_real"],
            "L254_domain": opt254["domain"],
            "L254_scale_macros": opt254["scale_macros"],
            "L253_schedule": schedule253,
            "L254_schedule": schedule254,
            "independent_composition_complex": independent_invoice["complex_primitives"],
            "joint_delta_real": joint["delta_real"],
            "joint_scale_macros": joint["scale_macros"],
            "joint_total_variation": joint["total_variation"],
            "joint_domain": joint["domain"],
            "joint_union_events": joint["union_events"],
            "joint_states_per_event": joint["states_per_event"],
            "joint_edge_evaluations": joint["edge_evaluations"],
            "joint_shared_add_ids": joint["shared_add_ids"],
            "joint_schedules": joint["schedules"],
            "joint_schedule_equals_independent": {
                str(h): joint_matches_independent[str(h)] for h in (253, 254)
            },
            "shared_add_offsets": shared_offsets,
            "candidate_word_sha256": hashlib.sha256(candidate_bytes).hexdigest(),
            "negative_controls": controls,
        }
        need(endpoint["formal_input_columns"] == 712 and endpoint["all_restored"],
             orientation + " all 712 formal columns and restoration")
        need(row["paid_profile_unchanged"] and row["payload_bits"] == 192
             and row["prefix_bits"] <= 192, orientation + " paid profile and precision charge")
        need(baseline_endpoint["formal_input_columns"] == 712,
             orientation + " baseline positive control")
        need(len(shared) == 1 and shared == joint["shared_add_ids"],
             orientation + " complete one-shared-ADD incidence")
        need(row["real_saving"] == -joint["delta_real"]
             and row["complex_saving"] == 2 * row["real_saving"],
             orientation + " DP agrees with complete invoice")
        need(row["candidate_complex"] == row["independent_composition_complex"],
             orientation + " joint optimum matches independently composed invoice")
        need(shared_offsets == {"253": 0, "254": 0},
             orientation + " optimal offsets at shared ADD")
        need(row["candidate_complex"] < row["baseline_complex"],
             orientation + " strict complete scalar saving")
        result["orientations"][orientation] = row
    return result


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the deterministic RESULT.json")
    args = parser.parse_args()
    result = compute()
    result_bytes = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    result_path = HERE / "RESULT.json"
    if args.write:
        result_path.write_bytes(result_bytes)
    elif not result_path.is_file() or result_path.read_bytes() != result_bytes:
        raise ValueError("stored RESULT.json differs from exact replay; rerun with --write to update")
    print("PASS_L253_L254_JOINT_BOX",
          "forward_saving_complex", result["orientations"]["forward"]["complex_saving"],
          "backward_saving_complex", result["orientations"]["backward"]["complex_saving"],
          "shared", result["orientations"]["forward"]["shared_add_ids"],
          "joint_box", result["orientations"]["forward"]["joint_domain"],
          "events", result["orientations"]["forward"]["joint_union_events"])


if __name__ == "__main__":
    main()
