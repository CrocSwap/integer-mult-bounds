#!/usr/bin/env python3
"""Four actual P104 source-query carriers from a dependency-preserving B reorder.

Run with Python 3.12+ and the standard library:
    python3 -I -B research/p104-interleaved-search/query_construction.py

This verifies source formation and the retained side word, not a complete new
multiplication schedule. The old centre cut is omitted. Four punctured Y roles
then contain minus one quarter of the required initial-live-X query, plus dirt
from initial frame-zero roles. Completing their B dependency closures first
makes those carriers available before the remaining side events. No register's
B event order changes, so its native transport path and charge are unchanged.

The successor still needs legal delivery after each source becomes available,
its compensation/restoration, all eight terms, hosting, and a full cost proof.
Sources and predecessor attribution are retained in this package's README.
New verifier prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "word": (
        "research/complex-block-rank-optimum/inputs/selected.json.gz",
        "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    ),
    "coordinates": (
        "research/frame-sa504/inputs/hamming/PROTOTYPE.json",
        "327d2a868043e846381aa58a33053c24425e8cad522ff401b10ec8af1d649a3f",
    ),
    "fixture": (
        "research/p104-native-channel/inputs/P104-FIXTURE.json",
        "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
    ),
}
REMOVED = (3, 14, 21, 34, 39, 61, 76, 93)
QUERY_ROOTS = (28, 47, 113, 57)
RETAINED_AXIS_ROOTS = (7, 0, 6, 5)
Q = Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_inputs():
    result = {}
    for name, (relative, expected) in INPUTS.items():
        data = (ROOT / relative).read_bytes()
        require(hashlib.sha256(data).hexdigest() == expected, f"source hash: {relative}")
        result[name] = json.loads(gzip.decompress(data) if relative.endswith(".gz") else data)
    return result


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def span(frame):
    result = {0}
    for vector in frame:
        result |= {x ^ vector for x in tuple(result)}
    require(len(result) == 1 << len(frame), "dependent frame basis")
    return frozenset(result)


def touched(event):
    return event[1:3] if event[0] == "add" else event[1:2]


def identity(n):
    return [{i: Q(1)} for i in range(n)]


def apply(event, rows):
    if event[0] == "scale":
        coefficient = Q(event[2], event[3])
        require(bool(coefficient), "noninvertible zero scale")
        rows[event[1]] = {j: coefficient * x for j, x in rows[event[1]].items()}
    else:
        require(event[0] == "add" and event[1] != event[2], "invalid scalar event")
        target, source, coefficient = rows[event[1]], rows[event[2]], Q(event[3], event[4])
        for j, x in list(source.items()):
            value = target.get(j, Q(0)) + coefficient * x
            if value:
                target[j] = value
            else:
                target.pop(j, None)


def run(rows, events):
    for event in events:
        apply(event, rows)
    return rows


def serial_row(row):
    return {str(j): str(row[j]) for j in sorted(row)}


def row_digest(row):
    return hashlib.sha256(json.dumps(serial_row(row), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def geometry(inputs, query_roots=QUERY_ROOTS):
    word, prototype = inputs["word"], inputs["coordinates"]
    roots, labels = prototype["root_lines"], prototype["binary_ports"]
    native = inputs["fixture"]["section4_explicit_P104"]
    transform = lambda x: x ^ (43 if (x & 43).bit_count() % 2 else 0)
    root_index = {tuple(root): j for j, root in enumerate(roots)}
    root_by_label = {transform(label): root for label, root in zip(labels, roots)}
    selected = [root_by_label[label] for label in word["ports"]]
    deleted_labels = set()
    for c in native["C"]:
        products = [dot(c, f) for f in native["F0"]]
        require(all(x % 4 == 0 for x in products), "nonintegral fixture coordinates")
        root = tuple(x // 4 for x in products)
        if next(x for x in root if x) < 0:
            root = tuple(-x for x in root)
        deleted_labels.add(transform(labels[root_index[root]]))
    derived = tuple(j for j, label in enumerate(word["ports"]) if label in deleted_labels)
    require(derived == REMOVED, "P104 puncture mismatch")
    position = {root_index[tuple(selected[j])]: j for j in REMOVED}
    return selected, {
        q: {"register": word["v"] + position[q], "label": transform(labels[q]), "root": roots[q]}
        for q in query_roots
    }


def schedule(word, specs):
    """Close literal read/write/frame dependencies; greedily finish shortest next closure."""
    previous, dependencies = {}, []
    for j, event in enumerate(word["B"]):
        registers = touched(event)
        dependencies.append({previous[r] for r in registers if r in previous})
        for r in registers:
            previous[r] = j
    closures = {}
    for q, spec in specs.items():
        target = previous[spec["register"]]
        closure, todo = {target}, [target]
        while todo:
            for j in dependencies[todo.pop()]:
                if j not in closure:
                    closure.add(j)
                    todo.append(j)
        closures[q] = closure
    order, included, availability, priority = [], set(), {}, []
    while len(priority) != len(specs):
        q = min((q for q in specs if q not in availability),
                key=lambda q: (len(closures[q] - included), q))
        order.extend(sorted(closures[q] - included))
        included |= closures[q]
        availability[q] = len(order)
        priority.append(q)
    order.extend(j for j in range(len(word["B"])) if j not in included)
    require(sorted(order) == list(range(len(word["B"]))), "B permutation")
    # Stronger than scalar commutation: every frame-setting source read stays ordered too.
    for r in range(2 * word["v"] + word["R"]):
        original = [j for j, event in enumerate(word["B"]) if r in touched(event)]
        reordered = [j for j in order if r in touched(word["B"][j])]
        require(original == reordered, f"register {r} changed event order")
    return order, availability, closures, priority


def native_step(event, current, frame_sets, frames, profile):
    destination = event[-1]
    for r in touched(event):
        require(frame_sets[current[r]] <= frame_sets[destination], f"nonnested frame at register {r}")
        rank = len(frames[destination]) - len(frames[current[r]])
        if rank:
            profile[rank] += 1
        current[r] = destination


def native_run(events, current, frame_sets, frames):
    profile = Counter()
    for event in events:
        native_step(event, current, frame_sets, frames, profile)
    return profile


def verify():
    inputs = load_inputs()
    word = inputs["word"]
    v, n = word["v"], 2 * word["v"] + word["R"]
    require((v, n) == (112, 704), "selected word dimensions")
    selected, specs = geometry(inputs)
    live = [j for j in range(v) if j not in REMOVED]
    live_set = set(live)
    frames, frame_sets = word["frames"], list(map(span, word["frames"]))
    prefix = word["precondition"] + word["compensation"] + word["A"]
    before_B = run(identity(n), prefix)
    baseline = run([row.copy() for row in before_B], word["B"])
    order, availability, closures, priority = schedule(word, specs)
    rows = [row.copy() for row in before_B]
    current = list(word["start"])
    prefix_profile = native_run(prefix, current, frame_sets, frames)
    before_frames = current.copy()
    original_end_frames = current.copy()
    original_B_profile = native_run(word["B"], original_end_frames, frame_sets, frames)
    new_B_profile, records = Counter(), {}
    for j, original_j in enumerate(order):
        event = word["B"][original_j]
        native_step(event, current, frame_sets, frames, new_B_profile)
        apply(event, rows)
        for q, cut in availability.items():
            if j + 1 != cut:
                continue
            spec, register = specs[q], specs[q]["register"]
            wanted = {i: -Q(dot(selected[i], spec["root"]), 4) for i in live if dot(selected[i], spec["root"])}
            clean = {i: x for i, x in rows[register].items() if i in live_set}
            dirt = {i: x for i, x in rows[register].items() if i not in live_set}
            require(clean == wanted and len(clean) == 52, f"query {q} clean coefficients")
            require(rows[register] == baseline[register], f"query {q} not final at availability")
            require(all(not frames[word["start"][i]] for i in dirt), f"query {q} nonzero-entrance dirt")
            require(not any(v <= i < 2 * v and i - v in live_set for i in dirt), f"query {q} live initial Y")
            hyperplane = {x for x in range(512) if not (x & spec["label"]).bit_count() % 2}
            require(frame_sets[current[register]] == hyperplane, f"query {q} wrong frame")
            last_touch = max(k for k, e in enumerate(word["B"]) if register in touched(e))
            last_write = max(k for k, e in enumerate(word["B"]) if e[1] == register)
            records[str(q)] = {
                "register": register,
                "available_before_reordered_B_event": cut,
                "original_last_touch": last_touch,
                "original_last_write": last_write,
                "dependency_closure_events": len(closures[q]),
                "raw_query_coefficient": "-1/4",
                "multiplier_for_raw_query_over_8": "-1/2",
                "frame_basis": frames[current[register]],
                "live_X_columns": len(clean),
                "initial_frame_zero_dirty_columns": len(dirt),
                "nonzero_entrance_dirty_columns": 0,
                "initial_live_Y_columns": 0,
                "full_704_column_row_sha256": row_digest(rows[register]),
                "remaining_B_events": len(order) - cut,
                "live_Y_frame_rank_counts": {str(rank): count for rank, count in
                                             sorted(Counter(len(frames[current[v+t]]) for t in live).items())},
                "live_Y_already_at_final_frame": sum(current[v+t] == word["final"][v+t] for t in live),
            }
    require(rows == baseline, "reordered B differs on the full 704 by 704 matrix")
    require(current == original_end_frames, "reordered B frame endpoints")
    require(new_B_profile == original_B_profile, "reordered B transport profile")
    require(len(records) == 4, "missing query records")

    # Inventory all sixteen admissible source banks, without asserting that a
    # particular delivery can wait for the four unselected C banks. Coordinate
    # centres are available at A end; all C banks are available by B end.
    roots = inputs["coordinates"]["root_lines"]
    root_index = {tuple(root): i for i, root in enumerate(roots)}
    all_C_roots = sorted(root_index[tuple(selected[t])] for t in REMOVED)
    _, all_C_specs = geometry(inputs, all_C_roots)
    source_banks = {}
    for q in list(range(8)) + all_C_roots:
        is_coordinate = q < 8
        register = word["centers"][q] if is_coordinate else all_C_specs[q]["register"]
        row = before_B[register] if is_coordinate else baseline[register]
        coefficient = Q(1, 2) if is_coordinate else -Q(1, 4)
        wanted = {i: coefficient * dot(selected[i], roots[q]) for i in live if dot(selected[i], roots[q])}
        require({i: x for i, x in row.items() if i in live_set} == wanted, f"source bank {q} clean row")
        dirt = {i: x for i, x in row.items() if i not in live_set}
        require(not any(v <= i < 2*v and i-v in live_set for i in dirt), f"source bank {q} initial live Y")
        require(all(i in REMOVED or not frames[word["start"][i]] for i in dirt), f"source bank {q} nonzero-entrance dirt")
        label = (all_C_specs[q]["label"] if not is_coordinate else
                 inputs["coordinates"]["binary_ports"][q])
        if is_coordinate:
            label ^= 43 if (label & 43).bit_count() % 2 else 0
        current_frame = before_frames[register] if is_coordinate else original_end_frames[register]
        require(frame_sets[current_frame] == {x for x in range(512) if not (x & label).bit_count() % 2}, f"source bank {q} chart")
        source_banks[str(q)] = {
            "register": register,
            "raw_query_coefficient": str(coefficient),
            "live_X_columns": len(wanted),
            "initial_frame_zero_dirty_columns": sum(not frames[word["start"][i]] for i in dirt),
            "punctured_X_dirty_columns_reclassified_to_frame_zero": sum(i in REMOVED for i in dirt),
            "other_nonzero_entrance_dirty_columns": 0,
            "initial_live_Y_columns": 0,
            "frame_basis": frames[current_frame],
            "available_before_reordered_B_event": 0 if is_coordinate else availability.get(q, len(order)),
            "full_704_column_row_sha256": row_digest(row),
        }
    chosen_pairs = ((1, 28), (2, 47), (3, 113), (4, 57),
                    (12, 7), (65, 0), (82, 6), (97, 5))
    chosen_sources = []
    for aa, bb in chosen_pairs:
        coefficient = Q(source_banks[str(bb)]["raw_query_coefficient"])
        denominator = 4 * dot(roots[aa], roots[bb])
        require(denominator, "zero decoder denominator")
        chosen_sources.append({
            "a_root": aa, "b_root": bb,
            "register": source_banks[str(bb)]["register"],
            "raw_query_coefficient": str(coefficient),
            "multiplier_for_query_over_four_a_dot_b": str(1 / (denominator * coefficient)),
            "available_before_reordered_B_event": source_banks[str(bb)]["available_before_reordered_B_event"],
        })

    # A missing actual write must fail the source-row check, independently of the DAG check.
    q = priority[0]
    removed_event = records[str(q)]["original_last_write"]
    damaged = [row.copy() for row in before_B]
    run(damaged, [word["B"][k] for k in order[:availability[q]] if k != removed_event])
    require(damaged[specs[q]["register"]] != baseline[specs[q]["register"]], "missing-event control passed")
    clean = {i: x for i, x in baseline[specs[q]["register"]].items() if i in live_set}
    wrong = {i: -Q(dot(selected[i], specs[q]["root"]), 8) for i in live if dot(selected[i], specs[q]["root"])}
    require(clean != wrong, "wrong-query-normalization control passed")

    # The final 48 A operations gather the eight old coordinate centres. The
    # four unused coordinate gathers can be omitted for this source fragment.
    # This check deliberately does not claim their old cleanup remains valid.
    gather = word["A"][-48:]
    omitted = []
    for axis in range(8):
        group = gather[6 * axis:6 * axis + 6]
        require(len(group) == 6 and all(e[0] == "add" for e in group), "coordinate gather shape")
        centre = group[0][1]
        require(all(e[1] == centre for e in group), "coordinate gather target")
        require(not any(centre in touched(e) for e in word["B"]), "centre used in B")
        expected = {i: Q(selected[i][axis]) for i in range(v) if selected[i][axis]}
        actual = {i: x for i, x in before_B[centre].items() if i < v}
        require(actual == expected, "coordinate gather axis binding")
        if axis not in RETAINED_AXIS_ROOTS:
            omitted.extend(range(len(word["A"]) - 48 + 6 * axis, len(word["A"]) - 48 + 6 * axis + 6))
    require(len(omitted) == 24, "four old gathers")
    changed_A = [e for j, e in enumerate(word["A"]) if j not in set(omitted)]
    changed_prefix = word["precondition"] + word["compensation"] + changed_A
    changed = run(identity(n), changed_prefix + [word["B"][j] for j in order])
    require(all(changed[specs[q]["register"]] == baseline[specs[q]["register"]] for q in specs), "omitting gathers changed queries")
    require(all(changed[v+t] == baseline[v+t] for t in live), "omitting gathers changed live Y")
    changed_frames = list(word["start"])
    changed_profile = native_run(changed_prefix + [word["B"][j] for j in order], changed_frames, frame_sets, frames)
    original_profile = prefix_profile + original_B_profile
    delta = {str(k): changed_profile[k] - original_profile[k] for k in sorted(set(changed_profile) | set(original_profile)) if changed_profile[k] != original_profile[k]}

    return {
        "status": "FOUR_ACTUAL_DIRTY_QUERIES_NOT_COMPLETE_SUPPLIER",
        "source_sha256": {relative: digest for relative, digest in INPUTS.values()},
        "physical_registers": n,
        "live_ports": len(live),
        "punctured_selected_positions": list(REMOVED),
        "old_centre_cut_included": False,
        "query_priority": priority,
        "all_queries_available_before_B_event": max(availability.values()),
        "B_events": len(order),
        "B_events_remaining_after_all_queries": len(order) - max(availability.values()),
        "B_permutation_sha256": hashlib.sha256(json.dumps(order, separators=(",", ":")).encode()).hexdigest(),
        "full_704_column_B_equivalence": True,
        "per_register_B_event_order_preserved": True,
        "B_transport_profile_unchanged": True,
        "B_transport_profile": {str(k): x for k, x in sorted(original_B_profile.items())},
        "queries": records,
        "all_sixteen_source_banks": source_banks,
        "chosen_eight_query_sources": chosen_sources,
        "failure_controls": {
            "missing_actual_B_write": {"query_root": q, "removed_original_B_event": removed_event, "rejected": True},
            "wrong_query_coefficient_minus_one_eighth": True,
        },
        "optional_unused_coordinate_gather_omission": {
            "omitted_A_events": omitted,
            "queries_and_all_live_Y_rows_unchanged_on_704_columns": True,
            "remaining_prefix_frames_legal": True,
            "prefix_plus_B_profile_delta": delta,
            "old_cleanup_not_reverified": True,
        },
        "unproved_obligations": [
            "legal delivery after each actual query availability cut",
            "complete eight-term scalar compensation and restoration with these carriers",
            "native compilation, ownership, simultaneous lifetimes, and complete cost",
            "replacement cleanup if the optional old-coordinate gathers are omitted",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
