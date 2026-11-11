"""Modular row and column transport for the fixed Type A one-QUERY/J scope."""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import isqrt
from pathlib import Path
import time

CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
PRIME = 65521
N = 36


def residue(q):
    q = Fraction(q)
    if q.denominator % PRIME == 0:
        raise ValueError("Nonunit scalar denominator")
    return q.numerator*pow(q.denominator, -1, PRIME) % PRIME


def trace(caller):
    gates, queries, j_blocks = [], {}, {}
    ty = caller["types"]["A"]
    assert (ty["roles"], ty["offset"], len(ty["ports"]), caller["stages"]) == (36,0,96,17)
    alpha = residue(ty["alpha2"])
    assert alpha and not residue(ty["beta2"])
    for clock, event in enumerate(caller["events"]):
        kind, op, *args = event
        if kind == "J":
            x, y, u, v = args[0]
            assert len({x,y,u,v}) == 4 and 0 <= min(x,y,u,v) <= max(x,y,u,v) < N
            j_blocks[clock] = (op, (x,y,u,v))
            gates.extend(((clock, "ADD", y, x, -1), (clock, "ADD", u, v, -alpha)))
        elif kind == "A":
            r = args[0]
            assert 0 <= r < N
            if op in ("ADD", "SWAP", "QUERY"):
                s = args[1]
                assert r != s and 0 <= s < N
                if op == "ADD":
                    gates.append((clock, "ADD", r, s, residue(args[2])))
                elif op == "SWAP":
                    gates.append((clock, "SWAP", r, s, 0))
                else:
                    power = args[2]
                    gates.append((clock, "ADD", r, s, -1 if power % 2 else 1))
                    assert power % 2
                    queries[clock] = (r,s)
            elif op == "SCALE":
                factor = residue(args[1])
                if not factor:
                    raise ValueError("Nonunit SCALE inverse")
                gates.append((clock, "SCALE", r, r, factor))
            elif op not in ("LAMBDA", "IDLE_ONE"):
                raise ValueError(op)
    assert len(queries) == 4 and [v[0] for v in j_blocks.values()] == list(range(1,18))
    return gates, queries, j_blocks


def apply_vector(gates, initial, row, inverse, dimension=N):
    vec = [0]*dimension
    vec[initial] = 1
    ordered = reversed(gates) if row != inverse else gates
    for _, op, d, s, c in ordered:
        if op == "ADD":
            coefficient = -c if inverse else c
            target, source = (s,d) if row else (d,s)
            vec[target] = (vec[target] + coefficient*vec[source]) % PRIME
        elif op == "SCALE":
            factor = pow(c, -1, PRIME) if inverse else c
            vec[d] = vec[d]*factor % PRIME
        elif op == "SWAP":
            vec[d], vec[s] = vec[s], vec[d]
        else:
            raise ValueError(op)
    assert any(vec)
    return vec


def transport(gates, d, s, j_before, dimension=N):
    return (apply_vector(gates, d, False, j_before, dimension),
            apply_vector(gates, s, True, not j_before, dimension))


def outside(vector, allowed):
    return next(([i, c] for i, c in enumerate(vector) if i not in allowed and c), None)


def outside_entry(write, read, bad_write, bad_read):
    if bad_write is not None:
        i = bad_write[0]
        j = next(j for j, v in enumerate(read) if v)
    elif bad_read is not None:
        i = next(i for i, v in enumerate(write) if v)
        j = bad_read[0]
    else:
        return None
    return [i, j, (-2*write[i]*read[j]) % PRIME]


def controls():
    local = [(0,"ADD",1,0,1), (1,"SCALE",0,0,residue("3/2"))]
    before = transport(local,0,1,True,4)
    after = transport(local,0,1,False,4)
    assert before == ([residue("2/3"),residue("-2/3"),0,0], [1,1,0,0])
    assert after == ([residue("3/2"),1,0,0], [residue("-2/3"),1,0,0])
    assert all(outside(vec,{0,1}) is None for vec in before+after)
    write_gate = [(0,"ADD",3,0,1)]
    read_gate = [(0,"ADD",1,3,1)]
    for order in (True,False):
        write, read = transport(write_gate,0,1,order,4)
        assert outside(write,{0,1}) == [3,PRIME-1 if order else 1] and outside(read,{0,1}) is None
        write, read = transport(read_gate,0,1,order,4)
        assert outside(read,{0,1}) == [3,1 if order else PRIME-1] and outside(write,{0,1}) is None
    return {"local_in_support_both_orders":True, "outside_write_both_orders":True, "outside_read_both_orders":True}


def audit(caller, start, cap):
    assert all(PRIME % d for d in range(2,isqrt(PRIME)+1))
    gates, queries, j_blocks = trace(caller)
    scope = list(product(queries,j_blocks))
    records = []
    for query, clock in scope:
        if time.monotonic()-start >= cap:
            break
        d,s = queries[query]
        stage, roles = j_blocks[clock]
        lower, upper = sorted((query,clock))
        middle = [gate for gate in gates if lower < gate[0] < upper]
        write, read = transport(middle,d,s,clock < query)
        bad_write, bad_read = outside(write,roles), outside(read,roles)
        witness = outside_entry(write,read,bad_write,bad_read)
        if witness is not None:
            assert witness[2]
        status = ("both" if bad_write and bad_read else "write" if bad_write else
                  "read" if bad_read else "unresolved")
        records.append({
            "query_clock":query, "query_destination":d, "query_source":s, "j_clock":clock,
            "j_stage":stage, "j_roles":roles, "j_before_query":clock < query,
            "outside_write_residue":bad_write, "outside_read_residue":bad_read,
            "outside_relative_entry_residue":witness, "status":status,
        })
    return {
        "head":HEAD, "caller_sha256":CALLER, "field_prime":PRIME, "dimension":N,
        "checked_elementary_factors":len(gates), "scope_pairs":len(scope), "tested_pairs":len(records),
        "unvisited":scope[len(records):], "status_counts":dict(Counter(r["status"] for r in records)),
        "records":records, "controls":controls(),
    }


def main():
    start = time.monotonic()
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caller", type=Path, required=True)
    parser.add_argument("--cap", type=float, default=22)
    args = parser.parse_args()
    assert 0 < args.cap <= 22
    raw = args.caller.read_bytes()
    if sha256(raw).hexdigest() != CALLER:
        raise ValueError("Changed caller bytes")
    print(json.dumps(audit(json.loads(raw),start,args.cap),indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
