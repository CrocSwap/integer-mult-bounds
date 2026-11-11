"""Exact one-donor proportionality census on the pinned #7277 word."""

import argparse
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import runpy
import time

WORD = "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756"
HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"


def checked(path, pin):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != pin:
        raise ValueError(f"Unexpected SHA-256 for {path.name}")
    return raw


def proportional(source, donor):
    """Return the signed factor source/donor when both rational vectors are nonzero."""
    source_den, x = source
    donor_den, y = donor
    if not x or x.keys() != y.keys():
        return None
    pivot = min(x)
    source_entry, donor_entry = x[pivot], y[pivot]
    if any(v * donor_entry != y[key] * source_entry for key, v in x.items()):
        return None
    return Fraction(source_entry * donor_den, donor_entry * source_den)


def collector(records):
    def visit(index, role, source, destination, rank, charts, rows, owned):
        live_roles = [r for r, chart in enumerate(charts) if r != role and chart == destination]
        donors = [r for r in live_roles if rows[r][1]]
        hits = []
        for r in donors:
            q = proportional(rows[role], rows[r])
            if q is not None:
                hits.append({"role": r, "factor": str(q), "owned": r in owned})
        records.append({
            "literal_index": index, "role": role, "from": source, "to": destination, "rank": rank,
            "live_destination_roles": len(live_roles),
            "nonzero_destination_roles": len(donors),
            "zero_destination_roles": len(live_roles) - len(donors),
            "owned_nonzero_donor_roles": sum(r in owned for r in donors),
            "matches": hits,
        })
    return visit


def controls(audit):
    word = {
        "public": 2, "owned_fields": 3, "initial": [0, 0], "final": [0, 0], "frames": [[], [1]],
        "program": [
            ["INIT", 2, 0], ["COPY", 2, 0, "2/3", 0], ["ADD", 2, 1, "-4/3", 0],
            ["INIT", 3, 0], ["COPY", 3, 0, "-1/5", 0], ["ADD", 3, 1, "2/5", 0],
            ["MOVE", 3, 0, 1, True], ["INIT", 4, 1], ["MOVE", 2, 0, 1, True],
            ["CLEAR", 2, 1], ["CLEAR", 3, 1], ["CLEAR", 4, 1],
        ],
    }
    hits = []
    result = audit(word, time.monotonic(), 1, collector(hits))
    assert result["scope_exhausted"]
    assert hits[-1]["matches"] == [{"role": 3, "factor": "-10/3", "owned": True}]
    assert hits[-1]["zero_destination_roles"] == 1
    word["program"][5][3] = "-2/5"
    misses = []
    result = audit(word, time.monotonic(), 1, collector(misses))
    assert result["scope_exhausted"] and misses[-1]["nonzero_destination_roles"] == 1
    assert not misses[-1]["matches"]
    return {"signed_factor": "-10/3", "zero_donor_ignored": True, "sign_mutation_rejected": True}


def main():
    start = time.monotonic()
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", required=True, type=Path)
    parser.add_argument("--cap", default=20, type=float)
    options = parser.parse_args()
    assert 0 < options.cap <= 20
    here = Path(__file__).resolve().parent
    core_path = here / "replay_core.py"
    core_pin = 'fd7a1a7f9cb8f71caa5e0d89ed16ea056503fa283bc05f655eb0da7e8d5fc6e0'
    checked(core_path, core_pin)
    replay = runpy.run_path(str(core_path))["audit"]
    raw = checked(options.word, WORD)
    records = []
    report = replay(json.loads(gzip.decompress(raw)), start, options.cap, collector(records))
    assert len(records) == report["paid_owned_moves"]
    if report["scope_exhausted"]:
        assert len(records) == 47 and report["paid_owned_histogram"] == {1:20, 2:9, 3:2, 4:13, 5:2, 6:1}
        assert not report["exact_zero_moves"] and (report["owned_lifetimes"], report["peak_owned"]) == (70, 49)
    result = {
        **report, "scientific_head": HEAD, "word_sha256": WORD, "core_sha256": core_pin,
        "destination_live_comparisons": sum(r["live_destination_roles"] for r in records),
        "destination_nonzero_comparisons": sum(r["nonzero_destination_roles"] for r in records),
        "destination_zero_exclusions": sum(r["zero_destination_roles"] for r in records),
        "destination_owned_nonzero_comparisons": sum(r["owned_nonzero_donor_roles"] for r in records),
        "match_count": sum(len(r["matches"]) for r in records),
        "controls": controls(replay), "records": records,
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
