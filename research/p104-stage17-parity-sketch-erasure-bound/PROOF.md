# Five linear parities leave an exact capacity gap

The #7416 predecessor fixes the exact two stage-17 returns at clocks 4646 and 4660 in #7113. The intervening 13 ordinary operations have an invertible scalar matrix. The corresponding rank-one lane projectors are complementary, so the old normalized operator on their common range is the scalar `D` on both independent dirty lanes. The independent replay reconstructs the two-lane projector by applying the actual scalar interval and inverse on all four basis columns. The stage body acts as `C^(8f)`, with binary C eigenvalues 1 and i on the plus and minus Walsh characters. Set `f=2`, `m=16`, `N=2^m`, and work in the fixed common Walsh addresses. The target at address x is `i^w I₂`, where w is the Hamming weight of x.

## Occupancy of a parity cell

The two bits of w modulo four are `p(x)=w mod 2` and `Q(x)=binom(w,2) mod 2`. The polar form of Q is `B(x,y)=p(x)p(y)+x·y`, with alternating matrix `I+J` over GF(2), where J is the all-ones matrix. Since m is even, J²=0 and `(I+J)²=I`. The form is nondegenerate.

At most five linear probes give cells that are affine cosets `v+W`, where W has codimension k≤5. Nondegeneracy gives `dim W⊥=k`. The restriction radical `W∩W⊥` has dimension at most k, so the restriction rank is at least `m−2k≥6`. The squared quadratic-character mean on a cell is a sum over differences h∈W. For each h, averaging the polar character `(-1)^B(x,h)` over x∈W gives zero unless h is in the restriction radical. The remaining terms have magnitude one. The squared mean is therefore at most `2^(-rank(B|W))≤1/64`. Thus the absolute bias is at most 1/8 and each value of Q has occupancy at most 9/16. Every phase of `i^w` specifies a value of Q, so every phase has occupancy at most 9/16 in each cell.

The one explicit control uses total parity plus the parities of four disjoint pairs on the first eight bits. Its restriction rank is six. Independent direct counting covers all 32 cells and all 65,536 addresses and attains phase occupancy 9/16 in cell 30. That single sketch would in fact require residual rank 65,280 after its optimal erased matrix choices. The universal bound uses the worst possible phase occupancy in every cell.

## Erased matrix and normalized core

Let E be any complex 2×2 erased matrix for a cell, without an invertibility or normality requirement. The eigenspaces at the four distinct target phases have dimensions whose sum is at most two. The cell's matched dimension is the phase-count weighted sum of those eigenspace dimensions. The maximum occupancy bound puts it at most `2(9/16)` times the number of addresses in the cell. Summing over cells, the old target minus erasure has rank at least `2N−(9/8)N=7N/8`.

Grant arbitrary fixed linear routes around the one changed normalized core. Write the actual map as `B₀+F C_core E₀` and its erased version as `B₀+F E₀`. Their difference is `F(C_core−I)E₀`, with rank at most the core's displacement. A normalized rank-16 core at f=2 has 32 independent binary C factors. The exact mod-four binomial count gives an eigenvalue-one fraction `32769/131072>1/4`, so the displacement capacity on t old lane volumes is at most `3tN/4`. Consequently `t≥7/6` is necessary. A rank-zero core has no displacement.

## Directed price and scope

The inherited conditional tariff removes `16H(8)` and adds `8tH(16)` over eight ports, where `H(r)=r^(1−κ)`. The directed lead replay uses the incumbent crossing interval to bound the funded volume above by approximately 1.0025308637644, strictly below 1.003. With t≥7/6, the resulting optimistic gross upper is below −20.798 raw before all ancillary charges. See the exact rational result in `receipts/R215-LEAD.json`.

This excludes only the stated width-two fixed-fibre family with at most five linear parity probes, one normalized rank-16 core and the inherited volume tariff. The erased matrices can mix both lanes within each cell. Mixed Walsh addresses, more probes, nonlinear dependence, a changed core or a different tariff need their own proof. No native supplier was built.
