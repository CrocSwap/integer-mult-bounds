# Local-ring fallback with a fixed instruction schedule

This package emits and independently checks the **algebraic bad-class
fallback** retained by the selected BIT supplier. A zero leading residue
need not be zero modulo q^w. The compiler uses low residues to choose unit
pivots, evaluates coefficients in the full ring, and reconstructs the entire
ADDRESS operator with explicit inverse order and determinant sign.

The new artifact is an executable common schedule and its independent
consumer. Gaussian elimination, its diagonal-covariance argument and the
fallback allowance are inherited from the source527 cover note; their
existence and numerical bound are not claimed as new. There is no supplier,
stock-coefficient or exponent improvement.

## The precise implication

Fix an odd prime q, w>=1, N=2m, and an invertible N-dimensional residual
of determinant +1 or -1 over Z/q^w Z. Its coefficients may depend on exposed
parent fields, but not on the active ADDRESS values, VALUE data or fresh
descendant stock. Atom columns may have distinct diagonal unit conjugations
of the same unweighted residual.

The [written proof](PROOF.md) establishes:

1. The first-unit pivot itinerary depends only on the unweighted low residue.
2. A complete schedule of N(N-1) shear slots and N-1 diagonal-pair slots
   works for every high lift in that low class and every such weight array.
3. Full-ring elimination and literal inverse chronology implement the exact
   residual. The program preserves arbitrary complete spectators.
4. Under the stated ordered-affine and completed weighted-child interfaces,
   every child has at most f atoms and the inherited child allowance is
   `6N(N-1)+3N+6(N-1)=24m^2+6m-6 < 32m^2`.

At selected dimension m=64, that allowance is **98,682**, within the charged
131,072. Additive adapters, the fixed sign, coefficient preparation and
routing remain paid separately. This is not a new or reduced selected bill.

Keeping zero and identity slots matters. Two high lifts with the same low
matrix can require coefficients 0 and q in one shear slot. Likewise, the
identity diagonal pair obtained from an unweighted swap becomes nontrivial
under diagonal weighting. Eliding those slots can preserve one finite
operator while failing the common-program contract. The package checks
operator equality and schedule coverage separately.

## Nonunit witness and selected binding

For q odd and w>=2, take

```
G = [[q,q-1],[1,1]],  det(G)=1,
P = G diag(1,0) G^-1.
```

Then P is a split rank-one projector with P[0,0]=q, a nonzero nonunit.
At modulus 9 it is `[[3,3],[1,7]]`. Its full four-coordinate residual
`D_P` is invertible even though the generic northeast pivot is not a unit.
Dropping nonzero q-multiple shears changes its full operator while leaving
the low-residue computation unchanged.

Embedding G on axes 0 and 42 of `diag(I_42,0_22)` gives a GL64 rank-42
model. The independent oracle constructs this chart and its residual by
basis-vector conjugation, separately from the compiler's block formula.
It is a witness in the assumed full-cover model, **not an emitted selected
physical residual ID**.

The source-pinned PR1087 assembler binds the selected PR589 receipt by its
Git blob. That receipt supplies m=64, 28,425 physical roles and maximum
child rank 42. The historical source527 note has m=67; only its generic
algebra is reused. The selected pricer's `32*m*m` surcharge is authenticated.
No predecessor Python is imported or executed.

## Exact coverage and reproduction

Use standard-library Python 3.12 from the repository root:

```sh
python3.12 scripts/research_package.py --package research/selected-bit-bad-class-fallback
```

The registered replay checks the fixed [RESULT.json](RESULT.json), source
bindings and behavior controls in normal and optimized Python. The default
verifier never overwrites or regenerates a missing receipt. To reproduce a
candidate receipt separately, pass `--write-result /new/external/path.json`;
an existing path or an output inside the package is rejected.

Finite coverage is deliberately separate from the all-parameter proof:

| Domain | Coverage |
|---|---:|
| All 2x2 determinant +/-1 matrices modulo 3, 9, 5, 25 | 48 + 1,296 + 240 + 30,000 = 31,584 |
| Complete determinant-sign high lifts modulo 9 and 25 | 31,296 lifts in 288 low classes |
| GL64 rank-42 model, weighted 128-coordinate residual | All coefficients at (q,w)=(3,2),(5,3),(7,1) |
| Varying unit weights and arbitrary complete spectators | f=1,2,3,5; all 16 orientations of four fields, 64 fixtures |

These small primes are arithmetic fixtures, not admitted selected primes.
`oracle.py` uses direct value/basis execution, a separate Schur-complement
pivot calculation and explicit reversed-child maps. It imports no compiler
code. Meaningful controls detect lost nonunit terms, inverse order/signs,
diagonal-pair order, nonunit inversion, unpaid reversal, omitted determinant
sign, changed targets, missing schedule slots and spectator corruption.
Disabling the named complete-coefficient check makes its defect pass,
demonstrating that the control tests that check. Source/receipt corruption,
no-overwrite and read-only relocated replays are also covered.

## Relation to other work and limitations

The task draw was `uniform-transfer-audit`, seed
`d6eb344e6d2d09d0b7ec2e982bdc5ff9`, priority revision 4. The scope was refined
to the complementary bad-class branch after live overlap found PR2140's
fixed-port route and an active generic-good rank-42 lowering claim.
[TASK.json](TASK.json) records the domain, stop rule and source heads;
[SOURCES.json](SOURCES.json) pins all external inputs. The selected record
and catalogue are historical provenance, rather than moving replay inputs.

The conditional stock proofs [PR2084](https://github.com/CrocSwap/integer-mult-bounds/pull/2084)
and [PR2120](https://github.com/CrocSwap/integer-mult-bounds/pull/2120),
fresh-fiber theorem [PR2097](https://github.com/CrocSwap/integer-mult-bounds/pull/2097)
and carry route [PR2140](https://github.com/CrocSwap/integer-mult-bounds/pull/2140)
remain distinct results. The active good-child claim in
[Discussion2114](https://github.com/CrocSwap/integer-mult-bounds/discussions/2114)
and fixed-port stream work in
[Discussion2149](https://github.com/CrocSwap/integer-mult-bounds/discussions/2149)
are complementary. The final overlap refresh found Jose Manuel's
[PR2157](https://github.com/CrocSwap/integer-mult-bounds/pull/2157), which
publishes that fixed-route reduction and explicitly leaves bad-residue
fallback open; it is parallel work, not an input certified here.
Earlier PR461/465/490 already discuss sharper fallback
pricing; this package does not claim that numerical refinement.

This is an abstract ADDRESS program with a conditional child tariff. Actual
selected residual/owner/common-label binding, physical tape/routing admission,
completed-child internal borrowing, full invocation domains, global
precision and outer transfer remain open. No full selected cold replay,
formal-kernel proof, independent human review or hosted-CI pass is claimed.

## Open next questions

**Can one actual selected bad residual be lowered onto its paid physical
layout?** Start with an emitted selected residual and annotate every ordered
adapter, coefficient descriptor, reversed child and restored row field.
This would connect the algebraic program to the remaining all-size compiler
obligation. The blockers are selected residual provenance, paid routing and
the inherited completed-child implementation, not another moment estimate.

## Credit

The source527 package preserves the cover framework and credits Henry Grant,
Rohan Arun, eumemic and its prior geometry/compiler lineage. The selected
PR589 tuned BIT pipeline is DreamingOfClouds' work on eumemic's PR555, with
the original nine-stage, hosting and E8 credits retained in the source notices.
Rohan Arun's selected PR1094 assembly builds on Jeremy Kothe's PR1087.
Adam Gall authored PR2084/2097 and Nick Petalas PR2120/2140; Josie Elliston
and ToikY supplied the stock/cutoff audit lineage. Their results and original
fallback theorem retain credit.

Prepared for Ross Richardson with substantial OpenAI Codex assistance in
proof, implementation and separate recursive-interface/exact-verification
specialist review. Apache-2.0. Frozen sources and their notices are unchanged.
