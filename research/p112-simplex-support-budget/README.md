# P112 root-simplex support budgets

Four actual TWOSIDE beta profiles are impossible over every characteristic-zero
field:

```
3,5,5,6^(b+1)    and    4,4,5,6^(b+1),    b=6,7, t=4.
```

The [proof](PROOF.md) replaces the earlier edge-incidence estimate with the
minimum number of nonzero vertex evaluations after an arbitrary common shift.
A complete, small stabilizer-reflection enumeration gives one rank-six root
star and two rank-seven branches. After allowing 36 arbitrary coordinate
deletions, their endpoint support sums are at least 145 and 166. The pieces
allow only 140 and 160. The four contradiction margins are `5,5,6,6`.

These are new applications beyond PR3173's losing margins `-7,-8`, not full
C5, `C(P112)>=64`, a supplier or a new kappa. The selected result is unchanged.
The quotient has support cap `48<53`; every simplex edge has cap `68<70`.
The weight-only predecessor-cover audit needs sixteen line cuts and has no
rank-four nonbasis anchor. No five-flat containment is assumed.

## Reproduction

From the repository root, Python 3.12+ and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p112-simplex-support-budget
python3.12 -W error -B research/p112-simplex-support-budget/test_verify.py
```

The registered replay compares a freshly computed receipt with `RESULT.json`,
runs the fourteen behavioral test groups and enforces source pins. It checks
all 4,097,782 five/six-flat kernels, 960 simple reflections, 7,140 root planes,
the complete stabilizer partitions and both original target-cell lists.
The direct common-shift oracle covers 1,092 small value tuples. Additional
controls reject a missing simplex branch, changed sources, labels, geometric
premises and receipt fields. See [CHECKS.json](CHECKS.json) for executed checks.

For a fresh receipt, give `verify.py --output` a nonexistent path outside the
checkout. It refuses to overwrite files. Do not use Python's `-I` for the direct
script commands, because they import package-local modules. The registered
runner isolates bytecode caches. Direct replay from a source export needs this
package and the pinned `research/one-sided-six-multisets/data/data.txt` at their
repository-relative paths; it needs no Git database or network.

## Scope and credit

This takes the released PR3173 handoff in [Discussion3156](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156).
Canonical-main baseline `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority
revision 6. `TASK.json` records the handoff-first override of the formal-interface
card. This is a written proof with exact finite evidence, not Lean.

Credit DreamingOfClouds/PR3154 at `708f0ad8928c383de8294aea3c126e9461d2066d`
for TWOSIDE and its E8/P112 decoder lineage; Nick Petalas/PR3164 at
`857384079ab640a949fb7618b7909664d3e737e5` for retained geometry and the
root-simplex proof; PR3170 at `182168c4a7af570902b231aa6d35bbf4139098f2`
for larger simplices; and PR3169/3173 for the preceding coordinate count.
PR3161/3162/3167 are read for the deletion/anchor overlap boundary, not replayed
as full packages here. [SOURCES.json](SOURCES.json) pins the unchanged retained
files and their original notices. Apache-2.0.

Development and local checking used substantial automated assistance.
The evidence is author-checked, not independent human or proof-kernel review.
The standard Weyl-chamber theorem and the original decoder reduction remain
inherited written dependencies. No complete current residue count, full supplier
invoice, physical hosting, precision or outer theorem is claimed.

## Open next questions

Can actual frame and small-support geometry strengthen the arbitrary-36-line
relaxation for a named remaining profile? This could remove another decoder
configuration, but a further census needs a still-open target. First refresh
the live residue and claims, bind its quotient and root-edge hypotheses, and
price the changed support allowance. No complete residue after all pending
contributions is asserted here. Without that target, do not expand the search.
