#!/usr/bin/env python3
"""Exact all-length receiver-window floor. Apache-2.0.

Mihir Srivastava with substantial OpenAI Codex assistance. Model/source credit:
Clear1nsight #4546, Ryanson Jonathan #4567, Cinna Davis #4470, zxv and the
retained native/Clifford contributors. No predecessor acceptance code imported.
"""
import argparse
from collections import Counter, deque
from fractions import Fraction
from itertools import combinations, product
import hashlib
import heapq
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PAIRS = tuple(combinations(range(3), 2))
SOURCE_BIT, ALL_REACHED = 4, 7


def need(condition, message):
    if not condition:
        raise ValueError(message)


def span(basis):
    values = {0}
    for value in basis:
        need(type(value) is int and 0 < value < 512 and value not in values,
             "independent F2^9 basis")
        values |= {x ^ value for x in tuple(values)}
    return frozenset(values)


def dim(space):
    need(len(space) > 0 and len(space) & (len(space) - 1) == 0, "subspace size")
    return len(space).bit_length() - 1


def bounds(starts, ends):
    need(all(s <= e for s, e in zip(starts, ends)), "monotone boundaries")
    out = []
    for i, j in PAIRS:
        low = {x ^ y for x in starts[i] for y in starts[j]}
        high = ends[i] & ends[j]
        out.append((dim(low), dim(high)) if low <= high else None)
    return tuple(out)


def charge(paid, gaps):
    need(all(type(g) is int and g >= 0 for g in gaps), "nonnegative rank gaps")
    return tuple(sorted(paid + tuple(g for g in gaps if g), reverse=True))


def successors(state, intervals):
    dimensions, reached, paid = state
    for (i, j), interval in zip(PAIRS, intervals):
        if interval is None:
            continue
        for height in range(max(interval[0], dimensions[i], dimensions[j]), interval[1] + 1):
            after = list(dimensions)
            after[i] = after[j] = height
            pair = (1 << i) | (1 << j)
            reach = reached | pair if reached & pair else reached
            yield (tuple(after), reach,
                   charge(paid, (height - dimensions[i], height - dimensions[j])))


def finish(state, ends):
    return charge(state[2], tuple(e - d for e, d in zip(ends, state[0])))


def closure(starts, ends, require_reach=True):
    intervals = bounds(starts, ends)
    initial_dims, final_dims = tuple(map(dim, starts)), tuple(map(dim, ends))
    initial = (initial_dims, SOURCE_BIT, ())
    seen, pending = {initial}, deque([initial])
    while pending:
        for nxt in successors(pending.popleft(), intervals):
            need(sum(nxt[2]) == sum(nxt[0]) - sum(initial_dims), "intermediate paid mass")
            if nxt not in seen:
                seen.add(nxt)
                pending.append(nxt)
    # Independently check closure after the worklist terminates; no length cutoff.
    edges, accepted, profiles = 0, 0, set()
    for state in seen:
        for nxt in successors(state, intervals):
            need(nxt in seen, "transition-closed state set")
            edges += 1
        if not require_reach or state[1] == ALL_REACHED:
            profile = finish(state, final_dims)
            need(sum(profile) == sum(final_dims) - sum(initial_dims), "complete terminal mass")
            profiles.add(profile)
            accepted += 1
    return profiles, seen, edges, accepted, intervals


def no_dearer(old, candidate):
    """Exact order for every concave f with f(0)=0 (README slope identity)."""
    return sum(old) == sum(candidate) and all(
        sum(min(r, k) for r in old) <= sum(min(r, k) for r in candidate)
        for k in range(1, max(old + candidate, default=0)))


def shortest_truncated_cost(starts, ends, cutoff):
    """Second computation: scalar Dijkstra costs, with no paid-profile history.

    Rebuild bounds and transitions directly instead of calling closure helpers.
    All edge weights are nonnegative integers, including zero-rank loops.
    """
    begin = tuple(len(s).bit_length() - 1 for s in starts)
    final = tuple(len(e).bit_length() - 1 for e in ends)
    edges = []
    for i in range(3):
        for j in range(i + 1, 3):
            required = {x ^ y for x in starts[i] for y in starts[j]}
            allowed = ends[i] & ends[j]
            if required <= allowed:
                edges.append((i, j, len(required).bit_length() - 1,
                              len(allowed).bit_length() - 1))
    initial = (begin, (False, False, True))
    distances = {initial: 0}
    queue = [(0, initial)]
    best = None
    while queue:
        cost, state = heapq.heappop(queue)
        if cost != distances[state]:
            continue
        dimensions, reached = state
        if all(reached):
            complete = cost + sum(min(e - d, cutoff) for e, d in zip(final, dimensions))
            best = complete if best is None else min(best, complete)
        for i, j, low, high in edges:
            for h in range(max(low, dimensions[i], dimensions[j]), high + 1):
                ds, rs = list(dimensions), list(reached)
                ds[i] = ds[j] = h
                rs[i] = rs[j] = reached[i] or reached[j]
                target = (tuple(ds), tuple(rs))
                value = cost + min(h - dimensions[i], cutoff) + min(h - dimensions[j], cutoff)
                if target not in distances or value < distances[target]:
                    distances[target] = value
                    heapq.heappush(queue, (value, target))
    return best


def operands(event):
    if event[0] != "scalar":
        return ()
    gate = event[1]
    need(gate[0] in ("add", "copy", "scale", "clear"), "known scalar event")
    return gate[1:3] if gate[0] in ("add", "copy") else gate[1:2]


def windows(c, emitted):
    # Include transports into both contacts and the next-use exits, as in #4546.
    word = [e for e in emitted if e[0] != "climb"]
    state, phase, out = list(c["start"]), None, []
    for index, event in enumerate(word):
        if event[0] == "phase":
            phase = event[1]
        if phase in ("B", "cleanup_tail") and index + 1 < len(word):
            following = word[index + 1]
            if (event[0] == following[0] == "scalar"
                    and event[1][0] == following[1][0] == "add"
                    and all(r[0] == "L" for r in operands(event) + operands(following))):
                a, x = event[1][1][1], event[1][2][1]
                b, y = following[1][1][1], following[1][2][1]
                ca, cb = Fraction(*event[1][3:]), Fraction(*following[1][3:])
                if x == y and len({a, b, x}) == 3 and ca in (-1, 1) and cb in (-1, 1):
                    roles, exits = (a, b, x), []
                    for r in roles:
                        end = c["final"][r]
                        for later in word[index + 2:]:
                            if ["L", r] in operands(later):
                                end = later[2]
                                break
                            if later[0] == "warp" and later[1] == ["L", r]:
                                end = later[3]
                                break
                        exits.append(end)
                    out.append({"index": index, "phase": phase, "roles": list(roles),
                                "coefficients": [int(ca), int(cb)],
                                "entrance_bases": [c["frames"][state[r]] for r in roles],
                                "exit_bases": [c["frames"][f] for f in exits],
                                "contact_bases": [c["frames"][event[2]], c["frames"][following[2]]]})
        for r in operands(event):
            if r[0] == "L":
                state[r[1]] = event[2]
        if event[0] == "warp":
            need(event[1][0] == "L", "persistent warp")
            state[event[1][1]] = event[4]
    return out


def incumbent(starts, ends, contacts):
    current, per_field = list(starts), [[], [], []]
    for pair, contact in zip(((0, 2), (1, 2)), contacts):
        for i in pair:
            need(current[i] <= contact <= ends[i], "legal incumbent contact")
            gap = dim(contact) - dim(current[i])
            if gap:
                per_field[i].append(gap)
            current[i] = contact
    for i in range(3):
        need(current[i] <= ends[i], "legal incumbent terminal move")
        gap = dim(ends[i]) - dim(current[i])
        if gap:
            per_field[i].append(gap)
    return charge((), tuple(g for field in per_field for g in field)), per_field


def authenticate():
    count = 0
    for row in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        need(path.is_file() and not path.is_symlink(), "regular source file")
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256: " + row["path"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == row["git_blob"], "source Git blob: " + row["path"])
        count += 1
    need(count == 7, "complete seven-input constructor closure")


def construct():
    authenticate()
    code = ("import json,sys;sys.path.insert(0,sys.argv[1]);import native_joint;"
            "c,p,*_=native_joint.construct();print(json.dumps({'c':c,'p':p['forward']}))")
    with tempfile.TemporaryDirectory(prefix="receiver-floor-cache-") as cache:
        result = subprocess.run([sys.executable, "-I", "-B", "-X", "pycache_prefix=" + cache,
                                 "-c", code, str(ROOT / "research/joint-helper-lattice")],
                                capture_output=True, check=True, timeout=60)
    return json.loads(result.stdout)


def controls():
    zero, line, plane = span(()), span((1,)), span((1, 2))
    need(no_dearer((2,), (1, 1)), "concave merging positive control")
    need(not no_dearer((1, 1), (2,)), "reversed cost order rejected")
    need(not no_dearer((1,), (2,)), "missing mass rejected")
    # A model with an actual cheaper coalesced path must not be falsely excluded.
    positive, *_ = closure((zero,) * 3, (plane,) * 3)
    need((2, 2, 2) in positive and not no_dearer((1,) * 6, (2, 2, 2)),
         "positive improvement fixture")
    starts, ends = (zero, zero, line), (plane, line, line)
    valid, states, _, _, intervals = closure(starts, ends)
    mutant, *_ = closure(starts, ends, require_reach=False)
    need(valid == {(1, 1, 1)} and (2, 1) in mutant, "chronology omission caught")
    early = ((0, 0, 1), SOURCE_BIT, ())
    late = ((0, 1, 1), 6, (1,))
    need(early in set(successors(early, intervals)), "a-b zero contact before x arrives")
    need(late in set(successors(early, intervals)) and late[1] != ALL_REACHED,
         "b-x contact cannot retroactively inform a")
    need(finish(late, (2, 1, 1)) == (2, 1), "connected graph alone admits false cheap path")
    accepted = [s for s in states if s[1] == ALL_REACHED]
    need(any(sum(s[2]) < 3 for s in accepted)
         and all(sum(finish(s, (2, 1, 1))) == 3 for s in accepted), "terminal-charge omission caught")
    incompatible = bounds((line, span((2,)), zero), (line, span((2,)), zero))
    need(incompatible[0] is None, "incompatible exits disable contact")
    # Enumerate actual F2^1 geometries for all 27 monotone boundary triples and
    # all contact/frame sequences through length three. Check relaxation inclusion.
    actual_count = accepted_count = 0
    for selected in product(((zero, zero), (zero, line), (line, line)), repeat=3):
        starts, ends = tuple(s[0] for s in selected), tuple(s[1] for s in selected)
        profiles, seen, *_ = closure(starts, ends)
        layer = [(starts, SOURCE_BIT, ())]
        for length in range(4):
            next_layer = []
            for current, reach, paid in layer:
                abstract = (tuple(map(dim, current)), reach, paid)
                need(abstract in seen, "actual geometric prefix belongs to closure")
                actual_count += 1
                if reach == ALL_REACHED:
                    need(finish(abstract, tuple(map(dim, ends))) in profiles, "actual terminal profile included")
                    accepted_count += 1
                if length == 3:
                    continue
                for i, j in PAIRS:
                    for contact in (zero, line):
                        if current[i] <= contact <= ends[i] and current[j] <= contact <= ends[j]:
                            nxt = list(current)
                            nxt[i] = nxt[j] = contact
                            pair = (1 << i) | (1 << j)
                            new_reach = reach | pair if reach & pair else reach
                            new_paid = charge(paid, (dim(contact) - dim(current[i]), dim(contact) - dim(current[j])))
                            next_layer.append((tuple(nxt), new_reach, new_paid))
            layer = next_layer
    fixed = ((1, 1, 1), ALL_REACHED, (1, 1))
    need(fixed in set(successors(fixed, bounds((zero, zero, line), (line,) * 3))),
         "zero-rank loop retained without length cutoff")
    # Separately execute every directed unit-shear word through length four on
    # the exact x coefficient. Cancellations must never create unmarked support.
    coefficient_checks = 0
    layer = [((0, 0, 1), frozenset({2}))]
    for length in range(5):
        nxt = []
        for coefficients, reached in layer:
            need(all(not value or i in reached for i, value in enumerate(coefficients)),
                 "exact directed coefficient support is covered by reached mask")
            coefficient_checks += 1
            if length == 4:
                continue
            for i in range(3):
                for j in range(3):
                    if i == j:
                        continue
                    for sign in (-1, 1):
                        values = list(coefficients)
                        values[i] += sign * coefficients[j]
                        reach = reached | {i, j} if i in reached or j in reached else reached
                        nxt.append((tuple(values), reach))
        layer = nxt
    return {"actual_geometric_prefixes": actual_count, "accepted_geometric_prefixes": accepted_count,
            "directed_coefficient_prefixes": coefficient_checks,
            "chronology_mutation_rejected": True, "terminal_mass_mutation_rejected": True,
            "cost_order_mutation_rejected": True, "positive_improvement_fixture": True,
            "incompatible_contact_rejected": True, "zero_rank_loop_checked": True}


def run():
    tested = controls()
    data = construct()
    extracted = windows(data["c"], data["p"])
    need(len(extracted) == 128, "128 eligible windows")
    need(Counter(w["phase"] for w in extracted) == {"B": 123, "cleanup_tail": 5}, "phase census")
    rows = []
    for w in extracted:
        starts, ends = tuple(map(span, w["entrance_bases"])), tuple(map(span, w["exit_bases"]))
        old, per_field = incumbent(starts, ends, tuple(map(span, w["contact_bases"])))
        profiles, seen, edges, accepted, intervals = closure(starts, ends)
        need(old in profiles, "incumbent admitted")
        need(all(no_dearer(old, p) for p in profiles), "all-concave floor at " + str(w["index"]))
        m = max((r for p in profiles for r in p), default=1)
        independently_minimized = [shortest_truncated_cost(starts, ends, k) for k in range(1, m + 1)]
        need(independently_minimized == [sum(min(r, k) for r in old) for k in range(1, m + 1)],
             "Dijkstra corroborates every truncated-cost floor independently of profile history")
        rows.append({**w, "entrance_dimensions": list(map(dim, starts)), "exit_dimensions": list(map(dim, ends)),
                     "pair_bounds_ab_ax_bx": intervals, "incumbent_gaps_by_field": per_field,
                     "incumbent_profile": old, "relaxed_profiles": sorted(profiles),
                     "reachable_states": len(seen), "transition_edges": edges,
                     "accepting_states": accepted, "all_concave_costs_certified": True,
                     "dijkstra_truncated_cost_minima": independently_minimized})
    return {"schema": "receiver-window-all-length-floor/v1", "status": "PASS_RECEIVER_WINDOW_ALL_LENGTH_FLOOR",
            "base_commit": "f626db5c3a3d781d8f7695038776c621651f75e1", "new_kappa": False,
            "source_pr4470_head": "b9a13c1673e0e9697de410de16e8bbf3207a7363",
            "windows_checked": len(rows), "reachable_states": sum(w["reachable_states"] for w in rows),
            "transition_edges": sum(w["transition_edges"] for w in rows),
            "terminal_profiles_checked": sum(len(w["relaxed_profiles"]) for w in rows),
            "dijkstra_cost_checks": sum(len(w["dijkstra_truncated_cost_minima"]) for w in rows),
            "profile_count_histogram": dict(sorted(Counter(len(w["relaxed_profiles"]) for w in rows).items())),
            "controls": tested, "windows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="authoring only: replace receipt")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(controls(), sort_keys=True))
        return
    result = run()
    if args.write:
        # Keep the machine-readable window receipts at one record per line.
        header = json.dumps({k: v for k, v in result.items() if k != "windows"},
                            indent=2, sort_keys=True).rstrip()[:-1].rstrip()
        records = ",\n".join("    " + json.dumps(w, sort_keys=True) for w in result["windows"])
        encoded = header + ',\n  "windows": [\n' + records + "\n  ]\n}\n"
        (HERE / "RESULT.json").write_text(encoded, encoding="utf-8", newline="\n")
    else:
        recorded = json.loads((HERE / "RESULT.json").read_bytes())
        need(json.dumps(recorded, sort_keys=True) == json.dumps(result, sort_keys=True),
             "all receipt fields and JSON types reproduce")
    print(json.dumps({k: v for k, v in result.items() if k != "windows"}, sort_keys=True))


if __name__ == "__main__":
    main()
