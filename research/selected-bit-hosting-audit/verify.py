#!/usr/bin/env python3
"""Finite PR589 pending-axis audit; standard library, no supplier admission claim.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
Apache-2.0. Source algorithm/geometry credit is recorded in README.md.
"""
import argparse
import ast
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BIT = "research/e8-bit-p111-tuned/"
VENDOR = BIT + "vendor/pr510/e8-r480-nine-stage/vendor/"
CONTROLLER = VENDOR + "e8-r715-eleven-stage-whole/code/global_k.py"
HOSTING = VENDOR + "idle-axis-hosting/hosting_core.py"
GEOMETRY = "research/e8-bit-carrier-skeleton/code/nine/geometry.py"
V, R, REPLICAS, STAGES, DIM = 111, 439, 32, 9, 64


class Reject(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Reject(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read_json(path):
    return json.loads((ROOT / path).read_text())


def source_bindings():
    pins = json.loads((PACKAGE / "SOURCES.json").read_text())
    hashes = {}
    for item in pins["files"]:
        if item["usage"] == "input":
            raw = (ROOT / item["path"]).read_bytes()
            need(digest(raw) == item["sha256"], "source hash: " + item["path"])
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            need(blob == item["git_blob"], "source blob: " + item["path"])
            hashes[item["path"]] = digest(raw)
    selected = read_json("research/community-frontier1094-audit/SELECTED-SOURCE.json")["files"]
    for path in (BIT + "tune/EXPECTED.json", BIT + "tune/bitE8mut-p111-tuned.json.gz",
                 BIT + "data/selection9-p111.json"):
        need(selected[path] == hashes[path], "selected bit input binding")
    assembly = read_json("research/community-frontier1094-audit/ASSEMBLY.json")
    need(assembly["bit_supplier"]["commit"] == "a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46",
         "selected PR589 source head")
    need(assembly["bit_supplier"]["git_blob_sha1"] == next(
        p["git_blob"] for p in pins["files"] if p["path"] == BIT + "tune/EXPECTED.json"),
        "selected bit receipt blob")
    return hashes


def source_function(path, name):
    """Execute only a named, pinned pure function; no module imports/main/solver.

    Source recipe is an input. Source windows/expand are comparison oracles only;
    neither computes the audit's masks, timing predicate or allocation.
    """
    tree = ast.parse((ROOT / path).read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    need(len(nodes) == 1, "unique source function " + name)
    namespace = {"Counter": Counter, "defaultdict": defaultdict}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), path, "exec"), namespace)
    return namespace[name]


def source_idle_table():
    """Extract only the literal idle-table construction from pinned geometry.main.

    No sympy, port compiler or other geometry code is executed. Exact equality
    with these source entries binds the independently replayed level evolution.
    """
    tree = ast.parse((ROOT / GEOMETRY).read_text())
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    start = next(i for i, n in enumerate(main.body) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == "idle" for t in n.targets))
    nodes = main.body[start:start + 3]
    need(isinstance(nodes[0], ast.Assign) and all(isinstance(n, ast.For) for n in nodes[1:]),
         "source idle-table syntax")
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), GEOMETRY, "exec"), namespace)
    return namespace["idle"]


def controller():
    """Replay levels, including zero-rank terminal child, in source chronology."""
    recipe = source_function(CONTROLLER, "recipe")(4)
    levels = [-1] * 4
    events, children = [], []

    def advance(pair, target):
        old = levels[pair]
        need(-1 <= old <= target <= 8, "monotone idle levels")
        child = dict(kind="idle", idx=len(children), pair=pair,
                     source_level=old, target_level=target, rank=7 * (target - old))
        events.append(child)
        children.append(child)
        levels[pair] = target

    for event in recipe:
        kind = event["kind"]
        if kind == "local":
            stage, pair = event["stage"], event["pair"]
            need(levels[pair] == stage - 1, "local entry level")
            levels[pair] = stage
            events.append(event)
            if 1 <= stage <= 6:
                advance((stage + 1) // 2, stage)
            if stage == 8:
                for other in range(4):
                    advance(other, 8)
        elif kind == "bridge":
            need(levels[event["dst"]] == levels[event["src"]], "bridge levels")
            events.append(event)
        else:
            need(kind == "exchange" and levels == [8] * 4, "terminal exchange")
            events.append(event)
    keys = ("pair", "source_level", "target_level", "rank")
    need([[c[k] for k in keys] for c in children] ==
         [[c[k] for k in keys] for c in source_idle_table()], "source idle-table agreement")
    need(len(children) == 10 and sum(c["rank"] for c in children) == 189,
         "ten children, including zero-rank terminal")
    return events, children


def pending_axes(child):
    a, b = child["source_level"], child["target_level"]
    need(-1 <= a <= b <= 8, "pending level domain")
    # Chart axis 0 is q/2, axes 1..7 are q-perp, E_j = [8+7(j-1),8+7j).
    return tuple(range(1 if a == -1 else 8 + 7 * a, 8 + 7 * b))


def backwards_windows(events, children):
    answer = {}
    for child in children:
        position = events.index(child)
        pair = child["pair"]
        stages = []
        for event in reversed(events[:position]):
            if event["kind"] == "local":
                if event["pair"] == pair:
                    break
                stages.append(event["stage"])
            elif event["kind"] == "bridge" and pair in (event["src"], event["dst"]):
                break
        answer[child["idx"]] = (pair, child["rank"], frozenset(stages))
    return answer


def allocate(selection, windows):
    """Independent finite expansion of the frozen pattern/stage demand table."""
    patterns = defaultdict(list)
    for child, widths, copies in selection["patterns"]:
        need(child in windows and copies > 0 and all(w == 8 for w in widths), "pattern domain")
        patterns[child].append((tuple(widths), copies))
    demand = defaultdict(Counter)
    seen = set()
    for child, width, stage, count in selection["stages"]:
        need((child, width, stage) not in seen, "duplicate stage demand")
        seen.add((child, width, stage))
        need(child in windows and stage in windows[child][2] and width == 8 and count > 0,
             "stage demand outside window or width")
        demand[child][stage] = count
    next_helper = Counter()
    slots, remainders = [], {}
    for child, (_, child_rank, _) in sorted(windows.items()):
        copy = 0
        for widths, count in sorted(patterns[child], key=lambda p: (-sum(p[0]), p[0])):
            need(sum(widths) <= child_rank, "pattern exceeds child")
            for _ in range(count):
                need(copy < 2 * V, "too many copies")
                offset = 0
                for width in sorted(widths, reverse=True):
                    candidates = [s for s, n in demand[child].items() if n > 0]
                    need(candidates, "missing stage supply")
                    stage = min(candidates)
                    helper = next_helper[stage]
                    need(helper < R, "helper supply exhausted")
                    next_helper[stage] += 1
                    demand[child][stage] -= 1
                    slots.append((child, copy, offset, width, stage, helper))
                    offset += width
                remainders[child, copy] = child_rank - offset
                copy += 1
        while copy < 2 * V:
            remainders[child, copy] = child_rank
            copy += 1
        need(not any(demand[child].values()), "unused stage supply")
    need(dict(next_helper) == {s: R for s in range(STAGES)}, "all helper occurrences allocated")
    return slots, remainders


def mask(axes):
    axes = tuple(axes)
    need(all(type(a) is int and 0 <= a < DIM for a in axes) and len(set(axes)) == len(axes),
         "ambient axes distinct and bounded")
    return sum(1 << a for a in axes)


def check_children(children, charts, strong=True):
    families = defaultdict(int)
    for child in children:
        axes = charts[child["idx"]]
        current = mask(axes)
        need(len(axes) == child["rank"], "child rank")
        if strong:
            need(not families[child["pair"]] & current, "cross-child physical overlap")
        families[child["pair"]] |= current
    if strong:
        for child in children:
            need(tuple(charts[child["idx"]]) == pending_axes(child), "source pending-axis binding")
    return dict(families)


def audit_slots(events, children, windows, slots, charts, strong=True):
    check_children(children, charts, strong)
    used = defaultdict(int)
    helpers = set()
    call_position = {e["stage"]: i for i, e in enumerate(events) if e["kind"] == "local"}
    deadline = {e["idx"]: i for i, e in enumerate(events) if e["kind"] == "idle"}
    calls = {e["stage"]: e for e in events if e["kind"] == "local"}
    role_masks = []
    for child, copy, offset, width, stage, helper in slots:
        need(child in windows and 0 <= copy < 2 * V and 0 <= stage < STAGES and 0 <= helper < R,
             "slot indices")
        need((stage, helper) not in helpers, "duplicate helper")
        helpers.add((stage, helper))
        need(width == 8 and 0 <= offset and offset + width <= len(charts[child]), "slot extent")
        pair = children[child]["pair"]
        need(stage in windows[child][2] and calls[stage]["pair"] != pair, "slot window")
        begin, end = call_position[stage], deadline[child]
        need(begin < end, "call before deadline")
        # Direct chronology, separate from the reverse-scan window predicate.
        for event in events[begin + 1:end]:
            need(not (event["kind"] == "local" and event["pair"] == pair), "intervening local touch")
            need(not (event["kind"] == "bridge" and pair in (event["src"], event["dst"])),
                 "intervening bridge touch")
        active = mask(charts[child][offset:offset + width])
        need(not active & used[child, copy], "within-child slot overlap")
        used[child, copy] |= active
        role_masks.append((child, copy, stage, helper, active))
    need(helpers == {(s, h) for s in range(STAGES) for h in range(R)}, "helper coverage")
    remainder = {}
    for child in children:
        whole = mask(charts[child["idx"]])
        for copy in range(2 * V):
            taken = used[child["idx"], copy]
            need(taken & ~whole == 0, "slot inside child")
            rest = whole ^ taken
            need(not taken & rest and (taken ^ rest) == whole, "exact remainder factorization")
            remainder[child["idx"], copy] = rest.bit_count()
    return role_masks, remainder


def rank(rows):
    work = [[Q(x) for x in row] for row in rows]
    pivot = 0
    for col in range(8):
        found = next((i for i in range(pivot, len(work)) if work[i][col]), None)
        if found is None:
            continue
        work[pivot], work[found] = work[found], work[pivot]
        lead = work[pivot][col]
        work[pivot] = [x / lead for x in work[pivot]]
        for i in range(pivot + 1, len(work)):
            if work[i][col]:
                coefficient = work[i][col]
                work[i] = [x - coefficient * y for x, y in zip(work[i], work[pivot])]
        pivot += 1
        if pivot == len(work):
            break
    return pivot


def local_profile(word):
    """Recount frame transitions and COPY charges, not scalar/operator semantics."""
    need((word["h"], word["v"], word["R"]) == (8, V, R), "word header")
    dims = [rank([word["lines"][i] for i in frame]) for frame in word["frames"]]
    current = word["start"][:]
    need(len(current) == 2 * V + R and all(dims[f] == 0 for f in current[2 * V:]),
         "width-eight helper entrances")
    profile = Counter()

    def climb(register, frame):
        old = current[register]
        if old != frame:
            need(dims[frame] > dims[old], "strict frame climb")
            need(set(word["frames"][old]) <= set(word["frames"][frame]), "nested closed frames")
            profile[dims[frame] - dims[old]] += 1
            current[register] = frame

    copies = []
    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            copies = [dims[current[helper]] for helper in word["ret"]]
            profile.update(copies)
            continue
        for frame, destination, sources in word[section]:
            for register in (destination, *sources):
                climb(register, frame)
    for register, frame in enumerate(word["final"]):
        climb(register, frame)
    need(copies == [7] * 9, "nine rank-seven copies")
    need(all(dims[word["final"][r]] == 8 for r in range(2 * V, 2 * V + R)), "full helper exits")
    return profile, dims


def port_projectors(word, role_masks, charts):
    # In this selection q-perp is never split. Its projector K_q suffices;
    # no particular orthonormal completion of q/2 enters this calculation.
    all_masks = [m for *_, m in role_masks] + [mask(c) for c in charts.values()]
    need(all((m & 255) in (0, 254) for m in all_masks), "whole q-perp local component")
    used = defaultdict(int)
    for child, copy, _, _, support in role_masks:
        used[child, copy] |= support
    need(all(((mask(axes) ^ used[child, copy]) & 255) in (0, 254)
             for child, axes in charts.items() for copy in range(2 * V)),
         "whole q-perp remainder component")
    need(len(word["lines"]) == V, "all live ports")
    for q in word["lines"]:
        need(len(q) == 8 and sum(x*x for x in q) == 4, "port norm")
        P = [[Q(q[i] * q[j], 4) for j in range(8)] for i in range(8)]
        K = [[Q(i == j) - P[i][j] for j in range(8)] for i in range(8)]
        need(all(sum(K[i][k] * K[k][j] for k in range(8)) == K[i][j]
                 for i in range(8) for j in range(8)), "q-perp idempotence")
        need(all(sum(K[i][j] * q[j] for j in range(8)) == 0 for i in range(8)), "q-perp kernel")
        need(sum(K[i][i] for i in range(8)) == 7, "q-perp rank")
    return len(word["lines"])


def physical_census(children, roles, remainders):
    seen_roles = set()
    family_masks = defaultdict(int)
    family_children = defaultdict(set)
    call_families = Counter()
    for replica in range(REPLICAS):
        for child, copy, stage, helper, active in roles:
            family = replica * (8 * V) + 2 * children[child]["pair"] * V + copy
            need(0 <= family < 8 * V * REPLICAS, "physical family bounds")
            key = (replica, stage, helper)
            need(key not in seen_roles, "physical role alias")
            seen_roles.add(key)
            need(not family_masks[family] & active, "physical slot overlap across children/calls")
            family_masks[family] |= active
            family_children[family].add(child)
            call_families[replica, stage, family] += 1
    need(len(seen_roles) == REPLICAS * STAGES * R, "all physical roles")
    return dict(helper_occurrences=len(seen_roles), calls=REPLICAS * STAGES,
                whole_q_perp_helper_occurrences=REPLICAS * sum((m & 255) == 254 for *_, m in roles),
                occupied_physical_families=len(family_masks),
                families_with_multiple_children=sum(len(c) > 1 for c in family_children.values()),
                maximum_helpers_of_one_call_on_one_family=max(call_families.values()),
                idle_remainder_histogram={str(r): n * REPLICAS for r, n in
                                          sorted(Counter(remainders.values()).items())})


def d_apply(support, head, tail):
    """Exact D_P on coordinate projectors: swap head/tail at support axes."""
    return (head & ~support) | (tail & support), (tail & ~support) | (head & support)


def counterexample(events, children, windows, slots, charts):
    # Pair 1: child 0 is [1,15), child 7 is [36,64). Swap axes 8 and 36
    # ONLY in the latter child's realization. Each local bin keeps its
    # rank, disjointness, window, offset and helper identity.
    need(pending_axes(children[0]) == tuple(range(1, 15)) and
         pending_axes(children[7]) == tuple(range(36, 64)) and
         children[0]["pair"] == children[7]["pair"] == 1, "counterexample source children")
    changed = dict(charts)
    changed[7] = tuple(8 if a == 36 else a for a in charts[7])
    audit_slots(events, children, windows, slots, changed, strong=False)
    original = modified = 0
    for child in children:
        if child["pair"] == 1:
            original ^= mask(charts[child["idx"]])
            modified ^= mask(changed[child["idx"]])
    need(original ^ modified == (1 << 8) | (1 << 36), "two-axis operator defect")
    expected = d_apply(original, 1 << 8, 0)
    actual = d_apply(modified, 1 << 8, 0)
    need(expected == (0, 1 << 8) and actual == (1 << 8, 0), "exact coordinate witness")
    return changed, dict(child=7, family_pair=1, axis_removed=36, axis_inserted=8,
                         overlapping_child=0, affected_axes=[8, 36],
                         input_head_axes=[8], input_tail_axes=[],
                         expected_head_axes=[], expected_tail_axes=[8],
                         actual_head_axes=[8], actual_tail_axes=[],
                         weak_count_window_check="accept", strong_geometric_check="reject")


def controls(events, children, windows, slots, charts, changed):
    rejected = []

    def reject(name, fn, expected):
        try:
            fn()
        except Reject as error:
            need(expected in str(error), name + " failed at unrelated check: " + str(error))
            rejected.append(name)
        else:
            raise Reject("accepted control: " + name)

    reject("equal_rank_cross_child_chart", lambda: check_children(children, changed), "cross-child")
    swapped = dict(charts); swapped[1] = tuple(range(22, 29))
    reject("equal_rank_disjoint_wrong_child", lambda: check_children(children, swapped), "source pending")
    repeated = dict(charts); repeated[0] = charts[0][:-1] + (charts[0][0],)
    reject("duplicate_axis_within_chart", lambda: check_children(children, repeated), "axes distinct")
    reject("omitted_helper", lambda: audit_slots(events, children, windows, slots[:-1], charts), "helper coverage")
    reject("duplicate_helper", lambda: audit_slots(events, children, windows, slots + [slots[0]], charts), "duplicate helper")
    first_multi = next(i for i, x in enumerate(slots) if x[2] == 8)
    overlapping = list(slots)
    x = list(overlapping[first_multi]); x[2] = 0; overlapping[first_multi] = tuple(x)
    reject("distinct_helper_same_child_overlap", lambda: audit_slots(events, children, windows, overlapping, charts),
           "within-child slot overlap")
    outside = list(slots)
    x = list(outside[0]); x[4] = next(s for s in range(STAGES) if s not in windows[x[0]][2]); outside[0] = tuple(x)
    reject("call_outside_window", lambda: audit_slots(events, children, windows, outside, charts), "slot window")
    bad_extent = list(slots)
    x = list(bad_extent[0]); x[2] = -1; bad_extent[0] = tuple(x)
    reject("negative_slot_offset", lambda: audit_slots(events, children, windows, bad_extent, charts), "slot extent")
    bad_width = list(slots)
    x = list(bad_width[0]); x[3] = 7; bad_width[0] = tuple(x)
    reject("rank_seven_helper", lambda: audit_slots(events, children, windows, bad_width, charts), "slot extent")
    bad_copy = list(slots)
    x = list(bad_copy[0]); x[1] = 2 * V; bad_copy[0] = tuple(x)
    reject("copy_outside_replica", lambda: audit_slots(events, children, windows, bad_copy, charts), "slot indices")
    # Retain old windows: direct chronology must detect the new touch.
    touched = deepcopy(events)
    child, _, _, _, stage, _ = slots[0]
    pos = next(i for i, e in enumerate(touched) if e.get("kind") == "local" and e["stage"] == stage)
    pair = children[child]["pair"]
    touched.insert(pos + 1, dict(kind="bridge", src=pair, dst=(pair + 1) % 4, coefficient=1))
    reject("intervening_touch_with_stale_windows", lambda: audit_slots(touched, children, windows, slots, charts),
           "intervening bridge touch")
    zero = dict(charts); zero[9] = (63,)
    reject("nonempty_zero_rank_child", lambda: check_children(children, zero), "child rank")
    return rejected


def verify():
    hashes = source_bindings()
    events, children = controller()
    charts = {c["idx"]: pending_axes(c) for c in children}
    windows = backwards_windows(events, children)
    need(windows == source_function(HOSTING, "windows")(events), "independent/source windows agree")
    selection = read_json(BIT + "data/selection9-p111.json")["bit"]
    slots, remaining = allocate(selection, windows)
    ys = {(i, tuple(p)): n for i, p, n in selection["patterns"]}
    zs = {(i, w, s): n for i, w, s, n in selection["stages"]}
    # The emitter omits the zero-rank/no-window child. Retain it in our
    # census as an explicit empty factor, but compare the exact emitted domain.
    emitted_windows = {i: w for i, w in windows.items() if w[1] > 0 and w[2]}
    reference, reference_remaining = source_function(HOSTING, "expand")(
        emitted_windows, ys, zs, {s: [(h, 8) for h in range(R)] for s in range(STAGES)}, 2 * V)
    need(slots == reference and {k: v for k, v in remaining.items() if k[0] in emitted_windows}
         == reference_remaining, "independent/source expansion agree")
    roles, actual_remaining = audit_slots(events, children, windows, slots, charts)
    need(remaining == actual_remaining, "expanded/geometric remainders agree")
    word = json.loads(gzip.decompress((ROOT / (BIT + "tune/bitE8mut-p111-tuned.json.gz")).read_bytes()))
    local, dimensions = local_profile(word)
    ports = port_projectors(word, roles, charts)
    census = physical_census(children, roles, remaining)
    complete = Counter({r: n * STAGES * REPLICAS for r, n in local.items()})
    complete.update({r: n * REPLICAS for r, n in Counter(remaining.values()).items() if r})
    expected = read_json(BIT + "tune/EXPECTED.json")
    need(dict(complete) == {int(r): n for r, n in expected["nine"]["profile"].items()}, "full paid profile")
    need(sum(r*n for r, n in complete.items()) == 1808352, "rank mass")
    need(DIM * (8 * V * REPLICAS) - sum(r*n for r, n in complete.items()) == 10272, "deficit")
    changed, witness = counterexample(events, children, windows, slots, charts)
    faults = controls(events, children, windows, slots, charts, changed)
    return dict(status="PASS_SELECTED_BIT_HOSTING_AUDIT", source_hashes=hashes,
                result_kind="finite geometric audit with a weakened-implication counterexample",
                idle_children=[dict(c, axes=list(charts[c["idx"]]), legal_stages=sorted(windows[c["idx"]][2]))
                               for c in children],
                schedule_events=len(events), local_frames=len(dimensions), port_projectors=ports,
                one_replica_slots=len(slots), slot_encoding="JSON ordered six-integer rows; compact separators",
                one_replica_slots_sha256=digest(canonical(slots)),
                local_profile={str(r): n for r, n in sorted(local.items())},
                full_profile={str(r): n for r, n in sorted(complete.items())},
                physical_census=census, counterexample=witness, rejected_controls=faults,
                scope="No full native replay, arbitrary correlated-helper realization, all-size compiler, precision/tape, analytic transfer or new kappa.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a NEW result receipt exclusively")
    args = parser.parse_args()
    try:
        result = verify()
        if args.write:
            with args.write.open("x") as stream:
                json.dump(result, stream, indent=2, sort_keys=True)
                stream.write("\n")
        else:
            expected = json.loads((PACKAGE / "RESULT.json").read_text())
            need(result == expected, "committed result receipt mismatch")
        print(result["status"] + ": 126432 helper occurrences; 111 port projectors; "
              + str(len(result["rejected_controls"])) + " controls rejected")
    except (Reject, OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit("REJECT_SELECTED_BIT_HOSTING_AUDIT: " + str(error)) from error


if __name__ == "__main__":
    main()
