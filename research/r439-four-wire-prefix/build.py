#!/usr/bin/env python3
"""Reproduce the seed-11, same-frame, four-wire R439 prefix nomination.

Prepared for Gareth Davidson (@bitplane), with OpenAI Codex assistance.
Exact small-GL/interval method: credit Jeffrey Cox (@namredips), PR754.
Apache-2.0. This nominates circuits; verify.py checks them independently.
"""
import argparse
import collections
import copy
import gzip
from pathlib import Path
import random
import runpy

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))


def tables(n):
    ops = [(d, s) for d in range(n) for s in range(n) if d != s]
    random.Random(11).shuffle(ops)
    unit = tuple(1 << i for i in range(n))
    distance, parent = {unit: 0}, {}
    queue = collections.deque([unit])
    while queue:
        rows = queue.popleft()
        for d, s in ops:
            nxt = list(rows)
            nxt[d] ^= nxt[s]
            nxt = tuple(nxt)
            if nxt not in distance:
                distance[nxt] = distance[rows] + 1
                parent[nxt] = (rows, (d, s))
                queue.append(nxt)
    return distance, parent


def circuit(rows, parent):
    result = []
    while rows in parent:
        rows, op = parent[rows]
        result.append(list(op))
    return result[::-1]


def positive(ops, n):
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    for d, s in ops:
        rows[d] = [x + y for x, y in zip(rows[d], rows[s])]
    return rows


def dominated(new, old):
    return all(x <= y for rn, ro in zip(new, old) for x, y in zip(rn, ro))


def construct(word):
    tab = {n: tables(n) for n in range(2, 5)}
    selected, counts = [], {}
    v = word["v"]
    for section in ("A", "B"):
        flat = [(f, d, s) for f, d, srcs in word[section] for s in srcs]
        scanned = shorter = used = dominant = 0
        found = []
        for i, (f, _, _) in enumerate(flat):
            regs = set()
            for j in range(i, len(flat)):
                ff, dd, ss = flat[j]
                if ff != f or v <= dd < 2 * v or v <= ss < 2 * v:
                    break
                regs.update((dd, ss))
                if len(regs) > 4:
                    break
                if j == i:
                    continue
                scanned += 1
                labels = sorted(regs)
                idx = {r: k for k, r in enumerate(labels)}
                old = [[idx[a], idx[b]] for _, a, b in flat[i:j + 1]]
                rows = [1 << k for k in range(len(regs))]
                for a, b in old:
                    rows[a] ^= rows[b]
                distance, parent = tab[len(regs)]
                if distance[tuple(rows)] >= len(old):
                    continue
                shorter += 1
                new = circuit(tuple(rows), parent)
                if {x for op in new for x in op} != set(range(len(regs))):
                    continue
                used += 1
                if not dominated(positive(new, len(regs)), positive(old, len(regs))):
                    continue
                if not dominated(positive(new[::-1], len(regs)), positive(old[::-1], len(regs))):
                    continue
                dominant += 1
                found.append(dict(section=section, start=i, stop=j + 1, frame=f,
                                  registers=labels, old=old, new=new, saving=len(old) - len(new)))
        ending = collections.defaultdict(list)
        for item in found:
            ending[item["stop"]].append(item)
        dp = [(0, []) for _ in range(len(flat) + 1)]
        for i in range(1, len(dp)):
            dp[i] = dp[i - 1]
            for item in ending[i]:
                score = dp[item["start"]][0] + item["saving"]
                if score > dp[i][0]:
                    dp[i] = (score, dp[item["start"]][1] + [item])
        counts[section] = dict(windows=scanned, shorter=shorter, all_used=used,
                               dominant=dominant, selected=len(dp[-1][1]), saved=dp[-1][0])
        selected.extend(dp[-1][1])
    candidate = copy.deepcopy(word)
    for section in ("A", "B"):
        flat = [[f, d, [s]] for f, d, srcs in word[section] for s in srcs]
        result, position = [], 0
        for item in [x for x in selected if x["section"] == section]:
            result.extend(flat[position:item["start"]])
            result.extend([item["frame"], item["registers"][d], [item["registers"][s]]]
                          for d, s in item["new"])
            position = item["stop"]
        result.extend(flat[position:])
        candidate[section] = result
    full = word["frames"].index(list(range(v)))
    candidate["C"] = [[full, d, srcs[:]] for _, d, srcs in
                      reversed(candidate["A"] + candidate["B"]) if not v <= d < 2 * v]
    certificate = dict(format="r439-prefix/1", seed=11,
                       baseline_sha256=C["digest"](word), candidate_sha256=C["digest"](candidate),
                       group_sizes={str(n): len(pair[0]) for n, pair in tab.items()},
                       counts=counts, selected=selected)
    return candidate, certificate


def run(root, output):
    C["pins"](root)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    word, certificate = construct(C["load"](Path(root) / C["WORD"]))
    C["write"](output / "CERTIFICATE.json", certificate)
    with (output / "candidate.json.gz").open("xb") as stream:
        stream.write(gzip.compress(C["canonical"](word), mtime=0))
    return certificate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=C["ROOT"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = run(args.source_root, args.output)
    print("BUILT_R439_PREFIX", receipt["counts"])
