# Independent review of the fixed E8 package

Reviewer: a separate OpenAI Codex agent, `/root/e8_cost_review`.
This is an independent agent review. It is not human review or a proof-kernel
certificate. The reviewer did not write the submitted mathematical proofs.

Review result: **PASS for the stated scope**. No material mathematical issue
remains in the reviewed package. Publication is justified as two related,
scoped obstructions. Neither result is a supplier construction or a verified
improvement to the complete kappa bound.

The reviewed package is
`work/project-final-cleanup-20261022/early-remainder-audit/packages/e8-small-redundancy`.
`REVIEWED-FILE-HASHES.json` records SHA-256 for all 30 reviewed files.
The final check confirmed that those bytes did not change during replay.
The local PR description standard was read before this review:
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.

## Claims checked

1. Over Q, nine totals assigned to the nine specified binary coordinate
   hyperplanes, with span containing the canonical E8 coefficient space,
   are individual nonzero scalar multiples of `a_i-t`. Each total has 64
   nonzero coefficients. Its binary source labels span its full
   dimension-eight coordinate hyperplane.
2. Over F2, every factorization of the fixed 120-line corrector matrix
   `K(q,r)=1+(q dot r)/2 mod 2` with at most eleven outer-product terms has
   rational source-reader pairing-rank sum at least 72. Factors outside
   the rank-nine code are permitted.

These are different coefficient fields and different support prices. The
first uses rational coefficients and binary label spans. The second uses
binary coefficients and the rational Euclidean pairing of root spans.
Neither theorem allows substitution of one price for the other.

The physical interpretation of the second bound requires separate scalar
copy trees, drop-free gathering, and readers at the required orthogonal
frames. The written algebraic theorem does not require that interpretation.
Shared delivery, changed matrices, punctures, and twelve or more terms are
outside its scope. No complete bill for access, restoration, hosting,
physical tapes, or recursive children is supplied or claimed.

## Proof review

The rational proof is complete within its hypotheses. The pair equations
and triple equations prove full binary support span for each nonzero
element of the rank-eight coefficient space. This forces nine independent
retained totals and a one-dimensional quotient. Quotient normalization
then puts every pairwise difference in that coefficient space. The common
forbidden triples force each difference to be a multiple of `a_i-a_j`.
The three-index consistency equation makes that scalar common. Evaluation
at a forbidden coordinate determines the remaining common function.
The eight pair rows prove that the actual scatter has exactly the required
row space. The displayed scatter identity proves that the classified
totals can reconstruct it.

The source-frame argument tracks source coefficients separately from
arbitrary initial helper dirt. Nested frame changes and common-frame gates
preserve that invariant. Cancellation does not create a forbidden source
coefficient. Thus the stated frame and copy-charge consequence follows for
the specified certificate format. This is a written bridge, not a replay of
the whole circuit.

The binary coset proof covers all root hyperplanes. A root support of rank
at most seven extends to a rank-seven root flat. A Weyl transformation can
move its normal into a closed dominant chamber. The positive-root expansion
then identifies a seven-simple-root subsystem. This explains why all eight
deletions suffice; they are not sampled hyperplanes. The same argument
within E7 makes its seven deletions sufficient for every proper E7 root
span. The primary replay checks reflection closure and the finite ranks.
The reviewer also checked integral, single-sign expansions of all 240
signed roots in the reported simple basis without importing package code.
The Weyl-chamber reduction remains written mathematics.

The ten-term argument uses the complete description of the low-rank words
in each outside coset. The non-E7 case has pairwise orthogonal isolated
roots. The E7 case also needs complementary support rank and common
neighbors; the proof uses both. Their bounds give a total coset defect of
at most eight.

The eleven-term proof includes rank-eight star centres and omitted centres.
This is necessary for its defect identity. If the sum of the three centres
is a nonzero codeword, the small-change lemma forces the residual support
into one E7 hyperplane. Any omitted centre then contains its normal in the
span of the removed orthogonal roots. If that normal is not one of those
roots, its four nonzero coefficients contradict the pairwise intersection
bound. The remaining normal-root cases each give a basis dependence.
If the centre sum is zero, the three dual vectors in the lifted root spaces
prove the bound on distinct satellite roots. The duplicate count covers
all pair types. The sole possible defect-17 equality case forces a rank-one
centre and contradicts a second centre's rank eight.

The factor-rank reduction is complete. Sylvester's inequality leaves the
six listed rank pairs. Zero terms can be removed. Repeated columns can be
merged without increasing the pairing-rank objective, including terms of
zero cost. The `(10,10)` case uses both coset budgets. The `(9,11)` case and
its transpose reduce to the eleven-dimensional basis theorem. Fewer than
nine terms are impossible by binary matrix rank.

## Fresh checks

All mathematical checks ran sequentially with the Python standard library
on CPython 3.14.7. No package module was imported by the separate control
script. Run from the workspace root:

```sh
python3 -B work/project-final-cleanup-20261022/early-remainder-audit/packages/e8-small-redundancy/verify.py
PYTHONOPTIMIZE=1 python3 -I -O -B work/project-final-cleanup-20261022/early-remainder-audit/packages/e8-small-redundancy/verify.py
python3 -B work/project-final-cleanup-20261022/reviews/e8-cost/independent_controls.py
```

The first replay passed in 13.26 seconds. The final isolated and optimized
replay passed in 12.92 seconds. Its child commands use `-E -B`, so inherited
Python environment flags cannot disable historical assertions. All 30
package files were unchanged. The expected final lines were:

```text
PASS_E8_SMALL_REDUNDANCY coordinate_rigidity=9 binary_terms<=11 pairing_floor=72 no_new_kappa
PASS_E8_INDEPENDENT_CONTROLS root_expansions=240 coset_words=512 rejected=5
```

The replay reproduces all saved mathematical receipts, all 511 nonzero
codeword supports, all eight E8 and seven E7 deletion cases, the outside
weight histogram, and the exact similarity between both coordinate models.
It also reproduces the rational coordinate ranks, 14,400 scatter entries,
and the separate 72-variable modular ranks.

The separate checks give one complete outside-coset support-rank histogram:
one word of rank one, one word of rank seven, and 510 words of rank eight.
Its total defect is exactly eight. Deleting a root from its own corrector
row lowers support rank to seven. Removing the affine constant from the
binary kernel changes its rank from nine to eight. These are exact boundary
checks, not a search for a new construction.

Five negative controls passed. They reject an input hash change, an omitted
root, a changed certificate port order, and a false receipt with its hash
updated. A malformed root norm with an updated hash is also rejected at the
original assertion while `PYTHONOPTIMIZE=1` is set and the wrapper uses
isolated optimized mode. Each mutation runs only in a temporary copy.

One intermediate optimized replay passed its mathematical checks but saw a
concurrent wrapper edit. Its file-immutability check therefore failed.
That result is retained in `verify-isolated-optimized-command.json`; it is
not the final receipt. The subsequent final replay used stable files and
passed both mathematical and immutability checks.

No Lean check, complete supplier replay, repository-wide build, hosted CI,
or independent human certification was run.

## Dependencies, credit, and overlap

`PUBLIC-DEPENDENCY-BYTE-CHECKS.json` records live GitHub reads of the two
input archives, PR446's proof, and the pinned `gx.py` source. Both archives
match the package byte for byte. All four exact source targets resolve.
The source notices retain Jacob Sussman's certificate credit and the
historical bit-word contributors. PR446's copy-tree hypothesis remains an
explicit dependency of the physical interpretation. Substantial AI help
is disclosed, and the historical reviews are identified as agent reviews.

At main commit `cef4b52f2a59009865bf8eabde1be3f159063703`, the PR3755
one-coset package uses scalar fields of characteristic other than two and
binary support prices. It does not imply the binary-factor theorem here.
It subsumes the older nine-small-total numerical obstruction, which this
package correctly omits. Its equality conditions expressly do not classify
scalar coefficients. The present fixed-coordinate classification retains
a separate use.

The tensor E8 package covers the minimum `9^d` terms, and its overcomplete
corollary requires both factors to remain in the code. The ten- and
eleven-term theorem here permits factors outside that code. The R429
package concerns a punctured 111-line matrix and gives different bounds.
Open PR3045 excludes factors outside its root code and overcomplete decoder
cases from its stated coverage. Open PR3040 concerns fitting-matrix
rigidity, not this coefficient or pairing-rank classification.

`OVERLAP-CHECK.json` records the three main-file hashes and the 315-entry
open-PR snapshot used. All titles and bodies in that snapshot were searched
for relevant field, term-count, coset, and coordinate-hyperplane claims.
This is bounded overlap evidence, not a claim of exhaustive novelty across
all closed PRs or unpublished work.

## Resolved findings

The initial ten-term proof did not separate its algebraic objective from
its physical interpretation clearly. It now defines the exact rational
pairing-rank sum and applies PR446 only to the physical interpretation.
The coordinate proof now links its exact `gx.py` source. A separate package
review found the inherited-optimization risk in historical assertions; the
E8 wrapper now uses the standard `-E` child flag. The final replay and a
targeted negative control check that fix. No mathematical source change was
needed, and no frozen historical source was rewritten.

The coordinating agent must still check the final PR description, exact
published commit links, rendered Markdown, and published readback. This
review does not assert those later publication checks have occurred.
