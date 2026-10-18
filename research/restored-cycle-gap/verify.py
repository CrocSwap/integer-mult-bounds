"""Exact restored-cycle gap. Stdlib plus explicitly required C++17 compiler.
Philipp / mightyOil, substantial OpenAI Codex assistance. Apache-2.0.
Boundary recognizer adapted from credited Ross Richardson PR1216.
"""
import argparse
from collections import Counter, deque
from fractions import Fraction as F
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDERS = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/"
PREVIOUS = "research/complex-swap-runs-seed37/EXPECTED.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith(".gz") else raw)


def pins():
    manifest = read(HERE / "PINS.json")
    for section, base in (("package", HERE), ("live_inputs", ROOT)):
        for name, pin in manifest[section].items():
            raw = (base / name).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source SHA256: " + name)
            require(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
                    == pin["git_blob"], "source Git blob: " + name)
    return manifest


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def execute(word, n):
    rows = [list(map(F, row)) for row in identity(n)]
    for kind, t, s in word:
        if kind == "copy":
            rows[t] = list(rows[s])
        elif kind == "clear":
            rows[t] = [F(0)] * n
        elif kind == "scale":
            rows[t] = [s * x for x in rows[t]]
        else:
            require(kind in ("add", "sub") and t != s, "invalid ADD/SUB")
            rows[t] = [a + (1 if kind == "add" else -1)*b for a, b in zip(rows[t], rows[s])]
    return tuple(tuple(row) for row in rows)


def inverse(word):
    result = []
    for kind, t, s in reversed(word):
        require(kind not in ("copy", "clear"), "singular word has no declared inverse")
        result.append(("sub" if kind == "add" else "add" if kind == "sub" else "scale",
                       t, 1/s if kind == "scale" else s))
    return result


TWO = [("add", 0, 1), ("sub", 1, 0), ("add", 0, 1), ("scale", 1, F(-1))]
THREE = [("sub", 4, 3), ("sub", 2, 4), ("add", 3, 4),
         ("add", 4, 2), ("sub", 2, 4), ("add", 2, 3)]
TEN = TWO + THREE
PERMUTATION = (1, 0, 3, 4, 2, 5)


def exact_checks():
    target = tuple(identity(6)[i] for i in PERMUTATION)
    require(execute(TEN, 6) == target, "ten-word exact endpoint")
    require(execute(TEN + inverse(TEN), 6) == identity(6), "ten-word literal inverse")
    for i in range(10):
        require(execute(TEN[:i] + TEN[i+1:], 6) != target, "undetected omitted gate")
    for n in (5, 7, 13, 54):
        expected = tuple(identity(n)[i] for i in (1, 0, 3, 4, 2, *range(5, n)))
        require(execute(TEN, n) == expected, "dirty-donor extension")
    disposable = [("copy", 5, 0), ("copy", 0, 1), ("copy", 1, 5),
                  ("copy", 5, 2), ("copy", 2, 3), ("copy", 3, 4),
                  ("copy", 4, 5), ("clear", 5, None)]
    result = execute(disposable, 6)
    require(result[:5] == target[:5] and result[5] != target[5], "disposable/restored distinction")
    contaminated = execute([("add", 0, 5)] + TEN, 6)
    require(contaminated != target, "read-only donor is not freely zero")
    require(tuple(row[:5] for row in contaminated) == tuple(row[:5] for row in target),
            "read-only specialization")
    require((9 - 5)//2 == 2 and (9 - (5 + 2))//2 == 1, "donor bound improvement")
    for a in range(-7, 8):
        for depth in range(6):
            q = F(a, 2**depth)
            require(q.numerator * pow(q.denominator, -1, 3) % 3 == a * pow(2, depth, 3) % 3,
                    "dyadic reduction")
    for denominator, modulus in ((2, 2), (3, 3)):
        try:
            pow(denominator, -1, modulus)
        except ValueError:
            pass
        else:
            raise ValueError("nonunit denominator accepted")
    return {"exact_minimum": 10, "witness_length": 10, "omission_controls": 10,
            "donor_extensions": [0, 1, 2, 8, 49], "disposable_control_length": 8,
            "write_bound_at_nine": {"moved": 5, "cycles": 2, "written_donors_at_most": 1}}


def dense_group(n):
    """Third representation: dense coefficient tuples, complete GL(n,3) BFS."""
    start = identity(n)
    distance, queue = {start: 0}, deque([start])
    while queue:
        state = queue.popleft()
        for t in range(n):
            rows = list(state)
            rows[t] = tuple(-x % 3 for x in state[t])
            candidates = [tuple(rows)]
            for s in range(n):
                if s != t:
                    for sign in (-1, 1):
                        rows[t] = tuple((a+sign*b) % 3 for a, b in zip(state[t], state[s]))
                        candidates.append(tuple(rows))
            for new in candidates:
                if new not in distance:
                    distance[new] = distance[state] + 1
                    queue.append(new)
    return distance


def ball_records(distance):
    records = []
    for state, depth in distance.items():
        if depth > 4:
            continue
        key, place = 0, 1
        for row in state:
            for value in row:
                key += value*place
                place *= 3
        records.append((key, depth))
    return b"".join(struct.pack("<QB", key, depth) for key, depth in sorted(records))


def compile_engines(directory):
    compiler = shutil.which("c++")
    require(compiler is not None, "C++17 compiler required; see native workflow")
    engines = []
    for name in ("ternary", "packed"):
        executable = directory / name
        subprocess.run([compiler, "-std=c++17", "-O3", str(HERE / (name + ".cpp")), "-o", str(executable)],
                       check=True, timeout=60)
        engines.append(executable)
    return engines


def native_case(engines, directory, n, permutation):
    outputs = []
    for executable in engines:
        stem = executable.name + "-" + str(n) + "-" + permutation
        ball, report = directory / (stem + ".bin"), directory / (stem + ".json")
        subprocess.run([str(executable), str(n), permutation, str(ball), str(report)],
                       check=True, timeout=180, stdout=subprocess.PIPE)
        outputs.append((ball.read_bytes(), read(report)))
    require(outputs[0] == outputs[1], "native full matrix/distance or report disagreement")
    require(len(outputs[0][0]) == 9*outputs[0][1]["states"], "binary receipt size")
    return outputs[0]


def native_checks(directory):
    engines = compile_engines(directory)
    small = []
    for n in (2, 3):
        oracle = dense_group(n)
        require(len(oracle) == (48 if n == 2 else 11232), "GL order")
        expected_ball = ball_records(oracle)
        for permutation in itertools.permutations(range(n)):
            text = "".join(map(str, permutation))
            ball, report = native_case(engines, directory, n, text)
            require(ball == expected_ball, "full dense ball disagreement")
            target = tuple(identity(n)[i] for i in permutation)
            require(report["minimum_through_nine"] == oracle[target], "dense shortest-distance disagreement")
            small.append({"permutation": text, "minimum": oracle[target], "states": len(oracle)})
    for executable in engines:
        for n, p in ((1, "0"), (7, "0123456"), (3, "001"), (3, "01"), (3, "019")):
            response = subprocess.run([str(executable), str(n), p, str(directory/"bad.bin"), str(directory/"bad.json")],
                                      capture_output=True, timeout=10)
            require(response.returncode != 0, "invalid native interface accepted")
    # This is reachable in nine but not eight: omitting the middle-gate scan
    # would falsely reject it. Three signed adjacent swaps supply the upper word.
    nine = []
    for t, s in ((0, 1), (1, 2), (2, 3)):
        nine += [("add", t, s), ("sub", s, t), ("add", t, s)]
    signed_target = (identity(4)[1], identity(4)[2], identity(4)[3],
                     tuple(-x for x in identity(4)[0]))
    require(execute(nine, 4) == signed_target, "distance-nine rational positive witness")
    _, middle_control = native_case(engines, directory, 4, "123a")
    require(middle_control["direct_hits"] == 0 and middle_control["middle_hits"] > 0
            and middle_control["minimum_through_nine"] == 9, "essential middle-gate control")
    ball, target = native_case(engines, directory, 6, "103425")
    require(target == {"n": 6, "permutation": "103425", "layers": [1, 66, 2655, 83270, 2213925],
                       "states": 2299917, "generators": 66, "transitions": 151794522,
                       "direct_hits": 0, "middle_hits": 0, "minimum_through_nine": None}, "target census")
    target["canonical_ball_sha256"] = hashlib.sha256(ball).hexdigest()
    return {"target": target, "dense_controls": small, "distance_nine_control": middle_control,
            "invalid_native_inputs_rejected": 10}


def recognize(events, start, end):
    """Exact 2x2 recognition, adapted from Ross Richardson's PR1216."""
    if start + 4 > end:
        return None
    block = events[start:start+4]
    if any(event[0] != "scalar" for event in block):
        return None
    ops = [event[1] for event in block]
    if [op[0] for op in ops] != ["add", "add", "add", "scale"]:
        return None
    a, b = tuple(ops[0][1]), tuple(ops[0][2])
    if a == b or a[0] != "L" or b[0] != "L":
        return None
    rows = {a: [F(1), F(0)], b: [F(0), F(1)]}
    for op in ops:
        target = tuple(op[1])
        if target not in rows:
            return None
        if op[0] == "add":
            source = tuple(op[2])
            if source not in rows or source == target:
                return None
            rows[target] = [x + F(*op[3:5])*y for x, y in zip(rows[target], rows[source])]
        else:
            rows[target] = [F(*op[2:4])*x for x in rows[target]]
    return (a, b) if rows[a] == [0, 1] and rows[b] == [1, 0] else None


def cycles_of(mapping):
    pending = {a for a, b in mapping.items() if a != b}
    result = []
    while pending:
        first = min(pending)
        cycle, cursor = [first], mapping[first]
        while cursor != first:
            require(cursor in pending and cursor not in cycle, "invalid cycle")
            cycle.append(cursor)
            cursor = mapping[cursor]
        pending.difference_update(cycle)
        result.append(cycle)
    return result


def boundary_census(events):
    result, cursor = [], 0
    while cursor < len(events):
        if events[cursor][0] != "scalar":
            cursor += 1
            continue
        start, frame = cursor, events[cursor][2]
        while cursor < len(events) and events[cursor][0] == "scalar" and events[cursor][2] == frame:
            cursor += 1
        end, position, starts, mapping = cursor, start, [], {}
        while position < end:
            pair = recognize(events, position, end)
            if pair is None:
                position += 1
                continue
            a, b = pair
            mapping.setdefault(a, a)
            mapping.setdefault(b, b)
            mapping[a], mapping[b] = mapping[b], mapping[a]
            starts.append(position)
            position += 4
        if starts:
            result.append({"start": start, "end": end, "frame": frame, "swap_starts": starts,
                           "permutation": [[list(a), list(b)] for a, b in sorted(mapping.items())],
                           "cycles": [[list(a) for a in cycle] for cycle in cycles_of(mapping)]})
    return result


def invoice():
    prior, result = read(ROOT / PREVIOUS), {}
    for provider in ("ck", "jp8"):
        programs = read(ROOT / (PROVIDERS + provider + "/LOCAL-PROGRAMS.json.gz"))
        checks = read(ROOT / (PROVIDERS + provider + "/LOCAL-CHECKS.json"))
        for direction in ("forward", "backward"):
            key, events = provider + "/" + direction, programs[direction]
            require(hashlib.sha256(canonical(events)).hexdigest() == checks[direction]["sha256"], "event source digest")
            blocks = boundary_census(events)
            require(blocks == prior["candidate_blocks"][key], "complete historical boundary census")
            types = Counter(tuple(sorted(map(len, block["cycles"]))) for block in blocks)
            require(types == {(2,): 28, (2, 3): 14}, "historical cycle profile")
            result[key] = {"boundaries": len(blocks), "two_cycles": 28, "two_plus_three_cycles": 14,
                           "disposable_component_cost": 224, "restored_component_minimum": 252,
                           "separate_complex_components_extra": 56,
                           "census_sha256": hashlib.sha256(canonical(blocks)).hexdigest()}
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--record", type=Path)
    ap.add_argument("--quick", action="store_true", help="no native lower-bound replay")
    args = ap.parse_args()
    pins()
    result = {"format": "restored-cycle-gap-v1", "exact": exact_checks(), "historical_invoice": invoice()}
    if args.quick:
        print("PASS_RESTORED_CYCLE_QUICK exact_upper=10 historical_boundaries=168 full_lower_bound_not_replayed")
        return
    with tempfile.TemporaryDirectory(prefix="restored-cycle-gap-") as directory:
        result["finite_exclusion"] = native_checks(Path(directory))
    if args.record:
        with args.record.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == read(HERE / "EXPECTED.json"), "receipt drift")
    print("PASS_RESTORED_CYCLE_GAP exact_minimum=10 arbitrary_dirty_donors states=2299917 middle_tests=151794522 historical_component_bill=252 no_new_kappa")


if __name__ == "__main__":
    main()
