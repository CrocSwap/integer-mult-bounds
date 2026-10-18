#!/usr/bin/env python3
"""Exact finite Form-R obstruction and one-exception L8 witnesses."""

import argparse
import hashlib
import json
from pathlib import Path

SOURCE = "research/fstar-entry-class-scope-seed63d5f999/data/tied_min.json"
SOURCE_SHA256 = "670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93"
MAX_STATES = 100_000
ORTHOGONAL = tuple(
    sum(1 << b for b in range(1, 8) if (a & b).bit_count() % 2 == 0)
    for a in range(8)
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("nonfinite JSON constant: " + value)


def read_json(path, limit=2_000_000, digest=None):
    with path.open("rb") as stream:
        payload = stream.read(limit + 1)
    require(len(payload) <= limit, "JSON size limit")
    if digest is not None:
        require(hashlib.sha256(payload).hexdigest() == digest, "source hash mismatch")
    return json.loads(payload, object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def decode(raw):
    require(type(raw) is list and 1 <= len(raw) <= 12, "decoder size")
    rows = []
    for row in raw:
        require(type(row) is list and len(row) == 2, "factor pair")
        for factor in row:
            require(type(factor) is list and len(factor) == 3, "three totals")
            require(all(type(x) is int and -1 <= x <= 1 for x in factor),
                    "integer factor alphabet")
        p, q = map(tuple, row)
        require(all(p), "this finite model needs full odd P support")
        require(sum(x != 0 for x in q) == 2, "two odd Q entries")
        require(sum(p[j] * q[j] for j in range(3)) != 0, "nonzero diagonal")
        rows.append((p, q))
    return tuple(rows)


def local_pairs(q):
    """Cost zero is Form-R; cost one adds only (111, e_c)."""
    d = sum(1 << j for j in range(3) if q[j])
    result = []
    for a in range(1, 8):
        for b in range(1, 8):
            if b & ~d or (a & b).bit_count() % 2 != 1:
                continue
            form_r = b == d or (a == b and a in (1, 2, 4))
            if form_r or (a == 7 and b in (1, 2, 4)):
                result.append((a, b, int(not form_r)))
    return tuple(result)


def model(rows):
    n = len(rows)
    zeros = tuple(tuple(
        t != s and sum(rows[t][0][j] * rows[s][1][j] for j in range(3)) == 0
        for s in range(n)) for t in range(n))
    options = tuple(local_pairs(q) for _p, q in rows)
    return zeros, options


def advance(state, t, a, zeros):
    following = list(state)
    following[t] = 0
    for s in range(len(state)):
        if following[s] and zeros[t][s]:
            following[s] &= ORTHOGONAL[a]
            if following[s] == 0:
                return None
    return tuple(following)


def frontier_hash(frontier):
    records = [(state, frontier[state][0]) for state in sorted(frontier)]
    payload = json.dumps(records, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def next_layer(frontier, zeros, options, budget):
    following = {}
    for state in sorted(frontier):
        cost, prefix = frontier[state]
        for t, domain in enumerate(state):
            if not domain:
                continue
            for a in range(1, 8):
                choices = [(c, b) for aa, b, c in options[t]
                           if aa == a and domain & (1 << b)]
                if not choices:
                    continue
                extra, b = min(choices)
                if cost + extra > budget:
                    continue
                target = advance(state, t, a, zeros)
                if target is None:
                    continue
                total = cost + extra
                if target not in following or total < following[target][0]:
                    following[target] = (total, prefix + ((t, a, b),))
                    require(len(following) <= MAX_STATES, "state capacity exhausted")
    return following


def solve(rows, budget, capacity=MAX_STATES):
    """Keep every row, minimizing exceptional pairs up to the given budget."""
    require(type(budget) is int and 0 <= budget <= 1, "exception budget")
    require(type(capacity) is int and 1 <= capacity <= MAX_STATES, "state capacity")
    zeros, options = model(rows)
    initial = tuple(sum(1 << b for b in sorted({b for _a, b, _c in pairs}))
                    for pairs in options)
    frontier = {initial: (0, ())}
    layers = []
    total_states = 0
    for _depth in range(len(rows) + 1):
        total_states += len(frontier)
        require(total_states <= capacity, "state capacity exhausted")
        layers.append({"states": len(frontier), "sha256": frontier_hash(frontier)})
        if _depth == len(rows):
            break
        frontier = next_layer(frontier, zeros, options, budget)
    answer = frontier.get((0,) * len(rows))
    witness = None if answer is None else [list(item) for item in answer[1]]
    return {"minimum": None if answer is None else answer[0],
            "witness": witness, "layers": layers, "total_states": total_states}


def replay(rows, witness, expected_cost):
    n = len(rows)
    require(type(witness) is list and len(witness) == n, "witness length")
    require(all(type(item) is list and len(item) == 3
                and all(type(x) is int for x in item) for item in witness),
            "witness triples")
    require(sorted(t for t, _a, _b in witness) == list(range(n)), "witness order")
    zeros, options = model(rows)
    cost = 0
    for position, (t, a, b) in enumerate(witness):
        matches = [c for aa, bb, c in options[t] if (aa, bb) == (a, b)]
        require(len(matches) == 1, "invalid local pair")
        cost += matches[0]
        for s, _aa, bb in witness[position + 1:]:
            require(not zeros[t][s] or (a & bb).bit_count() % 2 == 0,
                    "forward zero-arc conflict")
    require(cost == expected_cost, "witness exception count")


def find_ten(sub):
    for dropped in range(11):
        indices = [t for t in range(11) if t != dropped]
        rows = tuple(sub[t] for t in indices)
        answer = solve(rows, 0)
        if answer["minimum"] == 0:
            replay(rows, answer["witness"], 0)
            return {"indices": indices, "witness": answer["witness"]}
    raise ValueError("ten-line Form-R witness missing")


def calculate(rows):
    require(len(rows) == 12, "the result needs the twelve-line fixture")
    records = []
    for omitted in range(12):
        indices = [t for t in range(12) if t != omitted]
        sub = tuple(rows[t] for t in indices)
        excluded = solve(sub, 0)
        require(excluded["minimum"] is None, "Form-R unexpectedly attains eleven")
        extended = solve(sub, 1)
        require(extended["minimum"] == 1, "one-exception witness missing")
        replay(sub, extended["witness"], 1)
        ten = find_ten(sub)
        records.append({"omitted": omitted, "indices": indices,
                        "form_r_maximum": 10, "minimum_interior_for_eleven": 1,
                        "form_r_exclusion": excluded, "extended": extended,
                        "ten_line": ten})
    return {"schema_version": 1, "source_sha256": SOURCE_SHA256,
            "scope": "twelve tied_min eleven-line restrictions only",
            "records": records, "full_twelve_form_r_maximum": 10}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--emit", action="store_true")
    output.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    source = args.source or package.parents[1] / SOURCE
    rows = decode(read_json(source, 4096, SOURCE_SHA256))
    result = calculate(rows)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.emit:
        print(text, end="")
    elif args.write_result:
        with args.write_result.open("x", encoding="utf-8") as stream:
            stream.write(text)
    else:
        retained = read_json(package / "RESULT.json")
        require(json.dumps(retained, sort_keys=True)
                == json.dumps(result, sort_keys=True), "complete receipt mismatch")
        print("PASS_FSTAR_ONE_INTERIOR records=12 form_r=10 "
              "minimum_interior=1 full_form_r=10")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        raise SystemExit("FAIL_FSTAR_ONE_INTERIOR: " + str(error)) from error
