#!/usr/bin/env python3
"""Exact adjacent Steinberg expansion obstruction for the pinned PR589 A word.

Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
Only the Python standard library is used; no predecessor code is imported.
See README.md for the flag-completion and concave-cost arguments.
"""

import argparse
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
RECEIPT = "research/e8-bit-p111-tuned/tune/EXPECTED.json"
DIMENSION = 8


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result

    data = path.read_bytes()
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    return json.loads(data, object_pairs_hook=unique)


def source_bytes(data, row):
    require(hashlib.sha256(data).hexdigest() == row["sha256"],
            "source SHA256 mismatch: " + row["path"])
    blob = b"blob " + str(len(data)).encode() + b"\0" + data
    require(hashlib.sha1(blob).hexdigest() == row["git_blob"],
            "source Git blob mismatch: " + row["path"])


def check_sources():
    pins = load_json(HERE / "SOURCES.json")
    for row in pins["files"]:
        if row["usage"] == "input":
            source_bytes((ROOT / row["path"]).read_bytes(), row)
    return pins


def rref(rows):
    """Canonical rational row space, including true rootless intersections."""
    matrix = [list(map(Fraction, row)) for row in rows]
    require(all(len(row) == DIMENSION for row in matrix), "row dimension")
    rank = 0
    for column in range(DIMENSION):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        divisor = matrix[rank][column]
        matrix[rank] = [x / divisor for x in matrix[rank]]
        for i in range(len(matrix)):
            if i != rank and matrix[i][column]:
                multiplier = matrix[i][column]
                matrix[i] = [x - multiplier * y for x, y in zip(matrix[i], matrix[rank])]
        rank += 1
    return tuple(tuple(row) for row in matrix[:rank])


@lru_cache(None)
def orthogonal(space):
    pivots = [next(i for i, x in enumerate(row) if x) for row in space]
    vectors = []
    for free in range(DIMENSION):
        if free not in pivots:
            vector = [Fraction(int(i == free)) for i in range(DIMENSION)]
            for pivot, row in zip(pivots, space):
                vector[pivot] = -row[free]
            vectors.append(vector)
    return rref(vectors)


@lru_cache(None)
def contained(left, right):
    return rref(left + right) == right


class Geometry:
    def __init__(self, word):
        self.spaces = [rref(word["lines"][i] for i in frame) for frame in word["frames"]]
        self.dimensions = list(map(len, self.spaces))

    @lru_cache(None)
    def join(self, indices):
        return rref(row for index in indices for row in self.spaces[index])

    @lru_cache(None)
    def meet(self, indices):
        return orthogonal(rref(row for index in indices for row in orthogonal(self.spaces[index])))


def elementary(word, phase):
    # Source-list order is part of the pinned domain; no permutation is searched.
    return [(frame, target, source) for frame, target, sources in word[phase] for source in sources]


def expansion_orders(first, second):
    """The three positions of the commuting correction, with the old pair reversed."""
    _, target, source = first
    _, other_target, other_source = second
    if len({target, source, other_target, other_source}) != 3:
        return []
    if target == other_source:
        correction = (other_target, source)
    elif source == other_target:
        correction = (target, other_source)
    else:
        return []
    reversed_pair = [(other_target, other_source), (target, source)]
    return [reversed_pair[:i] + [correction] + reversed_pair[i:] for i in range(3)]


def contexts(word, operations):
    """Frame immediately before, and next fixed contact after, each elementary A gate."""
    current = list(word["start"])
    before = []
    for frame, target, source in elementary(word, "D"):
        current[target] = current[source] = frame
    for frame, target, source in operations:
        before.append(list(current))
        current[target] = current[source] = frame
    copy_frames = {r: current[r] for r in word["ret"]}
    following = list(word["final"])
    for frame, target, source in reversed(elementary(word, "B") + elementary(word, "C")):
        following[target] = following[source] = frame
    for register, frame in copy_frames.items():
        following[register] = frame
    after = [None] * len(operations)
    for i in reversed(range(len(operations))):
        after[i] = list(following)
        frame, target, source = operations[i]
        following[target] = following[source] = frame
    return before, after, copy_frames


def histogram(operations, ranks, entry, exit_ranks, registers):
    current = dict(entry)
    result = Counter()
    for rank, operands in zip(ranks, operations):
        for register in operands:
            step = rank - current[register]
            require(step >= 0, "descending frame rank")
            if step:
                result[step] += 1
            current[register] = rank
    for register in registers:
        step = exit_ranks[register] - current[register]
        require(step >= 0, "final frame rank exceeded")
        if step:
            result[step] += 1
    return [result[r] for r in range(1, DIMENSION + 1)]


def concavity_slacks(candidate, baseline):
    require(len(candidate) == len(baseline) == DIMENSION, "histogram width")
    require(all(type(n) is int and n >= 0 for n in candidate + baseline), "invalid histogram count")
    delta = [a - b for a, b in zip(candidate, baseline)]
    require(sum(r * n for r, n in enumerate(delta, 1)) == 0, "rank mass changed")
    return [sum(min(r, cut) * n for r, n in enumerate(delta, 1))
            for cut in range(1, DIMENSION + 1)]


def require_dominance(candidate, baseline):
    slacks = concavity_slacks(candidate, baseline)
    require(min(slacks) >= 0, "candidate is not concavely dominated by baseline")
    return slacks


def flag(operations, entry, following, geometry):
    registers = sorted({r for pair in operations for r in pair})
    require(len(registers) == 3 and len({frozenset(p) for p in operations}) == 3,
            "not a three-register triangle")
    lower1 = geometry.join(tuple(sorted({entry[r] for r in operations[0]})))
    lower2 = geometry.join(tuple(sorted({entry[r] for r in registers})))
    upper2 = geometry.meet(tuple(sorted({following[r] for r in registers})))
    upper3 = geometry.meet(tuple(sorted({following[r] for r in operations[2]})))
    require(contained(lower1, lower2) and contained(lower2, upper2)
            and contained(upper2, upper3), "infeasible boundary flag")
    return [len(lower1), len(lower2), len(upper2), len(upper3)]


def rank_triples(bounds):
    low1, low2, high2, high3 = bounds
    for first in range(low1, high2 + 1):
        for second in range(max(first, low2), high2 + 1):
            for third in range(second, high3 + 1):
                yield (first, second, third)


def scalar_matrix(operations, registers):
    rows = {register: 1 << i for i, register in enumerate(registers)}
    for target, source in operations:
        require(target != source, "self addition")
        rows[target] ^= rows[source]
    return tuple(rows[r] for r in registers)


def scalar_stream(word, a_operations):
    """Literal copy/erase and regenerated full-frame C, with every ADD explicit."""
    v = word["v"]
    count = 2 * v + word["R"]
    body = [("add", t, s) for _, t, s in elementary(word, "D") + a_operations]
    for j, register in enumerate(word["ret"]):
        body.append(("copy", count, register))
        body.extend(("add", v + t, count) for t, selected in enumerate(word["scatter"]) if j in selected)
        body.append(("erase", count, register))
    b_operations = elementary(word, "B")
    body.extend(("add", t, s) for _, t, s in b_operations)
    body.extend(("add", t, s) for _, t, s in reversed(a_operations + b_operations)
                if not v <= t < 2 * v)
    return body


def check_scalar_stream(word, body, reverse=False):
    """Replay on all source, target and dirty-helper basis columns."""
    v = word["v"]
    count = 2 * v + word["R"]
    rows = [1 << i for i in range(count)] + [0]
    for kind, target, source in reversed(body) if reverse else body:
        if reverse:
            kind = {"copy": "erase", "erase": "copy"}.get(kind, kind)
        if kind == "add":
            rows[target] ^= rows[source]
        elif kind == "copy":
            require(rows[target] == 0, "copy into occupied temporary")
            rows[target] = rows[source]
        else:
            require(rows[target] == rows[source], "erase of unequal copy")
            rows[target] = 0
    expected = [(1 << r) ^ ((1 << (r - v)) if v <= r < 2 * v else 0)
                for r in range(count)] + [0]
    require(rows == expected, "whole dirty-column endpoint failed")
    return sum(kind == "add" for kind, _, _ in body)


def whole_endpoint(word, a_operations, reverse=False):
    return check_scalar_stream(word, scalar_stream(word, a_operations), reverse)


def baseline_profile(word, geometry):
    current = list(word["start"])
    profile = Counter()

    def climb(register, frame):
        previous = current[register]
        require(contained(geometry.spaces[previous], geometry.spaces[frame]), "baseline frame descent")
        step = geometry.dimensions[frame] - geometry.dimensions[previous]
        if step:
            profile[step] += 1
        current[register] = frame

    for phase in "DABC":
        if phase == "B":
            for register in word["ret"]:
                profile[geometry.dimensions[current[register]]] += 1
        for frame, target, source in elementary(word, phase):
            climb(target, frame)
            climb(source, frame)
    for register, frame in enumerate(word["final"]):
        climb(register, frame)
    require(0 not in profile, "unexpected rank-zero COPY")
    return {str(rank): count for rank, count in sorted(profile.items())}


def census(word, receipt):
    require((word["h"], word["v"], word["R"]) == (8, 111, 439), "wrong word header")
    geometry = Geometry(word)
    # The source reverses compressed blocks, keeping each block's commuting
    # sources in stored order. Reversing the elementary gates is equivalent.
    z_blocks = [(t, sorted(sources)) for _, t, sources in reversed(word["A"] + word["B"])
                if not word["v"] <= t < 2 * word["v"]]
    require([(t, sorted(sources)) for _, t, sources in word["C"]] == z_blocks,
            "source cleanup differs from inverse z blocks")
    require(all(geometry.dimensions[f] == DIMENSION
                and geometry.dimensions[word["final"][r]] == DIMENSION
                for f, t, s in elementary(word, "C") for r in (t, s)),
            "cleanup or its final boundary is not full frame")
    operations = elementary(word, "A")
    require(len(operations) == 2130, "wrong elementary A count")
    before, after, copy_frames = contexts(word, operations)
    profile = baseline_profile(word, geometry)
    require(profile == receipt["word"]["local_histogram"], "baseline paid histogram mismatch")
    require(all(geometry.dimensions[f] == 7 for f in copy_frames.values()), "COPY ranks changed")
    baseline_adds = whole_endpoint(word, operations)
    require(baseline_adds == whole_endpoint(word, operations, reverse=True) == 24305,
            "baseline scalar bill")
    windows = []
    schedule_count = equal = strict = 0
    deltas = Counter()
    for index in range(len(operations) - 1):
        original = operations[index:index + 2]
        orders = expansion_orders(*original)
        if not orders:
            continue
        registers = sorted({r for _, t, s in original for r in (t, s)})
        require(not set(registers).intersection(word["ret"]), "COPY-touching window outside proof")
        entry = {r: before[index][r] for r in registers}
        following = {r: after[index + 1][r] for r in registers}
        entry_ranks = {r: geometry.dimensions[f] for r, f in entry.items()}
        exit_ranks = {r: geometry.dimensions[f] for r, f in following.items()}
        old_pairs = [(t, s) for _, t, s in original]
        old = histogram(old_pairs, [geometry.dimensions[f] for f, _, _ in original],
                        entry_ranks, exit_ranks, registers)
        variants = []
        for replacement in orders:
            require(scalar_matrix(replacement, registers) == scalar_matrix(old_pairs, registers),
                    "incorrect Steinberg identity")
            # Frames are irrelevant to these scalar-column checks; all geometric schedules
            # are priced separately below. No arbitrary frame assignment is asserted here.
            changed = operations[:index] + [(0, t, s) for t, s in replacement] + operations[index + 2:]
            require(whole_endpoint(word, changed) == whole_endpoint(word, changed, reverse=True) == baseline_adds + 2,
                    "unpaid new gate or cleanup")
            bounds = flag(replacement, entry, following, geometry)
            schedules = []
            for ranks in rank_triples(bounds):
                candidate = histogram(replacement, ranks, entry_ranks, exit_ranks, registers)
                slacks = require_dominance(candidate, old)
                delta = tuple(a - b for a, b in zip(candidate, old))
                deltas[delta] += 1
                equal += not any(delta)
                strict += any(delta)
                schedule_count += 1
                schedules.append([*ranks, candidate, slacks])
            require(bool(schedules), "empty schedule class")
            variants.append(dict(gates=replacement, flag_dimensions=bounds, schedules=schedules))
        windows.append(dict(index=index, original=original,
                            entry=sorted(entry.items()), following=sorted(following.items()),
                            baseline_histogram=old, variants=variants))
    remainder = {2: 13920, 4: 14208, 6: 14208, 7: 21312, 42: 288}
    global_profile = Counter({int(r): 288 * n for r, n in profile.items()})
    global_profile.update(remainder)
    require({str(r): n for r, n in sorted(global_profile.items())} == receipt["nine"]["profile"],
            "nine-stage remainder binding")
    summary = dict(windows=len(windows), corrective_orders=3 * len(windows),
                   rational_rank_schedules=schedule_count, equal_profiles=equal,
                   strictly_worse_profiles=strict, improving_profiles=0,
                   dirty_columns=661, full_scalar_replays=2 + 6 * len(windows),
                   baseline_adds=baseline_adds, expanded_adds=baseline_adds + 2,
                   local_profile=profile, local_rank_mass=sum(int(r) * n for r, n in profile.items()),
                   retained_totals=9, copy_rank=7, global_multiplier=288,
                   global_remainder={str(r): n for r, n in remainder.items()},
                   nine_stage_deficit=64 * 28416 - sum(r * n for r, n in global_profile.items()))
    require(summary["windows"] == 316 and schedule_count == 1671, "census coverage changed")
    return dict(schema="bit589-adjacent-steinberg-rational-v1", summary=summary,
                schedule_schema=["rank1", "rank2", "rank3", "histogram_at_ranks_1_through_8",
                                 "concavity_slacks_at_cuts_1_through_8"],
                delta_frequencies=[dict(delta=list(delta), multiplicity=n) for delta, n in sorted(deltas.items())],
                windows=windows)


def controls():
    rejected = []

    def rejection(name, function):
        try:
            function()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("negative control accepted: " + name)

    pair = [(1, 2), (0, 1)]
    expanded = [(0, 1), (0, 2), (1, 2)]
    endpoint = scalar_matrix(pair, [0, 1, 2])
    require(scalar_matrix(expanded, [0, 1, 2]) == endpoint, "positive scalar identity")
    for i in range(3):
        rejection("omit_expansion_gate_" + str(i),
                  lambda i=i: require(scalar_matrix(expanded[:i] + expanded[i + 1:], [0, 1, 2]) == endpoint,
                                      "deleted corrective-word gate"))
    rejection("reverse_noncommuting_chain", lambda: require(scalar_matrix(pair[::-1], [0, 1, 2]) == endpoint,
                                                            "incorrect chain order"))
    e0 = rref([[1, 0, 0, 0, 0, 0, 0, 0]])
    e1 = rref([[0, 1, 0, 0, 0, 0, 0, 0]])
    require(len(e0) == len(e1), "control dimensions")
    rejection("same_rank_wrong_subspace", lambda: require(contained(e0, e1), "rank is not containment"))
    rejection("source_rank_below_entry", lambda: histogram([(0, 1)], [0], {0: 0, 1: 1}, {0: 1, 1: 1}, [0, 1]))
    rejection("omit_paid_final_climb", lambda: require_dominance([3, 0, 0, 0, 0, 0, 0, 0],
                                                                [4, 0, 0, 0, 0, 0, 0, 0]))
    # Valid improvement outside the pinned boundary contexts: the algorithm must detect it.
    old = histogram(pair, [1, 1], {0: 0, 1: 0, 2: 1}, {0: 1, 1: 2, 2: 2}, [0, 1, 2])
    new = histogram(expanded, [0, 1, 2], {0: 0, 1: 0, 2: 1}, {0: 1, 1: 2, 2: 2}, [0, 1, 2])
    require(old == [4, 0, 0, 0, 0, 0, 0, 0] and new == [2, 1, 0, 0, 0, 0, 0, 0], "improving fixture")
    rejection("reject_false_universal_obstruction", lambda: require_dominance(new, old))
    return dict(rejected=rejected, positive_fixture=dict(old=old, expanded=new,
                                                        concavity_slacks=concavity_slacks(new, old)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", type=Path)
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json.gz")
    args = parser.parse_args()
    require(not (args.write_certificate and args.write_certificate.exists()), "output already exists")
    check_sources()
    result = census(load_json(ROOT / WORD), load_json(ROOT / RECEIPT))
    result["controls"] = controls()
    if args.write_certificate:
        args.write_certificate.write_bytes(gzip.compress(canonical(result), mtime=0))
        print("WROTE", args.write_certificate)
        return
    require(canonical(load_json(args.certificate)) == canonical(result), "certificate differs from complete replay")
    independent = [sys.executable, "-I", "-B"]
    if sys.flags.optimize:
        independent.append("-O")
    subprocess.run(independent + [str(HERE / "independent.py"), str(args.certificate.resolve())], check=True)
    summary = result["summary"]
    print("PASS_BIT589_STEINBERG_FAN",
          "pairs=" + str(summary["windows"]), "orders=" + str(summary["corrective_orders"]),
          "rank_schedules=" + str(summary["rational_rank_schedules"]),
          "improving=0", "controls=" + str(len(result["controls"]["rejected"])), "no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        raise SystemExit("FAIL_BIT589_STEINBERG_FAN: " + str(error)) from error
