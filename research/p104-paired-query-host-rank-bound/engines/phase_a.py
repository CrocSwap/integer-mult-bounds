"""Independent exact Type A phase replay and query deletion controls."""

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
    for raw in rows:
        row = raw.copy()
        while row:
            key = min(row)
            if key not in pivots:
                pivots[key] = scaled(row, 1/row[key])
                break
            row = add(row, pivots[key], -row[key])
    return len(pivots)


def product(a, b):
    result = []
    for row in a:
        out = {}
        for j, factor in row.items():
            out = add(out, b[j], factor)
        result.append(out)
    return result


def difference(a, b):
    return [add(x, y, -1) for x, y in zip(a, b, strict=True)]


def replay(caller, q, removed):
    ty = caller["types"]["A"]
    n, alpha = ty["roles"], Q(ty["alpha2"])
    rows = identity(n)
    for index, event in enumerate(caller["events"]):
        kind, op, *rest = event
        if kind == "J":
            x, y, u, v = rest[0]
            rows[y] = add(rows[y], rows[x], q)
            rows[u] = add(rows[u], rows[v], alpha*q)
        elif kind == "A":
            r = rest[0]
            if op == "ADD":
                rows[r] = add(rows[r], rows[rest[1]], Q(rest[2]))
            elif op == "SCALE":
                rows[r] = scaled(rows[r], Q(rest[1]))
            elif op == "SWAP":
                s = rest[1]
                rows[r], rows[s] = rows[s], rows[r]
            elif op == "QUERY":
                phase = q if rest[2] % 2 else 1
                rows[r] = add(rows[r], rows[rest[1]], 1 if index in removed else phase)
            elif op not in ("LAMBDA", "IDLE_ONE"):
                raise ValueError(op)
    return rows


def relative_shears(axes, alpha):
    x, y, u, v = axes
    assert len({x,y,u,v}) == 4 and min(axes) >= 0 and max(axes) < 36 and alpha
    local = {global_role: local_role for local_role, global_role in enumerate(axes)}
    i, j, k, l = [local[r] for r in axes]
    unit = identity(4)
    plus_inverse = identity(4)
    plus_inverse[j][i] = Q(-1)
    plus_inverse[k][l] = -alpha
    relative = product(plus_inverse, plus_inverse)
    defect = difference(relative, unit)
    assert rank(defect) == 2 and not any(product(defect, defect))
    plus_identity = [add(a,b,1) for a,b in zip(relative,unit,strict=True)]
    assert rank(product(plus_identity,defect)) == 2
    return [[y,x,str(defect[j][i])], [u,v,str(defect[k][l])]]


def controls():
    unit = identity(4)
    first = identity(4)
    first[1][0] = Q(1)
    first[3][2] = Q(1)
    inverse = identity(4)
    inverse[1][0] = Q(-1)
    inverse[3][2] = Q(-1)
    positive = [scaled(row,-1) for row in inverse]
    negative = [{0:Q(-1)}, {1:Q(-2)}, {2:Q(1,2)}, {3:Q(1)}]
    assert product(positive, first) == identity(4,-1)
    assert rank(difference(first,unit)) + rank(difference(positive,unit)) == 6
    assert Q(-1)*Q(-2)*Q(1,2) == 1
    assert rank(difference(first,unit)) + rank(difference(negative,unit)) == 5
    assert product(negative, first) != identity(4,-1)
    return {"positive_exact_slack_two": True, "negative_determinant_one_slack_one": True}


def reason(subset):
    return "slack_one" if len(subset) == 1 else ("slack_zero" if len(subset) == 2 else "rank")


def audit(caller, start, cap):
    ty = caller["types"]["A"]
    assert (ty["roles"], ty["offset"], len(ty["ports"]), caller["stages"]) == (36,0,96,17)
    assert len(ty["diagonal"]) == 36 and all(row[:2] == [-1,0] for row in ty["diagonal"])
    alpha = Q(ty["alpha2"])
    assert alpha == -1 and not Q(ty["beta2"])
    queries = {}
    j_rows = []
    for index, event in enumerate(caller["events"]):
        if event[:2] == ["A","QUERY"]:
            dst, src, power = event[2:]
            assert 0 <= dst < 36 and 0 <= src < 36 and dst != src and power%2
            queries[index] = {"destination": dst, "source": src, "q_power": power,
                              "relative_defect_rank": 1}
        elif event[0] == "J":
            j_rows.append({"stage": event[1], "axes": event[2], "relative_defect_rank": 2,
                           "plus_identity_restricted_rank": 2,
                           "relative_defect_entries": relative_shears(event[2],alpha)})
    assert len(queries) == 4 and [r["stage"] for r in j_rows] == list(range(1,18))
    good_plus, good_minus = identity(36), identity(36,-1)
    assert replay(caller,1,set()) == good_plus
    assert replay(caller,-1,set()) == good_minus
    assert replay(caller,1,set(queries)) == good_plus
    all_subsets = [sub for n in range(1,5) for sub in combinations(queries,n)]
    tested = []
    for subset in all_subsets:
        if time.monotonic()-start >= cap:
            break
        delta = difference(replay(caller,-1,set(subset)),good_minus)
        defect = rank(delta)
        assert defect > 0
        tested.append({"removed": subset, "minus_endpoint_difference_rank": defect,
                       "remaining_defect_rank_budget": 38-len(subset), "proof": reason(subset)})
    return {
        "head": HEAD, "caller_sha256": CALLER, "dimension": 36, "ports": ty["ports"],
        "q_plus_endpoint": "+I", "q_minus_endpoint": "-I", "query_events": queries,
        "relative_j_blocks": j_rows, "proof_census": dict(Counter(map(reason,all_subsets))),
        "mutants": tested, "subsets_tested": len(tested), "unvisited_subsets": all_subsets[len(tested):],
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
    print(json.dumps(audit(json.loads(raw),start,args.cap), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
