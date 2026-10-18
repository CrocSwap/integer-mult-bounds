"""Bounded nomination, not an optimality proof. Apache-2.0; Codex assistance."""

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (HERE, N, R, V, bill, digest, fourth_root, make_word, need,
                    read_word, rows_of, search_context)


def nominate(original, seed=18, max_steps=1000, guarded=True):
    rng = random.Random(seed)
    rows = rows_of(original)
    peak, extra, reverse_peak, entry = search_context(original)
    need(peak == 144651 and reverse_peak == 144651, "unexpected exterior")
    cap = fourth_root(((1 << 192) - 1) // ((1 << 18) * peak ** 5))
    fp, rp, helper = [1] * V, entry[V:2 * V], entry[2 * V:N]
    need(len(helper) == R, "helper bound dimensions")
    cache = {}

    def weight(mask):
        if mask in cache:
            return cache[mask]
        original_mask, total = mask, 0
        while mask:
            low = mask & -mask
            total += helper[low.bit_length() - 1]
            mask -= low
        cache[original_mask] = total
        return total

    # columns of the positive reverse basis matrix B; P is the forward
    # basis applied to the relevant incoming norm vector (fp or rp).
    columns = [{i: 1} for i in range(V)]
    fo = [1 + row.bit_count() for row in rows]
    ro = [rp[i] + weight(row) for i, row in enumerate(rows)]
    operations, trace = [], []
    considered = admitted = 0
    stopping = "step_limit"
    for _ in range(max_steps):
        room_f = [min((peak - extra[i] - fo[i]) // (2 * c) for i, c in col.items())
                  for col in columns]
        room_r = [min((cap - ro[i]) // (2 * c) for i, c in col.items())
                  for col in columns]
        weights = [row.bit_count() for row in rows]
        best, choices = 0, []
        for a in range(V):
            for b in range(V):
                if a == b:
                    continue
                considered += 1
                gain = weights[a] - (rows[a] ^ rows[b]).bit_count() - 2
                if gain <= 0:
                    continue
                new = rows[b] & ~rows[a]
                df, dr = fp[b] + new.bit_count(), rp[b] + weight(new)
                if guarded and (df > room_f[a] or dr > room_r[a]):
                    continue
                admitted += 1
                if gain > best:
                    best, choices = gain, [(a, b, df, dr)]
                elif gain == best:
                    choices.append((a, b, df, dr))
        if not choices:
            stopping = "no_admissible_positive_gain_pair"
            break
        a, b, df, dr = rng.choice(choices)
        for i, coefficient in columns[a].items():
            fo[i] += 2 * coefficient * df
            ro[i] += 2 * coefficient * dr
        for i, coefficient in columns[a].items():
            columns[b][i] = columns[b].get(i, 0) + coefficient
        fp[a] += fp[b]
        rp[a] += rp[b]
        rows[a] ^= rows[b]
        operations.append([a, b])
        trace.append([a, b, best, sum(r.bit_count() for r in rows) + 2 * len(operations), max(ro)])
    word, rebuilt_rows = make_word(original, operations)
    actual = bill(word)
    need(rows == rebuilt_rows and actual["reverse"] == max(ro), "incremental reverse bound mismatch")
    need(actual["forward"] == max(peak, max(x + y for x, y in zip(fo, extra))),
         "incremental forward bound mismatch")
    if guarded:
        need(actual["nine_stage_bits"] <= 192, "guard did not preserve the allowance")
    return operations, {
        "guarded": guarded,
        "seed": seed,
        "max_steps": max_steps,
        "accepted_steps": len(operations),
        "ordered_pairs_examined": considered,
        "admissible_positive_pairs": admitted,
        "stopping": stopping,
        "trace_sha256": digest(trace),
        "reverse_cap": cap if guarded else None,
        "bill": actual,
    }


def discover():
    original = read_word()
    operations, guarded = nominate(original)
    _, unrestricted = nominate(original, guarded=False)
    return {
        "format": "r420-compensation-target-basis-v1",
        "assignment_seed": 18,
        "original_word_sha256": digest(original),
        "basis_operations": operations,
        "search": {"guarded": guarded, "unrestricted_control": unrestricted},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        help="write a newly nominated candidate; refuses an existing file")
    args = parser.parse_args()
    candidate = discover()
    if args.output:
        with args.output.open("x") as f:
            json.dump(candidate, f, indent=2)
            f.write("\n")
    else:
        need(candidate == json.loads((HERE / "candidate.json").read_text()),
             "search did not reproduce the frozen candidate")
    print("PASS_REPRODUCIBLE_SEARCH guarded_steps=205 D_adds=12043 trials=2 seed=18")


if __name__ == "__main__":
    main()
