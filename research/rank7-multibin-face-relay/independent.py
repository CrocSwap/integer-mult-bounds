#!/usr/bin/env python3
"""Independent exact finite geometry check; Python standard library only.

Does not import constructor.py or any predecessor verifier. Native arithmetic,
ordered provider widths and local invoices remain the pinned source premises.
"""

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGET37 = {1: 822840, 2: 235098, 3: 79734, 4: 35964,
            5: 6858, 8: 2664, 48: 14095}
COLUMNS = ["time", "helper", "owner_replica", "child", "port", "offset"]


class Failure(Exception):
    def __init__(self, code, detail):
        super().__init__(f"{code}: {detail}")
        self.code = code


def require(value, code, detail):
    if not value:
        raise Failure(code, detail)


def read(relative):
    p = ROOT / relative
    data = gzip.decompress(p.read_bytes()) if p.suffix == ".gz" else p.read_bytes()
    return json.loads(data)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def json_counter(c):
    return {str(k): v for k, v in sorted(c.items()) if v}


def check_pins():
    manifest = read("SOURCES.json")
    receipts = {}
    for name, item in manifest["exports"].items():
        p = ROOT / name
        require(p.is_file(), "pin", name)
        require(p.stat().st_size == item["bytes"], "pin", f"size {name}")
        digest = sha(p)
        require(digest == item["sha256"], "pin", f"hash {name}")
        receipts[name] = digest
    require(len(receipts) == 16, "pin", "exactly 16 frozen exports")
    require(manifest["base_commit"] == "d8e0f83f00191df62174b641e9fff055c357f641",
            "pin", "frozen scientific base")
    require(manifest["source_commit"] == "be191346391661f4d35fc0d1508d0a6029572576",
            "pin", "source commit")
    require(manifest["predecessor_commit"] == "87ca15cf005ab232ca0104ec5137014ac754f487",
            "pin", "predecessor commit")
    return manifest, receipts


class Geometry:
    def __init__(self, order, dispatch, template, providers):
        self.order = [tuple(x) for x in order]
        self.T = len(self.order) // 9
        self.N = len(self.order)
        require(self.T in (37, 74) and self.N == 9 * self.T,
                "order", "only the frozen T37/T74 instances")
        require(set(self.order) == {(s, r) for s in range(9) for r in range(self.T)},
                "order", "each stage/replica exactly once")
        require(len(set(self.order)) == self.N, "order", "duplicate call")
        self.at = {sr: t for t, sr in enumerate(self.order)}
        for r in range(self.T):
            require([self.at[s, r] for s in range(9)] ==
                    sorted(self.at[s, r] for s in range(9)), "order", "replica order")

        local = [event for event in template["recipe"] if event["kind"] == "local"]
        require(len(local) == 9, "source", "nine local recipe stages")
        self.pair = {event["stage"]: event["pair"] for event in local}
        self.orientation = {event["stage"]: "backward" if event["reverse"] else "forward"
                            for event in local}
        require(set(self.pair) == set(range(9)), "source", "recipe stage names")
        for c in template["calls"]:
            require(c["pair"] == self.pair[c["stage"]] and
                    c["orientation"] == self.orientation[c["stage"]],
                    "source", "template call/recipe metadata")
            data_owners = {f for f, owner in c["owners"] if owner[0] == 1}
            native_active = {896*c["replica"] + 224*c["pair"] + 112*side + p
                             for side in range(2) for p in range(112)}
            require(data_owners == native_active, "source", "physical active-family address map")

        require(len(dispatch) == self.N, "dispatch", "one provider per call")
        self.providers = providers
        self.names = []
        self.widths = []
        for t, (s, r, name) in enumerate(dispatch):
            require((s, r) == self.order[t], "dispatch", "dispatch order")
            require(name in providers, "dispatch", "registered provider")
            width = providers[name]["widths"]
            require(len(width) == 408 and all(type(w) is int and 4 <= w <= 9 for w in width),
                    "width", "actual ordered 408 helper widths")
            self.names.append(name)
            self.widths.append(width)

        # A level denotes the most recently completed local event. The pending
        # interval opens strictly after the prior source event and includes the
        # complete local call immediately before its next source access.
        self.child = {}
        native_rank = {}
        for c in template["idle_children"]:
            key = c["child"]
            require(0 <= c["port"] < 112 and c["replicas"] == 37,
                    "source", "idle port inventory")
            require(key not in native_rank or native_rank[key] == c["rank"],
                    "source", "consistent child rank")
            native_rank[key] = c["rank"]
        require(len(template["idle_children"]) == 18 * 112 and
                set(native_rank) == set(range(18)), "source", "all nonzero idle ports")
        require({(c["child"], c["port"]) for c in template["idle_children"]} ==
                {(j, p) for j in range(18) for p in range(112)},
                "source", "idle child/port coverage")
        for event in template["execution_schedule"]:
            if event["kind"] != "idle_cover_sweep":
                continue
            lo, hi = event["from_level"], event["to_level"]
            rank = 8 * (hi - lo)
            for side, child in enumerate(event["child_indices"]):
                if child not in native_rank:
                    require(rank == 0, "source", "omitted idle has rank zero")
                    continue
                require(rank == native_rank[child] and rank > 0,
                        "source", "idle rank equals eight times level gap")
                require(child not in self.child, "source", "one sweep per child")
                self.child[child] = (event["pair"], side, rank, lo, hi)
        require(set(self.child) == set(range(18)), "source", "all idle source sweeps")
        self.windows = {}
        for r in range(self.T):
            for child, (pair, side, cap, lo, hi) in self.child.items():
                L = -1 if lo == -1 else self.at[lo, r]
                U = self.at[hi, r]
                require(L < U, "source", "nonempty pending interval")
                self.windows[r, child] = (L, U, cap)
        self.bins = {(r, child, p) for r in range(self.T)
                     for child in range(18) for p in range(112)}
        self.check_source_family_invariants()

    def family(self, owner):
        r, child, port = owner
        pair, side, _, _, _ = self.child[child]
        return (r, pair, side, port)

    def legal(self, time, owner):
        L, U, _ = self.windows[owner[0], owner[1]]
        return L < time <= U

    def check_source_family_invariants(self):
        # All ports share these time sets. Distinct child windows of one
        # physical family never admit the same call. No window admits a call
        # at which its physical family belongs to the active data pair.
        groups = defaultdict(list)
        for child, (pair, side, _, _, _) in self.child.items():
            groups[pair, side].append(child)
        for r in range(self.T):
            for (pair, side), children in groups.items():
                seen = set()
                for child in children:
                    L, U, _ = self.windows[r, child]
                    legal = set(range(L + 1, U + 1))
                    require(not (seen & legal), "source", "same-family child-window overlap")
                    seen.update(legal)
                    require(all(not (rr == r and self.pair[s] == pair)
                                for s, rr in (self.order[t] for t in legal)),
                            "source", "active family lies in a source window")

    def check(self, fill, expected_k):
        require(fill["columns"] == COLUMNS and fill["dispatch_overrides"] == [],
                "format", "fixed column/dispatch contract")
        rows = fill["rows"]
        require(len(rows) == self.N * 408, "coverage", "one role for every call/helper")
        seen = set()
        occupied = defaultdict(list)
        family_at_call = set()
        for row in rows:
            require(len(row) == 6 and all(type(x) is int for x in row),
                    "format", "six integer columns")
            t, h, r, child, port, offset = row
            require(0 <= t < self.N and 0 <= h < 408, "coverage", "role index")
            identity = (t, h)
            require(identity not in seen, "coverage", "duplicate role")
            seen.add(identity)
            owner = (r, child, port)
            require(owner in self.bins, "owner", "owner identity")
            require(self.legal(t, owner), "window", f"role {identity} outside {owner}")
            width = self.widths[t][h]
            family = self.family(owner)
            s, replica = self.order[t]
            require(not (r == replica and family[1] == self.pair[s]),
                    "active", "helper hosted on its active data family")
            call_family = (t, family)
            require(call_family not in family_at_call, "family", "two helpers share one physical family at a call")
            family_at_call.add(call_family)
            require(offset >= 0 and offset + width <= self.windows[r, child][2],
                    "mask", "mask outside capacity")
            occupied[owner].append((offset, offset + width, t, h, width))
        require(len(seen) == self.N * 408, "coverage", "complete role set")
        idle = Counter()
        patterns = Counter()
        loads = {}
        for owner in self.bins:
            cap = self.windows[owner[0], owner[1]][2]
            entries = sorted(occupied.get(owner, []))
            end = 0
            for offset, stop, t, h, width in entries:
                require(offset == end, "mask", "overlap or noncompact pending prefix")
                end = stop
            require(end <= cap, "mask", "capacity")
            loads[owner] = end
            remainder = cap - end
            if remainder:
                idle[remainder] += 1
            patterns[cap, tuple(sorted(e[4] for e in entries))] += 1
        expected = face_patterns(expected_k, self.T // 37)
        require(patterns == expected, "face", f"exact face k={expected_k}")
        native = Counter()
        for name in self.names:
            native.update({int(k): n for k, n in self.providers[name]["actual_paid_profile"].items()})
        invoice = native + idle
        require(invoice == Counter({r: n * (self.T // 37) for r, n in TARGET37.items()}),
                "invoice", "complete local-plus-idle paid histogram")
        rank_mass = sum(r * n for r, n in invoice.items())
        return {"T": self.T, "calls": self.N, "roles": len(rows), "bins": len(self.bins),
                "windows": len(self.windows), "k": expected_k,
                "provider_calls": dict(Counter(self.names)),
                "native_histogram": json_counter(native), "idle_histogram": json_counter(idle),
                "paid_histogram": json_counter(invoice), "paid_rank_mass": rank_mass,
                "face_patterns": [{"capacity": cap, "widths": list(widths), "count": n}
                                  for (cap, widths), n in sorted(patterns.items())]}, loads


def face_patterns(k, copies=1):
    require(type(k) is int and 0 <= k <= 1063, "face", "specified face parameter")
    base = read("sources/construction/allocation/T37-FACE-MIX.json")
    widths = base["widths"]
    out = Counter()
    for cap, vector, count in base["target"]:
        pattern = tuple(w for w, n in zip(widths, vector) for _ in range(n))
        out[cap, pattern] += count
    delta = 1063 - k
    out[16, (8, 8)] -= delta
    out[16, (7, 9)] += delta
    out[32, (7, 7, 9, 9)] -= delta
    out[32, (7, 8, 8, 9)] += delta
    return Counter({key: value * copies for key, value in out.items() if value})


def copy_fill(fill, b):
    return {**fill, "rows": [[2*t+b, h, r+37*b, child, port, offset]
                             for t, h, r, child, port, offset in fill["rows"]]}


def two_copy_fill(fill):
    rows = copy_fill(fill, 0)["rows"] + copy_fill(fill, 1)["rows"]
    return {**fill, "rows": sorted(rows, key=lambda x: (x[0], x[1]))}


def repack(rows, affected, geometry):
    groups = defaultdict(list)
    for row in rows:
        owner = tuple(row[2:5])
        if owner in affected:
            groups[owner].append(row)
    for group in groups.values():
        offset = 0
        for row in sorted(group, key=lambda x: (x[0], x[1])):
            row[5] = offset
            offset += geometry.widths[row[0]][row[1]]


def check_start_journal(source37, start, geometry):
    rows = [row[:] for row in source37["rows"]]
    operations = read("start/JOURNAL.json.gz")
    require(len(operations) == 123, "journal", "123 predecessor swaps")
    affected = set()
    for op in operations:
        require(len(op["moves"]) == 4, "journal", "four roles per predecessor swap")
        C, D = tuple(op["C"]), tuple(op["D"])
        require(C != D and C not in affected and D not in affected,
                "journal", "disjoint frozen predecessor bins")
        affected.update((C, D))
        for mv in op["moves"]:
            i = mv["source_row"]
            require(rows[i] == mv["before"], "journal", "predecessor before row")
            t, h = rows[i][:2]
            require(geometry.widths[t][h] == mv["width"], "journal", "predecessor ordered width")
            require(tuple(mv["before"][2:5]) in (C, D) and
                    tuple(mv["after_owner"]) in (C, D), "journal", "predecessor owner support")
            rows[i][2:5] = mv["after_owner"]
    repack(rows, affected, geometry)
    require(rows == start["rows"], "journal", "exact source-to-start journal replay")
    return {"entries": len(operations), "moved_roles": 4 * len(operations),
            "touched_bins": len(affected), "exact_replay": True}


def check_candidate_journal(start, candidate, geometry, journal=None):
    journal = read("candidate/JOURNAL.json") if journal is None else journal
    require(journal["columns"] == COLUMNS and journal["start_k"] == 940 and
            journal["end_k"] == 939, "journal", "candidate journal endpoints")
    # The certificate is declarative data, never executable constructor code.
    moves = journal["moves"] if isinstance(journal, dict) else journal
    rows = [row[:] for row in start["rows"]]
    index = {(row[0], row[1]): i for i, row in enumerate(rows)}
    affected = set()
    moved = set()
    for mv in moves:
        before, after = mv["before"], mv["after"]
        key = tuple(before[:2])
        require(list(key) == mv["role"], "journal", "candidate role label")
        require(key not in moved and before[:2] == after[:2], "journal", "unchanged unique role identity")
        moved.add(key)
        i = index[key]
        require(rows[i] == before, "journal", "candidate before row")
        t, h = key
        require(geometry.widths[t][h] == mv["width"], "journal", "candidate ordered width")
        require(before[2:5] == mv["before_bin"] and after[2:5] == mv["after_bin"],
                "journal", "candidate owner labels")
        affected.update((tuple(before[2:5]), tuple(after[2:5])))
        rows[i] = after[:]
    repack(rows, affected, geometry)
    require(rows == candidate["rows"], "journal", "exact start-to-candidate journal replay")
    require(len(moves) == 6 and len(affected) == 4,
            "journal", "six-role four-bin witness")
    require(all(geometry.windows[r, child][2] in (16, 32) for r, child, port in affected),
            "journal", "no capacity-48 bin changed")
    stationary = []
    for before, after in zip(start["rows"], candidate["rows"]):
        if before != after and before[2:5] == after[2:5]:
            stationary.append({"role": before[:2], "before": before, "after": after})
    require(stationary == journal["repacked_stationary"],
            "journal", "all endpoint offset-only changes declared exactly")
    states = journal["bin_states"]
    require(len(states) == 4 and {tuple(x["bin"]) for x in states} == affected,
            "journal", "four complete endpoint bin states")
    for state in states:
        owner = tuple(state["bin"])
        before = [row for row in start["rows"] if tuple(row[2:5]) == owner]
        after = [row for row in candidate["rows"] if tuple(row[2:5]) == owner]
        L, U, cap = geometry.windows[owner[0], owner[1]]
        require(state["before"] == before and state["after"] == after,
                "journal", "exact endpoint bin occupants")
        require(state["capacity"] == cap and state["window"] ==
                {"lower_open": L, "upper_closed": U}, "journal", "independently derived bin window")

    require([x["name"] for x in journal["stages"]] ==
            ["same_width_7", "same_width_9", "inverse_face_swap"],
            "journal", "three relay stages")
    stage_rows = [row[:] for row in start["rows"]]
    stage_reports = []
    for number, stage in enumerate(journal["stages"]):
        before_rows = [row[:] for row in stage_rows]
        stage_owners = set()
        declared = stage["transfers"] + stage["repacked_stationary"]
        declared_roles = set()
        for mv in declared:
            before, after = mv["before"], mv["after"]
            key = tuple(mv["role"])
            require(key == tuple(before[:2]) == tuple(after[:2]) and key not in declared_roles,
                    "journal", "stage role identity and coverage")
            declared_roles.add(key)
            i = index[key]
            require(stage_rows[i] == before, "journal", "stage before row")
            if mv in stage["transfers"]:
                require(before[2:5] != after[2:5] and geometry.widths[key[0]][key[1]] == mv["width"],
                        "journal", "stage owner transfer width")
                stage_owners.update((tuple(before[2:5]), tuple(after[2:5])))
                stage_rows[i][2:5] = after[2:5]
            else:
                require(before[:5] == after[:5], "journal", "stage stationary role")
        repack(stage_rows, stage_owners, geometry)
        actual_roles = {tuple(before[:2]) for before, after in zip(before_rows, stage_rows) if before != after}
        require(actual_roles == declared_roles, "journal", "all and only stage changes declared")
        for mv in declared:
            require(stage_rows[index[tuple(mv["role"])]] == mv["after"],
                    "journal", "stage after row")
        stage_fill = {**start, "rows": stage_rows}
        report, _ = geometry.check(stage_fill, 940 if number < 2 else 939)
        stage_reports.append({"name": stage["name"], "transfers": len(stage["transfers"]),
                              "offset_only": len(stage["repacked_stationary"]),
                              "k": report["k"], "full_geometry_and_invoice": "PASS"})
    require(stage_rows == candidate["rows"], "journal", "three-stage replay equals endpoint witness")
    return {"moved_roles": len(moves), "touched_bins": len(affected), "exact_replay": True,
            "affected_bins": [list(x) for x in sorted(affected)],
            "staged_transfers": sum(x["transfers"] for x in stage_reports),
            "stages": stage_reports}


def controls(fill, geometry, k):
    rows = fill["rows"]
    receipts = []

    def reject(name, changed_rows, expected, expected_k=k):
        altered = {**fill, "rows": changed_rows}
        try:
            geometry.check(altered, expected_k)
        except Failure as error:
            require(error.code == expected, "control", f"{name} failed for {error.code}, wanted {expected}")
            receipts.append({"name": name, "rejected_by": error.code})
            return
        raise Failure("control", f"{name} accepted")

    reject("omitted_role", rows[:-1], "coverage")
    changed = [row[:] for row in rows]
    a = 0
    first = rows[a]
    width = geometry.widths[first[0]][first[1]]
    b = next(i for i, row in enumerate(rows) if geometry.widths[row[0]][row[1]] == width
             and not geometry.legal(row[0], tuple(first[2:5])))
    changed[a][2:] = rows[b][2:]
    changed[b][2:] = rows[a][2:]
    reject("same_width_wrong_window_exchange", changed, "window")

    groups = defaultdict(list)
    for i, row in enumerate(rows):
        groups[tuple(row[2:5])].append(i)
    by_time = defaultdict(list)
    for i, row in enumerate(rows):
        by_time[row[0]].append(i)
    collision = None
    for owner, indices in groups.items():
        cap = geometry.windows[owner[0], owner[1]][2]
        load = sum(geometry.widths[rows[i][0]][rows[i][1]] for i in indices)
        for target_i in indices:
            t = rows[target_i][0]
            for donor_i in by_time[t]:
                if tuple(rows[donor_i][2:5]) != owner and geometry.widths[t][rows[donor_i][1]] <= cap-load:
                    collision = (donor_i, owner)
                    break
            if collision:
                break
        if collision:
            break
    require(collision is not None, "control", "disjoint-mask collision fixture")
    donor_i, owner = collision
    changed = [row[:] for row in rows]
    old_owner = tuple(changed[donor_i][2:5])
    changed[donor_i][2:5] = owner
    repack(changed, {old_owner, owner}, geometry)
    reject("same_call_physical_family_disjoint_masks", changed, "family")

    owner, indices = next((owner, ix) for owner, ix in groups.items() if len(ix) >= 2)
    indices = sorted(indices, key=lambda i: rows[i][5])
    changed = [row[:] for row in rows]
    changed[indices[1]][5] = changed[indices[0]][5]
    reject("overlapping_offsets", changed, "mask")

    endpoint = None
    for owner, indices in groups.items():
        L, U, cap = geometry.windows[owner[0], owner[1]]
        if L < 0:
            continue
        for i in indices:
            width = geometry.widths[rows[i][0]][rows[i][1]]
            for j in by_time[L]:
                if geometry.widths[L][rows[j][1]] == width:
                    endpoint = (i, j)
                    break
            if endpoint:
                break
        if endpoint:
            break
    require(endpoint is not None, "control", "open lower endpoint fixture")
    i, j = endpoint
    changed = [row[:] for row in rows]
    changed[i][2:] = rows[j][2:]
    changed[j][2:] = rows[i][2:]
    reject("excluded_lower_endpoint_same_width_exchange", changed, "window")
    reject("wrong_face_parameter", rows, "face", k+1)
    return receipts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(ROOT / "INDEPENDENT-RESULT.json"))
    parser.add_argument("--check-result", help="Recompute and compare a saved receipt without rewriting it")
    args = parser.parse_args()
    manifest, pins = check_pins()
    template = read("sources/allocation/vendor/TEMPLATE.json.gz")
    plan = read("sources/allocation/vendor/PLAN.json.gz")
    providers = read("sources/allocation/PROVIDERS.json")
    order37, dispatch37 = read("start/ORDER.json"), read("start/DISPATCH.json")
    geometry37 = Geometry(order37, dispatch37, template, providers)
    require(plan["order"] == order37, "source", "PLAN order cross-check")
    for child, (pair, side, cap, lo, hi) in geometry37.child.items():
        require(plan["pairs"][str(child)] == pair and plan["sides"][str(child)] == side,
                "source", "PLAN family cross-check")
    for (r, child), (L, U, cap) in geometry37.windows.items():
        require(plan["windows"][f"{r},{child}"] == [cap, list(range(L+1, U+1))],
                "source", "PLAN window cross-check")
    call_registry = {(c["stage"], c["replica"]): c for c in plan["provider_calls"]}
    require(len(call_registry) == 333, "source", "PLAN provider identity coverage")
    require(all(call_registry[s, r]["provider"] == name for s, r, name in dispatch37),
            "dispatch", "PLAN provider assignment cross-check")
    order74 = [[s, r+37*b] for s, r in order37 for b in (0, 1)]
    dispatch74 = [[s, r+37*b, name] for s, r, name in dispatch37 for b in (0, 1)]
    require(order74 == read("sources/allocation/ORDER.json"), "embedding", "exact source T74 order")
    require(dispatch74 == read("sources/allocation/DISPATCH.json"), "embedding", "exact source T74 dispatch")
    geometry74 = Geometry(order74, dispatch74, template, providers)
    source74 = read("sources/allocation/FILL.json.gz")
    source37 = {**source74, "rows": [[t//2, h, r, c, p, o]
                                   for t, h, r, c, p, o in source74["rows"] if t % 2 == 0]}
    require(two_copy_fill(source37)["rows"] == source74["rows"],
            "embedding", "source literal fill is exact two-copy embedding")
    source_report, source_loads = geometry37.check(source37, 1063)
    source74_report, _ = geometry74.check(source74, 1063)
    require(source74_report["paid_histogram"] == read("sources/allocation/PROFILE.json"),
            "invoice", "source paid profile export")
    start = read("start/FILL.json.gz")
    start_report, start_loads = geometry37.check(start, 940)
    start_journal = check_start_journal(source37, start, geometry37)
    start74_report, _ = geometry74.check(two_copy_fill(start), 940)
    require(read("candidate/ORDER.json") == order37 and read("candidate/DISPATCH.json") == dispatch37,
            "source", "candidate order and providers unchanged")
    candidate = read("candidate/FILL.json.gz")
    candidate_report, candidate_loads = geometry37.check(candidate, 939)
    require(candidate_report["paid_histogram"] == read("candidate/PROFILE.json"),
            "invoice", "candidate complete profile file")
    candidate_journal = check_candidate_journal(start, candidate, geometry37)
    candidate74_report, candidate74_loads = geometry74.check(two_copy_fill(candidate), 939)
    require(source_loads == start_loads == candidate_loads, "invoice", "all per-bin occupied ranks unchanged")
    controls_report = controls(candidate, geometry37, 939)
    for name, mutate in [
            ("false_journal_width", lambda j: j["moves"][0].__setitem__("width", j["moves"][0]["width"]+1)),
            ("false_intermediate_offset", lambda j: j["stages"][0]["transfers"][0]["after"].__setitem__(5, 1))]:
        damaged = read("candidate/JOURNAL.json")
        mutate(damaged)
        try:
            check_candidate_journal(start, candidate, geometry37, damaged)
        except Failure as error:
            require(error.code == "journal", "control", f"{name} rejected by wrong assertion")
            controls_report.append({"name": name, "rejected_by": "journal"})
        else:
            raise Failure("control", f"{name} accepted")

    pattern_file = read("candidate/PATTERNS.json")
    require(pattern_file["T"] == 37 and pattern_file["k"] == 939 and
            pattern_file["widths"] == [4, 5, 6, 7, 8, 9], "metadata", "pattern contract")
    declared_patterns = Counter()
    for cap, vector, count in pattern_file["target"]:
        require(len(vector) == 6 and all(type(v) is int and v >= 0 for v in vector) and
                type(count) is int and count > 0, "metadata", "integral pattern multiplicities")
        pattern = tuple(w for w, n in zip(pattern_file["widths"], vector) for _ in range(n))
        require((cap, pattern) not in declared_patterns, "metadata", "unique listed pattern")
        declared_patterns[cap, pattern] = count
    require(declared_patterns == face_patterns(939), "metadata", "complete pattern file")
    meta = read("candidate/META.json")
    expected_meta = {"schema_version": 1, "T": 37, "k": 939,
            "base_commit": manifest["base_commit"], "source_commit": manifest["source_commit"],
            "capacity48_bins_changed": 0, "changed_bins": 4, "conditional_stock": 896*37+408+8+91+2,
            "cost_delta_for_every_rank_tariff": 0, "idle_profile": candidate_report["idle_histogram"],
            "moves": 6, "no_new_kappa": True, "private_buffers": 91,
            "profile": candidate_report["paid_histogram"], "rank_mass": candidate_report["paid_rank_mass"],
            "staged_transfers": 8, "start_reference": {
                "commit": manifest["predecessor_commit"], "k": 940, "path": "start/FILL.json.gz",
                "sha256": pins["start/FILL.json.gz"]}}
    require(all(meta.get(k) == v for k, v in expected_meta.items()), "metadata", "candidate numeric/boolean claims")
    descriptive_meta = {k: v for k, v in meta.items() if k not in expected_meta}
    require(set(descriptive_meta) == {"mode", "proof_level", "search"} and
            all(isinstance(v, str) for v in descriptive_meta.values()),
            "metadata", "only enumerated descriptive metadata is narrative")
    changed_bins = []
    for owner in map(tuple, candidate_journal["affected_bins"]):
        before = [row for row in start["rows"] if tuple(row[2:5]) == owner]
        after = [row for row in candidate["rows"] if tuple(row[2:5]) == owner]
        L, U, cap = geometry37.windows[owner[0], owner[1]]
        changed_bins.append({"owner": list(owner), "family": list(geometry37.family(owner)),
                             "window": {"L_open": L, "U_closed": U}, "capacity": cap,
                             "before": sorted(geometry37.widths[t][h] for t,h,*_ in before),
                             "after": sorted(geometry37.widths[t][h] for t,h,*_ in after)})
    inputs = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT/"candidate").iterdir())
              if p.is_file()}
    result = {"status": "PASS", "proof_level": "finite exact integer geometry; written tariff identity; no formal kernel proof",
              "generated_utc": datetime.now(timezone.utc).isoformat(),
              "base_commit": manifest["base_commit"], "source_manifest_sha256": sha(ROOT/"SOURCES.json"),
              "source_commit": manifest["source_commit"], "predecessor_commit": manifest["predecessor_commit"],
              "checker_sha256": sha(Path(__file__)), "source_export_sha256": pins,
              "candidate_input_sha256": inputs, "source_T37": source_report,
              "source_T74": source74_report, "start_T37": start_report,
              "start_T74": start74_report, "candidate_T37": candidate_report,
              "candidate_T74": candidate74_report, "start_journal": start_journal,
              "candidate_journal": candidate_journal, "affected_bins": changed_bins,
              "all_per_bin_loads_unchanged": True, "rejecting_controls": controls_report,
              "metadata_assertions": "all numeric, boolean and pin fields checked; 91 is an inherited premise",
              "metadata_narrative_only": descriptive_meta,
              "native_private_buffers_premise": 91,
              "conditional_namespace_formula": "896*T+408+8+91+2",
              "inherited_obligations": ["native arbitrary dirty arithmetic and literal restoration",
                  "native phase and provider endpoint widths", "physical stock and movement",
                  "precision and reachable-prefix bounds", "consumer and outer admission",
                  "all-size and machine/compiler transfer"], "new_kappa_claim": False}
    output = Path(args.check_result or args.output)
    if args.check_result:
        saved = json.loads(output.read_text())
        require(set(saved) == set(result), "receipt", "saved receipt keys")
        require(all(saved[k] == v for k, v in result.items() if k != "generated_utc"),
                "receipt", "all deterministic receipt fields reproduce")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"status": "PASS", "checked_result" if args.check_result else "output": str(output), "candidate_k": 939,
                      "roles_T37": candidate_report["roles"], "bins_T37": candidate_report["bins"],
                      "controls": len(controls_report), "new_kappa_claim": False}, sort_keys=True))


if __name__ == "__main__":
    main()
