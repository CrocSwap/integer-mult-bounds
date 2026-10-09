#!/usr/bin/env python3
"""Verify the composed diagonal-bit bootstrap record.

    python3 -B research/composed-diagonal-bit-bootstrap/verify.py

Checks, in order: every pinned byte against SOURCE.json; an exact regeneration of
certificate.json from the vendored inputs; two published cross-checks (the
depth-0 value against PR200's announced value for this composition, and PR184's
grid legacy leaf against PR200's published atom-wrapper value); the standing
claim; the bit branch's own ceiling; the finite-leaf tolls; the adjacent final
grid; and the corruption controls. The physical words are inherited pins and are
not replayed here.
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = HERE / ".work"
GRID = 10 ** 10
OLD = Q(384599, GRID)

# Published references, quoted from the open pull requests.
PR197_KAPPA = Q(135216063303877, 200000000000000000)   # #197 packed bit: standing claim
PR200_LEGACY_KAPPA = Q(6768823, GRID)                  # #200's own value for this composition
PR200_THETA = Q(677340914792209011107, 10 ** 24)       # #200 README atom-wrapper exponent
PR200_A0 = Q(677773948354561, 10 ** 18)                # #200 README bit coarse saving
PR194_KAPPA = Q(1668581, 2500000000)                   # #194 as published


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def rejects(name, operation, errors=(AssertionError, ValueError, KeyError)):
    try:
        operation()
    except errors:
        return name
    raise AssertionError("control accepted: " + name)


def tolls(coarse, leaf):
    """compose.py's own guard, mirrored so the control exercises that condition."""
    assert Q(leaf) < Q(coarse) < 1 - Q(leaf), "strict paid tolls"


def main():
    assert not sys.flags.optimize, "refusing -O"
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)

    # 1. Every pinned byte.
    manifest = json.loads((HERE / "SOURCE.json").read_text())
    drift = sorted(rel for rel, digest in manifest["files"].items()
                   if sha(ROOT / rel) != digest)
    assert not drift, ("pinned byte drift", drift)
    print("[pins] {} package and input files match SOURCE.json".format(len(manifest["files"])))

    # 2. Regenerate the certificate from the vendored inputs alone.
    WORK.mkdir(exist_ok=True)
    regenerated = WORK / "certificate.json"
    if regenerated.exists():
        regenerated.unlink()
    subprocess.run([sys.executable, "-B", str(HERE / "compose.py"), "--out", str(regenerated)],
                   check=True, stdout=subprocess.DEVNULL)
    record = json.loads(regenerated.read_text())
    assert record == json.loads((HERE / "certificate.json").read_text()), \
        "regenerated certificate differs from the committed one"
    print("[regenerate] certificate.json reproduced exactly from the vendored pins")

    pr184 = load(HERE / "references/pr184/assemble_profiles.py", "verify_pr184")
    bit_cert = json.loads((HERE / "inputs/pr200-bit-certificate.json").read_text())
    complex_cert = json.loads((HERE / "references/pr194/certificate.json").read_text())
    row = bit_cert["bit"]["profile"]
    coarse = Q(record["bit_coarse_saving"])
    legacy = Q(record["legacy_leaf"])
    depths = record["depths"]
    best_depth = max(depths, key=lambda d: Q(depths[d]["kappa"]))
    best = Q(depths[best_depth]["kappa"])

    # 3. The suppliers are the ones the certificate names.
    assert Q(record["complex_supplier"]["saving"]) == Q(complex_cert["complex_saving"])
    assert Q(complex_cert["kappa"]) == PR194_KAPPA, "PR194 reference"
    assert all(depths[d]["binding"] == "bit" for d in depths), "the bit branch must bind"
    assert all(Q(depths[d]["kappa"]) <= best for d in depths), "best is not the maximum"
    print("[pins] complex saving = {} (PR194 as published, kappa {}), binding branch = bit at "
          "every depth".format(record["complex_supplier"]["saving"], PR194_KAPPA))

    # 4. The depth-0 row must equal what PR200 announced for this composition.
    assert Q(depths["0"]["kappa"]) == PR200_LEGACY_KAPPA, "PR200 announced legacy value"
    assert depths["0"]["binding"] == "bit"
    print("[cross-check] depth 0 kappa = {} equals PR200's announced value for this "
          "composition".format(PR200_LEGACY_KAPPA))

    # 5. PR184's grid legacy leaf against PR200's published atom wrapper. The two
    #    suppliers define the same wrapper at different precision, so the control is
    #    what the difference does to the price: exactly one grid step at depth 0, and
    #    nothing at all once the wrapper is bootstrapped. PR184's select() is the
    #    pricing path the record's assembly is defined with, so the record uses it.
    complex_row = pr184.select(pr184.normalize(complex_cert["complex_profile"]))
    bit_row = pr184.select(pr184.normalize(row), True)
    assert Q(bit_row["saving"]) == coarse and Q(bit_row["effective_saving"]) == legacy

    def price(leaf):
        boot = dict(bit_row)
        boot["effective_saving"] = Q(leaf)
        return Q(pr184.assemble(complex_row, boot, HERE / "references/pr168-v4",
                                HERE / "references/pr184/FINITE_BRIDGE.txt")["kappa"])

    published_leaf = (1 - PR200_THETA) * PR200_A0 + PR200_THETA * OLD
    assert 0 < published_leaf - legacy < Q(1, GRID), "legacy leaf disagreement"
    assert price(published_leaf) - price(legacy) == Q(1, GRID), "one grid step at depth 0"
    alternative = [published_leaf]
    for _ in range(int(best_depth)):
        alternative.append((1 - coarse) * coarse + coarse * alternative[-1])
    assert price(alternative[-1]) == best, "the bootstrapped price must not depend on the start"
    print("[cross-check] PR184 legacy leaf {:.15g} vs PR200 published {:.15g} (delta {:.3g}): "
          "one grid step at depth 0, identical at depth {}".format(
              float(legacy), float(published_leaf), float(published_leaf - legacy), best_depth))

    # 6. The standing claim, the ceiling, and the exhaustion of pricing.
    assert best > PR197_KAPPA, "does not beat the standing claim"
    assert best > PR200_LEGACY_KAPPA, "does not beat the unbootstrapped composition"
    assert best > PR194_KAPPA
    ceiling = Q(record["ceiling"])
    assert best <= ceiling < best + Q(1, GRID), "not within one grid unit of the ceiling"
    assert Q(depths["1"]["kappa"]) < best == Q(depths["2"]["kappa"]), "depth 2 is not the claim"
    print("[claim] kappa = {} ({:.15g}) at depth {}; vs #197 {:+.4f}%, vs PR200 announced "
          "{:+.4f}%".format(best, float(best), best_depth,
                            float(best / PR197_KAPPA - 1) * 100,
                            float(best / PR200_LEGACY_KAPPA - 1) * 100))
    print("[ceiling] C/(1+C) = {:.15g}; the claim sits {:.3g} below it, under one grid unit "
          "({:.1g})".format(float(ceiling), float(ceiling - best), 1 / GRID))

    # 7. The finite-leaf tolls, recomputed independently in closed form.
    assert legacy < coarse < 1 - coarse, "coarse saving must be a strict leaf toll"
    chain = [legacy]
    for _ in range(int(best_depth)):
        chain.append((1 - coarse) * coarse + coarse * chain[-1])
    assert chain[-1] == coarse - coarse ** int(best_depth) * (coarse - legacy)
    for i in range(1, len(chain)):
        assert chain[i - 1] < chain[i] < coarse < 1 - chain[i], "strict paid tolls"
    assert Q(depths[best_depth]["leaf"]) == chain[-1], "recorded leaf"
    print("[tolls] a_0 < a_1 < ... < a_{} < C < 1 - a_{}".format(best_depth, best_depth))

    # 8. The assembly's minimum margin must be that closed form, and the next grid
    #    point must lie beyond it, so no finer leaf can buy another grid step.
    eta, stop = Q(1, 10 ** 8), Q(1, 10 ** 9)
    q = chain[-1] * (1 - 2 * eta)
    minimum = (1 - eta) * q / (1 + q)
    assert Q(depths[best_depth]["minimum_margin"]) == minimum, "recorded minimum margin"
    assert minimum < best + Q(1, GRID), "the next grid point is inside the minimum margin"
    print("[adjacent grid] minimum margin = {:.15g} lies in (kappa, kappa + 1e-10)".format(
        float(minimum)))

    # 9. Corruption controls, each of which must be refused.
    def accept_only_a_better_composition():
        assert PR200_LEGACY_KAPPA > best, "the unbootstrapped value must not reach the claim"

    rejected = [
        rejects("bit profile with a perturbed W",
                lambda: pr184.normalize(dict(row, W_per_vertex=row["W_per_vertex"] + 1))),
        rejects("leaf at or above the coarse saving",
                lambda: tolls(coarse, coarse + Q(1, GRID))),
        rejects("unbootstrapped depth-0 value offered as the claim",
                accept_only_a_better_composition),
    ]
    print("[controls] rejected: " + ", ".join(rejected))

    # 10. The lever model: what the next word-side move is worth. It must reproduce the
    #     three published values it can be checked on, and it must stay a model.
    lever_out = WORK / "levers.json"
    if lever_out.exists():
        lever_out.unlink()
    subprocess.run([sys.executable, "-B", str(HERE / "levers.py"), "--out", str(lever_out)],
                   check=True, stdout=subprocess.DEVNULL)
    levers = json.loads(lever_out.read_text())
    assert levers == json.loads((HERE / "levers.json").read_text()), "levers.json drift"
    for item in levers["validations"]:
        assert item["model"] == item["published"], (
            "the lever model must reproduce " + item["name"] + " exactly")
    banked = levers["pr200_banked"]
    assert Q(banked["W_per_vertex"]) == Q(56402, 3), "banked stock"
    assert banked["W_three_copies"] == 56402 and banked["rank60_children_per_copy"] == 2200
    assert Q(banked["ceiling"]) / Q(levers["claim"]["kappa"]) - 1 > Q(1, 200), "lever too small"
    assert levers["status"].startswith("MODELLED"), "the lever must not be presented as built"
    print("[levers] three published values reproduced exactly; banking the rank-60 "
          "exterior corrections is worth {:+.4f}% of kappa ({:.10g} -> {:.10g}), which "
          "this package models and does not build".format(
              levers["gain_vs_claim"] * 100,
              float(Q(levers["pr200_unpacked"]["ceiling"])),
              float(Q(banked["ceiling"]))))
    # 11. The queue audit: the model must price the banked rows now in the queue to exactly
    #     the coarse savings their own certificates state, and the frontier must be the
    #     banked row this package's lever predicted.
    audit_out = WORK / "audit.json"
    if audit_out.exists():
        audit_out.unlink()
    subprocess.run([sys.executable, "-B", str(HERE / "audit.py"), "--out", str(audit_out)],
                   check=True, stdout=subprocess.DEVNULL)
    audit = json.loads(audit_out.read_text())
    assert audit == json.loads((HERE / "audit.json").read_text()), "audit.json drift"
    for item in audit["rows"]:
        assert item["stated_in_certificate"], (
            "the model must reproduce " + item["name"] + " to the last digit")
    queue_best = max(audit["rows"], key=lambda item: Q(item["coarse"]))
    assert queue_best["name"] == audit["frontier"]["name"], "frontier row"
    assert Q(audit["frontier"]["ceiling"]) > best, "the banked rows must now stand above this claim"
    assert audit["cheapest_ledger_gain"] > Q(1, 2), "the ledger must be where the room is"
    assert audit["status"].startswith("MODELLED"), "the audit must not present a construction"
    print("[audit] {} banked rows priced to their own certificates exactly; the frontier is "
          "{} at {:.15g}, and its cheapest admissible ledger would reach {:.10g} ({:+.1f}%), "
          "a bound rather than a construction".format(
              len(audit["rows"]), audit["frontier"]["name"],
              float(Q(audit["frontier"]["ceiling"])),
              float(Q(audit["frontier"]["cheapest_ledger"]["coarse"])),
              audit["cheapest_ledger_gain"] * 100))
    # 12. The frontier calculator: what each next move on the two suppliers would be
    #     worth, from the queue's own rows. It must reproduce the published kappa of two
    #     different authors' banked rows, keep its ladder monotone, and stay a model.
    targets_out = WORK / "targets.json"
    if targets_out.exists():
        targets_out.unlink()
    subprocess.run([sys.executable, "-B", str(HERE / "targets.py"), "--out", str(targets_out)],
                   check=True, stdout=subprocess.DEVNULL)
    targets = json.loads(targets_out.read_text())
    assert targets == json.loads((HERE / "targets.json").read_text()), "targets.json drift"
    for name, item in targets["published_checks"].items():
        assert item["within_one_grid_step"], (
            "the assembly replica must reproduce " + name + " to within a grid step")
    assert targets["status"].startswith("MODELLED"), "the targets must not present a construction"
    assert Q(targets["complex_side_cap"]["gain"]) > 0, "the complex side must cap the frontier"
    ladder = [Q(targets["both_soaked"][key]["gain"])
              for key in sorted(targets["both_soaked"], key=int)]
    assert all(left < right for left, right in zip(ladder, ladder[1:])), \
        "soaking more rank mass into larger children must buy more"
    assert Q(targets["cheapest_ledger_both"]["gain"]) > Q(1, 2), "the ledger must be the room"
    first = targets["first_rung"]
    assert first and Q(first["coarse"]) >= Q(targets["complex_side_cap"]["bit_coarse_needed"]), \
        "the first rung must clear the complex side"
    assert Q(first["thousandths"], 1000) < Q(1, 5), "the first rung must be a small part"
    print("[targets] the frontier is {} at {}; taking the bit word's rank-1 children into "
          "larger ones reaches the complex side's {:.10g} ({:+.2%}), and soaking both words' "
          "cheap children buys {:+.2%}, rising to {:+.2%} at the cheapest admissible "
          "ledgers".format(
              targets["frontier"]["binding"], Q(targets["frontier"]["kappa"]),
              targets["complex_side_cap"]["kappa_decimal"],
              float(Q(targets["complex_side_cap"]["gain"])),
              float(Q(targets["both_soaked"]["1"]["gain"])),
              float(Q(targets["cheapest_ledger_both"]["gain"]))))
    print("[first rung] coarsening {:d}/1000 of the mass in the bit word's smallest children "
          "reaches the complex side (bit coarse {} vs the {} it needs)".format(
              first["thousandths"], Q(first["coarse"]),
              Q(targets["complex_side_cap"]["bit_coarse_needed"])))

    # 13. The big rungs: absorbing whole child families into the banks, which is the
    #     construction the audit's ledger bound says the room is in. Every candidate must
    #     fill a whole number of width-m banks; the ladder must start at the frontier's own
    #     price; its cheap rungs must beat the frontier; and the recorded headline rungs are
    #     re-priced here from the queue's certificate, independently of rungs.py.
    rungs_out = WORK / "rungs.json"
    if rungs_out.exists():
        rungs_out.unlink()
    subprocess.run([sys.executable, "-B", str(HERE / "rungs.py"), "--out", str(rungs_out)],
                   check=True, stdout=subprocess.DEVNULL)
    rungs = json.loads(rungs_out.read_text())
    assert rungs == json.loads((HERE / "rungs.json").read_text()), "rungs.json drift"
    assert rungs["status"].startswith("MODEL"), "the rungs must not present a construction"
    assert Q(rungs["frontier"]["kappa"]) == Q(targets["frontier"]["kappa"]), "frontier price"
    assert abs(Q(rungs["frontier"]["published_claim"]) - Q(rungs["frontier"]["kappa"])) \
        < Q(1, GRID), "the ladder must start at #207's published kappa"
    for tier in ("strict", "volume_only"):
        summary = rungs[tier]
        assert 0 < summary["pairs_above_frontier"] <= summary["pairs_considered"]
        assert summary["cheapest_pair"] and summary["best_pair"]
    for side, item in rungs["sides"].items():
        m, deficit = item["m"], Q(item["deficit"])
        for schedule in item["strict_schedules"] + item["volume_schedules"]:
            assert m * schedule["stock"] - schedule["rank_mass"] == deficit, \
                "scheduled row identity on the " + side + " word"
            assert schedule["banks"] * m == schedule["absorbed_rank_mass"], \
                "a schedule must fill whole banks on the " + side + " word"
            assert schedule["stock"] <= item["W"] and schedule["maxchild"] <= item["maxchild"]
            assert schedule["types"] == len(schedule["families"])
        # A strict schedule must bank each family on its own: its rank tiles the bank and
        # its own volume is a whole number of banks. This is re-derived below from the
        # queue's certificate, independently of rungs.py.
        assert all(sorted(schedule["families"]) != [] for schedule in item["strict_schedules"])
        for schedule in item["strict_schedules"]:
            assert set(schedule["families"]) <= set(item["tiles_the_bank"])

    ladder = {tier: rungs[tier]["type_ladder"] for tier in ("strict", "volume_only")}
    gains = [[Q(ladder[tier][key]["gain"]) for key in sorted(ladder[tier], key=int)]
             for tier in ("strict", "volume_only")]
    for values in gains:
        assert all(left <= right for left, right in zip(values, values[1:])), \
            "a bigger type budget must not buy less"
    assert all(Q(ladder["strict"][key]["kappa"]) <= Q(ladder["volume_only"][key]["kappa"])
               for key in ladder["strict"]), "the sound tier must sit inside the bracket"
    for tier in ("strict", "volume_only"):
        for item in ladder[tier].values():
            assert Q(item["bit_coarse"]) > Q(rungs["sides"]["bit"]["coarse"]) \
                or not item["bit_families"]
            assert Q(item["complex_coarse"]) > Q(rungs["sides"]["complex"]["coarse"]) \
                or not item["complex_families"]
    cheap = rungs["strict"]["cheapest_pair"]
    cap = Q(targets["complex_side_cap"]["kappa"])
    assert cheap["types"] == 1, "the cheapest sound rung must be a single new residual type"
    assert cheap["complex"]["families"] == [], "the one-type rung must not move the complex word"
    # The two-type rung reaches the ceiling the *frontier calculator* prices for the
    # unmoved complex side: two independent tools must agree on that number.
    assert Q(ladder["strict"]["2"]["kappa"]) == cap, \
        "the two-type sound rung must land on the unmoved complex cap"
    assert Q(ladder["strict"]["3"]["kappa"]) > cap, \
        "the complex word's own family must beat the unmoved cap"
    assert Q(ladder["strict"]["3"]["gain"]) > Q(1, 30), "the sound rung must be worth a few percent"
    assert Q(ladder["volume_only"]["5"]["gain"]) > Q(1, 3), "the bracket's rung must be worth a third"

    targets_mod = load(HERE / "targets.py", "verify_targets")
    levers_mod = load(HERE / "levers.py", "verify_levers")
    interval_mod = load(HERE / "references/pr200/interval_moment.py", "verify_interval")
    queue = json.loads(
        (HERE / "references/queue/pr207-coordinated-crossover.certificate.json").read_text())

    def rows_and_histogram(side):
        return targets_mod.rows(queue[side + "_profile"])

    def repriced(m, W, deficit, hist, families):
        """Re-price an arm from the queue's certificate, from scratch."""
        if not families:
            # An untouched arm is the frontier word's own row, absorbed nothing.
            return levers_mod.certified(interval_mod, levers_mod.row(m, W, deficit, hist))
        taken = sum(r * n for r, n in hist.items() if r in families)
        assert taken and taken % m == 0, "the arm must fill whole banks"
        kept = {r: n for r, n in hist.items() if r not in families}
        stock = (m * W - taken) // m
        assert m * stock - sum(r * n for r, n in kept.items()) == deficit, "arm identity"
        return levers_mod.certified(interval_mod, levers_mod.row(m, int(stock), deficit, kept))

    # The sound tier, re-derived: every family must tile the bank by itself and hold a
    # whole number of banks of its own, then the recorded kappa must follow from the arms.
    banked = {}
    for side in ("bit", "complex"):
        m, W, deficit, hist = rows_and_histogram(side)
        tiles = [r for r in sorted(hist) if m % r == 0 and (r * hist[r]) % m == 0]
        banked[side] = tiles
    for side, tiles in banked.items():
        assert tiles == rungs["sides"][side]["tiles_the_bank"], \
            "the bankable families of the " + side + " word must be re-derivable"
    for key in ("1", "2", "3", "4"):
        item = ladder["strict"][key]
        arms = {}
        for side in ("bit", "complex"):
            m, W, deficit, hist = rows_and_histogram(side)
            families = item[side + "_families"]
            assert set(families) <= set(banked[side]), \
                "a sound arm must bank each family on its own"
            arms[side] = repriced(m, W, deficit, hist, families)
        budget = min(arms["bit"], (1 - Q(1, 10 ** 9)) * arms["complex"] - Q(1, GRID))
        assert targets_mod.assembly_kappa(budget) == Q(item["kappa"]), \
            "the recorded rung must follow from its own schedule"
    for key, item in ladder["volume_only"].items():
        for side in ("bit", "complex"):
            m, W, deficit, hist = rows_and_histogram(side)
            taken = sum(r * hist[r] for r in item[side + "_families"])
            assert taken % m == 0, "every bracket arm must at least fill whole banks"
    print("[rungs] absorbing whole families into the banks, two tiers. Sound schedules "
          "(each family's blocks tile the bank by themselves): the bit word can bank ranks "
          "{}, the complex word rank {} -- {} new residual type on rank {} is {} ({:+.2%}), "
          "two types reach the unmoved complex cap at {} ({:+.2%}), and three types (adding "
          "the complex word's own rank {}) reach {} ({:+.2%})".format(
              banked["bit"], banked["complex"], cheap["types"], cheap["bit"]["families"][0],
              Q(cheap["kappa"]), float(Q(cheap["gain"])), Q(ladder["strict"]["2"]["kappa"]),
              float(Q(ladder["strict"]["2"]["gain"])), ladder["strict"]["3"]["complex_families"][0],
              Q(ladder["strict"]["3"]["kappa"]), float(Q(ladder["strict"]["3"]["gain"]))))
    print("[rungs bracket] keeping only the volume condition -- the shape the certified "
          "#197/#205/#207 banks have, whose absorbed rank 60 does not divide 72 either -- "
          "{} candidate pairs, {} of them above the frontier, rising to {} ({:+.2%}) at {} "
          "types".format(
              rungs["volume_only"]["pairs_considered"],
              rungs["volume_only"]["pairs_above_frontier"],
              Q(rungs["volume_only"]["best_pair"]["kappa"]),
              float(Q(rungs["volume_only"]["best_pair"]["gain"])),
              rungs["volume_only"]["best_pair"]["types"]))
    print("PASS composed-diagonal-bit-bootstrap kappa = {} at depth {}; 47 strict constraints "
          "and 7 margins per depth".format(best, best_depth))


if __name__ == "__main__":
    main()
