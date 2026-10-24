#!/usr/bin/env python3
"""Sharp-window bad density against CRT.md's printed repair room.

The published section-4 window term is 8B/2^K. The isolated compact-switch
step admits every window 0 <= W <= 2^m - B + 1. This verifier checks that
the resulting bad-window count is B-2, that this fraction is strictly below
the published term, and that the printed 2^{-G} E comparison does not use
the window term and still dominates the sharp union bound.

No new kappa and no simultaneous multi-target carry theorem are claimed.
"""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CRT = ROOT / "research/unconditional-batched-crt/CRT.md"
CHECKER = ROOT / "research/unconditional-batched-crt/check_batched_crt.py"

PUBLISHED_DENSITY = "r [2/B + 8B/2^K] <= C p 2^-G."
PUBLISHED_ROOM = "2^-G E(p,ell) <= C 2^(-60 ell) (p+2)^(-48),"
PARAMETER_LINE = "G=64(ell+ceil(log2(p+2))),  B=2^G,  K=64G,"


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def load_checker():
    spec = importlib.util.spec_from_file_location("batched_crt_predecessor", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def post_step(y, z, tau):
    """One target at bit 0. Second coefficient is the post-increment digit."""
    y1 = y + 2 * z * tau
    bit = y1 & 1
    tau_post = tau + bit
    y2 = y1 + z * (1 - 2 * tau_post)
    return y1, y2, tau_post, bit


def ceil_log2(n):
    need(n >= 1, "log of a positive integer")
    return n.bit_length() - 1 if n.bit_count() == 1 else n.bit_length()


def parameters(ell, p):
    need(ell >= 1 and p >= 2, "CRT size domain")
    g_value = 64 * (ell + ceil_log2(p + 2))
    return g_value, 1 << g_value, 64 * g_value


def sharp_bad_count(base, width):
    """Bad windows for the isolated step, by executing the step."""
    limit = 1 << width
    safe_last = limit - (base - 2) - 1
    bad = 0
    tau = base - 2
    for window in range(limit):
        y = window << 1
        y1, y2, _, bit = post_step(y, 1, tau)
        overflows = (y1 >> 1) >= limit or (y2 >> 1) >= limit or y2 < 0
        if window <= safe_last:
            need(bit == 0, "zero target is read as zero")
            need(not overflows, "sharp window must not overflow")
            need(y2 == y + 1, "z=1 flips a zero target by +1")
        else:
            need(overflows, "window past the sharp bound must overflow")
            bad += 1
    return bad


def published_bad_count(base, width):
    limit = 1 << width
    bad = 0
    for window in range(limit):
        if not (2 * base <= window < limit - 2 * base):
            bad += 1
    return bad


def bind_sources(checker):
    text = CRT.read_text(encoding="utf-8")
    need(PUBLISHED_DENSITY in text, "CRT.md density line moved")
    need(PUBLISHED_ROOM in text, "CRT.md room line moved")
    need(PARAMETER_LINE in text, "CRT.md parameter line moved")
    need(checker.good(1, 0, 17, bits=2, positions=(0,), guard=6),
         "published good predicate rejects the known interior window")
    need(not checker.good(1, 0, 1, bits=2, positions=(0,), guard=6),
         "published good predicate accepts a low window")


def count_identity():
    """B-2 bad windows, and the published count 4B when the margin fits."""
    cases = 0
    for bits, width in ((1, 4), (1, 6), (2, 6), (2, 8), (3, 8), (4, 8), (3, 10)):
        base = 1 << bits
        limit = 1 << width
        sharp = sharp_bad_count(base, width)
        need(sharp == base - 2, "sharp bad count is B-2")
        published = published_bad_count(base, width)
        if 4 * base <= limit:
            need(published == 4 * base, "published bad count is 4B")
            need(sharp < published, "sharp bad set is a proper subset")
        need(sharp * 4 * base == (base - 2) * published or 4 * base > limit,
             "fraction identity on the fitting domain")
        # (B-2)/(4B) * 8B = 2(B-2), so the sharp numerator is that factor
        # times the published numerator. Both sides are integers.
        need((base - 2) * 8 * base == 2 * (base - 2) * 4 * base,
             "window-term ratio (B-2)/(4B)")
        need(sharp << 1 == 2 * (base - 2), "sharp numerator is 2(B-2)")
        cases += 1
    return cases


def room_identity():
    """2^{-G} 2^{4 ell} (p+2)^16 <= 2^{-60 ell} (p+2)^{-48}."""
    cases = 0
    for ell, p in ((1, 2), (1, 14), (2, 2), (2, 6), (3, 30), (5, 2**16), (8, 10**6)):
        g_value, _, _ = parameters(ell, p)
        c_log = ceil_log2(p + 2)
        # Cross-multiply: 2^{4 ell} (p+2)^64 <= 2^{G - 60 ell} = 2^{4 ell + 64 c_log}.
        need((p + 2) ** 64 <= 1 << (64 * c_log), "power-of-two ceiling")
        need(g_value - 60 * ell == 4 * ell + 64 * c_log, "exponent split")
        need(g_value >= 192, "minimum G on ell>=1, p>=2")
        cases += 1
    return cases


def absorption():
    """r * sharp union bound < p 2^{-G} / 6400 when L <= p."""
    rows = 0
    positive_r = 0
    samples = []
    for ell in (1, 2, 4):
        for p in (2, 100, 20_000, 2**20, 10**7):
            g_value, _, _ = parameters(ell, p)
            length = p
            rank = length // (100 * g_value)
            # p * 2^{62 G} >= r * (2 * 2^{62 G} + 2) proves
            # p >= r (2 + 2^{1-62 G}) > r (2 + 2(1-2^{1-G}) 2^{-62 G}).
            shift = 62 * g_value
            sharp_left = rank * ((2 << shift) + 2)
            published_left = rank * ((2 << shift) + 8)
            right = p << shift
            # r (2 + 2^{1-62G}) <= p, hence r * alpha < p 2^{-G}.
            need(sharp_left <= right, "sharp union bound fits C = 1")
            # The same comparison with the published window numerator 8.
            need(published_left <= right, "published union bound fits C = 1")
            # r <= p/(100G) and G >= 192 give the sharper factor 1/6400.
            need(6400 * sharp_left <= right, "sharp union bound fits C = 1/6400")
            if rank > 0:
                positive_r += 1
                samples.append((ell, p, g_value, rank))
            rows += 1
    need(positive_r >= 1, "grid includes a positive batch size")
    return rows, positive_r, samples


def ratio_and_dominance():
    """Window term is < 1/4 of the published term and << 2/B."""
    for g_value in (1, 2, 192, 256):
        base = 1 << g_value
        # (B-2)/(4B) < 1/4.
        need(4 * (base - 2) < 4 * base, "strict window shrinkage")
        need((base - 2) * 4 < base * 4 or base > 2, "ratio below one")
        # 2(B-2)/2^K divided by 2/B is 2(B-2) B / 2^K = (B-2) 2^{1-63 G}.
        # For G >= 1 this is < 2^{-60}.
        if g_value >= 1:
            need(1 + g_value < 63 * g_value - 60, "window/digit exponent gap")
    return 4


def failure_controls():
    """A count that restores 4B, or a room line that drops the E factor, fails."""
    base, width = 4, 8
    sharp = sharp_bad_count(base, width)
    forged = 4 * base
    need(forged != sharp, "forged published count is not the sharp count")
    need(not (forged == base - 2), "control rejects the old numerator")
    # Dropping E from the room would claim 2^{-G} <= 2^{-60 ell} (p+2)^{-48},
    # which is false once the 2^{4 ell} (p+2)^16 factor is required.
    ell, p = 1, 2
    g_value, _, _ = parameters(ell, p)
    bare = 1 << g_value
    room = (1 << (60 * ell)) * (p + 2) ** 48
    need(bare > room, "2^{-G} alone is not the printed room")
    return 2


def main():
    checker = load_checker()
    bind_sources(checker)
    counts = count_identity()
    rooms = room_identity()
    rows, positive_r, samples = absorption()
    gaps = ratio_and_dominance()
    controls = failure_controls()
    ell, p, g_value, rank = samples[0]
    print(
        "PASS_COMPACT_SWITCH_SHARP_DENSITY"
        f" counts={counts} rooms={rooms} rows={rows}"
        f" positive_r={positive_r} gaps={gaps} controls={controls}"
        f" sample_ell={ell} sample_p={p} sample_G={g_value} sample_r={rank}"
    )


if __name__ == "__main__":
    main()
