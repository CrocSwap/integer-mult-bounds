# One-root deletions and a common cut have different span bounds

Use the fixed P112 root order and leading-one nine-bit labels in the pinned
canonical geometry. Write L(U) for the root lines whose labels lie in a binary
space U, and Off(h) for the roots r with r dot h nonzero. All root coordinates
are integers, so this witness works over every characteristic-zero field.

## Exact result

There exist fixed binary spaces U,V of dimensions seven and four, respectively,
and eight directions h_i such that:

1. The directions are an orthogonal basis of the eight-dimensional real space.
2. For each i, removing ONE root t_i, allowed to depend on i, leaves
   Off(h_i) outside L(U) union L(V) with binary support rank seven.
3. For every ONE common set P of at most two roots, h_i qualifies under that
   common cut exactly when t_i belongs to P. The qualifying span among these
   eight directions therefore has dimension at most two, and two is attained.

Thus the maximal direction span for the direction-dependent one-root-cut
extension of alpha74 is eight, the ambient maximum. The common-two-cut bound
here concerns ONLY this exhibited eight-normal family. The universal question
whether ALL directions qualifying for arbitrary fixed U,V,P span dimension at
most five remains UNSETTLED. This is not a counterexample to that question.

## The literal witness

WITNESS.json lists all root indices in L(U),L(V), all eight integer normals,
and the individual singleton cuts. Indices refer to the sorted canonical P112
roots returned by the pinned geometry.py, with zero-based numbering.
The cover lists have 32 and eight roots. Exact binary elimination verifies
that their spans have dimensions seven and four and that their complete
root closures equal the listed sets. This avoids interpreting a support-cap
sum as a realizable union.

The normal matrix, with one direction per row, is

```text
 1 -1 -1  1 -1 -1  1  1
 1  1  1  1 -1  1 -1  1
 1 -1  1 -1 -1 -1 -1 -1
 1 -1  1 -1  1  1  1  1
 1  1  1  1  1 -1  1 -1
 1 -1 -1  1  1  1 -1 -1
 1  1 -1 -1  1 -1 -1  1
 1  1 -1 -1 -1  1  1 -1
```

Its Gram matrix is 8 times the identity. Hence every subfamily is independent,
also after scalar extension to any characteristic-zero field. The eight
normal roots t_i have indices 45,94,52,59,97,50,72,71, respectively. They are
distinct and lie outside both covers.

For each i put R_i=Off(h_i) minus the two covers. Direct exact checks give

```text
|Off(h_i)| = 53; |R_i| = 33;
rank_F2 labels(R_i) = 8;
rank_F2 labels(R_i minus {t_i}) = 7.
```

The one-root cuts therefore prove the direction-dependent span-eight result
without any catalog-completeness, root-subsystem or real-chamber assumption.

## Why a common two-root cut qualifies exactly its own normals

Enumerate all 512 binary linear functionals on the nine-bit labels. For each
i the histogram of their nonzero support sizes on R_i is

```text
weight       0  1 12 13  16  17 20 21 32 33
functionals  2  2 32 32 188 188 32 32  2  2
```

The ONLY nonempty functional support of size at most two is the singleton
{t_i}. Both functionals of weight one have that same support. The two
functionals of weight zero agree on the whole eight-dimensional span.

Suppose deleting P with |P|<=2 lowers the rank of R_i below eight. There is
then a linear functional that vanishes on all retained labels but does not
vanish on the span of R_i. Its nonempty support is contained in P. The finite
functional certificate forces that support to be {t_i}, so t_i belongs to P.
Conversely, removing t_i already lowers the rank to seven, and deleting more
roots cannot raise it. This proves the exact eligibility rule.

At most two distinct t_i belong to a two-root common cut, so the eligible
subfamily has span at most two. Choosing any two distinct normal roots attains
two. A separate checker, using matrix row elimination rather than the primary
pivot dictionary and functional enumeration, checks every one of the 6,216
root pairs. It finds 5,356 cuts qualifying zero normals, 832 qualifying one,
and 28 qualifying two. Cuts of size zero or one follow by monotonicity.
The two engines share the authenticated canonical geometry input; they are
not independent audits of the root-label model.

## Relation to the reserved question and predecessors

PR3154's alpha74 statement has no additional deletion and direction-span bound
four. Its t.c deletion routine tests an existential cut separately for each
h. That stronger direction-dependent relaxation is intentional, useful when
it succeeds, and is not a common-cut theorem. The original no-deletion
statement is unchanged and not challenged by this witness.

PR3289 identifies the historical row 2^3,7^7 and quotient basis [2,2,2,7]. Its
actual supports fit a seven-flat, a four-flat and one common two-line set.
That motivated this session's universal common-two span-five question.
The bounded probe found instead the exact obstruction above. Replacing the
common-cut test by the predecessor's direction-dependent relaxation cannot
prove span five, since even one deletion per direction permits the full span
eight. A fixed-cut argument remains necessary. No conclusion about the
historical caller follows from the eight-normal family.

The candidate came from a bounded, modified copy of PR3154's proposer, using
one seven-flat representative and eight-root four-flats. That search was not
exhaustive. Neither its failure to find a common-cut counterexample nor its
finite direction catalog is used as proof. The committed verifiers reconstruct
and validate only the actual witness from canonical-main geometry. Exact
predecessor proof/code bytes and provenance are retained for attribution and
to make the changed quantifier reviewable; no pending Git objects are needed.

## Limits and Open next questions

The universal common-two span-five predicate remains open in this package.
A useful next step is a fixed-cut classification of all qualifying zero
patterns for one cover, before a global bound or a counterexample search.
The obstruction is quantifier-specific; it does not rule out a common-cut
lemma or every cover architecture.

No new caller exclusion, full C5, global decoder floor, physical/native
program, restoration or consumer invoice, supplier admission, multiplication
theorem, selected-frontier change or kappa is established. Historical capacity
censuses, the full alpha74/beta theorems, Lean, Docker, the selected cold replay,
and human/proof-kernel review were not performed.

Credit DreamingOfClouds/PR3154 and its retained E8/P112 lineage, Nick Petalas's
PR3289 quotient-basis handoff and canonical root-simplex geometry, with the
PR3161/3162 and joaqcoo lineage retained by that geometry. Apache-2.0.
