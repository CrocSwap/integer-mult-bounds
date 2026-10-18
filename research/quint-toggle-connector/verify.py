#!/usr/bin/env python3
"""Check the priced conclusion against the pinned singleton witness."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERT = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
BASE = json.loads(
    (ROOT / "research/universal-connector-boundary/CERTIFICATE.json").read_text(
        encoding="utf-8"
    )
)


def main():
    baseline = CERT["singleton_alphabet_baseline_witness"]
    schedule = BASE["schedules"]["five_extra_source"]
    word = schedule["word"]
    a_calls = sum(call[0] == "A" for call in word)
    b_calls = sum(call[0] == "B" for call in word)
    assert schedule["queries"] == baseline["root_queries"] == 74
    assert a_calls == baseline["readout_calls"] == 62
    assert b_calls == baseline["source_calls"] == baseline["source_adds"] == 12
    assert baseline["total_elementary_adds"] == 74
    assert baseline["covered_nonzero_masks"] == 31

    walks = CERT["one_q5_source_walks"]
    comparisons = [
        (walks["m5"]["total_root_queries_at_least"], walks["m5"]["total_elementary_adds_at_least"]),
        (walks["m7_census"]["total_root_queries_at_least"], walks["m7_census"]["total_elementary_adds_at_least"]),
        (walks["m9_aggregate"]["total_root_queries_at_least"], walks["m9_aggregate"]["total_elementary_adds_at_least"]),
        (walks["m_at_least_11"]["total_root_queries_at_least"], walks["m_at_least_11"]["total_elementary_adds_at_least"]),
    ]
    assert comparisons == [(90, 94), (92, 96), (80, 84), (74, 78)]
    for queries, adds in comparisons:
        assert queries >= 74 and adds >= 74
    print("PASS_QUINT_TOGGLE_PRICING q5_lower_bounds=90/94,92/96,80/84,74/78 baseline=74/74")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
