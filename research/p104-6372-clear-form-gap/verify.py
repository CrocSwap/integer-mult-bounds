#!/usr/bin/env python3
"""Forward-CLEAR form gap on the frozen PR6372 candidate word.

Literal sparse rational projection only. MOVE does not change coefficients.
No predecessor checker, native engine or oracle is imported.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLIC, OWNED = 770, 29
FILES = {
    "inputs/candidate-WORD.json.gz": (
        "e3b6f1c25d672b8c85433be97ebad77ae6a6972352ce2ff63507d30835fcb491",
        "0af79e58172f85c302c35b193205c0b185b09393",
    ),
    "inputs/source-WORD.json.gz": (
        "0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928",
        "03ea7690285d4cda72815f962d5710ab96e08490",
    ),
}
# f is role 779 at CLEAR 17756; g is role 780 at CLEAR 17755.
# These hashes use the same canonical row encoding as PR6376's endpoint receipt.
ROW_SHA = {
    779: "02ce1aeb475900c8075ad512ad444960a7766f940f489825a56374a3c3d85f39",
    780: "b949deff3f5c36b3465df10cbb1e38c0731284f0c0a72897fcacac5f54e83193",
}
DIFFERENCE = {27: 2, 57: -2, 87: 2, 92: -2, 228: 2, 230: 2, 232: -2, 234: -2}
ALLOWED = {Fraction(1), Fraction(-1), Fraction(2), Fraction(-2), Fraction(4)}


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return sha256((canonical(value) + "\n").encode()).hexdigest()


def encoded(row):
    return [[coordinate, str(value)] for coordinate, value in sorted(row.items())]


def load_words():
    words = {}
    for name, (expected_sha, expected_blob) in FILES.items():
        raw = (HERE / name).read_bytes()
        require(sha256(raw).hexdigest() == expected_sha, "SHA256 mismatch: " + name)
        blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == expected_blob, "Git blob mismatch: " + name)
        words[name] = json.loads(gzip.decompress(raw))
    return words


def rational(value):
    require(type(value) is str, "coefficient must be a canonical string")
    result = Fraction(value)
    require(result != 0 and str(result) == value, "coefficient is not a canonical nonzero rational")
    require(result.denominator & (result.denominator - 1) == 0, "coefficient is not dyadic")
    return result


def plus(destination, source, coefficient):
    result = dict(destination)
    for coordinate, value in source.items():
        updated = result.get(coordinate, 0) + coefficient * value
        if updated:
            result[coordinate] = updated
        else:
            result.pop(coordinate, None)
    return result


def forward(word):
    require(word.get("public") == PUBLIC and word.get("owned_fields") == OWNED,
            "word is not the 770-public / 29-owned interface")
    frames = word["frames"]
    require(type(frames) is list and len(frames) == 1095, "frame inventory is not 1095 labels")
    require(len(word["initial"]) == len(word["final"]) == PUBLIC, "public frame boundary is incomplete")
    rows = [{role: Fraction(1)} if role < PUBLIC else {} for role in range(PUBLIC + OWNED)]
    current = dict(enumerate(word["initial"]))
    lifetime = {}
    clears = []
    initialized = 0
    for index, event in enumerate(word["program"]):
        require(type(event) is list and event, "event is not a literal list")
        op, role = event[0], event[1]
        require(type(role) is int and 0 <= role < PUBLIC + OWNED, "role out of range")
        if op == "MOVE":
            require(len(event) == 5, "MOVE arity")
            start, end, private = event[2], event[3], event[4]
            require(current.get(role) == start and type(private) is bool and private == (role >= PUBLIC),
                    "MOVE chronology")
            current[role] = end
        elif op == "INIT":
            require(len(event) == 3 and role >= PUBLIC and role not in current, "INIT lifetime")
            rows[role] = {}
            current[role] = event[2]
            lifetime[role] = (initialized, index)
            initialized += 1
        elif op == "CLEAR":
            require(len(event) == 3 and role in lifetime and current.get(role) == event[2], "CLEAR lifetime")
            sequence, birth = lifetime.pop(role)
            row = dict(rows[role])
            clears.append({
                "role": role,
                "lifetime": sequence + 1,
                "init_index": birth,
                "clear_index": index,
                "frame": event[2],
                "row": row,
            })
            rows[role] = {}
            del current[role]
        elif op == "SCALE":
            require(len(event) == 4 and current.get(role) == event[3], "SCALE frame")
            coefficient = rational(event[2])
            rows[role] = {coordinate: coefficient * value for coordinate, value in rows[role].items()}
        elif op in ("ADD", "COPY"):
            require(len(event) == 5, "scalar arity")
            source, coefficient, frame = event[2], rational(event[3]), event[4]
            require(source != role and current.get(role) == current.get(source) == frame,
                    "scalar operands are not co-active")
            if op == "COPY":
                require(role >= PUBLIC and role in lifetime and not rows[role], "COPY destination")
                rows[role] = {coordinate: coefficient * value for coordinate, value in rows[source].items()}
            else:
                rows[role] = plus(rows[role], rows[source], coefficient)
        else:
            require(False, "unknown opcode")
    require(not lifetime, "an owned lifetime is still open at exit")
    return clears


def moves(word):
    return Counter(tuple(event) for event in word["program"] if event[0] == "MOVE")


def frame_dimension(frames, label):
    space = {0}
    for vector in frames[label]:
        require(type(vector) is int and 1 <= vector < 512, "frame basis vector")
        require(vector not in space, "frame basis is linearly dependent")
        space |= {point ^ vector for point in tuple(space)}
    size = len(space)
    require(size & (size - 1) == 0, "frame span is not a coordinate subspace")
    return size.bit_length() - 1


def sparse_difference(left, right):
    result = {}
    for coordinate in set(left) | set(right):
        value = left.get(coordinate, 0) - right.get(coordinate, 0)
        if value:
            result[coordinate] = value
    return result


def main():
    words = load_words()
    candidate = words["inputs/candidate-WORD.json.gz"]
    source = words["inputs/source-WORD.json.gz"]
    removed = moves(source) - moves(candidate)
    added = moves(candidate) - moves(source)
    require(removed == Counter({("MOVE", role, 1091, 127, False): 1 for role in (224, 227)}),
            "source-only MOVE records are not the two 1091→127 helper transports")
    require(added == Counter({("MOVE", role, 1091, 245, False): 1 for role in (224, 227)}),
            "candidate-only MOVE records are not the two 1091→245 helper transports")
    dimensions = {label: frame_dimension(candidate["frames"], label) for label in (3, 1091, 245, 127)}
    require(dimensions == {3: 0, 1091: 4, 245: 8, 127: 9}, "changed-frame dimensions")
    for label in dimensions:
        require(candidate["frames"][label] == source["frames"][label], "frame basis changed")
    paid, productive = Counter(), Counter()
    for records, sign in ((added, 1), (removed, -1)):
        for event, count in records.items():
            paid[abs(dimensions[event[3]] - dimensions[event[2]])] += sign * count
    for role in (224, 227):
        require(source["final"][role] == 127 and candidate["final"][role] == 245, "helper final frame")
        productive[dimensions[candidate["final"][role]] - dimensions[3]] += 1
        productive[dimensions[source["final"][role]] - dimensions[3]] -= 1
    require(dict(paid) == {4: 2, 5: -2} and dict(productive) == {8: 2, 9: -2},
            "local declared-tariff delta is not 2H4-2H5 paid and 2H8-2H9 productive")

    found = {(row["role"], row["init_index"], row["clear_index"], row["frame"]): row
             for row in forward(candidate)}
    tails = {}
    for role, init_index, clear_index in ((779, 12998, 17756), (780, 12999, 17755)):
        key = (role, init_index, clear_index, 127)
        require(key in found, "missing added forward CLEAR " + str(key))
        tails[role] = found[key]["row"]
        require(digest(encoded(tails[role])) == ROW_SHA[role], "CLEAR row hash drifted for role " + str(role))
        require(set(tails[role].values()) <= ALLOWED, "unexpected CLEAR coefficient")
        require(len(tails[role]) == 97, "CLEAR support is not 97")
    source_tail = [row for row in forward(source)
                   if row["role"] in (779, 780) and row["clear_index"] in (17755, 17756)]
    require(source_tail == [], "the source word already has these tail CLEAR indices")

    left, right = tails[779], tails[780]
    difference = sparse_difference(left, right)
    require(difference == {key: Fraction(value) for key, value in DIFFERENCE.items()},
            "f-g is not the stated eight-term form")
    shared = set(left) & set(right)
    require(len(shared) == 93 and all(left[key] == right[key] for key in shared),
            "the two forms do not agree off the eight-term difference")
    mutant = dict(left)
    mutant[2] = mutant.get(2, 0) + 1
    require(sparse_difference(mutant, right) != difference, "mutant control did not change the difference")
    print("PASS_P104_6372_CLEAR_FORM_GAP support=97 difference=8 "
          "paid=2H4-2H5 productive=2H8-2H9")


if __name__ == "__main__":
    main()
