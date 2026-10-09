# Pair-star exclusion trees and the retained complex contract

The scalar and physical framework is icekylinx's PR104; Rohan Arun's PR107
contributes the order-only comparison. The new finite change replaces each
pair-star prefix/suffix exclusion construction by a binary exclusion tree.
The selected leaves retain the forward aligned pair order. Each internal
split uses the largest power of two strictly smaller than its leaf count.

## Exact scalar coverage

Fix a pair {a,b}. Its leaves are the distinct triples {a,b,i}, with i outside
the pair. Every subtree is the sum of exactly its leaves. The downward
traversal carries the sum of leaves outside the current subtree. Passing to
one child adds the other child's subtree sum; the summands are disjoint.
At leaf i the carried value is exactly the pair-star sum excluding i.
Thus the replacement changes the addition DAG while preserving every named
partial output and the pair total. It introduces no cancellation, division,
or new center coefficient.

Every pair-tree frame is the span over F2 of its supported triple indicators.
Each indicator has self-dot one, and two distinct indicators in a fixed
pair-star have dot zero. These indicators are an orthonormal basis; all
subtree/outside sums therefore have nondegenerate frames. Disjoint additions
produce containing frames. Other ordinary coordinate-cover frames, the 24
retained disjoint centers, and their output orthogonality are checked from
the actual serialized graph.

The centers remain `A_i=sum_{S avoiding i} x_S`. Therefore
`sum_i A_i=21*sum_S x_S`, and the same rational center scatter applies.
For a source and target intersecting in j points, twice the complete scalar
coefficient is `(j-1)+[j=0]-[j=2]`, equal to two only at j=3. The independent
raw-file audit verifies all 2024^2 coefficients, not only sample pairs.

## Physical carriers and dirty values

A selected donor passes an unchanged operand to a later use. The audit
checks distinct donors and use IDs, the actual preserved operand, physical
rank/time order, and inclusion of the donor's actual F2 subspace in the
recipient's actual subspace. Each such match replaces a retired tail and a
fresh copied operand with one continued path. Every removed and added rank
charge is reconstructed; the resulting 45,266 roles and complete matched
histogram agree with the literal matcher output. Matching edges are not
inferred from the final role count.

The resulting middle word is an invertible sequence of scalar additions.
Writing its role map as L, its source injection as V and its complete signed
readout as J, the audited identity is JLV=I. Subtracting the readout of the
old arbitrary role values and adding the readout after injection yields
`JL(z+Vx)-JLz=x`; inverse additions restore z. This argument requires the
complete signed readout and all restored roles, not an ordinary-input-only
simulation. Exact common frames and the retained two-stage construction
transfer that scalar identity to the physical address operators.

The changed tree leaves the inherited signed endpoint correction, inverse
rank-one child, both tensor connectors, copied-center transforms, divisor21,
and completed complex tensor contract in place. All new internal edges are
actual nested nondegenerate binary residuals handled by the retained complex
normal form. The paid child profile and the scalar/precision/three-stock
bridge must be regenerated from the new graph. No exponent improvement is
claimed from the smaller addition count alone.

`physical_check.py` independently parses graph.bin, graph.labels and
matches.bin. It imports no producer or matching implementation. It checks
all scalar supports, all binary frame Gram ranks and inclusions, all signed
transfer coefficients, every matching witness, and both the unlinked and
matched rank ledgers. The literal program check, inherited signed endpoint proof, complete
recursive moments and three-factor assembly are separate parts of the
selected verification and proof described in PROOF.md.
