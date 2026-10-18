#!/usr/bin/env python3
"""Reproduce the singleton census and test basis-character isolation."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "rank7-idle-star-stream-obstruction"))

import algebra as A  # noqa: E402
import source as S  # noqa: E402

RESULT = HERE / "RESULT.json"
PORTS = 112
AXIS_LIMIT = 1 << 73


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_port_contexts():
    """Authenticate the full fill, then independently group all owner-zero rows."""
    base_context = S.load_context()
    vendor = S.PACKAGE / "vendor"
    base = S.decode(S.read_bytes(vendor / "BASE-FILL.json.gz"))["rows"]
    journal = S.decode(S.read_bytes(vendor / "EXCHANGE.json"))
    edits = S.journal_edits(base, journal)
    rows = defaultdict(list)
    for index in range(S.TOTAL_ROWS):
        row = edits[index] if index in edits else S.lifted_row(base, index)
        if row[2] == 0:
            require(type(row[4]) is int and 0 <= row[4] < PORTS, "owner-zero port range")
            rows[row[4]].append(row)
    require(set(rows) == set(range(PORTS)), "all owner-zero ports present")
    require(rows[0] == base_context["rows"], "port-zero source projection")
    recipes = S.decode(S.read_bytes(S.ROOT / S.PHASES))["recipes"]
    require(len(recipes) == PORTS, "recipe count")
    require(all(recipe["port"] == port for port, recipe in enumerate(recipes)), "recipe order")
    return base_context, rows, recipes


def host_and_residual(context):
    """Reconstruct hosted slices and remaining axes for one exact port."""
    recipe, plan = context["recipe"], context["plan"]
    used, hosts = defaultdict(set), defaultdict(list)
    for time, helper, owner, child, port, offset in context["rows"]:
        require(owner == 0 and port == recipe["port"], "role owner and port")
        require(0 <= time < len(context["order"]), "host chronology index")
        require(0 <= child < len(recipe["idle_children"]), "host child index")
        stage, replica = context["order"][time]
        tag = context["dispatch"][stage, replica % 74]
        width = context["providers"][tag]["widths"][helper]
        axes = [int(v) for v in recipe["idle_children"][child]["orthogonal_axes"]]
        require(type(width) is int and width > 0, "positive provider width")
        require(0 <= offset and offset + width <= len(axes), "hosted slice bounds")
        positions = set(range(offset, offset + width))
        require(not (used[child] & positions), "hosted slice overlap")
        used[child].update(positions)
        stream = 2 * plan["pairs"][str(child)] + plan["sides"][str(child)]
        hosts[time].append((stream, axes[offset : offset + width]))

    residual, full = {}, {}
    for child, entry in enumerate(recipe["idle_children"]):
        axes = [int(v) for v in entry["orthogonal_axes"]]
        require(all(type(v) is int and 0 < v < AXIS_LIMIT for v in axes), "73-bit axes")
        require(
            all(A.dot(v, w) == int(i == j)
                for i, v in enumerate(axes) for j, w in enumerate(axes)),
            "within-child orthonormal axes",
        )
        require(used[child] == set(range(len(used[child]))), "compact hosted prefix")
        full[child] = len(axes)
        residual[child] = [v for i, v in enumerate(axes) if i not in used[child]]
    return residual, hosts, full


def scalar(character):
    return [
        [A.rotate((1, 0), character.bit_count()) if i == j else (0, 0)
         for j in range(8)]
        for i in range(8)
    ]


def replay(context, blocks, hosts, residual, character):
    """Run the unchanged eight-stream event semantics on one residual assignment."""
    require(type(character) is int and 0 <= character < AXIS_LIMIT, "73-bit character")
    matrix = A.identity()
    for time, (stage, replica) in enumerate(context["order"]):
        for stream, axes in hosts.get(time, ()):
            A.phase(matrix, stream, sum(A.dot(character, axis) for axis in axes))
        if replica == 0:
            for event in blocks[stage]:
                A.data_event(matrix, event, context, residual, character)
    return matrix


def declared_rule(recipe, current, donor, receiver, axis):
    """The stated PR3190 per-axis commuting condition, without its move code."""
    translations = [
        int(stage[key])
        for stage in recipe["stage_alignment"]
        for key in ("entry_X", "exit_X", "entry_Y", "exit_Y")
    ]
    translations.append(int(recipe["terminal_Y_translation"]))
    translations.extend(
        int(recipe["idle_children"][child]["translation_after"])
        for child in (donor, receiver)
    )
    return (
        donor != receiver
        and axis in current[donor]
        and all(A.dot(axis, other) == 0
                for other in current[receiver] + translations)
    )


def apply_moves(recipe, original, moves):
    """Apply distinct moves in order, checking the declared rule and final ranks."""
    final = {child: list(axes) for child, axes in original.items()}
    moved = set()
    for donor, receiver, axis in moves:
        require((donor, axis) not in moved, "one source axis cannot be moved twice")
        require(declared_rule(recipe, final, donor, receiver, axis), "declared move rule")
        moved.add((donor, axis))
        final[donor].remove(axis)
        final[receiver].append(axis)
    for axes in final.values():
        require(len(axes) <= 51, "final child rank cap")
        require(
            all(A.dot(v, w) == int(i == j)
                for i, v in enumerate(axes) for j, w in enumerate(axes)),
            "final within-child orthonormal axes",
        )
    return final


def difference_count(left, right):
    return sum(left[i][j] != right[i][j] for i in range(8) for j in range(8))


def differences(left, right):
    return [
        [i, j, list(left[i][j]), list(right[i][j])]
        for i in range(8)
        for j in range(8)
        if left[i][j] != right[i][j]
    ]


def fail_control(call, label):
    try:
        call()
    except ValueError:
        return
    raise ValueError(label + " failure control was accepted")


def find_pair_control(port, recipe, original, candidates):
    by_axis = defaultdict(list)
    for move in candidates:
        by_axis[move[2]].append(move)
    axes = sorted(by_axis)
    for left_index, left_axis in enumerate(axes):
        for right_axis in axes[left_index + 1 :]:
            if A.dot(left_axis, right_axis) != 0:
                continue
            for left in by_axis[left_axis]:
                for right in by_axis[right_axis]:
                    try:
                        bundled = apply_moves(recipe, original, [left, right])
                    except ValueError:
                        continue
                    return left, right, bundled
    return None


def census():
    base_context, rows_by_port, recipes = load_port_contexts()
    blocks = A.stage_blocks(base_context["template"])
    per_port, summary = {}, Counter()
    pair_control = None
    positive_control = None
    for port in range(PORTS):
        context = dict(base_context, rows=rows_by_port[port], recipe=recipes[port])
        residual, hosts, full = host_and_residual(context)
        counts = Counter()
        baseline_by_axis = {}
        candidates = []
        for donor, axes in residual.items():
            if not axes or len(axes) == full[donor]:
                continue  # only a hosted child with a nonempty remainder is a donor
            for receiver in residual:
                if receiver == donor or full[receiver] == 0:
                    continue
                for axis in axes:
                    counts["raw_candidates"] += 1
                    if not declared_rule(recipes[port], residual, donor, receiver, axis):
                        counts["rule_rejects"] += 1
                        continue
                    counts["rule_passes"] += 1
                    try:
                        final = apply_moves(recipes[port], residual, [(donor, receiver, axis)])
                    except ValueError:
                        counts["final_validity_rejects"] += 1
                        continue
                    counts["final_valid_singletons"] += 1
                    candidates.append((donor, receiver, axis))
                    if axis not in baseline_by_axis:
                        baseline = replay(context, blocks, hosts, residual, axis)
                        require(baseline == scalar(axis), "singleton-character scalar baseline")
                        baseline_by_axis[axis] = baseline
                    after = replay(context, blocks, hosts, final, axis)
                    delta = difference_count(baseline_by_axis[axis], after)
                    if delta:
                        counts["changed_at_own_character"] += 1
                    else:
                        counts["preserved_at_own_character"] += 1

        require(counts["preserved_at_own_character"] == 0,
                "some admissible singleton preserved the operator at its moved-axis character")
        counts["distinct_singleton_characters"] = len(baseline_by_axis)
        for key in (
            "raw_candidates",
            "rule_rejects",
            "rule_passes",
            "final_validity_rejects",
            "final_valid_singletons",
            "changed_at_own_character",
            "preserved_at_own_character",
            "distinct_singleton_characters",
        ):
            counts.setdefault(key, 0)
        if positive_control is None and candidates:
            donor, receiver, axis = candidates[0]
            empty = replay(context, blocks, hosts, residual, axis)
            require(empty == baseline_by_axis[axis], "empty-overlay positive control")
            fail_control(
                lambda: apply_moves(recipes[port], residual, [(donor, donor, axis)]),
                "self-transfer",
            )
            alternative = next(
                (v for child_axes in recipes[port]["idle_children"]
                 for v in map(int, child_axes["orthogonal_axes"])
                 if v not in residual[donor]),
                None,
            )
            if alternative is not None:
                fail_control(
                    lambda: apply_moves(recipes[port], residual, [(donor, receiver, alternative)]),
                    "axis absent from donor",
                )
            positive_control = {
                "port": port,
                "character": axis,
                "empty_overlay_equals_baseline": True,
                "self_transfer_rejected": True,
                "axis_absent_from_donor_rejected": alternative is not None,
            }

        if pair_control is None and candidates:
            pair = find_pair_control(port, recipes[port], residual, candidates)
            if pair is not None:
                left, right, bundled = pair
                left_single = apply_moves(recipes[port], residual, [left])
                right_single = apply_moves(recipes[port], residual, [right])
                comparisons = []
                for move, single in ((left, left_single), (right, right_single)):
                    axis = move[2]
                    require(A.dot(left[2], right[2]) == 0, "pair-control orthogonality")
                    baseline = baseline_by_axis[axis]
                    singleton_matrix = replay(context, blocks, hosts, single, axis)
                    bundle_matrix = replay(context, blocks, hosts, bundled, axis)
                    require(singleton_matrix != baseline, "pair-control singleton changes")
                    require(
                        bundle_matrix == singleton_matrix,
                        "two-move isolation equality",
                    )
                    comparisons.append({
                        "character": axis,
                        "baseline": baseline,
                        "singleton": singleton_matrix,
                        "bundle": bundle_matrix,
                        "singleton_difference_count": difference_count(baseline, singleton_matrix),
                        "singleton_differences": differences(baseline, singleton_matrix),
                    })
                pair_control = {
                    "port": port,
                    "moves": [
                        [left[0], left[1], left[2]],
                        [right[0], right[1], right[2]],
                    ],
                    "characters": [left[2], right[2]],
                    "axis_dot": 0,
                    "bundle_equals_each_singleton_at_its_character": True,
                    "character_comparisons": comparisons,
                }
        per_port[str(port)] = dict(counts)
        summary.update(counts)

    require(positive_control is not None, "at least one positive control")
    require(pair_control is not None, "at least one legal orthogonal pair control")
    require(summary["raw_candidates"] == 9384, "expected raw hosted-remainder domain")
    require(summary["rule_passes"] == 3809, "expected declared-rule count")
    require(summary["final_valid_singletons"] == 3809, "expected final-valid singleton count")
    require(summary["changed_at_own_character"] == 3809, "every admissible singleton changes")
    require(summary["rule_rejects"] == 5575, "expected declared-rule rejects")
    require(summary["final_validity_rejects"] == 0, "no post-rule singleton rejection")
    no_pass_ports = sum(p["rule_passes"] == 0 for p in per_port.values())
    require(no_pass_ports == 47, "expected ports with no singleton admitted by the declared rule")
    summary["ports_with_no_rule_passes"] = no_pass_ports
    result = {
        "status": "PASS_DISTINCT_AXIS_OVERLAY_ISOLATION",
        "source_base_commit": "463113d675af7410ac91d53a4fed51ec6494eb9a",
        "audited_owner_replica": 0,
        "ports": PORTS,
        "authenticated_fill_rows": S.TOTAL_ROWS,
        "fill_payload_sha256": S.FILL_SHA,
        "cover": "identity",
        "operator": "exact eight-stream Gaussian-integer replay from PR3187",
        "singleton_domain": "hosted remainder donor with nonempty remainder; distinct receiver with nonempty full axis list (hosted receivers admitted); PR3190 commuting rule; final rank <= 51 and within-child orthonormality",
        "per_port": per_port,
        "summary": dict(summary),
        "positive_control": positive_control,
        "orthogonal_pair_control": pair_control,
        "scope_note": "The receiver domain relaxes PR3190's construction restrictions. The theorem covers only finite legal overlays whose moved axes are pairwise orthogonal and whose components lie in that enumerated singleton domain.",
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the regenerated RESULT.json")
    args = parser.parse_args()
    result = json.loads(json.dumps(census()))
    if args.write:
        RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        expected = json.loads(S.read_bytes(RESULT))
        require(result == expected, "stored RESULT.json differs from exact replay")
    counts = result["summary"]
    print(
        "PASS_DISTINCT_AXIS_OVERLAY_ISOLATION ports=112 candidates=%d admissible=%d changed=%d pair_control=yes"
        % (counts["raw_candidates"], counts["changed_at_own_character"], counts["changed_at_own_character"])
    )


if __name__ == "__main__":
    main()
