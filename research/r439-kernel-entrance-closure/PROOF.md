# Proof of the fixed first-contact classification

## 1. Precisely delimited finite problem

Let `K : F₂^439 → F₂^111` be the dirty-helper response of the frozen PR589
A/scatter/B/C word. Physical helper labels run from 222 through 660. Its D
section has one target-only compensation matrix. The verifier independently
replays the raw word on 661 formal dirty columns and requires that its helper
response is exactly this D matrix; sources and helpers are restored and the
remaining target map is `y_i ↦ y_i+x_i`.

For each helper `h`, let `F_h ≤ Q^8` be the span of the frame at its first A/B
contact. Every helper occurs, and every retained copied helper has an A contact
before the copy. Thus omission of scatter in the first-contact extraction does
not skip any earlier helper contact. Each `F_h` has dimension one or two.

A **candidate direction** in this note is a nonzero binary vector `c` and a
nonzero rational subspace `U` such that

1. `Kc=0`;
2. `U ⊆ F_h` for every `h ∈ supp(c)`.

These are necessary conditions for the particular common-frame entrance
mechanism: an initial helper coordinate mapped into the raw helper bank as
column `c` is absent from D exactly when `Kc=0`; every helper carrying that
coordinate must admit the same entrance subspace before its first frozen raw
contact. We do not assert that these two conditions suffice for a physical
compiler, address realization or hosted execution. We do not assert their
necessity for differently timed or differently framed mechanisms.

**Finite classification.** In this precise problem, every candidate has
`c=e_444+e_470` and
`U=span_Q(0,1,0,-1,1,0,1,0)`. Consequently there is only one independent binary
candidate direction, even without a support-size bound.

## 2. A finite closure covers all rational entrances

Let `L` be the nonzero intersection closure of the distinct `F_h`. Because all
generators have dimension at most two, its elements are exactly:

- the distinct original lines and planes;
- every nonzero intersection of two distinct original planes.

Indeed, an intersection involving a line is either that line or zero. An
intersection involving only planes is one plane if all are equal; otherwise
choose two unequal ones. Their intersection has dimension at most one, and
further intersections can only preserve that line or make it zero. This proves
closure and completeness without sampling vectors or bounding their rational
numerators or denominators.

For any candidate with support `S`, let `V=∩_{h∈S} F_h`. Then `U⊆V`, so `V≠0`
and `V∈L`. Define the eligible set

`I(V)={h : V⊆F_h}`.

All of S lies in I(V). Thus c belongs to the kernel of the column restriction
`K|_{I(V)}`. It suffices to compute these finitely many kernels. Testing the
maximal intersection V is enough even when U is an arbitrary subline of a
plane: V contains the whole support's common subspace and still has every
support helper in its eligible set. No possible candidate is discarded by
using V rather than listing infinitely many sublines U.

## 3. Exact finite certificate

The certificate has 264 original rowspaces (111 lines and 153 planes). All
`153 choose 2 = 11628` distinct plane pairs are checked. Of those, 549 have a
one-dimensional intersection. After identifying equal rational subspaces the
closure consists of 213 lines and 153 planes, or 366 elements.

For each V, `CERTIFICATE.json` lists a rational RREF basis of V, the entire
I(V), rank of its response matrix and a complete binary nullbasis. Column
Gaussian elimination retains each input column's binary combination mask.
A newly dependent column produces one null vector with a distinct highest
input position. Those dependency vectors are independent and their count is
`|I(V)|−rank(K|I(V))`; hence they form the full kernel, not a sparse sample.

The separately implemented checker converts source spaces and certificate
spaces to exact orthogonal Gram projectors, so equality is equality of rational
subspaces rather than coordinate representatives. For two different planes
A and B, it forms the residuals of A's two basis vectors after projection onto
B. A nonzero linear combination in the joint kernel exists exactly when those
two residual columns are dependent. It obtains that line from one nonzero
residual coordinate and checks every residual coordinate. This yields exactly
the same closure. Eligibility is checked by exact projection. Binary row
elimination of all target equations independently recovers every rank and
nullbasis.

There are 365 zero kernels. The remaining space is the line U₀ stated above,
with `I(U₀)={390,391,444,470,578,580,582}`. Its response rank is six and its
kernel is spanned by `e_444+e_470`. Over F₂ that one-dimensional kernel has only
one nonzero vector. The intersection `F_444 ∩ F_470` is exactly U₀ (checked
by both engines' source geometry). Therefore every nonzero U admitted by the
candidate pair is U₀ itself. This proves the finite classification.

## 4. What the result does and does not bound

For any invertible binary helper-basis matrix in this same common-first-contact
model, independent dormant coordinates would have independent response-null
columns. There is only one allowable nonzero column direction, so the model
cannot provide two independent dormant coordinates. A single direction also
has only a one-dimensional common entrance. This is an algebraic limitation
on the stated boundary, not a global bound on gate counts or recursive moments.

PR1179 constructs this direction by a restored pair shear; its finite word and
physical costs are not re-executed here. New helpers, changed first contacts,
nonuniform timing, later cuts, raw-word changes, changed target interfaces and
broader address maps are outside this proof. Finite exact checking of this
source word does not establish any inherited all-size, realization, hosting,
precision/tape or analytic implication, or the integer-multiplication theorem.
