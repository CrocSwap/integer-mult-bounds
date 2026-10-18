"""Independent literal-event and integer-bitset allocation interpreter."""
from collections import Counter, defaultdict
import json
from power import need


def canonical(value):
    # JSON object keys are strings. Normalize generated integer rank keys before
    # sorting, preserving the types of all values (e.g. 1, true, and 1.0 differ).
    normalized = json.loads(json.dumps(value, allow_nan=False))
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def span(rows):
    values = {0}
    for row in rows:
        need(type(row) is int and 0 <= row < 512, "nine-bit frame vector")
        values |= {row ^ old for old in values}
    return values


def inventory(word):
    removed = word["removed"]
    need(len(removed) == len(set(removed)) and set(removed) <= set(range(224, 704)), "removed labels")
    labels = [label for label in range(224, 704) if label not in removed]
    need(len(labels) == 422, "helper count")
    widths = []
    for label in labels:
        initial = span(word["start_extra"].get(str(label), []))
        final = span(word["helper_final"].get(str(label), [1 << i for i in range(9)]))
        need(initial <= final, "helper endpoint containment")
        width = len(final).bit_length() - len(initial).bit_length()
        need(0 < width <= 9, "helper endpoint width")
        widths.append(width)
    return widths


def schedule(parent, order):
    """Expand source blocks, including every bridge, before deriving idle cuts."""
    need(len(order) == 666 and {tuple(x) for x in order} == {(s, r) for s in range(9) for r in range(74)}, "call inventory")
    source = parent["execution_schedule"]
    need(len(source) == 32, "source event count")
    need([x["kind"] for x in source[-2:]] == ["bank_padding_cover_sweep", "translate_every_live_family"], "terminal global events")
    pair_of_stage = {x["stage"]: x["pair"] for x in parent["recipe"] if x["kind"] == "local"}
    need(set(pair_of_stage) == set(range(9)), "local stage pairs")
    caps, ports = {}, defaultdict(set)
    for child in parent["idle_children"]:
        c, p, rank = child["child"], child["port"], child["rank"]
        need(c not in caps or caps[c] == rank, "constant child capacity")
        need(p not in ports[c] and 0 <= p < 112, "idle port uniqueness")
        caps[c] = rank
        ports[c].add(p)
    need(len(caps) == 18 and all(ps == set(range(112)) for ps in ports.values()), "idle child inventory")
    blocks = {}
    for index, event in enumerate(source[:30]):
        if event["kind"] == "local_cover_sweep":
            stage = event["stage"]
            need(stage not in blocks, "duplicate source block")
            blocks[stage] = []
        blocks[stage].append((index, event))
    projected = defaultdict(list)
    touched, windows, call_position, child_roles = {}, {}, {}, {}
    position = bridges = 0
    for time, (stage, replica) in enumerate(order):
        for index, event in blocks[stage]:
            projected[replica].append(index)
            kind = event["kind"]
            if kind == "local_cover_sweep":
                call_position[time] = position
                touched[replica, pair_of_stage[stage]] = position
            elif kind == "bridge":
                touched[replica, event["src"]] = position
                touched[replica, event["dst"]] = position
                bridges += 1
            elif kind == "idle_cover_sweep":
                for side, child in enumerate(event["child_indices"]):
                    if child not in caps:
                        continue
                    need((replica, child) not in windows, "duplicate idle cut")
                    windows[replica, child] = (touched.get((replica, event["pair"]), -1), position)
                    child_roles[child] = (event["pair"], side)
            position += 1
    need(all(projected[r] == list(range(30)) for r in range(74)), "per-replica source projection")
    need(len(windows) == 74 * 18 and bridges == 666, "window and bridge inventory")
    allowed = {key: {t for t, pos in call_position.items() if lo < pos < hi} for key, (lo, hi) in windows.items()}
    return dict(order=order, caps=caps, allowed=allowed, child_roles=child_roles,
                pair_of_stage=pair_of_stage, positions=call_position, windows=windows,
                events=position, bridges=bridges)


def bind_plan(context, plan, widths, dispatch):
    need(plan["order"] == context["order"], "plan order")
    need((plan["M"], plan["T"], plan["live"], plan["deficit"]) == (73, 74, 66304, 23680), "plan dimensions")
    need({int(c): (plan["pairs"][c], plan["sides"][c]) for c in plan["pairs"]} == context["child_roles"], "plan child roles")
    expected = {f"{r},{c}": [context["caps"][c], sorted(times)] for (r, c), times in context["allowed"].items()}
    need(plan["windows"] == expected, "plan literal windows")
    calls = plan["provider_calls"]
    need(len(calls) == 666 and [[x["stage"], x["replica"], x["provider"]] for x in calls] == dispatch, "common dispatch")
    need(all(x["time"] == t for t, x in enumerate(calls)), "dispatch times")
    entries = plan["per_call_widths"]
    need(len(entries) == 666, "plan width entries")
    for t, row in enumerate(entries):
        need([row["stage"], row["replica"]] == context["order"][t] and row["time"] == t, "width entry call")
        need(row["widths"] == widths[dispatch[t][2]], "width entry contents")


def audit_fill(context, widths, dispatch, fill):
    need(fill["columns"] == ["time", "helper", "owner_replica", "child", "port", "offset"], "fill schema")
    need(fill["dispatch_overrides"] == [], "unbound dispatch override")
    rows = fill["rows"]
    need(len(rows) == 666 * 422, "complete role count")
    families = [set() for _ in range(666)]
    cells, roles = {}, {}
    for row in rows:
        need(len(row) == 6 and all(type(x) is int for x in row), "integer role row")
        time, helper, owner, child, port, offset = row
        need(0 <= time < 666 and 0 <= helper < 422 and 0 <= owner < 74 and 0 <= port < 112 and child in context["caps"], "role domain")
        need(time in context["allowed"][owner, child], "strict bridge-aware window")
        stage, replica = context["order"][time]
        pair, side = context["child_roles"][child]
        family = owner * 896 + (2 * pair + side) * 112 + port
        need(not (owner == replica and pair == context["pair_of_stage"][stage]), "active data collision")
        need((time, helper) not in roles, "duplicate helper")
        need(family not in families[time], "duplicate physical family")
        families[time].add(family)
        width = widths[dispatch[time][2]][helper]
        need(0 <= offset and offset + width <= context["caps"][child], "slice capacity")
        key = (owner, child, port)
        mask = ((1 << width) - 1) << offset
        need(not cells.get(key, 0) & mask, "slice overlap")
        cells[key] = cells.get(key, 0) | mask
        roles[time, helper] = (owner, child, port, offset, width, family)
    need(len(roles) == 666 * 422, "complete role domain")
    idle, residual = Counter(), {}
    for owner in range(74):
        for child, capacity in context["caps"].items():
            for port in range(112):
                key = (owner, child, port)
                mask = cells.get(key, 0)
                occupied = mask.bit_count()
                need(mask == (1 << occupied) - 1, "nonprefix occupancy")
                residual[key] = capacity - occupied
                idle[capacity - occupied] += 1
    need(sum(idle.values()) == 149184, "all idle bins")
    need(sum(r * n for r, n in idle.items()) + sum(z[4] for z in roles.values()) == sum(context["caps"].values()) * 74 * 112, "allocated rank conservation")
    return roles, residual, idle


def bind_owners(context, roles, owners):
    need(len(owners) == len(roles), "emitted owner count")
    seen = set()
    for row in owners:
        t, h = row["time"], row["helper"]
        need((t, h) in roles and (t, h) not in seen, "emitted owner key")
        seen.add((t, h))
        owner, child, port, offset, width, family = roles[t, h]
        stage, replica = context["order"][t]
        want = dict(time=t, helper=h, owner_replica=owner, child=child, port=port,
                    offset=offset, width=width, family=family, stage=stage,
                    replica=replica, copy=112 * owner + port)
        need(canonical(row) == canonical(want), "emitted owner binding")
