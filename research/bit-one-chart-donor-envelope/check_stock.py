"""Verify the zero-stock receipt by solving the dual parity equations."""
import argparse
import gzip
import json
from pathlib import Path
import runpy
import time

from screen import authenticated


def consistent(equations):
    """Equations have the coefficient bitset followed by the right side in bit 0."""
    pivots = {}
    for equation in equations:
        while equation > 1:
            key = (equation & -2) & -(equation & -2)
            if key in pivots:
                equation ^= pivots[key]
            else:
                pivots[key] = equation
                break
        else:
            if equation:
                return False
    return True


def verify(deps, receipt_path):
    here = Path(__file__).resolve().parent
    authenticated({"deps": deps, "screen": here})
    src = runpy.run_path(str(here / "pr7200_verify.py"))
    rewrite = runpy.run_path(str(here / "retag.py"))
    word = json.loads(gzip.decompress((deps / "inputs/WORD.json.gz").read_bytes()))
    expected = json.loads(receipt_path.read_text())
    frames, ranks, canonical = src["geometry"](word)
    changed, origin, adjusted, _ = rewrite["retag"](word, rewrite["modules"](word))
    _, sites, observed = src["trace"](changed, origin, adjusted, frames, ranks, canonical)
    assert len(sites) == len(expected["sites"]) == 35
    charts = {chart for chart in canonical.values() if ranks[chart]}
    chart_total = len(charts)
    assert chart_total == 635
    assert sum(bool(observed.get(chart)) for chart in charts) == 627
    assert consistent([3]) and not consistent([2, 3])
    # An appended copy of the target makes a previously separating dual impossible.
    assert consistent([2, 4, 9]) and not consistent([2, 4, 8, 9])
    count = 0
    for site, record in zip(sites, expected["sites"], strict=True):
        assert all(site[k] == record[k] for k in ("event", "target_chart", "due"))
        n = 0
        for chart in charts - {site["target_chart"]}:
            rows = observed.get(chart, {})
            equations = [2 * row for row, cut in rows.items() if cut <= site["due"]]
            equations.append(2 * site["target_row"] + 1)
            assert consistent(equations), (site["event"], chart)
            n += 1
        assert n == record["chart_count"] == 634
        count += n
    assert count == expected["all_chart_pairs"] == 22190
    assert expected["optimistic_saving_upper_whole"] == "0"
    print(json.dumps({"dual_systems_consistent": count, "sites": len(sites),
                      "positive_charts": chart_total, "controls": "PASS"}))


if __name__ == "__main__":
    start = time.monotonic()
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deps", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    verify(args.deps.resolve(), args.receipt.resolve())
    print(f"seconds={time.monotonic()-start:.6f}")
