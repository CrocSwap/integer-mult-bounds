#!/usr/bin/env python3
"""Code-disjoint reconstruction of the pinned bit word's paid-rank mass accounting.

Reads research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz and tune/EXPECTED.json
directly and re-derives, from the gate-operations file alone (frames as live line sets,
per-register start/final frame ids) plus the recorded copy-rank block, the aggregate

    word.legality.rank_mass = 5129 = 8R + 63 + 14v,

including its per-class decomposition, and cross-checks the recorded histograms against it.
No code is imported from the supplier's checker chain (stage_cohort.py, legality_h.cpp,
global_k.py); frame dimensions are computed here by exact rational rank.

Usage: python3 -B research/bit-ledger-frame-ranks-seedfeb2/verify.py
Prints PASS_BIT_LEDGER_FRAME_RANKS on success.

Task card: TASK-CARD.md. Prepared by Aaron Wang, with help from opencode. Apache-2.0.
"""
import copy
import gzip
import hashlib
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
TUNE = os.path.join(ROOT, "research", "e8-bit-p111-tuned", "tune")
WORD_PATH = os.path.join(TUNE, "bitE8mut-p111-tuned.json.gz")
EXP_PATH = os.path.join(TUNE, "EXPECTED.json")

# Expected frame-dimension spectrum of the 636 label frames (counts by exact rank).
EXPECTED_DIM_SPECTRUM = {0: 1, 1: 111, 2: 153, 4: 70, 6: 180, 7: 120, 8: 1}


def qrank(vecs):
    """Exact rank over Q of integer row vectors (Gauss-Jordan with fractions)."""
    rows = [[Fraction(x) for x in vr] for vr in vecs]
    rank = 0
    ncol = len(rows[0]) if rows else 0
    for c in range(ncol):
        piv = None
        for i in range(rank, len(rows)):
            if rows[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        pv = rows[rank][c]
        rows[rank] = [x / pv for x in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][c] != 0:
                f = rows[i][c]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def analyse(w):
    """Recompute frame dimensions and per-register net frame climbs from the word."""
    lines = [tuple(x) for x in w["lines"]]
    dims = [qrank([lines[i] for i in fset]) for fset in w["frames"]]
    net = [dims[w["final"][i]] - dims[w["start"][i]] for i in range(len(w["start"]))]
    return dims, net


def core_checks(w, exp, silent=False):
    ew = exp["word"]
    v, R = w["v"], w["R"]
    say = (lambda m: print("   ok:", m)) if not silent else (lambda m: None)

    dims, net = analyse(w)
    spectrum = {d: dims.count(d) for d in sorted(set(dims))}
    if spectrum != EXPECTED_DIM_SPECTRUM:
        raise AssertionError("FAIL: frame dimension spectrum " + str(spectrum))
    say("frame dimension spectrum")

    X, Y, H = net[:v], net[v:2 * v], net[2 * v:]
    if not (set(X) == {7} and len(X) == v):
        raise AssertionError("FAIL: X-slot net climbs " + str(set(X)))
    if not (set(Y) == {7} and len(Y) == v):
        raise AssertionError("FAIL: Y-slot net climbs " + str(set(Y)))
    if not (set(H) == {8} and len(H) == R):
        raise AssertionError("FAIL: helper net climbs " + str(set(H)))
    total_net = sum(net)
    if total_net != 8 * R + 14 * v:
        raise AssertionError("FAIL: total net climb %d != 8R + 14v" % total_net)
    say("per-register net climbs 7/7/8; 8R + 14v = %d" % total_net)

    # Copy ranks of the nine retained totals: recorded block, 63 = 9 * 7. The
    # from-operations term is the climb mass above; the per-copy rank is the
    # recorded pin (see README limits).
    copy_ranks = ew["copy_ranks"]
    if not (len(w["ret"]) == 9 and len(copy_ranks) == 9
            and len(set(w["ret"])) == 9 and all(2 * v <= r < 2 * v + R for r in w["ret"])):
        raise AssertionError("FAIL: retained-total shape")
    if set(copy_ranks) != {7}:
        raise AssertionError("FAIL: copy ranks " + str(set(copy_ranks)))
    say("nine retained totals; copy ranks all 7")

    mass = total_net + sum(copy_ranks)
    if not (mass == 8 * R + 63 + 14 * v == 5129):
        raise AssertionError("FAIL: rank_mass identity " + str(mass))
    if mass != ew["legality"]["rank_mass"]:
        raise AssertionError("FAIL: rank_mass != recorded %d" % ew["legality"]["rank_mass"])
    say("rank_mass = 8R + 63 + 14v = %d matches the record" % mass)

    hist = {int(k): n for k, n in ew["local_histogram"].items()}
    if sum(r * n for r, n in hist.items()) != mass:
        raise AssertionError("FAIL: local_histogram weighted sum")
    if not all(0 < r < 8 for r in hist):
        raise AssertionError("FAIL: local_histogram ranks")
    say("local_histogram weighted sum equals rank_mass")

    # Aggregate cross-consistency of nine.profile with the bit coverage identity
    # deficit = W - 63N, W = 32 * 8 * 111, N = 32 * 9 (aggregate level only).
    nb, profile = exp["nine"]["bit"], exp["nine"]["profile"]
    W, N = nb["live"], 32 * 9
    if W != 32 * 8 * v:
        raise AssertionError("FAIL: W != 32 * 8 * v")
    if sum(int(r) * n for r, n in profile.items()) != 64 * W - (W - 63 * N):
        raise AssertionError("FAIL: nine.profile weighted sum")
    if ew["decoder_constant"] != sum(copy_ranks):
        raise AssertionError("FAIL: decoder_constant")
    say("nine.profile weighted sum = 64W - (W - 63N); decoder_constant = 63")


def expect_reject(name, mutate, w, exp):
    w2, exp2 = copy.deepcopy(w), copy.deepcopy(exp)
    mutate(w2, exp2)
    try:
        core_checks(w2, exp2, silent=True)
    except AssertionError:
        print("   ok: control rejected:", name)
        return
    raise AssertionError("FAIL: control not rejected: " + name)

def main():
    with gzip.open(WORD_PATH, "rt", encoding="utf-8") as f:
        w = json.load(f)
    with open(EXP_PATH, encoding="utf-8") as f:
        exp = json.load(f)
    ew = exp["word"]

    # Source binding: the analysed file is exactly the pinned word.
    file_sha = hashlib.sha256(open(WORD_PATH, "rb").read()).hexdigest()
    content_sha = hashlib.sha256(
        json.dumps(w, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if file_sha != ew["file_sha256"]:
        raise AssertionError("FAIL: word file_sha256 " + file_sha)
    if content_sha != ew["content_sha256"]:
        raise AssertionError("FAIL: word content_sha256 " + content_sha)
    if not ((w["v"], w["R"], w["h"]) == (111, 439, 8) and len(w["frames"]) == 636
            and len(w["start"]) == len(w["final"]) == 2 * w["v"] + w["R"]):
        raise AssertionError("FAIL: word shape")
    print("   ok: pinned word file/content sha256 and shape")

    core_checks(w, exp)

    # Semantic failure controls: each mutation must be rejected (source binding
    # is exercised separately in main; these are the geometric/aggregate checks).
    expect_reject(
        "full frame collapsed to one label",
        lambda w2, e2: w2["frames"].__setitem__(1, [0]), w, exp)
    expect_reject(
        "one register start frame set to its final frame",
        lambda w2, e2: w2["start"].__setitem__(5, w2["final"][5]), w, exp)
    expect_reject(
        "copy rank mutated to 6",
        lambda w2, e2: e2["word"]["copy_ranks"].__setitem__(0, 6), w, exp)
    expect_reject(
        "local histogram one-count mutation",
        lambda w2, e2: e2["word"]["local_histogram"].__setitem__("1", e2["word"]["local_histogram"]["1"] + 1),
        w, exp)
    expect_reject(
        "nine.profile one-count mutation",
        lambda w2, e2: e2["nine"]["profile"].__setitem__("1", e2["nine"]["profile"]["1"] - 288),
        w, exp)

    print("PASS_BIT_LEDGER_FRAME_RANKS")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(e)
        sys.exit(1)
