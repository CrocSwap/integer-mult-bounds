# Exact bit grouping and inherited compiler obligations

## Rational orthogonality and explicit partition

On the 23-dimensional rational space use H=9I−J. For a triple T let t_T
be its indicator column. Then t_TᵀHt_U=9|T∩U|−9. Each triple has norm
18, and its orthogonal projector is

    P_T = t_T (3t_Tᵀ−1ᵀ)/6.

Distinct triples meeting in one point have P_T P_U=P_U P_T=0. A class of
11 triples through one common point and 11 disjoint pairs is therefore an
orthogonal rank-11 family. The profile verifier checks every Gram incidence,
coverage, the integer identity Q²=6Q for Q=6ΣP_T, trace(Q)=66 and HQ symmetric.
The rational denominator 6 is inherited from the old rank-one projectors.

The partition generator works modulo 23. Each of the 77 translation orbits
of triples can be represented by {0,a,b}. Requiring a quadratic residue a
and nonresidue b leaves one or three possible centers. The 55 forced choices
give degree five at every nonzero point. A deterministic exhaustive search
chooses the remaining 22 pairs to add degree two at every point. The resulting
7-regular bipartite graph has seven explicitly computed perfect matchings.
Their translated sunflower classes give 7×23=161 classes of 11. The exported
1771 triples are checked against the complete triple set, with no repetition.

## Share restored scratch between completed cores

The pinned opposite-bank proof states that a role s beginning in frame σ_s
has completed-core relative dirty residual

    E_(s,b) = (I−P_σs) ⊗ P_b

in the first tensor orientation, or P_a⊗(I−P_σs) in the reflected orientation.
This is the already gauged residual, not a dimension inferred by cancellation.
The literal scalar word restores each arbitrary logical scratch register
individually, including the nonzero initial gauge. The initial and final
gauges are part of the supplied core identity.

For a projector E define D_E by blocks [[I−E,E],[E,I−E]]. Direct multiplication
gives D_A D_B=D_(A+B) whenever AB=BA=0. Thus serial execution of all completed
cores in a class J on the same physical role s leaves exactly

    E_(s,J) = (I−P_σs) ⊗ Σ_(b∈J) P_b,
    rank E_(s,J) = (23−dim σ_s)|J|.

Aliasing occurs only between completed, individually restored cores. The
construction starts with one new arbitrary dirty register per physical
shared role; it does not identify two independently prescribed input values.
Within each core all its original distinct logical roles remain distinct.
Data roles and all internal events, copied centers, bridges and endpoint
corrections retain their old allocation and order. Both tensor orientations
use the same argument. After a class, one explicitly paid complement child
has projector I−E_(s,J) and width 529−(23−dim σ_s)|J|. Its composition with
D_E is D_I. Every complement is proper and nonzero.

The new allocation is W=2×1771²+2×161×28866=15567734. The profile replaces
only the old `auxiliary_exteriors` class. It enumerates all new complements
and retains every other old multiplicity. The total rank is 8233987097,
so 529W−rank=1344189 exactly. This unchanged deficit is independently checked.

## One basis, one execution prime, paid routing

The expanded family consists of all old internal residuals, copied-center,
bridge and endpoint projectors and **all new group complements**. Choose one
generic rational similarity for this entire finite family so the leading
minors needed by the PR104 factorization are nonzero. The finite product of
the corresponding nonzero polynomials is nonzero; enumeration of rational
matrices terminates. Apply that same similarity to every incident frame,
gauge and endpoint and then the same global opposite-bank conjugation.
No edge gets an independent basis switch or a free adapter.

Only after the entire finite basis and factorization are fixed, choose one
odd prime avoiding every denominator and pivot numerator. The prime used
inside rank checks (Q31) is merely a nonzero-determinant witness and is not
automatically the execution prime. All rational operator identities then
hold over the retained radix-q atom ring. This extends the finite avoidance
set from the inherited compiler; it does not change its all-size contract.

Each idempotent produces one child of its full rank with its paid PR104
atom adapters. For f atoms, the cross shear uses K⊗C_f. Every head atom is
physically earlier than every tail atom, and lower-triangular same-bank
matrices expand into earlier-control scalar passes. The fixed finite family
therefore has the inherited O(Vn) adapter charge per recursive node. Reversal
is represented inside those paid indexed atom operations, not treated as a
free rearrangement. The grouped allocation changes constants and must be
used in the enclosing stopped/row-reserve calculation.

The ordinary two-call wrapper is applied once outside the reversed recursion
and sequentially reuses restored row stock. This package does not price it.
The three row reserves and all stopping, precision, tape, prime-supply and
analytic constraints belong to the enclosing final certificate.

## Finite witness and exact arithmetic

The scalar schedule is frozen, while the literal physical event stream is
regenerated from it. Exact frame inclusion checks bind actual source order
and every auxiliary/target chain to nondegenerate rational frames. Forward
and reverse-chronological, bank-swapped, complemented-frame replay verifies
all formal input and dirty columns over F2, including all original center
macros. The new grouping leaves that local word unchanged. Event bytes and
local rank histograms are compared with the frozen PR128 ledger.

For the complete new histogram c_t, the moment certificate proves

    Σ_t c_t (t/529)^(1−a) / W < 1,
    a = 129310447 / 10^12.

Logarithms have a rational 24-term artanh-series upper bound with its exact
positive tail, rounded upward to denominator 10^12. For u=a log(529/t)<1,
exp(u)≤1+u+u²/[2(1−u/3)]. All arithmetic is rational. The maximum child 518
has exact halving degree 33, checked by 2×518^33≤529^33 and failure at 32.
The accepted moment upper bound is strictly below one. The next 10^−12
grid point fails this upper enclosure; no claim about exact noncontraction
at that next point is made. Numerical root estimates are not proof inputs.

