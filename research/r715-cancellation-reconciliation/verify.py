#!/usr/bin/env python3
"""Portable, exact reconciliation of the archived R715 deletion witness.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
No historical checker, numerical package, solver or native binary is imported.
"""
import argparse
from collections import Counter
import hashlib
import json
from math import gcd
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PHASES = ("D", "A", "B", "C")
ARCHIVE = "research/experiment-log/negative-searches/"
PARENT = ARCHIVE + "nested-donors/trial-16/WORD.json"
CHILD = ARCHIVE + "commuting-cancellations/WORD.json"
RECORD = ARCHIVE + "commuting-cancellations/RESULT.json"
PARENT_HASH = "7721fa65c554b99e739b775e0015a46bb31d9afedd2172b0ad807e7cbf160757"
CHILD_HASH = "64e0796232c5ce0a06f7f9f685474dc9e4fb6e7e0368a8b24250d20bf0e280b7"


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def integer(x, lo, hi, message):
    require(type(x) is int and lo <= x < hi, message)
    return x


def primitive(row):
    """Unique primitive integer representative of a rational row direction."""
    g = 0
    for a in row:
        g = gcd(g, a)
    if not g:
        return tuple(row)
    if next(a for a in row if a) < 0:
        g = -g
    return tuple(a // g for a in row)


def reduce_row(vector, rows):
    v = tuple(vector)
    for row in rows:
        p = next(i for i, a in enumerate(row) if a)
        if v[p]:
            v = primitive(tuple(row[p] * a - v[p] * b
                                for a, b in zip(v, row)))
    return v


def rational_basis(vectors):
    """Fraction-free elimination, with a canonical primitive reduced result."""
    rows = []
    for vector in vectors:
        v = primitive(reduce_row(vector, rows))
        if any(v):
            rows.append(v)
            rows.sort(key=lambda r: next(i for i, a in enumerate(r) if a))
    for j in range(len(rows) - 1, -1, -1):
        p = next(i for i, a in enumerate(rows[j]) if a)
        for i in range(j):
            if rows[i][p]:
                rows[i] = primitive(tuple(rows[j][p] * a - rows[i][p] * b
                                          for a, b in zip(rows[i], rows[j])))
    return tuple(rows)


def contained(left, right):
    return all(not any(reduce_row(row, right)) for row in left)


def flatten(word, phase):
    n = 2 * word["v"] + word["R"]
    out = []
    for gate in word[phase]:
        require(type(gate) is list and len(gate) == 3, "gate shape")
        f, d, sources = gate
        integer(f, 0, len(word["frames"]), "gate frame index")
        integer(d, word["v"], n, "destination index")
        require(type(sources) is list, "source list")
        for s in sources:
            integer(s, 0, n, "source index")
        require(len(set(sources)) == len(sources) and d not in sources,
                "distinct transvection endpoints")
        out.extend((f, d, s) for s in sources)
    return out


def deletion_audit(before, after, record):
    require(set(before) == set(after), "word metadata keys")
    require(all(before[k] == after[k] for k in before if k not in PHASES),
            "unchanged non-gate metadata")
    require(record["source_sha256"] == PARENT_HASH and
            record["word_sha256"] == CHILD_HASH, "historical source identifiers")
    require(len(record["changes"]) == 20, "complete 20-pair witness")
    removed = {p: set() for p in PHASES}
    crossed = 0
    for change in record["changes"]:
        ph = change["phase"]
        require(ph in PHASES, "deletion phase")
        gates = flatten(before, ph)
        pair = change["removed_original_indices"]
        require(type(pair) is list and len(pair) == 2, "deletion index pair")
        i, j = pair
        integer(i, 0, len(gates), "first deletion index")
        integer(j, i + 1, len(gates), "second deletion index")
        require(not ({i, j} & removed[ph]), "overlapping deletion indices")
        removed[ph].update((i, j))
        f, d, s = gates[i]
        require(gates[j] == gates[i] and change["gate"] == [f, d, [s]],
                "identical framed deletion gates")
        # Sufficient symbolic commutation law for elementary F2 transvections.
        # Check the ORIGINAL middle, including gates removed by other pairs.
        for _, dd, ss in gates[i + 1:j]:
            require(dd != s and ss != d, "noncommuting crossed gate")
            crossed += 1
    counts = {}
    for ph in PHASES:
        old, new = flatten(before, ph), flatten(after, ph)
        require([g for k, g in enumerate(old) if k not in removed[ph]] == new,
                "exact retained gate subsequence")
        counts[ph] = {"before": len(old), "after": len(new),
                      "removed": len(removed[ph])}
    return {"pairs": len(record["changes"]), "crossed_gates": crossed,
            "phase_additions": counts}


def geometry(word):
    require((word["format"], word["h"], word["v"], word["R"],
             word["form"], word["coords"]) ==
            ("bitE8/1", 8, 120, 715, "<x,y>/2", "ham"), "frozen geometry")
    lines = word["lines"]
    require(len(lines) == 120, "root line count")
    require(all(len(r) == 8 and all(type(x) is int for x in r) for r in lines),
            "integral root coordinates")
    bases, closures = [], []
    for frame in word["frames"]:
        require(type(frame) is list and len(set(frame)) == len(frame), "frame set")
        for i in frame:
            integer(i, 0, 120, "root line index")
        b = rational_basis(lines[i] for i in frame)
        bases.append(b)
        closures.append(sum(1 << i for i, row in enumerate(lines)
                            if not any(reduce_row(row, b))))
    full = rational_basis(lines)
    require(len(full) == 8, "ambient rank")
    perps = [rational_basis(row for row in lines if
                            sum(a * b for a, b in zip(row, target)) == 0)
             for target in lines]
    return bases, closures, full, perps


def scalar_run(word, values, reverse=False):
    """Literal arbitrary-dirty binary map; copy values frozen at the scatter."""
    phases = tuple(reversed(PHASES)) if reverse else PHASES
    for phase in phases:
        if not reverse and phase == "B":
            copies = [values[r] for r in word["ret"]]
            for t, row in enumerate(word["scatter"]):
                for k in row:
                    values[word["v"] + t] ^= copies[k]
        gates = flatten(word, phase)
        for _, d, s in reversed(gates) if reverse else gates:
            values[d] ^= values[s]
        if reverse and phase == "B":
            copies = [values[r] for r in word["ret"]]
            for t, row in enumerate(word["scatter"]):
                for k in row:
                    values[word["v"] + t] ^= copies[k]
    return values


def replay(word, geo):
    bases, closures, full, perps = geo
    n, v = 955, 120
    require(len(word["start"]) == n and len(word["final"]) == n, "frame endpoints")
    for f in word["start"] + word["final"]:
        integer(f, 0, len(bases), "endpoint frame index")
    cur = [bases[f] for f in word["start"]]
    initial = list(cur)
    for i in range(v):
        require(cur[i] == rational_basis([word["lines"][i]]), "source start frame")
        require(not cur[v + i], "target start frame")
    require(len(word["ret"]) == 9 and len(set(word["ret"])) == 9, "retained copies")
    for r in word["ret"]:
        integer(r, 2 * v, n, "retained helper index")
    require(len(word["scatter"]) == v, "scatter output count")
    for row in word["scatter"]:
        require(type(row) is list and len(set(row)) == len(row), "scatter row")
        for k in row:
            integer(k, 0, len(word["ret"]), "scatter copy index")
    values = [1 << i for i in range(n)]
    support = [1 << i if i < v else 0 for i in range(n)]
    hist = Counter()
    paths = [[b] for b in cur]
    boundaries, support_boundaries = {}, {}
    checked_supports = 0

    def climb(r, frame):
        new = bases[frame]
        if cur[r] != new:
            require(contained(cur[r], new), "non-nested frame transition")
            delta = len(new) - len(cur[r])
            require(delta > 0, "strict frame rank increase")
            hist[delta] += 1
            cur[r] = new
            paths[r].append(new)

    for ph in PHASES:
        if ph == "B":
            require(all(not cur[r] for r in range(v, 2 * v)), "scatter target frame")
            copies = [values[r] for r in word["ret"]]
            copy_support = [support[r] for r in word["ret"]]
            for r in word["ret"]:
                hist[len(cur[r])] += 1
            for t, row in enumerate(word["scatter"]):
                for k in row:
                    values[v + t] ^= copies[k]
                    support[v + t] |= copy_support[k]
        flatten(word, ph)  # Validate even empty-source frame-visit records.
        for f, d, sources in word[ph]:
            climb(d, f)
            for s in sources:
                climb(s, f)
            for s in sources:
                if s < v or s >= 2 * v:
                    require(support[s] & ~closures[f] == 0, "source support outside frame")
                    checked_supports += 1
                values[d] ^= values[s]
                support[d] |= support[s]
            if d >= 2 * v:
                require(support[d] & ~closures[f] == 0, "helper support outside frame")
                checked_supports += 1
        if ph == "D":
            require(cur[v:] == initial[v:], "D compensation frame boundary")
        boundaries[ph] = digest(canonical(values))
        support_boundaries[ph] = tuple(support)
    for r, f in enumerate(word["final"]):
        climb(r, f)
    for r in range(n):
        expected = (1 << r) ^ ((1 << (r - v)) if v <= r < 2 * v else 0)
        require(values[r] == expected, "arbitrary-dirty endpoint")
        require(cur[r] == (perps[r - v] if v <= r < 2 * v else full), "final frame")
    identity = [1 << i for i in range(n)]
    require(scalar_run(word, list(identity)) == values, "separate scalar replay")
    require(scalar_run(word, list(values), reverse=True) == identity, "literal inverse roundtrip")
    require(scalar_run(word, list(identity), reverse=True) == values, "inverse endpoint")
    return {"profile": {str(k): hist[k] for k in sorted(hist)},
            "rank_mass": sum(k * c for k, c in hist.items()),
            "paid_children": sum(hist.values()), "copies": len(word["ret"]),
            "checked_supports": checked_supports,
            "phase_map_sha256": boundaries,
            "frame_itineraries_sha256": digest(canonical(paths)),
            "support_boundaries": support_boundaries}


def reconcile(before, after, record):
    deletion = deletion_audit(before, after, record)
    for key in ("before_profile", "after_profile"):
        require(set(record[key]) == {str(i) for i in range(1, 9)} and
                all(type(v) is int and v > 0 for v in record[key].values()),
                "exact integer profile counts")
    geo = geometry(before)
    a, b = replay(before, geo), replay(after, geo)
    require(a["profile"] == record["before_profile"], "before paid profile")
    require(b["profile"] == record["after_profile"], "after paid profile")
    require(a["profile"] == b["profile"], "unchanged paid profile")
    require(a["frame_itineraries_sha256"] == b["frame_itineraries_sha256"],
            "unchanged complete frame itineraries")
    require(a["phase_map_sha256"] == b["phase_map_sha256"], "equal phase boundary maps")
    for ph in PHASES:
        require(all(y & ~x == 0 for x, y in
                    zip(a["support_boundaries"][ph], b["support_boundaries"][ph])),
                "positive source-support domination")
    a.pop("support_boundaries")
    b.pop("support_boundaries")
    return {"status": "PASS_R715_CANCELLATION_RECONCILIATION", "columns": 955,
            "source_aliases": 4, "deletion": deletion,
            "empty_source_frame_visits": {
                "before": sum(not g[2] for p in PHASES for g in before[p]),
                "after": sum(not g[2] for p in PHASES for g in after[p])},
            "frames": len(geo[0]), "distinct_rational_frames": len(set(geo[0])),
            "before": a, "after": b,
            "scope": "Exact finite binary maps, rational frame paths and local paid profile; no fresh native, global, precision or outer replay."}


def load_sources(root):
    pins = json.loads((HERE / "SOURCE-PINS.json").read_text())
    for name, item in pins["files"].items():
        raw = (root / name).read_bytes()
        require(digest(raw) == item["sha256"], "source pin: " + name)
        obj = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(obj).hexdigest() == item["git_blob"], "Git blob pin: " + name)
    manifest = json.loads((root / "research/experiment-log/MANIFEST.json").read_text())
    aliases = [ARCHIVE + f"nested-donors/trial-{i}/WORD.json" for i in range(16, 20)]
    for name in aliases:
        require(digest((root / name).read_bytes()) == PARENT_HASH, "parent alias bytes")
        require(manifest[name.removeprefix("research/experiment-log/")] == PARENT_HASH,
                "parent alias manifest")
    require(digest((root / CHILD).read_bytes()) == CHILD_HASH, "child word bytes")
    return tuple(json.loads((root / p).read_text()) for p in (PARENT, CHILD, RECORD))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=HERE.parents[1])
    parser.add_argument("--write", type=Path, help="write a new receipt (must not exist)")
    args = parser.parse_args()
    result = reconcile(*load_sources(args.root))
    raw = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        with args.write.open("x") as f:
            f.write(raw)
    else:
        require(json.loads((HERE / "RESULT.json").read_text()) == result, "complete receipt equality")
    print("PASS_R715_CANCELLATION_RECONCILIATION aliases=4 pairs=20 ADDs=15014->14974 columns=955 profile=unchanged")


if __name__ == "__main__":
    try:
        main()
    except (Invalid, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        print("FAIL_R715_CANCELLATION_RECONCILIATION:", error, file=sys.stderr)
        sys.exit(1)
