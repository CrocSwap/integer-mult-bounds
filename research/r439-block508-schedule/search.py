"""Deterministic discovery: whole-block single-write minimum for the R439
phase-B block at frame 508 (B[205:242]) of the tuned word, and one achieving
witness program.

Method: forward dynamic programming over realized-register subsets.  Each of
the block's registers is realized once, in some order, from donors that are
either already-realized rows (their final integer values) or not-yet-realized
registers (their entry singletons), each donor used at most once per
realization (doubling-free positive-addition class).  Integer sums must match
the block's forward integer map exactly.  No randomness is used.

This discovery program is NOT imported by verify.py, which rechecks the
minimum with an independently written backward Bellman recursion.

Prepared with help from opencode. Apache-2.0.
"""
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
FRAME = 508
BEGIN, END = 205, 242


def load_word():
    return json.loads(gzip.decompress((ROOT / WORD).read_bytes()))


def block_map(word):
    gates = word["B"][BEGIN:END]
    assert len(gates) == END - BEGIN
    assert all(f == FRAME and len(ss) == 1 for f, _, ss in gates)
    regs = sorted({t for _, t, _ in gates} | {s for _, _, ss in gates for s in ss})
    index = {r: i for i, r in enumerate(regs)}
    pairs = [(index[t], index[s]) for _, t, (s,) in gates]
    n = len(regs)
    cols = []
    for c in range(n):
        values = [1 if i == c else 0 for i in range(n)]
        for dst, src in pairs:
            values[dst] += values[src]
        cols.append(values)
    forward = [list(row) for row in zip(*cols)]
    return regs, pairs, forward


def packed(row):
    assert all(0 <= x < 16 for x in row), "row entry outside base-16 digit range"
    return sum(x << (4 * j) for j, x in enumerate(row))


def forward_minimum(forward):
    """Returns (minimum, predecessor table). Deterministic; no randomness."""
    n = len(forward)
    assert all(forward[i][i] >= 1 for i in range(n))
    wanted = []
    for i in range(n):
        row = list(forward[i])
        row[i] -= 1
        wanted.append(packed(row))
    rows = [packed(row) for row in forward]
    size = 1 << n
    infinity = 10 ** 9
    best = [infinity] * size
    parent = [None] * size
    best[0] = 0
    for mask in range(size):
        if best[mask] == infinity:
            continue
        for i in range(n):
            if mask >> i & 1:
                continue
            goal = wanted[i]
            donors = []
            for d in range(n):
                if d == i:
                    continue
                value = rows[d] if mask >> d & 1 else (1 << (4 * d))
                fits = True
                for j in range(n):
                    if ((value >> (4 * j)) & 15) > ((goal >> (4 * j)) & 15):
                        fits = False
                        break
                if fits:
                    donors.append((d, value))
            sums = {0: (0, ())}
            for d, value in donors:
                for total, (cost, used) in list(sums.items()):
                    merged = total + value
                    overflows = False
                    for j in range(n):
                        if ((merged >> (4 * j)) & 15) > ((goal >> (4 * j)) & 15):
                            overflows = True
                            break
                    if overflows:
                        continue
                    if merged not in sums:
                        sums[merged] = (cost + 1, used + (d,))
            if goal in sums:
                cost, used = sums[goal]
                nxt = mask | (1 << i)
                if best[mask] + cost < best[nxt]:
                    best[nxt] = best[mask] + cost
                    parent[nxt] = (mask, i, used)
    return best[size - 1], parent


def recover(parent, regs):
    n = len(regs)
    mask = (1 << n) - 1
    steps = []
    while mask:
        prev, i, donors = parent[mask]
        steps.append((i, donors))
        mask = prev
    steps.reverse()
    return [[FRAME, regs[i], [regs[d]]] for i, donors in steps for d in donors]


def main():
    word = load_word()
    regs, pairs, forward = block_map(word)
    print("block registers: %s" % (regs,))
    print("original gates: %d" % len(pairs))
    minimum, parent = forward_minimum(forward)
    print("forward single-write minimum: %d" % minimum)
    gates = recover(parent, regs)
    print("witness gates: %d" % len(gates))
    out = {"frame": FRAME, "slice": [BEGIN, END], "registers": regs,
           "original_gates": len(pairs), "minimum": minimum, "gates": gates}
    digest = hashlib.sha256(json.dumps(out, sort_keys=True, separators=(",", ":")).encode())
    print("candidate sha256: %s" % digest.hexdigest())
    if "--write" in sys.argv:
        path = HERE / "CANDIDATE.json"
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("wrote %s" % path)


if __name__ == "__main__":
    main()
