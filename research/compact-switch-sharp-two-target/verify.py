#!/usr/bin/env python3
"""Live two-target compact switch on the sharp window edges.

CRT.md's simultaneous argument assumes the published 2B margin. PR #4646
left open whether one K-separated pair still restores both control words
on a window that is sharp-good and outside that margin. This verifier runs
that macro at W=0 and at W=2^m-B+1. It does not replay the twelve paid
H-bit exchanges, and it claims no new kappa.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "compact-switch-sharp-two-target"

PHRASES = (
    "y additions then have total z(1-2b)2^j",
    "2B margins keep every intermediate carry inside its own guard interval",
    "Color targets by current position modulo K, so guard intervals are disjoint.",
    "r [2/B + 8B/2^K] <= C p 2^-G.",
)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            need(digest == row["sha256"], row["path"])
    crt = (ROOT / "research/unconditional-batched-crt/CRT.md").read_text(encoding="utf-8")
    for phrase in PHRASES:
        need(phrase in crt, phrase)
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.


def live_macro(u: int, t: int, y: int, sources, bits: int, positions: tuple[int, int]):
    """Two live-digit steps with a load of f between them and an unload after."""
    base = 1 << bits
    count = len(positions)

    def one_f(u0: int, t0: int, y0: int):
        parity = [(u0 >> (bits * i)) & 1 for i in range(count)]
        digits = [(t0 >> (bits * i)) & (base - 1) for i in range(count)]
        y1 = y0
        for i in range(count):
            y1 += 2 * parity[i] * digits[i] * (1 << positions[i])
        t1 = t0
        for i in range(count):
            t1 += ((y1 >> positions[i]) & 1) << (bits * i)
        live = [(t1 >> (bits * i)) & (base - 1) for i in range(count)]
        y2 = y1
        for i in range(count):
            y2 += parity[i] * (1 - 2 * live[i]) * (1 << positions[i])
        t2 = t1
        for i in range(count):
            t2 -= (((y2 >> positions[i]) & 1) ^ parity[i]) << (bits * i)
        return u0, t2, y2

    u, t, y = one_f(u, t, y)
    loaded = sources(y)
    for i, value in enumerate(loaded):
        u += value << (bits * i)
    u, t, y = one_f(u, t, y)
    unloaded = sources(y)
    for i, value in enumerate(unloaded):
        u -= value << (bits * i)
    return u, t, y


def ideal_y(y: int, values: tuple[int, int], positions: tuple[int, int]) -> int:
    for value, pos in zip(values, positions):
        y ^= value << pos
    return y


def pack(b0: int, w0: int, b1: int, w1: int, gap: int) -> int:
    return b0 + (w0 << 1) + (b1 << gap) + (w1 << (gap + 1))


def edge_pair(bits: int, width: int, independent: bool) -> int:
    """Both targets sit on a sharp edge outside the published 2B margin."""
    base = 1 << bits
    limit = 1 << width
    gap = width + 1
    upper = limit - base + 1
    published_hi = limit - 2 * base
    for window in (0, upper):
        need(not (2 * base <= window < published_hi), "edge is outside the published margin")
        need(0 <= window <= upper, "edge is sharp-good")
    positions = (0, gap)
    passes = 0
    windows = ((0, 0), (upper, upper))
    if independent:
        windows = ((0, 0), (0, upper), (upper, 0), (upper, upper))
    legal = range(base - 1)
    for w0, w1 in windows:
        for b0 in (0, 1):
            for b1 in (0, 1):
                for s0 in (0, 1):
                    for s1 in (0, 1):
                        values = (s0, s1)
                        source = lambda word, values=values: values
                        for d0 in legal:
                            for d1 in legal:
                                for e0 in legal:
                                    for e1 in legal:
                                        y = pack(b0, w0, b1, w1, gap)
                                        u = e0 + (e1 << bits)
                                        t = d0 + (d1 << bits)
                                        end = live_macro(u, t, y, source, bits, positions)
                                        need(end == (u, t, ideal_y(y, values, positions)),
                                             "sharp edge restores both controls")
                                        passes += 1
    return passes


def window_sources() -> int:
    """A source may read a restored window bit. It must not read a target."""
    bits = 2
    width = 5
    base = 1 << bits
    gap = width + 1
    upper = (1 << width) - base + 1
    positions = (0, gap)
    passes = 0

    def source(word: int) -> tuple[int, int]:
        return (word >> 3) & 1, (word >> (gap + 2)) & 1

    for window in (0, upper):
        for b0 in (0, 1):
            for b1 in (0, 1):
                for d0 in range(base - 1):
                    for d1 in range(base - 1):
                        for e0 in range(base - 1):
                            for e1 in range(base - 1):
                                y = pack(b0, window, b1, window, gap)
                                u = e0 + (e1 << bits)
                                t = d0 + (d1 << bits)
                                values = source(y)
                                end = live_macro(u, t, y, source, bits, positions)
                                need(end == (u, t, ideal_y(y, values, positions)),
                                     "window-bit source restores both controls")
                                passes += 1
    return passes


def failure_controls() -> None:
    bits = 2
    width = 5
    base = 1 << bits
    gap = width + 1
    positions = (0, gap)
    # One past the sharp upper edge. The first window spills onto the next target.
    spilled = (1 << width) - (base - 2)
    y = pack(0, spilled, 0, 0, gap)
    need(y == 60, "past-sharp witness address")
    end = live_macro(1, 2, y, lambda word: (0, 0), bits, positions)
    need(end == (1, 10, 60), "past-sharp window does not restore t")
    need(end != (1, 2, ideal_y(y, (0, 0), positions)), "past-sharp witness is not ideal")

    def reads_targets(word: int) -> tuple[int, int]:
        return word & 1, (word >> gap) & 1

    leaked = live_macro(1, 0, 0, reads_targets, bits, positions)
    need(leaked == (1, 0, 1), "target-reading source changes y")
    need(leaked != (1, 0, 0), "target-reading source is not the ideal switch")

    # The published overlapping pair. Each window meets the 2B margin; t does not return.
    overlap_positions = (0, 1)

    def overlap_source(word: int) -> tuple[int, int]:
        return (word >> 4) & 1, (word >> 5) & 1

    overlap = live_macro(0, 1, 80, overlap_source, bits, overlap_positions)
    need(overlap == (0, 5, 81), "overlapping targets do not restore t")
    need(overlap != (0, 1, 81), "overlap witness is not the ideal switch")


def main() -> None:
    pins_and_phrases()
    b4 = edge_pair(2, 5, True)
    b2 = edge_pair(1, 5, False)
    b8 = edge_pair(3, 6, False)
    windows = window_sources()
    failure_controls()
    need(b4 == 5184 and b2 == 32 and b8 == 76832 and windows == 648, "unexpected counts")
    print(
        "PASS_COMPACT_SWITCH_SHARP_TWO_TARGET "
        f"b4_m5={b4} b2_m5={b2} b8_m6={b8} window_sources={windows}"
    )


if __name__ == "__main__":
    main()
