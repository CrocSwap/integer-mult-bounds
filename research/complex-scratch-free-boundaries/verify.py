"""Reproduce the complete finite boundary result; offline, no writes by default."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import os
import shlex
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import search

BASE = "ba82555c64e1879e4b7decce28186f208fcb8262"
PROVIDERS = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/"
PREDECESSOR = "research/complex-swap-runs-seed37/"
INPUTS = ["research/complex-dyadic-lowering/lower.py",
          PREDECESSOR + "compiler.py", PREDECESSOR + "EXPECTED.json"]
INPUTS += [PROVIDERS + provider + "/" + name for provider in ("ck", "jp8")
           for name in ("LOCAL-PROGRAMS.json.gz", "LOCAL-CHECKS.json")]
require = search.require


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def admit_sources(root=ROOT):
    manifest = read(HERE / "SOURCES.json")
    require(manifest["base_commit"] == BASE, "base pin")
    require(set(manifest["files"]) == set(INPUTS), "source inventory")
    for name, pin in manifest["files"].items():
        raw = (root / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source SHA256: " + name)
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == pin["git_blob"], "source Git blob: " + name)
    return manifest


def recognize(events, start, end):
    """Recognize by exact 2x2 multiplication, independently of PR971's code."""
    if start + 4 > end:
        return None
    block = events[start:start + 4]
    if any(e[0] != "scalar" for e in block):
        return None
    ops = [e[1] for e in block]
    if [o[0] for o in ops] != ["add", "add", "add", "scale"]:
        return None
    a, b = tuple(ops[0][1]), tuple(ops[0][2])
    if a == b or a[0] != "L" or b[0] != "L":
        return None
    rows = {a: [Q(1), Q(0)], b: [Q(0), Q(1)]}
    for op in ops:
        target = tuple(op[1])
        if target not in rows:
            return None
        if op[0] == "add":
            source = tuple(op[2])
            if source not in rows or source == target:
                return None
            scale = Q(*op[3:5])
            rows[target] = [x + scale * y for x, y in zip(rows[target], rows[source])]
        else:
            rows[target] = [Q(*op[2:4]) * x for x in rows[target]]
    return (a, b) if rows[a] == [0, 1] and rows[b] == [1, 0] else None


def runs(events):
    cursor = 0
    while cursor < len(events):
        if events[cursor][0] != "scalar":
            cursor += 1
            continue
        start, frame = cursor, events[cursor][2]
        while cursor < len(events) and events[cursor][0] == "scalar" and events[cursor][2] == frame:
            cursor += 1
        yield start, cursor, frame


def cycles_of(mapping):
    pending = {a for a, b in mapping.items() if a != b}
    result = []
    while pending:
        first = min(pending)
        cycle = [first]
        cursor = mapping[first]
        while cursor != first:
            require(cursor in pending and cursor not in cycle, "invalid cycle")
            cycle.append(cursor)
            cursor = mapping[cursor]
        pending.difference_update(cycle)
        result.append(cycle)
    return result


def boundary_census(events):
    result = []
    for start, end, frame in runs(events):
        positions, mapping = [], {}
        cursor = start
        while cursor < end:
            pair = recognize(events, cursor, end)
            if pair is None:
                cursor += 1
                continue
            a, b = pair
            mapping.setdefault(a, a)
            mapping.setdefault(b, b)
            mapping[a], mapping[b] = mapping[b], mapping[a]
            positions.append(cursor)
            cursor += 4
        if positions:
            result.append({"start": start, "end": end, "frame": frame,
                           "swap_starts": positions,
                           "permutation": [[list(a), list(b)] for a, b in sorted(mapping.items())],
                           "cycles": [[list(a) for a in cycle] for cycle in cycles_of(mapping)]})
    return result


def census(root=ROOT):
    previous = read(root / (PREDECESSOR + "EXPECTED.json"))
    result = {}
    for provider in ("ck", "jp8"):
        directory = root / (PROVIDERS + provider)
        programs = read(directory / "LOCAL-PROGRAMS.json.gz")
        checks = read(directory / "LOCAL-CHECKS.json")
        require(set(programs) == {"forward", "backward"}, "source orientations")
        for direction, events in programs.items():
            key = provider + "/" + direction
            require(hashlib.sha256(canonical(events)).hexdigest() == checks[direction]["sha256"], "semantic source pin")
            blocks = boundary_census(events)
            require(canonical(blocks) == canonical(previous["candidate_blocks"][key]), "complete boundary census: " + key)
            types = Counter(tuple(sorted(len(c) for c in b["cycles"])) for b in blocks)
            require(types == {(2,): 28, (2, 3): 14}, "cycle census")
            result[key] = {"boundaries": blocks, "two_cycles": 28, "two_plus_three_cycles": 14,
                           "scratch_component_cost": 28 * 4 + 14 * 8,
                           "scratch_free_component_lower_bound": 28 * 4 + 14 * 9,
                           "scratch_free_component_upper_bound": 28 * 4 + 14 * 10,
                           "real_primitive_penalty_at_least": 2 * 14}
    return result


def exact_word(n):
    two = [("add", 0, 1), ("subtract", 1, 0), ("add", 0, 1), ("negate", 1)]
    three = [("subtract", 2, 1), ("subtract", 0, 2), ("add", 1, 2),
             ("add", 2, 0), ("subtract", 0, 2), ("add", 0, 1)]
    return {2: two, 3: three, 5: two + [tuple([op[0]] + [i + 2 for i in op[1:]]) for op in three]}[n]


def with_scratch(n):
    permutation = search.PERMUTATIONS[n]
    cycles = cycles_of(dict(enumerate(permutation)))
    word = []
    for cycle in cycles:
        word.append(("copy", n, cycle[0]))
        word.extend(("copy", t, s) for t, s in zip(cycle, cycle[1:]))
        word.append(("copy", cycle[-1], n))
    return word + [("clear", n)]


def exact_matrix(width, word):
    rows = [[Q(i == j) for j in range(width)] for i in range(width)]
    peak = Q(1)
    for op in word:
        tag, target = op[:2]
        require(0 <= target < width, "primitive target")
        if tag == "clear":
            rows[target] = [Q(0)] * width
        elif tag in ("negate", "double", "halve"):
            scale = {"negate": Q(-1), "double": Q(2), "halve": Q(1, 2)}[tag]
            rows[target] = [scale * x for x in rows[target]]
        else:
            source = op[2]
            require(0 <= source < width and source != target, "primitive source")
            if tag == "copy":
                rows[target] = rows[source][:]
            else:
                require(tag in ("add", "subtract"), "primitive tag")
                sign = 1 if tag == "add" else -1
                rows[target] = [x + sign * y for x, y in zip(rows[target], rows[source])]
        peak = max(peak, *(sum(abs(x) for x in row) for row in rows))
    return rows, peak


def witnesses():
    result, omissions = {}, 0
    for n, perm in search.PERMUTATIONS.items():
        target = [[Q(j == perm[i]) for j in range(n)] for i in range(n)]
        word, copy_word = exact_word(n), with_scratch(n)
        actual, peak = exact_matrix(n, word)
        require(actual == target, "scratch-free exact endpoint")
        extended = [row + [Q(0)] for row in target] + [[Q(0)] * (n + 1)]
        actual_copy, copy_peak = exact_matrix(n + 1, copy_word)
        require(actual_copy == extended, "arbitrary-dirty scratch endpoint")
        inverse = [("subtract" if op[0] == "add" else "add" if op[0] == "subtract" else op[0], *op[1:])
                   for op in reversed(word)]
        identity, _ = exact_matrix(n, word + inverse)
        require(identity == [[Q(i == j) for j in range(n)] for i in range(n)], "literal inverse")
        for width, candidate, goal in ((n, word, target), (n + 1, copy_word, extended)):
            for i in range(len(candidate)):
                bad, _ = exact_matrix(width, candidate[:i] + candidate[i + 1:])
                require(bad != goal, "omitted primitive survived")
                omissions += 1
        result[str(n)] = {"without_scratch": word, "with_scratch": copy_word,
                          "without_cost": len(word), "with_cost": len(copy_word),
                          "without_prefix_row_l1": str(peak), "with_prefix_row_l1": str(copy_peak)}
    return result, omissions


def run(root=ROOT):
    admit_sources(root)
    finite = {}
    with tempfile.TemporaryDirectory(prefix="scratch-free-boundaries-") as temporary:
        tmp = Path(temporary)
        executable = tmp / "independent"
        command = shlex.split(os.environ.get("CXX", "c++"))
        subprocess.run(command + ["-std=c++17", "-O2", "-Wall", "-Wextra", "-pedantic",
                                  str(HERE / "independent.cpp"), "-o", str(executable)], check=True)
        for n in search.PERMUTATIONS:
            distance = search.ball(n)
            path = tmp / (str(n) + ".bin")
            completed = subprocess.run([str(executable), str(n), str(path)], check=True, capture_output=True, text=True)
            require(completed.stdout == f"PASS_INDEPENDENT_BALL n={n} states={len(distance)}\n", "independent completion")
            require(path.read_bytes() == search.ball_bytes(distance), "full independent states/distances differ")
            finite[str(n)] = search.certificate(n, distance)
    require([finite[str(n)]["lower_bound"] for n in (2, 3, 5)] == [4, 6, 9], "modular cost result")
    exact, omissions = witnesses()
    return {"status": "PASS_COMPLEX_SCRATCH_FREE_BOUNDARIES", "base_commit": BASE,
            "assignment_seed": 24, "finite_search": finite, "witnesses": exact,
            "omitted_primitive_controls": omissions, "source_census": census(root),
            "scope": "Arbitrary-input permutation interfaces on exactly the moved registers. No new kappa."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, help="write a NEW receipt after all checks")
    args = parser.parse_args()
    result = run()
    if args.record:
        with args.record.open("x") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    else:
        require(canonical(result) == canonical(read(HERE / "EXPECTED.json")), "complete receipt mismatch")
    print("PASS_COMPLEX_SCRATCH_FREE_BOUNDARIES boundaries=168 states=509157 costs=4,6,>=9 scratch_costs=4,5,8 no_new_kappa")


if __name__ == "__main__":
    main()
