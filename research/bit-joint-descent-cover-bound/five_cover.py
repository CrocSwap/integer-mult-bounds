"""Necessary disjoint source-line packing for the eight rank-four profile."""
import argparse
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

CAP = 4096
PIN = "51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78"


def scan(path, extra_line=False):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    word = json.loads(gzip.decompress(raw))
    frames = word["frames"]
    lines = [tuple(map(Fraction, frames[str(i)]["B"][0])) for i in word["start"][:111]]
    groups = {}
    count = 0
    for chart, frame in frames.items():
        if frame["dim"] != 4:
            continue
        count += 1
        annihilator = [tuple(map(Fraction, row)) for row in frame["A"]]
        support = sum(1 << i for i, line in enumerate(lines)
                      if all(not sum(x * y for x, y in zip(line, row, strict=True)) for row in annihilator))
        assert support.bit_count() <= 12
        if support.bit_count() >= 12 - int(extra_line):
            groups.setdefault(support, []).append(int(chart))
    masks = list(groups)
    states = 0
    stopped = False

    def choose(chosen, remaining):
        nonlocal states, stopped
        if len(chosen) == 8:
            return chosen
        if len(chosen) + len(remaining) < 8:
            return None
        if states >= CAP:
            stopped = True
            return None
        states += 1
        for i, mask in enumerate(remaining):
            if extra_line:
                if any((a | b | c | mask).bit_count() < 47 for a, b, c in combinations(chosen, 3)):
                    continue
                others = [other for other in remaining[i + 1:] if (mask | other).bit_count() >= 23]
            else:
                others = [other for other in remaining[i + 1:] if not (mask & other)]
            found = choose([*chosen, mask], others)
            if found is not None or stopped:
                return found
        return None

    found = choose([], masks)
    result = dict(status="NECESSARY_DISJOINT_COVER_ONLY", rank_four_charts=count,
                maximal_charts=sum(map(len, groups.values())), distinct_maximal_supports=len(masks),
                disjoint_pairs=sum(not (a & b) for i, a in enumerate(masks) for b in masks[i + 1:]),
                checked_states=states, cap=CAP, capped=stopped,
                first_survivor=None if found is None else [groups[mask] for mask in found],
                word_sha256=PIN)
    if extra_line:
        result.update(status="NECESSARY_FIVE_SUMMARY_TARGET_COVER_ONLY", optional_extra_line=1,
                      minimum_four_chart_cover=47)
        result["eligible_charts"] = result.pop("maximal_charts")
        result["distinct_eligible_supports"] = result.pop("distinct_maximal_supports")
    return result


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Use assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--extra-line", action="store_true")
    print(json.dumps(scan(**vars(parser.parse_args())), indent=2, sort_keys=True))
