#!/usr/bin/env python3
"""Finite PR626 ownership audit by next-touch traversal, without producer imports.

Prepared for tekuuu with substantial OpenAI Codex assistance. Apache-2.0.
This checks the finite pinned controller, not its all-size physical realization.
"""
import argparse
from collections import Counter, defaultdict
import copy
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = "research/complex-k492-owner-repair/"
PARENT = "research/direct-delivery504-global/inputs/data-base/split-centres/GLOBAL-TEMPLATE.json.gz"
PHASES = "research/direct-delivery504-global/inputs/data-base/work/complex-nine-native/DATA-PHASES.json"
ROUND20 = PACKAGE + "vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor535/inputs/ROUND20-PARENT-TEMPLATE.json.gz"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def expand(parent, order):
    """Project each replica's source events, then merge complete call blocks."""
    source = parent["execution_schedule"][:30]
    starts = [i for i, event in enumerate(source) if event["kind"] == "local_cover_sweep"]
    need(len(starts) == 9, "nine source calls")
    blocks = [source[a:b] for a, b in zip(starts, starts[1:] + [30])]
    need(sorted(map(tuple, order)) == [(s, r) for s in range(9) for r in range(8)], "complete call order")
    need(all([s for s, r in order if r == replica] == list(range(9)) for replica in range(8)), "replica source order")
    events = []
    for time, (stage, replica) in enumerate(order):
        for offset, event in enumerate(blocks[stage]):
            events.append(dict(event, replica=replica, time=time, source_event=starts[stage] + offset))
    return events


def next_touch(events, stage_pair, child_geometry):
    """Reverse state: first future touch of each family pair is an idle or a barrier.

    An active local call is a barrier BEFORE sampling its helper eligibility.
    Idle deadlines after that call have already entered the reverse state.
    """
    state = {(r, p): None for r in range(8) for p in range(4)}
    admitted = defaultdict(set)
    calls = {}
    deadlines = {}
    for position in range(len(events) - 1, -1, -1):
        event = events[position]
        replica, kind = event["replica"], event["kind"]
        if kind == "idle_cover_sweep":
            pair = event["pair"]
            children = event["child_indices"]
            need(len(children) == 2, "two idle sides")
            state[replica, pair] = tuple(children)
            for child in children:
                need((replica, child) not in deadlines, "unique idle deadline")
                deadlines[replica, child] = (position, event["time"])
        elif kind == "bridge":
            state[replica, event["src"]] = None
            state[replica, event["dst"]] = None
        elif kind == "local_cover_sweep":
            state[replica, stage_pair[event["stage"]]] = None
            time = event["time"]
            need(time not in calls, "one local event per call")
            calls[time] = position
            for (owner_replica, pair), children in state.items():
                if children is not None:
                    for child in children:
                        if child in child_geometry:
                            need(child_geometry[child][0] == pair, "idle pair")
                            admitted[owner_replica, child].add(time)
        elif kind in ("terminal_Y_translations", "terminal"):
            for pair in range(4):
                state[replica, pair] = None
        else:
            raise ValueError("unknown controller event: " + kind)
    need(set(calls) == set(range(72)), "72 event positions")
    return admitted, calls, deadlines


def geometry(parent):
    ranks = {}
    for row in parent["idle_children"]:
        child = row["child"]
        need(child not in ranks or ranks[child] == row["rank"], "port-independent rank")
        ranks[child] = row["rank"]
    result = {}
    for event in parent["execution_schedule"][:30]:
        if event["kind"] == "idle_cover_sweep":
            for side, child in enumerate(event["child_indices"]):
                if child in ranks:
                    result[child] = (event["pair"], side, ranks[child])
    need(set(result) == set(range(18)), "18 nonzero idle children")
    return result


def compare_windows(plan, admitted, geom):
    need(set(plan["windows"]) == {f"{r},{c}" for r in range(8) for c in geom}, "144 windows")
    for replica in range(8):
        for child, (pair, side, rank) in geom.items():
            cap, window = plan["windows"][f"{replica},{child}"]
            need(cap == rank and len(window) == len(set(window)), "window capacity and uniqueness")
            need(set(window) == admitted[replica, child], "next-touch window mismatch")
            need(plan["pairs"][str(child)] == pair and plan["sides"][str(child)] == side, "child geometry")


def check_roles(roles, plan, admitted, geom, stage_pair, phases):
    families = defaultdict(set)
    helpers = defaultdict(set)
    cells = defaultdict(set)
    dispatch = {c["time"]: c for c in plan["provider_calls"]}
    need(set(dispatch) == set(range(72)), "complete dispatch")
    cross = 0
    for row in roles:
        t, helper = row["time"], row["helper"]
        need(t in dispatch and 0 <= helper < 492, "call and helper domain")
        stage, replica = plan["order"][t]
        need((row["stage"], row["replica"]) == (stage, replica), "role call")
        owner, child, port = row["owner_replica"], row["child"], row["port"]
        need(0 <= owner < 8 and child in geom and 0 <= port < 112, "owner domain")
        pair, side, cap = geom[child]
        need(t in admitted[owner, child], "role outside next-touch window")
        family = owner * 896 + (2 * pair + side) * 112 + port
        need(row["family"] == family and row["copy"] == owner * 112 + port, "family identity")
        need((owner, pair) != (replica, stage_pair[stage]), "helper aliases active data")
        need(family not in families[t] and helper not in helpers[t], "same-call whole-family alias")
        families[t].add(family)
        helpers[t].add(helper)
        width = plan["provider_registry"][dispatch[t]["provider"]]["widths"][helper]
        off = row["offset"]
        need(row["width"] == width and 0 < width <= 9 and 0 <= off and off + width <= cap, "width and footprint")
        axes = phases["recipes"][port]["idle_children"][child]["orthogonal_axes"]
        need(len(axes) == cap and len(set(axes)) == cap, "phase axes")
        occupied = set(axes[off:off + width])
        key = owner, child, port
        need(not occupied & cells[key], "reused pending coordinate")
        cells[key].update(occupied)
        cross += owner != replica
    need(len(roles) == 35424 and all(helpers[t] == set(range(492)) for t in range(72)), "complete role census")
    return {"roles": len(roles), "cross_replica_roles": cross, "occupied_owner_groups": len(cells)}


def scalar_columns(recipe):
    """Apply the inherited normalized data contract to each input basis vector.

    The existing complex_replay.py composes matrix rows. This implementation
    instead executes eight separate integer vectors; it imports no replay code.
    Idle residuals and phase work have no additional data-shear action here.
    """
    columns = []
    for basis in range(8):
        x = [int(basis == 2 * p) for p in range(4)]
        y = [int(basis == 2 * p + 1) for p in range(4)]
        for event in recipe:
            if event["kind"] == "local":
                pair = event["pair"]
                if event["reverse"]:
                    x[pair] -= y[pair]
                else:
                    y[pair] += x[pair]
            elif event["kind"] == "bridge":
                src, dst, q = event["src"], event["dst"], event["coefficient"]
                x[dst] += q * x[src]
                y[src] -= q * y[dst]
            elif event["kind"] == "terminal":
                x, y = y, [-value for value in x]
            else:
                raise ValueError("unknown scalar recipe event")
        columns.append([value for pair in zip(x, y) for value in pair])
    return columns


def audit():
    pins = read(HERE / "SOURCES.json")
    for name, expected in pins["sha256"].items():
        need(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, "source pin: " + name)
    source_manifest = read(ROOT / "research/community-k492-audit/SELECTED-SOURCE.json")["files"]
    for name in (PARENT, PHASES, PACKAGE + "data/PLAN.json", PACKAGE + "data/OWNERS.json.gz"):
        need(source_manifest[name] == pins["sha256"][name], "selected source binding")
    parent, plan = read(ROOT / PARENT), read(ROOT / (PACKAGE + "data/PLAN.json"))
    installed_parent = read(ROOT / ROUND20)
    for key in ("recipe", "idle_children"):
        need(parent[key] == installed_parent[key], "installed controller " + key)
    need(parent["execution_schedule"][:30] == installed_parent["execution_schedule"][:30], "installed replica controller")
    roles, phases = read(ROOT / (PACKAGE + "data/OWNERS.json.gz")), read(ROOT / PHASES)
    geom = geometry(parent)
    stage_pair = {e["stage"]: e["pair"] for e in parent["recipe"] if e["kind"] == "local"}
    events = expand(parent, plan["order"])
    admitted, calls, deadlines = next_touch(events, stage_pair, geom)
    compare_windows(plan, admitted, geom)
    census = check_roles(roles, plan, admitted, geom, stage_pair, phases)
    # Enumerate the COMPLETE matrix, including all inadmissible entries.
    matrix = [[r, c, t, int(t in admitted[r, c])] for r in range(8) for c in geom for t in range(72)]
    need(len(matrix) == 10368, "complete eligibility matrix")
    closing_block = [(r, c, tm) for (r, c), (pos, tm) in deadlines.items()
                     if c in geom and tm in admitted[r, c] and calls[tm] < pos]
    closing_set = set(closing_block)
    closing_roles = sum((z["owner_replica"], z["child"], z["time"]) in closing_set for z in roles)
    controls = Counter()

    def rejects(label, function, expected):
        try:
            function()
        except ValueError as error:
            need(str(error) == expected, "unexpected control failure: " + str(error))
            controls[label] += 1
        else:
            raise ValueError("accepted negative control: " + label)

    # Both one-call extensions of every nonempty window, and deleting either
    # legal endpoint, model the two off-by-one errors in block-time bounds.
    for r in range(8):
        for c in geom:
            values = admitted[r, c]
            for t in sorted({min(values) - 1, min(values), max(values), max(values) + 1}):
                if not 0 <= t < 72:
                    continue
                mutant = {**plan, "windows": dict(plan["windows"])}
                cap = plan["windows"][f"{r},{c}"][0]
                mutant["windows"][f"{r},{c}"] = [cap, sorted(values ^ {t})]
                rejects("window_endpoint_shift", lambda: compare_windows(mutant, admitted, geom), "next-touch window mismatch")
    # Endpoint controls exercise the scanner rather than just frozen pin comparison.
    # Move each idle event before the call of its own block: the deadline now
    # precedes that call and must remove its eligibility, leaving all else valid.
    swaps = 0
    for i, b in enumerate(events):
        if b["kind"] == "idle_cover_sweep" and any(c in geom for c in b["child_indices"]):
            call_position = calls[b["time"]]
            a = events[call_position]
            mutant = list(events)
            mutant.pop(i)
            mutant.insert(call_position, b)
            changed, _, _ = next_touch(mutant, stage_pair, geom)
            for c in b["child_indices"]:
                if c in geom:
                    need(a["time"] in admitted[b["replica"], c], "positive closing-block control")
                    need(a["time"] not in changed[b["replica"], c], "deadline swap must remove call")
                    swaps += 1
    controls["deadline_before_call"] = swaps
    identity = [[int(i == j) for i in range(8)] for j in range(8)]
    need(scalar_columns(parent["recipe"]) == identity, "inherited scalar controller identity")
    scalar_omissions = []
    source_bridges = [(i, e) for i, e in enumerate(parent["execution_schedule"][:30]) if e["kind"] == "bridge"]
    recipe_bridges = [(i, e) for i, e in enumerate(parent["recipe"]) if e["kind"] == "bridge"]
    need(len(source_bridges) == len(recipe_bridges) == 9, "nine scalar bridges")
    for (source_index, source_event), (recipe_index, recipe_event) in zip(source_bridges, recipe_bridges):
        need(source_event == recipe_event, "scalar bridge/controller binding")
        mutated_recipe = parent["recipe"][:recipe_index] + parent["recipe"][recipe_index + 1:]
        columns = scalar_columns(mutated_recipe)
        need(columns != identity, "omitted bridge must change scalar map")
        witness = next(j for j in range(8) if columns[j] != identity[j])
        scalar_omissions.append({
            "source_event": source_index,
            "input_basis_column": witness,
            "actual_output": columns[witness],
            "expected_output": identity[witness],
            "changed_matrix_entries": sum(a != b for col, expected in zip(columns, identity) for a, b in zip(col, expected)),
        })
    # Deleting a bridge is invisible to this timing abstraction on THIS
    # controller: adjacent idle/local barriers already delimit the windows.
    # This is a limitation witness, not evidence that bridges may be deleted
    # from the actual scalar program. Source/controller binding remains vital.
    bridge_effects = Counter()
    for i, event in enumerate(events):
        if event["kind"] == "bridge":
            mutant = events[:i] + events[i + 1:]
            changed, _, _ = next_touch(mutant, stage_pair, geom)
            difference = sum((t in changed[r, c]) != bool(ok) for r, c, t, ok in matrix)
            need(difference == 0, "pinned bridge-deletion limitation changed")
            bridge_effects["terminal_no_change" if event["source_event"] >= 25 else "nonterminal_no_change"] += 1
    # A NEW intervening physical touch is not redundant. For every window,
    # insert a bridge just after a seed-selected legal call and require that
    # this call loses eligibility for the touched owner pair.
    for r in range(8):
        for c, (pair, _, _) in geom.items():
            options = sorted(admitted[r, c])
            t = options[60 % len(options)]
            other = (pair + 1) % 4
            for src, dst in ((pair, other), (other, pair)):
                new_bridge = dict(kind="bridge", replica=r, src=src, dst=dst, time=t)
                position = calls[t] + 1
                mutant = events[:position] + [new_bridge] + events[position:]
                changed, _, _ = next_touch(mutant, stage_pair, geom)
                need(t not in changed[r, c], "intervening bridge must invalidate the selected call")
                rejects("intervening_bridge_source" if src == pair else "intervening_bridge_destination",
                        lambda: compare_windows(plan, changed, geom), "next-touch window mismatch")
    mutant = copy.deepcopy(events)
    mutant[0]["kind"] = "unrecognized_touch"
    rejects("unknown_event", lambda: next_touch(mutant, stage_pair, geom), "unknown controller event: unrecognized_touch")
    # Same call, same family, disjoint coordinates: scalar coordinate disjointness
    # does NOT permit two simultaneously live whole helpers.
    first = roles[0]
    second_index = next(i for i, z in enumerate(roles) if z["time"] == first["time"] and z["helper"] != first["helper"])
    mutant = list(roles)
    mutant[second_index] = dict(first, helper=roles[second_index]["helper"], offset=first["offset"] + first["width"])
    rejects("same_family_disjoint_coordinates", lambda: check_roles(mutant, plan, admitted, geom, stage_pair, phases), "same-call whole-family alias")
    return {
        "status": "PASS_PR626_NEXT_TOUCH_BOUNDARY_AUDIT",
        "base_commit": pins["base_commit"],
        "assignment_seed": 60,
        "replica_events": len(events),
        "idle_deadlines_including_zero_rank": len(deadlines),
        "nonzero_windows": 144,
        "eligibility_decisions": len(matrix),
        "admitted_decisions": sum(row[3] for row in matrix),
        "eligibility_sha256": digest(matrix),
        **census,
        "closing_block_admitted_child_calls": len(closing_block),
        "closing_block_helper_roles": closing_roles,
        "valid_roles_rejected_if_borrower_replica_is_used": sum(z["time"] not in admitted[z["replica"], z["child"]] for z in roles),
        "negative_controls": dict(sorted(controls.items())),
        "bridge_deletion_sensitivity": dict(sorted(bridge_effects.items())),
        "scalar_bridge_omission_counterexamples": scalar_omissions,
        "scope": "Finite pinned PR626 controller and literal owner roles; native widths, normalized residual semantics, atomic calls and all-size realization are inherited, not re-proved. No new kappa.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a deterministic receipt")
    args = parser.parse_args()
    result = audit()
    if args.write:
        args.write.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(result == read(HERE / "EXPECTED.json"), "receipt mismatch")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
