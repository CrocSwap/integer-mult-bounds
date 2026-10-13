#!/usr/bin/env python3
"""Build the frozen exact-matching recipe, with every helper operation charged.

Prepared for Gareth Davidson (@bitplane), with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
import gzip
from pathlib import Path
import runpy

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))
need = C["need"]


def assemble(parent, pairs):
    v, helpers, count = parent["v"], parent["R"], 306
    columns = [0] * helpers
    for _, d, sources in parent["D"][count:count + v]:
        for source in sources:
            columns[source - 2 * v] ^= 1 << (d - v)
    for a, b in pairs:
        columns[b] ^= columns[a]
    preparation = [[0, 2 * v + a, [2 * v + b]] for a, b in pairs]
    middle = [[0, v + i, [2 * v + j for j, col in enumerate(columns) if (col >> i) & 1]]
              for i in range(v)]
    result = copy.deepcopy(parent)
    result["D"] = preparation + parent["D"][:count] + middle + parent["D"][count + v:] + preparation[::-1]
    return result


def positive(word, reverse=False):
    """Macro evaluation; the verifier independently lowers individual instructions."""
    v, n = word["v"], 2 * word["v"] + word["R"]
    values, largest = [1] * n, 1
    sections = ("C", "B", "scatter", "A", "D") if reverse else ("D", "A", "scatter", "B", "C")
    for section in sections:
        if section == "scatter":
            centers = range(len(word["ret"]) - 1, -1, -1) if reverse else range(len(word["ret"]))
            for j in centers:
                for i, row in enumerate(word["scatter"]):
                    if j in row:
                        values[v + i] += values[word["ret"][j]]
                        largest = max(largest, values[v + i])
        else:
            for _, d, sources in (reversed(word[section]) if reverse else word[section]):
                values[d] += sum(values[s] for s in sources)
                largest = max(largest, values[d])
    return largest


def run(root, output):
    C["pins"](root)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    original = C["load"](Path(root) / C["WORD"])
    parent = C["load"](C["HERE"] / "vendor/pr915/candidate.json.gz")
    greedy = C["load"](C["HERE"] / "vendor/pr926/candidate.json.gz")
    nomination = C["load"](C["HERE"] / "NOMINATION.json")
    pairs = nomination["selected_pairs"]
    candidate = assemble(parent, pairs)
    floor_word = assemble(parent, nomination["nominations"][0]["pairs"])
    forward, backward = positive(candidate), positive(candidate, True)
    d_cost = sum(len(g[2]) for g in candidate["D"])
    total = sum(len(g[2]) for section in "DABC" for g in candidate[section]) + sum(map(len, candidate["scatter"]))
    result = dict(format="r439-helper-matching/1", seed=4, baseline_sha256=C["digest"](original),
                  parent_sha256=C["digest"](parent), greedy_sha256=C["digest"](greedy),
                  candidate_sha256=C["digest"](candidate), floor_word_sha256=C["digest"](floor_word),
                  nomination_sha256=C["digest"](nomination), helper_pairs=len(pairs), target_shears=306,
                  D_adds=d_cost, native_ADDs=total, middle_weight=d_cost - 612 - 2 * len(pairs),
                  saved_beyond_parent=13208 - total, saved_beyond_greedy=11980 - total,
                  F=forward, B=backward, payload_bits=(64 * forward ** 3 * backward ** 2).bit_length(),
                  nine_stage_prefix_bits=((1 << 18) * forward ** 5 * backward ** 4).bit_length())
    C["write"](output / "CERTIFICATE.json", result)
    for name, word in (("candidate", candidate), ("floor-word", floor_word)):
        with (output / (name + ".json.gz")).open("xb") as stream:
            stream.write(gzip.compress(C["canonical"](word), mtime=0))
    print("built", len(pairs), "helper pairs; complete ADDs", total,
          "F", forward, "B", backward, "nine-stage bits", result["nine_stage_prefix_bits"], flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=C["ROOT"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.source_root, args.output)
