# Proof of the scoped paid ceiling

Let `d_r` be a complete candidate paid-histogram change, including every
incident old-field edge and all center work, with the helper invoice fixed.
Zero-rank events have no recursive charge. For `1<=j<=9` define

    S_j(d) = sum_{r=1}^9 d_r min(r,j).

For `0<theta<1`, put `q_j=j^theta-(j-1)^theta`. These numbers are positive
and strictly decreasing. Finite summation by parts gives

    sum_r d_r r^theta
      = sum_{j=1}^8 S_j(d)(q_j-q_{j+1}) + S_9(d)q_9.

Thus componentwise nonnegative S_j certify a nonnegative paid change for every
such theta. S_1>=1 makes the change at least `q_1-q_2=2-2^theta>0`.
This is an elementary identity for this finite invoice, not an assumption
about asymptotic supplier composition.

## Complete local neighborhoods

The pinned #4841 single-neighbor theorem gives exactly 1,022 distinct changed
Lagrangians from each nine-dimensional chart. Its paired theorem gives
`2^(n+r+1)-2^(2r)-1` representatives for two charts at distance r. In this
new graph the 264 internal edges have distances zero (256 edges) and eight
(eight edges). The complete pair count is therefore

    256*1022 + 8*196607 = 1834488.

The source graph's every actual incident rank is recomputed by binary row
elimination after each move. A pair applies the same transported transvection
to both endpoints, which preserves the shared edge rank, but every other edge
is also recomputed. Independent axes are a different, unsearched grammar.

The resulting 18 single and 46 pair classes all satisfy

    S_j(d) >= S_j(d*) for every j,
    d* = {1:+1,7:+1,8:-1}.

The actual classes include d*. Consequently the exact minimum over each
nontrivial tested family is `1+7^theta-8^theta`. Strict subadditivity of
`x^theta` proves this is positive. The identity chart/no change is excluded
from a nontrivial-neighbor family and of course has zero change.

## Arbitrary coherent blocks

Fix one original chart L, its alternative L'=T_a L at distance one, and any
subset of the variable contacts with original chart L. Retag precisely that
subset to L'. All other contacts remain fixed. Every internal edge is the
identity map with original rank zero. Its new rank is zero when the two labels
agree and one when they differ. This holds also for noncontiguous subsets and
for edges between contacts of different retained centers. Every external edge
contributes a unary cost determined by its full actual mapped rank.

For tariff `h_j(r)=min(r,j)`, the complete changed invoice therefore has form

    S_j = sum_v unary_j(v) x_v + sum_{uv internal} |x_u-x_v|.

The coefficients are integers. This is exactly an s-t cut energy. Positive
unaries use vertex-to-sink edges; negative unaries use source-to-vertex edges
and add their value to the constant offset; internal edges have unit capacity
in each direction. No mixed-original-chart or mixed-alternative submodularity
is assumed.

The only group of size greater than one has 176 original empty-chart contacts.
The exact replay checks all 1,022 distinct alternatives and all nine tariffs.
Every flow has nonnegative capacities, satisfies conservation and has a value
equal to an independently recounted attaining cut capacity. Including the
negative-unary offset gives zero in every case. Feasible flow and equal cut
capacity prove optimality; the empty subset directly attains zero.

For every first-prefix problem, all variable vertices can reach the sink in
the residual graph. Any minimum cut has no positive residual edge leaving its
source side. A variable vertex placed on that side would therefore force the
sink onto the same side, a contradiction. The unique minimum is the empty
subset, so every nonempty subset has integer S_1>=1. Since its other S_j are
nonnegative, the summation identity proves loss at least `2-2^theta`.

The other eight original-chart groups are singletons, already covered by the
complete single-neighbor classes. No extra independent center output is
rewarded in any equation. None of these graph arguments asserts a complete
native phase, caller, compiler or outer-multiplication theorem.
