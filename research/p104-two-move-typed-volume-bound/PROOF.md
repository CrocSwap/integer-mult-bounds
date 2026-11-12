# One-field displacement bound for the exact chart-117 pair

Fix the two old public MOVE instructions at clocks 32944 and 32945 in #7334. Their exact records are `MOVE 625 3 117 false` and `MOVE 624 3 117 false`. The old frame is empty and the new frame vectors are `(8,17,34,68,391)` in the nine-axis field. The exact normalized signed compiler lowers the chart operation to rank five. The verifier writes the literal frame as P⁻¹ C^⊗5 P on its five active axes with four spectators, for a unitary monomial P. The signed Pauli and exact global phase agree with the compiled recipe. An independent Gaussian-integer evaluator matches every one of the 512 one-slice columns. Removing one C gate changes the result. The signed square sends the zero basis column to −i times basis 504, so the square is not scalar. Together with the exact fourth power I, this establishes projective order four.

For tensor width f, let N=2^(9f), T be the lifted one-lane chart, and A=diag(T,T) be the required map on the two original arbitrary lanes. The verified one-slice frame conjugation lifts by tensor product across the f independent slices. All estimates below allow arbitrary inputs in both lanes. The paid-rank tariff alone does not determine address volume.

## Identity erasure at every positive width

The normalized single-axis C has eigenvalues 1 and i. For five independent C axes, the counts of eigenvalue exponents modulo four are (6,6,10,10). Each extra active axis averages the previous cyclic distribution with a one-step translate, so the largest probability cannot increase. For all f≥1 the maximum one-field eigenspace dimension is therefore at most (5/16)N. Spectators multiply all multiplicities by the same factor. Thus rank(A−I)≥2N−2(5/16)N=11N/8.

Under identity erasure, removing the one body-dependent change leaves the identity on both original lanes. If the difference factors through one original N-dimensional field with fixed adapters, write it as B K D, where D maps the pair to the field and B maps back. Its rank is at most N even with unrestricted linear adapters. This is incompatible with 11N/8. The same eigenvalue bound is insensitive to a common global scalar on the target chart.

## Unitary monomial erasure with one normalized core

Each one-slice chart column has 32 nonzero entries, all with squared modulus 1/32. This was checked for all 512 columns in both evaluators. The lifted chart at f=4 has maximum entry modulus (1/√32)^4=1/1024. The same maximum applies to A.

Let M be any unitary monomial on the complete two-lane space, allowing coordinate permutations across lanes and arbitrary unit-modulus coefficients. Set W=M* A. Its trace selects at most 2N entries of A, each multiplied by a unit phase. Hence |tr W|≤2N/1024. If z is the dimension fixed by W, unitarity gives Re(tr W)≥z−(2N−z). It follows that z≤N(1+1/1024), and therefore rank(A−M)≥(1023/1024)N.

A proposed one-core map has the same pre/post unitary monomial adapters with and without the core. After removing the core, the adapters give a monomial M. The difference from M has the rank of the core minus identity on its one active N-dimensional lane. The other lane contributes zero. At f=4 a normalized rank-r core for r=1,…,6 has 4r independent C axes and the remaining spectators. The least fraction of any phase residue modulo four is at least 1/8, as checked by exact binomial counts in both engines. Thus its displacement rank is at most 7N/8. This bound also permits a fourth-root phase normalization of the core, which only changes the residue fixed by identity. The strict dimension gap is (127/1024)N, or 8,522,825,728 at f=4. A rank-1-to-6 core cannot realize the target.

Within the same tensor-lift model, the last inequality also holds for every f≥4 by an algebraic bound. The target entry maximum cannot exceed 1/1024 once f≥4. The minimum of the four residue probabilities is 1/8 at four active axes and cannot decrease under the same averaging for any further axes. The direct numerical width check in this package is f=4.

## Directed price and scope

Let H(r)=r^(1−κ) at the pinned comparator crossing. An optimistic retirement of both old rank-five paid children in favor of one rank-six child on each of 17 invocations gives `17(2H(5)−H(6))`. Directed rational evaluation places it between 67.66946959214 and 67.66946959215 raw. The frozen receipt carries both exact endpoints. This is a gross price before extra sources, routing, restoration or physical checks. The normalized rank exclusions stop this model before a literal build.

The identity result assumes a change that factors through one original field. The monomial result assumes one original field with one normalized core and unitary monomial erasure on the pair. A larger active field, additional body-dependent bypasses, nonmonomial erasure or changed comparator premises need separate analysis and a full price. No arbitrary-input native replacement, all-size complexity change, or κ increase is established.
