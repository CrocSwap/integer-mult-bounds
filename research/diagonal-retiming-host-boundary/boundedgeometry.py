"""Independent whole-invocation geometry audit of the selected PR1094 export.

No local compiler, emitter, owner optimizer, or predecessor executable is imported.
The input is parsed archive members, not paths. This checks the boundary consumed
by hosting; it does not admit a new child operator, native recipe, or invoice.
Prepared by @ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""

import copy
import hashlib
import json
from collections import Counter, defaultdict

BASE = "candidate/strict/global/"
TEMPLATE = BASE + "hosted/GLOBAL-TEMPLATE.json.gz"
PLAN = BASE + "PLAN.json"
PARENT = BASE + "base/split-centres/GLOBAL-TEMPLATE.json.gz"
PHASES = BASE + "base/work/complex-nine-native/DATA-PHASES.json"
SIGMAS = BASE + "hosted/ACTUAL-SIGMAS.json.gz"
IDLE_FRAMES = BASE + "hosted/IDLE-REMAINDER-FRAMES.json.gz"
CANONICAL = BASE + "base/providers/gauge44/CANONICAL-WORD.json.gz"
REQUIRED_MEMBERS = (TEMPLATE, PLAN, PARENT, PHASES, SIGMAS, IDLE_FRAMES, CANONICAL)


class GeometryError(ValueError):
    """A named finite geometry predicate failed."""


def require(condition, predicate):
    if not condition:
        raise GeometryError(predicate)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def boundary(word):
    """Actual ordered endpoint vectors, independent of frame identifier names."""
    return {
        **{k: word[k] for k in ("v", "h", "R", "ports", "centers")},
        "start": [word["frames"][i] for i in word["start"]],
        "final": [word["frames"][i] for i in word["final"]],
        "center_frames": [word["frames"][i] for i in word["center_frames"]],
    }


def audit_geometry(members, word):
    """Return counts/signature after checking every selected owner reservation."""
    require(set(REQUIRED_MEMBERS) <= set(members), "required_archive_members")
    template, plan, parent, phases, stored_sigmas, idle_frames, source = (
        members[p] for p in REQUIRED_MEMBERS
    )
    require((word["v"], word["h"], word["R"]) == (112, 9, 480), "local_dimensions")
    require(len(word["start"]) == len(word["final"]) == 704, "local_role_count")
    require(boundary(word) == boundary(source), "unchanged_actual_local_boundary")
    require((template["m"], template["live"]) == (73, 14336), "global_dimensions")
    require(template["physical"] == 14826 and template["private_namespace"] == {
        "centers": [14336, 14344], "reserved_tableau": [14344, 14824],
        "coefficient": [14824, 14826]}, "private_namespace_disjoint_from_live_owners")
    require(phases["m"] == 73 and len(phases["recipes"]) == 112, "data_phase_dimensions")
    require(template["recipe"] == parent["recipe"], "unchanged_outer_recipe")
    require("no within-cover or within-invocation interleaving" in template["async_schedule"]["scope"], "indivisible_invocation_contract")
    require(template["hosting"]["max_helpers_per_physical_family_per_call"] == 1, "whole_helper_contract")
    require(template["hosting"]["banks"] == [0] * 9, "unchanged_bankless_hosting")
    widths = [len(word["frames"][word["final"][224+h]]) - len(word["frames"][word["start"][224+h]]) for h in range(480)]
    require(all(0 < w <= 9 for w in widths), "positive_residual_widths")
    registry = template["local_providers"]
    require(set(registry) == {"gauge44"} and registry["gauge44"]["widths"] == widths, "provider_width_boundary")
    require(registry["gauge44"]["ports"] == word["ports"], "provider_ports")
    require(plan["provider_registry"]["gauge44"]["widths"] == widths and plan["provider_registry"]["gauge44"]["ports"] == word["ports"], "plan_provider_geometry")
    order = [[c["stage"], c["replica"]] for c in template["calls"]]
    require(len(order) == 144 and len({tuple(c) for c in order}) == 144, "complete_call_order")
    require(set(map(tuple, order)) == {(s, r) for s in range(9) for r in range(16)}, "complete_call_domain")
    require(order == plan["order"] == template["async_schedule"]["order"], "bound_call_order")
    require(template["async_schedule"]["source_schedule"] == parent["execution_schedule"], "source_schedule_binding")
    require(template["async_schedule"]["source_call_order"] == [[c["stage"], c["replica"]] for c in parent["calls"]], "source_call_order_binding")
    require(all("replica" in e for e in template["execution_schedule"][:-2]) and [e["source_event"] for e in template["execution_schedule"][-2:]] == [30, 31], "final_global_tail_positions")
    stage_pair = {e["stage"]: e["pair"] for e in parent["recipe"] if e["kind"] == "local"}
    ranks = {e["child"]: e["rank"] for e in parent["idle_children"]}
    require(len(ranks) == 18, "pending_child_inventory")
    pair_side, intervals, last, callpos = {}, {}, {}, {}
    per_replica = defaultdict(list)
    global_events = []
    block = -1
    for pos, event in enumerate(template["execution_schedule"]):
        j = event["source_event"]
        require(0 <= j < len(parent["execution_schedule"]), "source_event_index")
        expected = dict(parent["execution_schedule"][j], source_event=j)
        if "replica" not in event:
            global_events.append(j)
            if event["kind"] == "bank_padding_cover_sweep":
                expected["families"] = [14336, 14336]
            if event["kind"] == "translate_every_live_family":
                expected.update(families=[0, 14336], charged_calls_per_cover=14336)
            require(event == expected, "global_event_projection")
            continue
        r = event["replica"]
        require(0 <= r < 16 and j < 30, "replica_event_domain")
        per_replica[r].append(j)
        expected.update(replica=r, replicas=[r], time=event["time"])
        if event["kind"] == "local_cover_sweep":
            block += 1
            expected["provider_id"] = "gauge44"
            require(order[block] == [event["stage"], r], "schedule_call_order")
            callpos[block] = pos
            last[r, stage_pair[event["stage"]]] = pos
        require(event["time"] == block, "indivisible_schedule_block")
        require(event == expected, "replica_event_projection")
        if event["kind"] == "bridge":
            last[r, event["src"]] = last[r, event["dst"]] = pos
        if event["kind"] == "idle_cover_sweep":
            for side, child in enumerate(event["child_indices"]):
                if child not in ranks:  # The inherited schedule also names zero-rank children.
                    continue
                pair_side[child] = (event["pair"], side)
                intervals[r, child] = (last.get((r, event["pair"]), -1), pos)
    require(global_events == [30, 31] and set(per_replica) == set(range(16)), "global_tail_and_replicas")
    require(all(v == list(range(30)) for v in per_replica.values()), "per_replica_source_order")
    require(set(callpos) == set(range(144)), "scheduled_complete_calls")
    windows = {f"{r},{i}": [ranks[i], [t for t, p in sorted(callpos.items()) if a < p < b]] for (r, i), (a, b) in intervals.items()}
    require(windows == plan["windows"], "actual_source_touch_windows")
    bases = []
    for port, q in enumerate(word["ports"]):
        require(0 < q < 512 and q.bit_count() % 2 == 1, "odd_port_vector")
        z = next((i for i in range(9) if not (q >> i) & 1), None)
        require(z is not None, "port_missing_coordinate")
        a = q ^ (1 << z)
        positions = list(range(9))
        positions[0], positions[z] = positions[z], positions[0]
        basis = [(1 << i) ^ (a if (a >> i) & 1 else 0) for i in positions] + [1 << i for i in range(9, 73)]
        require(all((x & y).bit_count() % 2 == int(i == j) for i, x in enumerate(basis) for j, y in enumerate(basis)), "orthogonal_73_axis_basis")
        bases.append(basis)
        for i, e in enumerate(phases["recipes"][port]["idle_children"]):
            require(e["rank"] == len(e["orthogonal_axes"]) == ranks.get(i, 0), "pending_axis_rank")
            require(len(set(e["orthogonal_axes"])) == e["rank"] and set(e["orthogonal_axes"]) <= set(basis), "pending_axes_in_port_basis")
    used, roles, actual_sigmas = defaultdict(set), {}, {}
    parent_calls = {(c["stage"], c["replica"]): c for c in parent["calls"]}
    for time, call in enumerate(template["calls"]):
        s, r = call["stage"], call["replica"]
        require(call["time"] == time and call["provider_id"] == "gauge44", "call_time_and_provider")
        old = parent_calls[s, r]
        require(all(call[k] == old[k] for k in ("stage", "replica", "pair", "orientation", "window")), "data_call_boundary")
        own = call["owners"]
        require(len(own) == 704 and len({f for f, _ in own}) == 704, "distinct_704_owner_families")
        require(all(0 <= f < 14336 for f, _ in own), "live_owner_domain")
        require(own[:224] == old["owners"][:224], "unchanged_data_owner_routes")
        for h, (family, route) in enumerate(own[224:]):
            width = widths[h]
            require(len(route) >= 3, "helper_route_shape")
            _, child, offset = route[:3]
            owner_replica, sub = divmod(family, 896)
            pair, sub = divmod(sub, 224)
            side, port = divmod(sub, 112)
            require(child in ranks and (pair, side) == pair_side[child], "helper_owner_child_family")
            require(time in windows[f"{owner_replica},{child}"][1], "helper_strict_busy_window")
            require(0 <= offset and offset + width <= ranks[child], "helper_pending_capacity")
            pending = phases["recipes"][port]["idle_children"][child]["orthogonal_axes"]
            occupied = [bases[port].index(x) for x in pending[offset:offset+width]]
            spectators = [i for i in range(73) if i not in occupied][:9-width]
            expected_route = [3, child, offset] if width == 9 else [4, child, offset, width, spectators]
            require(route == expected_route, "literal_helper_spectator_route")
            permutation = occupied + spectators + [i for i in range(73) if i not in occupied and i not in spectators]
            require(sorted(permutation) == list(range(73)), "helper_chart_axis_permutation")
            sigma = [bases[port][i] for i in permutation]
            # All charts are permutations of an independently checked orthobasis.
            actual_sigmas[digest(sigma)] = sigma
            key = (owner_replica, child, port)
            cells = set(range(offset, offset+width))
            require(not used[key] & cells, "disjoint_pending_reservations")
            used[key].update(cells)
            roles[s, r, h] = dict(stage=s, replica=r, helper=h, family=family, owner_replica=owner_replica, child=child, copy=owner_replica*112+port, port=port, offset=offset, width=width)
    require(actual_sigmas == stored_sigmas, "all_literal_73_axis_charts")
    pooled = template["hosting"]["pooled_slots"]
    require(len(pooled) == len(roles) == 69120, "complete_helper_reservations")
    seen = set()
    for slot in pooled:
        key = slot["stage"], slot["replica"], slot["helper"]
        require(key in roles and key not in seen, "unique_pooled_role")
        require({k: slot[k] for k in roles[key]} == roles[key], "literal_pooled_role_binding")
        require(slot["time"] == order.index([key[0], key[1]]), "pooled_role_time")
        seen.add(key)
    wanted = []
    for old in parent["idle_children"]:
        child, port = old["child"], old["port"]
        for r in range(16):
            cells = used[r, child, port]
            require(cells == set(range(len(cells))), "compacted_pending_prefix")
            remaining = old["rank"] - len(cells)
            require(remaining >= 0, "nonnegative_idle_remainder")
            if remaining:
                pair, side = pair_side[child]
                wanted.append(dict(child=child, port=port, replica=r, replicas=1, family=896*r+(2*pair+side)*112+port, rank=remaining, hosted=len(cells), pending_offset=len(cells)))
    require(template["idle_children"] == wanted, "exact_idle_remainder_inventory")
    exported = [dict(e, orthogonal_axes=phases["recipes"][e["port"]]["idle_children"][e["child"]]["orthogonal_axes"][e["pending_offset"]:]) for e in wanted]
    require(all(len(e["orthogonal_axes"]) == e["rank"] for e in exported), "idle_suffix_rank")
    require(exported == idle_frames, "literal_idle_pending_suffix_axes")
    projection = dict(local_boundary=boundary(word), order=order, windows=windows, calls=[{k: c[k] for k in ("stage", "replica", "pair", "orientation", "window", "owners")} for c in template["calls"]], charts=actual_sigmas, idle_frames=exported)
    return dict(status="PASS_WHOLE_INVOCATION_HOST_GEOMETRY", complete_invocations=144, logical_roles_per_call=704, helper_reservations=69120, actual_73_axis_charts=len(actual_sigmas), pending_windows=len(windows), idle_remainders=len(wanted), width_profile=dict(sorted(Counter(widths).items())), idle_rank_profile=dict(sorted(Counter(e["rank"] for e in wanted).items())), geometry_sha256=digest(projection))


def run_geometry_controls(members, word):
    """Five independently mutated geometric exports must fail named checks."""
    controls = {}
    mutations = ("duplicate_owner", "excluded_call_time", "changed_pending_offset", "changed_idle_axis",
                 "private_namespace_overlap")
    for name in mutations:
        changed = dict(members)
        path = PLAN if name == "excluded_call_time" else IDLE_FRAMES if name == "changed_idle_axis" else TEMPLATE
        changed[path] = copy.deepcopy(members[path])
        if name == "duplicate_owner":
            changed[path]["calls"][0]["owners"][224][0] = changed[path]["calls"][0]["owners"][0][0]
        elif name == "excluded_call_time":
            call = members[TEMPLATE]["calls"][0]
            family, route = call["owners"][224]
            changed[path]["windows"][f"{family//896},{route[1]}"][1].remove(0)
        elif name == "changed_pending_offset":
            changed[path]["idle_children"][0]["pending_offset"] += 1
        elif name == "changed_idle_axis":
            changed[path][0]["orthogonal_axes"][0] ^= 1
        else:
            changed[path]["private_namespace"]["centers"][0] = 14335
        try:
            audit_geometry(changed, word)
        except GeometryError as error:
            controls[name] = dict(rejected=True, predicate=str(error))
        else:
            raise GeometryError("control_not_rejected:" + name)
    return controls
