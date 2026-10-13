#!/usr/bin/env python3
"""One guarded disjoint helper-pair pass around the frozen PR915 target basis.

Prepared for Gareth Davidson (@bitplane), with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
import gzip
from pathlib import Path
import random
import runpy

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))
need = C["need"]


def assemble(parent, count, columns, pairs):
    result = copy.deepcopy(parent)
    v = parent["v"]
    helpers = [[0, 2 * v + a, [2 * v + b]] for a, b in pairs]
    middle = [[0, v + i, [2 * v + j for j, col in enumerate(columns) if (col >> i) & 1]]
              for i in range(v)]
    result["D"] = helpers + parent["D"][:count] + middle + parent["D"][count + v:] + helpers[::-1]
    return result


def bounds(word, reverse=False):
    """Direct macro interpreter; the verifier separately lowers literal instructions."""
    v, n = word["v"], 2 * word["v"] + word["R"]
    values, peak = [1] * n, 1
    sections = ("C", "B", "scatter", "A", "D") if reverse else ("D", "A", "scatter", "B", "C")
    for section in sections:
        if section == "scatter":
            centers = range(len(word["ret"]) - 1, -1, -1) if reverse else range(len(word["ret"]))
            for j in centers:
                copied = values[word["ret"][j]]
                for i, row in enumerate(word["scatter"]):
                    if j in row:
                        values[v + i] += copied
                        peak = max(peak, values[v + i])
        else:
            gates = reversed(word[section]) if reverse else word[section]
            for _, destination, sources in gates:
                values[destination] += sum(values[s] for s in sources)
                peak = max(peak, values[destination])
    return peak


def admitted(forward, backward):
    return (64 * forward ** 3 * backward ** 2 < 1 << 104
            and (1 << 18) * forward ** 5 * backward ** 4 < 1 << 192)


def run(root, output):
    C["pins"](root)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    original = C["load"](Path(root) / C["WORD"])
    parent = C["load"](C["HERE"] / "vendor/pr915/candidate.json.gz")
    parent_cert = C["load"](C["HERE"] / "vendor/pr915/CERTIFICATE.json")
    m, v, helpers = len(parent_cert["steps"]), parent["v"], parent["R"]
    need((v, helpers, m) == (111, 439, 306), "frozen parent dimensions")
    columns = [0] * helpers
    for frame, d, sources in parent["D"][m:m + v]:
        need(frame == 0 and v <= d < 2 * v, "parent injection")
        for source in sources:
            need(2 * v <= source < 2 * v + helpers, "parent helper source")
            columns[source - 2 * v] ^= 1 << (d - v)
    rng, census, positive = random.Random(5), [], []
    for a in range(helpers):
        for b in range(helpers):
            if a == b:
                continue
            gain = columns[b].bit_count() - (columns[b] ^ columns[a]).bit_count() - 2
            tie = rng.getrandbits(64)
            census.append([a, b, gain, tie])
            if gain > 0:
                positive.append((-gain, tie, a, b))
    positive.sort()
    used, accepted, history, skipped, rejected = set(), [], [], 0, []
    for neg_gain, tie, a, b in positive:
        if a in used or b in used:
            skipped += 1
            continue
        trial_cols = list(columns)
        trial_cols[b] ^= trial_cols[a]
        trial_pairs = accepted + [(a, b)]
        trial = assemble(parent, m, trial_cols, trial_pairs)
        forward, backward = bounds(trial), bounds(trial, True)
        if not admitted(forward, backward):
            rejected.append(dict(a=a, b=b, gain=-neg_gain, F=forward, B=backward))
            continue
        columns, accepted = trial_cols, trial_pairs
        used.update((a, b))
        history.append(dict(a=a, b=b, gain=-neg_gain, F=forward, B=backward,
                            middle_weight=sum(x.bit_count() for x in columns)))
    candidate = assemble(parent, m, columns, accepted)
    forward, backward = bounds(candidate), bounds(candidate, True)
    d_cost = sum(len(g[2]) for g in candidate["D"])
    total = sum(len(g[2]) for section in "DABC" for g in candidate[section]) + sum(map(len, candidate["scatter"]))
    certificate = dict(format="r439-two-sided/1", seed=5, baseline_sha256=C["digest"](original),
                       parent_sha256=C["digest"](parent), candidate_sha256=C["digest"](candidate),
                       census_sha256=C["digest"](census), pair_scores=len(census), positive_pairs=len(positive),
                       max_pair_gain=max(-p[0] for p in positive), overlap_skips=skipped,
                       guard_rejections=rejected, steps=history, target_shears=m,
                       helper_pairs=len(accepted), middle_weight=sum(x.bit_count() for x in columns),
                       D_adds=d_cost, native_ADDs=total, saved_beyond_parent=13208 - total,
                       F=forward, B=backward, payload_bits=(64 * forward ** 3 * backward ** 2).bit_length(),
                       nine_stage_prefix_bits=((1 << 18) * forward ** 5 * backward ** 4).bit_length(),
                       stopping_reason="completed one sorted disjoint greedy pass on all positive ordered pairs")
    C["write"](output / "CERTIFICATE.json", certificate)
    with (output / "candidate.json.gz").open("xb") as stream:
        stream.write(gzip.compress(C["canonical"](candidate), mtime=0))
    print("built", len(accepted), "helper pairs; D", d_cost, "total ADDs", total,
          "F", forward, "B", backward, "nine-stage bits", certificate["nine_stage_prefix_bits"], flush=True)
    return certificate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=C["ROOT"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.source_root, args.output)
