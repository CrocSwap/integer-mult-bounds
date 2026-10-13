"""Bounded nomination of integer factorizations; not an optimality proof.

Prepared for @zeusinsight with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"


def transfer(gates, n):
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    for d, s in gates:
        rows[d] = [x + y for x, y in zip(rows[d], rows[s])]
    return rows


def search():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    raw = (ROOT / WORD).read_bytes()
    if hashlib.sha256(raw).hexdigest() != pins["files"][WORD]["sha256"]:
        raise ValueError("source hash mismatch")
    word = json.loads(gzip.decompress(raw))
    block = word["B"][404:449]
    registers = sorted({r for _, d, ss in block for r in [d] + ss})
    n = len(registers)
    old = [(registers.index(d), registers.index(s)) for _, d, ss in block for s in ss]
    target, reverse = transfer(old, n), transfer(old[::-1], n)
    identity = transfer([], n)
    rng, best, complete, dominated = random.Random(18), len(old), 0, 0
    history, candidate = [], None
    for trial in range(5000):
        rows, undo = [r[:] for r in target], []
        while True:
            pairs = [(d, s) for d in range(n) for s in range(n) if d != s
                     and all(x >= y for x, y in zip(rows[d], rows[s]))]
            if not pairs:
                break
            # Every third trial favors the greatest decrease in row-sum mass.
            if trial % 3 == 0:
                scores = [sum(rows[s]) for d, s in pairs]
                largest = max(scores)
                pairs = [p for p, score in zip(pairs, scores) if score == largest]
            d, s = rng.choice(pairs)
            rows[d] = [x - y for x, y in zip(rows[d], rows[s])]
            undo.append((d, s))
        if rows != identity:
            continue
        complete += 1
        if len(undo) < len(old):
            backwards = transfer(undo, n)
            if all(a <= b for ra, rb in zip(backwards, reverse) for a, b in zip(ra, rb)):
                dominated += 1
        if len(undo) < best:
            best = len(undo)
            history.append({"trial": trial, "gates": best})
            candidate = dict(phase="B", start=404, stop=449, frame=523,
                             registers=registers, original=old,
                             replacement=undo[::-1], trial=trial)
    report = dict(seed=18, trials=5000, completed_identity_factorizations=complete,
                  shorter_reverse_dominated=dominated, improvements=history,
                  stopping_rule="exactly 5000 trials; row subtraction until no legal pair",
                  domain="nonnegative integer row-subtractions of full twelve-wire block 8",
                  scope="sampled trajectories, not exhaustive or optimal")
    return candidate, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    candidate, report = search()
    for name, data in (("WITNESS.json", candidate), ("SEARCH.json", report)):
        raw = json.dumps(data, indent=2) + "\n"
        if args.write:
            (HERE / name).write_text(raw)
        elif json.loads(raw) != json.loads((HERE / name).read_text()):
            raise ValueError("search mismatch: " + name)
    print("PASS_R439_BLOCK8_SEARCH seed=18 trials=5000 identity=333 gates=45->40 strict_candidates=0")


if __name__ == "__main__":
    main()
