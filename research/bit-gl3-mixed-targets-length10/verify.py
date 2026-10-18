#!/usr/bin/env python3
"""Exact minima for the 916 open mixed GL3 target pairs of seed18.

Quick mode (default, stdlib only, a few seconds): rebuild GL_3(F2) and its
coordinate-CNOT distances, re-derive the 916 open pairs, check every recorded
witness word in the full formal algebra M_2(F2[GL_3(F2)]), check the direct
twelve-call words, bind the recorded receipt to seed18's pinned certificate and
reject tampered witnesses.

Full mode (--full): additionally compile engine.cpp (C++17) and rerun the
exhaustive radius-5 join plus the length-11 stage, and require its complete
output to equal RESULT.json. That run is the lower-bound evidence; quick mode
only checks its recorded output and the upper-bound words.

Session 32 for Josie Elliston, with Claude Code. Apache-2.0.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED18 = ROOT / "research" / "bit-gl3-mixed-targets-seed18" / "CERTIFICATE.json"
ID3 = 0b100010001
LABELS = [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]
RECEIPT = {  # complete engine receipt; --full recomputes every entry
    "address_layers": [1, 6, 24, 51, 60, 24, 2],
    "ball4_layers": [1, 36, 996, 25518, 636945], "ball4_states": 663496,
    "raw_layer5_images": 22930020, "records_before_dedupe": 22188112,
    "layer5_distinct": 15628866, "ball5_states": 16292362,
    "key_buckets": 3137495, "key_buckets_meeting_ball4": 133207, "largest_bucket": 5011,
    "ordered_pairs": 1119282418, "radius4_table_mismatches": 0,
    "pairs_direct_le9": 27308, "pairs_direct_ge10": 916,
    "l11_targets": 100, "l11_images": 562639176,
    "l11_images_meeting_ball5_keys": 282223416, "l11_hits": 1169568,
}


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def mul3(a, b):
    out = 0
    for r in range(3):
        v = 0
        for c in range(3):
            if a >> (3 * r + c) & 1:
                v ^= (b >> (3 * c)) & 7
        out |= v << (3 * r)
    return out


def address_distances():
    labels = [ID3 ^ (1 << (3 * i + j)) for i, j in LABELS]
    dist, queue = {ID3: 0}, [ID3]
    for g in queue:
        for x in labels:
            t = mul3(x, g)
            if t not in dist:
                dist[t] = dist[g] + 1
                queue.append(t)
    require(len(dist) == 168, "GL3(F2) has 168 elements")
    return dist


def translate(p, g):
    """Left multiplication [g] * p; p is a bitmask over 9-bit group encodings."""
    out = 0
    while p:
        low = p & -p
        p ^= low
        out ^= 1 << mul3(g, low.bit_length() - 1)
    return out


def apply_word(word):
    """Apply paid calls left to right: state <- (I + ([g]+[e]) u v^T) state."""
    e = 1 << ID3
    a, b, c, d = e, 0, 0, e
    for u, v, i, j in word:
        require(u in (1, 2, 3) and v in (1, 2, 3) and bin(u & v).count("1") % 2 == 1,
                "scalar factor must be a binary rank-one idempotent")
        require(i != j and 0 <= i < 3 and 0 <= j < 3, "label must be a coordinate CNOT")
        g = ID3 ^ (1 << (3 * i + j))
        x = (a if v & 1 else 0) ^ (c if v & 2 else 0)
        y = (b if v & 1 else 0) ^ (d if v & 2 else 0)
        x ^= translate(x, g)
        y ^= translate(y, g)
        if u & 1:
            a, b = a ^ x, b ^ y
        if u & 2:
            c, d = c ^ x, d ^ y
    return a, b, c, d


def parse_word(tokens):
    return [tuple(int(ch) for ch in t) for t in tokens]


def direct_word(a, b, dist):
    """Shortest coordinate-CNOT words for a and b on registers 1 and 2."""
    labels = [ID3 ^ (1 << (3 * i + j)) for i, j in LABELS]

    def path(target):
        out, g = [], target
        while g != ID3:
            for k, x in enumerate(labels):
                prev = mul3(x, g)  # x is an involution: g = x * prev
                if dist.get(prev) == dist[g] - 1:
                    out.append(k)
                    g = prev
                    break
        return out[::-1]  # applied first to last

    return ([(1, 1, *LABELS[k]) for k in path(a)]
            + [(2, 2, *LABELS[k]) for k in path(b)])


def parse_output(text):
    receipt, pairs, l11, hist = {}, [], [], []
    for line in text.splitlines():
        f = line.split()
        if not f or f[0] == "DONE":
            continue
        if f[0] == "pair":
            row = {"a": int(f[1]), "b": int(f[2]), "direct": int(f[4]), "min_le10": int(f[6])}
            if len(f) > 7:
                require(f[7] == "word", "malformed pair line")
                row["word"] = f[8:]
            pairs.append(row)
        elif f[0] == "l11":
            row = {"a": int(f[2]), "b": int(f[3]), "direct": int(f[5]), "min_le11": int(f[7])}
            if len(f) > 8:
                require(f[8] == "word", "malformed l11 line")
                row["word"] = f[9:]
            l11.append(row)
        elif f[0] == "histogram":
            hist.append([int(f[2]), int(f[4]), int(f[6])])
        else:
            receipt[f[0]] = [int(x) for x in f[1:]] if len(f) > 2 else int(f[1])
    require("l11_hits" in receipt, "engine output is missing the length-11 stage")
    return {"receipt": receipt, "histogram": hist, "pairs": pairs, "l11": l11}


def quick(result):
    dist = address_distances()
    layers = [0] * 7
    for v in dist.values():
        layers[v] += 1
    require(layers == [1, 6, 24, 51, 60, 24, 2], "address Cayley layers")
    rec = result["receipt"]
    require(rec["address_layers"] == layers, "receipt address layers")

    # bind to seed18's pinned certificate: same ball and same coset count
    cert = json.loads(SEED18.read_text())
    require(rec["ball4_layers"] == cert["formal"]["layers"] == [1, 36, 996, 25518, 636945],
            "ball-4 layers agree with seed18")
    require(rec["ball4_states"] == cert["formal"]["states"] == 663496, "ball-4 states")
    require(rec["key_buckets_meeting_ball4"] == cert["formal"]["cosets"] == 133207, "ball-4 cosets")
    require(rec["radius4_table_mismatches"] == 0, "radius-4 join reproduces seed18's table")
    require(rec == RECEIPT, "recorded engine receipt")
    require(sorted(result["histogram"]) == [[10, 10, 816], [11, 11, 96], [12, 11, 4]],
            "recorded radius-5 histogram")
    require(len(result["pairs"]) == 916 and len(result["l11"]) == 100, "no duplicate rows")
    cov = cert["completed_coverage"]
    require(cov["remaining_direct_cost_10_to_12"] == 916 and cov["remaining_lower_bound"] == 9,
            "seed18 open pairs and lower bound")
    hist = cert["direct_pair_cost_histogram"]
    require((hist["10"], hist["11"], hist["12"]) == (816, 96, 4), "seed18 direct-cost histogram")

    # the open pairs are exactly d(a)+d(b) >= 10
    open_pairs = sorted((a, b) for a in dist for b in dist if dist[a] + dist[b] >= 10)
    require(len(open_pairs) == 916, "916 open pairs")
    require(sorted((p["a"], p["b"]) for p in result["pairs"]) == open_pairs, "pair list")
    for p in result["pairs"]:
        require(p["direct"] == dist[p["a"]] + dist[p["b"]], "recorded direct cost")
    by_direct = {}
    for p in result["pairs"]:
        by_direct[p["direct"]] = by_direct.get(p["direct"], 0) + 1
    require(by_direct == {10: 816, 11: 96, 12: 4}, "open pairs by direct cost")

    checked = 0
    # radius-5 join: every direct-10 pair has a length-10 word, nothing shorter;
    # direct-11/12 pairs have no word of length <= 10
    for p in result["pairs"]:
        if p["direct"] == 10:
            require(p["min_le10"] == 10 and len(p["word"]) == 10, "direct-10 pair")
            target = (1 << p["a"], 0, 0, 1 << p["b"])
            require(apply_word(parse_word(p["word"])) == target, "formal witness, direct 10")
            checked += 1
        else:
            require(p["min_le10"] == 11 and "word" not in p, "no word of length <= 10")
    # length-11 stage: the 96 direct-11 pairs are positive controls; the four
    # direct-12 pairs have no length-11 word
    l11 = {(p["a"], p["b"]): p for p in result["l11"]}
    require(sorted(l11) == sorted((p["a"], p["b"]) for p in result["pairs"] if p["direct"] >= 11),
            "length-11 stage target set")
    for (a, b), p in l11.items():
        target = (1 << a, 0, 0, 1 << b)
        if p["direct"] == 11:
            require(p["min_le11"] == 11 and len(p["word"]) == 11, "direct-11 control")
            require(apply_word(parse_word(p["word"])) == target, "formal witness, direct 11")
            checked += 1
        else:
            require(p["direct"] == 12 and p["min_le11"] == 12 and "word" not in p,
                    "direct-12 pair has no word of length <= 11")
            word = direct_word(a, b, dist)
            require(len(word) == 12 and apply_word(word) == target, "direct twelve-call word")
            checked += 1

    # tamper controls: each must fail the formal check
    sample = next(p for p in result["pairs"] if p["direct"] == 10)
    word = parse_word(sample["word"])
    target = (1 << sample["a"], 0, 0, 1 << sample["b"])
    rejected = 0
    for k in range(len(word)):
        rejected += apply_word(word[:k] + word[k + 1:]) != target
    mutated = list(word)
    u, v, i, j = mutated[0]
    mutated[0] = (u, v, j, i)
    rejected += apply_word(mutated) != target
    swapped = (1 << sample["b"], 0, 0, 1 << sample["a"])
    rejected += sample["a"] == sample["b"] or apply_word(word) != swapped
    require(rejected == len(word) + 2, "tampered witnesses must be rejected")
    return checked, rejected


def full(result):
    compiler = shutil.which("c++") or shutil.which("clang++") or shutil.which("g++")
    require(compiler is not None, "full mode needs a C++17 compiler")
    with tempfile.TemporaryDirectory() as tmp:
        exe = Path(tmp) / "engine"
        subprocess.run([compiler, "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror", "-pthread",
                        str(HERE / "engine.cpp"), "-o", str(exe)], check=True, timeout=300)
        threads = str(max(1, os.cpu_count() or 1))
        run = subprocess.run([str(exe), threads, "--l11"], capture_output=True, text=True,
                             check=True, timeout=1800)
    fresh = parse_output(run.stdout)
    require(fresh == result, "fresh engine output differs from RESULT.json")


RECEIPT3 = {  # bounded third-register probe (engine3.cpp), lengths <= 7
    "ball3_layers": [1, 168, 21882, 2683740], "ball3_states": 2705791,
    "ball3_buckets": 1629130, "layer4_images": 450868320,
    "saving_restored": 0, "saving_any_third": 0, "direct_le7_not_found": 0,
}
DIRECT_HISTOGRAM = {0: 1, 1: 12, 2: 84, 3: 390, 4: 1308, 5: 3216, 6: 5773, 7: 7296,
                    8: 6144, 9: 3084, 10: 816, 11: 96, 12: 4}


def three(compiler):
    """Recompute the third-register probe and check it against RECEIPT3."""
    with tempfile.TemporaryDirectory() as tmp:
        exe = Path(tmp) / "engine3"
        subprocess.run([compiler, "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror", "-pthread",
                        str(HERE / "engine3.cpp"), "-o", str(exe)], check=True, timeout=300)
        run = subprocess.run([str(exe), str(max(1, os.cpu_count() or 1))], capture_output=True,
                             text=True, check=True, timeout=1800)
    receipt, hist = {}, {"hist_restored": {}, "hist_any_third": {}}
    for line in run.stdout.splitlines():
        f = line.split()
        if not f or f[0] == "DONE":
            continue
        if f[0] in hist:
            hist[f[0]][int(f[2])] = (int(f[4]), int(f[6]))
        else:
            receipt[f[0]] = [int(x) for x in f[1:]] if len(f) > 2 else int(f[1])
    require(receipt == RECEIPT3, "third-register receipt")
    for name, rows in hist.items():
        # 99 = no word of length <= 7; every direct word of length <= 7 is found
        expected = {d: (d if d <= 7 else 99, n) for d, n in DIRECT_HISTOGRAM.items()}
        require(rows == expected, f"third-register histogram {name}")


def main():
    result = json.loads((HERE / "RESULT.json").read_text())
    checked, rejected = quick(result)
    mode = "quick"
    if "--full" in sys.argv[1:]:
        full(result)
        mode = "full"
    if "--three" in sys.argv[1:]:
        compiler = shutil.which("c++") or shutil.which("clang++") or shutil.which("g++")
        require(compiler is not None, "--three needs a C++17 compiler")
        three(compiler)
        mode += "+three"
    print(f"PASS_GL3_MIXED_TARGETS_LENGTH10 mode={mode} open_pairs=916 exact=916 "
          f"min_equals_direct=all formal_words={checked} tamper_rejected={rejected}")


if __name__ == "__main__":
    main()
