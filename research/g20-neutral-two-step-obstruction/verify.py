"""Exhaust the fixed-route two-step neighborhood of fourteen G20 neutral words.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The source emitter and A2 model are Ali Romman's #5708; the first-neighbor
question is Nick Petalas's #6305, following unpaidmoon #6290.
No predecessor executable is imported.
"""
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PREFIX = "research/g20-conjugation-admission/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_inputs():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    raw = {}
    for entry in manifest["files"]:
        if entry["usage"] != "input":
            continue
        data = (ROOT / entry["path"]).read_bytes()
        require(len(data) < 2_000_000, "source byte capacity")
        require(sha256(data).hexdigest() == entry["sha256"], "source hash: " + entry["path"])
        raw[entry["path"]] = data
    word = json.loads(gzip.decompress(raw[PREFIX + "WORD.json.gz"]))
    paths = json.loads(raw[PREFIX + "PATHS.json"])
    edges = {}
    for key, path in paths.items():
        require(len(path) == 1, "only published single-edge routes")
        origin, target, rank = path[0]
        require(key == f"{origin}:{target}" and type(rank) is int and 1 <= rank <= 7,
                "route encoding")
        edges[origin, target] = rank
    records = [tuple(event) for event in word["records"] if event[0] not in ("Q", "ZERO_Q")]
    require(len(records) == 11930 and len(word["start"]) == 685 and len(edges) == 2369,
            "frozen source dimensions")
    return word, records, edges


def indices(records):
    gates, destination, source, barriers = (defaultdict(list) for _ in range(4))
    for index, event in enumerate(records):
        if event[0] == "ADD":
            a, b = event[1:3]
            gates[a, b].append(index)
            destination[a].append(index)
            source[b].append(index)
        else:
            require(event[0] in ("INIT", "ERASE"), "scalar opcode")
            barriers[event[1]].append(index)
    return gates, destination, source, barriers


def interior(values, left, right):
    return values[bisect_right(values, left):bisect_left(values, right)]


def candidates(records, minimum=0):
    """All valid equal-gate intervals, indexed independently of interval scanning."""
    gates, dest, src, barriers = indices(records)
    for (a, b), positions in sorted(gates.items()):
        contacts = sorted(set(dest[b]) | set(src[a]))
        invalid = sorted(set(barriers[a]) | set(barriers[b]) | set(gates[b, a]))
        for offset, left in enumerate(positions):
            for right in positions[offset + 1:]:
                if interior(invalid, left, right):
                    continue
                touched = interior(contacts, left, right)
                if len(touched) < minimum:
                    continue
                changes = {}
                for index in touched:
                    _, d, s, frame = records[index]
                    changes[index] = ("ADD", a, s, frame) if d == b else ("ADD", d, b, frame)
                yield left, right, a, b, changes


def rewrite(records, candidate):
    left, right, a, b, changes = candidate
    require(records[left][:3] == records[right][:3] == ("ADD", a, b), "outer gates")
    result = []
    for index, event in enumerate(records):
        if index in (left, right):
            continue
        result.append(event)
        if index in changes:
            result.append(changes[index])
    require(len(result) == len(records) - 2 + len(changes), "rewrite event accounting")
    return result


def scalar_rows(records, width, owned):
    rows = [1 << i for i in range(width)]
    for event in records:
        op, dest = event[:2]
        if op == "ADD":
            rows[dest] ^= rows[event[2]]
        else:
            require(op in ("INIT", "ERASE") and dest in owned, "owned action")
            require(op != "INIT" or rows[dest] == 0, "live INIT")
            rows[dest] = 0
    return rows


def emit(records, start, final, owned, edges):
    """Charge complete routes, including obligations to route a zero destination."""
    rows, frames, paid = [1 << i for i in range(len(start))], list(start), Counter()
    for event in records:
        op, dest = event[:2]
        if op in ("INIT", "ERASE"):
            require(dest in owned and (op != "INIT" or not rows[dest]), "invalid owned event")
            rows[dest], frames[dest] = 0, event[2]
            continue
        require(op == "ADD", "unknown scalar event")
        source, frame = event[2:]
        if rows[source] == 0:
            continue
        for wire in (dest, source):
            old = frames[wire]
            if old == frame:
                continue
            if old is None:
                require(wire in owned and not rows[wire], "uninitialized nonzero row")
            elif (old, frame) not in edges:
                return None, (old, frame)
            elif rows[wire]:
                paid[edges[old, frame]] += 1
            frames[wire] = frame
        rows[dest] ^= rows[source]
    for wire, frame in enumerate(final):
        if wire in owned:
            require(not rows[wire], "owned return")
        elif frames[wire] != frame:
            if (frames[wire], frame) not in edges:
                return None, (frames[wire], frame)
            if rows[wire]:
                paid[edges[frames[wire], frame]] += 1
        frames[wire] = frame
    require(frames == list(final), "final frame restoration")
    return paid, None


def difference(paid, base):
    return tuple((rank, paid[rank] - base[rank]) for rank in sorted(paid.keys() | base.keys())
                 if paid[rank] != base[rank])


def positive_for_all_powers(delta):
    """Strict loss on 0<t<1 from positive charges or strict subadditivity."""
    if not delta:
        return False
    if all(count > 0 for rank, count in delta):
        return True
    positive = [(rank, count) for rank, count in delta if count > 0]
    negative = [(rank, -count) for rank, count in delta if count < 0]
    return (len(negative) == 1 and negative[0][1] == 1
            and sum(count for rank, count in positive) >= 2
            and sum(rank * count for rank, count in positive) == negative[0][0])


def identify_first(word, records, edges, base, endpoint):
    owned, first, total = set(word["owned"]), [], 0
    for candidate in candidates(records, minimum=4):
        total += 1
        changed = rewrite(records, candidate)
        require(scalar_rows(changed, len(word["start"]), owned) == endpoint, "first endpoint")
        paid, missing = emit(changed, word["start"], word["final"], owned, edges)
        if missing is None and paid == base:
            first.append(candidate)
    require(total == 1503 and len(first) == 14, "first-neighbor coverage")
    return first


def neighborhood(word, changed, edges, base, endpoint):
    owned, outcomes, counts, shapes = set(word["owned"]), [], Counter(), Counter()
    for candidate in candidates(changed):
        left, right, a, b, corrections = candidate
        final = rewrite(changed, candidate)
        require(scalar_rows(final, len(word["start"]), owned) == endpoint, "second endpoint")
        paid, missing = emit(final, word["start"], word["final"], owned, edges)
        delta = None if missing else difference(paid, base)
        if missing is None:
            require(not delta or positive_for_all_powers(delta), "unproved paid-moment sign")
            counts["strict_loss" if delta else "neutral"] += 1
            shapes[delta] += 1
        else:
            counts["missing_route"] += 1
        counts["candidates"] += 1
        counts["zero_contact"] += not corrections
        outcomes.append([left, right, a, b, len(corrections), missing, delta])
    return {"counts": dict(sorted(counts.items())), "shapes": [[k, v] for k, v in sorted(shapes.items())],
            "outcomes": outcomes}


def census(word, records, edges):
    width, owned = len(word["start"]), set(word["owned"])
    endpoint = [0 if i in owned else (1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0)
                for i in range(width)]
    require(scalar_rows(records, width, owned) == endpoint, "original scalar endpoint")
    base, missing = emit(records, word["start"], word["final"], owned, edges)
    require(missing is None and base == {1: 1281, 2: 1338, 3: 58, 4: 57, 5: 102, 6: 10},
            "original complete paid histogram")
    first = identify_first(word, records, edges, base, endpoint)
    branches = []
    for candidate in first:
        left, right, a, b, corrections = candidate
        result = neighborhood(word, rewrite(records, candidate), edges, base, endpoint)
        result["first"] = [left, right, a, b, len(corrections)]
        branches.append(result)
    return {"schema": "g20-neutral-two-step/v1", "base_paid": dict(sorted(base.items())),
            "first_domain": {"long_candidates": 1503, "neutral": 14}, "branches": branches}


def summarize(certificate):
    totals, shapes = Counter(), Counter()
    for branch in certificate["branches"]:
        totals.update(branch["counts"])
        for shape, count in branch["shapes"]:
            shapes[tuple(tuple(x) for x in shape)] += count
    require(totals["candidates"] == 31719 and totals["missing_route"] == 28746
            and totals["neutral"] == 297 and totals["strict_loss"] == 2676, "two-step coverage")
    return {"first_neighbors": len(certificate["branches"]), **dict(sorted(totals.items())),
            "shapes": [[shape, count] for shape, count in sorted(shapes.items())]}


def controls():
    outer = ("ADD", 0, 1, 0)
    simple = [outer, ("ADD", 1, 2, 0), outer]
    candidate = list(candidates(simple))[0]
    changed = rewrite(simple, candidate)
    require(scalar_rows(simple, 3, set()) == scalar_rows(changed, 3, set()), "A2 control")
    require(scalar_rows(simple, 3, set()) != scalar_rows(changed[:1], 3, set()), "missing correction")
    require(not list(candidates([outer, ("ADD", 1, 0, 0), outer])), "reverse contact rejection")
    require(not list(candidates([outer, ("ERASE", 0, 0), outer])), "barrier rejection")
    require(len(list(candidates([outer, outer]))) == 1, "zero-contact inclusion")
    require(not list(candidates([outer, outer], 1)), "contact lower boundary")
    for delta in (((1, 1), (2, -2), (3, 1)), ((1, -1),), ((1, 1), (3, -1))):
        require(not positive_for_all_powers(delta), "profitable or unknown shape accepted")
    require(positive_for_all_powers(((1, 2), (2, -1))), "strict split control")
    require(positive_for_all_powers(((1, 3), (2, 2))), "positive charge control")
    require(emit([outer], [1, 1], [0, 0], set(), {(1, 0): 2}) == ({2: 2}, None), "route charge")
    require(emit([outer], [1, 1], [0, 0], set(), {}) == (None, (1, 0)), "missing route")
    zero = [("ERASE", 0, 1), ("ADD", 1, 0, 0)]
    require(emit(zero, [0, 0], [1, 0], {0}, {}) == ({}, None), "zero-source omission")
    dirty = [("ERASE", 0, 1), ("ADD", 0, 1, 0)]
    require(emit(dirty, [0, 0], [0, 0], {0}, {}) == (None, (1, 0)), "zero-destination route")
    return 15


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write regenerated canonical certificate outside checkout")
    args = parser.parse_args()
    word, records, edges = load_inputs()
    result = census(word, records, edges)
    summary = summarize(result)
    checked = controls()
    payload = canonical(result)
    if args.output:
        require(not args.output.resolve().is_relative_to(ROOT), "output must be outside checkout")
        args.output.write_bytes(payload)
    else:
        expected = gzip.decompress((PACKAGE / "CERTIFICATE.json.gz").read_bytes())
        require(payload == expected, "complete certificate mismatch")
    print(json.dumps({"summary": summary, "controls": checked,
                      "certificate_sha256": sha256(payload).hexdigest()}, sort_keys=True))
    print("PASS_G20_NEUTRAL_TWO_STEP candidates=31719 missing=28746 neutral=297 strict_loss=2676")


if __name__ == "__main__":
    main()
