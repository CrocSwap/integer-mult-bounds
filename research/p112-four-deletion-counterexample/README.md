# Four deletions per direction are not four common deletions

This answers the C5 handoff in [Discussion3156](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156).
For two six-dimensional binary label spaces, five rationally independent E8
directions each qualify after at most four **direction-dependent** deletions.
Making these same five directions qualify with a **common** deletion set needs
exactly twelve lines.

The checked p=2 span-four bound therefore does not extend to the per-direction
relaxation used by `FINITE/t.c` at `R=7, p=4`. This does **not** refute the original
common-set S66+P statement, `C(P112) >= 64`, or any selected supplier. No new
multiplication exponent is claimed. The result is an author-checked finite
counterexample and a scoped proof, not independent human or proof-kernel review.

## Source and scope

The predecessor is DreamingOfClouds's [PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154),
exact head `708f0ad8928c383de8294aea3c126e9461d2066d`.
Its `checks/FINITE/NOTES.md` defines qualification by existence of at most `p`
removed lines **per direction**, a superset of the common-set condition.
Its `checks/TWOSIDE/NOTES.md` section 1 instead asks for a **common** set P.
C5's suggested complete `t.c` and `f2.cpp` runs use the stronger relaxation.
This example defeats a span-four continuation of the p=2 result. C5 does not
state one numeric target for all beta cells. This package does not determine
the correct target in each cell or the maximum dimension of the p=4 family.

The catalogue card `formal-interface-lemma` was retrieved for provenance, not
randomly assigned. The explicit new handoff took precedence. `TASK.json` declares
the changed scope from a formal-interface task to this finite decoder question.
Canonical main was `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6.
No predecessor package or selected record is changed.

## The example

Use doubled E8 root coordinates. Delete the orthogonal frame consisting of
`2(e1 +/- e2)`, `2(e3 +/- e4)`, `2(e5 +/- e6)`, `2(e7 +/- e8)`.
The remaining 112 root lines form P112.

For a root r, write its doubled vector in the doubled Bourbaki simple-root basis
listed in `verify.py`. Encode its label as the integer
`256 + sum_i (c_i mod 2) * 2^i`, with i from 0 to 7.
The predecessor's label is a one-bit cyclic left rotation of this nine-bit word.
The optional source check verifies that relation on all 112 source rows.

Take the following bases over F2, using integer XOR for addition:

```text
V1 = span {436, 6, 66, 138, 2, 57}
V2 = span {480, 84, 6, 16, 1, 2}
```

Both spaces have dimension six. Let Lambda(V) contain the root lines whose
labels lie in V, and let X be Lambda(V1) union Lambda(V2).
Their sizes are 20 and 16, with union size 32.
For a direction h, let R(h) be the labels of root lines not orthogonal to h,
excluding X. The five directions and deletion sets are:

| h | Vector | Deleted labels | Size of R(h) | Next nonzero character support |
|---|---|---|---:|---:|
| 1 | `(1,-1,1,-1,-1,-1,1,1)` | 279, 341 | 34 | 13 |
| 2 | `(0,0,0,1,0,0,0,-1)` | 317, 319, 381, 383 | 36 | 14 |
| 3 | `(1,-1,1,-1,1,1,1,1)` | 275, 337 | 34 | 13 |
| 4 | `(0,0,1,-1,0,0,0,0)` | 409, 411, 473, 475 | 36 | 14 |
| 5 | `(1,-1,0,0,0,0,0,0)` | 275, 279, 337, 341 | 36 | 14 |

Every residual has binary rank eight. Each listed deletion lowers it to seven.
The five vectors' minor on zero-based columns `0,2,3,4,6` has determinant `-2`.
Thus their real span has dimension five, despite the per-direction budget four.
With budget two, only directions 1 and 3 in this list qualify. No full p=2
census is claimed.

### Why the common minimum is twelve

For each residual R, enumerate the supports
`{r in R : dot_F2(a, label(r)) = 1}` for all 511 nonzero nine-bit a.
Because R has rank eight, this gives exactly 255 distinct nonempty supports.
Exactly one has size below twelve, namely the listed deletion set. Every other
nonempty support has size at least thirteen or fourteen, as shown in the table.

If deleting P lowers the rank of R from eight to at most seven, there is a
nonzero functional on span(R) that vanishes on R minus P. Extend it to F2^9.
Its nonempty support on R is contained in P. Therefore any P of size at most
eleven that works for all five residuals must contain all five listed supports.
Their union has twelve labels, a contradiction. Conversely that twelve-label
union works for every residual. This proves the exact common minimum.
The argument concerns nonzero character supports, not arbitrary deletion sets;
supersets of a listed cut also work.

## Reproduce

Python 3.12 or later, standard library only, no solver or network needed:

```sh
python3.12 -B research/p112-four-deletion-counterexample/verify.py
python3.12 -B research/p112-four-deletion-counterexample/test_verify.py
python3.12 scripts/research_package.py --package research/p112-four-deletion-counterexample
```

`WITNESS.json` is the complete mathematical input. The verifier reconstructs E8,
checks the frame and both spaces, computes the minor over the rationals, and
enumerates all restricted binary characters. Its output must equal `RESULT.json`.
Tests include a separate rational coordinate solve on all 120 root lines,
Leibniz evaluation of the minor, a separate XOR-code enumeration of every
residual's character supports, an exhaustive deletion check through four
lines on a 36-line residual, and rejection controls. Normal and optimized
Python must produce the same result.

For the optional exact-head source translation, export the one pinned file
into an external scratch directory after fetching PR3154's head:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git refs/pull/3154/head
git show 708f0ad8928c383de8294aea3c126e9461d2066d:research/p112-reduction-to-conjectures/checks/FINITE/data80.txt > "$RUN/data80.txt"
python3.12 -B research/p112-four-deletion-counterexample/verify.py --source-data "$RUN/data80.txt"
```

Set `RUN` to your session-owned external directory first. The source check
requires the entire file's pinned SHA256, checks all 112 label rotations, the
actual six-dimensional spaces, five direction IDs and deletion translations.
The predecessor head is documentary provenance in `SOURCES.json`, not a Git
object required by the default replay. This keeps the self-contained proof
replayable in CI and in a Git-free export without fetching an unmerged fork.

The nomination used a scratch adaptation of the predecessor's `t.c`, selecting
rep 82 and finding the first example at second-mask index 1839. Search was only
a proposal mechanism. Acceptance uses the literal witness and separately
written checker, not a claimed exhaustive search. `EVIDENCE.md` records commands
and environment. The whole C5 census and other predecessor suites were not run.

## Implementation bounds

All mathematical loops are bounded by eight coordinates, 120 root lines,
512 binary labels, five directions or 120 determinant permutations.
The exhaustive test checks `sum_{k=0}^4 binom(36,k) = 66712` deletion sets.
Inputs are capped at 32 KiB, or 2 MiB for the optional source file.
Internal assertions do not replace boundary validation or proof checks.

Power-of-Ten rule 3 has a managed-runtime deviation in `verify.py` and
`test_verify.py`. Python and Fraction allocate during checking. Fixed domain
sizes bound every live collection, with at most 512 character supports of at
most 112 labels. No persistent workers or unbounded queues exist. Replacing
Python with fixed-capacity arithmetic is only justified if a deployment needs
allocation-free execution. Rule 9's test-framework dispatch is limited to the
finite unittest cases. The verifier itself uses direct calls.

## Open next questions

- Does the original common-P beta statement hold in the needed cells? Retain
  one common set in the quantifier and test the smallest unresolved cell.
  This matters for the two-sided decoder reduction. The blocker is a precise
  cell-specific target bound and a common-set search, not completing the
  failed per-direction span-four continuation.
- Can a cheaper necessary condition retain enough coupling between the deleted
  sets? Start by rejecting this literal example whenever a common budget four
  is required. It may reduce future census cost, but needs its own soundness
  proof and bounded coverage before it can close C5.

Credit DreamingOfClouds for PR3154, FINITE/FINITE2, the C5 handoff and the retained
K1/K2, E8 and decoder lineage. Nick Petalas supplied this example, exact common
minimum and independent checker. Apache-2.0. Substantial automated assistance
was used in analysis and local checking; no independent human review is claimed.
