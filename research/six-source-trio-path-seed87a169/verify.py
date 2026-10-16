#!/usr/bin/env python3
"""Replay the complete census and check its witness, controls, and cost."""
import json
from pathlib import Path

import search

HERE = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


def main():
    cert = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    expected = search.enumerate_class()
    need(cert == expected, "complete census differs from certificate")
    enum = cert["enumeration"]
    need(enum["complete_six_label_words"] == 9_321_312, "RGS domain count")
    need(enum["words_in_allowed_profiles"] == 2_342_340, "profile domain count")
    need(enum["maximum_coverage"] == 61 and enum["number_at_maximum"] == 88,
         "coverage maximum or multiplicity")
    need("62" not in enum["histogram_nonzero_pair_masks"] and
         "63" not in enum["histogram_nonzero_pair_masks"], "unexpected near/full cover")

    witness = cert["maximum_witness"]
    counts, trio, prefixes, cover = search.analyze_word(witness["singleton_word"])
    need(counts == witness["singleton_counts"], "witness singleton counts")
    need(trio == witness["closing_trio_mask"], "closing TRIO parity")
    need(prefixes == witness["prefixes"], "witness prefixes")
    need((cover & ~1).bit_count() == 61, "witness coverage")
    need(witness["missing_masks"] == [11, 40], "witness missing rows")
    for mask in witness["missing_masks"]:
        indices = witness["four_readout_indices_for_missing_masks"][str(mask)]
        need(indices is not None and len(indices) == 4, "missing row has no four-readout realization")
        realized = 0
        for index in indices:
            realized ^= prefixes[index]
        need(realized == mask, "four-readout realization is wrong")

    # The source-map multiset matches the incumbent; query costs are 144 vs 142.
    total_maps = witness["total_source_map_counts"]
    need(sorted(total_maps) == [2, 2, 2, 2, 4, 4], "source-map profile")
    cost = cert["cost"]
    need(cost["incumbent"]["root_calls"] == 16 + 126 == 142, "incumbent bill")
    need(cost["best_one_trio_with_four_readout_repairs"]["root_calls"] == 14 + 130 == 144,
         "completed TRIO bill")
    need(cost["unit_call_delta"] == 2, "unit-price comparison")

    # Positive control: the incumbent singleton word covers all 63 nonzero masks.
    word, baseline_prefixes = search.singleton_positive_control()
    need(word == cert["positive_control"]["incumbent_singleton_word"], "positive word")
    need(search.differences(baseline_prefixes) == (1 << 64) - 2, "positive coverage")

    # Negative controls: wrong profile and deleted edge cannot enter the census.
    bad_profile = [0] * 13
    try:
        search.analyze_word(bad_profile)
    except ValueError:
        pass
    else:
        raise ValueError("negative control accepted an invalid profile")
    altered = witness["singleton_word"].copy()
    altered[-1] = 6
    try:
        search.analyze_word(altered)
    except ValueError:
        pass
    else:
        raise ValueError("negative control accepted an out-of-alphabet label")

    print("PASS_SINGLE_TRIO_CENSUS eligible=%d max=61/63 at_max=88 completed_queries=144 incumbent=142" %
          enum["words_in_allowed_profiles"])
    print("CONTROLS positive=singleton_full_cover negative=profile,alphabet")


if __name__ == "__main__":
    main()
