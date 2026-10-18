# Nested prefix promotion and supplier substitution

## Exact prefix transformation
Let the commuting correction prefix consist of gates D_d <- D_d + a_dp P_p, with donor and pivot register sets disjoint. Give each pivot p an entrance frame F_p containing its old entrance E_p. Require F_p to lie in the first downstream frame of p and of every donor with a_dp != 0. For each donor, require the frames of its incoming gates to form a containment chain above its previous frame. Order these gates by that chain (a global increasing-dimension order works when all the requirements hold), and regenerate literal background cleanup.

The scalar prefix is unchanged: the product is I+sum a_dp e_d e_p^T because every cross product vanishes. Hence its entire arbitrary-dirt transfer is unchanged, not merely its clean response. The only changed paid edges are the actually reconstructed donor and pivot frame chains. Exact phase/normalization and physical owner compatibility still require the ordinary finite pipeline. This is a sufficient compiler transformation, not an assertion that every promotion is profitable.

## Complete bounded census on epoch14
The frozen input is recorded in NESTED-PIVOT-CENSUS.json. For each of 56 pivots we intersected its first downstream frame with the first frames of all donors that it writes. We enumerated every extension of its original rank-four entrance within that intersection. Twelve four-pivot groups each have exactly one rank-five extension per pivot; two groups have none. There is no rank-six option. Because each available quotient has dimension at most one, this enumeration is complete for this fixed prefix and downstream word. All 194 legal group assignments were enumerated; no claim extends this census to changed donor bases or changed downstream gates.

For j=0,1,2,3,4 promotions within an eligible group the local histogram changes are respectively
  0;
  7[r1]-4[r2];
  10[r1]-6[r2];
  10[r1]-7[r2]-[r3]+[r4];
  8[r1]-8[r2]-4[r3]+4[r4].
Each promotion changes one width-five helper to width four. These signatures are identical in all twelve eligible groups.

At any paid exponent 0<p<1, every partial group has strictly larger moment than the mixture j/4 of the fully promoted group and 1-j/4 of the original group, at the same mean width inventory. To prove this, subtract that mixture. For j=1, the positive ranks are (3,1,1,1,1,1), the negative ranks are (4,2,2,0,0,0). For j=2 they are (3,3,1,1,1,1,1,1) and (4,4,2,2,0,0,0,0). For j=3 they are (3,3,1,1,1,1) and (4,4,2,0,0,0). In every case the negative list majorizes the positive list, with equal total rank. Strict concavity of x^p proves the claim. This supports whole-group mixtures in the fractional stock problem; it does not replace an actual timed integer owner construction.

## Complete-call mixture theorem
Take any sequence of full normalized supplier calls, selected from a finite registry. Suppose all variants implement the same required data transformation in each orientation. Each selected variant must independently satisfy the arbitrary-dirt local identity and have its exact phase recipes, entrance normalization, output adapters, and scalar ledger bound to its immutable source.

A helper endpoint on a borrowed owner is the prescribed residual C_[w] on its selected subspace, tensor identity on the restored spectator coordinates; it is not the identity on the whole owner. For each call require distinct whole owners for distinct roles, actual per-role width and chart matching that selected variant, and every borrowed owner idle for the complete call. Across calls require an exact disjoint decomposition of each owner's pending coordinate axes into the hosted residual subspaces and its explicitly executed remainder. Require all private work erased at the end of every complete call.

Under these conditions the registry may vary call by call. Each call's arbitrary-dirt identity applies to the actual state left by previous calls. Its data endpoint is the required data gate. Every spectator is restored, while the selected residual acts only on the admitted pending subspace. Owner-wise these disjoint factors commute and multiply with the explicit remainder to the original pending operator. Induction in actual execution order therefore proves the full global data and owner endpoint. The proof applies separately to both required orientations. If the inverse program of the total composition is needed, call order reverses as well as local inversion; one may not simply invert each call in the same order.

The paid profile is the sum of actual selected local profiles plus actual owner remainders. Row and prefix invoices must bound both variants, every invocation, every bridge, and all routing/normalization primitives. No gains are added numerically. The ordinary exact moment and outer assembly compute the resulting kappa.

## Source connections, novelty and scope
We read OAI.InformationTheory.AmplitudeDamping.BlockFactors.blockProjection_range and blockInjection_isometry: a proved projection-range condition gives an actual reconstructing injection, and the injection has an exact left adjoint inverse. This motivates demanding full owner charts and spectator identities rather than matching dimensions alone. We also read OAI.Topology.CoarseAssembly.ProjectionBlocks.blockOperator_adjoint and flattenOperator_eq_conjugation: blockwise adjoints and explicit flattening preserve actual operators. Their finite-dimensional specialization motivates the independent orientation and disjoint-copy bookkeeping above. These statements are structural analogues; the present circuit lemma is proved explicitly here and does not import these Lean files as a formal certificate.

OAI.Algebra.Determinantal.RankTransfer.exists_matrix_right_inverse was also examined. Its surjectivity hypothesis supplies an actual right-inverse matrix, but no new such coordinate transformation with a profitable paid bill was found. We do not count it as an achieved numerical technique. Likewise, this lane's complete promotion census found no improvement beyond whole-group mixtures; the positive mixture is the resource lane's construction, extending PR558 and the prior finite-copy pooling work.
