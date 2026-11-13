"""Replay the two exact prefix separators for the #7481 chart-1049 cycle."""
import argparse
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path
from signal import alarm
from time import perf_counter

ARCHIVE = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"
NATIVE = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
CUT, CHART = 36481, 1049
BANK = (1322, 1352, 1440)
PROBES = ({982: F(1, 2), 1322: F(1)}, {1324: F(-2), 1440: F(1)})
CONTRASTS = ((1322, 1352), (1352, 1440))


def forward(word, probe):
    values = probe.copy()
    frames = dict(enumerate(word["initial"]))
    for op, dest, *args in word["program"][:CUT]:
        if op == "MOVE":
            assert frames[dest] == args[0]
            assert args[2] == (dest >= word["public"])
            frames[dest] = args[1]
            continue
        if op == "INIT":
            assert dest not in frames and dest not in values
            frames[dest] = args[0]
            continue
        if op == "CLEAR":
            assert frames.pop(dest) == args[0]
            values.pop(dest, None)
            continue
        value = values.get(dest, 0)
        if op == "SCALE":
            assert frames[dest] == args[1]
            value *= F(args[0])
        else:
            assert op in ("ADD", "COPY")
            src, coefficient, chart = args
            assert frames[src] == frames[dest] == chart
            if op == "COPY":
                assert not value
            if src in values:
                value += F(coefficient) * values[src]
        if value:
            values[dest] = value
        else:
            values.pop(dest, None)
    assert all(frames[role] == CHART for role in BANK)
    return [values.get(role, 0) for role in BANK]


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", required=True, type=Path)
    args = parser.parse_args()
    start = perf_counter()
    alarm(30)
    archive = args.word.read_bytes()
    assert sha256(archive).hexdigest() == ARCHIVE
    payload = gzip.decompress(archive)
    assert sha256(payload).hexdigest() == NATIVE
    word = json.loads(payload)
    assert word["program"][CUT - 1:CUT + 2] == [
        ["MOVE", 1322, 3, CHART, False], ["ADD", 1352, 1322, "2", CHART],
        ["ADD", 1440, 1322, "-2", CHART],
    ]
    checks = []
    for probe, contrast, want in zip(PROBES, CONTRASTS, (1, -1), strict=True):
        bank = forward(word, probe)
        assert bank == [0, 0, 0]
        result = probe.get(contrast[0], 0) - probe.get(contrast[1], 0)
        assert result == want
        checks.append({"probe": probe, "contrast_roles": contrast,
                       "contrast": result, "cut_bank": bank})
    print(json.dumps({
        "status": "PASS_BOTH_EXACT_FORWARD_PREFIX_SEPARATORS",
        "native_sha256": NATIVE, "cut_before": CUT, "chart": CHART, "bank_order": BANK,
        "case_count": 1, "probe_count": len(checks), "checks": checks,
        "cap_seconds": 30, "seconds": perf_counter() - start,
    }, default=str, sort_keys=True, indent=2))
    alarm(0)


if __name__ == "__main__":
    main()
