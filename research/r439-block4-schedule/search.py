"""Bounded nomination of a positive-integer schedule, not an optimality proof.

Gautam Gupta, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
REGISTERS = [21, 26, 36, 44, 51, 55, 64, 71, 80, 84, 94, 102]


def transfer(ops):
    rows = [[int(i == j) for j in range(12)] for i in range(12)]
    for dst, src in ops:
        rows[dst] = [a + b for a, b in zip(rows[dst], rows[src])]
    return rows


def nominate(rng, target):
    """Strip a left or right positive elementary factor until identity/stuck."""
    rows = [r[:] for r in target]
    left, right = [], []
    while len(left) + len(right) < 41:
        if rows == [[int(i == j) for j in range(12)] for i in range(12)]:
            return right + list(reversed(left))
        choices = []
        for a in range(12):
            for b in range(12):
                if a == b:
                    continue
                if all(x >= y for x, y in zip(rows[a], rows[b])):
                    choices.append((0, a, b, sum(rows[b])))
                if all(r[b] >= r[a] for r in rows):
                    choices.append((1, a, b, sum(r[a] for r in rows)))
        if not choices:
            return None
        # Weighted random choice explores factorizations, favoring large reductions.
        side, a, b, _ = rng.choices(choices, weights=[x[3] for x in choices])[0]
        if side == 0:
            rows[a] = [x - y for x, y in zip(rows[a], rows[b])]
            left.append([a, b])
        else:
            for row in rows:
                row[b] -= row[a]
            right.append([a, b])
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    word = json.loads(gzip.decompress(SOURCE.read_bytes()))
    original = [[REGISTERS.index(t), REGISTERS.index(s)]
                for frame, t, sources in word["B"][242:283] for s in sources]
    target = transfer(original)
    old_reverse = transfer(list(reversed(original)))
    rng = random.Random(4)
    best, completed, dominated = None, 0, 0
    for trial in range(1, 2001):
        ops = nominate(rng, target)
        if ops is None:
            continue
        completed += 1
        if transfer(ops) != target:
            raise RuntimeError("factor reconstruction failed")
        reverse = transfer(list(reversed(ops)))
        if not all(x <= y for r, s in zip(reverse, old_reverse) for x, y in zip(r, s)):
            continue
        dominated += 1
        if best is None or len(ops) < len(best):
            best = ops
            print(f"trial={trial} gates={len(ops)}", flush=True)
        if len(best) <= 30:
            break
    if best is None:
        result = {"status": "NO_REVERSE_DOMINATED_CANDIDATE_FOUND",
                  "source": SOURCE.relative_to(HERE.parents[1]).as_posix(),
                  "block": 4, "seed": 4, "maximum_trials": 2000,
                  "completed_trials": trial, "identity_factorizations_below_41_steps": completed,
                  "reverse_dominated": dominated,
                  "stopping_rule": "first reverse-dominated circuit with <=30 additions, or 2000 trials",
                  "scope": "bounded randomized search failure; not an impossibility theorem"}
        args.output.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
        print(json.dumps(result, sort_keys=True))
        return
    result = {
        "base_commit": "7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261",
        "source": SOURCE.relative_to(HERE.parents[1]).as_posix(),
        "section": "B", "block": 4, "frame": 520, "slice": [242, 283],
        "registers": REGISTERS, "original_additions": len(original), "operations": best,
        "search": {"seed": 4, "maximum_trials": 2000, "completed_trials": trial,
                   "identity_factorizations": completed, "reverse_dominated": dominated,
                   "stopping_rule": "first reverse-dominated circuit with <=30 additions, or 2000 trials"},
    }
    args.output.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(result["search"], sort_keys=True))


if __name__ == "__main__":
    main()
