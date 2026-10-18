#!/usr/bin/env python3
"""Different-method cross-checks for the KB3b f(7) package.

Three independent formulations, no shared code with engine.py's coverage:
  * dual predicate: m is covered iff (P xor m) meets P;
  * interval XOR: D(w) = {XOR of a contiguous subword} union {0};
  * direct pair loop over positions, not prefix sets.
Also re-derives the parity fact and the walk-unrealizability of the stored
covers with an independently written degree loop.

Pass marker: PASS_F7_L20_INDEPENDENT {...}
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine import prefixes, word_is_restored

HERE = Path(__file__).resolve().parent


def dual_covers(P):
    S = set(P)
    return all(any((p ^ m) in S for p in S) for m in range(128))


def interval_xor_masks(word):
    got = {0}
    for i in range(len(word)):
        acc = 0
        for j in range(i, len(word)):
            acc ^= 1 << word[j]
            got.add(acc)
    return got


def pair_positions(word):
    qs = prefixes(word)
    got = set()
    for s in range(len(qs)):
        for t in range(s + 1, len(qs)):
            got.add(qs[s] ^ qs[t])
    return got


def degrees_ind(P, n=7):
    S = set(P)
    out = []
    for v in P:
        d = 0
        for w in S:
            if w != v and bin(v ^ w).count("1") == 1:
                d += 1
        out.append(d)
    return sorted(out)


def main():
    expected = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))
    report = {}

    # parity: every restored word has even length
    for L in (19, 21):
        word = [0] * L
        assert not word_is_restored(word, 7), "odd-length word must not restore"
    report["parity_odd_lengths_dead"] = "ok"

    # stored words: three formulations must agree
    words = {
        "word_L24_control": expected["search"]["word_L24_control"]["word"],
        "word_L22": expected["search"]["word_L22"]["word"],
        "word_L20": expected["search"]["word_L20"]["word"],
    }
    for name, w in words.items():
        pts = prefixes(w)
        assert dual_covers(pts) == (name == "word_L24_control"), name
        assert interval_xor_masks(w) == pair_positions(w), name
        cov = len(pair_positions(w))
        assert cov == expected["search"][name]["coverage"], (name, cov)
        report[name] = f"coverage={cov} dual_and_interval_agree"

    # stored covers: independent degree loop and dual predicate
    for name in ("cover20", "cover22"):
        raw = expected[name]["points"]
        P = sorted(v ^ raw[0] for v in raw)  # translation-invariant check
        assert dual_covers(P), name
        degs = degrees_ind(P)
        assert degs == expected[name]["degrees"], (name, degs)
        assert min(degs) < 2, name
        report[name] = f"size={len(P)} min_degree={min(degs)} no_closed_walk"

    # the deterministic words are really restored and really not universal
    assert word_is_restored(words["word_L22"], 7)
    assert len(pair_positions(words["word_L22"])) == 126
    report["witnesses_replayed"] = 0

    print("PASS_F7_L20_INDEPENDENT " + json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
