#!/usr/bin/env python3
"""Bounded, fully charged GL(3,2) replacements of R439 helper pairs.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
The frozen target basis and disjoint-pair predecessor are Gareth Davidson's
PR915 and PR926, extending Scott Woolsey Biggart's PR733 mechanism.
"""
import argparse
from collections import deque
import copy
import gzip
import hashlib
import json
from pathlib import Path
import random
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRE = ROOT / "research/r439-two-sided-compensation"
SEED = 12


def load(path):
    path = Path(path)
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pins():
    for path, expected in load(HERE / "SOURCES.json")["files"].items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected,
                "source pin: " + path)


def group():
    """All maps, with one seed-determined shortest chronological helper word."""
    generators = [(d, s) for d in range(3) for s in range(3) if d != s]
    random.Random(SEED).shuffle(generators)
    words = {(1, 2, 4): []}
    queue = deque(words)
    while queue:
        matrix = queue.popleft()
        for d, s in generators:
            nxt = list(matrix)
            nxt[d] ^= nxt[s]
            nxt = tuple(nxt)
            if nxt not in words:
                words[nxt] = words[matrix] + [(d, s)]
                queue.append(nxt)
    require(len(words) == 168, "GL(3,2) order")
    return words


def input_data():
    parent = load(PRE / "vendor/pr915/candidate.json.gz")
    target_count = len(load(PRE / "vendor/pr915/CERTIFICATE.json")["steps"])
    previous = load(PRE / "CERTIFICATE.json")
    pairs = [(step["a"], step["b"]) for step in previous["steps"]]
    used = {j for pair in pairs for j in pair}
    unused = sorted(set(range(parent["R"])) - used)
    columns = [0] * parent["R"]
    for _, destination, sources in parent["D"][target_count:target_count + parent["v"]]:
        for source in sources:
            columns[source - 2 * parent["v"]] ^= 1 << (destination - parent["v"])
    require((len(pairs), len(unused), target_count) == (192, 55, 306), "input dimensions")
    return parent, target_count, pairs, unused, columns


def inverse_columns(word):
    masks = [1, 2, 4]
    for d, s in word:
        masks[s] ^= masks[d]
    return masks


def candidate(parent, target_count, columns, pairs, replacements):
    operations = []
    for index, pair in enumerate(pairs):
        if index not in replacements:
            operations.append(pair)
        else:
            singleton, word = replacements[index]
            labels = (*pair, singleton)
            operations.extend((labels[d], labels[s]) for d, s in word)
    transformed = list(columns)
    for d, s in operations:
        transformed[s] ^= transformed[d]
    v = parent["v"]
    helpers = [[0, 2 * v + d, [2 * v + s]] for d, s in operations]
    middle = [[0, v + i, [2 * v + j for j, col in enumerate(transformed) if col >> i & 1]]
              for i in range(v)]
    result = copy.deepcopy(parent)
    result["D"] = helpers + parent["D"][:target_count] + middle + parent["D"][target_count + v:] + helpers[::-1]
    return result


def charges(word):
    # Frozen predecessor's macro interpreter. verify.py uses literal events.
    helpers = runpy.run_path(str(PRE / "build.py"))
    forward = helpers["bounds"](word)
    backward = helpers["bounds"](word, True)
    return {"F": forward, "B": backward,
            "D_adds": sum(len(g[2]) for g in word["D"]),
            "native_ADDs": sum(len(g[2]) for sec in "DABC" for g in word[sec]) + sum(map(len, word["scatter"])),
            "local_expression": 64 * forward ** 3 * backward ** 2,
            "nine_stage_expression": (1 << 18) * forward ** 5 * backward ** 4}


def admitted(bill):
    return bill["local_expression"] < 1 << 104 and bill["nine_stage_expression"] < 1 << 192


def nominate():
    pins()
    parent, target_count, pairs, unused, columns = input_data()
    words = group()
    representatives = [(matrix, word, inverse_columns(word)) for matrix, word in sorted(words.items())]
    rng = random.Random(SEED)
    census_hash = hashlib.sha256()
    nominees = []
    scores = 0
    for index, (a, b) in enumerate(pairs):
        for c in unused:
            local = [columns[a], columns[b], columns[c]]
            sums = [0] * 8
            for mask in range(1, 8):
                low = mask & -mask
                sums[mask] = sums[mask ^ low] ^ local[low.bit_length() - 1]
            baseline_cost = 2 + sums[1].bit_count() + sums[3].bit_count() + sums[4].bit_count()
            for matrix, word, masks in representatives:
                cost = 2 * len(word) + sum(sums[mask].bit_count() for mask in masks)
                gain = baseline_cost - cost
                tie = rng.getrandbits(64)
                row = [index, c, list(matrix), gain, tie]
                census_hash.update(canonical(row) + b"\n")
                scores += 1
                if gain > 0:
                    nominees.append((-gain, tie, index, c, matrix, word))
    nominees.sort()
    baseline = candidate(parent, target_count, columns, pairs, {})
    require(digest(baseline) == digest(load(PRE / "candidate.json.gz")), "reconstruct PR926")
    baseline_bill = charges(baseline)
    replacements, taken_singletons, history, rejected = {}, set(), [], []
    conflicts = 0
    for negative_gain, tie, index, c, matrix, word in nominees:
        if index in replacements or c in taken_singletons:
            conflicts += 1
            continue
        trial_replacements = {**replacements, index: (c, word)}
        trial = candidate(parent, target_count, columns, pairs, trial_replacements)
        bill = charges(trial)
        entry = {"pair_index": index, "singleton": c, "matrix": list(matrix),
                 "word": word, "gain": -negative_gain, "bill": bill}
        if not admitted(bill):
            rejected.append(entry)
            continue
        replacements = trial_replacements
        taken_singletons.add(c)
        history.append(entry)
    result = candidate(parent, target_count, columns, pairs, replacements)
    result_bill = charges(result)
    certificate = {"format": "r439-helper-triples/1", "seed": SEED,
                   "group": [{"matrix": list(m), "word": w} for m, w in sorted(words.items())],
                   "pair_count": len(pairs), "singleton_count": len(unused), "scores": scores,
                   "positive_nominees": len(nominees), "census_sha256": census_hash.hexdigest(),
                   "conflicts": conflicts, "rejected": rejected, "accepted": history,
                   "baseline": baseline_bill, "result": result_bill,
                   "saved_ADDs": baseline_bill["native_ADDs"] - result_bill["native_ADDs"],
                   "candidate_sha256": digest(result),
                   "stopping_rule": "one sorted pass through every strict-gain representative; no restart"}
    require(certificate["saved_ADDs"] == sum(x["gain"] for x in history), "disjoint gain accounting")
    return result, certificate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new directory")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    result, certificate = nominate()
    (args.output / "CERTIFICATE.json").write_text(json.dumps(certificate, indent=2) + "\n")
    (args.output / "candidate.json.gz").write_bytes(gzip.compress(canonical(result), mtime=0))
    print(json.dumps({k: certificate[k] for k in ("scores", "positive_nominees", "conflicts", "saved_ADDs", "result")}))
    print("accepted", len(certificate["accepted"]), "rejected", len(certificate["rejected"]))


if __name__ == "__main__":
    main()
