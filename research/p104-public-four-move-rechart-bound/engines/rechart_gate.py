"""Exact inherited public ADD contact and GF(2) chart-rank gate."""

from argparse import ArgumentParser
from bisect import bisect_left
from collections import Counter
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import alarm
from time import monotonic

PRICE = "preflight/PRICE.json"
WORD = "preflight/inputs/7334-WORD.json.gz"
ANCESTOR = "lead/inputs/7277-WORD.json.gz"
PINS = {
    PRICE: "005efb8329d38638800d82e5273580b1bb529ac490d9923ba1a92e112d31c8b1",
    WORD: "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    ANCESTOR: "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
ANCESTOR_HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
CASE_CAP, HARD_SECONDS, SOFT_SECONDS = 9, 20, 18


class DeadlineReached(Exception):
    """The cooperative gate stopped before resolving a frozen key."""


def check_time(deadline):
    if monotonic() >= deadline:
        raise DeadlineReached


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def authenticate(root):
    raw = {}
    for relative, pin in PINS.items():
        raw[relative] = (root / relative).read_bytes()
        if sha256(raw[relative]).hexdigest() != pin:
            raise ValueError(f"changed dependency {relative}")
    return raw


def contacts(word, tracked, deadline):
    tape = word["program"]
    public = word["public"]
    initial, final = word["initial"], word["final"]
    active = {role: initial[role] for role in tracked}
    index = {role: [] for role in tracked}
    for clock, event in enumerate(tape):
        if clock % 256 == 0:
            check_time(deadline)
        opcode, dst = event[:2]
        if opcode == "MOVE":
            if dst in index:
                a, b, owned = event[2:]
                assert dst < public and owned is False and active[dst] == a
                active[dst] = b
                index[dst].append(clock)
        elif opcode in ("ADD", "COPY", "SCALE"):
            roles = event[1:3] if opcode in ("ADD", "COPY") else event[1:2]
            for role in roles:
                if role in index:
                    assert active[role] == event[-1]
                    index[role].append(clock)
        else:
            assert opcode in ("INIT", "CLEAR") and dst not in index
    assert all(active[role] == final[role] for role in tracked)
    return index


def expected_moves(operand):
    r = operand["role"]
    a, b, c = operand["charts"]
    return ["MOVE", r, a, b, False], ["MOVE", r, b, c, False]


def incident_neighbors(tape, index, role, clock):
    row = index[role]
    k = bisect_left(row, clock)
    assert k < len(row) and row[k] == clock
    return [
        [row[k - 1], tape[row[k - 1]]] if k else None,
        [row[k + 1], tape[row[k + 1]]] if k + 1 < len(row) else None,
    ]


def clock_order(add, pairs):
    named = [(add, "ADD")]
    for role, (a, b) in pairs.items():
        named.extend(((a, f"{role}:in"), (b, f"{role}:out")))
    assert len({clock for clock, _ in named}) == 5
    return [name for _, name in sorted(named)]


def identify(old, now, old_index, now_index, row):
    old_tape, now_tape = old["program"], now["program"]
    old_add, _ = row["key"]
    operands = row["operands"]
    roles = [x["role"] for x in operands]
    add = old_tape[old_add]
    assert add[0] == "ADD" and set(add[1:3]) == set(roles) and Fraction(add[3])
    assert add[-1] == operands[0]["charts"][1] == operands[1]["charts"][1]
    old_moves = {x["role"]: x["moves"] for x in operands}
    for operand in operands:
        r = operand["role"]
        expected = expected_moves(operand)
        a, b = old_moves[r]
        assert a < old_add < b
        assert incident_neighbors(old_tape, old_index, r, old_add) == [[a, expected[0]], [b, expected[1]]]

    # The protected-role filter excludes the sources of changed public-public
    # contacts in #7314 and #7334. Equal literal contacts retain their order.
    same_old = [k for k in old_index[roles[0]] if old_tape[k] == add]
    same_now = [k for k in now_index[roles[0]] if now_tape[k] == add]
    old_ordinal = same_old.index(old_add)
    evidence = {
        "literal_ADD": add, "ancestor_ADD_clock": old_add, "ancestor_MOVE_clocks": old_moves,
        "ancestor_exact_ADD_clocks": same_old, "current_exact_ADD_clocks": same_now,
        "ancestor_exact_ADD_ordinal": old_ordinal,
    }
    if not same_now:
        return "missing_inherited_literal_ADD", evidence
    if len(same_old) != len(same_now):
        return "unresolved_ancestry_ordinal", evidence

    current_add = same_now[old_ordinal]
    neighbors = {r: incident_neighbors(now_tape, now_index, r, current_add) for r in roles}
    evidence |= {"current_ADD_clock": current_add, "current_incident_neighbors": neighbors}
    current_moves = {}
    for operand in operands:
        r = operand["role"]
        incoming, outgoing = neighbors[r]
        expected = expected_moves(operand)
        if not incoming or not outgoing or incoming[1] != expected[0] or outgoing[1] != expected[1]:
            return "missing_inherited_immediate_MOVE_pair", evidence
        current_moves[r] = [incoming[0], outgoing[0]]

    old_order = clock_order(old_add, old_moves)
    now_order = clock_order(current_add, current_moves)
    evidence |= {"current_MOVE_clocks": current_moves, "ancestor_relative_order": old_order,
                 "current_relative_order": now_order}
    if old_order != now_order:
        return "changed_inherited_clock_order", evidence
    charts = {c for operand in operands for c in operand["charts"]}
    if any(old["frames"][c] != now["frames"][c] for c in charts):
        return "unresolved_chart_payload", evidence
    return "contact_match", evidence


def space(vectors):
    elements = {0}
    for v in vectors:
        assert type(v) is int and 0 <= v < 512
        if v not in elements:
            elements |= {v ^ x for x in elements}
    return elements


def basis(elements):
    vectors = []
    span = {0}
    for x in sorted(elements):
        if x not in span:
            vectors.append(x)
            span |= {x ^ y for y in span}
    assert span == elements
    return vectors


def dimensions(elements):
    size = len(elements)
    rank = size.bit_length() - 1
    assert size == 1 << rank
    return rank


def geometry(frames, chart_paths, old_ranks, offset, deadline):
    check_time(deadline)
    (a, b, c), (d, middle, e) = chart_paths
    assert b == middle and offset
    frame = {i: frames[i] for i in {a,b,c,d,e}}
    spans = {i: space(vectors) for i, vectors in frame.items()}
    rank = {i: dimensions(value) for i, value in spans.items()}
    assert all(rank[i] == len(frame[i]) for i in frame)
    assert spans[a] < spans[b] < spans[c] and spans[d] < spans[b] < spans[e]
    assert old_ranks == [[rank[b] - rank[a], rank[c] - rank[b]], [rank[b] - rank[d], rank[e] - rank[b]]]
    low = space(frame[a] + frame[d])
    high = spans[c] & spans[e]
    high_sum = space(frame[c] + frame[e])
    assert low <= spans[b] <= high
    low_dim, high_dim, high_sum_dim = map(dimensions, (low, high, high_sum))
    assert high_dim == rank[c] + rank[e] - high_sum_dim
    wanted = rank[b] + offset
    new_ranks = [[wanted-rank[a], rank[c]-wanted], [wanted-rank[d], rank[e]-wanted]]
    assert new_ranks == [[p+offset,q-offset] for p,q in old_ranks] and min(sum(new_ranks, [])) > 0
    certificate = {
        "chart_bases": frame, "chart_ranks": rank, "wanted_rank": wanted,
        "low_union_basis": basis(low), "low_union_rank": low_dim,
        "high_intersection_basis": basis(high), "high_intersection_rank": high_dim,
        "high_sum_basis": basis(high_sum), "high_sum_rank": high_sum_dim,
        "new_paid_ranks": new_ranks,
    }
    if wanted < low_dim:
        return "low_union_too_large", certificate
    if wanted > high_dim:
        return "high_intersection_too_small", certificate

    for i, f in enumerate(frames):
        if i % 32 == 0:
            check_time(deadline)
        if len(f) == wanted and all(x in high for x in f):
            s = space(f)
            if len(s) == 1 << wanted and low <= s:
                certificate["midpoint"] = {"kind": "existing_chart", "chart": i, "basis": f}
                break
    else:
        constructed = basis(low)
        current = low.copy()
        for x in sorted(high):
            if len(constructed) == wanted:
                break
            if x not in current:
                constructed.append(x)
                current |= {x ^ y for y in current}
        assert len(constructed) == wanted and low <= current <= high
        certificate["midpoint"] = {"kind": "new_descriptor_pending_compiler", "basis": constructed}
    return "exact_geometry_survivor", certificate


def controls():
    paths, old = [[0,1,2],[0,1,3]], [[1,2],[1,2]]
    start = monotonic()
    expand = [[], [1], [1,2,4], [1,2,8], [1,2]]
    status, r = geometry(expand,paths,old,1,start+2)
    assert status == "exact_geometry_survivor" and r["midpoint"]["chart"] == 4
    saturated = [[], [1], [1,2,4], [1,8,16]]
    status, r = geometry(saturated,paths,old,1,start+2)
    assert status == "high_intersection_too_small" and r["high_intersection_basis"] == [1]
    new = expand[:-1]
    status, r = geometry(new,paths,old,1,start+2)
    assert status == "exact_geometry_survivor" and r["midpoint"]["basis"] == [1,2]
    w = {"public":3,"initial":[0,0,1],"final":[2,3,1],"frames":expand,
         "program":[["MOVE",0,0,1,False],["MOVE",1,0,1,False],["ADD",0,1,"-2",1],
                    ["MOVE",0,1,2,False],["MOVE",1,1,3,False]]}
    row = {"key":[2,1],"operands":[{"role":0,"moves":[0,3],"charts":paths[0]},
                                    {"role":1,"moves":[1,4],"charts":paths[1]}]}
    n = w | {"program":w["program"][:2]+[["ADD",2,1,"1",1]]+w["program"][2:]}
    old_index, now_index = [contacts(x,{0,1},start+2) for x in (w,n)]
    status, evidence = identify(w,n,old_index,now_index,row)
    assert status == "missing_inherited_immediate_MOVE_pair"
    assert evidence["current_incident_neighbors"][1][0] == [2,["ADD",2,1,"1",1]]
    return ["expanded_high_intersection", "saturated_high_intersection",
            "deterministic_new_descriptor", "intervening_source_read_blocks_contact"]


def helpers(word):
    mains = set(word["live"]) | {r+112 for r in word["live"]}
    mains.update(word["hosted"]["X2"], word["hosted"]["Y2"])
    assert len(mains) == 400 and word["public"] == 1501
    return set(range(word["public"])) - mains


def audit(raw, deadline):
    price = loads(raw[PRICE], object_pairs_hook=unique)
    assert price["head"] == HEAD and price["predecessor_head"] == ANCESTOR_HEAD and price["word_sha256"] == PINS[WORD]
    assert not price["price_unresolved"] and price["first_runner_seconds"] == HARD_SECONDS
    cases = price["alternatives"]
    assert len(cases) == CASE_CAP and len({tuple(row["key"]) for row in cases}) == CASE_CAP
    outcomes, visited = [], 0
    stage = "decode"
    try:
        old, now = [loads(decompress(raw[rel]), object_pairs_hook=unique) for rel in (ANCESTOR, WORD)]
        stage = "contact_index"
        tracked = {operand["role"] for row in cases for operand in row["operands"]}
        assert tracked <= helpers(old) & helpers(now) and not tracked & set(price["protected_roles"])
        old_index, now_index = [contacts(w,tracked,deadline) for w in (old,now)]
        stage = "nine_frozen_keys"
        for row in cases:
            check_time(deadline)
            status, evidence = identify(old,now,old_index,now_index,row)
            if status == "contact_match":
                status, certificate = geometry(now["frames"],[x["charts"] for x in row["operands"]],
                                               [x["ranks"] for x in row["operands"]],
                                               row["delta_midpoint_rank"], deadline)
                evidence["geometry_certificate"] = certificate
            outcomes.append({"key": row["key"], "status": status,
                             "gross_at_incumbent": row["gross_at_incumbent"], **evidence})
            visited += 1
    except DeadlineReached:
        pass
    unvisited = [{"key": row["key"],"gross_at_incumbent":row["gross_at_incumbent"]} for row in cases[visited:]]
    unresolved = [r["key"] for r in outcomes if r["status"].startswith("unresolved")]
    survivors = [r["key"] for r in outcomes if r["status"] == "exact_geometry_survivor"]
    return {
        "head":HEAD, "ancestor_head":ANCESTOR_HEAD, "input_sha256":PINS,
        "price_sha256":PINS[PRICE], "word_sha256":PINS[WORD],
        "status":"CAPPED" if unvisited else "EXHAUSTED", "last_stage":stage,
        "case_cap":CASE_CAP, "hard_seconds":HARD_SECONDS, "cooperative_seconds":SOFT_SECONDS,
        "visited":visited, "unvisited":unvisited, "unresolved":unresolved,
        "counts":dict(Counter(r["status"] for r in outcomes)), "survivors":survivors, "outcomes":outcomes,
        "scope":"Nine frozen public-helper fixed-clock ADD recharts, exact ancestor ordinal and current contact topology, then exact GF(2) rank.",
    }


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?")
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    if args.controls_only:
        print(dumps({"controls": controls()}, sort_keys=True))
        return
    if args.root is None:
        parser.error("the R88 evidence root is required")
    alarm(HARD_SECONDS)
    deadline = monotonic() + SOFT_SECONDS
    raw = authenticate(args.root)
    checked = controls()
    result = audit(raw, deadline)
    result["controls"] = checked
    print(dumps(result, sort_keys=True, indent=2))
    alarm(0)


if __name__ == "__main__":
    main()
