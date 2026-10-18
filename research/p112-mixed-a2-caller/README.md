# A mixed-rank P112 shortening theorem and actual caller

Three endpoint pieces of binary ranks at most 5,5,6, outside one common set
of at most 37 P112 coordinates, have root-code intersection dimension at
most one over every characteristic-zero field. This is a sufficient bound,
not a sharp threshold. [PROOF.md](PROOF.md) separates classification from
the singleton count and states every inherited dependency.

The theorem excludes the literal historical TWOSIDE `(6,4)` profile
`5^5,6^5`. Delete four pieces, retain two code dimensions, then delete the
common support of three rank-five pieces. Its size is at most 36. The
remaining endpoint ranks are 5,5,6, and the new inequality is 84>80.
The old uniform thresholds do not directly cover this support size.

The replay recomputes all 1,120 A2 union supports, the chamber inventories,
three 2,667-space rank-five fiber censuses and three 127-hyperplane rank-six
fiber censuses. Both original and new historical-filter implementations
agree over all 7,546 multisets in the actual cell and reproduce 69 historical
survivors. An invertible nine-bit map binds all 112 original root/label pairs.
These historical counts do not give the number of currently unresolved cases.
[RESULT.json](RESULT.json) records the finite data and caller separately.

## Reproduce

Python 3.12 or later, standard library only, from the repository root:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/p112-mixed-a2-caller
```

Set TMPDIR to a session-owned external directory if local policy requires
it. The registered commands run the primary verifier and eight optimized
behavioral groups sequentially. Each has a timeout of at most 120 seconds.
`verify.py --output NEW_EXTERNAL_PATH` creates an external receipt without
overwriting an existing file. The direct scripts also work in a Git-free
export containing the package and its two declared inputs at their original
relative paths. [CHECKS.json](CHECKS.json) records executed checks and limits.

## Open next questions

Before applying this result again, reconcile another named original profile
against current public exclusions and derive its retained code dimension
and one common support. At support 38, the present classification and
singleton bounds both stop. A larger theorem needs the 30-root parabolic
case treated first. These are unrun obligations, not a proposed next
construction round. Structured relevance and blockers are in
[TASK.json](TASK.json).

## Sources and limits

Credit DreamingOfClouds/PR3154 for TWOSIDE and the original caller, Nick
Petalas/PR3249 for the rank-five fiber theorem and A2 normalization argument,
and PR3255 for the rank-six fiber theorem and original label isomorphism.
The retained root-simplex/E8/P112 lineage includes joaqcoo. Exact commits,
Git blobs, hashes and retained files are in [SOURCES.json](SOURCES.json).
Copied material and new work are Apache-2.0. Frozen predecessors are unchanged.

The global five-/six-flat capacities 12/20, uniform reflection transport and
standard Weyl-chamber theorem are inherited written/finite dependencies.
The historical global flat censuses are not rerun. The new result is a
mixed-rank proof and one caller transfer, not an independent proof of those
dependencies. Internal automated checks do not constitute independent human
or proof-kernel review. [ENGINEERING.md](ENGINEERING.md) records code bounds.

No full C5, complete decoder floor, native/physical realization, restoration,
supplier, all-size multiplication theorem, new kappa or selected-frontier
update is established. The selected cold replay, Lean and Docker are unrun.
The tentative pre-reservation `4,5^9` caller was already PR3171 and was
rejected; it is not part of the contribution.
