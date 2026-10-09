#!/usr/bin/env python3
"""What the next gains are worth, priced exactly.

PR184's unchanged assembly takes

    a = min(bit_leaf, (1-1e-9)*C_complex - 1e-10),   kappa = a/(1+a)

to the `10^-10` grid, where `bit_leaf` is the finite ordinary leaf after PR185's
bootstrap (the fixed point of `a_{n+1} = (1-C_bit)C_bit + C_bit a_n`, so `C_bit`
itself once bootstrapped) and `C_complex` is the complex word's coarse saving. Two
consequences drive everything below:

* the **binding branch is the smaller budget**, so a gain on the stronger side is
  worth nothing until the other side catches up, and the complex budget carries a
  fixed `10^-10` grid step plus `1e-9` that the bit budget does not;
* a budget is raised only by raising a word's **coarse saving** `C`, and

      C = (1 - mass/(W m)) / L,   L = rank-mass-weighted mean of ln(m/r),

  so at fixed stock and deficit the lever is `L`: a ledger whose residual dirt sits
  in fewer, larger children. This script prices the ladder of such ledgers --
  soaking children of rank at or below a threshold into the largest admissible
  child -- for both suppliers, and reports the exact `kappa` each rung buys, with
  the branch that binds at every rung.

    python3 -B targets.py [--out targets.json]
"""
import argparse
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
STOP, ETA, SELECT_GRID = Q(1, 10 ** 9), Q(1, 10 ** 8), 10 ** 10
THRESHOLDS = (1, 2, 3, 4, 6, 8, 12, 16)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def assembly_kappa(budget):
    """PR184's `assemble`, exactly: the minimum budget to the 10^-10 grid."""
    assert 0 < budget < 1, "budget must be a saving"
    q = budget * (1 - 2 * ETA)
    minimum = (1 - ETA) * q / (1 + q)
    kappa = Q(minimum.numerator * SELECT_GRID // minimum.denominator, SELECT_GRID)
    if kappa == minimum:
        kappa -= Q(1, SELECT_GRID)
    return kappa


def branch_budgets(bit_coarse, complex_coarse):
    bit = bit_coarse                        # bootstrapped leaf, the fixed point
    complex_ = (1 - STOP) * complex_coarse - Q(1, SELECT_GRID)
    return bit, complex_, ("bit" if bit <= complex_ else "complex")


def rows(profile):
    """The family's three-copy row, whichever form the certificate stores."""
    m = int(profile["m"])
    key = "child_multiplicities" if "child_multiplicities" in profile else "child_histogram"
    hist = {int(r): int(n) for r, n in profile[key].items() if n}
    W = Q(str(profile.get("W_per_vertex", profile.get("W"))))
    D = Q(str(profile.get("deficit_per_vertex",
                          profile.get("N", profile.get("deficit")))))
    for copies in (1, 3):
        w, d = W * copies, D * copies
        packed = {r: copies * n for r, n in hist.items()}
        if w.denominator == 1 and m * w - sum(r * n for r, n in packed.items()) == d:
            return m, int(w), d, packed
    raise ValueError("no copy count satisfies the row identity")


def soak(m, W, D, hist, threshold):
    """Move all mass in children of rank <= threshold into the largest child.

    The rank mass, the stock and the deficit are unchanged: only the shape of the
    ledger differs, which is what a better schedule would have to deliver.
    """
    if threshold >= max(hist):
        return None
    kept = {r: n for r, n in hist.items() if r > threshold}
    mass = m * W - D
    remaining = mass - sum(r * n for r, n in kept.items())
    top = max(hist)
    for rank in range(top, 1, -1):
        count, remaining = divmod(remaining, rank)
        if count:
            kept[rank] = kept.get(rank, 0) + int(count)
    assert not remaining and sum(r * n for r, n in kept.items()) == mass
    return kept


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "targets.json")
    args = parser.parse_args()
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    assert not sys.flags.optimize, "assertions must stay enabled"
    interval = module("targets_interval_moment", HERE / "references/pr200/interval_moment.py")
    levers = module("targets_levers", HERE / "levers.py")
    pr184 = module("targets_pr184", HERE / "references/pr184/assemble_profiles.py")

    queue = HERE / "references/queue/pr207-coordinated-crossover.certificate.json"
    newest = json.loads(queue.read_text())
    suppliers = {}
    for side, key in (("bit", "bit_profile"), ("complex", "complex_profile")):
        m, W, D, hist = rows(newest[key])
        ladder = {}
        for threshold in THRESHOLDS:
            candidate = soak(m, W, D, hist, threshold)
            if candidate:
                ladder[str(threshold)] = levers.certified(
                    interval, levers.row(m, W, D, candidate))
        cheapest = soak(m, W, D, hist, max(hist) - 1)
        suppliers[side] = dict(
            m=m, W=W, deficit=str(D), rank_mass=int(m * W - D), edges=sum(hist.values()),
            maxchild=max(hist), coarse=levers.certified(interval, levers.row(m, W, D, hist)),
            ladder=ladder,
            cheapest_ledger=levers.certified(interval, levers.row(m, W, D, cheapest)))
        # Soaking more mass into larger children can only raise the coarse saving.
        rungs = [Q(suppliers[side]["coarse"])] + [Q(ladder[k]) for k in ladder]
        assert all(left <= right for left, right in zip(rungs, rungs[1:])), side
        assert Q(suppliers[side]["cheapest_ledger"]) >= rungs[-1], side

    # Validate the replica against PR184's own assembly on the vendored pair.
    complex_cert = json.loads((HERE / "references/pr194/certificate.json").read_text())
    bit_cert = json.loads((HERE / "inputs/pr200-bit-certificate.json").read_text())
    complex_row = pr184.select(pr184.normalize(complex_cert["complex_profile"]))
    bit_row = pr184.select(pr184.normalize(bit_cert["bit"]["profile"]), True)
    bit_leaf = Q(bit_row["saving"])          # the bootstrap's fixed point
    complex_coarse = Q(complex_row["saving"])
    boot = dict(bit_row)
    boot["effective_saving"] = bit_leaf
    real = Q(pr184.assemble(complex_row, boot, HERE / "references/pr168-v4",
                            HERE / "references/pr184/FINITE_BRIDGE.txt")["kappa"])
    assert real == assembly_kappa(min(*branch_budgets(bit_leaf, complex_coarse)[:2])), \
        "the replica must equal PR184's own assembly"

    # The queue's claims, each against its own row: an independent check that the
    # formula reproduces what three authors certified on two different words.
    packed205 = json.loads((HERE / "references/queue/pr205-packed-diagonal-bit.certificate.json").read_text())
    published = [("PR205 packed diagonal bit", packed205["arithmetic"]["packed_profile"],
                  Q(683061299399923, 10 ** 18)),
                 ("PR207 coordinated crossover", newest["bit_profile"],
                  Q(1366380910073, 2 * 10 ** 15))]
    checks = {}
    for name, profile, claimed in published:
        m, W, D, hist = rows(profile)
        coarse = levers.certified(interval, levers.row(m, W, D, hist))
        modelled = assembly_kappa(
            branch_budgets(coarse, Q(suppliers["complex"]["coarse"]))[0])
        checks[name] = dict(claimed=str(claimed), modelled=str(modelled),
                            coarse=str(coarse),
                            within_one_grid_step=abs(modelled - claimed) <= Q(1, SELECT_GRID))

    bit_coarse = Q(suppliers["bit"]["coarse"])
    complex_coarse = Q(suppliers["complex"]["coarse"])
    bit_budget, complex_budget, binding = branch_budgets(bit_coarse, complex_coarse)
    now = assembly_kappa(min(bit_budget, complex_budget))
    complex_only = assembly_kappa(complex_budget)
    # The bit coarse saving this word needs to stop binding.
    needed = complex_budget
    bit_soaked = {k: assembly_kappa(min(Q(v), complex_budget))
                  for k, v in suppliers["bit"]["ladder"].items()}
    both = {}
    for threshold, bit_value in suppliers["bit"]["ladder"].items():
        complex_value = suppliers["complex"]["ladder"].get(threshold)
        if complex_value:
            pair_budget = min(Q(bit_value), (1 - STOP) * Q(complex_value) - Q(1, SELECT_GRID))
            both[threshold] = dict(kappa=str(assembly_kappa(pair_budget)),
                                   binding=branch_budgets(Q(bit_value), Q(complex_value))[2],
                                   gain=str(assembly_kappa(pair_budget) / now - 1))
    out = dict(
        status="MODELLED, NOT CONSTRUCTED: these are schedules the assembly would price "
               "this way, computed from the queue's certified rows; no ledger or word is "
               "built here.",
        method="PR184's unchanged assembly formula on this package's exact coarse savings",
        assembly_replica_check=str(real),
        published_checks=checks,
        suppliers={k: dict(v, coarse=str(v["coarse"]),
                           ladder={t: str(c) for t, c in v["ladder"].items()},
                           cheapest_ledger=str(v["cheapest_ledger"]))
                   for k, v in suppliers.items()},
        frontier=dict(binding=binding, kappa=str(now), kappa_decimal=float(now),
                      bit_budget=str(bit_budget), complex_budget=str(complex_budget)),
        complex_side_cap=dict(kappa=str(complex_only), kappa_decimal=float(complex_only),
                              gain=str(complex_only / now - 1),
                              bit_coarse_needed=str(needed)),
        bit_ladder={
            t: dict(kappa=str(k), gain=str(k / now - 1),
                    binding=branch_budgets(Q(v), complex_coarse)[2])
            for (t, v), k in zip(suppliers["bit"]["ladder"].items(), bit_soaked.values())},
        both_soaked=both,
        cheapest_ledger_both=dict(
            kappa=str(assembly_kappa(min(Q(suppliers["bit"]["cheapest_ledger"]),
                                         (1 - STOP) * Q(suppliers["complex"]["cheapest_ledger"])
                                         - Q(1, SELECT_GRID)))),
            gain=str(assembly_kappa(min(Q(suppliers["bit"]["cheapest_ledger"]),
                                        (1 - STOP) * Q(suppliers["complex"]["cheapest_ledger"])
                                        - Q(1, SELECT_GRID))) / now - 1)),
    )
    args.out.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")

    for side in ("bit", "complex"):
        item = suppliers[side]
        print("[{side}] m={m} W={W} deficit={deficit} rank mass={rank_mass} children={edges} "
              "maxchild={maxchild}".format(side=side, **item))
        print("        coarse today = {coarse}".format(**item))
        for threshold, value in item["ladder"].items():
            print("        soak children <= {t:>2}: coarse = {v}".format(t=threshold, v=value))
        print("        cheapest ledger: coarse = " + str(item["cheapest_ledger"]))
    print("[frontier] {binding} binds: kappa = {k}".format(k=now, **out["frontier"]))
    print("[complex cap] kappa = {k} ({g:+.2%}), reached when the bit coarse saving is "
          "{n}".format(k=complex_only, g=float(complex_only / now - 1), n=needed))
    for threshold, item in out["bit_ladder"].items():
        print("[bit soak {t:>2}] kappa = {k} ({g:+.2%}, binding {b})".format(
            t=threshold, k=item["kappa"], g=float(Q(item["gain"])), b=item["binding"]))
    print("[cheapest both] kappa = {k} ({g:+.2%})".format(
        k=out["cheapest_ledger_both"]["kappa"],
        g=float(Q(out["cheapest_ledger_both"]["gain"]))))
    print("[published] " + "; ".join(
        "{k}: modelled {v[modelled]} vs claimed {v[claimed]} ({ok})".format(
            k=k, ok="within a grid step" if v["within_one_grid_step"] else "MISMATCH",
            **{"v": v}) for k, v in checks.items()))
    print("[write] " + str(args.out))


if __name__ == "__main__":
    main()
