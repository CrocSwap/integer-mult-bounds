"""Sparse, exact collector for the unchanged P104 scalar/frame trace.

This is a fresh implementation of the pooled-snapshot premise used in
AAAmirinu's PR2345.  The channel and schedule are inherited from Rohan Arun
(PR1972), Adam Gall (PR1940), and Chafik Boukhalfa (PR1991); the E8 fixture
derives from Josie Elliston (PR1071).  Substantial OpenAI Codex assistance.
Apache-2.0.  Native physical recipes and global hosting are not replayed here.
"""

from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import argparse
import hashlib
import json
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT_NAMES = {"LOWRANK-WITNESS.json", "P104-FIXTURE.json"}
PROFILE = {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8}
EVENTS = {"add": 2624, "transport": 1410, "zero": 8, "copy": 8, "erase": 8}


def need(condition, message):
    """Keep every mathematical check enabled under python -O."""
    if not condition:
        raise ValueError(message)


def _unique_json(pairs):
    answer = {}
    for key, value in pairs:
        need(key not in answer, "duplicate JSON key: " + key)
        answer[key] = value
    return answer


def read(path):
    return json.loads(Path(path).read_bytes(), object_pairs_hook=_unique_json)


def sources():
    """Read the two immutable JSON inputs through this package's own pins."""
    answer = {}
    for item in read(HERE / "SOURCES.json")["files"]:
        if item["usage"] != "input":
            continue
        path = ROOT / item["path"]
        if path.name not in INPUT_NAMES:
            continue
        need(path.name not in answer, "duplicate input pin")
        payload = path.read_bytes()
        need(hashlib.sha256(payload).hexdigest() == item["sha256"],
             "input hash mismatch: " + item["path"])
        answer[path.name] = json.loads(payload, object_pairs_hook=_unique_json)
    need(set(answer) == INPUT_NAMES, "both frozen input pins are required")
    return answer


@lru_cache(maxsize=None)
def frame(vectors):
    """Compare actual binary subspaces, independently of a chosen basis."""
    span = {0}
    for vector in vectors:
        need(type(vector) is int and 0 < vector < 512, "binary frame vector")
        need(vector not in span, "dependent binary frame basis")
        span.update(vector ^ previous for previous in tuple(span))
    return frozenset(span)


def geometry(fixture):
    """Reconstruct canonical doubled E8 root lines, then remove F0 and C."""
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            root = [0] * 8
            root[i], root[j] = 2, 2 * sign
            roots.add(tuple(root))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    removed = {tuple(row) for row in fixture["F0"] + fixture["C"]}
    need(len(roots) == 120 and len(removed) == 16 and removed <= roots,
         "P104 punctured E8 fixture")
    ports = sorted(roots - removed)
    need(len(ports) == 104, "P104 root count")
    need(all(sum(root[i] * root[j] for root in ports) == 104 * (i == j)
             for i in range(8) for j in range(8)), "root tight-frame identity")
    return ports


def collect(prefix_cuts, contacts=(), word_override=None, fixture_override=None):
    """Return nonzero source-code rows available through each prefix cut.

    All 280 arbitrary-input columns are carried as sparse integers divided
    by eight.  Every scalar update checks that this lattice remains exact.
    For target t, an eligible donor is any *other* live register in its exact
    binary frame.  Its 104 source coefficients must equal alpha R and its
    own-target dirt coefficient must vanish.  The returned alpha is an exact
    eight-tuple over Q.  Zero alpha is omitted from pools (it changes no span).

    Pools are a relaxation: contacts from different cuts may be combined
    without establishing that an inserted correction preserves the trace.
    The 175 initial independent nuisance units for each target are checked.

    Only changed frame groups require reinspection: an unchanged group's
    full rows and memberships are identical to its preceding cut.  Exact-cut
    requested contacts are checked separately, even on unchanged cuts.
    Overrides exist solely for rejecting controls; original source pins are
    still checked before applying them.  The entire endpoint is always run.
    """
    cuts = tuple(sorted(set(prefix_cuts)))
    need(all(type(cut) is int and 0 <= cut <= 4058 for cut in cuts),
         "prefix cut outside full trace")
    requested = {tuple(contact) for contact in contacts}
    for contact in requested:
        need(len(contact) == 3, "contact must have target, cut, register")
        target, cut, register = contact
        need(type(target) is int and 0 <= target < 104 and
             type(cut) is int and 0 <= cut <= 4058 and isinstance(register, str),
             "contact index outside full trace")
    by_cut = defaultdict(list)
    for target, cut, register in sorted(requested):
        by_cut[cut].append((target, register))
    pinned = sources()
    word = pinned["LOWRANK-WITNESS.json"] if word_override is None else word_override
    fixture = pinned["P104-FIXTURE.json"] if fixture_override is None else fixture_override
    ports = geometry(fixture["section4_explicit_P104"])
    names = (["X" + str(i) for i in range(104)] +
             ["Y" + str(i) for i in range(104)] +
             ["Q" + str(i) for i in range(8)] +
             ["G" + str(i) for i in range(32)] +
             ["D" + str(i) for i in range(32)])
    need(set(word) == {"initial_frames", "final_frames", "program"}, "trace fields")
    need(set(word["initial_frames"]) == set(word["final_frames"]) == set(names),
         "280 boundary register names")
    need(len(word["program"]) == 4058, "4058 channel events")
    state = {name: {index: 8} for index, name in enumerate(names)}
    frames = {name: frame(tuple(word["initial_frames"][name])) for name in names}
    need(all(len(frames[name]) == (2 if index < 104 else 1)
             for index, name in enumerate(names)), "initial source and nuisance frames")
    groups = defaultdict(set)
    for name in names:
        groups[frames[name]].add(name)
    need(len(groups[frame(())]) == 176, "175 initial nuisance donors per target")
    pools = [set() for _ in range(104)]
    checkpoints, captured = {}, {}
    projection_cache, row_cache = {}, {}
    observed = set()
    profile, events = Counter(), Counter()
    group_checks = 0
    private_copied = False

    def project(register):
        row = state[register]
        source = tuple(sorted((column, value) for column, value in row.items() if column < 104))
        if source not in projection_cache:
            alpha = tuple(Q(sum(value * ports[column][j] for column, value in source), 832)
                          for j in range(8))
            need(all(sum(alpha[j] * root[j] for j in range(8)) == Q(row.get(i, 0), 8)
                     for i, root in enumerate(ports)), "eligible source projection outside row R")
            projection_cache[source] = alpha
        return projection_cache[source]

    def donor(target, register):
        target_name = "Y" + str(target)
        need(register in state and register != target_name and
             frames[register] == frames[target_name], "contact absent or self-contact")
        need(state[register].get(104 + target, 0) == 0, "eligible donor contains own target dirt")
        return project(register)

    def inspect(cut, changed):
        nonlocal group_checks
        for chart in changed:
            members = groups.get(chart, ())
            targets = [int(name[1:]) for name in members if name.startswith("Y")]
            if not targets:
                continue
            group_checks += 1
            for register in members:
                eligible_targets = [target for target in targets if register != "Y" + str(target)]
                if not eligible_targets:
                    continue
                alpha = project(register)
                key = tuple(sorted(state[register].items()))
                # Share the immutable row object between observed target pairs.
                key = row_cache.setdefault(key, key)
                for target in eligible_targets:
                    need(state[register].get(104 + target, 0) == 0,
                         "eligible donor contains own target dirt")
                    observed.add((target, key))
                    if any(alpha):
                        pools[target].add(alpha)
        for target, register in by_cut.get(cut, ()):
            captured[target, cut, register] = donor(target, register)
        if cut in cuts:
            checkpoints[cut] = [set(pool) for pool in pools]

    inspect(0, set(groups))
    for cut, event in enumerate(word["program"], 1):
        need(isinstance(event, list) and len(event) >= 2, "malformed trace event")
        op, register = event[:2]
        need(op in EVENTS, "unknown trace operation")
        events[op] += 1
        if op == "zero":
            need(len(event) == 3 and register == "C" and register not in state,
                 "owned private allocation")
            chart = frame(tuple(event[2]))
            need(len(chart) == 256, "private allocation rank eight")
            state[register], frames[register] = {}, chart
            groups[chart].add(register)
            private_copied = False
            changed = {chart}
        else:
            need(register in state, "operation on absent register")
            old = frames[register]
            changed = {old}
            if op == "transport":
                need(len(event) == 5, "transport fields")
                before, after, paid = frame(tuple(event[2])), frame(tuple(event[3])), event[4]
                need(old == before, "transport entry frame")
                need(before < after or after < before, "strict nested transport")
                need(type(paid) is int and paid == abs(len(event[3]) - len(event[2])),
                     "transport rank")
                groups[old].remove(register)
                groups[after].add(register)
                frames[register] = after
                profile[paid] += 1
                changed.add(after)
            elif op == "erase":
                need(len(event) == 3 and register == "C" and private_copied and
                     old == frame(tuple(event[2])) and len(old) == 2,
                     "owned private discard after copied rank-one descent")
                groups[old].remove(register)
                del state[register], frames[register]
            else:
                need(len(event) == (4 if op == "copy" else 5), "scalar event fields")
                source, chart = event[2], frame(tuple(event[-1]))
                need(source in state and register != source and frames[source] == old == chart,
                     "common scalar frame")
                if op == "copy":
                    need(register == "C" and not private_copied and not state[register],
                         "copy into owned private zero")
                    state[register] = dict(state[source])
                    private_copied = True
                else:
                    need(type(event[3]) in (int, str), "exact scalar coefficient")
                    weight = Q(event[3])
                    need(weight != 0, "nonzero scalar update")
                    row = dict(state[register])
                    for column, value in state[source].items():
                        scaled = weight.numerator * value
                        need(scaled % weight.denominator == 0, "denominator-eight lattice")
                        updated = row.get(column, 0) + scaled // weight.denominator
                        if updated:
                            row[column] = updated
                        else:
                            row.pop(column, None)
                    state[register] = row
        inspect(cut, changed)

    need(set(state) == set(frames) == set(names), "private storage closed at endpoint")
    need(dict(profile) == PROFILE and dict(events) == EVENTS, "unchanged full local invoice")
    for index, register in enumerate(names):
        expected = {index: 8}
        if register.startswith("Y"):
            target = int(register[1:])
            for source, root in enumerate(ports):
                value = sum(x * y for x, y in zip(ports[target], root))
                if value:
                    expected[source] = value
        need(state[register] == expected, "arbitrary-input endpoint: " + register)
        need(frames[register] == frame(tuple(word["final_frames"][register])),
             "final frame: " + register)
        need(len(frames[register]) == (256 if register.startswith("Y") else 512),
             "final source, target or helper dimension")
    need(set(captured) == requested and set(checkpoints) == set(cuts), "requested cut coverage")
    receipt = {
        "schema": "p104-prefix-tail-trace/1",
        "cuts_replayed": 4059,
        "boundary_columns": 280,
        "initial_nuisance_units_per_target": 175,
        "distinct_target_snapshots": len(observed),
        "distinct_source_projections_checked": len(projection_cache),
        "changed_target_groups_checked": group_checks,
        "local_profile": {str(k): v for k, v in sorted(profile.items())},
        "rank_mass": sum(rank * count for rank, count in profile.items()),
        "events": dict(sorted(events.items())),
        "endpoint": "G/2; all 104 sources and 72 dirty helpers restored; private storage closed",
        "prefix_pool_totals": {str(cut): sum(map(len, checkpoints[cut])) for cut in cuts},
        "requested_contacts": len(captured),
        "input_overrides": word_override is not None or fixture_override is not None,
    }
    return {"ports": ports, "pools": checkpoints, "contacts": captured, "receipt": receipt}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    need(args.self_check, "use --self-check or import collect")
    started = time.monotonic()
    result = collect([2753, 2823])
    print(json.dumps(result["receipt"], indent=2, sort_keys=True))
    print("elapsed_seconds=%.3f" % (time.monotonic() - started))


if __name__ == "__main__":
    main()
