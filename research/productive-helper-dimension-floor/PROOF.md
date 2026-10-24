# Fixed projection dimensions: arbitrary Lagrangian chart obstruction

This source-specific theorem concerns the unchanged round-three word in each orientation, with all
chronological paid incidences retained and the eight owned center costs fixed.
It does not fix the subspace direction or its quadratic form. At each node it
fixes only the dimension of the chart's projection onto the first (x) half of
the binary symplectic coordinates, equal to the original frame dimension.

The source is `research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`.
The canonical compact JSON payload SHA-256 is
`cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.
The separately reconstructed program hashes are
`03e406a5672ada3e1762011d667c79ec04a55d7d1163a9423d0005720234d2ca`
(forward) and
`a4ff7b7ca8f23c858f8e6f1044bc6abf92168ab17abd2aa420ad384f58a519d3`
(backward), under the same sorted-key compact JSON convention.

Write V = F_2^n x F_2^n with its usual symplectic form and let Z = 0 x F_2^n.
For a physical frame F, use the **inverse-image** chart L(F)=F^-1(Z), an
n-dimensional Lagrangian. A paid physical transition is F_next F_prev^-1;
its Fourier rank is

    d(L(F_prev),L(F_next))=n-dim(L(F_prev) intersect L(F_next)).

Forward images F(Z) cannot be substituted for these inverse images for a
general frame. This convention and the exact symmetric-phase chart grammar
are documented in `research/native-quotient-interface/PHASE-FORM-GRAMMAR.md`;
the canonical specialization is in
`research/complex-frame-distance-seed80/PROOF.md`. Let k(L)=dim pi_x(L).
Signs, affine
translations and overall phases do not change this rank; granting them
freely only enlarges the geometric relaxation. No physical compiler or
endpoint phase admission follows from a rank obstruction.

## Projection lower bound and rigid zero entrances

Rank-nullity gives dim(L intersect Z)=n-k(L), hence d(L,Z)=k(L). The
Grassmann/subspace distance d on equal-dimensional subspaces is a metric.
Its reverse triangle inequality therefore gives

    d(L,M) >= |d(L,Z)-d(M,Z)| = |k(L)-k(M)|.

For completeness, triangle inequality follows from
dim(L intersect N) >= dim(L intersect M)+dim(M intersect N)-n: the two
intersections are subspaces of the n-dimensional M, and their intersection
lies inside L intersect N. This proves the needed metric statement without
any isotropy assumption beyond the common dimension.

This metric is standard: Koetter and Kschischang, *Coding for Errors and
Erasures in Random Network Coding*, section 3.1, Lemma 1, proves the subspace
metric dim(A)+dim(B)-2dim(A intersect B). On equal n-dimensional spaces the
distance used here is half that metric. The source-specific path accounting,
not the metric identity, is the new application:
<https://arxiv.org/pdf/cs/0703061> (v2, 25 March 2008).

If k(L)=0, then L=Z. Consequently a helper with zero entrance projection has
rank k(M), regardless of its exit's quadratic form or projection direction.

The original paid edges are nested canonical charts, so their original ranks
r are the nonnegative differences of the source frame dimensions. Arbitrary
new Lagrangians with the same per-node projection dimensions have paid ranks
r+delta with delta>=0. In contrast to the canonical theorem, delta need not
be even. Every original native rank is zero, so arbitrary changes of native
maps cannot decrease their cost. Owned costs are held fixed.

## Incremental concavity pays each helper credit

Let H be any nondecreasing concave function on all nonnegative reals, with H(0)=0.
For r_i,delta_i>=0 put R=sum r_i and D=sum delta_i. Diminishing increments
of a concave function imply, with s_i=sum_{j<i}delta_j,

    H(r_i+delta_i)-H(r_i)
      >= H(R+s_i+delta_i)-H(R+s_i),

because r_i<=R+s_i. Summing telescopes and proves

    sum_i [H(r_i+delta_i)-H(r_i)] >= H(R+D)-H(R).

For a paid-only source-geodesic helper wire, R equals its original residual
rank. The metric triangle inequality bounds its new residual q by R+D.
Monotonicity of H then shows that the increase in the wire's paid tariffs is
at least H(q)-H(R), its entire additional helper credit. This remains true
if q<R, in which case the helper supplies less credit. No parity assertion
or strict positive margin is needed for this stronger non-improvement claim.

## Source-bound application

There are 358 zero-entrance helpers, whose ranks are rigid under fixed
projection dimensions. All other 50 helpers have paid-only actual wires,
no native operation, and source paid rank sum equal to their source residual.
The 50 paths are disjoint in charged edge occurrences even if scalar-contact
vertices are shared. Apply the preceding inequality separately on these
paths; every remaining paid or native tariff is nondecreasing, and owned
center costs are fixed. Therefore the entire paid-minus-helper invoice
cannot decrease.

This argument applies separately to forward and backward words and even
allows independently chosen charts and native maps in the two orientations.
It applies to H(r)=r^(1-C) for 0<C<1, and by the same argument at C=0. It is a
statement about the whole geometric invoice, not a new supplier or improved
bound. It does not exclude changing per-node projection dimensions, owned
center costs, scalar/contact incidences, helper roles, or the supplier model.


## Predecessors and distinction

Matarener's [PR5060](https://github.com/CrocSwap/integer-mult-bounds/pull/5060)
established an owned-center path floor under nested-chart constraints.
zxv's [PR5283](https://github.com/CrocSwap/integer-mult-bounds/pull/5283)
extends the intersection-loss argument to arbitrary Clifford intermediate
charts and typed-copy trees under fixed common-contact constraints. Those
path-floor ideas and their native/Clifford predecessors deserve credit.
The present result binds a different whole-invoice accounting argument to
the round-three word: 50 disjoint paid-only helper paths fund all possible
helper-credit changes at fixed projection heights, including quadratic
chart changes, while the source's eight owned center charges remain fixed.
It does not re-prove or claim the geometric metric as new.
