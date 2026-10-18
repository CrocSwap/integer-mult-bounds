"""Exact endpoint-run rewriting and logical replay; no predecessor executable imports."""

from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import copy
import hashlib
import json
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def same_json(a, b):
    # Preserve JSON scalar types, unlike Python's True == 1 == 1.0.
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def authenticate():
    for item in read_json(PACKAGE / "SOURCES.json")["files"]:
        if item["usage"] == "input":
            check_bytes(ROOT / item["path"], item)
    for item in read_json(PACKAGE / "PREDECESSORS.json")["files"]:
        check_bytes(PACKAGE / item["local"], item)


def check_bytes(path, item):
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == item["sha256"], "source SHA256 " + str(path))
    header = b"blob " + str(len(raw)).encode() + b"\0"
    require(hashlib.sha1(header + raw).hexdigest() == item["git_blob"], "source Git blob")
    return raw


def native_module(filename):
    path = ROOT / "research/p104-native-channel/vendor" / filename
    pin = next(x for x in read_json(PACKAGE / "SOURCES.json")["files"]
               if x["path"] == str(path.relative_to(ROOT)))
    raw = check_bytes(path, pin)
    module = types.ModuleType(filename[:-3])
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def basis(vectors):
    pivots = {}
    for value in vectors:
        require(type(value) is int and 0 < value < 512, "binary vector")
        while value:
            p = value.bit_length() - 1
            if p in pivots:
                value ^= pivots[p]
            else:
                pivots[p] = value
                break
    for p in sorted(pivots):
        for q in pivots:
            if q > p and (pivots[q] >> p) & 1:
                pivots[q] ^= pivots[p]
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def touches(event, role):
    return event[1] == role or (event[0] == "add" and event[2] == role)


def endpoint_runs(word):
    """Enumerate all 416 maximal endpoint runs; ADD reads are barriers too."""
    program = word["program"]
    result = []
    for side in ("entry", "exit"):
        for group in ("X", "Y"):
            for number in range(104):
                role = group + str(number)
                indices = [i for i, e in enumerate(program) if touches(e, role)]
                if side == "exit":
                    indices.reverse()
                transports, signs, barrier = [], [], None
                for i in indices:
                    event = program[i]
                    if event[0] == "transport":
                        transports.append(i)
                    elif event[0] == "sign":
                        signs.append(i)
                    else:
                        barrier = i
                        break
                require(transports and barrier is not None, "endpoint run has a barrier")
                endpoint = program[transports[0]]
                require(endpoint[4] == 1, "rank-one endpoint conversion")
                if side == "entry":
                    require(endpoint[2] == word["initial_frames"][role], "entry boundary")
                else:
                    require(endpoint[3] == word["final_frames"][role], "exit boundary")
                result.append(dict(side=side, role=role, transports=sorted(transports),
                                   signs=sorted(signs), barrier=barrier))
    return result


def fuse(word):
    runs = endpoint_runs(word)
    removed, replacement = set(), {}
    pairs = []
    for run in runs:
        ids = run["transports"]
        require(len(ids) in (1, 2), "fixed word has at most two endpoint-run transports")
        if len(ids) == 1:
            continue
        i, j = ids
        left, right = word["program"][i], word["program"][j]
        role = run["role"]
        require(left[3] == right[2], "transport telescope")
        require(basis(left[2] + right[3]) == basis(right[3]), "increasing fused run")
        rank = len(basis(right[3])) - len(basis(left[2]))
        require(rank == left[4] + right[4], "fused rank sum")
        for k in range(i + 1, j):
            e = word["program"][k]
            require(not touches(e, role) or e[0] == "sign", "no ADD/private barrier crossed")
            if touches(e, role):
                require(e[2] == "-1", "scalar sign")
                replacement[k] = ["sign", role, "-1", left[2]]
        require(i not in removed and j not in replacement, "disjoint fusion pairs")
        removed.add(i)
        replacement[j] = ["transport", role, left[2], right[3], rank]
        pairs.append(dict(role=role, side=run["side"], original_events=[i, j],
                          old=left[2], middle=left[3], new=right[3],
                          original_ranks=[left[4], right[4]], rank=rank))
    candidate = copy.deepcopy(word)
    candidate["program"] = [copy.deepcopy(replacement.get(i, e))
                            for i, e in enumerate(word["program"]) if i not in removed]
    position = {i: i - sum(j < i for j in removed) for i in range(len(word["program"]))
                if i not in removed}
    for pair in pairs:
        pair["candidate_event"] = position[pair["original_events"][1]]
    return candidate, runs, pairs


def ports():
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.append(tuple(row))
    roots.extend((1,) + row for row in product((-1, 1), repeat=7) if row.count(-1) % 2 == 0)
    fixture = read_json(ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json")
    excluded = {tuple(r) for r in fixture["section4_explicit_P104"]["F0"]
                + fixture["section4_explicit_P104"]["C"]}
    selected = sorted(set(roots) - excluded)
    require(len(set(roots)) == 120 and len(selected) == 104, "P104 root reconstruction")
    return selected


def replay(word):
    """Independent sparse Fraction replay of every original and changed event."""
    names = list(word["initial_frames"])
    require(len(names) == len(set(names)) == 358, "358 public inputs")
    frames = {r: basis(f) for r, f in word["initial_frames"].items()}
    rows = {r: {r: Fraction(1)} for r in names}
    counts, profile = Counter(), Counter()
    erasures = 0
    for i, event in enumerate(word["program"]):
        op, role = event[:2]
        counts[op] += 1
        if op == "transport":
            require(len(event) == 5, "transport schema")
            old, new, rank = basis(event[2]), basis(event[3]), event[4]
            require(frames[role] == old, "transport input frame at " + str(i))
            require(basis(old + new) in (old, new), "nested transport")
            require(type(rank) is int and rank == abs(len(old) - len(new)) > 0, "transport rank")
            frames[role] = new
            profile[rank] += 1
        elif op == "sign":
            require(event[2] == "-1" and frames[role] == basis(event[3]), "sign frame")
            rows[role] = {k: -v for k, v in rows[role].items()}
        elif op == "zero":
            require(role == "C" and role not in rows, "fresh private zero")
            rows[role], frames[role] = {}, basis(event[2])
        elif op == "erase":
            require(role == "C" and frames[role] == basis(event[2]), "private erase frame")
            require(not rows[role], "exact zero before private erase")
            del rows[role], frames[role]
            erasures += 1
        else:
            require(op == "add" and len(event) == 5, "ADD schema")
            _, target, source, scalar, frame = event
            require(target != source and frames[target] == frames[source] == basis(frame),
                    "ADD common frame at " + str(i))
            scalar = Fraction(scalar)
            for column, value in list(rows[source].items()):
                updated = rows[target].get(column, Fraction(0)) + scalar * value
                if updated:
                    rows[target][column] = updated
                else:
                    rows[target].pop(column, None)
    require(set(rows) == set(names), "public register set")
    require(frames == {r: basis(f) for r, f in word["final_frames"].items()}, "final frames")
    root = ports()
    for role in names:
        expected = {role: Fraction(1)}
        if role.startswith("X"):
            s = int(role[1:])
            for t in range(104):
                coefficient = (Fraction(int(t == s)) if t < 2 else
                               Fraction(sum(a * b for a, b in zip(root[s], root[t])), 8))
                if coefficient:
                    expected["Y" + str(t)] = -coefficient
        require(rows[role] == expected, "all-input boundary " + role)
    return dict(events=len(word["program"]), counts=dict(sorted(counts.items())),
                profile={str(k): v for k, v in sorted(profile.items())},
                rank_mass=sum(k * v for k, v in profile.items()),
                boundary_coefficients=len(names) ** 2, zero_erasures=erasures)


def conjugate(circuit):
    result = []
    for gate in circuit:
        if gate[0] == "C":
            result.append(("C", gate[1], -gate[2]))
        elif gate[0] == "D":
            result.append(("D", tuple(gate[1]), tuple(-x % 4 for x in gate[2])))
        elif gate[0] == "phase":
            result.append(("phase", -gate[1] % 4))
        else:
            require(gate[0] in ("P", "X"), "native conjugation alphabet")
            result.append(tuple(gate))
    return tuple(result)


def edge_key(old, new):
    return tuple(old), tuple(new)


def native_edges(pairs):
    edges = {}
    for pair in pairs:
        edges.setdefault(edge_key(pair["old"], pair["new"]), []).append(pair["candidate_event"])
    return edges


def write_json_new(path, value):
    with open(path, "x") as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n")
