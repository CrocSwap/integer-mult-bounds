#!/usr/bin/env python3
"""Which families the suppliers' construction may bank, and the schedule a rung hands it.

Two questions, both answered from the queue's own code and certificates rather than from
this package's model.

**Allocation.** #207's proof banks exactly one dirt family: the selected entrance gauges'
exteriors. Its own word builder builds that family as `hist[3*z['dim']] += 1` for every
gauge outside the donor set, which on this word is 2,200 children of rank `3*20 = 60`, one
per selected gauge -- and `pack-pr200.py` removes exactly that bin (`H.pop(60)`). Everything
else is retained: "Retain every internal, source, target, center, compensating and
terminal-substitution child." The proof also states three exclusions -- "Internal alias
recipients, source births and deleted terminals are excluded from fresh bank allocation" --
and its code shows where two of those kinds live: rank 2 is the alias children
(`hist[2] += 2*v`, two per compensated alias) and rank 1 carries the source births
(`if s in self.source.values(): H[1] += 1`), while the 1,760 recipient gauges are "internal
splices [that] receive no separate bank allocation".

**Schedule.** For a chosen rung this emits the bank inventory and the retained profile in the
supplier's vocabulary -- banks of width `m`, block patterns drawn from the word's residual
families, and the profile its moment pricer consumes -- and checks the invariants its own
generator asserts (each bank exactly full, exact full banks per pattern, the row identity,
the replica divisibility). It builds no chart, no column and no witness.

    python3 -B allocate.py [--out allocation.json]
"""
import argparse
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The proof's own patterns, each of which fills a width-72 bank exactly.
PATTERNS = [((18, 4),), ((3, 24),), ((6, 4), (2, 24))]
REPLICAS = 9

# Where the suppliers' code and proof put each rank's children.
KINDS = {
    60: (dict(status="banked", kind="selected entrance-gauge exteriors",
              why="`hist[3*z['dim']] += 1` outside the donor set; `H.pop(60)` in "
                  "pack-pr200.py, one child per selected gauge")),
    2: (dict(status="excluded", kind="alias children",
             why="#207: \"Internal alias recipients ... are excluded from fresh bank "
                 "allocation\"; `hist[2] += 2*v` is two children per compensated alias")),
    1: (dict(status="excluded", kind="source births (mixed with rank-1 increments)",
             why="#207: \"source births ... are excluded from fresh bank allocation\"; "
                 "`if s in self.source.values(): H[1] += 1`")),
}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def classify(rank):
    """What the suppliers' own materials say about a bin of children of this rank."""
    if rank in KINDS:
        return dict(KINDS[rank])
    return dict(status="retained",
                kind="internal / target / center / compensating / terminal-substitution dirt",
                why="#207: \"Retain every internal, source, target, center, compensating and "
                    "terminal-substitution child\"; absorbing it needs the \"future genuinely "
                    "different residual types\" the same proof reserves")


def schedule(m, W, D, hist, families):
    """The bank inventory and retained profile a rung hands the supplier's generator."""
    kept = {r: n for r, n in hist.items() if r not in families}
    taken = {r: n for r, n in hist.items() if r in families}
    volume = sum(r * n for r, n in taken.items())
    assert volume and volume % m == 0, "the absorbed volume must fill whole banks"
    banks = volume // m
    exact_mass = m * W - D - volume
    assert exact_mass.denominator == 1, "integral rank mass"
    mass = int(exact_mass)
    stock = Q(mass + D, m)
    assert stock.denominator == 1 and sum(r * n for r, n in kept.items()) == mass, "row identity"
    # A bank is a coordinate-block partition of width m, so its patterns must fill it exactly,
    # and a whole number of banks means the occurrence count of each uniform pattern divides.
    patterns = []
    for pattern in PATTERNS:
        blocks = sum(count for count, size in pattern)
        size_sum = sum(count * size for count, size in pattern)
        assert size_sum == m, "a pattern must fill the bank exactly"
        patterns.append(dict(blocks=blocks, blocks_per_size=[[count, size] for count, size in pattern],
                             fills_bank=size_sum))
    uniforms = [p for p in patterns if p["blocks_per_size"].__len__() == 1]
    placement = []
    for rank, count in sorted(taken.items()):
        occurrences = REPLICAS * count
        placement.append(dict(
            rank=rank, children_per_copy=count, replica_occurrences=occurrences,
            rank_volume=rank * count,
            banks_if_own_blocks=str(Q(rank * count, m)),
            own_block_size_divides_width=(m % rank == 0),
            occurrences_per_uniform_bank=[dict(size=p["blocks_per_size"][0][1],
                                               blocks_per_bank=p["blocks_per_size"][0][0],
                                               exact_full_banks=(occurrences %
                                                                 p["blocks_per_size"][0][0] == 0))
                                          for p in uniforms]))
    return dict(absorbed={str(r): n for r, n in sorted(taken.items())},
                volume=volume, banks=banks, banks_per_stage=str(Q(banks, 3)),
                banks_per_stage_exact=Q(banks, 3).denominator == 1,
                patterns=patterns, placement=placement,
                retained_profile=dict(m=m, W=int(stock), deficit=str(D), rank_mass=mass,
                                      children=sum(kept.values()), maxchild=max(kept),
                                      histogram={str(r): n for r, n in sorted(kept.items())}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "allocation.json")
    parser.add_argument("--rungs", type=Path, default=HERE / "rungs.json")
    args = parser.parse_args()
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    assert not sys.flags.optimize, "assertions must stay enabled"
    targets = module("allocate_targets", HERE / "targets.py")
    rungs = json.loads(args.rungs.read_text())
    certificate = json.loads(
        (HERE / "references/queue/pr207-coordinated-crossover.certificate.json").read_text())

    rows = {}
    for side in ("bit", "complex"):
        rows[side] = targets.rows(certificate[side + "_profile"])

    # Two rungs on the bit word, each with the complex word untouched: the cheapest
    # certified-shape rung, and the two-family tiling rung whose blocks tile a bank alone.
    chosen = {
        "cheapest_certified": dict(
            tier="volume_only", key="1",
            source="cheapest pair above the frontier with the absorbed rank free"),
        "two_type_tiling": dict(
            tier="strict", key="2",
            source="the two-family rung whose blocks tile a bank by themselves"),
    }
    out = dict(
        status="BLUEPRINT_FOR_THE_SUPPLIERS_GENERATOR: this package builds no bank chart, no "
               "F2 or defining-integer column and no prime witness, and it does not claim a "
               "rung is constructed. What it fixes is the schedule a builder would hand the "
               "generator, with the invariants that generator asserts.",
        source="queue certificate (byte-identical), the suppliers' proof text and their "
               "pack-pr200.py / retained-packing.py / base_word.row()",
        replicas=REPLICAS,
        rungs={},
    )
    for name, spec in chosen.items():
        tier = rungs[spec["tier"]]["type_ladder"][spec["key"]]
        arms, blocked = {}, []
        for side in ("bit", "complex"):
            families = tier[side + "_families"]
            if not families:
                arms[side] = None
                continue
            m, W, D, hist = rows[side]
            arm = schedule(m, W, D, hist, families)
            assert arm["banks"] == tier[side + "_banks"], "the two tools must agree on banks"
            arm["classification"] = {str(rank): classify(rank) for rank in families}
            blocked += [rank for rank in families if classify(rank)["status"] == "excluded"]
            arms[side] = arm
        out["rungs"][name] = dict(spec=spec, kappa=tier["kappa"], gain=tier["gain"],
                                  types=tier["types"], binding=tier["binding"],
                                  arms=arms,
                                  excluded_ranks=sorted(blocked),
                                  verdict=("blocked for an excluded kind and needing a new "
                                           "residual type for the rest; no rung on this word "
                                           "is bankable with the suppliers' construction as "
                                           "published, because every bin it would take is a "
                                           "retained child family"
                                           if blocked else
                                           "needs the new residual type the supplier's proof "
                                           "reserves; not buildable with the construction as "
                                           "published"))
    args.out.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", newline="\n")

    for name in out["rungs"]:
        item = out["rungs"][name]
        print("[{n}] {t} types, kappa {k} ({g:+.2%}), binding {b}: {v}".format(
            n=name, t=item["types"], k=item["kappa"], g=float(Q(item["gain"])),
            b=item["binding"], v=item["verdict"]))
        for side, arm in item["arms"].items():
            if arm is None:
                print("        {s}: untouched".format(s=side))
                continue
            print("        {s}: ranks {f} -> {b} banks, volume {v}, W {w}, deficit {d}, "
                  "per stage {ps}".format(
                      s=side, f=sorted(int(r) for r in arm["absorbed"]), b=arm["banks"],
                      v=arm["volume"], w=arm["retained_profile"]["W"],
                      d=arm["retained_profile"]["deficit"],
                      ps=arm["banks_per_stage"]))
            for rank, kind in sorted(arm["classification"].items(), key=lambda kv: int(kv[0])):
                print("            rank {r}: {st} ({kd})".format(
                    r=rank, st=kind["status"], kd=kind["kind"]))
    print("[allocation] no rung of this ladder is bankable by the suppliers' published "
          "construction: it banks one family (the selected entrance-gauge exteriors, already "
          "taken in this word) and retains every other, with alias children, source births "
          "and deleted terminals excluded outright")
    print("[write] " + str(args.out))


if __name__ == "__main__":
    main()
