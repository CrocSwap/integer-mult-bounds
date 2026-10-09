#!/usr/bin/env python3
"""Price the top of the queue with this package's model, exactly.

`levers.py` turns a certified bit row into the largest `a` on the `10^-18` grid
whose paid moment is below 1, and `kappa = a/(1+a)` is what the balanced assembly
reaches on that word once the finite ordinary leaf is bootstrapped. This script
runs that model over the banked bit rows now in the queue -- #205's packed
diagonal-bit word, #206's entrance-bank word (the same row) and #207's
coordinated-crossover word -- and reports, for each, the model's coarse saving
beside the value the author's own certificate states.

The rows are vendored byte-identically under `references/queue/`; the model
reproduces every one of them exactly, so a mismatch here would be a real
disagreement rather than a grid artefact. Each row's ceiling is compared with the
`10^-18` floor the same word's ledger leaves (`ln(m/22)` per rank-mass unit if the
residual dirt could be packed at the largest admissible child), which is a bound
on how much a future schedule change can still buy and not a construction.

    python3 -B audit.py [--out audit.json]
"""
import argparse
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRID = 10 ** 18

# Vendored queue certificates and the priced row inside each.
SOURCES = [
    ("PR205 packed diagonal bit", "pr205-packed-diagonal-bit.certificate.json",
     ("arithmetic", "packed_profile"), "rohanarun"),
    ("PR206 entrance banks on PR200", "pr206-pr200-entrance-banks.certificate.json",
     ("bit", "profile"), "EcmaXp"),
    ("PR207 coordinated crossover", "pr207-coordinated-crossover.certificate.json",
     ("bit_profile",), "Dugongue"),
]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def dig(data, keys):
    for key in keys:
        data = data[key]
    return data


def copies_row(profile):
    """The family's three-copy row, whichever form the certificate stores."""
    m = int(profile["m"])
    hist_key = "child_multiplicities" if "child_multiplicities" in profile else "child_histogram"
    hist = {int(r): int(n) for r, n in profile[hist_key].items() if n}
    for key in ("W_per_vertex", "W"):
        if key in profile:
            W = Q(str(profile[key]))
            break
    for key in ("deficit_per_vertex", "N", "deficit"):
        if key in profile:
            D = Q(str(profile[key]))
            break
    for copies in (1, 3):
        w, d = W * copies, D * copies
        packed = {r: copies * n for r, n in hist.items()}
        mass = sum(r * n for r, n in packed.items())
        if w.denominator == 1 and m * w - mass == d:
            return copies, m, int(w), d, packed
    raise ValueError("no copy count satisfies the row identity: " + json.dumps(profile)[:200])


def cheapest_ledger(m, W, D, maxchild):
    """The least-paying integral ledger of the same rank mass and largest child.

    Per unit of rank mass a child of rank r costs (m/r)^a/(W*m), which falls as r
    grows, so filling the mass greedily from the largest admissible rank downwards
    minimises the paid moment and therefore maximises the coarse saving over all
    admissible ledgers -- an upper bound on the saving, not an arrangement any
    schedule has to admit.
    """
    mass = m * W - D
    hist, remaining = {}, mass
    for rank in range(maxchild, 1, -1):
        count, remaining = divmod(remaining, rank)
        if count:
            hist[rank] = int(count)
    assert not remaining, "mass must be packable into admissible children"
    return hist


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "audit.json")
    args = parser.parse_args()
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    assert not sys.flags.optimize, "assertions must stay enabled"
    interval = module("audit_interval_moment", HERE / "references/pr200/interval_moment.py")
    levers = module("audit_levers", HERE / "levers.py")

    rows, frontier = [], None
    for name, filename, keys, author in SOURCES:
        path = HERE / "references/queue" / filename
        text = path.read_text()
        profile = dig(json.loads(text), keys)
        copies, m, W, D, hist = copies_row(profile)
        mass = sum(r * n for r, n in hist.items())
        word = levers.row(m, W, D, hist)
        coarse = levers.certified(interval, word)
        assert levers.paid_moment(interval, word, coarse)["upper"] < 1 < \
            levers.paid_moment(interval, word, coarse + Q(1, GRID))["lower"], name
        ceiling = coarse / (1 + coarse)
        bound_hist = cheapest_ledger(m, W, D, max(hist))
        bound = levers.certified(interval, levers.row(m, W, D, bound_hist))
        rows.append(dict(
            name=name, author=author, file="references/queue/" + filename,
            row=".".join(keys), copies=copies, m=m, W=W, deficit=str(D), rank_mass=mass,
            edges=sum(hist.values()), maxchild=max(hist), coarse=str(coarse),
            coarse_decimal=float(coarse), ceiling=str(ceiling), ceiling_decimal=float(ceiling),
            stated_in_certificate=str(coarse) in text,
            cheapest_ledger=dict(children=sum(bound_hist.values()), coarse=str(bound),
                                 coarse_decimal=float(bound),
                                 ceiling_decimal=float(bound / (1 + bound)))))
        if frontier is None or coarse > Q(frontier["coarse"]):
            frontier = rows[-1]

    out = dict(
        status="MODELLED, NOT CONSTRUCTED: the queue's rows are priced from their authors' "
               "certificates and their own stated coarse savings; nothing is built here, and "
               "the packed bound is a bound on admissible ledgers, not a construction.",
        method="levers.py's model, PR200's vendored enclosure arithmetic, 10^-18 grid",
        rows=rows,
        frontier=dict(name=frontier["name"], author=frontier["author"],
                      coarse=frontier["coarse"], ceiling=frontier["ceiling"],
                      ceiling_decimal=frontier["ceiling_decimal"],
                      edges=frontier["edges"], maxchild=frontier["maxchild"],
                      cheapest_ledger=frontier["cheapest_ledger"]),
        cheapest_ledger_gain=float(Q(frontier["cheapest_ledger"]["coarse"]) / Q(frontier["coarse"]) - 1),
    )
    args.out.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")

    for item in rows:
        print("[{stated}] {name} ({author}): W={W} D={deficit} mass={rank_mass} edges={edges} "
              "maxchild={maxchild}".format(
                  stated="stated" if item["stated_in_certificate"] else "UNSTATED", **item))
        print("        model coarse = {coarse} = {coarse_decimal:.15g}; ceiling kappa = "
              "{ceiling} = {ceiling_decimal:.15g}".format(**item))
    print("[frontier] {name}: coarse {coarse} -> kappa ceiling {ceiling}".format(**frontier))
    bound = frontier["cheapest_ledger"]
    print("[bounds] the frontier's ledger has {edges} children down to rank 1; the cheapest "
          "admissible ledger of the same stock, deficit and rank mass has {children} from rank "
          "{maxchild} downwards and would lift its coarse saving {gain:.4f}%, from {now} to "
          "{coarse} (ceiling kappa {ceiling:.15g}). That bounds what a better schedule can still "
          "buy and is not a construction.".format(
              edges=frontier["edges"], now=frontier["coarse_decimal"],
              children=bound["children"], maxchild=frontier["maxchild"],
              gain=out["cheapest_ledger_gain"] * 100, coarse=bound["coarse"],
              ceiling=bound["ceiling_decimal"]))
    print("[write] " + str(args.out))


if __name__ == "__main__":
    main()
