# Minimum native Gaussian rank for a partial Pauli contract

For a compatible signed partial Pauli map, this result gives the least native Gaussian rank over every symplectic completion. It answers the released [Discussion #5334](https://github.com/CrocSwap/integer-mult-bounds/discussions/5334). Compatibility and minimum quarter-turn length are different questions. The complete kappa calculation is unchanged.

**The minimum.** Let V be a 2n-dimensional binary symplectic space. Let Z be the fixed computational Lagrangian. Let h:U -> U' be an injective partial symplectic isometry. Put A=U intersect Z, B=h(A), c=dim(B intersect Z), and t=dim(U' intersect Z intersect B-perp). Then

    min_g [dim(Z+gZ)-n] = dim(B) + t - 2c,

where g ranges over all symplectic extensions of h. The minimum is attained. It does not depend on the compatible Pauli signs. The proof below constructs an attaining extension with linear algebra over F2. This is an offline construction; no physical preparation cost is assigned to it.

**Transverse extension lemma.** In a symplectic space of dimension 2m, a subspace W has a disjoint Lagrangian if and only if dim W <= m. Necessity is the dimension inequality. For sufficiency, take a symplectic basis with W spanned by e_i,f_i for i<=r and e_(r+j) for j<=s. Thus dim W=2r+s<=m. Use r unused symplectic pairs indexed r+s+i. The vectors e_i+e_(r+s+i), f_i+f_(r+s+i), f_(r+j), and one e-vector for each remaining pair span a disjoint Lagrangian. Their pairings vanish in F2. Their components outside W prove disjointness. Symplectic elimination constructs this basis.

Fix a Lagrangian R and a subspace W with dim W=w<=m. Write D=R intersect W and r0=dim D. Among Lagrangians L disjoint from W, the largest dim(L intersect R) is m-r0. The dimension bound follows because L intersect R is disjoint from D. For attainment, set N=R intersect W-perp, so dim N=m-w+r0>=r0. Choose a linear projection pi:R -> D that is the identity on D and is onto D on N. To construct it, extend a basis of D intersect N separately to D and N; send enough of the added N vectors to the remaining D basis vectors and extend to R. Set K=ker pi. Then dim K=m-r0, K intersect W=0, and K+N=R. The pairing K x W has rank w-r0. In K-perp/K, the image of W intersect K-perp has dimension r0, half the ambient dimension. Apply the transverse extension lemma there and pull its Lagrangian back. The resulting L contains K and is disjoint from W. This proves attainment without an enumeration assumption.

**Application to the partial map.** Set b=dim B. A completion L=gZ must contain B and satisfy L intersect U'=B. Conversely these two conditions suffice. The pairing maps from Z to U-star and from L to U'-star have images equal to the annihilators of A and B. Their restrictions on A and B agree through h. Choose adapted bases for their kernels and images to extend h on A to an isomorphism Z -> L that preserves all pairings with U. Together with h this defines an isometry U+Z -> U'+L. Symplectic basis extension then extends it to V. This also gives an explicit construction.

Pass to B-perp/B, of dimension 2m with m=n-b. Define

    W=(U' intersect B-perp)/B,
    R=((Z intersect B-perp)+B)/B.

R is Lagrangian. An admissible L/B is precisely a Lagrangian disjoint from W. In particular dim W<=m: alternatively, transfer W through h to (U intersect A-perp)/A and project into V/Z; its image lies in the (n-b)-dimensional annihilator of A. Moreover dim(R intersect W)=t-c, and dim(L intersect Z)=c+dim((L/B) intersect R). The preceding lemma gives maximum intersection c+(n-b)-(t-c), and hence the stated minimum. These quotient constructions also prove that the chosen L meets U' only in B.

**Signed dyadic lift and phase boundary.** Complete the unsigned map as above. The fixed-prefix transvection construction in the cited source emits a literal dyadic quarter-turn word for that full symplectic map. For each prescribed Pauli generator, its sign discrepancy is a binary linear functional on U'. Compatibility of dependent signed relations is required. Nondegeneracy of the ambient symplectic form extends this functional to pairing with a Pauli correction. Append that Pauli; it fixes all requested signs and does not change gZ or the rank. Each turn uses the source convention (I-iP)/(1-i), with positive Hermitian P. The literal word chooses its absolute scalar phase. No equality to an externally supplied scalar is implied. A specified target operator requires one exact amplitude check in addition to its signed tableau. Apply the cited native compiler to this word: its one grouped rank-d Gaussian and monomial factors have the attained rank. Their preparation and scan costs remain charged obligations.

**Exact evidence.** The standalone checker enumerates all symplectic completions and all subspaces for n=0,1,2. It groups completions by their exact partial map and compares all 10,113 minimum values with the formula. It also constructs 386 signed lifts and checks 848 literal Gaussian-rational matrix-column identities. Five controls include an inconsistent dependent Pauli sign, an absolute scalar mismatch, and the one-qubit Z-to-X, X-to-X and X-to-Z cases. The executable census is finite corroboration of the dimension-uniform constructive proof; it is not a polynomial-time implementation of the quotient construction.

Credit JoyboyBrian's [PR #5051](https://github.com/CrocSwap/integer-mult-bounds/pull/5051) supplies the signed partial-map contract, compatibility test, fixed-prefix extension and turn convention in [pauli.py](https://github.com/CrocSwap/integer-mult-bounds/blob/0960807a68ff46acbe6510c8867912ef2324ee71/research/signed-pauli-partial-extension/pauli.py). David Ganz/Dugongue's [PR #4841](https://github.com/CrocSwap/integer-mult-bounds/pull/4841) supplies the native Gaussian rank, monomial-factor bill and absolute-phase contract in the [compiler proof](https://github.com/CrocSwap/integer-mult-bounds/blob/6debdcdac8fe1c87958f8cd42ccb7db73c0a0eef/research/native-clifford-gauge-compiler/compiler/CLIFFORD-COMPILER.md). Nick Petalas's partial-transvection work is a separate tariff predecessor, as recorded in the released handoff. Symplectic basis extension and the Clifford/Bruhat methods are classical; this result addresses minimization over the prescribed extension fiber. The checker adapts the credited source's literal turn conventions and extension steps, and independently enumerates the full small completion fibers.

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/partial-pauli-gaussian-minimum
```

Use Python 3.12 with the standard library. The normal and optimized commands must print `PASS_PARTIAL_PAULI_GAUSSIAN_MINIMUM`. The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The checker has no external runtime inputs.

## Open next questions

Implement the quotient construction on one actual contact constraint set, retain its literal phase and charge all monomial passes. The source binding and physical cost model are not supplied by this package. See `TASK.json` for the structured scope.
