#!/usr/bin/env python3
"""What instantiating the bit rank-6 bank rung would take.

`beats.py` prices the cheapest way to beat the frontier at +2.167%: absorb the bit
word's rank-6 child family into width-72 banks. This script asks the next question --
what would have to exist for that rung to be a construction rather than a price.

It does three things, all with the same hashed pins:

1.  **The schedule.** For every family of either word whose rank divides the bank
    width, it states the block partition (`m/rank` blocks fill a bank), the bank
    count the family's own volume fills, and whether that count is integral per
    physical copy. The whole-bank condition has a simple form here: for rank `r` on
    width `m`, `r * count % m == 0`, i.e. the family's child count must be divisible
    by `m/r`, the number of blocks per bank.

2.  **The rung's arithmetic.** Re-derived from the frontier certificate: counts per
    copy and over three copies, removed rank mass, banks, the retained ledger and
    stock, the certified saving, and the kappa and gain the assembly returns.

3.  **The checklist.** The supplier's own bank proof
    (`references/queue/coordinated-bank-proof.md`) is a finite verification of a
    *different* absorption: it removes the 2,200 rank-60 gauge exteriors, one per
    selected entrance gauge, and it checks 144 columns of each two-bank address map
    over F2 and over Z. Each item of that proof is listed here with what this rung
    inherits from it, what it would have to add, and what in the queue already
    records the gap.

    python3 -B instantiate.py [--out instantiate.json]
    python3 -B instantiate.py --check
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAVING_GRID = 10 ** 18
BAD = Q(1, 10 ** 16)
BANK_RANK = 6            # the rung this document is about
COPIES = 3               # the certificate's row is the three-copy row


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def rows(profile):
    m = int(profile["m"])
    hist = {int(r): int(n) for r, n in profile["child_multiplicities"].items() if n}
    W, N = int(profile["W"]), int(profile["N"])
    assert sum(r * n for r, n in hist.items()) == m * W - N, "row identity"
    return m, W, N, hist


def row_profile(m, W, N, hist):
    hist = {int(r): int(n) for r, n in hist.items() if n}
    total = sum(r * n for r, n in hist.items())
    assert total == m * W - N, "row identity"
    return dict(m=m, W=W, N=N, L=0, total_rank=total, maxchild=max(hist),
                child_multiplicities={str(r): n for r, n in hist.items()})


def saving_paid(interval, profile):
    """The bit side's own convention in the frontier certificate: with the fallback."""
    low, high = 0, SAVING_GRID // 100
    def moment(a):
        raw = interval.moment(profile, a)
        m, W = profile["m"], profile["W"]
        edges = sum(profile["child_multiplicities"].values())
        lo, hi = interval.log_interval(Q(m))
        elo, ehi = interval.exp_interval(a * lo, a * hi)
        weight = BAD * Q(32 * m * m * edges, W * m)
        return raw["upper"] + weight * ehi, raw["lower"] + weight * elo
    assert moment(Q(low, SAVING_GRID))[0] < 1 and moment(Q(high, SAVING_GRID))[1] > 1
    while high - low > 1:
        mid = (low + high) // 2
        if moment(Q(mid, SAVING_GRID))[0] < 1:
            low = mid
        else:
            high = mid
    assert moment(Q(low, SAVING_GRID))[0] < 1 < moment(Q(high, SAVING_GRID))[1]
    return Q(low, SAVING_GRID)


def schedule(m, hist):
    """Every family whose rank divides the bank width, with its bank arithmetic."""
    out = []
    for rank in sorted(hist):
        if m % rank:
            continue
        blocks = m // rank
        count = hist[rank]
        volume = rank * count
        out.append(dict(
            rank=rank, children=count, blocks_per_bank=blocks,
            rank_volume=volume, banks=volume // m,
            whole_banks=volume % m == 0,
            condition="children divisible by %d" % blocks,
            per_copy_children=count // COPIES if count % COPIES == 0 else None,
            per_copy_banks=(volume // m) // COPIES if volume % m == 0
                            and (volume // m) % COPIES == 0 else None))
    return out


def checklist(rung):
    """The supplier's bank proof, item by item, read against this rung."""
    return [
        dict(item="block partition of the bank",
             in_the_proof="P_s(j) = 1[j div 4 = s] for s = 0..17 and Q_s(j) = "
                          "1[j div 24 = s] for s = 0,1,2, on j = 0..71; each family "
                          "disjoint, idempotent and exhaustive",
             status="new instance, inherited algebra",
             note="a rank-6 partition is the same construction with stride 6 "
                  "(12 blocks), so `S_P S_Q = S_{P+Q}` and `S_P^2 = I` need no new "
                  "proof: the proof states them for any finite disjoint projector "
                  "partition summing to I. The stride-6 partition itself is new."),
        dict(item="normalizer and the child-to-block map",
             in_the_proof="the banked items are the 2,200 rank-60 gauge exteriors, "
                          "one per selected entrance gauge, and the gauge's own "
                          "itinerary supplies the address",
             status="NEW, and blank in the queue",
             note="the rank-6 family is interior dirt with no registered gauge "
                  "address, and no pinned package enumerates it: this is the same "
                  "gap that stops the complex rung (an inventory obligation). The "
                  "counts match exactly -- one block per absorbed child -- but which "
                  "child goes to which block is not in any pin."),
        dict(item="charts for the new block frames",
             in_the_proof="one common invertible weighted chart per bank, with "
                          "inverse; product(A S_P A^-1) = A (product S_P) A^-1",
             status="new instance",
             note="integer kernel bases with fraction-free inverses and replayed "
                  "elementary factors for the stride-6 blocks; the certified proof's "
                  "universal conjugation covers any common weighted chart, so this is "
                  "work rather than new theory."),
        dict(item="the two-bank address-map columns",
             in_the_proof="144 columns of each two-bank address map over F2 and over "
                          "Z, for the endpoint and its inverse, rejecting a missing "
                          "last block and a repeated last block in both rings",
             status="inherited check, new instance",
             note="144 = 2 rings x 72 coordinates, so the check is unchanged in "
                  "shape; it has to be run on the stride-6 address map."),
        dict(item="per-block prime witnesses",
             in_the_proof="prime supply and residual factors below the retained q "
                          "bound",
             status="new supply",
             note="%d blocks over three copies need distinct integer Gram/prime "
                  "witnesses; the certified supply is per block frame, not per bank."
                  % rung["blocks_three_copies"]),
        dict(item="moment-envelope parity",
             in_the_proof="rare-class fraction 10^-16, fallback 32*72^2 children per "
                          "edge, the positive atom/row-adapter toll on its own 10^-24 "
                          "grid, and two independent rational log/exp enclosures "
                          "certifying the accepted moment and rejecting the adjacent "
                          "10^-18 grid point",
             status="already satisfied in this package",
             note="the retained ledger, stock and deficit are stated below and the "
                  "certified saving is recomputed with the supplier's own enclosure "
                  "implementation; the fallback bill is unchanged because the word's "
                  "edges are unchanged."),
        dict(item="the assembly",
             in_the_proof="47 strict constraints and 7 margins at the selected "
                          "parameters",
             status="verified here",
             note="PR207's unchanged rule on the two side savings; the rung is "
                  "bit-binding, so the complex budget is untouched and the binding "
                  "side value is the banked bit row's own."),
        dict(item="stage-private allocation",
             in_the_proof="1100 selected and 47484 undeferred banks per stage, with "
                          "nine physical replicas making each stage-private "
                          "allocation integral",
             status="inference, not verified",
             note="the per-copy bank count here is %s; reading the rung as three "
                  "stage-private families gives %s per stage, so the allocation would "
                  "be integral without replicas -- but no pin states that the rank-6 "
                  "dirt is stage-private, so this is an inference."
                  % (rung["banks_per_copy"], rung["banks_per_copy"] // 3)),
        dict(item="the inherited conditional interfaces",
             in_the_proof="all-input weighted compiler, completed-core routing, stage "
                          "cover, local-ring precision/recovery, prime supply, "
                          "uniform setup, all-size analytic and tape contracts remain "
                          "conditional",
             status="conditional in the record itself",
             note="no finite bank verification discharges these, and neither does "
                  "this package."),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "instantiate.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    assert not sys.flags.optimize, "assertions must stay enabled"

    source = json.loads((HERE / "SOURCE.json").read_text())
    for pin in source["pins"]:
        digest = hashlib.sha256((HERE / pin["path"]).read_bytes()).hexdigest()
        assert digest == pin["sha256"], ("pin hash mismatch", pin["path"])
    interval = module("inst_interval_moment", HERE / "references/pr200/interval_moment.py")
    cert = json.loads((HERE / "references/queue/pr207-coordinated-crossover.certificate.json").read_text())
    m, W, N, hist = rows(cert["bit_profile"])
    assert BANK_RANK in hist, "the rung's family must be in the word" 

    # ---- the schedule of every bankable family on both words ----------------
    words = {}
    for side, key in (("bit", "bit_profile"), ("complex", "complex_profile")):
        w_m, w_W, w_N, w_hist = rows(cert[key])
        words[side] = dict(m=w_m, W=w_W, deficit=w_N, families=len(w_hist),
                           schedule=schedule(w_m, w_hist))
    rung_schedule = [row for row in words["bit"]["schedule"] if row["rank"] == BANK_RANK][0]
    assert rung_schedule["whole_banks"] and rung_schedule["per_copy_banks"], \
        "the rung must fill whole banks with an integral per-copy count"

    # ---- the rung's arithmetic, re-derived ----------------------------------
    count_three = hist[BANK_RANK]
    count_copy = count_three // COPIES
    assert count_three % COPIES == 0, "the family is integral per copy"
    blocks_per_bank = m // BANK_RANK
    banks_copy = rung_schedule["per_copy_banks"]
    taken = BANK_RANK * count_three
    kept = {r: n for r, n in hist.items() if r != BANK_RANK}
    mass = sum(r * n for r, n in kept.items())
    stock, leftover = divmod(mass + N, m)
    assert leftover == 0 and stock == W - taken // m, "row identity after absorption"
    base = saving_paid(interval, row_profile(m, W, N, hist))
    banked = saving_paid(interval, row_profile(m, stock, N, kept))
    published = Q(cert["a_bit"])
    assert abs(base / published - 1) < Q(1, 10 ** 12), "the certificate's bit saving"
    grid = 10 ** 16
    kappa = lambda a: Q((a / (1 + a)).numerator * grid // (a / (1 + a)).denominator, grid)
    frontier = kappa(base)
    gain = kappa(banked) / frontier - 1
    rung = dict(
        family_rank=BANK_RANK, bank_width=m, blocks_per_bank=blocks_per_bank,
        children_three_copies=count_three, children_per_copy=count_copy,
        rank_volume=taken, banks_three_copies=taken // m, banks_per_copy=banks_copy,
        blocks_three_copies=blocks_per_bank * (taken // m),
        blocks_per_copy=blocks_per_bank * banks_copy,
        stock_before=W, stock_after=stock, stock_fall=W - stock,
        rank_mass_before=m * W - N, rank_mass_after=mass,
        deficit=str(N), maxchild_after=max(kept),
        retained_families=len(kept), certified_saving=str(banked),
        certified_saving_decimal=float(banked), frontier_kappa=str(frontier),
        kappa=str(kappa(banked)), gain=str(gain))
    # one block per absorbed child, count for count: the bijection is a bijection
    assert rung["blocks_per_copy"] == rung["children_per_copy"], \
        "one rank-6 block per absorbed child"
    assert blocks_per_bank * BANK_RANK == m, "the blocks tile the bank"
    # the block patterns that tile the same width: this rung's, and the certified ones
    uniform = {"rank6_this_rung": (blocks_per_bank, BANK_RANK), "rank4_certified": (18, 4),
               "rank24_certified": (3, 24)}
    sums = {name: count * rank for name, (count, rank) in uniform.items()}
    sums["mixed_certified"] = 6 * 4 + 2 * 24
    tilings = dict(
        patterns={name: "%d x %d" % pair for name, pair in uniform.items()} |
                 {"mixed_certified": "6 x 4 + 2 x 24"},
        sums=sums, all_tile_the_width=all(value == m for value in sums.values()))
    assert tilings["all_tile_the_width"], tilings
    assert tilings["patterns"]["rank6_this_rung"] == "%d x %d" % (blocks_per_bank, BANK_RANK)

    checklist_rows = checklist(rung)
    out = dict(
        status="Read-only: no construction, no new word, no bank. This states what "
               "the +2.167% rung's arithmetic is and what the supplier's published "
               "bank proof already covers for it.",
        method="the frontier certificate's own three-copy rows, the supplier's "
               "enclosure implementation, and the supplier's bank proof read item by "
               "item; every count below is derived, not quoted",
        source=dict(certificate="references/queue/pr207-coordinated-crossover.certificate.json",
                    bank_proof="references/queue/coordinated-bank-proof.md",
                    arithmetic="references/pr200/interval_moment.py"),
        validated=dict(
            certificate_bit_saving=str(published),
            recomputed_bit_saving=str(base),
            relative_gap=str(base / published - 1),
            note="the recomputation is the certificate's own value to sixteen "
                 "significant digits; the residual is in beats.json's validations"),
        schedule={side: words[side] for side in words},
        rung=rung,
        tilings=tilings,
        checklist=checklist_rows,
        verdict=(
            "The rung's arithmetic is exact and its saving is certifiable with the "
            "tooling already in this package. Its construction reduces to a new "
            "block stride plus the items the certified bank spent on the gauge "
            "exteriors: the universal projector algebra is inherited (the proof "
            "states it for any disjoint exhaustive partition), the 144-column "
            "address check and the moment-envelope parity are inherited in shape, "
            "and the per-copy allocation is integral, so this rung does not need the "
            "nine physical replicas the certified allocation used. What does not "
            "exist is the part that identifies the dirt: no pin enumerates the "
            "word's rank-6 children, so the normalizer, the charts and the prime "
            "witnesses have nothing to be attached to yet. That is the same blank "
            "shape as the complex rung's inventory obligation, and it is smaller: "
            "one family of one word, whose counts and bank schedule are already "
            "pinned by this file."),
        limits=[
            "No bank is built, no chart is computed, no witness is supplied and no "
            "physical word is replayed: the checklist states what would be needed.",
            "The stage-private reading is an inference (the per-copy count is "
            "divisible by three); no pin says the rank-6 dirt is stage-private.",
            "The rank-6 family is interior dirt: the certified proof removed the "
            "entrance exteriors, and the frontier profile no longer carries them.",
        ])
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if args.check:
        if args.out.read_text() != text:
            print("[check] MISMATCH: instantiate.json does not match a fresh run")
            return 1
        print("[check] instantiate.json matches a fresh run byte for byte")
        return 0
    args.out.write_text(text, newline="\n")

    print("[rung] absorb the bit word's rank-%d family on width %d" % (BANK_RANK, m))
    print("       %d children over three copies = %d per copy; %d blocks per bank, "
          "one per child" % (count_three, count_copy, blocks_per_bank))
    print("       %d banks over three copies = %d per copy (integral); volume %d"
          % (taken // m, banks_copy, taken))
    print("       stock %d -> %d (fall %d), rank mass %d -> %d, deficit %s unchanged"
          % (W, stock, W - stock, m * W - N, mass, N))
    print("       saving %s -> %s; kappa %s -> %s (%+.4f%%)"
          % (base, banked, frontier, kappa(banked), float(gain) * 100))
    for row in words["bit"]["schedule"] + words["complex"]["schedule"]:
        print("       [%s] rank %-2d: %d blocks/bank, %-5s banks, children divisible "
              "by %d: %s" % ("bankable" if row["whole_banks"] else "no bank ",
                             row["rank"], row["blocks_per_bank"], row["banks"],
                             row["blocks_per_bank"], "yes" if row["whole_banks"] else "NO"))
    for item in checklist_rows:
        print("[%-34s] %s" % (item["status"], item["item"]))
    print("[write] " + str(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
