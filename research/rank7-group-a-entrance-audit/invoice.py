# SPDX-License-Identifier: Apache-2.0
"""Independent time-major width, source-window and complete histogram recount.

The window convention is the retained PR2839 owner contract. This does not
reprove its native physical realization, movement or precision bounds.
"""

from collections import Counter, defaultdict

from common import HELPERS, data, digest, encoded, require


def widths(word):
    live = [r for r in range(224, 704) if r not in word["removed"]]
    require(len(live) == 408, "408 helper names")
    result = []
    for h in live:
        end_rank = len(word["helper_final"][str(h)]) if str(h) in word["helper_final"] else 9
        start = word["start_extra"].get(str(h), [])
        result.append(end_rank - len(start))
    require(all(type(r) is int and 0 < r <= 9 for r in result), "positive native widths")
    return live, result


def windows(template, order):
    ranks = {}
    for item in template["idle_children"]:
        c, r = item["child"], item["rank"]
        require(c not in ranks or ranks[c] == r, "unique source capacity")
        ranks[c] = r
    require(set(ranks) == set(range(18)), "18 idle children")
    pairs = {e["stage"]: e["pair"] for e in template["recipe"] if e["kind"] == "local"}
    blocks, stage = defaultdict(list), None
    for event in template["execution_schedule"]:
        kind = event["kind"]
        if kind in ("bank_padding_cover_sweep", "translate_every_live_family"):
            continue
        if kind == "local_cover_sweep":
            stage = event["stage"]
        require(stage is not None, "initial local source event")
        blocks[stage].append(event)
    progress, last, result = [0] * 74, {}, {}
    for time, (stage, replica) in enumerate(order):
        require(0 <= replica < 74 and progress[replica] == stage, "source chronology")
        progress[replica] += 1
        for event in blocks[stage]:
            kind = event["kind"]
            if kind == "local_cover_sweep":
                last[replica, pairs[stage]] = time
            elif kind == "bridge":
                for pair in (event["src"], event["dst"]):
                    last[replica, pair] = time
            elif kind == "idle_cover_sweep":
                for child in event["child_indices"]:
                    if child not in ranks:
                        continue  # Template padding children carry no helper slots.
                    require((replica, child) not in result, "one idle deadline")
                    result[replica, child] = (ranks[child], last.get((replica, event["pair"]), -1), time)
            else:
                require(kind in ("terminal", "terminal_Y_translations"), "known event")
    require(progress == [9] * 74 and len(result) == 74 * 18, "all source windows")
    return result


def recount(fill, order, dispatch, template, plan, words, local):
    require(len(order) == len(dispatch) == 666 and [x[:2] for x in dispatch] == order,
            "complete dispatch binding")
    require(fill["columns"] == ["time", "helper", "owner_replica", "child", "port", "offset"],
            "literal fill columns")
    require(not fill["dispatch_overrides"], "no hidden provider override")
    bounds = windows(template, order)
    for event in template["execution_schedule"]:
        if event["kind"] != "idle_cover_sweep":
            continue
        require(len(event["child_indices"]) == 2, "two ordered source sides")
        for side, child in enumerate(event["child_indices"]):
            if (0, child) in bounds:
                require(plan["pairs"][str(child)] == event["pair"] and
                        plan["sides"][str(child)] == side, "source child family binding")
    inventories = {tag: widths(word) for tag, word in words.items()}
    names, ws = inventories["base"]
    require(inventories["extra"] == (names, ws), "provider width equality")
    tags = {"gauge44": "base", "extra": "extra"}
    require(len(fill["rows"]) == 666 * 408, "all 271728 roles")
    roles, families, bins = set(), set(), defaultdict(list)
    group_rows = []
    for row in fill["rows"]:
        require(len(row) == 6 and all(type(x) is int for x in row), "integer role record")
        t, h, owner, child, port, offset = row
        require(0 <= t < 666 and 0 <= h < 408 and 0 <= port < 112, "role domain")
        require((t, h) not in roles, "unique helper role")
        roles.add((t, h))
        require((owner, child) in bounds, "existing source bin")
        cap, begin, end = bounds[owner, child]
        require(begin < t <= end, "source availability")
        family = (t, owner, 2 * plan["pairs"][str(child)] + plan["sides"][str(child)], port)
        require(family not in families, "distinct per-call physical families")
        families.add(family)
        tag = tags[dispatch[t][2]]
        width = inventories[tag][1][h]
        require(0 <= offset and offset + width <= cap, "capacity at literal offset")
        bins[owner, child, port].append((offset, width))
        if names[h] in HELPERS:
            group_rows.append([*row, names[h], width])
    idle, occupied = Counter(), 0
    for (owner, child), (capacity, _, _) in sorted(bounds.items()):
        for port in range(112):
            cursor = 0
            for offset, width in sorted(bins.get((owner, child, port), [])):
                require(offset == cursor, "nonoverlapping compact prefix")
                cursor += width
            occupied += cursor
            if cursor < capacity:
                idle[capacity - cursor] += 1
    complete = Counter(idle)
    calls = Counter(tags[row[2]] for row in dispatch)
    for tag, n in calls.items():
        complete.update({int(r): n * c for r, c in local[tag].items()})
    require(len(roles) == 666 * 408 and len(group_rows) == 666 * 5, "complete group coverage")
    require(occupied == sum(ws) * 666, "used width conservation")
    return {"calls": dict(calls), "roles": len(roles), "bins": 74 * 18 * 112,
            "group_placements": len(group_rows), "group_rows_sha256": digest(encoded(group_rows)),
            "group_widths": {str(h): ws[names.index(h)] for h in HELPERS},
            "width_inventory": dict(sorted(Counter(ws).items())), "width_mass": sum(ws),
            "idle": dict(sorted(idle.items())), "complete": dict(sorted(complete.items())),
            "rank_mass": sum(r * n for r, n in complete.items())}


def audit(blobs, words, profiles):
    result = recount(data(blobs, "allocation/FILL.json.gz"), data(blobs, "allocation/ORDER.json"),
        data(blobs, "allocation/DISPATCH.json"), data(blobs, "allocation/vendor/TEMPLATE.json.gz"),
        data(blobs, "allocation/vendor/PLAN.json.gz"), words, profiles)
    claimed = {int(r): n for r, n in data(blobs, "allocation/PROFILE.json").items()}
    require(result["complete"] == claimed, "complete independently recounted invoice")
    claim = data(blobs, "CLAIM.json")
    require(result["group_widths"] == {"331": 7, "450": 6, "451": 6, "508": 6, "509": 6},
            "native group widths reach owner invoice")
    require(result["rank_mass"] == 65088 * 74, "completed mass identity")
    private = [set(map(int, word["helper_final"])) for word in words.values()]
    require(private[0] == private[1] and len(private[0]) == claim["zero_buffers"] == 91,
            "91 private names retained")
    nominal = 896 * 74 + 408 + 8 + 91 + 2
    require(claim["live_families"] == 896 * 74 and claim["helpers"] == 408 and
            claim["independent_inputs"] == 632, "nominal stock components")
    require(nominal == claim["physical_families"] == 66813, "nominal physical stock declaration")
    result["nominal_physical_stock"] = {"live": 66304, "helpers": 408, "centres": 8,
        "private": 91, "scratch": 2, "total": nominal,
        "status": "declaration reconciled; movement, physical realization and precision not proved"}
    result["normalization"] = "sum(n_r * (r/73)^(1-a)) / (896*74)"
    result["supplier_caps"] = {
        "complex": {"source_claimed_endpoint": claim["complex_lower"],
                    "input_profile_recounted": True, "root_and_admission_replayed": False},
        "bit": {"changed_by_this_audit": False, "cap_or_outer_coupling_replayed": False}}
    result["supplier_status"] = "Neither supplier cap is independently admitted here; no new kappa."
    return result
