# Two P112 six-flats need fifteen extra lines

For every nonzero P112 root-code word, at least **fifteen** live coordinates
remain outside any two binary label spaces of dimension at most six.
Fifteen is sharp. The crude distance/capacity estimate gives only thirteen.
For each of the 120 root directions, the exact maximum covered by two
six-flats is 38. Its residual minimum is fifteen for 112 directions and
eighteen for the eight frame directions.

The [proof](PROOF.md) extends the finite root calculation to every
characteristic-zero field. This is a new scoped cover theorem and a preferred
quotient-basis implication for one actual TWOSIDE caller. It is not a profile
exclusion, full C5, `C(P112)>=64`, supplier admission or a new kappa.

The actual historical `(6,5)` profile is `2,3,4,6^8`. Its preferred five-set
`2,3,4,6,6` has support capacity 54, above the usual strict-below-53 threshold.
The new theorem certifies its quotient independence because it is covered
by two six-flats and fourteen extra coordinates. Every five-piece subset has
capacity at least 54, so the profile-based capacity test certifies none. Actual supports may overlap; their unions are not asserted
to have size at least 54. The new theorem supplies this quotient-basis implication.
Six independent residual directions of rank at most six, with one common
fourteen-line set, are the exact remaining obligation.

## Reproduction

Use Python 3.12 and the standard library for the registered runner:

```sh
python3.12 -B scripts/research_package.py --package research/p112-two-six-flat-cover
```

The registered replay computes the complete receipt and compares it with
[RESULT.json](RESULT.json), then runs twelve behavioral test groups. To run
the controls alone:

```sh
python3 -B research/p112-two-six-flat-cover/test_verify.py
```

For a fresh receipt, use `verify.py --output /an/external/new-file.json`.
The output path must be outside the checkout and must not exist. The verifier
writes no generated files by default. The registered runner supplies a private
bytecode cache; direct commands use `-B` and assume no preexisting bytecode.

The direct verifier was also checked with Python 3.13 and 3.15.
Direct source-export replay needs this package and the pinned
`research/one-sided-six-multisets/data/data.txt` at their repository-relative
paths. It needs no Git database, network, native compiler, Lean or solver.
The generic metadata runner additionally requires repository Git provenance.

## Evidence and coverage

The primary checker enumerates all 788,035 six-dimensional linear label
spaces by their rank-three annihilators. A separate direct-basis implementation
enumerates 97,155 linear five-spaces in eight coordinates and all 777,240
affine cosets. Both yield exactly the same 776,806 distinct live masks,
including the empty mask. Every root direction is checked without assuming
any orbit transitivity. Exact union checks include every potentially extremal
pair, and all 120 attaining witnesses carry independently checked binary spans.

Controls compare the pair-pruning rule with exhaustive unions on 255 small
inventories, reject a literal 39-coordinate counterexample, and test false
single-flat bounds, false sharpness, changed sources, changed labels/roots,
receipt corruption, witness corruption and output safety. The original
TWOSIDE filter is retained unchanged and reproduces all 24 historical cell
counts. [CHECKS.json](CHECKS.json) records actual validation and limitations;
[ENGINEERING.md](ENGINEERING.md) records the bounded-code review.

## Scope and credit

This answers a narrowed part of [the C5 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-19000404).
Baseline main is `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6.
[TASK.json](TASK.json) records the changed scope from the formal-interface card.
The new finite enumerators, cover proof and quotient application are by
Nick Petalas. Credit DreamingOfClouds/PR3154 at
`708f0ad8928c383de8294aea3c126e9461d2066d` for TWOSIDE, the handoff and the
retained E8/P112 decoder lineage. The unchanged geometry comes through
Nick Petalas/PR3177 at `47558b8d6e296b15496edd19dbf3fb0f5f9f6ed5`, following
PR3161/3162/3164. [SOURCES.json](SOURCES.json) pins the exact source heads,
paths, Git blobs and SHA256 digests. Retained files preserve their original
notice and Apache-2.0 license.

Development and local checking used substantial automated assistance.
The evidence is author-checked, not independent human or proof-kernel review.
The standard Weyl-chamber theorem and original TWOSIDE reduction remain
written dependencies. No selected scientific record or frozen predecessor
is changed. Other pending exclusions and complete supplier budgets are not
recertified here.

## Open next questions

Can the actual common-fourteen-cut, rank-six direction set span six?
A bound of five would exclude the named historical profile. First retain
one common cut set on a six-flat pair and compare a small exact slice with
literal subset checks. Existing separate-cut/one-anchor witnesses do not
settle this question. No complete current residue count is asserted here.

The earlier calibration profile `2,3,4,5^2,6^5` is already excluded by
PR3169 at `2dbbd3004b70772cef200e341037c7c05b094fbc`; independent review
caught and corrected the draft's application-overlap error. Credit that
coordinate-bound predecessor. PR2985 at
`b07b0e3226bcbe32a90c1b43ab225c339086f7b5` supplies older three-flat
root-cover censuses; the new sharp two-flat theorem has different scope.
These are context pins in SOURCES.json, not imported scientific assumptions.
