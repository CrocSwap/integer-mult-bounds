"""Exhaust the destination-once schedules of the two fixed positive factors.

Gautam Gupta, with substantial OpenAI Codex assistance. Apache-2.0.
Related fixed-factor R420 schedule research: Yuzhou Wang, PR789.
"""
import argparse
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
REGISTERS = [21, 26, 36, 44, 51, 55, 64, 71, 80, 84, 94, 102]
N = len(REGISTERS)


def transfer(ops):
    rows = [[int(i == j) for j in range(N)] for i in range(N)]
    for a, b in ops:
        rows[a] = [x + y for x, y in zip(rows[a], rows[b])]
    return rows


def solve(ops):
    rows = transfer(ops)
    if not all(x in (0, 1) for row in rows for x in row):
        raise ValueError("not a binary positive factor")
    masks = [sum(x << j for j, x in enumerate(row)) for row in rows]
    distance = [10**9] * (1 << N)
    distance[0] = 0
    previous = {}
    edges = 0
    for done in range(1 << N):
        for dst in range(N):
            if done >> dst & 1:
                continue
            need = masks[dst] ^ (1 << dst)
            cover = {0: ()}
            for src in range(N):
                if src == dst:
                    continue
                donor = masks[src] if done >> src & 1 else (1 << src)
                if donor & ~need:
                    continue
                for covered, chosen in list(cover.items()):
                    if covered & donor:
                        continue
                    new = covered | donor
                    candidate = chosen + (src,)
                    if new not in cover or (len(candidate), candidate) < (len(cover[new]), cover[new]):
                        cover[new] = candidate
            if need not in cover:
                continue
            edges += 1
            nxt = done | (1 << dst)
            candidate = distance[done] + len(cover[need])
            if candidate < distance[nxt]:
                distance[nxt] = candidate
                previous[nxt] = (done, dst, cover[need])
    state = (1 << N) - 1
    batches = []
    while state:
        parent, dst, donors = previous[state]
        batches.append([[dst, src] for src in donors])
        state = parent
    result = [op for batch in reversed(batches) for op in batch]
    if transfer(result) != rows:
        raise RuntimeError("factor mismatch")
    return result, {"minimum": distance[-1], "states": len(distance), "feasible_edges": edges,
                    "target_rows": masks}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    word = json.loads(gzip.decompress(SOURCE.read_bytes()))
    original = [[REGISTERS.index(t), REGISTERS.index(s)]
                for _, t, sources in word["B"][242:283] for s in sources]
    first, a = solve(original[:20])
    second, b = solve(original[20:])
    ops = first + second
    reverse = transfer(list(reversed(ops)))
    old_reverse = transfer(list(reversed(original)))
    dominated = all(x <= y for r, s in zip(reverse, old_reverse) for x, y in zip(r, s))
    result = {"source": SOURCE.relative_to(HERE.parents[1]).as_posix(), "section": "B", "block": 4,
              "frame": 520, "slice": [242, 283], "registers": REGISTERS,
              "original_split": 20, "candidate_split": len(first), "operations": ops,
              "factor_certificates": [a, b], "reverse_dominated": dominated}
    args.output.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    print(f"factor minima {len(first)}+{len(second)}, total {len(ops)}, reverse_dominated={dominated}")


if __name__ == "__main__":
    main()
