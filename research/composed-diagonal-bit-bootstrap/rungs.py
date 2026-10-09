#!/usr/bin/env python3
"""The big rungs: what absorbing whole child families into the banks is worth.

`targets.py` re-ranks a word's dirty children, which re-uses the same stock. The
bank construction does something stronger: the dirt of an *absorbed* family leaves
the ledger, so by the row identity `W = (mass + D)/m` the stock falls with it and
the paid moment pays less twice over.

A bank is a width-`m` coordinate-block partition, so a schedule absorbs exactly when
the families it takes have a total rank volume that is a whole number of banks over
the row's normalization; otherwise a bank would be left partly empty. That is a
cheap arithmetic condition on which families can be taken together, and it is
checked here for every candidate.

The search has two stages. Every subset of up to `MAX_TYPES` families of either word
is screened with the ledger form this package prices with, `C = (1 - mass/(W m))/L`;
the best few per subset size are then priced *exactly*, together with the first
search's window (every subset of the smallest six families and every prefix of the
ledger) so that nothing regresses. Each priced schedule is what PR184's unchanged
assembly would return if the schedule were built; the physical side -- bank charts,
normalizers, the F2 and defining-integer columns, per-bank prime witnesses -- is the
supplier's harness and is not done here. The number of families a rung takes is the
number of new residual types that harness would have to instantiate.

    python3 -B rungs.py [--out rungs.json]
"""
import argparse
import importlib.util
import itertools
import json
import math
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_TYPES = 4       # families per word searched in all combinations (across all ranks)
NEW_TOP = 6         # of each subset size, exactly priced
OLD_WINDOW = 6      # the first search's window: every subset of the smallest families
PREFIXES = 22       # and every prefix of the ledger


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def certified(interval, levers, profile):
    """`levers.certified` with a widening upper bracket.

    A deep absorption can price far above the frontier row's own bracket, so the
    bracket doubles until the paid moment refuses. On the frontier rows this repeats
    `levers.certified` exactly, which is asserted where they are priced.
    """
    assert levers.paid_moment(interval, profile, Q(0))["upper"] < 1, "zero-saving contraction"
    # The moment's exponential enclosure is valid only for `a*ln(m) < 1/4`, which caps
    # the priceable saving at 1/24; a ledger that still pays there is past the model.
    cap = levers.GRID // 24
    high = levers.GRID // 100
    while high < cap and levers.paid_moment(interval, profile, Q(high, levers.GRID))["lower"] <= 1:
        high *= 2
    if levers.paid_moment(interval, profile, Q(min(high, cap), levers.GRID))["lower"] <= 1:
        raise ValueError("saving beyond the enclosure domain")
    low = 0
    while high - low > 1:
        mid = (low + high) // 2
        if levers.paid_moment(interval, profile, Q(mid, levers.GRID))["upper"] < 1:
            low = mid
        else:
            high = mid
    accepted = levers.paid_moment(interval, profile, Q(low, levers.GRID))["upper"]
    rejected = levers.paid_moment(interval, profile, Q(high, levers.GRID))["lower"]
    assert accepted < 1 < rejected, "adjacent grid exclusion"
    return Q(low, levers.GRID)


def screen(m, W, hist):
    """The ledger form the package prices with, for ranking only.

    `C = (1 - mass/(W m))/L` with `L` the rank-mass-weighted mean of `ln(m/r)` is the
    decomposition `targets.py` documents; the exact interval moment decides every
    priced value, this only chooses which candidates are worth pricing exactly. Callers
    keep candidates in Python floats, so it never enters a pin.
    """
    mass = sum(r * n for r, n in hist.items())
    if mass <= 0:
        return 0.0
    mean_log = sum(r * n * math.log(m / r) for r, n in hist.items()) / mass
    return float(1 - Q(mass, m * W)) / mean_log


def absorb(m, W, D, hist, families):
    """Take the listed child families out of the ledger and into the banks."""
    kept = {r: n for r, n in hist.items() if r not in families}
    taken = sum(r * n for r, n in hist.items() if r in families)
    assert taken and kept, "a schedule absorbs something and leaves a ledger"
    remainder_mass = m * W - D - taken
    assert remainder_mass.denominator == 1, "integral rank mass"
    mass = int(remainder_mass)
    assert sum(r * n for r, n in kept.items()) == mass, "row identity after absorption"
    stock, remainder = divmod(mass + D, m)
    assert remainder == 0, "half-filled stock"
    return int(stock), mass, kept, taken


def whole_banks(m, W, hist, families):
    """The bank condition on its own: a family set absorbs only if it fills whole banks."""
    return all(families) and sum(r * hist[r] for r in families) % m == 0


def bankable_alone(m, hist):
    """The families whose blocks tile a bank by themselves.

    A bank is a width-`m` block partition, so a family can be banked on its own only when
    its rank divides the width and its own volume is a whole number of banks. #207's bank
    schedule is exactly this shape -- `18 x rank-4`, `3 x rank-24`, and the mixed
    `6 x rank-4 + 2 x rank-24` -- so banking the families separately is sound, and the
    schedules it admits need no new block shape at all. Everything else in this tool is an
    upper bracket: it keeps only the volume condition, which is what the *certified* banks
    of #197/#205/#207 satisfy (their absorbed rank 60 does not divide 72 either).
    """
    return sorted(r for r in hist if m % r == 0 and (r * hist[r]) % m == 0)


def summarize(pools, base, targets, now):
    """Pair every bit schedule with every complex one and summarize the rungs."""
    def pair(bit, complex_):
        """PR184's unchanged budget and its exact 10^-10 grid."""
        budget = min(bit, (1 - targets.STOP) * complex_ - Q(1, targets.SELECT_GRID))
        return targets.assembly_kappa(budget), budget

    combos = []
    for bit_row in pools["bit"]:
        for complex_row in pools["complex"]:
            kappa, budget = pair(Q(bit_row["coarse"]), Q(complex_row["coarse"]))
            combos.append(dict(kappa=kappa, budget=budget,
                               types=bit_row["types"] + complex_row["types"],
                               bit=bit_row, complex=complex_row, gain=kappa / now - 1))
    frontier = targets.assembly_kappa(
        pair(base["bit"], base["complex"])[1])
    assert frontier == now, "every pool must contain the frontier rows themselves"
    above = [c for c in combos if c["kappa"] > now]
    ladder = {}
    for budget_types in list(range(1, 9)) + [12, 24]:
        step = [c for c in combos if c["types"] <= budget_types]
        if step:
            top = max(step, key=lambda c: c["kappa"])
            ladder[str(budget_types)] = dict(
                kappa=str(top["kappa"]), gain=str(top["gain"]), types=top["types"],
                bit_families=top["bit"]["families"],
                complex_families=top["complex"]["families"],
                bit_coarse=top["bit"]["coarse"], complex_coarse=top["complex"]["coarse"],
                bit_banks=top["bit"]["banks"], complex_banks=top["complex"]["banks"],
                binding=("bit" if Q(top["bit"]["coarse"]) <= (1 - targets.STOP)
                         * Q(top["complex"]["coarse"]) - Q(1, targets.SELECT_GRID)
                         else "complex"))
    cheapest = min(above, key=lambda c: (c["types"], -c["kappa"])) if above else None
    best = max(combos, key=lambda c: c["kappa"])

    def clean(item):
        if item is None:
            return None
        return {k: v for k, v in item.items() if k not in ("bit", "complex")} | dict(
            kappa=str(item["kappa"]), budget=str(item["budget"]), gain=str(item["gain"]),
            bit={k: v for k, v in item["bit"].items()},
            complex={k: v for k, v in item["complex"].items()})

    return dict(pairs_considered=len(combos), pairs_above_frontier=len(above),
                cheapest_pair=clean(cheapest), best_pair=clean(best), type_ladder=ladder)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "rungs.json")
    args = parser.parse_args()
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    assert not sys.flags.optimize, "assertions must stay enabled"
    interval = module("rungs_interval_moment", HERE / "references/pr200/interval_moment.py")
    levers = module("rungs_levers", HERE / "levers.py")
    targets = module("rungs_targets", HERE / "targets.py")

    newest = json.loads(
        (HERE / "references/queue/pr207-coordinated-crossover.certificate.json").read_text())
    sides, pools = {}, {"strict": {}, "volume": {}}
    for side, key in (("bit", "bit_profile"), ("complex", "complex_profile")):
        m, W, D, hist = targets.rows(newest[key])
        word = levers.row(m, W, D, hist)
        base = certified(interval, levers, word)
        # The widened certifier must reproduce the frontier row's own bracket exactly.
        assert base == levers.certified(interval, word), side
        ranks = sorted(hist)
        mass = int(m * W - D)

        # Stage one: every subset of up to MAX_TYPES families of either word, screened
        # across all ranks, keeping the best few of each size for exact pricing.
        candidates, kept_screen, screened = [], {}, 0
        for size in range(1, MAX_TYPES + 1):
            for combo in itertools.combinations(ranks, size):
                families = frozenset(combo)
                if not whole_banks(m, W, hist, families):
                    continue
                screened += 1
                kept = {r: n for r, n in hist.items() if r not in families}
                if not kept:
                    continue
                taken = sum(r * hist[r] for r in families)
                candidates.append((screen(m, W - taken // m, kept), families, taken))
        for size in range(1, MAX_TYPES + 1):
            ranked = sorted((item for item in candidates if len(item[1]) == size),
                            key=lambda item: -item[0])
            for score, families, taken in ranked[:NEW_TOP]:
                kept_screen[families] = score

        # Stage two: the first search's window, so nothing that was priced before is lost.
        old_class = [frozenset(c) for size in range(1, OLD_WINDOW + 1)
                     for c in itertools.combinations(ranks[:OLD_WINDOW], size)]
        old_class += [frozenset(ranks[:end]) for end in range(1, min(PREFIXES, len(ranks)) + 1)]

        priced, state = {}, {"beyond": 0}

        def price(families):
            """Price one family set once, or return None when it is not a schedule."""
            families = frozenset(families)
            if families not in state:
                row = None
                if families and whole_banks(m, W, hist, families):
                    try:
                        stock, remainder, kept, taken = absorb(m, W, D, hist, families)
                        coarse = certified(interval, levers, levers.row(m, stock, D, kept))
                    except (AssertionError, ValueError):
                        state["beyond"] += 1
                    else:
                        row = dict(
                            families=sorted(families), types=len(families),
                            banks=taken // m, absorbed_rank_mass=taken,
                            absorbed_share_of_ledger=float(Q(taken, m * W - D)),
                            stock=stock, rank_mass=remainder, children=sum(kept.values()),
                            maxchild=max(kept), coarse=str(coarse),
                            screen=round(screen(m, stock, kept), 12))
                state[families] = row
            return state[families]

        base_row = dict(families=[], types=0, banks=0, absorbed_rank_mass=0,
                        absorbed_share_of_ledger=0.0, stock=W, rank_mass=mass,
                        children=sum(hist.values()), maxchild=max(hist),
                        coarse=str(base), screen=round(screen(m, W, hist), 12))

        # The families whose blocks tile a bank by themselves: banking them separately is
        # sound, and it needs no block shape the word does not already use.
        on_their_own = bankable_alone(m, hist)
        strict_rows = [price(combo) for size in range(1, MAX_TYPES + 1)
                       for combo in itertools.combinations(on_their_own, size)]
        strict_rows = [row for row in strict_rows if row]
        volume_rows = [row for row in (price(f) for f in old_class + list(kept_screen)) if row]
        assert strict_rows or volume_rows, "some family set must be bankable"
        strict_rows.sort(key=lambda item: -Q(item["coarse"]))
        volume_rows.sort(key=lambda item: -Q(item["coarse"]))
        pools["strict"][side] = [base_row] + strict_rows
        pools["volume"][side] = [base_row] + volume_rows
        singles = [item for item in strict_rows if item["types"] == 1]
        sides[side] = dict(m=m, W=W, deficit=str(D), rank_mass=mass,
                           children=sum(hist.values()), maxchild=max(hist),
                           families=len(ranks), coarse=str(base), coarse_decimal=float(base),
                           tiles_the_bank=on_their_own, combinations_screened=screened,
                           priced=sum(1 for key, row in state.items()
                                      if key != "beyond" and row),
                           unpriceable=state["beyond"],
                           single_family=singles[0] if singles else None,
                           strict_schedules=strict_rows[:6],
                           volume_schedules=volume_rows[:6])

    def budget_of(bit, complex_):
        return min(bit, (1 - targets.STOP) * complex_ - Q(1, targets.SELECT_GRID))

    now = targets.assembly_kappa(budget_of(Q(sides["bit"]["coarse"]),
                                           Q(sides["complex"]["coarse"])))
    assert now == Q(213497, 312500000), "the ladder must start at the frontier word's price"
    published = Q(1366380910073, 2 * 10 ** 15)
    assert abs(now - published) < Q(1, targets.SELECT_GRID), "frontier claim"
    base = dict(bit=Q(sides["bit"]["coarse"]), complex=Q(sides["complex"]["coarse"]))
    strict = summarize(pools["strict"], base, targets, now)
    bracket = summarize(pools["volume"], base, targets, now)
    assert strict["pairs_considered"] <= bracket["pairs_considered"]
    assert all(Q(strict["type_ladder"][key]["kappa"])
               <= Q(bracket["type_ladder"][key]["kappa"]) for key in strict["type_ladder"]), \
        "the strict rungs must not price above the volume bracket"

    # What a bank requires is settled by the queue's own banked rows and the supplier's
    # published bank proof, and it is *not* the tiling I first assumed: PR205/PR206/PR207
    # removed the rank-60 entrance exteriors from a width-72 word, so an absorbed family's
    # rank is free. What must hold is that the absorbed volume fills whole banks (their
    # 5,500 banks over three copies) and that a bank's blocks -- the word's own residual
    # families, 4 and 24 -- tile the width exactly, as their proof's "18 four-coordinate
    # blocks", "three 24-coordinate blocks" and `6 x rank-4 + 2 x rank-24` patterns do.
    patterns = [[(18, 4)], [(3, 24)], [(6, 4), (2, 24)]]
    volume = 3 * 2200 * 60
    precedent = dict(
        source="the queue's banked rows (#205/#206/#207), priced exactly by audit.py",
        supplier_proof="geometry/BANK-PROOF-PR200.md and retained-packing.py pin rank 60 on "
                        "width 72 and tile each bank with the word's residual families",
        absorbed_rank=60,
        bank_width=72,
        rank_divides_width=bool(72 % 60 == 0),
        absorbed_children_per_copy=2200,
        volume_three_copies=volume,
        banks_three_copies=volume // 72,
        volume_fills_whole_banks=bool(volume % 72 == 0),
        residual_families=[4, 24],
        block_patterns=patterns,
        blocks_sum_to_width=all(sum(count * size for count, size in pattern) == 72
                                for pattern in patterns),
        conclusion="an absorbed family's rank is free; only its volume must fill whole banks, "
                   "and a bank's blocks come from the word's residual families, which must "
                   "tile the width",
        effect="the certified-shape ladder below is the primary one; banking each family on "
               "its own tiled blocks is the conservative subset that needs no new shape",
    )

    def compact(summary, label):
        return dict(label=label, pairs_considered=summary["pairs_considered"],
                    pairs_above_frontier=summary["pairs_above_frontier"],
                    cheapest_pair=summary["cheapest_pair"], best_pair=summary["best_pair"],
                    type_ladder=summary["type_ladder"])

    out = dict(
        status="MODEL, NOT CONSTRUCTED: every schedule below is checked for whole-bank "
               "filling, the row identity, the paid moment's adjacent-grid exclusion and "
               "PR184's assembly arithmetic, but the bank charts, normalizers, F2 and "
               "defining-integer columns and per-bank prime witnesses are the supplier's "
               "harness and are not built here. Each rung is a target, priced exactly.",
        method="every subset of up to {} families per word screened across all ranks with "
               "the package's own ledger form, the best few of each size priced exactly by "
               "levers.py on PR200's interval arithmetic, and assembled by PR184's "
               "unchanged rule".format(MAX_TYPES),
        window=OLD_WINDOW, max_types=MAX_TYPES, new_top=NEW_TOP,
        frontier=dict(kappa=str(now), kappa_decimal=float(now),
                      budget=str(budget_of(base["bit"], base["complex"])),
                      published_claim=str(published), published_claim_decimal=float(published),
                      published_claim_delta=str(published - now),
                      binding="bit" if base["bit"] <= (1 - targets.STOP) * base["complex"]
                      - Q(1, targets.SELECT_GRID) else "complex"),
        sides={side: dict(item, coarse_decimal=float(Q(item["coarse"])))
               for side, item in sides.items()},
        precedent=precedent,
        strict=compact(strict, "conservative sub-tier: each family's own blocks tile a bank "
                               "and its own volume is a whole number of banks, so no block "
                               "shape beyond the word's residual families is used"),
        volume_only=compact(bracket, "the certified shape: the absorbed family's rank is "
                                     "free and only its volume must fill whole banks, "
                                     "exactly as #205/#206/#207 banked rank 60 on width 72"),
    )
    # Explicit LF: the committed JSON is pinned by its bytes, and a Windows checkout
    # must produce the same file a Linux one does.
    args.out.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", newline="\n")

    for side in ("bit", "complex"):
        item = sides[side]
        print("[{side}] m={m} W={W} deficit={deficit} rank mass={rank_mass} children="
              "{children} families={families} coarse today = {c}".format(
                  side=side, c=item["coarse"], **item))
        print("        families whose blocks tile a bank alone: {tiles_the_bank}".format(**item))
        print("        screened {combinations_screened} whole-bank family sets, priced "
              "{priced} exactly ({unpriceable} past the enclosure domain)".format(**item))
        single = item["single_family"]
        print("        best single family: " + ("none tiles a bank alone"
              if not single else "ranks {families} -> {banks} banks, coarse {coarse}"
              .format(**single)))
        for schedule in item["strict_schedules"][:3]:
            print("        [strict] absorb ranks {families} ({types} type(s)) -> {banks} banks, "
                  "stock {stock}, rank mass {rank_mass}, coarse {coarse}".format(**schedule))
        for schedule in item["volume_schedules"][:3]:
            print("        [bracket] absorb ranks {families} ({types} type(s)) -> {banks} "
                  "banks, stock {stock}, rank mass {rank_mass}, coarse {coarse}"
                  .format(**schedule))
    print("[frontier] kappa = {k}".format(k=now))
    for name, summary in (("strict", strict), ("volume bracket", bracket)):
        print("[{name}] {c} pairs, {a} above the frontier".format(
            name=name, c=summary["pairs_considered"], a=summary["pairs_above_frontier"]))
        for label in ("cheapest_pair", "best_pair"):
            item = summary[label]
            if item is None:
                print("        {label}: none".format(label=label))
                continue
            print("        {label}: kappa = {k} ({g:+.2%}) using {t} new residual type(s): "
                  "bit absorbs {b}, complex absorbs {c}".format(
                      label=label, k=item["kappa"], g=float(Q(item["gain"])), t=item["types"],
                      b=item["bit"]["families"] or "nothing",
                      c=item["complex"]["families"] or "nothing"))
        for budget_types, item in summary["type_ladder"].items():
            print("        types <= {t:>2}: kappa = {k} ({g:+.2%}, binding {b}, bit {bf} / "
                  "complex {cf})".format(t=budget_types, k=item["kappa"],
                                         g=float(Q(item["gain"])), b=item["binding"],
                                         bf=item["bit_families"], cf=item["complex_families"]))
    print("[write] " + str(args.out))


if __name__ == "__main__":
    main()
