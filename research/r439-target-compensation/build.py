#!/usr/bin/env python3
"""Seed-10 guarded target-row nomination for selected PR589 compensation.

Prepared for Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance.
Credit commdata2338 PR794 for guarded target-basis search; see NOTICE.md.
Apache-2.0. Independent acceptance is in verify.py.
"""
import argparse
import copy
import gzip
import math
from pathlib import Path
import random
import runpy

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))
need = C["need"]


def events(word, sections):
    v, temp = word["v"], 2 * word["v"] + word["R"]
    output = []
    for section in sections:
        if section == "scatter":
            for k, center in enumerate(word["ret"]):
                output.append(("copy", temp, center))
                output.extend(("add", v + t, temp) for t, row in enumerate(word["scatter"]) if k in row)
                output.append(("erase", temp, center))
        else:
            output.extend(("add", d, s) for _, d, sources in word[section] for s in sources)
    return output


def positive(instructions, size, reverse=False, values=None):
    values = [1] * size if values is None else values[:]
    peak = max(values)
    for op, d, s in (reversed(instructions) if reverse else instructions):
        if reverse and op != "add":
            op = "erase" if op == "copy" else "copy"
        if op == "add":
            values[d] += values[s]
        elif op == "copy":
            values[d] = values[s]
        else:
            values[d] = 0
        peak = max(peak, values[d])
    return values, peak


def weighted(bits, weights):
    total = 0
    while bits:
        low = bits & -bits
        bits -= low
        total += weights[low.bit_length() - 1]
    return total


def construct(word):
    v, helpers = word["v"], word["R"]
    n = 2 * v + helpers
    tail = events(word, ("A", "scatter", "B", "C"))
    need(all(not v <= s < 2 * v for op, _, s in tail if op == "add"), "tail reads a target")
    start = [1] * (n + 1)
    start[v:2 * v] = [0] * v
    forward_tail, fixed_forward = positive(tail, n + 1, values=start)
    beta = forward_tail[v:2 * v]
    reverse_tail, fixed_reverse = positive(tail, n + 1, reverse=True)
    helper_weights = reverse_tail[2 * v:n]
    rows = [0] * v
    for frame, d, sources in word["D"]:
        need(frame == 0 and v <= d < 2 * v and all(2 * v <= s < n for s in sources), "original D shape")
        for s in sources:
            rows[d - v] ^= 1 << (s - 2 * v)
    weights = [row.bit_count() for row in rows]
    u_forward, u_reverse = [1] * v, reverse_tail[v:2 * v]
    out_forward = [1 + weight for weight in weights]
    out_reverse = [u_reverse[i] + weighted(rows[i], helper_weights) for i in range(v)]
    forward = max(fixed_forward, max(x + y for x, y in zip(out_forward, beta)))
    reverse = max(fixed_reverse, max(out_reverse))
    need((forward, reverse) == (49347, 1113070), "baseline positive bounds")
    forward_cap = forward
    reverse_cap = min(math.isqrt(((1 << 104) - 1) // (64 * forward_cap ** 3)),
                      math.isqrt(math.isqrt(((1 << 192) - 1) // ((1 << 18) * forward_cap ** 5))))
    columns = [[int(i == j) for i in range(v)] for j in range(v)]
    order = [(d, s) for d in range(v) for s in range(v) if d != s]
    random.Random(10).shuffle(order)
    steps = []
    scores = positive_pairs = forward_rejections = reverse_rejections = 0
    for _ in range(1000):
        cap_forward = [min((forward_cap - beta[i] - out_forward[i]) // z
                           for i, z in enumerate(col) if z) for col in columns]
        cap_reverse = [min((reverse_cap - out_reverse[i]) // z
                           for i, z in enumerate(col) if z) for col in columns]
        nominees = []
        for tie, (d, s) in enumerate(order):
            scores += 1
            gain = weights[d] - (rows[d] ^ rows[s]).bit_count() - 2
            if gain <= 0:
                continue
            positive_pairs += 1
            delta_forward = 2 * (u_forward[s] + (rows[s] & ~rows[d]).bit_count())
            if delta_forward > cap_forward[d]:
                forward_rejections += 1
                continue
            nominees.append((-gain, tie, d, s, delta_forward))
        accepted = None
        for negative_gain, _, d, s, delta_forward in sorted(nominees):
            delta_reverse = 2 * (u_reverse[s] + weighted(rows[s] & ~rows[d], helper_weights))
            if delta_reverse > cap_reverse[d]:
                reverse_rejections += 1
                continue
            accepted = (d, s, -negative_gain, delta_forward, delta_reverse)
            break
        if accepted is None:
            stopping_reason = "no admissible strict-gain ordered pair"
            break
        d, s, gain, delta_forward, delta_reverse = accepted
        col = columns[d]
        out_forward = [x + delta_forward * z for x, z in zip(out_forward, col)]
        out_reverse = [x + delta_reverse * z for x, z in zip(out_reverse, col)]
        columns[s] = [x + y for x, y in zip(columns[s], col)]
        rows[d] ^= rows[s]
        weights[d] = rows[d].bit_count()
        u_forward[d] += u_forward[s]
        u_reverse[d] += u_reverse[s]
        steps.append(dict(destination=d, source=s, gain=gain, delta_forward=delta_forward,
                          delta_reverse=delta_reverse,
                          F=max(fixed_forward, max(x + y for x, y in zip(out_forward, beta))),
                          B=max(fixed_reverse, max(out_reverse))))
    else:
        stopping_reason = "1000 accepted-step cap"
    candidate = copy.deepcopy(word)
    entrance = [[0, v + step["destination"], [v + step["source"]]] for step in steps]
    injections = [[0, v + i, [2 * v + j for j in range(helpers) if row >> j & 1]] for i, row in enumerate(rows)]
    candidate["D"] = entrance + injections + entrance[::-1]
    full = events(candidate, ("D", "A", "scatter", "B", "C"))
    _, forward = positive(full, n + 1)
    _, reverse = positive(full, n + 1, reverse=True)
    need(steps and (forward, reverse) == (steps[-1]["F"], steps[-1]["B"]), "incremental/full prefix mismatch")
    certificate = dict(format="r439-compensation/1", seed=10, steps=steps, stopping_reason=stopping_reason,
                       forward_cap=forward_cap, reverse_cap=reverse_cap,
                       pair_scores=scores, positive_pairs=positive_pairs,
                       forward_rejections=forward_rejections, reverse_rejections=reverse_rejections,
                       D_adds=sum(len(g[2]) for g in candidate["D"]),
                       native_ADDs=sum(op == "add" for op, _, _ in full), F=forward, B=reverse,
                       payload_bits=(64 * forward ** 3 * reverse ** 2).bit_length(),
                       nine_stage_prefix_bits=((1 << 18) * forward ** 5 * reverse ** 4).bit_length(),
                       baseline_sha256=C["digest"](word), candidate_sha256=C["digest"](candidate))
    return candidate, certificate


def run(root, output):
    C["pins"](root)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    candidate, certificate = construct(C["load"](Path(root) / C["WORD"]))
    C["write"](output / "CERTIFICATE.json", certificate)
    with (output / "candidate.json.gz").open("xb") as stream:
        stream.write(gzip.compress(C["canonical"](candidate), mtime=0))
    return certificate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=C["ROOT"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    certificate = run(args.source_root, args.output)
    print("BUILT_R439_COMPENSATION", len(certificate["steps"]), "steps; D", certificate["D_adds"],
          "ADDs", certificate["native_ADDs"], "prefix", certificate["nine_stage_prefix_bits"])
