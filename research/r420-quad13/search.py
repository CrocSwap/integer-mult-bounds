"""Bounded deterministic nomination; not a circuit optimality proof.

Prepared for mtpsl with substantial OpenAI Codex assistance, Apache-2.0.
"""
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent


def transfer(ops, positive=False):
    rows = [[int(i == j) for j in range(6)] for i in range(6)]
    for a, b in ops:
        rows[a] = [x + y if positive else x ^ y
                   for x, y in zip(rows[a], rows[b])]
    return tuple(tuple(r) for r in rows)


def dominated(a, b):
    return all(x <= y for r, s in zip(a, b) for x, y in zip(r, s))


def nominate(original):
    gates = [(a, b) for a in range(6) for b in range(6) if a != b]
    small = {}
    for a in gates:
        small.setdefault(transfer([a]), []).append([a])
        for b in gates:
            small.setdefault(transfer([a, b]), []).append([a, b])
    small[transfer([])] = [[]]
    rng = random.Random(13)
    best = [tuple(g) for g in original]
    history = []
    for _ in range(100):
        cur = list(best)
        for _ in range(1000):
            i = rng.randrange(len(cur) - 2)
            window = cur[i:i + 3]
            legal = [c for c in small.get(transfer(window), [])
                     if dominated(transfer(c, True), transfer(window, True))
                     and dominated(transfer(c[::-1], True), transfer(window[::-1], True))]
            if legal:
                cur[i:i + 3] = min(legal, key=lambda x: (len(x), x))
            else:
                a, b = cur[i:i + 2]
                if a[0] != b[1] and b[0] != a[1]:
                    cur[i:i + 2] = [b, a]
            if len(cur) < len(best):
                best = list(cur)
        history.append(len(best))
    return {"replacement": [list(g) for g in best], "history": history}


if __name__ == "__main__":
    witness = json.loads((HERE / "WITNESS.json").read_text())
    result = nominate(witness["original"])
    if result != {k: witness[k] for k in result}:
        raise SystemExit("REJECT search does not reproduce the frozen nomination")
    print("PASS_QUAD13_SEARCH seed=13 attempts=100000 gates=19->12")
