"""Price and test one #7404 retimed host with two productive q retirements."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "PR7404-RESULT.json": "eba0ebfac85759cc9c884b3a12237975ff487c76b17f6095949e80d2fbca60fc",
    "R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
HOST, QUERIES, BOUND, N = 1423, {1580, 1659}, (8, 0, 18, 26), 36
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PEER_HEAD = "aadd1de3e520cfd1e5b062729bd76f543dc879f4"


def read(name):
    path = ROOT / "inputs" / name
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == PINS[name], name
    return raw


def identity(sign=1):
    return [[Q(sign if i == j else 0) for j in range(N)] for i in range(N)]


def multiply(left, right):
    return [[sum(a * b for a, b in zip(row, col, strict=True) if a and b)
             for col in zip(*right, strict=True)] for row in left]


def difference(left, right):
    return [[a - b for a, b in zip(x, y, strict=True)] for x, y in zip(left, right, strict=True)]


def tape(events, q, body8, demote=False, inverse=False):
    rows = identity()

    def add(dest, src, scale):
        rows[dest] = [a + scale * b for a, b in zip(rows[dest], rows[src], strict=True)]

    def scale(role, multiplier):
        rows[role] = [x * multiplier for x in rows[role]]

    orient = -1 if inverse else 1
    for clock, event in reversed(events) if inverse else events:
        if event[0] == "B":
            continue
        if event[0] == "J":
            _, stage, (u, v, x, y), _ = event
            add(v, u, Q(orient * q))
            add(x, y, Q(-orient * q))
            if stage == 8:
                for role in (u, v, x, y):
                    scale(role, body8)
            continue
        assert event[0] == "A"
        _, op, role, *args = event
        if op == "ADD":
            add(role, args[0], orient * Q(args[1]))
        elif op == "QUERY":
            assert args[1] == -1
            factor = 1 if demote and clock in QUERIES else q
            add(role, args[0], Q(orient * factor))
        elif op == "SCALE":
            scale(role, Q(args[0]) ** orient)
        elif op == "SWAP":
            other, = args
            rows[role], rows[other] = rows[other], rows[role]
        elif op == "IDLE_ONE":
            mask, = args
            if 8 in mask:
                scale(role, body8)
        else:
            assert op == "LAMBDA"
    return rows


def retiming(events, peer):
    assert events[HOST][:3] == ["J", 8, list(BOUND)]
    assert peer["stage_host"] == HOST and set(peer["queries"]) == QUERIES
    assert peer["native_role_binding"] == {"8": 0, "0": 112, "18": 772, "26": 882}
    assert all(events[k] == ["A", "QUERY", 0, 1, -1] for k in QUERIES)
    moved = peer["hoisted_paid_idles"]
    assert len(moved) == 14
    omitted = set()
    hoisted = []
    for item in moved:
        role, mask, clock = item["role"], item["mask"], item["idle"]
        assert HOST < clock <= 1487 and 8 in mask and role not in BOUND
        assert events[clock] == ["A", "IDLE_ONE", role, mask]
        early, late = item["canceled_adds"]
        donor = 0 if role < 18 else 18
        assert HOST < early < late < clock
        assert events[early] == ["A", "ADD", role, donor, "2"]
        assert events[late] == ["A", "ADD", role, donor, "-2"]
        omitted.update((early, late, clock))
        hoisted.append((clock, events[clock]))
    assert len(omitted) == 42
    indexed = list(enumerate(events))
    before = indexed[:HOST] + hoisted
    after = [(i, event) for i, event in indexed[HOST + 1:] if i not in omitted]
    return indexed, before, after


def outside(matrix):
    return [(i, j, value) for i, row in enumerate(matrix)
            for j, value in enumerate(row) if value and (i not in BOUND or j not in BOUND)]


def determinant(matrix):
    work = [row.copy() for row in matrix]
    value = Q(1)
    for col in range(len(work)):
        pivot = next((k for k in range(col, len(work)) if work[k][col]), None)
        if pivot is None:
            return Q(0)
        if pivot != col:
            work[pivot], work[col] = work[col], work[pivot]
            value = -value
        entry = work[col][col]
        value *= entry
        for k in range(col + 1, len(work)):
            ratio = work[k][col] / entry
            work[k] = [a - ratio * b for a, b in zip(work[k], work[col], strict=True)]
    return value


def quote(caller, roots):
    base = json.loads(read("R92-PRICE.json"))
    assert base["head"] == HEAD and base["caller_head"] == CALLER_HEAD
    pricing = ROOT / "inputs" / "pricing.py"
    read("pricing.py")
    cost = run_path(str(pricing))["cost"]
    type_a = caller["types"]["A"]
    ranks = [1 + 8 * sum(row[2:]) for row in type_a["diagonal"]]
    ports = len(type_a["ports"])
    assert type_a["roles"] == N and type_a["alpha2"] == "-1" and ports == 96
    crossing = Q(base["old_crossing_upper"])
    stock = Counter({int(r): n for r, n in base["old_targets"].items()})
    stock.subtract({int(r): n for r, n in base["old_paid"].items()})
    results = {}
    for count in (1, ports):
        delta = Counter({1: 2 * count})
        for root in roots:
            delta[ranks[root]] -= count
            delta[ranks[root] - 1] += count
        assert sum(r * n for r, n in delta.items()) == 0
        edited = stock.copy()
        edited.update(delta)
        results[count] = {
            "signed_histogram_delta": delta,
            "gross_at_crossing_upper": cost(delta, crossing),
            "complete_at_crossing_upper": cost(edited, crossing),
            "complete_at_probe": cost(edited, Q(base["probe"])),
        }
    return {"roots": roots, "target_ranks": [ranks[r] for r in roots], "ports": results}


def stop(*_):
    raise TimeoutError("10-second exact gate cap")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--price-only", action="store_true")
    args = parser.parse_args()
    assert __debug__
    signal(SIGALRM, stop)
    alarm(10)
    caller = json.loads(read("CALLER.json"))
    roots = (0, 18)
    pricing = quote(caller, roots)
    result = {"native_head": HEAD, "caller_head": CALLER_HEAD, "peer_head": PEER_HEAD,
              "caps": {"target_pairs": 1, "phases": 2, "basis_columns": 36, "seconds": 10},
              "host": HOST, "demote_queries": sorted(QUERIES), "price": pricing, "pins": PINS}
    if not args.price_only:
        events = caller["events"]
        assert len(events) == 4783
        indexed, prefix, suffix = retiming(events, json.loads(read("PR7404-RESULT.json")))
        required = {}
        original_host = [(HOST, events[HOST])]
        for q, body8 in ((1, 1), (1, -1), (-1, 1)):
            original = tape(indexed, q, body8)
            if body8 == 1:
                assert original == identity(q)
            pre = tape(prefix, q, body8)
            post = tape(suffix, q, body8)
            j = tape(original_host, q, body8)
            assert multiply(post, multiply(j, pre)) == original
            post_demoted = tape(suffix, q, body8, demote=True)
            inverse_post = tape(suffix, q, body8, demote=True, inverse=True)
            inverse_pre = tape(prefix, q, body8, inverse=True)
            assert multiply(post_demoted, inverse_post) == multiply(pre, inverse_pre) == identity()
            if q == -1:
                for role in roots:
                    original[role] = [-x for x in original[role]]
            need = multiply(inverse_post, multiply(original, inverse_pre))
            assert multiply(post_demoted, multiply(need, pre)) == original
            if q == 1:
                assert need == j
            required[q, body8] = need
        body_delta = difference(required[1, -1], required[1, 1])
        assert not outside(body_delta)
        body_minor = determinant([[body_delta[i][j] for j in BOUND] for i in BOUND])
        assert body_minor
        phase_delta = difference(required[-1, 1], required[1, 1])
        nonzero = outside(phase_delta)
        result.update({"bound": BOUND, "body_minor": body_minor,
                       "outside_nonzero_count": len(nonzero), "first_outside_entries": nonzero[:12],
                       "decision": "EXCLUDED by four-role support" if nonzero else "SURVIVES support only"})
    alarm(0)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
