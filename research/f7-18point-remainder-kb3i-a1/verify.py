"""KB3i registered replay: re-derives every number cited in the README/PR for
the 18-point cover question remainder ((4,2)/(3,3)/(11,7)/(9,9)), set level.

Modes:
  quick   vendored pins + anchor reproduction (FOURIER 7,1 =175/239,
          OBSTRUCTION 696/504/192, CLASSIFY 32=32 TIGHT cases=6720),
          the complete m=3 reduced-covering census (parity-shortcut DEMOTION),
          and the (11,7)/(9,9) identity-frontier numbers.
          marker PASS_KB3I_QUICK
  full    quick + the complete m=4 sum-10 split censuses (the m=5 ground
          truth: (2,8),(4,6) cover; (1,9),(3,7),(5,5) empty) and the (5,5)
          self-obstruction localization.  Slower (minutes).
          marker PASS_KB3I_FULL
  search  the bounded construction search ceiling (route c).  marker PASS_KB3I_SEARCH

Everything is exact integer arithmetic (int bitmasks, no floats).  The census
counts below are COMPLETE enumerations (brute force over all subset pairs at
the stated sizes); a zero count with complete enumeration PROVES the split
empty at that (m, split).
"""

import hashlib
import sys
import time
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))
sys.stdout.reconfigure(encoding="utf-8")

import cover18 as c18  # noqa: E402
import tight  # noqa: E402
import vanish  # noqa: E402

VENDOR_PINS = {
    "vendor/tight.py": "14670ef2d3df9e4ecc9e1db962f4e8cb77545d1c889144352760c1fd14e2273b",
    "vendor/cover18.py": "24c6a2f4911dc2d5de76972eb5ae93dc4e66d8fa1e904443de6d0638e70c0a04",
    "vendor/vanish.py": "6c605c54074f725321c5d770d538a652bf7727598a128270831f92fe7b9746d9",
    "vendor/agent64_cover17.py": "082bc838134cba9754368cff894d53c729467a689b4cafee8374423688d93654",
    "vendor/agent64_search17.py": "9eb1bf79ffb99b0efcdaf57916c493bc781abd4a0096d584dc6bc6ca294bf674",
    "vendor/anchors.py": "73d73a9b94539403448d7ff8c914c03711907f75c019c4ccb6843b32c259e8e7",
}


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check_pins():
    for rel, want in VENDOR_PINS.items():
        got = sha256_file(HERE / rel)
        assert got == want, (rel, got, want)
    print("PIN all %d vendored engines sha256 match" % len(VENDOR_PINS), flush=True)


# ---------------------------------------------------- reduced-covering census


def _build(m):
    gsize = 1 << m
    allg = (1 << gsize) - 1
    xors = [[1 << (i ^ j) for j in range(gsize)] for i in range(gsize)]

    def trans(mask, a):
        out = 0
        x = mask
        while x:
            lsb = x & -x
            out |= xors[lsb.bit_length() - 1][a]
            x ^= lsb
        return out

    def sumset(mx, my):
        out = 0
        x = mx
        while x:
            lsb = x & -x
            out |= trans(my, lsb.bit_length() - 1)
            x ^= lsb
        return out

    return gsize, allg, sumset


def _mask_of(idxs):
    m = 0
    for i in idxs:
        m |= 1 << i
    return m


def census_split_count(m, a, b):
    """COMPLETE count of reduced covering (A,B) pairs in F2^m with |A|=a,|B|=b.
    Returns (covers, cross_covering, self_covering_when_cross, max_selfunion)."""
    gsize, allg, sumset = _build(m)
    Alist = [_mask_of(c) for c in combinations(range(gsize), a)]
    Blist = [_mask_of(c) for c in combinations(range(gsize), b)]
    covers = 0
    cross_cov = 0
    self_when_cross = 0
    max_su = -1
    for am in Alist:
        ssa = sumset(am, am)
        for bm in Blist:
            if sumset(am, bm) != allg:
                continue
            cross_cov += 1
            su = ssa | sumset(bm, bm)
            su_sz = su.bit_count()
            if su_sz > max_su:
                max_su = su_sz
            if su == allg:
                self_when_cross += 1
                covers += 1
    return covers, cross_cov, self_when_cross, max_su


def m3_census():
    """Complete reduced-covering census of F2^3 by split; return the both-odd
    nonempty list and the (5,5),(3,3) counts."""
    gsize, allg, sumset = _build(3)
    both_odd_nonempty = []
    counts = {}
    for a in range(9):
        for b in range(9):
            Alist = [_mask_of(c) for c in combinations(range(gsize), a)]
            Blist = [_mask_of(c) for c in combinations(range(gsize), b)]
            cnt = 0
            for am in Alist:
                ssa = sumset(am, am)
                for bm in Blist:
                    if sumset(am, bm) == allg and (ssa | sumset(bm, bm)) == allg:
                        cnt += 1
            counts[(a, b)] = cnt
            if cnt > 0 and a % 2 == 1 and b % 2 == 1:
                both_odd_nonempty.append((a, b))
    return counts, both_odd_nonempty


def mode_quick():
    t0 = time.time()
    check_pins()
    # Anchor: PR 2961 FOURIER (7,1)
    fid = tight.fourier_71_identity()
    assert (fid["m5_k5"]["need"], fid["m5_k5"]["lower_bound"]) == (175, 239), fid
    print("ANCHOR PR2961 FOURIER (7,1) need=175 lower=239 contradiction=True", flush=True)
    # Anchor: PR 2933 CLASSIFY 32=32 TIGHT cases=6720
    res7 = vanish.check_tight_equality(3)
    assert res7["checked"] == 6720 and res7["ok"], res7
    print("ANCHOR PR2933 CLASSIFY tight-equality Sidon m=3 cases=6720 ok=true", flush=True)
    tight_seen = 0
    for (s, t) in [(12, 6), (11, 7), (10, 8), (9, 9)]:
        tab = vanish.class_table(s, t, m=6)
        for side in ("A_vanish", "D_vanish"):
            for c in tab[side]:
                if c["tight"]:
                    tight_seen += 1
    assert tight_seen == 2, tight_seen
    print("ANCHOR PR2933 CLASSIFY 32=32 TIGHT count=2 across splits", flush=True)
    # Anchor: PR 2870 OBSTRUCTION
    sq = c18.squeeze_numbers(7, 11, 6)
    assert (sq["parseval_remainder"], sq["max_allowed"], sq["deficit"]) == (696, 504, 192), sq
    print("ANCHOR PR2870 OBSTRUCTION parseval=696 allowed=504 deficit=192", flush=True)

    # PARITY-SHORTCUT DEMOTION: complete m=3 census.
    counts, bon = m3_census()
    assert counts[(5, 5)] == 3136, counts[(5, 5)]
    assert counts[(7, 7)] == 64, counts[(7, 7)]
    assert counts[(3, 3)] == 0, counts[(3, 3)]
    expected_bon = [(3, 5), (3, 7), (5, 3), (5, 5), (5, 7), (7, 3), (7, 5), (7, 7)]
    assert bon == expected_bon, bon
    print("DEMOTION m=3 COMPLETE: both-odd covers EXIST: %s" % (bon,), flush=True)
    print("  (5,5) covers=%d, (7,7) covers=%d, (3,3) covers=0"
          % (counts[(5, 5)], counts[(7, 7)]), flush=True)
    print("  => 'both-odd impossible by parity' is FALSE; cannot kill (11,7)/(9,9)", flush=True)

    # IDENTITY FRONTIER for (11,7)/(9,9).
    for (s, t, eo_want, eh_want) in ((11, 7, 13, 42), (9, 9, 17, 34)):
        eo = s * t - 64
        eh = c18.even_half_max(7, s, t)
        assert eo == eo_want and eh == eh_want, (s, t, eo, eh)
        vals = c18.rho_square_values(eo)
        sqz = c18.squeeze_numbers(7, s, t)
        print("FRONTIER (%d,%d): E_o=%d even_half_max=%d min_sum_rho2=%d squeeze_opposite=%s"
              % (s, t, eo, eh, vals[0], sqz["opposite_parity"]), flush=True)
    print("PASS_KB3I_QUICK seconds=%.1f" % (time.time() - t0), flush=True)


def mode_full():
    mode_quick()
    t0 = time.time()
    # m=5 ground truth: complete m=4 sum-10 split censuses.
    print("=== m=5 ground truth: COMPLETE m=4 reduced covering by sum-10 split ===", flush=True)
    expect = {(2, 8): ">0", (4, 6): ">0", (1, 9): 0, (3, 7): 0, (5, 5): 0}
    for (a, b), want in expect.items():
        covers, cross_cov, self_when_cross, max_su = census_split_count(4, a, b)
        if want == ">0":
            assert covers > 0, (a, b, covers)
        else:
            assert covers == 0, (a, b, covers)
        print("  (%d,%d): covers=%d cross_covering=%d self_when_cross=%d max_selfunion=%d/16"
              % (a, b, covers, cross_cov, self_when_cross, max_su), flush=True)
    # (5,5) self obstruction localization.
    covers, cross_cov, self_when_cross, max_su = census_split_count(4, 5, 5)
    assert covers == 0 and self_when_cross == 0 and cross_cov > 0, (covers, self_when_cross, cross_cov)
    assert max_su == 15, max_su
    print("SELF-OBSTRUCTION (5,5): cross_covering=%d, self_covering_when_cross=%d, "
          "max_self_union=%d/16 (never 16)" % (cross_cov, self_when_cross, max_su), flush=True)
    print("PASS_KB3I_FULL seconds=%.1f" % (time.time() - t0), flush=True)


def mode_search():
    t0 = time.time()
    check_pins()
    rec = c18.search_direct(k=18, restarts=40, seed=1, seconds=25.0, n=7)
    print("SEARCH k=18 direct: found=%s score=%d/128 (record ceiling 119/128)"
          % (rec["found"], rec["score"]), flush=True)
    assert not rec["found"], rec
    print("PASS_KB3I_SEARCH seconds=%.1f" % (time.time() - t0), flush=True)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "quick"
    modes = {"quick": mode_quick, "full": mode_full, "search": mode_search}
    if mode not in modes:
        raise SystemExit("usage: verify.py quick|full|search")
    modes[mode]()


if __name__ == "__main__":
    main()
