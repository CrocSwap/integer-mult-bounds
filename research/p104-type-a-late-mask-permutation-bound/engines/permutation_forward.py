"""Bound all phase-even late-mask permutations at Type A cut 1741."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from math import factorial, prod
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

HERE = Path(__file__).resolve().parent
BRANCH_CAP = 20_000


class SearchCap(Exception):
    pass


def timeout(*_):
    raise SearchCap("runner cap")


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(60)
    forward = run_path(str(HERE / "family_forward.py"))
    assert sha256((HERE / "family_forward.py").read_bytes()).hexdigest() == FORWARD_HASH
    pins = forward["PINS"]
    for name, digest in pins.items():
        assert sha256((HERE / name).read_bytes()).hexdigest() == digest
    caller = loads((HERE / "inputs/CALLER.json").read_bytes())
    base = loads((HERE / "inputs/R92-PRICE.json").read_bytes())
    cut, n = forward["CUT"], forward["N"]
    tape = caller["events"]
    assert tape[cut] == ["A", "ADD", 10, 0, "2"] and len(tape) == 4783
    a = caller["types"]["A"]
    assert len(a["ports"]) == 96 and a["roles"] == n
    assert all(d[:2] == [-1, 0] for d in a["diagonal"])
    counts = [(sum(d[2:10]), sum(d[10:])) for d in a["diagonal"]]
    unit, apply = forward["unit"], forward["apply"]
    pre = tape[:cut]
    relative = []
    for j in range(n):
        v = apply(pre, unit(j), 1)
        relative.append(apply(pre, v, -1, inverse=True))
        assert apply(pre, relative[-1], -1) == v
    h = [list(row) for row in zip(*relative, strict=True)]
    # Every H-automorphism preserves loops and the multiset of directed
    # two-edge colours to every already invariant class.
    classes = [tuple(range(n))]
    rounds = []
    while True:
        refined = []
        for group in classes:
            buckets = {}
            for i in group:
                signature = (h[i][i], tuple(tuple(sorted(Counter((h[i][j], h[j][i]) for j in other).items()))
                                              for other in classes))
                buckets.setdefault(signature, []).append(i)
            refined.extend(tuple(bucket) for bucket in buckets.values())
        rounds.append(list(map(len, refined)))
        if refined == classes:
            break
        classes = refined
    old = [1+8*(x+y) for x,y in counts]
    optimistic = [1+8*(x+y)
                  for group in classes
                  for x,y in zip(sorted(counts[j][0] for j in group),
                                 sorted((counts[j][1] for j in group), reverse=True), strict=True)]
    assert sum(old) == sum(optimistic)
    cost = run_path(str(HERE / "inputs/pricing.py"))["cost"]
    k = Fraction(base["old_crossing_upper"])

    def quote(new):
        bill = Counter(new)
        bill.subtract(old)
        return cost(Counter({r: 96*v for r,v in bill.items() if v}), k)

    admissible = prod(factorial(len(g)) for g in classes)
    if Counter(old) == Counter(optimistic):
        upper = (Fraction(0), Fraction(0))
    else:
        upper = quote(optimistic)
    assert upper[1] >= 0
    attempts = 0
    full = 0
    best = None
    stop = "zero productive gain at class upper"
    if upper[1] > 0:
        targets = {j: g for g in classes for j in g}
        order = sorted(range(n), key=lambda j: (len(targets[j]), j))
        assigned = {}
        used = set()

        def visit(depth):
            nonlocal attempts, full, best
            if depth == n:
                full += 1
                ranks = [1+8*(counts[j][0]+counts[assigned[j]][1]) for j in range(n)]
                if Counter(ranks) == Counter(old):
                    return
                saving = quote(ranks)
                if saving[0] > 0 and (best is None or saving[0] > best[0][0]):
                    best = (saving, [assigned[j] for j in range(n)], ranks)
                return
            i = order[depth]
            for j in targets[i]:
                if j in used:
                    continue
                if attempts == BRANCH_CAP:
                    raise SearchCap("assignment cap")
                attempts += 1
                if h[i][i] != h[j][j]:
                    continue
                if any(h[i][u] != h[j][v] or h[u][i] != h[v][j] for u,v in assigned.items()):
                    continue
                assigned[i] = j
                used.add(j)
                visit(depth+1)
                del assigned[i]
                used.remove(j)

        try:
            visit(0)
            stop = "exhausted"
        except SearchCap as err:
            stop = str(err)
    alarm(0)
    print(dumps({"head": base["head"], "caller": base["caller_head"], "cut": cut,
                 "classes": classes, "round_sizes": rounds,
                 "class_permutation_upper": admissible, "compatible_optimal_ranks": sorted(optimistic),
                 "old_ranks": sorted(old), "class_gross": [str(x) for x in upper],
                 "assignments_visited": attempts, "full_automorphisms": full, "best": best,
                 "stop": stop, "assignment_cap": BRANCH_CAP, "runner_cap_seconds": 60,
                 "pins": pins | {"family_forward.py": FORWARD_HASH}}, default=str, indent=2, sort_keys=True))


FORWARD_HASH = "4ad876916978676b47350ad8c88c496a6b8761f52cf4a60b4d2e3595cbba7ffb"
if __name__ == "__main__":
    main()
