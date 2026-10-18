"""Exact inputs and independent nine-stage replay. This does not compile C++.

Gareth Davidson with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from collections import Counter
import gzip
import hashlib
import json
import math
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HUB = Path("research/e8-bit-carrier-skeleton")


def need(value, message):
    if not value:
        raise ValueError(message)


def pairs(items):
    out = {}
    for key, value in items:
        need(key not in out, "duplicate JSON key")
        out[key] = value
    return out


def reject(value):
    raise ValueError("nonfinite JSON: " + value)


def read(path):
    return json.loads(Path(path).read_bytes(), object_pairs_hook=pairs, parse_constant=reject)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_pins(root=ROOT, package=HERE):
    rows = [x for x in read(package / "SOURCES.json")["files"] if x["usage"] == "input"]
    need({x["path"] for x in rows} == {str(HUB / x) for x in
         ("code/bit/checkers/columns_k.cpp", "code/bit/checkers/json.hpp", "NOTICE.md")},
         "exact native source inventory")
    for row in rows:
        need(sha((root / row["path"]).read_bytes()) == row["sha256"], "source hash: " + row["path"])
    return rows


def fixtures(package=HERE):
    meta = read(package / "FIXTURES.json")
    need(meta["head"] == "b52f87f5355ad9f02ca4ac4395117655ac1b19c7", "fixture predecessor")
    need(set(meta["inputs"]) == {"baseline", "deferred", "missing-undo"}, "fixture inventory")
    out = {}
    for label, item in meta["inputs"].items():
        path = Path(item["path"])
        need(path.parts == ("fixtures", label + ".bin.gz"), "fixture path")
        container = (package / path).read_bytes()
        need(sha(container) == item["container_sha256"], "immutable fixture container")
        raw = gzip.decompress(container)
        need(sha(raw) == item["payload_sha256"] and len(raw) == 24 * item["records"], "fixture payload")
        out[label] = raw
    return out


def normalize(receipt, raw_path, raw):
    """Bind the sole location field before replacing it by the consumed byte hash."""
    out = dict(receipt)
    need(out.get("local_scalar_stream") == str(raw_path), "native input path binding")
    elapsed = out.pop("seconds", None)
    need(type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= 0, "native elapsed field")
    out["local_scalar_stream"] = "sha256:" + sha(raw)
    return out


def independent(raw):
    """All dirty columns as Python integer bitsets; literal fixed nine-stage schedule."""
    records = list(struct.iter_unpack("<6i", raw))
    operations = [q for q in records if q[0] != 0]
    need(all(q[0] in (0, 1, 2, 3) for q in records), "raw opcode")
    hist = Counter(q[4] for q in records if q[0] == 0 and q[4])
    hist.update(q[5] for q in operations if q[0] == 2)
    local, v, dirt, total = 661, 111, 439, 1327
    adds = sum(q[0] == 1 for q in operations)
    odd = sum(q[0] == 1 and q[3] % 2 for q in operations)
    copies = sum(q[0] == 2 for q in operations)
    need(copies == sum(q[0] == 3 for q in operations) == 9, "local copy count")
    maxima = []
    for reverse in (False, True):
        norms = [1] * (local + 1)
        maximum, opened = 1, False
        for op, a, b, c, _, _ in (reversed(operations) if reverse else operations):
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                norms[a] += abs(c) * norms[b]
                maximum = max(maximum, norms[a])
            elif op == 2:
                need(not opened, "fresh prefix copy")
                norms[local], opened = norms[a], True
            else:
                need(opened, "prefix erase")
                norms[local], opened = 0, False
        need(not opened, "prefix copy closed")
        maxima.append(maximum)
    # Independently spell the fixed 9-stage schedule, rather than generate it in C++.
    active = [(0, 1), (1, 0), (0, 1), (3, 2), (2, 3), (5, 4), (4, 5), (7, 6), (6, 7)]
    bridges = {1: [(0, 2), (3, 1)], 2: [(3, 1), (0, 2)],
               3: [(2, 4), (5, 3)], 4: [(5, 3), (2, 4)],
               5: [(4, 6), (7, 5)], 6: [(7, 5), (4, 6)],
               8: [(5, 7), (6, 4), (3, 5), (4, 2), (1, 3), (2, 0)]}
    state = [1 << i for i in range(total)] + [0]
    for stage, (left, right) in enumerate(active):
        reverse = stage % 2 == 1
        opened = False

        def loc(i):
            need(0 <= i <= local, "raw local index")
            if i < v:
                return left * v + i
            if i < 2 * v:
                return right * v + i - v
            return 8 * v + i - 2 * v

        for op, a, b, c, _, _ in (reversed(operations) if reverse else operations):
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                if c % 2:
                    state[loc(a)] ^= state[loc(b)]
            elif op == 2:
                need(not opened, "fresh physical copy")
                state[total], opened = state[loc(a)], True
            else:
                need(opened, "physical erase")
                state[total], opened = 0, False
        need(not opened, "stage copy closed")
        if stage == 0:
            need(state[:total] == [(1 << i) ^ ((1 << (i - v)) if v <= i < 2 * v else 0)
                                    for i in range(total)], "local defining full column")
        for dst, src in bridges.get(stage, []):
            for j in range(v):
                state[dst * v + j] ^= state[src * v + j]
    for bank in range(0, 8, 2):
        for j in range(v):
            a, b = bank * v + j, (bank + 1) * v + j
            state[a], state[b] = state[b], state[a]
    need(state == [1 << i for i in range(total)] + [0], "nine-stage full-column endpoint")
    bound = 64 * maxima[0]**3 * maxima[1]**2
    need(bound < 2**104, "local prefix bound")
    return {"formal_columns_checked": total, "independent_dirty_registers": dirt,
            "local_scalar_additions": adds, "local_odd_scalar_additions": odd,
            "stage_additions": 9 * adds, "bridge_additions": 18 * v,
            "fresh_center_copies": 81, "reverse_fresh_center_copies": 36,
            "local_raw_H": [[k, hist[k]] for k in sorted(hist)],
            "payload_prefix_upper": str(bound), "payload_prefix_bits": bound.bit_length(),
            "signed_lift_prefix": [{"reverse": bool(i), "cancellation_free_signed_row_l1_upper": str(m),
                                    "bits": m.bit_length()} for i, m in enumerate(maxima)]}


def replay(root=ROOT, package=HERE):
    source_pins(root, package)
    raw = fixtures(package)
    expected = read(package / "NATIVE.json")
    need(set(expected) == {"baseline", "deferred"}, "native receipt inventory")
    for label in ("baseline", "deferred"):
        actual = independent(raw[label])
        need(expected[label]["local_scalar_stream"] == "sha256:" + sha(raw[label]), "record binding")
        for key, value in actual.items():
            need(canonical(expected[label][key]) == canonical(value), "independent native field: " + key)
        need(len(expected[label]["stages"]) == 9, "native nine-stage receipt")
        controls = expected[label]["negative_controls"]
        need(canonical(controls) == canonical([{"omit_bridge": i, "rejected": True} for i in range(18)]),
             "bridge control inventory")
    try:
        independent(raw["missing-undo"])
    except ValueError as error:
        need(str(error) == "local defining full column", "wrong negative-control failure")
    else:
        raise ValueError("missing undo accepted")
    return {"status": "PASS_NATIVE_CACHE_INPUTS_AND_PYTHON_COLUMNS_ONLY", "native_executed": False,
            "words": 2, "formal_columns_per_word": 1327, "stages_per_word": 9,
            "payload_sha256": {key: sha(value) for key, value in raw.items()}}


if __name__ == "__main__":
    print(json.dumps(replay(), sort_keys=True))
