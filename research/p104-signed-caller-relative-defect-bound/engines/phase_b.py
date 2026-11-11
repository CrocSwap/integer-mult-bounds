"""Independent exact two-phase Type B caller specialization and subset controls."""

import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"


def scaled(row, factor):
    return {k: factor*v for k, v in row.items() if factor*v}


def add(row, source, factor):
    out = row.copy()
    for k, value in source.items():
        next_value = out.get(k, 0) + factor*value
        if next_value:
            out[k] = next_value
        else:
            out.pop(k, None)
    return out


def identity(n, sign=1):
    return [{j: Q(sign)} for j in range(n)]


def rank(rows):
    pivots = {}
    for row in rows:
        r = row.copy()
        while r:
            key = min(r)
            if key not in pivots:
                pivots[key] = scaled(r, 1/r[key])
                break
            r = add(r, pivots[key], -r[key])
    return len(pivots)


def dense_relative(a, b):
    plus = ((1, a), (b, 1+a*b))
    minus = ((1, -a), (-b, 1+a*b))
    inv_plus = ((plus[1][1], -plus[0][1]), (-plus[1][0], plus[0][0]))
    rel = [[sum(inv_plus[i][k]*minus[k][j] for k in range(2)) for j in range(2)]
           for i in range(2)]
    assert rel[0][0]*rel[1][1]-rel[0][1]*rel[1][0] == 1
    diff = [{j: value for j, cell in enumerate(row) if (value := cell-int(i==j))}
            for i, row in enumerate(rel)]
    assert rank(diff) == 2
    assert rel != [[-1, 0], [0, -1]]
    return rel


def replay(caller, q, removed):
    ty = caller["types"]["B"]
    n, offset = ty["roles"], ty["offset"]
    rows = identity(n)
    for index, event in enumerate(caller["events"]):
        kind, op, *rest = event
        if kind == "J":
            u, v, a, b = rest[1]
            u, v, a, b = u-offset, v-offset, Q(a), Q(b)
            x, y = rows[u], rows[v]
            rows[u] = add(x, y, a*q)
            rows[v] = add(scaled(y, 1+a*b), x, b*q)
        elif kind == "B":
            r = rest[0]-offset
            if op == "ADD":
                rows[r] = add(rows[r], rows[rest[1]-offset], Q(rest[2]))
            elif op == "SCALE":
                rows[r] = scaled(rows[r], Q(rest[1]))
            elif op == "SWAP":
                s = rest[1]-offset
                rows[r], rows[s] = rows[s], rows[r]
            elif op in ("LAMBDA", "IDLE_ONE"):
                continue
            elif op == "IDLE_ODD":
                if index not in removed:
                    rows[r] = scaled(rows[r], q)
            else:
                raise ValueError(op)
    return rows


def controls():
    good = identity(3, -1)
    reflect_plane = [{0: Q(-1)}, {1: Q(-1)}, {2: Q(1)}]
    rotate_plane = [{1: Q(1)}, {0: Q(-1)}, {2: Q(1)}]
    e = identity(3)
    for test in (reflect_plane, rotate_plane):
        assert rank([add(row, unit, -1) for row, unit in zip(test, e, strict=True)]) == 2
    reflect_plane[2] = {2: Q(-1)}
    rotate_plane[2] = {2: Q(-1)}
    assert reflect_plane == good and rotate_plane != good
    return {"saturation_negative_identity_factors_pass": True, "rank_equal_rotation_fails": True}


def audit(caller, start, cap):
    ty = caller["types"]["B"]
    assert (ty["roles"], ty["offset"], len(ty["ports"]), caller["stages"]) == (36,36,8,17)
    assert all(row[0] == -1 and row[1] == 0 for row in ty["diagonal"])
    odd = {}
    relative = []
    for index, event in enumerate(caller["events"]):
        if event[:2] == ["B", "IDLE_ODD"]:
            assert len(event[3]) == 1 and event[4] % 2
            odd[index] = {"role": event[2], "stage": event[3][0], "q_power": event[4]}
        elif event[0] == "J":
            s, t, a, b = event[3]
            assert a and b and s != t and 36 <= s < 72 and 36 <= t < 72
            relative.append({"stage": event[1], "relative_active_block":
                             [[str(v) for v in row] for row in dense_relative(Q(a), Q(b))]})
    assert len(odd) == 4 and [r["stage"] for r in relative] == list(range(1,18))
    good_plus, good_minus = identity(36), identity(36,-1)
    assert replay(caller, 1, set()) == good_plus
    assert replay(caller, -1, set()) == good_minus
    assert replay(caller, 1, set(odd)) == good_plus
    all_subsets = [subset for n in range(1, 5) for subset in combinations(odd, n)]
    results = []
    for subset in all_subsets:
        if time.monotonic()-start >= cap:
            break
        mutation = replay(caller, -1, set(subset))
        difference = [add(row, unit, -1) for row, unit in zip(mutation, good_minus, strict=True)]
        assert any(difference)
        reason = "determinant" if len(subset)%2 else ("rank" if len(subset)==4 else "saturation")
        results.append({"removed": subset, "literal_endpoint_difference_rank": rank(difference), "reason": reason})
    return {
        "head": HEAD, "caller_sha256": CALLER, "ports": ty["ports"], "dimension": 36,
        "q_plus_endpoint": "+I", "q_minus_endpoint": "-I", "odd_idles": odd,
        "j_relative_blocks": relative, "literal_mutation_records": results,
        "subsets_tested": len(results), "unvisited_subsets": all_subsets[len(results):],
        "proof_census": dict(Counter(
            "determinant" if len(s)%2 else ("rank" if len(s)==4 else "saturation") for s in all_subsets)),
        "controls": controls(),
    }


def main():
    start = time.monotonic()
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caller", type=Path, required=True)
    parser.add_argument("--cap", type=float, default=17)
    args = parser.parse_args()
    assert 0 < args.cap <= 17
    raw = args.caller.read_bytes()
    if sha256(raw).hexdigest() != CALLER:
        raise ValueError("Changed caller bytes")
    print(json.dumps(audit(json.loads(raw), start, args.cap), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
