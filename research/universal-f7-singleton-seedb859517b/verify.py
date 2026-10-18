#!/usr/bin/env python3
"""Verification for the f(7) singleton universal-path package.

Rebuilds every reproduced and controlled number from scratch and compares the
stored certificate with EXPECTED.json field by field.  With --full it also
re-runs the decisive length-18 census; without it, the census is replayed from
CERTIFICATE.json (witnesses are re-checked exactly) and its recorded node count
is compared against the stored expectation.

Pass marker: PASS_F7_SINGLETON_GAP_VERIFY <conclusion>
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine import (
    admissible_splits,
    census_words,
    counting_least_even_L,
    cyclic_census,
    gray_word,
    hamiltonian_cycle,
    joint_covers,
    lemma_a_table,
    normalized_set_census,
    set_level_splits,
    word_is_universal,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINNED = json.loads(
    (ROOT / "research" / "universal-connector-six-source" / "EXPECTED.json").read_text(
        encoding="utf-8"
    )
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="re-run the length-18 census")
    args = ap.parse_args()
    t0 = time.time()

    cert = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    expected = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))

    # reproduction: pinned censuses, counting bounds, Gray constructions
    for n, length in ((5, 10), (6, 12), (6, 14)):
        hist, digest, words = census_words(n, length)
        pinned = {(c["sources"], c["length"]): c for c in PINNED["censuses"]}[(n, length)]
        assert words == pinned["words"] and max(hist) == pinned["max_coverage"]
        assert {str(k): v for k, v in sorted(hist.items())} == pinned["histogram"]
        assert digest == pinned["records_sha256"]
    for n in (5, 6, 7):
        assert counting_least_even_L(n) == PINNED["constructions"][str(n)]["lower_bound"]
        w = gray_word(n)
        assert word_is_universal(w, n) and len(w) == PINNED["constructions"][str(n)]["length"]

    # controls
    stats9 = normalized_set_census(5, 9)
    assert stats9 == {"sets": 7_888_725, "max_coverage": 29, "covers": 0}
    stats10 = normalized_set_census(5, 10)
    joint10 = joint_covers(5, set_level_splits(5, 10))
    assert len(joint10) == stats10["covers"] > 0
    for E, O in joint10:
        P = sorted(set(E) | set(O))
        assert hamiltonian_cycle(P, 5) is None, "f(5)=12 forbids 10-cycles"
    for s, t in ((9, 8), (8, 9), (8, 8)):
        assert not any(r["feasible"] for r in lemma_a_table(7, s, t)), (s, t)
    assert any(r["feasible"] for r in lemma_a_table(7, 9, 9))
    assert admissible_splits(7, 18) == [(9, 9)]

    # certificate agreement
    assert cert["tier3_f7"]["admissible_splits_L18"] == [[9, 9]]
    assert cert["tier3_f7"]["size17_splits"] == {"9_8": False, "8_9": False}
    assert cert["conclusion"] == expected["conclusion"]

    if args.full:
        r = cyclic_census(7, 18, budget=9, simple=True)
        assert r["leaves"] == cert["tier3_f7"]["simple_18_cycles"], "cycle count drifted"
        assert len(r["words"]) == len(cert["tier3_f7"]["universal_words"]), "hit count drifted"
    else:
        assert cert["tier3_f7"]["census_nodes"] == expected["census_nodes"]
        assert cert["tier3_f7"]["simple_18_cycles"] == expected["simple_18_cycles"]
        assert len(cert["tier3_f7"]["universal_words"]) == expected["universal_words"]

    # every recorded witness is real
    for w in cert["tier3_f7"]["universal_words"]:
        assert len(w) == 18 and word_is_universal(tuple(w), 7)

    print(f"PASS_F7_SINGLETON_GAP_VERIFY {cert['conclusion']} "
          f"cycles={cert['tier3_f7']['simple_18_cycles']} "
          f"universal_words={len(cert['tier3_f7']['universal_words'])} "
          f"nodes={cert['tier3_f7']['census_nodes']} "
          f"seconds={round(time.time() - t0, 1)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
