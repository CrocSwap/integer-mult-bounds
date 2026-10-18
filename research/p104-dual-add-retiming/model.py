"""One source-bound two-operand retiming; exact finite canonical Delta charts."""
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import copy
import hashlib
import json
import types

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
FULL = (256, 128, 64, 32, 16, 8, 4, 2, 1)
COMMON = (258, 130, 64, 32, 16, 10, 6, 1)
REMOVED = (3897, 4643, 4645, 5152)
ADD, SIGN = 4644, 5048
EDGES = (("X90", (400, 80), FULL, 7), ("N90", (391,), FULL, 8))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            need(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def check_bytes(path, pin):
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source SHA256: " + str(path))
    need(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
         == pin["git_blob"], "source Git blob: " + str(path))
    return raw


def authenticate():
    for pin in read(P / "SOURCES.json")["files"]:
        if pin["usage"] == "input":
            check_bytes(ROOT / pin["path"], pin)
    for pin in read(P / "PREDECESSORS.json")["files"]:
        check_bytes(P / pin["local"], pin)


def native_module(name):
    path = ROOT / "research/p104-native-channel/vendor" / name
    relative = path.relative_to(ROOT).as_posix()
    pin = next(p for p in read(P / "SOURCES.json")["files"] if p["path"] == relative)
    raw = check_bytes(path, pin)
    module = types.ModuleType(name[:-3])
    module.__file__ = str(path)
    # Execute authenticated source bytes, never a timestamp .pyc.
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def basis(vectors):
    pivots = {}
    for value in vectors:
        need(type(value) is int and 0 < value < 512, "binary frame vector")
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    for bit in sorted(pivots):
        for other in pivots:
            if other > bit and (pivots[other] >> bit) & 1:
                pivots[other] ^= pivots[bit]
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


def touches(event, role):
    return event[1] == role or (event[0] == "add" and event[2] == role)


def rewrite(source):
    events = source["program"]
    need(len(events) == 5270, "source word length")
    expected = {
        3897: ["transport", "X90", [400, 80], list(COMMON), 6],
        4643: ["transport", "N90", [391], list(COMMON), 7],
        4644: ["add", "X90", "N90", "1/2", list(COMMON)],
        4645: ["transport", "N90", list(COMMON), list(FULL), 1],
        5048: ["sign", "X90", "-1", list(COMMON)],
        5152: ["transport", "X90", list(COMMON), list(FULL), 1],
    }
    for i, event in expected.items():
        need(events[i] == event, "source event binding: " + str(i))
    for role, start, end, allowed in (
        ("X90", 3897, 5152, {4644, 5048}),
        ("N90", 4643, 4645, {4644}),
    ):
        actual = {i for i in range(start + 1, end) if touches(events[i], role)}
        need(actual == allowed, "retiming dependency window: " + role)
    candidate = copy.deepcopy(source)
    out = []
    for i, event in enumerate(events):
        if i in REMOVED:
            continue
        if i == ADD:
            out.extend(["transport", role, list(old), list(new), rank]
                       for role, old, new, rank in EDGES)
            event = event[:4] + [list(FULL)]
        elif i == SIGN:
            event = event[:3] + [list(FULL)]
        out.append(copy.deepcopy(event))
    candidate["program"] = out
    return candidate


def root_ports():
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.append(tuple(row))
    roots += [(1,) + row for row in product((-1, 1), repeat=7) if row.count(-1) % 2 == 0]
    fixture = read(ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json")
    cut = fixture["section4_explicit_P104"]
    excluded = {tuple(row) for row in cut["F0"] + cut["C"]}
    ports = sorted(set(roots) - excluded)
    need(len(set(roots)) == 120 and len(ports) == 104, "root port count")
    return ports


def replay(word):
    names = list(word["initial_frames"])
    need(len(names) == 358, "public input count")
    frames = {r: basis(f) for r, f in word["initial_frames"].items()}
    rows = {r: {r: Fraction(1)} for r in names}
    counts, profile = Counter(), Counter()
    erased = 0
    for i, event in enumerate(word["program"]):
        op, role = event[:2]
        counts[op] += 1
        if op == "transport":
            old, new, rank = basis(event[2]), basis(event[3]), event[4]
            need(frames[role] == old, "transport input frame: " + str(i))
            need(basis(old + new) in (old, new), "nested transport")
            need(type(rank) is int and rank == abs(len(new) - len(old)) > 0, "transport rank")
            frames[role] = new
            profile[rank] += 1
        elif op == "add":
            _, role, source, coefficient, frame = event
            need(role != source and frames[role] == frames[source] == basis(frame),
                 "ADD common frame: " + str(i))
            coefficient = Fraction(coefficient)
            for key, value in rows[source].items():
                new = rows[role].get(key, 0) + coefficient * value
                if new:
                    rows[role][key] = new
                else:
                    rows[role].pop(key, None)
        elif op == "sign":
            need(event[2] == "-1" and frames[role] == basis(event[3]), "sign frame")
            rows[role] = {key: -value for key, value in rows[role].items()}
        elif op == "zero":
            need(role == "C" and role not in rows, "fresh private allocation")
            rows[role], frames[role] = {}, basis(event[2])
        elif op == "erase":
            need(role == "C" and frames[role] == basis(event[2]), "private erase frame")
            need(not rows[role], "exact private zero erasure")
            del rows[role], frames[role]
            erased += 1
        else:
            raise ValueError("unknown instruction")
    need(set(rows) == set(names), "public endpoint roles")
    need(frames == {r: basis(f) for r, f in word["final_frames"].items()}, "final frames")
    ports = root_ports()
    for role in names:
        want = {role: Fraction(1)}
        if role.startswith("X"):
            s = int(role[1:])
            for t, root in enumerate(ports):
                coefficient = (Fraction(int(t == s)) if t < 2 else
                               Fraction(sum(x*y for x, y in zip(root, ports[s])), 8))
                if coefficient:
                    want["Y" + str(t)] = -coefficient
        need(rows[role] == want, "all-input endpoint: " + role)
    endpoint = {r: {s: str(v) for s, v in row.items()} for r, row in rows.items()}
    return dict(events=len(word["program"]), counts=dict(sorted(counts.items())),
                profile={str(k): v for k, v in sorted(profile.items())},
                rank_mass=sum(k*v for k, v in profile.items()),
                boundary_coefficients=len(names)**2, zero_erasures=erased,
                endpoint_sha256=hashlib.sha256(encoded(endpoint).encode()).hexdigest())


def conjugate(gates):
    out = []
    for gate in gates:
        if gate[0] == "C":
            out.append(("C", gate[1], -gate[2]))
        elif gate[0] == "D":
            out.append(("D", tuple(gate[1]), tuple(-x % 4 for x in gate[2])))
        elif gate[0] == "phase":
            out.append(("phase", -gate[1] % 4))
        else:
            need(gate[0] in ("P", "X"), "conjugation gate")
            out.append(tuple(gate))
    return tuple(out)


def write_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")
