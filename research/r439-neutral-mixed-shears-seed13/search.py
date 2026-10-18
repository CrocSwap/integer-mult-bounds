#!/usr/bin/env python3
"""Exact mixed-neighborhood census on PR967; no supplier/kappa claim.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
Basis-change precedents: Sricharan Vagvala PR967, woklerx PR1040/1047,
Gareth Davidson PR915/926, and Scott Woolsey Biggart PR733.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = "research/r439-helper-stars-seed19/candidate.json.gz"
BASE = "cd91ac8e2652bfee6bf09da3b8724253bcf78f5f"
SEED = 13


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith(".gz") else raw)


def matrix(word):
    if len(word["D"]) != 1165:
        raise ValueError("wrong frozen PR967 D shape")
    core = word["D"][527:638]
    if [g[1] for g in core] != list(range(111, 222)):
        raise ValueError("wrong middle target order")
    rows = []
    for frame, _, sources in core:
        if frame != 0 or len(set(sources)) != len(sources) or not all(222 <= s < 661 for s in sources):
            raise ValueError("wrong middle row")
        rows.append(sum(1 << (s - 222) for s in sources))
    return rows


def correction(x, y, z, t):
    return (x ^ y) + (x ^ z) - (x ^ y ^ z ^ t) - x


def tie(case):
    a, b, d, s = case[:4]
    return hashlib.sha256(f"{SEED}:{a}:{b}:{d}:{s}".encode("ascii")).hexdigest()


def census(rows):
    columns = [sum(1 << i for i, r in enumerate(rows) if (r >> j) & 1) for j in range(439)]
    targets = [(a, b, rows[a].bit_count() - (rows[a] ^ rows[b]).bit_count() - 2)
               for a in range(111) for b in range(111) if a != b]
    helpers = [(d, s, columns[s].bit_count() - (columns[s] ^ columns[d]).bit_count() - 2)
               for d in range(439) for s in range(439) if d != s]
    target_hist = Counter(g for _, _, g in targets)
    helper_hist = Counter(g for _, _, g in helpers)
    # correction <= 2, so a sum <= -2 cannot produce a strict saving.
    near_t = [p for p in targets if -1 <= p[2] <= 0]
    near_h = [p for p in helpers if -1 <= p[2] <= 0]
    cases, survivors = [], Counter()
    for a, b, gt in near_t:
        for d, s, gh in near_h:
            if gt + gh < -1:
                continue
            x, y = (rows[a] >> s) & 1, (rows[b] >> s) & 1
            z, t = (rows[a] >> d) & 1, (rows[b] >> d) & 1
            gain = gt + gh + correction(x, y, z, t)
            survivors[gain] += 1
            if gain > 0:
                cases.append([a, b, d, s, gt, gh, gain])
    cases.sort(key=lambda c: (-c[6], tie(c), c[:4]))
    domain = sum(g <= 0 for _, _, g in targets) * sum(g <= 0 for _, _, g in helpers)
    explicit = sum(survivors.values())
    return {
        "all_target_pairs": len(targets), "all_helper_pairs": len(helpers),
        "target_gain_histogram": {str(k): v for k, v in sorted(target_hist.items())},
        "helper_gain_histogram": {str(k): v for k, v in sorted(helper_hist.items())},
        "nonpositive_unilateral_domain": domain,
        "excluded_by_interaction_upper_bound": domain - explicit,
        "explicit_interaction_cases": explicit,
        "explicit_gain_histogram": {str(k): v for k, v in sorted(survivors.items())},
        "positive_cases": cases, "positive_count": len(cases),
        "positive_cases_sha256": digest(cases),
        "interaction_table": [list(v) + [correction(*v)] for v in itertools.product((0, 1), repeat=4)],
    }


def construct(parent, case, use_target=True, use_helper=True):
    a, b, d, s = case[:4]
    rows = matrix(parent)
    if use_target:
        rows[a] ^= rows[b]
    if use_helper:
        rows = [r ^ (1 << s) if (r >> d) & 1 else r for r in rows]
    preparation = []
    if use_helper:
        preparation.append([0, 222 + d, [222 + s]])
    if use_target:
        preparation.append([0, 111 + a, [111 + b]])
    core = [[0, 111 + i, [222 + j for j in range(439) if (r >> j) & 1]]
            for i, r in enumerate(rows)]
    result = copy.deepcopy(parent)
    result["D"] = (copy.deepcopy(parent["D"][:527]) + preparation + core
                   + copy.deepcopy(preparation[::-1]) + copy.deepcopy(parent["D"][638:]))
    return result


def events(word):
    result = []
    for section in ("D", "A"):
        for _, d, sources in word[section]:
            result.extend(("add", d, s) for s in sources)
    for j, source in enumerate(word["ret"]):
        result.append(("copy", 661, source))
        result.extend(("add", 111 + i, 661) for i, row in enumerate(word["scatter"]) if j in row)
        result.append(("erase", 661, source))
    for section in ("B", "C"):
        for _, d, sources in word[section]:
            result.extend(("add", d, s) for s in sources)
    return result


def invoice(word):
    stream = events(word)
    bounds = []
    for reverse in (False, True):
        values = [1] * 661 + [0]
        maximum = 1
        for kind, d, s in reversed(stream) if reverse else stream:
            if reverse and kind != "add":
                kind = "erase" if kind == "copy" else "copy"
            if kind == "add":
                values[d] += values[s]
            elif kind == "copy":
                values[d] = values[s]
            else:
                values[d] = 0
            maximum = max(maximum, values[d])
        bounds.append(maximum)
    f, b = bounds
    local, nine = 64 * f**3 * b**2, (1 << 18) * f**5 * b**4
    return {"ADDs": sum(k == "add" for k, _, _ in stream),
            "D_ADDs": sum(len(g[2]) for g in word["D"]), "F": f, "B": b,
            "local_bound": str(local), "nine_stage_bound": str(nine),
            "admitted": local < (1 << 104) and nine < (1 << 192)}


def generate():
    parent = load(ROOT / PARENT)
    result = census(matrix(parent))
    trials, winner, candidate = [], None, None
    for index, case in enumerate(result["positive_cases"][:32]):
        word = construct(parent, case)
        bill = invoice(word)
        trials.append({"case": case, "tie_sha256": tie(case), "bill": bill,
                       "word_sha256": digest(word)})
        if winner is None and bill["admitted"]:
            winner, candidate = index, word
    if winner is None:
        raise ValueError("no admitted nominee; do not emit a construction")
    chosen = result["positive_cases"][winner]
    certificate = {"format": "r439-neutral-mixed-shears/1", "base_commit": BASE,
                   "seed": SEED, "census": result, "baseline": invoice(parent),
                   "trials": trials, "winner_index": winner,
                   "winner_single_target": invoice(construct(parent, chosen, use_helper=False)),
                   "winner_single_helper": invoice(construct(parent, chosen, use_target=False)),
                   "candidate_sha256": digest(candidate),
                   "stopping_rule": "complete support census using proved exclusions; price exactly first min(32,positive_count); first admitted; no descent or restart",
                   "no_new_kappa": True}
    return certificate, candidate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate only this package's two artifacts")
    args = parser.parse_args()
    certificate, word = generate()
    if args.write:
        (HERE / "CERTIFICATE.json").write_text(json.dumps(certificate, indent=2) + "\n")
        (HERE / "candidate.json.gz").write_bytes(gzip.compress(canonical(word), mtime=0))
    elif canonical(certificate) != canonical(load(HERE / "CERTIFICATE.json")) or canonical(word) != canonical(load(HERE / "candidate.json.gz")):
        raise ValueError("regenerated certificate or decoded candidate differs")
    print("PASS_R439_NEUTRAL_MIXED_SEARCH", "positive=" + str(certificate["census"]["positive_count"]),
          "trials=" + str(len(certificate["trials"])), "candidate=" + certificate["candidate_sha256"])


if __name__ == "__main__":
    main()
