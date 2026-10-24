# Fixed scalar codes and recursive interfaces

A code can reduce the number of native children even when every individual
port has a full input projection. Full coordinate projections do not exclude
that construction. The next theorem gives the actual restriction for a fixed
scalar code.

## A code closure criterion

Let `E` be a subspace of `C^W`, with orthogonal projection `P_E`. Let `V` be
a finite-dimensional complex vector space. For operators `A_i` on `V`, put
`D=diag(A_1,...,A_W)` on `C^W tensor V`. Form a graph on the `W` coordinates:
join distinct `i,j` when `(P_E)_(i,j)` is nonzero. Then

\[
D(E\otimes V)\subseteq E\otimes V
\]

holds if and only if `A_i=A_j` on each connected component of this graph.
The operators need not be invertible.

To prove necessity, choose a basis `B_alpha` of the span of the `A_i` and
write `A_i=sum_alpha c_(i,alpha) B_alpha`. Invariance and linear independence
of the `B_alpha` imply that each diagonal matrix
`diag(c_(i,alpha))` preserves `E`. A finite diagonal normal matrix has
orthogonal spectral projections that are polynomials in that matrix. These
projections preserve `E`, so the matrix also preserves its orthogonal
complement. It therefore commutes with `P_E`. Entry by entry,

\[
(c_{i,\alpha}-c_{j,\alpha})(P_E)_{ij}=0.
\]

Thus the operators agree along every graph edge and on each component.
For sufficiency, the same entrywise formula gives
`(P_E tensor I)D=D(P_E tensor I)`.

For `E=ker R`, the code projector is `I-R^T R/56`. The independent pinned
source check finds one connected component on all 112 ports. Thus a fixed
`ker R` code survives a block of independent native port operators only if
all 112 completed operators in that block agree. Equality of their ranks
does not suffice.

This statement concerns one fixed code at the stated block boundary. A
sequence can use different codes between its children. A circuit can also
compute a joint operator on several arrays. Neither possibility is excluded.

## A positive compression example and its limits

The code `(u,v,u+v)` has three full coordinate projections. For the common
operator `F`, compute `Fu` and `Fv`, then form their sum. This uses two
native calls for the three physical code coordinates. Its independent input
dimension is two arrays. That dimension, rather than three, enters a recursive
cost denominator.

The third coordinate in this example is a prescribed redundant value.
An arbitrary borrowed third array has independent old contents. Those contents
must be retained and restored; they cannot be overwritten at no cost. The
code `(u,u,v,v)` also shows why the theorem uses graph components: the first
pair may use one operator and the second pair another. The full space has
singleton components and permits arbitrary port operators.

For the current supplier, a useful code must therefore do more than remove
the centre syndrome. It must exploit relations among native children, give
the resulting exact joint map, and charge its independent input dimension,
preparation, adapters, arbitrary dirty state, and restoration. The existing
fixed-stock nullspace and equalizer bounds do not rule out such a new contract.

## Boundary encodings and completed children

The common-grid argument in the pinned `notes/stopped-product-complex.tex`
does permit one outer encoding. It scales the Gaussian-dyadic inputs and all
dirty auxiliaries by the same scalar power of 21. This scalar encoding
commutes with every linear operation. Each completed child is still exactly
the stipulated tensor `C` and adds no new odd denominator. Only unfinished
calls contribute to the grid height.

This argument does not itself defer line gauges. With per-role encodings
`T_i`, the logical addition `z_i += c z_j` requires the physical operator
`c T_i T_j^-1` between the two roles. A scalar add has that form only when
the two exact encodings agree. If their preimage frames agree, an actual
rank-zero adapter can reconcile them. Distinct norm-one source lines need
native rank 2 for the direct adapter under the retained frame convention.

There is a valid boundary freedom for the old exact local shear. Let `S`
be its logical map and let `D` be diagonal on roles. Give each helper the
same right gauge at input and output. Give the four endpoints of each
source/target pair the same right gauge. Then `DS=SD`, for both the forward
shear and its inverse transpose. If the physical endpoint frames are
`B_in,B_out`, the changed endpoint is exactly

\[
B_{out} D S D^{-1} B_{in}^{-1}
=B_{out} S B_{in}^{-1}.
\]

This holds on arbitrary data and helper inputs. It also holds for every
tensor power. Thus paired endpoint gauges can preserve the old local
contract and its global composition. The wire-gauge experiment uses this
freedom. It charges every relative native transition, including any rank-zero
adapter that becomes a rank-one child. A lower local graph objective alone
would still need exact phase lowering, native replay, and a complete finite
invoice before supplier admission.

If the two data roles receive unequal gauges, the cross term becomes
`D_y D_x^-1 x` and the old shear is lost. If a helper has unequal endpoint
gauges, its arbitrary old value is not restored. These are direct controls
on the boundary argument.

This note is campaign research. Its code-closure theorem has not yet received
an independent proof review. The source commit is
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The arguments build on the exact
preimage-frame and all-size contracts in the repository. This work used
OpenAI Codex assistance and makes no new supplier or kappa claim.
