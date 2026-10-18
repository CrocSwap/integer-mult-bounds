# Sharp rank-six P112 shortening at common support 29

Three residual pieces of binary support rank at most six span at most one
root-code dimension after deleting one common set of at most 29 P112
coordinates. A literal common-cut-30 witness has code intersection dimension
two, so the uniform threshold is sharp. Coefficients may belong to any
characteristic-zero field; dependent pieces are allowed.

PR3255's sufficient threshold was 21. Coupling each endpoint's total support
to its singleton support gives a bound of 32, and the actual orthogonal
puncture leaves an A2 union of at least 78. At common support 29 the required
count is 98 against allowance 96. The witness at thirty supplies actual
coefficients and exact rational ranks 8,3,9, rather than a counting equality.

[PROOF.md](PROOF.md) gives the full argument and written dependencies.
[RESULT.json](RESULT.json) contains complete finite receipts and the literal
witness. [SOURCES.json](SOURCES.json) pins main and pending predecessors.
[CHECKS.json](CHECKS.json) records commands, environments and limits.

```sh
python3.12 -I -W error -B scripts/research_package.py \
  --package research/p112-a2-rank6-sharp-shortening
```

The direct primary, independent and behavioral commands in VERIFY.json also
work from a Git-free source export containing the two declared inputs.
No third-party Python dependencies are required. Replay writes no checkout
artifacts. Optional `verify.py --output PATH` creates a new external receipt.

This is a scoped mathematical theorem supported by exact finite checks. It
supplies no historical profile exclusion, full C5, decoder floor, supplier,
new kappa or selected-frontier update. The standard Weyl-chamber theorem and
characteristic-zero root-direction classification remain written proof
obligations, with their finite ingredients replayed. Neither human nor
proof-kernel review is claimed.

The task began with PR3255's equality-at-22 handoff. The same closure argument
then gave the sharper 29/30 result. The earlier rank-five equality-at-45
proposal was left to the worker holding its prior reservation before any
computation on that predicate. The concurrent mixed-rank caller has a
different endpoint contract and supplies no premise used here.

Credit Nick Petalas/PR3255 for the affine quotient and arbitrary-shift method,
PR3249 for the fiber-capacity perspective, the retained root-simplex geometry,
and DreamingOfClouds/PR3154 with the E8/P112 lineage including joaqcoo.
Predecessors remain unchanged. See TASK.json for the family expansion decision.

## Open next questions

Bind this sharp contract to one still-open literal TWOSIDE caller, after
checking the current public reconciliation. The first step is to establish
its single common support and surviving two code dimensions. This package
does not supply that application or price a physical decoder.
