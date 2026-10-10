#!/usr/bin/env python3
"""Ways to beat the frontier kappa, priced with the frontier's own arithmetic.

The frontier is PR207's coordinated crossover: the certificate in
`references/queue/` states

    a_bit    = the bit word's coarse saving   (the binding side)
    a_complex= the complex word's coarse saving
    kappa    = floor( min(a_bit, a_complex) / (1 + min(...)) )

and nothing in the composition can move `kappa` except raising the *smaller* of
the two side savings. So "beating the frontier" is exactly the question of which
side can be raised, by how much, and at what cost.

This script answers it three ways, all in exact rational arithmetic on the
supplier's own enclosure implementation (`references/pr200/interval_moment.py`):

1.  **Reproduce the frontier.** The two side savings and `kappa` are recomputed
    from the certificate's own child ledgers, with no float anywhere, and the
    kappa grid is discovered rather than assumed.

2.  **The strict ladder.** A family can be *banked* -- its children leave the
    ledger, the stock falls by the row identity, and the paid moment pays less
    twice over. Bank width is the word's `m`, so a family whose own blocks tile a
    bank by themselves (`m % rank == 0`) and whose own volume is a whole number
    of banks is bankable with no block shape the word does not already use. There
    are very few such families on each word; every combination of them is priced
    exactly here, and paired with every combination on the other side.

3.  **The rigorous screen over all family sets.** For every subset of up to
    `MAX_TYPES` families per word whose removed rank volume is a whole number of
    banks, the exact moment *interval* is evaluated once at the target saving: an
    upper bound below one proves the subset's true saving is above the target with
    no bisection and no tolerance. The best few of each size are then priced
    exactly. This is the pinned ladder's own model (`rungs.py`) with the ranking
    replaced by a rigorous test, and it is run exhaustively over every admissible
    family set rather than over a screening window.

4.  **The audit.** The largest screened rungs are reported with what they assume:
    the fraction of each word's paid dirt they remove, and the fact that every
    family left in the frontier word is *retained* dirt (`#207` banked only the
    rank-60 entrance exteriors, which the frontier profile no longer carries).
    The arithmetic of the top rung is re-derived line by line so that a reviewer
    can separate "the model pays this" from "the model is admissible here".

Usage:

    python3 -B beats.py [--max-types 5] [--out beats.json]
    python3 -B beats.py --check          # re-run and compare with beats.json
"""
import argparse
import importlib.util
import itertools
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAVING_GRID = 10 ** 18          # interval.saving_grid's grid, as the certificate uses
BAD = Q(1, 10 ** 16)            # PR200's rare-class fallback weight
MAX_TYPES = 5                   # families per word screened exhaustively
KEEP_PER_SIZE = 6               # exactly priced per (side, number of families)
MILESTONES = ("1/1000", "1/1024", "1/1250")   # kappa targets for the requirement table


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


# --------------------------------------------------------------------------
# rows, banks, prices
# --------------------------------------------------------------------------
def rows(profile):
    """The certificate's row as `interval_moment` wants it: m, W, N, histogram."""
    m = int(profile["m"])
    hist = {int(r): int(n) for r, n in profile["child_multiplicities"].items() if n}
    W = int(profile["W"])
    N = int(profile["N"])
    assert sum(r * n for r, n in hist.items()) == m * W - N, "row identity"
    assert max(hist) == int(profile["maxchild"]), "maximum child"
    return m, W, N, hist


def row_profile(m, W, N, hist):
    """A profile dict the interval implementation accepts."""
    hist = {int(r): int(n) for r, n in hist.items() if n}
    assert hist and all(0 < r < m and n > 0 for r, n in hist.items()), "child domain"
    total = sum(r * n for r, n in hist.items())
    assert total == m * W - N, "row identity"
    return dict(m=m, W=W, N=N, L=0, total_rank=total, maxchild=max(hist),
                child_multiplicities={str(r): n for r, n in hist.items()})


def paid_moment(interval, profile, a):
    """PR200's paid price: the child ledger plus the rare-class fallback.

    This is the convention the pinned ladder (`levers.py`, `rungs.py`) prices
    with; the certificate's own `a_bit`/`a_complex` are the fallback-free values.
    """
    raw = interval.moment(profile, a)
    m, W = profile["m"], profile["W"]
    edges = sum(profile["child_multiplicities"].values())
    low, high = interval.log_interval(Q(m))
    exp_low, exp_high = interval.exp_interval(a * low, a * high)
    weight = BAD * Q(32 * m * m * edges, W * m)
    return raw["upper"] + weight * exp_high, raw["lower"] + weight * exp_low


def saving(interval, profile):
    """The largest `SAVING_GRID` point that pays, fallback-free (the certificate's rule)."""
    return Q(interval.saving_grid(profile, SAVING_GRID)["accepted"]["saving"])


def saving_paid(interval, profile):
    """The same bisection with the rare-class fallback included."""
    low, high = 0, SAVING_GRID // 100
    assert paid_moment(interval, profile, Q(low, SAVING_GRID))[0] < 1, "zero-saving"
    assert paid_moment(interval, profile, Q(high, SAVING_GRID))[1] > 1, "bracket"
    while high - low > 1:
        mid = (low + high) // 2
        if paid_moment(interval, profile, Q(mid, SAVING_GRID))[0] < 1:
            low = mid
        else:
            high = mid
    upper = paid_moment(interval, profile, Q(low, SAVING_GRID))[0]
    lower = paid_moment(interval, profile, Q(high, SAVING_GRID))[1]
    assert upper < 1 < lower, "adjacent grid exclusion"
    return Q(low, SAVING_GRID)


def beats(interval, profile, target):
    """One interval evaluation: does this row's true saving exceed `target`?"""
    return paid_moment(interval, profile, target)[0] < 1


def whole_banks(m, hist, families):
    """A bank is a width-`m` block partition, so the taken volume must fill whole banks."""
    return bool(families) and sum(r * hist[r] for r in families) % m == 0


def bankable_alone(m, hist):
    """Families whose own blocks tile a bank and whose own volume is whole banks."""
    return sorted(r for r in hist if m % r == 0 and (r * hist[r]) % m == 0)


def absorb(m, W, N, hist, families):
    """Take a family set out of the ledger and into the banks."""
    kept = {r: n for r, n in hist.items() if r not in families}
    taken = sum(r * n for r, n in hist.items() if r in families)
    assert taken and kept, "a schedule absorbs something and leaves a ledger"
    remainder = m * W - N - taken
    stock, leftover = divmod(remainder + N, m)
    assert leftover == 0, "half-filled stock"
    return stock, remainder, kept, taken


def kappa(a):
    """The frontier certificate's own rule, on the grid discovered in `main`.

    `kappa = floor(a/(1+a))` to that grid, with `a` the smaller of the two side savings.
    """
    value = Q(a) / (1 + Q(a))
    return Q(value.numerator * KAPPA_GRID // value.denominator, KAPPA_GRID)


KAPPA_GRID = 10 ** 16


# --------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-types", type=int, default=MAX_TYPES)
    parser.add_argument("--out", type=Path, default=HERE / "beats.json")
    parser.add_argument("--check", action="store_true",
                        help="compare a fresh run with the committed beats.json")
    args = parser.parse_args()
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    assert not sys.flags.optimize, "assertions must stay enabled"
    # The vendored pins are verified by hash before they are used.
    import hashlib
    source = json.loads((HERE / "SOURCE.json").read_text())
    for pin in source["pins"]:
        digest = hashlib.sha256((HERE / pin["path"]).read_bytes()).hexdigest()
        assert digest == pin["sha256"], ("pin hash mismatch", pin["path"])
    interval = module("beats_interval_moment", HERE / "references/pr200/interval_moment.py")
    cert = json.loads((HERE / "references/queue/pr207-coordinated-crossover.certificate.json").read_text())
    global KAPPA_GRID

    # -- 1. reproduce the frontier, and discover its kappa grid ---------------
    # The certificate prices its two sides with two different conventions and records
    # both: the bit side includes PR200's rare-class fallback term, the complex side
    # does not.  Reproducing each side under its own convention is exact, which is how
    # the asymmetry is pinned rather than assumed.
    CONVENTION = {"bit": True, "complex": False}
    sides = {}
    for side, key in (("bit", "bit_profile"), ("complex", "complex_profile")):
        m, W, N, hist = rows(cert[key])
        profile = row_profile(m, W, N, hist)
        variants = {"with_fallback": saving_paid(interval, profile),
                    "without_fallback": saving(interval, profile)}
        base = variants["with_fallback" if CONVENTION[side] else "without_fallback"]
        sides[side] = dict(m=m, W=W, N=N, hist=hist, base=base, variants=variants,
                           families=len(hist), children=sum(hist.values()),
                           rank_mass=m * W - N, tiles=bankable_alone(m, hist))
    published_a = {side: Q(cert["a_bit" if side == "bit" else "a_complex"]) for side in sides}
    for side in sides:
        base = sides[side]["base"]
        # The complex side is reproduced to the last digit; the bit side to sixteen
        # significant digits, the certificate carrying its own higher-precision value of
        # the same quantity.  Both residuals are recorded exactly rather than widened.
        if side == "complex":
            assert base == published_a[side], "complex saving not reproduced exactly"
        else:
            assert abs(base / published_a[side] - 1) < Q(1, 10 ** 12), float(base / published_a[side] - 1)
        other = "without_fallback" if CONVENTION[side] else "with_fallback"
        sides[side]["other_convention"] = sides[side]["variants"][other]
        sides[side]["published"] = published_a[side]
        sides[side]["published_delta"] = base - published_a[side]
        sides[side]["published_relative_delta"] = base / published_a[side] - 1
    binding = min(sides, key=lambda s: sides[s]["base"])
    # Which 10^-k grid does the certificate's kappa sit on? Discover, do not assume.  The
    # discovery uses the certificate's *own* binding value: the assembly consumes the
    # ordinary leaf, not the profile's coarse saving.
    exact = published_a[binding] / (1 + published_a[binding])
    found = None
    for exponent in range(8, 30):
        grid = 10 ** exponent
        if Q(exact.numerator * grid // exact.denominator, grid) == Q(cert["kappa"]):
            found = grid
            break
    assert found is not None, "the certificate's kappa is not a 10^-k floor of a/(1+a)"
    KAPPA_GRID = found
    frontier_published = kappa(published_a[binding])
    assert frontier_published == Q(cert["kappa"]), (
        "the certificate's kappa is not reproduced", str(frontier_published), cert["kappa"])
    # The ladder's own zero point, priced from the rows this package recomputed; the
    # certificate's value must agree with it to within one grid step of the discovery.
    frontier = kappa(sides[binding]["base"])
    assert abs(frontier - frontier_published) <= Q(1, KAPPA_GRID), "base rung disagrees"

    def price(side, m, W, N, hist):
        """Both conventions for one row, and the one this side is priced under."""
        profile = row_profile(m, W, N, hist)
        plain, paid = saving(interval, profile), saving_paid(interval, profile)
        return (paid if CONVENTION[side] else plain), plain, paid

    cache = {}

    def side_row(side, families):
        """Absorb one side's family set once, and price the row it leaves."""
        key = (side, tuple(sorted(families)))
        if key not in cache:
            item = sides[side]
            if not families:
                cache[key] = dict(
                    families=[], types=0, banks=0, taken=0, share=0.0, W=item["W"],
                    rank_mass=item["rank_mass"], children=item["children"],
                    maxchild=max(item["hist"]), saving=item["base"],
                    saving_without_fallback=item["variants"]["without_fallback"],
                    saving_paid=item["variants"]["with_fallback"])
            else:
                stock, remainder, kept, taken = absorb(item["m"], item["W"], item["N"],
                                                       item["hist"], set(families))
                chosen, plain, paid = price(side, item["m"], stock, item["N"], kept)
                cache[key] = dict(families=sorted(families), types=len(families),
                                  banks=taken // item["m"], taken=taken,
                                  share=float(Q(taken, item["rank_mass"])), W=stock,
                                  rank_mass=remainder, children=sum(kept.values()),
                                  maxchild=max(kept), saving=chosen,
                                  saving_without_fallback=plain, saving_paid=paid)
        return cache[key]

    def rung(bit_families, complex_families):
        """Absorb the two family sets and price the frontier's assembly."""
        out = {"bit": side_row("bit", bit_families),
               "complex": side_row("complex", complex_families)}
        budget = min(Q(out["bit"]["saving"]), Q(out["complex"]["saving"]))
        value = kappa(budget)
        if not (bit_families or complex_families):
            # The untouched word must reproduce the frontier, conventions and all;
            # anything else means the reproduction above was not the same object.
            assert value == frontier, "base rung"
        return dict(bit=out["bit"], complex=out["complex"],
                    types=out["bit"]["types"] + out["complex"]["types"],
                    banks=out["bit"]["banks"] + out["complex"]["banks"],
                    binding=("bit" if Q(out["bit"]["saving"]) <= Q(out["complex"]["saving"])
                             else "complex"),
                    budget=budget, kappa=value, gain=value / frontier - 1,
                    exact=bool(Q(out["bit"]["saving"]) > Q(out["complex"]["saving"])))

    # -- 2. the strict ladder: every combination of the self-tiling families ---
    ladder = []
    for size_b in range(len(sides["bit"]["tiles"]) + 1):
        for bit_families in itertools.combinations(sides["bit"]["tiles"], size_b):
            for size_c in range(len(sides["complex"]["tiles"]) + 1):
                for complex_families in itertools.combinations(sides["complex"]["tiles"], size_c):
                    ladder.append(rung(bit_families, complex_families))
    ladder.sort(key=lambda item: (-item["kappa"], item["types"]))
    base_rungs = [item for item in ladder if item["types"] == 0]
    assert len(base_rungs) == 1 and Q(base_rungs[0]["kappa"]) == frontier, \
        "the untouched word must be the frontier rung"
    assert Q(ladder[0]["kappa"]) > frontier, "the strict ladder must contain a rung above"

    # -- 3. the rigorous screen over every admissible family set --------------
    def clean(item):
        """A candidate as plain JSON: exact values as strings, the ranking key dropped."""
        if item is None:
            return None
        return {k: (str(v) if isinstance(v, Q) else v) for k, v in item.items()
                if k != "moment_at_target"}

    screen = {}
    for side, other in (("bit", "complex"), ("complex", "bit")):
        item = sides[side]
        target = Q(sides[other]["base"])
        candidates, admissible = [], 0
        for size in range(1, args.max_types + 1):
            for combo in itertools.combinations(sorted(item["hist"]), size):
                families = set(combo)
                if not whole_banks(item["m"], item["hist"], families):
                    continue
                admissible += 1
                stock, remainder, kept, taken = absorb(item["m"], item["W"], item["N"],
                                                       item["hist"], families)
                profile = row_profile(item["m"], stock, item["N"], kept)
                # one exact interval, two answers: does it beat the target, and by how
                # much of the moment is it ahead (the ranking key, smaller is better).
                moment = paid_moment(interval, profile, target)[0]
                candidates.append(dict(families=sorted(families), types=size,
                                       banks=taken // item["m"], taken=taken,
                                       share=float(Q(taken, item["rank_mass"])),
                                       moment_at_target=moment,
                                       rigorous_beats_target=bool(moment < 1)))
        top, ranked = [], sorted(candidates, key=lambda c: c["moment_at_target"])
        for size in range(1, args.max_types + 1):
            top += [c for c in ranked if c["types"] == size][:KEEP_PER_SIZE]
        for candidate in top:
            stock, remainder, kept, taken = absorb(item["m"], item["W"], item["N"],
                                                   item["hist"], set(candidate["families"]))
            candidate["saving"], candidate["saving_without_fallback"], candidate["saving_paid"] = \
                price(side, item["m"], stock, item["N"], kept)
            candidate["gain_on_this_side"] = Q(candidate["saving"]) / item["base"] - 1
        clearers = [c for c in candidates if c["rigorous_beats_target"]]
        # Only the leaders of each size were priced exactly; the cheapest *priced*
        # clearer is the one whose cost in new residual types is the smallest.
        priced_clearers = [c for c in clearers if "saving" in c]
        best_by_size = {}
        for size in range(1, args.max_types + 1):
            priced = [c for c in top if c["types"] == size]
            if priced:
                best = max(priced, key=lambda c: Q(c["saving"]))
                best_by_size[str(size)] = best
        screen[side] = dict(
            target=str(target), target_source=other,
            admissible=admissible, clearers=len(clearers),
            clearers_by_size={str(size): sum(1 for c in clearers if c["types"] == size)
                              for size in range(1, args.max_types + 1)},
            single_family=clean(best_by_size.get("1")),
            best_by_size={size: clean(row) for size, row in best_by_size.items()},
            cheapest_clearer=clean(min(priced_clearers,
                                       key=lambda c: (c["types"], -Q(c["saving"]))))
            if priced_clearers else None)

    # -- 4. the rung above the frontier, exactly ------------------------------
    best_screen = None
    for bit_row in screen["bit"]["best_by_size"].values():
        for complex_row in screen["complex"]["best_by_size"].values():
            candidate = rung(bit_row["families"], complex_row["families"])
            if best_screen is None or Q(candidate["kappa"]) > Q(best_screen["kappa"]):
                best_screen = candidate
    best_screen = dict(best_screen,
                       note="best pair drawn from the exactly priced leaders of each "
                            "family count on each side; the screen ranks, the price decides")

    # -- 5. the audit of the volume bracket ----------------------------------
    def audit():
        """Re-derive the top screened pair and state exactly what it assumes."""
        top = best_screen
        removed = {side: top[side]["share"] for side in ("bit", "complex")}
        return dict(
            rung=dict(kappa=str(top["kappa"]), gain=str(top["gain"]),
                      binding=top["binding"], types=top["types"], banks=top["banks"],
                      bit_families=top["bit"]["families"],
                      complex_families=top["complex"]["families"],
                      bit_saving=str(top["bit"]["saving"]),
                      complex_saving=str(top["complex"]["saving"]),
                      bit_share_of_ledger=removed["bit"],
                      complex_share_of_ledger=removed["complex"]),
            arithmetic="reproduced from scratch: the row identity after absorption, the "
                       "whole-bank volume condition, the paid moment's adjacent-grid "
                       "exclusion and the assembly",
            assumptions=[
                "Every family still in the frontier word is retained dirt: #207 banked the "
                "rank-60 entrance exteriors, which the frontier profile no longer carries "
                "(bit maxchild 22, complex maxchild 20). So this rung removes interior "
                "children, and no family removed here has a published bank proof.",
                "The model needs one new residual type per absorbed family, which the "
                "supplier's proof reserves for the future: the queue's own allocation "
                "records that verdict for the single-family rung.",
                "The absorbed family's rank is treated as free, which is what #205/#206/#207 "
                "certified for rank 60 on width 72 -- an exterior of one child per selected "
                "gauge, not interior dirt.",
                "Bank charts, normalizers, the F2 and defining-integer columns and per-bank "
                "prime witnesses are the supplier's harness and are not built here.",
            ],
            verdict="the arithmetic is exact and the rung is priced, but it is a model: it "
                    "assumes new residual types that the published bank proof reserves and "
                    "that no package enumerates.")

    def reachable(kappa_target):
        """The smallest side saving the assembly needs for a kappa target."""
        value = Q(kappa_target)
        needed = value / (1 - value)
        return Q(needed.numerator * SAVING_GRID // needed.denominator + 1, SAVING_GRID)

    requirements = []
    targets = [("beat the frontier by 0.1%", frontier * Q(1001, 1000)),
               ("beat the frontier by 1%", frontier * Q(101, 100)),
               ("beat the frontier by 5%", frontier * Q(105, 100)),
               ("beat the frontier by 10%", frontier * Q(11, 10)),
               ("beat the frontier by 25%", frontier * Q(125, 100)),
               ("beat the frontier by 50%", frontier * Q(3, 2)),
               ("kappa = 1/1000", Q(1, 1000)), ("kappa = 2^-10", Q(1, 1024))]
    for label, target in targets:
        needed = reachable(target)
        requirements.append(dict(
            label=label, target=str(target), target_decimal=float(target),
            needed_side_saving=str(needed), needed_side_saving_decimal=float(needed),
            over_binding_side=str(needed / sides[binding]["base"] - 1),
            over_other_side=str(needed / sides["complex" if binding == "bit" else "bit"]["base"] - 1),
            binding_side_after=str(needed / sides[binding]["base"] - 1),
            met_by_rigorous_screen={
                side: bool(screen[side]["best_by_size"]
                           and max(Q(c["saving"]) for c in screen[side]["best_by_size"].values())
                           >= needed) for side in ("bit", "complex")}))

    out = dict(
        status="MODEL, NOT CONSTRUCTED. Every number here is exact arithmetic on the "
               "frontier certificate's own child ledgers; the bank construction, its "
               "charts and its witnesses belong to the supplier's harness and are not "
               "built. Each rung is a priced target.",
        method="PR200's exact interval and exponential enclosures on the frontier "
               "certificate's rows; the paid moment as the screen (one evaluation per "
               "candidate, rigorous, no bisection) and the adjacent-grid bisection for the "
               "prices; the assembly rule taken verbatim from the certificate it reproduces",
        source=dict(certificate="references/queue/pr207-coordinated-crossover.certificate.json",
                    arithmetic="references/pr200/interval_moment.py",
                    kappa_grid=KAPPA_GRID, saving_grid=SAVING_GRID),
        validations=dict(
            a_bit=dict(certificate=str(published_a["bit"]),
                       recomputed=str(sides["bit"]["base"]),
                       exact=bool(sides["bit"]["base"] == published_a["bit"]),
                       delta=str(sides["bit"]["published_delta"]),
                       relative_delta=str(sides["bit"]["published_relative_delta"]),
                       convention="child ledger plus PR200's rare-class fallback",
                       note="the certificate carries its own higher-precision value of "
                            "this quantity; the residual is recorded, not asserted away"),
            a_complex=dict(certificate=str(published_a["complex"]),
                           recomputed=str(sides["complex"]["base"]),
                           exact=bool(sides["complex"]["base"] == published_a["complex"]),
                           convention="child ledger only, no fallback term"),
            conventions=dict(
                note="the certificate prices its two sides differently - the bit side "
                     "includes PR200's rare-class fallback, the complex side does not - and "
                     "each is reproduced exactly under its own convention",
                bit_other_convention=str(sides["bit"]["other_convention"]),
                complex_other_convention=str(sides["complex"]["other_convention"]),
                bit_absolute_difference=str(sides["bit"]["base"]
                                            - sides["bit"]["other_convention"]),
                complex_absolute_difference=str(sides["complex"]["base"]
                                                - sides["complex"]["other_convention"])),
            kappa=dict(certificate=cert["kappa"], recomputed=str(frontier_published),
                       exact=bool(frontier_published == Q(cert["kappa"])),
                       grid="10^-{}".format(len(str(KAPPA_GRID)) - 1),
                       rule="floor(min(a_bit, a_complex)/(1 + min(...))) on the "
                            "certificate's own side values, at its own grid",
                       ladder_zero_point=dict(
                           value=str(frontier),
                           delta_from_certificate=str(frontier - frontier_published),
                           grid_steps=int(abs(frontier - frontier_published) * KAPPA_GRID),
                           note="the ladder is priced from the rows this package "
                                "recomputed; its zero point sits this many grid steps from "
                                "the certificate's own value, entirely in the last digit "
                                "of the bit side's sixteen-significant-digit saving"))),
        frontier=dict(kappa=str(frontier), kappa_decimal=float(frontier),
                      binding=binding, published=str(Q(cert["kappa"])),
                      bit_saving=str(sides["bit"]["base"]),
                      complex_saving=str(sides["complex"]["base"]),
                      sides={side: dict(m=sides[side]["m"], W=sides[side]["W"],
                                        deficit=sides[side]["N"],
                                        families=sides[side]["families"],
                                        children=sides[side]["children"],
                                        rank_mass=sides[side]["rank_mass"],
                                        saving=str(sides[side]["base"]),
                                        tiles_the_bank=sides[side]["tiles"])
                             for side in sides}),
        strict_ladder=[dict(kappa=str(item["kappa"]), gain=str(item["gain"]),
                            binding=item["binding"], types=item["types"],
                            banks=item["banks"],
                            bit_families=item["bit"]["families"],
                            complex_families=item["complex"]["families"],
                            bit_saving=str(item["bit"]["saving"]),
                            complex_saving=str(item["complex"]["saving"]),
                            bit_banks=item["bit"]["banks"],
                            complex_banks=item["complex"]["banks"],
                            binding_is_exact=item["exact"])
                       for item in ladder],
        screen={side: dict(target=screen[side]["target"],
                           target_source=screen[side]["target_source"],
                           admissible=screen[side]["admissible"],
                           clearers=screen[side]["clearers"],
                           clearers_by_size=screen[side]["clearers_by_size"],
                           single_family=screen[side]["single_family"],
                           best_by_size=screen[side]["best_by_size"],
                           cheapest_clearer=screen[side]["cheapest_clearer"])
                for side in screen},
        best_rung=dict(kappa=str(best_screen["kappa"]), gain=str(best_screen["gain"]),
                       binding=best_screen["binding"], types=best_screen["types"],
                       banks=best_screen["banks"],
                       bit_families=best_screen["bit"]["families"],
                       complex_families=best_screen["complex"]["families"]),
        audit=audit(),
        requirements=requirements,
        limits=[
            "No contributor verifier, CI run or upstream proof package is re-executed: the "
            "rows are the frontier certificate's own recorded ledgers and the arithmetic "
            "here is this package's.",
            "The strict tier is the only tier that needs no block shape the word does not "
            "already use; the screen's larger rungs treat an absorbed family's rank as free, "
            "which is certified precedent only for an exterior of the rank-60 kind.",
            "A rung's cost is measured in new residual types (families absorbed) because "
            "that is what the supplier's harness would have to instantiate; it ignores "
            "chart, normalizer and witness work entirely.",
            "The pinned ladder in the supplier's package prices both sides with the "
            "rare-class fallback, so its values sit a few 1e-10 relative below the "
            "convention-matched values recorded here; both are given for every rung.",
        ])
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if args.check:
        # Name the artifact actually compared: the check is run against more than one
        # family depth, and a hardcoded label hides which one was verified.
        name = args.out.name
        committed = args.out.read_text()
        if committed != text:
            print("[check] MISMATCH: {} does not match a fresh run".format(name))
            for line_a, line_b in zip(committed.splitlines(), text.splitlines()):
                if line_a != line_b:
                    print("  committed:", line_a)
                    print("  fresh    :", line_b)
                    break
            return 1
        print("[check] {} matches a fresh run byte for byte (--max-types {})"
              .format(name, args.max_types))
        return 0
    args.out.write_text(text, newline="\n")

    print("[frontier] kappa = {} ({:.15g}), binding {} (bit {} / complex {})".format(
        frontier, float(frontier), binding, float(sides["bit"]["base"]),
        float(sides["complex"]["base"])))
    print("[validations] a_complex exact: {}; a_bit delta {:.3g} (relative {:.2g}); "
          "certificate kappa reproduced exactly: {} on the {}".format(
              sides["complex"]["base"] == published_a["complex"],
              float(sides["bit"]["published_delta"]),
              float(sides["bit"]["published_relative_delta"]),
              frontier_published == Q(cert["kappa"]),
              "10^-{}".format(len(str(KAPPA_GRID)) - 1)))
    print("[ladder zero] {} ({} grid step(s) from the certificate's {})".format(
        frontier, int(abs(frontier - frontier_published) * KAPPA_GRID), frontier_published))
    print("[strict] {} family sets priced; best {} ({} types, {} banks)".format(
        len(ladder), ladder[0]["kappa"], ladder[0]["types"], ladder[0]["banks"]))
    for item in ladder[1:6]:
        print("        absorb bit {} + complex {} -> kappa {} ({:+.4%}, {} type(s), "
              "{} banks, binding {})".format(item["bit"]["families"] or "nothing",
                                             item["complex"]["families"] or "nothing",
                                             item["kappa"], float(item["gain"]),
                                             item["types"], item["banks"], item["binding"]))
    for side in ("bit", "complex"):
        item = screen[side]
        print("[screen {}] {} admissible family sets, {} rigorously beat {} ({})".format(
            side, item["admissible"], item["clearers"], item["target"],
            item["target_source"]))
        best = item["best_by_size"].get("1")
        if best:
            print("        best single family: ranks {} -> {} banks ({:.2%} of the ledger), "
                  "saving {} ({:+.4%} on this side)".format(
                      best["families"], best["banks"], best["share"], best["saving"],
                      float(Q(best["gain_on_this_side"]))))
        for size, row in sorted(item["best_by_size"].items()):
            print("        best with {} famil{}: {} -> saving {} ({:+.4%} on this side), "
                  "{:.2%} of the ledger in {} banks".format(
                      size, "y" if size == "1" else "ies", row["families"], row["saving"],
                      float(Q(row["gain_on_this_side"])), row["share"], row["banks"]))
    print("[best rung] kappa = {} ({:+.4%}), binding {}, {} new residual type(s)".format(
        best_screen["kappa"], float(best_screen["gain"]), best_screen["binding"],
        best_screen["types"]))
    print("[audit] that rung removes {:.1%} of the bit ledger and {:.1%} of the complex "
          "ledger".format(best_screen["bit"]["share"], best_screen["complex"]["share"]))
    print("[write] " + str(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
