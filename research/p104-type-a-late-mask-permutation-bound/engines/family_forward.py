"""Check profitable Type A late-mask swaps by direct forward propagation."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

HERE = Path(__file__).resolve().parent
N = 36
CUT = 1741
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def unit(i):
    return [Fraction(i == j) for j in range(N)]


def apply(events, column, q, inverse=False):
    col = column.copy()
    direction = -1 if inverse else 1
    for event in reversed(events) if inverse else events:
        if event[0] == "B":
            continue
        if event[0] == "J":
            _, _, (u, v, x, y), _ = event
            assert len({u, v, x, y}) == 4
            col[v] += direction * q * col[u]
            col[x] -= direction * q * col[y]
            continue
        assert event[0] == "A"
        _, op, dest, *args = event
        if op == "ADD":
            src, value = args
            col[dest] += direction * Fraction(value) * col[src]
        elif op == "QUERY":
            src, exponent = args
            assert exponent == -1
            col[dest] += direction * q * col[src]
        elif op == "SWAP":
            src, = args
            col[dest], col[src] = col[src], col[dest]
        elif op == "SCALE":
            value, = args
            col[dest] *= Fraction(value) ** direction
        else:
            assert op in ("IDLE_ONE", "LAMBDA")
    return col


def stop(*_):
    raise TimeoutError("30-second solver cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(30)
    for name, digest in PINS.items():
        assert sha256((HERE / name).read_bytes()).hexdigest() == digest
    caller = loads((HERE / "inputs/CALLER.json").read_bytes())
    old = loads((HERE / "inputs/R92-PRICE.json").read_bytes())
    tape = caller["events"]
    a = caller["types"]["A"]
    assert len(a["ports"]) == 96 and a["roles"] == N and len(tape) == 4783
    assert tape[CUT] == ["A", "ADD", 10, 0, "2"]
    assert all(row[:2] == [-1, 0] for row in a["diagonal"])
    counts = [(sum(row[2:10]), sum(row[10:])) for row in a["diagonal"]]
    pre = tape[:CUT]
    forward, inverse = {}, {}
    for q in (1, -1):
        forward[q] = [apply(pre, unit(i), q) for i in range(N)]
        inverse[q] = [apply(pre, unit(i), q, inverse=True) for i in range(N)]
        for i in range(N):
            assert apply(pre, inverse[q][i], q) == unit(i)
            assert apply(tape, unit(i), q) == [q * entry for entry in unit(i)]
    cases = []
    ranks = Counter()
    for a, b in combinations(range(N), 2):
        x, y = counts[a]
        u, v = counts[b]
        before = sorted((1 + 8*(x+y), 1 + 8*(u+v)))
        after = sorted((1 + 8*(x+v), 1 + 8*(u+y)))
        assert sum(before) == sum(after)
        if after[0] <= before[0]:
            status = "tie" if after == before else "worse"
            ranks[status] += 1
            cases.append([a, b, before, after, status, None])
            continue
        ranks["profitable"] += 1
        vectors = {q: [x-y for x,y in zip(forward[q][a], forward[q][b], strict=True)]
                   for q in (1, -1)}
        duals = {q: [col[a]-col[b] for col in inverse[q]] for q in (1, -1)}
        for q in (1, -1):
            assert sum(x*y for x,y in zip(vectors[q], duals[q], strict=True)) == 2
        # W - I = -(G d)(d^T G^-1), where d = e_a - e_b.
        witness = None
        for i, j in ((i, j) for i in range(N) for j in range(N)):
            odd = vectors[-1][i]*duals[-1][j] - vectors[1][i]*duals[1][j]
            if odd:
                witness = [i, j, str(odd)]
                break
        status = "excluded" if witness else "survives"
        cases.append([a, b, before, after, status, witness])
        ranks[status] += 1
    assert len(cases) == 630
    assert next(case for case in cases if case[:2] == [0, 9])[-1] == [0, 0, "4"]
    cost = run_path(str(HERE / "inputs/pricing.py"))["cost"]
    quote = cost(Counter({73: 192, 137: -96, 9: -96}), Fraction(old["old_crossing_upper"]))
    alarm(0)
    print(dumps({"pins": PINS, "head": old["head"], "cut": CUT,
                 "counts": ranks, "budget_seconds": 30, "cases": cases,
                 "control_pair_0_9_upper": str(quote[1])}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
