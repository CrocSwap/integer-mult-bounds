# Independent review of the E8 hyperplane annex

Reviewer: the separate OpenAI Codex agent `/root/e8_cost_review`.
Result: **PASS as an alternative proof and certificate annex**.
There is no new floor, supplier, verified speed improvement, or kappa result.
This is an agent review, not independent human review or formal verification.

The reviewed package is
`work/project-final-cleanup-20261022/early-projects-audit/packages/e8-hyperplane-minrank`.
`REVIEWED-FILE-HASHES.json` binds all reviewed files. The PR description
standard at `/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`
was read before this review.

## Publication scope and overlap

For the standard 120 E8 root lines and any proper real linear hyperplane H,
every F2 fitting matrix on the lines outside H has rank at least nine.
Fitting means diagonal one and zero at each distinct nonorthogonal pair.
The entries at orthogonal pairs are free. No symmetry is required.

This theorem is already implied by DreamingOfClouds' public
[PR #3045](https://github.com/CrocSwap/integer-mult-bounds/pull/3045),
[Theorem 6 at commit 16feea078f5542964ae85ca1b1f35bb94314ae78](https://github.com/CrocSwap/integer-mult-bounds/blob/16feea078f5542964ae85ca1b1f35bb94314ae78/research/nondense-pairing-square-floors/README.md).
That theorem covers the intersection of the two nonzero-normal supports
when their normals have nonzero inner product. Set both normals equal to
the nonzero real normal of H. Their inner product is then positive, and
the intersection is exactly the complement under study. The old local
row-space and column-space consequence also follows by the displayed
linear algebra. No new theorem scope should be attributed to this annex.

The useful contribution is its explicit small certificate and short proof
of this slice. Each of eight representative complements needs only thirteen
roots. The replay uses integer arithmetic and the standard library, with
no SAT solver or discovery search. No comparative speed measurement was
made. The README now states this scope and credits the stronger public
theorem. The older dense-table and minimum-term consequences are not
claimed as new.

The overlap check read the exact PR3045 source, searched the current-main
research text at `cef4b52f2a59009865bf8eabde1be3f159063703`, and checked the
315-entry `OPEN-PRS.json` snapshot. The source of the decisive overlap is
PR3045's actual mixed-normal theorem, not its numerical 72 consequence.
The retained package is justified by its alternative proof, not by an
assertion of exhaustive novelty.

## Proof review

Each certificate has eight pairwise nonorthogonal anchors. Its anchor
fitting block is I8. Each of the other five roots is orthogonal to exactly
the two anchors specified by its pair. The five distinct pairs use four
anchor indices. Witnesses at incident pairs are nonorthogonal.

If a fitting matrix had rank at most eight, its I8 Schur complement would
give `D=CB`. The diagonal equation at each witness is the sum of two
binary products and equals one. Exactly one product equals one. Assign
that pair to its endpoint. If two incident pairs had the same assigned
endpoint, the corresponding off-diagonal product in `CB` would be one,
although the fitting condition requires zero. Each endpoint can therefore
receive at most one pair. Five pairs on four endpoints give a contradiction.
The argument permits unrelated C and B and thus does not assume symmetry.

This step is specific to F2. The assertion that one of two products is
uniquely one must not be transferred to an arbitrary larger field. The
README excludes larger fields and other punctures.

The eight-case reduction covers all real hyperplanes, including those whose
root intersection has rank below seven. The checker verifies a simple-root
basis, integral single-sign coordinates for every signed root, and closure
under each simple reflection. These reflections generate a finite group:
they permute the finite root set, which spans the ambient space. Choose an
interior chamber vector with positive inner product with each simple root.
On the finite orbit of any normal, maximize its inner product with this
vector. A negative simple-root inner product would permit a reflection that
increases that maximum. Thus an orbit normal lies in the closed dominant
chamber. For a positive root, perpendicularity to that normal forces every
simple root used in its expansion to be perpendicular to the normal.

The normal is nonzero, so one simple-root inner product is positive. Delete
that node. All roots in the original hyperplane then lie in the associated
seven-simple-root span. The complement of the original hyperplane contains
the tested parabolic complement. A larger fitting matrix has at least the
rank of that principal submatrix. This proves coverage; no enumeration of
sampled normals is being treated as universal evidence.

For the rank-nine full-matrix consequence, the outside principal block
has rank nine. Its outside rows and columns therefore span the full row
and column spaces. A vector in either space supported inside H must be
zero. Every nonzero row-space or column-space vector consequently has full
rational root support span. This consequence is sound but not a new public
bound, and it says nothing by itself about more than nine factors.

## Fresh verification

The frozen historical checker was run in a temporary copy and reproduced
its entire saved receipt. The package wrapper was then run from the
workspace root on CPython 3.14.7:

```sh
python3 -E -B work/project-final-cleanup-20261022/early-projects-audit/packages/e8-hyperplane-minrank/verify.py --build /absolute/fresh/output
```

The output directory must not already exist. The fresh run returned zero
and printed:

```text
PASS_E8_HYPERPLANE_MINRANK 240 8 13
```

It ran sequentially and left all package bytes unchanged.
`wrapper-command.json` records the actual command and result.
`HISTORICAL-INPUT-HASHES.json` binds the original proof, certificate,
checker, and receipt. The staged historical files match those originals.
No frozen source was changed.

A separate script imports no package code. It reconstructs all 240 signed
roots, checks the eight normals, all thirteen roots in each certificate,
the anchor constraints, and every witness support. For each certificate,
it enumerates all `6^5=7776` choices of the B and C witness entries that
satisfy the five binary diagonal equations. None satisfies all required
off-diagonal equations. This gives 62,208 exact Schur checks in total.
For each certificate, the first four witnesses do admit a rank-eight
completion. These positive controls check the five-edge boundary.

Run the separate controls with:

```sh
python3 -E -B work/project-final-cleanup-20261022/reviews/e8-parabolic/independent_controls.py work/project-final-cleanup-20261022/early-projects-audit/packages/e8-hyperplane-minrank --output /absolute/new/result.json
```

The final line is:

```text
PASS_E8_PARABOLIC_INDEPENDENT certificates=8 schur_assignments=62208 rejected=3
```

The three rejection controls cover changed source bytes, a repeated node
with a missing deletion case despite an updated source hash, and optimized
Python mode. The wrapper's explicit node-completeness check resolves the
historical checker's reliance on the saved receipt for that coverage.
The wrapper uses `-E` for its child and rejects `-O` at entry. This is an
explicit supported-mode limit, not an optimized-mode success claim.

The universal argument remains a written proof supported by finite checks.
No Lean run, prior SAT replay, complete supplier replay, full kappa
calculation, or hosted CI check was performed. The final PR description,
rendered links, and published readback still need the coordinator's checks.
