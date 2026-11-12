"""Reverse-covector check of one retimed Type A host support."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/PR7404-RESULT.json": "eba0ebfac85759cc9c884b3a12237975ff487c76b17f6095949e80d2fbca60fc",
}
HOST = (8,0,18,26)
CLOCK = 1423
QUERIES = (1580,1659)
N = 36


def load(name):
    raw = (ROOT/name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name]
    return loads(raw)


def right_inverse(row, word, q, body, demote):
    for clock, event in word:
        ty = event[0]
        if ty == "B":
            continue
        if ty == "J":
            _, stage, (u,v,x,y), _ = event
            row[u] -= q * row[v]
            row[y] += q * row[x]
            if stage == 8:
                for role in (u,v,x,y):
                    row[role] /= body
            continue
        _, op, dst, *args = event
        if op == "ADD":
            src, a = args
            row[src] -= Q(a) * row[dst]
        elif op == "QUERY":
            src, phase = args
            assert phase == -1
            a = 1 if demote and clock in QUERIES else q
            row[src] -= a * row[dst]
        elif op == "SCALE":
            row[dst] /= Q(args[0])
        elif op == "SWAP":
            src, = args
            row[dst], row[src] = row[src], row[dst]
        elif op == "IDLE_ONE":
            if 8 in args[0]:
                row[dst] /= body
        else:
            assert op == "LAMBDA"
    return row


def basis(i):
    return [Q(i==j) for j in range(N)]


def required(before, after, q, body, wanted):
    output = []
    for i in range(N):
        row = right_inverse(basis(i), after, q, body, True)
        row = [x * sign for x, sign in zip(row,wanted,strict=True)]
        output.append(right_inverse(row, before, q, body, False))
    return output


def actual_host(q, body):
    table = [basis(i) for i in range(N)]
    u,v,x,y = HOST
    table[v][u] = q
    table[x][y] = -q
    for r in HOST:
        table[r] = [body * a for a in table[r]]
    return table


def stop(*_):
    raise TimeoutError("10-second exact cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(10)
    c = load("inputs/CALLER.json")
    p = load("inputs/PR7404-RESULT.json")
    events = list(enumerate(c["events"]))
    assert p["stage_host"] == CLOCK and sorted(p["queries"]) == list(QUERIES)
    assert events[CLOCK][1][0:3] == ["J",8,list(HOST)]
    skip, moved = set(), []
    for z in p["hoisted_paid_idles"]:
        clock = z["idle"]
        moved.append(events[clock])
        skip.update([clock,*z["canceled_adds"]])
        assert events[clock][1] == ["A","IDLE_ONE",z["role"],z["mask"]]
    assert len(skip) == 42
    before = events[:CLOCK] + moved
    after = [x for x in events[CLOCK+1:] if x[0] not in skip]
    for q in (1,-1):
        for i in range(N):
            assert right_inverse(basis(i), events, q, Q(1), False) == [q*x for x in basis(i)]
    plus = required(before,after,1,Q(1),[1]*N)
    assert plus == actual_host(1,Q(1))
    alt = required(before,after,1,Q(-1),[-1 if d[9] else 1 for d in c["types"]["A"]["diagonal"]])
    assert alt == actual_host(1,Q(-1))
    minus = required(before,after,-1,Q(1),[1 if i in (0,18) else -1 for i in range(N)])
    witness = [[i,j,str(minus[i][j]-plus[i][j])] for i in range(N) for j in range(N)
               if (i not in HOST or j not in HOST) and minus[i][j] != plus[i][j]]
    alarm(0)
    print(dumps({"pins":PINS,"window_host":CLOCK,"host_roles":HOST,"queries":QUERIES,
                 "retired_roles":[0,18],"outside_nonzero_count":len(witness),
                 "first_outside_entries":witness[:12],"plus_body_control":"exact old host at both signs of B8",
                 "hard_cap_seconds":10,"basis_columns":N},sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
