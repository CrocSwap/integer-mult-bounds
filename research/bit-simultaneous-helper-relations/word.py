"""Interpret the pinned binary word and count the selected paired caller."""
from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = "research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz"
CALLER = "research/paired-query-only-bit/EFREE-CALLER.json.gz"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source(path):
    pins = json.loads((HERE / "SOURCES.json").read_bytes())["files"]
    pin, = [item for item in pins if item["path"] == path and item["usage"] == "input"]
    raw = (ROOT / path).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == pin["sha256"], "pinned source digest")
    return json.loads(gzip.decompress(raw))


def independent_rows(rows):
    """Full row rank over Q by fraction-free elimination on the eight axes."""
    pivots = {}
    for source_row in rows:
        row = list(source_row)
        for j in range(8):
            if row[j] == 0:
                continue
            if j not in pivots:
                pivots[j] = row
                break
            other = pivots[j]
            left, right = other[j], row[j]
            row = [left * a - right * b for a, b in zip(row, other, strict=True)]
        else:
            return False
    return True


def check_frames(word):
    frames = {int(c): frame for c, frame in word["frames"].items()}

    def orthogonal(left, right):
        return all(sum(a * b for a, b in zip(u, v, strict=True)) == 0 for u in left for v in right)

    for frame in frames.values():
        a, b, dim = frame["A"], frame["B"], frame["dim"]
        require(len(b) == dim and len(a) + dim == 8 and all(len(row) == 8 for row in a + b),
                "eight-axis frame dimensions")
        require(independent_rows(a) and independent_rows(b) and orthogonal(a, b), "rational frame bases")
    paid = {(e[2], e[3]) for e in word["program"] if e[0] == "MOVE"}
    helpers = set(zip(word["start"][222:], word["final"][222:], strict=True))
    for a, b in paid | helpers:
        small, large = sorted((frames[a], frames[b]), key=lambda f: f["dim"])
        require(small["dim"] < large["dim"] and orthogonal(small["B"], large["A"]), "nested rank price")
    return {"rational_frames": len(frames), "directed_paid_pairs": len(paid),
            "ordered_helper_boundaries": len(helpers)}


@dataclass(frozen=True)
class Bank:
    clock: int
    signal: int
    rank: int


def replay(word, transpose):
    """Banks are in chronological order, after all free entrance fields."""
    n = word["public"]
    ingress, egress = word["start"], word["final"]
    program = word["program"]
    if transpose:
        ingress, egress = egress, ingress
        program = reversed(program)
    frames = {int(c): data["dim"] for c, data in word["frames"].items()}
    charts = list(ingress) + [None] * word["owned_fields"]
    values = [1 << r for r in range(n)] + [0] * word["owned_fields"]
    banks = defaultdict(list)
    for role, chart in enumerate(ingress):
        banks[chart].append(Bank(~role, values[role], 0))

    for clock, (op, a, *tail) in enumerate(program):
        if transpose and op in ("INIT", "CLEAR"):
            op = {"INIT": "CLEAR", "CLEAR": "INIT"}[op]
        if op == "INIT":
            chart, = tail
            require(a >= n and charts[a] is None, "owned introduction")
            charts[a], values[a] = chart, 0
        elif op == "CLEAR":
            chart, = tail
            require(a >= n and charts[a] == chart, "owned retirement")
            charts[a], values[a] = None, 0
        elif op == "SWAP":
            b, = tail
            charts[a], charts[b] = charts[b], charts[a]
            values[a], values[b] = values[b], values[a]
        elif op == "ADD":
            b, chart = tail
            require(a != b and charts[a] == charts[b] == chart, "scalar XOR contact")
            dst, src = (b, a) if transpose else (a, b)
            values[dst] ^= values[src]
        else:
            require(op == "MOVE", "known operation")
            old, new = reversed(tail) if transpose else tail
            rank = abs(frames[old] - frames[new])
            require(charts[a] == old and rank > 0, "paid transfer direction")
            charts[a] = new
            banks[new].append(Bank(clock, values[a], rank))

    require(charts == list(egress) + [None] * word["owned_fields"], "public charts")
    for role, actual in enumerate(values[:n]):
        expected = 1 << role
        if transpose and role < 111:
            expected ^= 1 << (role + 111)
        if not transpose and 111 <= role < 222:
            expected ^= 1 << (role - 111)
        require(actual == expected, "arbitrary public input and helper endpoint")

    groups = defaultdict(list)
    for role in range(222, n):
        groups[ingress[role], egress[role]].append(role)
    keys = sorted(groups, key=lambda pair: (-len(groups[pair]), pair))
    return dict(banks), {pair: groups[pair] for pair in keys}, frames


def invoice(caller, banks, groups, frames):
    native = Counter(row.rank for bank in banks.values() for row in bank if row.rank)
    helper = Counter()
    for (a, d), roles in groups.items():
        helper[abs(frames[a] - frames[d])] += len(roles)
    ports = caller["ports"]
    calls = Counter(event[1] for event in caller["events"] if event[0] == "LOCAL")
    require(ports == 111 and caller["stages"] == 18 and
            calls == Counter({s: 2 for s in range(1, 19)}), "paired caller stages")
    uses = sum(calls.values())
    paid = Counter({r: uses * count for r, count in native.items()})
    targets = Counter({r: uses * count for r, count in helper.items()})
    for event in caller["events"]:
        if event[0] == "QUERY":
            paid[1] += ports
        if event[0] == "IDLE_ONE":
            paid[7 * len(event[2])] += ports
    for job in caller["diagonal"]:
        stages = job["stages"]
        require(job["q"] == 1 and stages and len(set(stages)) == len(stages), "positive root job")
        targets[1 + 7 * len(stages)] += ports
    require((sum(paid.values()), sum(targets.values())) == (107352, 19950), "whole caller counts")
    return {"native_invocations": uses, "native_paid": sum(native.values()),
            "native_helpers": sum(helper.values()), "paid": dict(sorted(paid.items())),
            "targets": dict(sorted(targets.items())),
            "rank_surplus": sum(r * n for r, n in targets.items())
                            - sum(r * n for r, n in paid.items())}
