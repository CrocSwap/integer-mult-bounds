#!/usr/bin/env python3
"""Contact floors independent of the #4546/#4567 search engines.

Mihir Srivastava with substantial OpenAI Codex assistance. Apache-2.0.
The inherited #4470 constructor supplies data only; README.md proves the bound.
"""
from collections import Counter
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERTIFICATE = HERE / "CERTIFICATE.json"


def need(condition, message):
    if not condition:
        raise ValueError(message)


@lru_cache(None)
def span(vectors):
    values = {0}
    for vector in vectors:
        values |= {value ^ vector for value in tuple(values)}
    return frozenset(values)


def join(*spaces):
    return span(tuple(sorted(set().union(*spaces))))


def dim(space):
    need(len(space) > 0 and len(space) & (len(space) - 1) == 0, "subspace size")
    return len(space).bit_length() - 1


def basis(space):
    result, generated = [], frozenset({0})
    for vector in sorted(space):
        if vector not in generated:
            result.append(vector)
            generated = span(tuple(result))
    need(generated == space, "binary subspace")
    return result


def authenticate_inputs():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    pins = [row for row in manifest["files"] if row["usage"] == "input"]
    need(len(pins) == 7, "seven constructor input pins")
    for row in pins:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
             "source hash: " + row["path"])
    return manifest["base_commit"]


def construct():
    # A fresh cache namespace prevents a stale .pyc from replacing pinned source.
    with tempfile.TemporaryDirectory(prefix="contact-floor-") as cache:
        code = ("import json,sys;sys.path.insert(0,sys.argv[1]);import native_joint;"
                "c,p,_,_,_=native_joint.construct();print(json.dumps([c,p['forward']]))")
        run = subprocess.run(
            [sys.executable, "-I", "-B", "-X", "pycache_prefix=" + cache, "-c", code,
             str(ROOT / "research/joint-helper-lattice")],
            check=True, capture_output=True, timeout=60)
    return json.loads(run.stdout)


def participants(event):
    if event[0] != "scalar":
        return []
    operation = event[1]
    return operation[1:3] if operation[0] in ("add", "copy") else operation[1:2]


def extract_windows(canonical, program):
    """Read entrance, two contacts, and the next external use for each field."""
    frames = [span(tuple(b)) for b in canonical["frames"]]
    events = [event for event in program if event[0] != "climb"]
    current = list(canonical["start"])
    phase, windows = None, []
    for index, first in enumerate(events):
        if first[0] == "phase":
            phase = first[1]
        if phase in ("B", "cleanup_tail") and index + 1 < len(events):
            second = events[index + 1]
            if first[0] == second[0] == "scalar" and first[1][0] == second[1][0] == "add":
                f, g = first[1], second[1]
                roles = (f[1], g[1], f[2])  # a, b, x
                eligible = (f[2] == g[2] and all(r[0] == "L" for r in roles)
                            and len(set(map(tuple, roles))) == 3
                            and f[3] in (-1, 1) and g[3] in (-1, 1)
                            and f[4] == g[4] == 1)
                if eligible:
                    owners = [r[1] for r in roles]
                    starts = [frames[current[r]] for r in owners]
                    ends = []
                    for role in roles:
                        label = canonical["final"][role[1]]
                        for later in events[index + 2:]:
                            if role in participants(later):
                                label = later[2]
                                break
                            if later[0] == "warp" and later[1] == role:
                                label = later[3]
                                break
                        ends.append(frames[label])
                    windows.append({"index": index, "phase": phase, "roles": owners,
                                    "coefficients": [f[3], g[3]], "starts": starts, "ends": ends,
                                    "contacts": [frames[first[2]], frames[second[2]]]})
        if first[0] == "scalar":
            for kind, role in participants(first):
                if kind == "L":
                    current[role] = first[2]
        elif first[0] == "warp":
            current[first[1][1]] = first[4]
    need(len({w["index"] for w in windows}) == len(windows), "unique window indices")
    return windows


def path_partition(starts, ends, word, contacts):
    need(len(word) == len(contacts), "one common frame per shear")
    current, gaps = list(starts), []
    for (i, j, coefficient), contact in zip(word, contacts):
        need(i != j and coefficient != 0, "nonzero two-field shear")
        for role in (i, j):
            need(current[role] <= contact <= ends[role], "monotone contact inside fixed exit")
            if current[role] != contact:
                gaps.append(dim(contact) - dim(current[role]))
            current[role] = contact
    for before, after in zip(current, ends):
        need(before <= after, "monotone terminal movement")
        if before != after:
            gaps.append(dim(after) - dim(before))
    need(sum(gaps) == sum(map(dim, ends)) - sum(map(dim, starts)), "complete paid rank mass")
    return tuple(sorted(gaps, reverse=True))


def connected(edges):
    reached = {2}
    while True:
        updated = reached | {v for edge in edges if reached.intersection(edge) for v in edge}
        if updated == reached:
            return len(reached) == 3
        reached = updated


def relaxed_partitions(starts, ends, *, use_information=True, use_bridges=True):
    """Necessary contact dimensions only; no scalar word is enumerated."""
    need(all(s <= e for s, e in zip(starts, ends)), "nested boundaries")
    edges = {}
    for i, j in itertools.combinations(range(3), 2):
        required, cap = join(starts[i], starts[j]), ends[i] & ends[j]
        if required <= cap:
            edges[i, j] = list(range(dim(required), dim(cap) + 1))
    need(connected(edges), "admissible contact graph must connect all fields")
    bridges = [edge for edge in edges if not connected([e for e in edges if e != edge])]
    field_choices, requirements_by_field = [], []
    for role in range(3):
        # Each receiver must acquire original x; x must export it at some contact.
        witnessed = set()
        for i, j in edges:
            if role not in (i, j):
                continue
            required = join(starts[i], starts[j], starts[2]) if use_information else join(starts[i], starts[j])
            cap = ends[i] & ends[j]
            if required <= cap:
                witnessed.update(range(dim(required), dim(cap) + 1))
        requirements = [sorted(witnessed)]
        if use_bridges:
            requirements += [edges[edge] for edge in bridges if role in edge]
        need(all(requirements), "required contact has no feasible dimension")
        choices = set()
        for contacts in itertools.product(*requirements):
            marks = sorted({dim(starts[role]), dim(ends[role]), *contacts})
            choices.add(tuple(sorted((b - a for a, b in zip(marks, marks[1:])), reverse=True)))
        field_choices.append(sorted(choices))
        requirements_by_field.append(requirements)
    partitions = sorted({tuple(sorted(sum(parts, ()), reverse=True))
                         for parts in itertools.product(*field_choices)})
    return partitions, {
        "admissible_edges": [{"roles": list(edge), "dimensions": ds} for edge, ds in edges.items()],
        "mandatory_bridges": [list(edge) for edge in bridges],
        "required_dimension_sets": requirements_by_field,
        "field_partitions": [[list(p) for p in choices] for choices in field_choices],
    }


def dominates(cheaper, dearer):
    """Exact concave-price comparison, including equality at linear price."""
    if sum(cheaper) != sum(dearer):
        return False
    return all(sum(min(r, k) for r in cheaper) <= sum(min(r, k) for r in dearer)
               for k in range(1, max((*cheaper, *dearer), default=0) + 1))


IDENTITY = (1, 0, 0, 0, 1, 0, 0, 0, 1)


def act(matrix, gate):
    i, j, coefficient = gate
    result = list(matrix)
    for column in range(3):
        result[3 * i + column] += coefficient * matrix[3 * j + column]
    return tuple(result)


def subspaces(ambient_dimension):
    found = {frozenset({0})}
    while True:
        expanded = found | {join(s, frozenset({0, v})) for s in found
                            for v in range(1 << ambient_dimension)}
        if expanded == found:
            return sorted(found, key=lambda s: (len(s), sorted(s)))
        found = expanded


def controls(windows):
    by_index = {w["index"]: w for w in windows}
    failures = {}
    for index, disabled in [(10557, "use_information"), (11073, "use_bridges")]:
        w = by_index[index]
        old = path_partition(w["starts"], w["ends"], ((0, 2, 1), (1, 2, 1)), w["contacts"])
        candidates, _ = relaxed_partitions(w["starts"], w["ends"], **{disabled: False})
        failures[disabled] = [list(p) for p in candidates if not dominates(old, p)]
        need(failures[disabled], "ablation must reveal missing cost: " + disabled)
    need(not dominates((1,), (1, 1)), "rank-mass mismatch rejected")
    zero, line, plane = span(()), span((1,)), span((1, 2))
    # Changed boundaries admit a cheaper path: the checker must not always return zero.
    starts, ends = [zero] * 3, [plane] * 3
    word = ((0, 2, 1), (1, 2, 1))
    old = path_partition(starts, ends, word, (line, plane))
    better = path_partition(starts, ends, word, (plane, plane))
    candidates, _ = relaxed_partitions(starts, ends)
    need(better in candidates and dominates(better, old) and not dominates(old, better),
         "positive headroom in changed boundary fixture")
    rejected = False
    try:
        path_partition([line, zero, line], [plane] * 3, word, [zero, plane])
    except ValueError:
        rejected = True
    need(rejected, "decreasing contact rejected")

    # Exhaust actual small geometric paths, not copies of the dimension rules.
    gates = tuple((i, j, s) for i in range(3) for j in range(3) if i != j for s in (-1, 1))
    target = act(act(IDENTITY, word[0]), word[1])
    matching = []
    for length in range(5):
        for candidate in itertools.product(gates, repeat=length):
            matrix = IDENTITY
            for gate in candidate:
                matrix = act(matrix, gate)
            if matrix == target:
                matching.append(candidate)
    need(len(matching) == 84, "small exact endpoint census")
    full3 = span((1, 2, 4))
    fixtures = [(2, [zero, zero, line], [plane, line, line]),
                (3, [line, full3, span((2,))], [plane, full3, full3]),
                (2, [zero] * 3, [plane] * 3)]
    checked = []
    for ambient, starts, ends in fixtures:
        all_frames = subspaces(ambient)
        candidates, _ = relaxed_partitions(starts, ends)
        count = 0
        for candidate in matching:
            def visit(position, current, matrix, contacts):
                nonlocal count
                for role in range(3):
                    if matrix[3 * role + 2]:
                        need(starts[2] <= current[role], "source-information frame invariant")
                if position == len(candidate):
                    paid = path_partition(starts, ends, candidate, contacts)
                    need(any(dominates(p, paid) for p in candidates), "every actual path has a relaxed lower bound")
                    count += 1
                    return
                i, j, _ = candidate[position]
                for contact in all_frames:
                    if current[i] <= contact <= ends[i] and current[j] <= contact <= ends[j]:
                        state = list(current)
                        state[i] = state[j] = contact
                        visit(position + 1, state, act(matrix, candidate[position]), contacts + [contact])
            visit(0, starts, IDENTITY, [])
        need(count > 0, "positive geometric fixture")
        checked.append(count)
    return {"ablations": failures, "rank_mass_mismatch_rejected": True,
            "decreasing_contact_rejected": True,
            "changed_boundary_positive": {"old": list(old), "better": list(better)},
            "tiny_endpoint_words": len(matching), "tiny_actual_paths": checked}


def build_certificate():
    base = authenticate_inputs()
    windows = extract_windows(*construct())
    need(len(windows) == 128, "exact forward eligible-window count")
    need(Counter(w["phase"] for w in windows) == {"B": 123, "cleanup_tail": 5}, "window phases")
    rows, graph_counts = [], Counter()
    for w in windows:
        ca, cb = w["coefficients"]
        incumbent = path_partition(w["starts"], w["ends"], ((0, 2, ca), (1, 2, cb)), w["contacts"])
        candidates, details = relaxed_partitions(w["starts"], w["ends"])
        need(all(dominates(incumbent, p) for p in candidates), "concave floor at window " + str(w["index"]))
        need(incumbent in candidates, "incumbent attains floor at window " + str(w["index"]))
        graph_counts[len(details["admissible_edges"])] += 1
        row = {key: w[key] for key in ("index", "phase", "roles", "coefficients")}
        row.update({key + "_bases": [basis(s) for s in w[key]] for key in ("starts", "ends", "contacts")})
        row.update(details)
        row.update({"incumbent_partition": list(incumbent), "relaxed_partitions": [list(p) for p in candidates],
                    "all_concave_prices_certified": True})
        rows.append(row)
    return {"schema_version": 1, "status": "PASS_RECEIVER_CONTACT_FLOOR", "base_commit": base,
            "scope": "All finite three-field scalar shear words, fixed monotone boundaries, forward windows",
            "windows": rows, "window_count": len(rows),
            "contact_graph_counts": {str(k): v for k, v in sorted(graph_counts.items())},
            "controls": controls(windows), "new_kappa_claimed": False}


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="explicit authoring only; replace local certificate")
    args = parser.parse_args()
    result = build_certificate()
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        summary = json.dumps({k: v for k, v in result.items() if k != "windows"}, indent=2, sort_keys=True)
        rows = ",\n".join("    " + json.dumps(row, sort_keys=True, separators=(",", ":")) for row in result["windows"])
        formatted = summary[:-2] + ',\n  "windows": [\n' + rows + "\n  ]\n}\n"
        CERTIFICATE.write_text(formatted, encoding="utf-8", newline="\n")
    else:
        # Canonical JSON preserves types/list order and checks every proof-relevant field.
        stored = json.dumps(json.loads(CERTIFICATE.read_text(encoding="utf-8")), indent=2, sort_keys=True) + "\n"
        need(stored == serialized, "complete committed certificate equality")
    print(json.dumps({key: value for key, value in result.items() if key != "windows"}, sort_keys=True))


if __name__ == "__main__":
    main()
