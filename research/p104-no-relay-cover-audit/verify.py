#!/usr/bin/env python3
"""Exact primal/dual certificate for the P104 no-relay access relaxation.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
Apache-2.0. No predecessor executable or third-party module is imported.
Default replay is read-only; all acceptance checks survive python -O.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WORD = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
FIXTURE = "research/p104-native-channel/inputs/P104-FIXTURE.json"
N = 104


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask -= low


def space(generators):
    """512-bit membership vector, independent of binary basis convention."""
    members = {0}
    for v in generators:
        require(type(v) is int and 0 <= v < 512, "invalid frame generator")
        members |= {x ^ v for x in tuple(members)}
    return sum(1 << x for x in members)


def includes(large, small):
    return large & small == small


def dimension(frame):
    size = frame.bit_count()
    require(size > 0 and size & (size - 1) == 0, "invalid subspace size")
    return size.bit_length() - 1


def authenticate():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    data = {}
    for pin in pins["files"]:
        if pin["usage"] == "input":
            raw = (ROOT / pin["path"]).read_bytes()
            require(sha256(raw).hexdigest() == pin["sha256"], "source drift")
            data[pin["path"]] = json.loads(raw)
    require(set(data) == {WORD, FIXTURE}, "input inventory drift")
    return data[WORD], data[FIXTURE]


def correction(fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            r = [0] * 8
            r[i], r[j] = 2, 2 * sign
            roots.add(tuple(r))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    section = fixture["section4_explicit_P104"]
    removed = {tuple(r) for r in section["F0"] + section["C"]}
    require(len(roots) == 120 and len(removed) == 16 and removed <= roots,
            "P104 puncture drift")
    ports = sorted(roots - removed)
    twice_c = [[2 * (t == s) - sum(x*y for x, y in zip(rt, rs)) // 4
                for s, rs in enumerate(ports)] for t, rt in enumerate(ports)]
    require(all(sum(x*y for x, y in zip(rt, rs)) % 4 == 0
                for rt in ports for rs in ports), "nonintegral Gram entry")
    require(all(sum(x != 0 for x in row) == 48 for row in twice_c),
            "correction row support drift")
    support = sum(1 << (N*t+s) for t, row in enumerate(twice_c)
                  for s, x in enumerate(row) if x)
    return support


def trace(word):
    """All event frames/directions; source/target paths, not native operators."""
    current = {r: space(f) for r, f in word["initial_frames"].items()}
    paths = {r: [(0, current[r])] for r in current if r.startswith(("X", "Y"))}
    require(len(paths) == 2*N, "data register inventory drift")
    source_cuts, target_cuts = [], []
    for cut, event in enumerate(word["program"], 1):
        op = event[0]
        if op == "transport":
            _, reg, before, after, rank = event
            a, b = space(before), space(after)
            require(current[reg] == a, "transport entry drift")
            require(a != b and (includes(a, b) or includes(b, a)), "nonnested transport")
            require(abs(dimension(a)-dimension(b)) == rank, "transport rank drift")
            if reg in paths:
                require(includes(b, a), "descending data path")
                paths[reg].append((cut, b))
                (source_cuts if reg.startswith("X") else target_cuts).append(cut)
            current[reg] = b
        elif op == "add":
            _, dst, src, coefficient, frame = event
            require(not dst.startswith("X"), "source value overwritten")
            require(not src.startswith("Y"), "target value read")
            require(current[dst] == current[src] == space(frame), "ADD frame drift")
            Fraction(coefficient)
        elif op == "zero":
            _, reg, frame = event
            require(reg == "C" and reg not in current, "private allocation drift")
            current[reg] = space(frame)
        elif op == "copy":
            _, dst, src, frame = event
            require(dst == "C" and not src.startswith("Y"), "private COPY direction drift")
            require(current[dst] == current[src] == space(frame), "COPY frame drift")
        elif op == "erase":
            _, reg, frame = event
            require(reg == "C" and current[reg] == space(frame), "private erase drift")
            del current[reg]
        else:
            raise Invalid("unknown event")
    require(current == {r: space(f) for r, f in word["final_frames"].items()},
            "final frame drift")
    require(max(source_cuts) < min(target_cuts), "source/target time separation fails")
    for i in range(N):
        xp, yp = paths[f"X{i}"], paths[f"Y{i}"]
        require(dimension(xp[0][1]) == 1 and dimension(xp[-1][1]) == 9,
                "source endpoint drift")
        require(yp[0][1] == 1 and dimension(yp[-1][1]) == 8,
                "target endpoint drift")
    return paths, {"events": len(word["program"]),
                   "last_source_transport_cut": max(source_cuts),
                   "first_target_transport_cut": min(target_cuts)}


def maximal_masks(items):
    """Drop subsets: every omitted option is covered by a retained option."""
    out = []
    for x in sorted(set(items), key=lambda x: (-x.bit_count(), x)):
        if not any(includes(y, x) for y in out):
            out.append(x)
    return tuple(sorted(out))


def chain_unions(nodes, upwards):
    """Antichain DP: all maximal port unions on nested contact chains.

    For sources, chains end at f and extend from a proper subspace.
    For targets, chains start at f and extend to a proper superspace.
    Sorting by dimension makes either recurrence acyclic.
    """
    result = {}
    for f in sorted(nodes, key=lambda x: (dimension(x), x), reverse=upwards):
        candidates = [nodes[f]]
        for u, unions in result.items():
            if (includes(u, f) if upwards else includes(f, u)):
                candidates.extend(nodes[f] | x for x in unions)
        result[f] = maximal_masks(candidates)
    return result


def rectangle(source_mask, target_mask):
    return sum(source_mask << (N*t) for t in bits(target_mask))


def cover_family(paths, support):
    source_nodes, target_nodes = defaultdict(int), defaultdict(int)
    for i in range(N):
        for _, f in paths[f"X{i}"]:
            source_nodes[f] |= 1 << i
        for _, f in paths[f"Y{i}"]:
            if f != 1:
                target_nodes[f] |= 1 << i
    src = chain_unions(source_nodes, False)
    tgt = chain_unions(target_nodes, True)
    raw = set()
    nested_count = 0
    for f, sources in src.items():
        for g, targets in tgt.items():
            if includes(g, f):
                nested_count += 1
                raw.update(rectangle(a, b) for a in sources for b in targets)
    require(all(includes(support, c) for c in raw), "carrier covers forbidden correction pair")
    covers = maximal_masks(raw)
    union = 0
    for c in covers:
        union |= c
    require(union == support, "cover family misses correction support")
    # Separate root/frame binding, not just agreement with the cover search.
    for t in range(N):
        terminal = paths[f"Y{t}"][-1][1]
        for s in range(N):
            label = next(v for v in bits(paths[f"X{s}"][0][1]) if v)
            require(bool(support & (1 << (N*t+s))) == bool(terminal & (1 << label)),
                    "root order / frame label mismatch")
    stats = {"source_frames": len(src), "target_frames": len(tgt),
             "source_chain_unions": sum(map(len, src.values())),
             "target_chain_unions": sum(map(len, tgt.values())),
             "nested_frame_pairs": nested_count, "raw_rectangles": len(raw),
             "maximal_rectangles": len(covers),
             "cover_size_histogram": dict(sorted(Counter(c.bit_count() for c in covers).items()))}
    return covers, stats


def edge_mask(entries):
    require(type(entries) is list, "edge list type")
    mask = 0
    for pair in entries:
        require(type(pair) is list and len(pair) == 2
                and all(type(x) is int and 0 <= x < N for x in pair), "invalid pair")
        t, s = pair
        b = 1 << (N*t+s)
        require(not mask & b, "duplicate pair")
        mask |= b
    return mask


def verify_certificate(certificate, support, covers):
    require(certificate["schema_version"] == 1, "certificate schema drift")
    singles = {c for c in covers if c.bit_count() == 1}
    singleton_mask = sum(singles)
    pack_extra = edge_mask(certificate["extra_packing"])
    require(not pack_extra & singleton_mask, "packing overlaps automatic singletons")
    packed = pack_extra | singleton_mask
    require(includes(support, packed), "packing outside correction support")
    require(all((packed & c).bit_count() <= 1 for c in covers), "packing capacity violated")
    chosen = []
    family = set(covers)
    for item in certificate["extra_cover"]:
        a = edge_mask([[0, s] for s in item["sources"]])
        b = edge_mask([[0, t] for t in item["targets"]])
        c = rectangle(a, b)
        require(c in family and c.bit_count() > 1, "cover is not a maximal admissible rectangle")
        chosen.append(c)
    require(len(set(chosen)) == len(chosen), "duplicate cover rectangle")
    covered = singleton_mask
    for c in chosen:
        covered |= c
    require(covered == support, "primal cover incomplete")
    lower = packed.bit_count()
    upper = len(singles) + len(chosen)
    require(lower == upper == certificate["optimum"], "primal/dual mismatch")
    require(type(certificate["optimum"]) is int, "optimum must be an integer")
    return {"correction_pairs": support.bit_count(), "forced_singletons": len(singles),
            "extra_packing_pairs": pack_extra.bit_count(), "extra_cover_rectangles": len(chosen),
            "exact_cover_minimum": lower}


def predecessor_fraction(covers):
    caps = {}
    for c in covers:
        for e in bits(c):
            caps[e] = max(caps.get(e, 0), c.bit_count())
    total = sum((Fraction(1, k) for k in caps.values()), Fraction())
    require(all(sum((Fraction(1, caps[e]) for e in bits(c)), Fraction()) <= 1
                for c in covers), "predecessor cover dual invalid")
    return {"fraction": str(total), "rounded_floor": -(-total.numerator // total.denominator),
            "edge_capacity_histogram": dict(sorted(Counter(caps.values()).items()))}


def reject(call, message):
    try:
        call()
    except Invalid as exc:
        require(str(exc) == message, "unexpected control failure: " + str(exc))
    else:
        raise Invalid("control was accepted: " + message)


def controls(word, fixture, certificate, support, covers):
    bad = deepcopy(word)
    next(e for e in bad["program"] if e[0] == "transport")[4] += 1
    reject(lambda: trace(bad), "transport rank drift")
    bad = deepcopy(word)
    event = next(e for e in bad["program"] if e[0] == "add")
    event[1] = "X0"
    reject(lambda: trace(bad), "source value overwritten")
    bad = deepcopy(fixture)
    bad["section4_explicit_P104"]["C"].pop()
    reject(lambda: correction(bad), "P104 puncture drift")
    bad = deepcopy(certificate)
    bad["extra_packing"].append(bad["extra_packing"][0])
    reject(lambda: verify_certificate(bad, support, covers), "duplicate pair")
    bad = deepcopy(certificate)
    bad["extra_packing"].append([0, 0])
    reject(lambda: verify_certificate(bad, support, covers), "packing outside correction support")
    bad = deepcopy(certificate)
    packed = edge_mask(bad["extra_packing"])
    c = next(c for c in covers if c.bit_count() > 1 and c & packed)
    extra = next(e for e in bits(c) if not packed & (1 << e))
    bad["extra_packing"].append([extra // N, extra % N])
    reject(lambda: verify_certificate(bad, support, covers), "packing capacity violated")
    bad = deepcopy(certificate)
    bad["extra_cover"].pop()
    reject(lambda: verify_certificate(bad, support, covers), "primal cover incomplete")
    bad = deepcopy(certificate)
    bad["extra_cover"][0] = {"sources": [0], "targets": [0]}
    reject(lambda: verify_certificate(bad, support, covers),
           "cover is not a maximal admissible rectangle")
    bad = deepcopy(certificate)
    bad["optimum"] -= 1
    reject(lambda: verify_certificate(bad, support, covers), "primal/dual mismatch")
    # Independent exhaustive tiny-poset oracle for the chain-antichain DP.
    nodes = {space([1]): 1, space([2]): 2, space([1, 2]): 4,
             space([4]): 8, space([1, 2, 4]): 16}
    for upwards in (False, True):
        actual = chain_unions(nodes, upwards)
        for start in nodes:
            all_unions = set()
            def visit(frame, acc):
                all_unions.add(acc)
                for nxt in nodes:
                    if nxt != frame and (includes(nxt, frame) if upwards else includes(frame, nxt)):
                        visit(nxt, acc | nodes[nxt])
            visit(start, nodes[start])
            require(actual[start] == maximal_masks(all_unions), "tiny chain oracle mismatch")
    # The source/target separation premise is material: with interleaving,
    # one carrier can read x0 and write y0 at <1>, then climb to <1,2>,
    # read x1 and write y1. The resulting support is triangular; neither
    # separated rectangle can cover the two diagonal entries together.
    left, full = space([1]), space([1, 2])
    src = chain_unions({left: 1, full: 2}, False)
    tgt = chain_unions({left: 1, full: 2}, True)
    tiny = [rectangle(a, b) for f, aa in src.items() for g, bb in tgt.items()
            if includes(g, f) for a in aa for b in bb]
    diagonal = (1 << 0) | (1 << (N+1))
    require(all((c & diagonal).bit_count() <= 1 for c in tiny), "interleaving boundary drift")
    carrier = [1, 0]
    y0 = carrier[:]
    carrier[1] += 1
    require(y0 == [1, 0] and carrier == [1, 1], "interleaving counterexample drift")
    # Relay or source-dependent initialization likewise invalidates the
    # direct-source-chain envelope: incomparable input lines may be merged.
    incomparable = chain_unions({space([1]): 1, space([2]): 2}, False)
    require(all(x != 3 for vv in incomparable.values() for x in vv), "line separation drift")
    require([a+b for a, b in zip([1, 0], [0, 1])] == [1, 1], "relay fixture drift")
    return ["transport_rank", "source_overwrite", "puncture", "duplicate_packing_pair",
            "unsupported_pair", "packing_capacity", "missing_cover", "illegal_cover",
            "wrong_optimum", "exhaustive_tiny_poset", "interleaved_read_write_boundary",
            "relay_or_preloaded_source_boundary"]


def calculate():
    word, fixture = authenticate()
    support = correction(fixture)
    paths, timing = trace(word)
    covers, enumeration = cover_family(paths, support)
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    result = verify_certificate(certificate, support, covers)
    old = predecessor_fraction(covers)
    checks = controls(word, fixture, certificate, support, covers)
    return {"schema_version": 1, "status": "PASS_P104_NO_RELAY_COVER_AUDIT",
            "timing": timing, "enumeration": enumeration, "primal_dual": result,
            "predecessor_fractional_certificate": old, "controls": checks,
            "scope": "Exact frozen-path access-cover relaxation; necessary no-relay carrier-lifetime bound, not an attaining physical circuit or supplier."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write a fresh checked result exclusively")
    args = parser.parse_args()
    result = calculate()
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.out:
        with args.out.open("x") as f:
            f.write(payload)
    else:
        require(json.loads(payload) == json.loads((HERE / "RESULT.json").read_text()), "result drift")
    print("PASS_P104_NO_RELAY_COVER_AUDIT pairs=4992 covers=4638 optimum=4580 previous_floor=4480 controls=12")


if __name__ == "__main__":
    try:
        main()
    except (Invalid, OSError, KeyError, TypeError, ValueError) as exc:
        raise SystemExit("FAIL: " + str(exc)) from exc
