"""Read-only exact verifier for the #7481 joint helper/cache bound.

Public API:
    rebuild(word_path) -> fresh source replay document
    structure(replay_doc) -> exact row-union/component document
    local_bounds(replay_doc, structure_doc) -> exact local prefix certificates

No function writes files or reads a repository/workspace snapshot. The only
native source input is the pinned compressed WORD. Fractions and standard
library modules are used throughout.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from math import gcd
from pathlib import Path


WORD_SHA256 = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"
PAYLOAD_SHA256 = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
ELIGIBLE_CACHE_EVENTS = [
    30581, 30593, 35152, 35448, 35452, 36346, 36358,
    39875, 39884, 41646, 42487, 42500, 44253, 45656,
]
CACHE_GROUPS = [
    [30581], [30593], [35152, 45656], [35448, 35452], [36346],
    [36358], [39875, 39884], [41646], [42487], [42500], [44253],
]
ZERO_ONLY_QUARTER = "6*min_column_basis_target_rank_sum >= 11*paid_rank_sum"


def need(condition, label):
    if not condition:
        raise ValueError(label)


def add(dst, src, factor=Q(1)):
    """In-place sparse rational row addition: dst += factor * src."""
    for h, value in src.items():
        result = dst.get(h, Q(0)) + factor * value
        if result:
            dst[h] = result
        else:
            dst.pop(h, None)


def reduce_row(row, basis):
    out = row.copy()
    for pivot in sorted(basis):
        if out.get(pivot):
            add(out, basis[pivot], -out[pivot])
    return out


def insert(basis, row):
    out = reduce_row(row, basis)
    if not out:
        return False
    pivot = min(out)
    scale = out[pivot]
    basis[pivot] = {h: value / scale for h, value in out.items()}
    return True


def echelon(rows):
    basis = {}
    for row in rows:
        insert(basis, row)
    return basis


def encode_row(row):
    return {str(h): str(value) for h, value in sorted(row.items()) if value}


def encode_basis(basis):
    return {str(p): encode_row(row) for p, row in sorted(basis.items())}


def _source_rows_digest(mainfree_moves, sites):
    payload = {
        "mainfree_moves": [{"event": r["event"], "owner": r["owner"],
            "owned": r["owned"], "rank": r["rank"], "row": encode_row(r["row"])}
            for r in sorted(mainfree_moves, key=lambda x: x["event"])],
        "sites": [{"event": event, "owner": sites[event]["owner"],
            "source": sites[event]["source"], "destination": sites[event]["destination"],
            "target_rank": sites[event]["target_rank"], "target": encode_row(sites[event]["target"]),
            "history_basis": encode_basis(sites[event]["history_basis"]),
            "L_basis": encode_basis(sites[event]["L_basis"])} for event in sorted(sites)],
    }
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def frame_span(basis):
    """Return the exact F2 span of an encoded native frame basis."""
    span = {0}
    for vector in basis:
        old = tuple(span)
        span.update(value ^ vector for value in old)
    need(len(span) == 1 << len(basis), "frame basis is F2 independent")
    return frozenset(span)


def kernel_lifts(rows, project):
    """Basis of the kernel on a row span, plus rank of the projected image."""
    image = {}
    image_lifts = {}
    kernel = {}
    for original in rows:
        projected = project(original)
        lift = original.copy()
        for pivot in sorted(image):
            coefficient = projected.get(pivot)
            if coefficient:
                factor = -coefficient
                add(projected, image[pivot], factor)
                add(lift, image_lifts[pivot], factor)
        if projected:
            pivot = min(projected)
            scale = projected[pivot]
            image[pivot] = {h: value / scale for h, value in projected.items()}
            image_lifts[pivot] = {h: value / scale for h, value in lift.items()}
        else:
            insert(kernel, lift)
    return kernel, len(image)


def _integer_dual_separator(history, target, coordinates):
    """Find integral t with history*t=0 and target*t!=0 in column order."""
    row_basis = echelon(history)
    pivots = set(row_basis)
    free = [h for h in coordinates if h not in pivots]
    for free_pivot in free:
        vector = {free_pivot: Q(1)}
        for pivot in sorted(row_basis, reverse=True):
            value = sum((coefficient * vector.get(h, Q(0))
                         for h, coefficient in row_basis[pivot].items() if h != pivot), Q(0))
            if value:
                vector[pivot] = -value
        dot = sum((target.get(h, Q(0)) * vector.get(h, Q(0)) for h in coordinates), Q(0))
        if dot:
            denominator = 1
            for value in vector.values():
                denominator = denominator * value.denominator // gcd(denominator, value.denominator)
            integers = {h: int(value * denominator) for h, value in vector.items() if value}
            common = 0
            for value in integers.values():
                common = gcd(common, abs(value))
            if common > 1:
                integers = {h: value // common for h, value in integers.items()}
            need(all(not sum((row.get(h, Q(0)) * integers.get(h, 0)
                              for h in coordinates), Q(0)) for row in history),
                 "separator annihilates every source history row")
            target_dot = sum((target.get(h, Q(0)) * integers.get(h, 0)
                              for h in coordinates), Q(0))
            need(target_dot, "separator distinguishes the target row")
            return {h: value for h, value in sorted(integers.items()) if value}, str(target_dot)
    raise ValueError("main-history row-space miss has a dual separator")


def rebuild(word_path):
    """Reconstruct exact source rows, 47 strict histories, and 14 L_E spaces."""
    raw = Path(word_path).read_bytes()
    need(sha256(raw).hexdigest() == WORD_SHA256, "exact #7481 native WORD bytes")
    word = json.loads(gzip.decompress(raw))
    payload = sha256(json.dumps(word, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    need(payload == PAYLOAD_SHA256, "canonical source payload")
    need(word.get("schema") and len(word["frames"]) == 1096, "native source schema and frame count")

    # Validate every frame basis before using dimension differences as prices.
    spans = [frame_span(frame) for frame in word["frames"]]
    frame_dims = [len(frame) for frame in word["frames"]]
    need(max(frame_dims) == 9, "frame dimension ceiling")
    frame_geometry = {"frame_count": len(spans), "independent_frame_count": 0,
                      "max_frame_dimension": max(frame_dims)}
    frame_geometry["independent_frame_count"] = len(spans)

    public_count = int(word["public"])
    mains = (set(word["live"]) | {h + 112 for h in word["live"]} |
             set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"]))
    helpers = set(range(public_count)) - mains
    need((len(mains), len(helpers)) == (400, 1101), "source main/helper partition")

    instructions = word["program"]
    move_instructions = [(i, ins) for i, ins in enumerate(instructions) if ins[0] == "MOVE"]
    need(len(move_instructions) == 6279, "all native MOVE instructions")
    move_forward = move_reverse = 0
    for _, ins in move_instructions:
        old, new = ins[2:4]
        old_span, new_span = spans[old], spans[new]
        need(old_span <= new_span or new_span <= old_span, "every MOVE frame pair nested")
        if old_span <= new_span:
            move_forward += 1
        else:
            move_reverse += 1
    helper_forward = helper_reverse = 0
    helper_ranks = {}
    for h in sorted(helpers):
        old, new = word["initial"][h], word["final"][h]
        old_span, new_span = spans[old], spans[new]
        need(old_span <= new_span or new_span <= old_span,
             "every helper entrance/final pair nested")
        if old_span <= new_span:
            helper_forward += 1
        else:
            helper_reverse += 1
        helper_ranks[h] = abs(frame_dims[old] - frame_dims[new])
    need((move_forward, move_reverse) == (6255, 24), "MOVE nesting census")
    need((helper_forward, helper_reverse) == (1101, 0), "helper entrance/final nesting census")
    need(all(1 <= rank <= 9 for rank in helper_ranks.values()), "helper target rank domain")
    frame_geometry.update(move_pairs=6279, move_forward=move_forward,
                          move_reverse=move_reverse,
                          helper_pairs=1101, helper_forward=helper_forward,
                          helper_reverse=helper_reverse)

    destination_keys = {spans[ins[3]] for _, ins in move_instructions if ins[4]}
    arrivals = {key: [] for key in destination_keys}
    rows = [{h: Q(1)} for h in range(public_count)] + [None] * int(word["owned_fields"])
    charts = list(word["initial"]) + [None] * int(word["owned_fields"])
    for h, frame in enumerate(word["initial"]):
        key = spans[frame]
        if key in arrivals:
            arrivals[key].append((-1, rows[h].copy()))

    cuts = {}
    mainfree_moves = []
    operation_counts = Counter()
    for event, ins in enumerate(instructions):
        operation_counts[ins[0]] += 1
        op, owner = ins[:2]
        if op == "MOVE":
            old, new = ins[2:4]
            need(charts[owner] == old and rows[owner] is not None, "MOVE source chart/value")
            source_row = rows[owner].copy()
            if source_row and set(source_row) <= helpers:
                mainfree_moves.append({"event": event, "owner": owner, "owned": bool(ins[4]),
                    "rank": abs(frame_dims[old] - frame_dims[new]), "row": source_row.copy()})
            if ins[4]:
                cuts[event] = {"event": event, "owner": owner, "source": old,
                    "destination": new, "target_rank": abs(frame_dims[old] - frame_dims[new]),
                    "target": source_row.copy()}
            rows[owner] = source_row
            charts[owner] = new
            key = spans[new]
            if key in arrivals:
                arrivals[key].append((event, source_row.copy()))
        elif op == "INIT":
            need(owner >= public_count and charts[owner] is None and rows[owner] is None,
                 "owned INIT lifecycle")
            charts[owner], rows[owner] = ins[2], {}
        elif op == "CLEAR":
            need(owner >= public_count and charts[owner] == ins[2] and rows[owner] is not None,
                 "owned CLEAR lifecycle")
            charts[owner], rows[owner] = None, None
        elif op == "SCALE":
            need(charts[owner] == ins[3] and rows[owner] is not None, "SCALE coframe")
            coefficient = Q(ins[2])
            need(coefficient, "nonzero SCALE coefficient")
            rows[owner] = {h: coefficient * value for h, value in rows[owner].items()
                           if coefficient * value}
        elif op in ("ADD", "COPY"):
            donor = ins[2]
            need(owner != donor and charts[owner] == charts[donor] == ins[4],
                 "coframed ordinary contact")
            need(rows[owner] is not None and rows[donor] is not None,
                 "ordinary contact has live rows")
            if op == "COPY":
                need(owner >= public_count and not rows[owner], "COPY begins at zero owned destination")
            add(rows[owner], rows[donor], Q(ins[3]))
        else:
            raise ValueError("unknown native operation: " + repr(op))
    need(charts == list(word["final"]) + [None] * int(word["owned_fields"]),
         "final owner chart map")
    need(len(cuts) == 47, "all 47 owned MOVE cuts")
    need(sum(operation_counts.values()) == len(instructions), "complete event replay")

    sites = {}
    cut_records = []
    main_only_events = []
    all_full_history_misses = []
    for event, cut in sorted(cuts.items()):
        key = spans[cut["destination"]]
        old_basis = {}
        earlier_rows = []
        for time, row in arrivals[key]:
            if time < event:
                earlier_rows.append(row)
                insert(old_basis, row)
        target = cut["target"]
        target_residual = reduce_row(target, old_basis)
        need(target_residual, f"owned target outside full strict history event={event} "
             f"target_support={len(target)} history_rank={len(old_basis)} "
             f"residual_support={len(target_residual)} arrivals={len(earlier_rows)}")
        old_main = echelon({h: value for h, value in row.items() if h in mains}
                           for row in old_basis.values())
        target_main = {h: value for h, value in target.items() if h in mains}
        need(target_main, "every owned target has a nonzero main projection")
        main_rem = reduce_row(target_main, old_main)
        if main_rem:
            main_only_events.append(event)
            main_history_separator, target_dot = _integer_dual_separator(
                list(old_main.values()), target_main, sorted(mains))
        else:
            main_history_separator = None
            target_dot = None
        all_full_history_misses.append(event)

        if event in ELIGIBLE_CACHE_EVENTS:
            need(word["program"][event] == ["MOVE", cut["owner"], cut["source"],
                                           cut["destination"], True], "cache MOVE literal")
            extended = {p: row.copy() for p, row in old_basis.items()}
            need(reduce_row(target, extended), "eligible target history miss")
            insert(extended, target)
            lifted, main_rank = kernel_lifts(list(extended.values()),
                lambda row: {h: value for h, value in row.items() if h in mains})
            need(len(lifted) == len(extended) - main_rank, "L_E projection rank-nullity")
            need(all(set(row) <= helpers for row in lifted.values()), "L_E is helper-only")
            need(all(reduce_row(row, extended) == {} for row in lifted.values()),
                 "L_E lies in P_E plus target")
            site = {**cut, "strict_history_rank": len(old_basis),
                    "history_basis": old_basis, "L_basis": lifted,
                    "L_dimension": len(lifted),
                    "support": sorted(set().union(*(set(row) for row in lifted.values())))}
            need(site["support"], "eligible cache space has nonempty helper support")
            sites[event] = site
        cut_records.append({"event": event, "owner": cut["owner"], "source": cut["source"],
            "destination": cut["destination"], "target_rank": cut["target_rank"],
            "strict_history_rank": len(old_basis), "full_history_miss": True,
            "main_target_support": len(target_main), "main_history_miss": bool(main_rem),
            "main_separator": main_history_separator, "separator_target_dot": target_dot})

    need(sorted(sites) == ELIGIBLE_CACHE_EVENTS, "exact 47-to-14 main-projection survivor set")
    need(len(main_only_events) == 33, "33 main-history-only obstructions")
    need(set(main_only_events).isdisjoint(sites), "main-only misses not cache-eligible")
    need(len(all_full_history_misses) == 47, "all 47 strict history misses")
    need(len(mainfree_moves) == 468, "all 468 nonzero main-free MOVE rows")
    need(all(x["row"] and set(x["row"]) <= helpers for x in mainfree_moves),
         "source-derived main-free MOVE row support")

    receipt = {
        "status": "FRESH_READ_ONLY_NATIVE_REPLAY",
        "source_sha256": WORD_SHA256,
        "source_payload_sha256": PAYLOAD_SHA256,
        "program_events": len(instructions), "public_variables": public_count,
        "main_variables": len(mains), "helper_variables": len(helpers),
        "owned_fields": int(word["owned_fields"]), "owned_MOVEs": len(cuts),
        "mainfree_nonzero_MOVEs": len(mainfree_moves),
        "all_owned_targets_miss_full_strict_history": len(all_full_history_misses),
        "main_only_history_misses": len(main_only_events),
        "cache_eligible_events": sorted(sites),
        "site_dimensions": {e: sites[e]["L_dimension"] for e in sorted(sites)},
        "sum_site_dimensions": sum(s["L_dimension"] for s in sites.values()),
        "source_rows_sha256": _source_rows_digest(mainfree_moves, sites),
        "history_model": "Strict earlier initial inputs and MOVE arrivals at equal normalized span; intervening scalar operations stay in that history span. Pooling equal-span aliases is an information overgrant only.",
        "frame_geometry": frame_geometry,
        "operation_counts": dict(sorted(operation_counts.items())),
    }
    return {"receipt": receipt, "word": word, "spans": spans,
        "main_coordinates": sorted(mains), "helper_coordinates": sorted(helpers),
        "helper_target_ranks": helper_ranks, "mainfree_moves": mainfree_moves,
        "owned_cut_records": cut_records, "main_only_events": sorted(main_only_events),
        "sites": sites}


class _DSU:
    def __init__(self, size):
        self.parent = list(range(size))
        self.size = [1] * size

    def find(self, value):
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left, right):
        left, right = self.find(left), self.find(right)
        if left == right:
            return
        if self.size[left] < self.size[right]:
            left, right = right, left
        self.parent[right] = left
        self.size[left] += self.size[right]


def structure(replay_doc):
    """Build exact zero-row/L_E union and fundamental-circuit components."""
    need(replay_doc["receipt"]["source_sha256"] == WORD_SHA256, "fresh replay source receipt")
    need(replay_doc["receipt"].get("source_rows_sha256") ==
         _source_rows_digest(replay_doc["mainfree_moves"], replay_doc["sites"]),
         "source-derived row and history digest")
    word = replay_doc["word"]
    frame_dims = [len(frame) for frame in word["frames"]]
    targets = replay_doc["helper_target_ranks"]
    expected_targets = {h: abs(frame_dims[word["initial"][h]] - frame_dims[word["final"][h]])
                        for h in replay_doc["helper_coordinates"]}
    need(targets == expected_targets, "helper target weights recomputed from native entrance/final frames")
    zero_records = sorted(replay_doc["mainfree_moves"], key=lambda item: item["event"])
    need(len(zero_records) == 468 and len({r["event"] for r in zero_records}) == 468,
         "unique complete zero MOVE set")
    zero_rows = [r["row"] for r in zero_records]
    for record in zero_records:
        ins = word["program"][record["event"]]
        need(ins[0] == "MOVE" and ins[1] == record["owner"] and
             bool(ins[4]) == record["owned"], "zero row source event identity")
        need(record["rank"] == abs(frame_dims[ins[2]] - frame_dims[ins[3]]),
             "zero MOVE paid rank recomputed from nested source frames")
    zero_rank = len(echelon(zero_rows))
    need(zero_rank == 463, "exact zero MOVE row rank")
    need(all(row and set(row) <= set(targets) for row in zero_rows), "zero MOVE helper-only rows")
    need(all(1 <= targets[h] <= 9 for row in zero_rows for h in row),
         "zero MOVE support helper ranks")
    need(all(record["rank"] <= targets[h] for record in zero_records for h in record["row"]),
         "every zero MOVE support target rank funds paid rank")
    zero_max_rank = max(record["rank"] for record in zero_records)
    need(zero_max_rank == 8, "coarse zero MOVE rank cap")

    # Ground-set order is source event order followed by fresh L_E pivots.
    labels = []
    rows = []
    for record in zero_records:
        labels.append({"kind": "zero_move", "event": record["event"],
                       "owner": record["owner"], "rank": record["rank"]})
        rows.append(record["row"].copy())
    site_indices = defaultdict(list)
    site_order = sorted(replay_doc["sites"])
    for event in site_order:
        for pivot, row in sorted(replay_doc["sites"][event]["L_basis"].items()):
            site_indices[event].append(len(rows))
            labels.append({"kind": "cache_basis", "site": event, "pivot": pivot})
            rows.append(row.copy())
    need(len(rows) == 567 and sum(len(s["L_basis"]) for s in replay_doc["sites"].values()) == 99,
         "567 source-derived rows equal 468 zero plus 99 L basis rows")

    pivots = {}
    pivot_expressions = {}
    basis_indices = []
    dsu = _DSU(len(rows))
    circuits = []
    for index, original in enumerate(rows):
        value = original.copy()
        expression = {index: Q(1)}
        for pivot in sorted(pivots):
            coefficient = value.get(pivot)
            if coefficient:
                add(value, pivots[pivot], -coefficient)
                add(expression, pivot_expressions[pivot], -coefficient)
        if value:
            pivot = min(value)
            scale = value[pivot]
            pivots[pivot] = {h: coefficient / scale for h, coefficient in value.items()}
            pivot_expressions[pivot] = {i: coefficient / scale for i, coefficient in expression.items()}
            basis_indices.append(index)
        else:
            need(expression.get(index) == 1, "fundamental relation own coefficient")
            support = sorted(i for i, coefficient in expression.items() if coefficient)
            need(index in support and len(support) >= 2, "nontrivial fundamental circuit")
            for other in support:
                if other != index:
                    dsu.union(index, other)
            circuits.append({"dependent_index": index, "support": support})
    union_rank = len(basis_indices)
    need(union_rank == 525 and len(circuits) == 42, "exact union rank and nullity")

    # Coarsen fundamental-circuit components so every whole cache space stays together.
    for indices in site_indices.values():
        for index in indices[1:]:
            dsu.union(indices[0], index)
    members_by_root = defaultdict(list)
    for index in range(len(rows)):
        members_by_root[dsu.find(index)].append(index)
    components = []
    for members in members_by_root.values():
        cache_sites = sorted({labels[i]["site"] for i in members if labels[i]["kind"] == "cache_basis"})
        zero_events = sorted(labels[i]["event"] for i in members if labels[i]["kind"] == "zero_move")
        component_rank = len(echelon(rows[i] for i in members))
        components.append({"cache_sites": cache_sites, "zero_events": zero_events,
                           "row_count": len(members), "rank": component_rank,
                           "ground_indices": sorted(members)})
    components.sort(key=lambda c: (not bool(c["cache_sites"]), c["cache_sites"], c["zero_events"]))
    cache_components = [c for c in components if c["cache_sites"]]
    zero_only = [c for c in components if not c["cache_sites"]]
    need([c["cache_sites"] for c in cache_components] == CACHE_GROUPS,
         "source-derived cache grouping")
    need(len(components) == 418 and len(cache_components) == 11 and len(zero_only) == 407,
         "coarsened source components")
    need(sum(c["rank"] for c in components) == union_rank,
         "coarsened row spaces form a direct sum")
    zero_histogram = Counter((c["row_count"], c["rank"]) for c in zero_only)
    need(zero_histogram == Counter({(1, 1): 403, (5, 4): 3, (11, 9): 1}),
         "zero-only component histogram")
    need(sum(c["rank"] for c in cache_components) == 101 and
         sum(c["rank"] for c in zero_only) == 424, "component rank partition")
    union_receipt = {
        "status": "FRESH_EXACT_567_ROW_UNION",
        "source_sha256": WORD_SHA256,
        "zero_move_rows": len(zero_records), "zero_move_rank": zero_rank,
        "zero_move_nullity": len(zero_records) - zero_rank,
        "max_zero_paid_rank": zero_max_rank,
        "cache_L_basis_rows": len(rows) - len(zero_records),
        "cache_L_dimension_sum": 99,
        "union_rows": len(rows), "union_rank": union_rank,
        "union_nullity": len(rows) - union_rank,
        "fundamental_circuit_count": len(circuits),
        "coarsened_component_count": len(components),
        "cache_component_count": len(cache_components),
        "mixed_cache_zero_component_count": sum(bool(c["zero_events"]) for c in cache_components),
        "cache_only_component_count": sum(not c["zero_events"] for c in cache_components),
        "zero_only_component_count": len(zero_only),
        "cache_component_rank_sum": sum(c["rank"] for c in cache_components),
        "zero_only_rank_sum": sum(c["rank"] for c in zero_only),
        "zero_only_component_histogram": [
            {"rows": nrows, "rank": rank, "components": count}
            for (nrows, rank), count in sorted(zero_histogram.items())],
    }
    return {"receipt": union_receipt, "labels": labels, "rows": rows,
            "circuits": circuits, "components": components,
            "cache_components": cache_components, "zero_only_components": zero_only,
            "helper_target_ranks": targets}


def _validate_structure_doc(replay_doc, structure_doc):
    """Reject altered/missing/duplicated rows or component partitions."""
    expected_labels = []
    expected_rows = []
    zero_records = sorted(replay_doc["mainfree_moves"], key=lambda r: r["event"])
    for record in zero_records:
        expected_labels.append({"kind": "zero_move", "event": record["event"],
                                "owner": record["owner"], "rank": record["rank"]})
        expected_rows.append(record["row"])
    expected_site_indices = {}
    for event in sorted(replay_doc["sites"]):
        expected_site_indices[event] = []
        for pivot, row in sorted(replay_doc["sites"][event]["L_basis"].items()):
            expected_site_indices[event].append(len(expected_rows))
            expected_labels.append({"kind": "cache_basis", "site": event, "pivot": pivot})
            expected_rows.append(row)
    need(structure_doc["labels"] == expected_labels, "complete unique ground-set labels")
    need(structure_doc["rows"] == expected_rows, "ground rows match fresh source replay")
    need(structure_doc["receipt"]["source_sha256"] == WORD_SHA256, "structure source binding")
    components = structure_doc["components"]
    seen = []
    rank_sum = 0
    for component in components:
        indices = component["ground_indices"]
        need(len(indices) == component["row_count"] and len(indices) == len(set(indices)),
             "component unique row indices")
        need(all(isinstance(i, int) and 0 <= i < len(expected_rows) for i in indices),
             "component ground-set index range")
        seen.extend(indices)
        actual_rank = len(echelon(expected_rows[i] for i in indices))
        need(actual_rank == component["rank"], "component exact rank recomputed")
        rank_sum += actual_rank
    need(sorted(seen) == list(range(len(expected_rows))), "component partition has no missing or duplicate rows")
    need(rank_sum == structure_doc["receipt"]["union_rank"] == 525,
         "component ranks reconstruct exact union rank")
    cache_components = [c for c in components if c["cache_sites"]]
    zero_only = [c for c in components if not c["cache_sites"]]
    need([c["cache_sites"] for c in cache_components] == CACHE_GROUPS,
         "component cache-site partition")
    need(len(cache_components) == 11 and len(zero_only) == 407,
         "cache and zero-only component counts")
    return True


def _restricted_rank(rows, allowed_columns):
    return len(echelon({h: coefficient for h, coefficient in row.items() if h in allowed_columns}
                       for row in rows))


def _prefix_profile(rows, target_ranks):
    columns_by_rank = {k: {h for h, rank in target_ranks.items() if rank <= k}
                       for k in range(10)}
    prefix = [_restricted_rank(rows, columns_by_rank[k]) for k in range(10)]
    need(prefix[0] == 0 and all(a <= b for a, b in zip(prefix, prefix[1:])),
         "monotone exact prefix ranks")
    return prefix, {k: prefix[k] - prefix[k-1] for k in range(1, 10)
                    if prefix[k] != prefix[k-1]}


def _site_enabled(site, zero_basis):
    combined = {p: row.copy() for p, row in site["history_basis"].items()}
    for row in zero_basis.values():
        insert(combined, row)
    return not reduce_row(site["target"], combined)


def _min_column_basis(rows, target_ranks):
    prefix, profile = _prefix_profile(rows, target_ranks)
    linear_price = sum(rank * count for rank, count in profile.items())
    return prefix, profile, linear_price


def _local_component(replay_doc, component, target_ranks, deadline_counter=None):
    events = component["cache_sites"]
    zero_events = component["zero_events"]
    zeros_by_event = {row["event"]: row for row in replay_doc["mainfree_moves"]}
    zero_rows = [zeros_by_event[event]["row"] for event in zero_events]
    zero_ranks = {event: int(zeros_by_event[event]["rank"]) for event in zero_events}
    sites = replay_doc["sites"]
    subset_docs = []
    for mask in range(1 << len(zero_events)):
        indices = [i for i in range(len(zero_events)) if mask >> i & 1]
        selected_events = [zero_events[i] for i in indices]
        Z_rows = [zero_rows[i] for i in indices]
        Z = echelon(Z_rows)
        beta_prefix, beta, _ = _min_column_basis(list(Z.values()), target_ranks)
        enabled = [event for event in events if _site_enabled(sites[event], Z)]
        newable = [event for event in events if event not in enabled]
        gamma = {}
        for event in newable:
            L = list(sites[event]["L_basis"].values())
            union_prefix, _ = _prefix_profile(list(Z.values()) + L, target_ranks)
            generic_prefix = [min(beta_prefix[k] + 1, union_prefix[k]) for k in range(10)]
            need(generic_prefix[0] == 0 and generic_prefix[9] == len(Z) + 1,
                 "generic one-row increment has exact full rank")
            need(all(a <= b for a, b in zip(generic_prefix, generic_prefix[1:])),
                 "generic prefix rank monotonicity")
            gamma[event] = {k: generic_prefix[k] - generic_prefix[k-1]
                            for k in range(1, 10)
                            if generic_prefix[k] != generic_prefix[k-1]}

        case_rows = []
        for nmask in range(1 << len(newable)):
            new = [event for j, event in enumerate(newable) if nmask >> j & 1]
            credits = Counter(zero_ranks[event] for event in selected_events)
            credits.update(sites[event]["target_rank"] for event in enabled + new)
            obligations = [(None, beta)] if not new else [(event, gamma[event]) for event in new]
            all_obligations = []
            for witness, debit in obligations:
                signed = credits.copy()
                signed.subtract(debit)
                signed = {rank: amount for rank, amount in signed.items() if amount}
                all_obligations.append({"witness": witness,
                                        "signed_profile": dict(sorted(signed.items()))})
            case_rows.append({"mask": mask, "newly_granted": new,
                              "all_necessary_obligations": all_obligations})
        subset_docs.append({"mask": mask, "zero_events": selected_events,
            "beta_prefix_ranks": beta_prefix, "beta_profile": beta,
            "enabled_sites": enabled, "new_sites": newable,
            "gamma_profiles": gamma, "cases": case_rows})
    return {"cache_sites": events, "zero_events": zero_events,
            "subset_count": len(subset_docs),
            "case_count": sum(len(s["cases"]) for s in subset_docs),
            "subsets": subset_docs}


def _verify_largest(replay_doc, component, targets):
    need(component["cache_sites"] == [35152, 45656], "largest component identity")
    expected_zeros = [32681, 39855, 39857, 39859, 45659, 45661, 45663,
                      45698, 45701, 45706, 51637, 57989, 58936, 76469]
    need(component["zero_events"] == expected_zeros, "largest component source event list")
    rows_by_event = {row["event"]: row for row in replay_doc["mainfree_moves"]}
    zero_rows = [rows_by_event[event]["row"] for event in expected_zeros]
    need(len(echelon(zero_rows)) == 14, "largest fourteen zero rows independent")
    need(all(rows_by_event[event]["rank"] <= targets[h]
             for event in expected_zeros for h in rows_by_event[event]["row"]),
         "largest zero support rank domination")
    need(all(targets[h] >= 4 for event in expected_zeros
             for h in rows_by_event[event]["row"]), "largest zero supports have target rank at least four")
    sites = replay_doc["sites"]
    need({event: sites[event]["target_rank"] for event in (35152,45656)} ==
         {35152: 2, 45656: 1}, "largest cache native MOVE ranks")
    support_min = {event: min(targets[h] for h in sites[event]["support"])
                   for event in (35152,45656)}
    need(support_min == {35152: 3, 45656: 4}, "largest cache L support minima")

    def quotient(event):
        site = sites[event]
        base = {p: row.copy() for p, row in site["history_basis"].items()}
        residual_rows = [reduce_row(row, base) for row in zero_rows]
        target_residual = reduce_row(site["target"], base)
        return residual_rows, target_residual

    rows351, target351 = quotient(35152)
    need(reduce_row(target351, echelon(rows351)), "35152 full zero quotient still misses")
    rows456, target456 = quotient(45656)
    needed = [45659,45661,45663,58936]
    index = {event:i for i,event in enumerate(expected_zeros)}
    basis = echelon(rows456)
    expression = {}
    residual = target456.copy()
    # Keep a row-coordinate expression while reducing the target.
    pivots = {}
    exprs = {}
    for i, row in enumerate(rows456):
        v = row.copy(); expr = {i: Q(1)}
        for p in sorted(pivots):
            if v.get(p):
                coefficient = v[p]
                add(v, pivots[p], -coefficient)
                add(expr, exprs[p], -coefficient)
        if v:
            p = min(v); scale = v[p]
            pivots[p] = {h: value/scale for h, value in v.items()}
            exprs[p] = {j: value/scale for j, value in expr.items()}
    for p in sorted(pivots):
        if residual.get(p):
            coefficient = residual[p]
            add(residual, pivots[p], -coefficient)
            add(expression, exprs[p], coefficient)
    need(not residual, "45656 full zero quotient hit")
    witness = {expected_zeros[i]: coefficient for i, coefficient in expression.items() if coefficient}
    need(set(witness) == set(needed), "exact four-row 45656 identity support")
    for event in needed:
        omitted = [row for other, row in zip(expected_zeros, rows456) if other != event]
        need(reduce_row(target456, echelon(omitted)), "each required zero row is essential")

    unit_events = [45659,45661,45663]
    unit_coordinates = []
    for event in unit_events:
        row = rows_by_event[event]["row"]
        need(len(row) == 1 and next(iter(row.values())) == 1 and rows_by_event[event]["rank"] == 1,
             "required disjoint unit zero row")
        coordinate = next(iter(row))
        need(targets[coordinate] == 4 and all(coordinate not in rows_by_event[other]["row"]
             for other in expected_zeros if other != event), "unit helper coordinate has target rank four and no cross-use")
        unit_coordinates.append(coordinate)
    need(len(set(unit_coordinates)) == 3, "three distinct mandatory R4 unit columns")
    need(rows_by_event[58936]["rank"] == 5 and all(targets[h] >= 5
         for h in rows_by_event[58936]["row"]), "fourth required row rank5 supported at rank>=5")
    return {"cache_sites": [35152,45656], "zero_events": expected_zeros,
        "zero_row_rank": 14, "all_zero_rows_independent": True,
        "zero_supports_dominate_paid_ranks": True, "all_zero_support_rank_at_least_four": True,
        "cache_MOVE_ranks": {"35152": 2, "45656": 1},
        "L_support_minima": {str(e): support_min[e] for e in support_min},
        "site35152_misses_full_zero_quotient": True,
        "site45656_hits_full_zero_quotient": True,
        "site45656_required_zero_events": needed,
        "site45656_witness": {str(e): str(v) for e,v in sorted(witness.items())},
        "four_omission_checks": len(needed),
        "mandatory_R4_unit_events": unit_events,
        "mandatory_R4_unit_coordinates": unit_coordinates,
        "rank5_fourth_event": 58936}


def _verify_six_zero(replay_doc, component, targets):
    expected = {
        (42487,): [31351,35683,43283,43285,46810,47178],
        (35448,35452): [34154,34156,46841,47000,48515,49195],
    }
    key = tuple(component["cache_sites"])
    need(key in expected and component["zero_events"] == expected[key], "six-zero source group")
    rows_by_event = {row["event"]: row for row in replay_doc["mainfree_moves"]}
    zero_rows = [rows_by_event[event]["row"] for event in component["zero_events"]]
    need(len(echelon(zero_rows)) == 6, "six zero rows independent")
    need(all(rows_by_event[event]["rank"] <= targets[h]
             for event in component["zero_events"] for h in rows_by_event[event]["row"]),
         "six-zero support target ranks dominate paid rank")
    need(all(targets[h] >= 4 for event in component["zero_events"]
             for h in rows_by_event[event]["row"]),
         "every six-zero support coordinate has target rank at least four")
    sites = replay_doc["sites"]
    for event in key:
        P = sites[event]["history_basis"]
        Zbasis = echelon(zero_rows)
        combined = {p:row.copy() for p,row in P.items()}
        for row in Zbasis.values(): insert(combined,row)
        need(reduce_row(sites[event]["target"], combined),
             "six-zero cache misses the full zero quotient")
    minima = {event: min(targets[h] for h in sites[event]["support"]) for event in key}
    expected_min = ({42487:4} if key == (42487,) else {35448:3, 35452:4})
    need(minima == expected_min, "six-zero cache L support minima")
    return {"cache_sites": list(key), "zero_events": component["zero_events"],
            "zero_row_rank": 6, "all_zero_rows_independent": True,
            "zero_supports_dominate_paid_ranks": True,
            "all_cache_targets_miss_full_zero_quotient": True,
            "all_zero_support_target_ranks_at_least_four": True,
            "L_support_minima": {str(e): minima[e] for e in minima}}


def _quarter_zero_certificate(replay_doc, structure_doc):
    targets = replay_doc["helper_target_ranks"]
    row_by_event = {row["event"]: row for row in replay_doc["mainfree_moves"]}
    checked = independent = dependent = 0
    dependent_margins = []
    per_component = []
    for component in structure_doc["zero_only_components"]:
        events = component["zero_events"]
        if len(events) == 1:
            continue
        component_dependent = component_independent = 0
        component_margin = None
        for mask in range(1, 1 << len(events)):
            selected = [events[i] for i in range(len(events)) if mask >> i & 1]
            subset = [row_by_event[event]["row"] for event in selected]
            rank = len(echelon(subset))
            paid = sum(row_by_event[event]["rank"] for event in selected)
            prefix, profile = _prefix_profile(subset, targets)
            basis_rank = prefix[-1]
            need(basis_rank == rank, "prefix rank agrees with exact selected row rank")
            target_sum = sum(k * count for k, count in profile.items())
            if rank == len(selected):
                independent += 1; component_independent += 1
                need(target_sum >= paid, "support matching funds independent zero-row subset")
            else:
                dependent += 1; component_dependent += 1
                margin = 6 * target_sum - 11 * paid
                dependent_margins.append(margin)
                component_margin = margin if component_margin is None else min(component_margin, margin)
                need(margin >= 0, "quarter-power funding for dependent zero-row subset")
            checked += 1
        per_component.append({"events": events, "rows": len(events), "rank": component["rank"],
                              "independent_subsets": component_independent,
                              "dependent_subsets": component_dependent,
                              "minimum_dependent_integer_margin": component_margin})
    need(checked == 2140 and independent == 2109 and dependent == 31,
         "complete 2140-subset zero-only certificate")
    need(9 * 6**4 < 11**4, "strict quarter-power envelope")
    return {"status": "PASS_SOURCE_DERIVED_ZERO_ONLY_QUARTER_FUNDING",
            "component_count": len(structure_doc["zero_only_components"]),
            "dependent_component_count": 4, "nonempty_subsets_checked": checked,
            "independent_subsets_funded_by_support": independent,
            "dependent_subsets_checked": dependent,
            "all_dependent_quarter_inequalities_pass": True,
            "minimum_dependent_integer_margin": min(dependent_margins),
            "envelope": "9*6^4<11^4",
            "component_checks": per_component,
            "scope": "For 0<=kappa<=1/4, source zero-only helper rows only; full mixed/cache and high-kappa bounds are separate."}


def local_bounds(replay_doc, structure_doc):
    """Return exact local rank-profile obligations and source checks, no prices."""
    need(replay_doc["receipt"]["source_sha256"] == structure_doc["receipt"]["source_sha256"] == WORD_SHA256,
         "local source binding")
    _validate_structure_doc(replay_doc, structure_doc)
    need(len(structure_doc["cache_components"]) == 11, "full cache component set")
    targets = replay_doc["helper_target_ranks"]
    components_by_sites = {tuple(c["cache_sites"]): c for c in structure_doc["cache_components"]}
    largest = _verify_largest(replay_doc, components_by_sites[(35152,45656)], targets)
    six = [_verify_six_zero(replay_doc, components_by_sites[key], targets)
           for key in ((42487,), (35448,35452))]
    small_keys = [(30593,), (36358,), (30581,), (36346,), (39875,39884),
                  (44253,), (42500,), (41646,)]
    small = [_local_component(replay_doc, components_by_sites[key], targets) for key in small_keys]
    need(sum(c["subset_count"] for c in small) == 43, "all eight small zero subsets")
    need(sum(c["case_count"] for c in small) == 89, "all eight small prefix cases")
    six_profiles = [_local_component(replay_doc, components_by_sites[tuple(c["cache_sites"])], targets)
                    for c in six]
    need(sum(c["subset_count"] for c in six_profiles) == 128 and
         sum(c["case_count"] for c in six_profiles) == 384,
         "all 128 six-zero subsets and 384 cache-set cases")
    quarter = _quarter_zero_certificate(replay_doc, structure_doc)
    return {"status": "PASS_SOURCE_DERIVED_LOCAL_PREFIX_OBLIGATIONS",
        "source_sha256": WORD_SHA256,
        "largest_component": largest,
        "six_zero_analytic_checks": six,
        "six_zero_prefix_profiles": six_profiles,
        "eight_small_components": small,
        "zero_only_quarter_certificate": quarter,
        "scope": "Exact source-derived scalar row-space and prefix-rank obligations. Pricing, cross-block envelopes, physical cache schedules, and any attained kappa are external and not asserted."}


def negative_controls(replay_doc, structure_doc):
    """Execute mutations against semantic rank/support/component validators."""
    controls = {}

    bad_rank = deepcopy(replay_doc)
    first = bad_rank["mainfree_moves"][0]
    first["rank"] = min(bad_rank["helper_target_ranks"][h] for h in first["row"]) + 1
    bad_rank["receipt"]["source_rows_sha256"] = _source_rows_digest(
        bad_rank["mainfree_moves"], bad_rank["sites"])
    try:
        structure(bad_rank)
    except ValueError as error:
        controls["forged_paid_rank_rejected"] = str(error) == \
            "zero MOVE paid rank recomputed from nested source frames"
    else:
        controls["forged_paid_rank_rejected"] = False
    need(controls["forged_paid_rank_rejected"], "paid rank mutation control executes and rejects")

    bad_support = deepcopy(replay_doc)
    first = bad_support["mainfree_moves"][0]
    main_coordinate = bad_support["main_coordinates"][0]
    need(main_coordinate not in first["row"], "support mutation control coordinate")
    first["row"][main_coordinate] = Q(1)
    bad_support["receipt"]["source_rows_sha256"] = _source_rows_digest(
        bad_support["mainfree_moves"], bad_support["sites"])
    try:
        structure(bad_support)
    except ValueError as error:
        controls["main_support_contamination_rejected"] = str(error) == \
            "zero MOVE helper-only rows"
    else:
        controls["main_support_contamination_rejected"] = False
    need(controls["main_support_contamination_rejected"], "support mutation control executes and rejects")

    bad_weight = deepcopy(replay_doc)
    coordinate = next(iter(bad_weight["helper_target_ranks"]))
    actual = bad_weight["helper_target_ranks"][coordinate]
    bad_weight["helper_target_ranks"][coordinate] = actual - 1 if actual > 1 else actual + 1
    try:
        structure(bad_weight)
    except ValueError as error:
        controls["forged_target_weight_rejected"] = str(error) == \
            "helper target weights recomputed from native entrance/final frames"
    else:
        controls["forged_target_weight_rejected"] = False
    need(controls["forged_target_weight_rejected"], "target weight mutation control executes and rejects")

    bad_component = deepcopy(structure_doc)
    bad_component["components"].pop()
    try:
        _validate_structure_doc(replay_doc, bad_component)
    except ValueError as error:
        controls["missing_component_rejected"] = str(error) == \
            "component partition has no missing or duplicate rows"
    else:
        controls["missing_component_rejected"] = False
    need(controls["missing_component_rejected"], "component mutation control executes and rejects")
    return {"status": "PASS_EXECUTED_NEGATIVE_CONTROLS", "controls": controls}


def to_jsonable(value):
    """Convert exact internal docs to deterministic JSON-compatible values."""
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in sorted(value.items(), key=lambda kv: str(kv[0]))}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return [to_jsonable(item) for item in sorted(value)]
    if isinstance(value, Counter):
        return to_jsonable(dict(value))
    return value
