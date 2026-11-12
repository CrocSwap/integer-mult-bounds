# Phase defect of a paired QUERY host

Use column-vector chronology on the same 36-dimensional Type A port. At body one and $q=\sigma\in\{+1,-1\}$, write the desired endpoint as $E_\sigma$, and the invertible prefix and suffix of the modified caller around the host as $B_{\mathrm{in},\sigma}$ and $B_{\mathrm{out},\sigma}$. The sole possible host is

$$
J_\sigma=B_{\mathrm{out},\sigma}^{-1}E_\sigma B_{\mathrm{in},\sigma}^{-1}.
$$

The modified QUERYs agree with the original at $q=+1$, so the required $J_+$ equals the original host there. The literal replay solves the displayed equation on the smallest interval containing both QUERYs and the host, cancelling the common prefix and suffix outside it. It reduces the coefficients modulo the prime 65521 after checking denominators and inverse factors. For every one of the 102 choices, a nonzero 3×3 minor of $J_--J_+$ certifies a rational rank lower bound of three. The relative defect $J_+^{-1}J_--I$ has the same rank.

A canonical Type A J at body one applies two disjoint signed shears. Its phase difference has rank two. With the same phase-even linear wrappers at both signs, $J_\sigma=L K_\sigma R+C$, so $J_--J_+=L(K_--K_+)R$ has rank at most two. This capacity argument also holds for rectangular adapters or a phase-even additive feedthrough whose contracted map satisfies the displayed factorization.

## Exact lower bound of four

Use the endpoint and relative defect lemma of [#7309](https://github.com/CrocSwap/integer-mult-bounds/pull/7309), with $E_+=I$, $E_-=-I$. For the chronological phase-specialized factors $A_i^\sigma$, the relative endpoint $E_+^{-1}E_-=-I$ is the chronological product of the local relative factors $D_i=(A_i^+)^{-1}A_i^-$, each conjugated by its phase-plus prefix. This follows by induction on the prefixes. Phase-even invertible mixers have identity local relative factors.

Write the conjugated factors as $G_i$, and put $U_i=\operatorname{im}(G_i-I)$, $S_i=\sum_{j\ne i}U_j$. Telescoping the product minus identity gives $U_i+S_i=V$, since the product minus identity is $-2I$. The centrality of $-I$ allows a cyclic shift applying $G_i$ first. For $x\in U_i$, all later factors change $G_ix$ by vectors in $S_i$, and the final result is $-x$. Consequently $(G_i+I)x$ lies in $U_i\cap S_i$. In characteristic zero this gives

$$
\operatorname{rank}((G_i+I)|_{U_i})
 \ \le\ \dim U_i+\dim S_i-36
 \ \le\ \sum_j\operatorname{rank}(G_j-I)-36.
$$

Pick any of the 16 unchanged J factors. Its local $D_i=I-2N_i$, where $N_i$ has rank two and $N_i^2=0$. Thus $D_i$ is identity on its two-dimensional defect image and the restriction of $D_i+I$ has rank two. The total local defect rank must be at least 38. The 16 unchanged J factors contribute 32, and the two unchanged QUERYs contribute two. Every new phase-even mixer contributes zero. The remaining host must therefore have relative phase-defect rank at least $38-34=4$, independent of the particular pair and host clock.

The rank-four floor uses the exact $\pm I$ endpoint and at least one unchanged J with the given defect-image action. It permits additional invertible phase-even mixing on the original port while keeping the other phase-odd factors fixed. Enlarged endpoint spaces, cross-port action, shared phase-odd state, several changed hosts and new phase-odd suppliers are outside the claimed family.
