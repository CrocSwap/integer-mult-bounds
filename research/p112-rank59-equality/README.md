# Classify all first nonadditive P112 rank-59 diagonal completions

This result classifies every first nonadditive rank-59 complex diagonal completion of the doubled P112 Gram matrix. It answers Open next question 1 of the cited boundary proof and the released [Discussion #5336](https://github.com/CrocSwap/integer-mult-bounds/discussions/5336). There are exactly 112 supports, in one orbit under the specified frame-preserving E8 symmetry group. Each support has a complete coefficient equation. This is an algebraic diagonal-mask result; the complete kappa calculation is unchanged.

**Model and retained premises.** Let X have the 112 doubled root-line representatives specified by the source, with squared row norm eight. Remove the eight lines 2e_(2j)+/-2e_(2j+1), j=0,1,2,3, from the 120 E8 root lines. Put G=XX^T. Corrections Delta are arbitrary complex diagonal matrices, with nonzero support S. All transposes are ordinary, not conjugate transposes. We retain the source's proved rank stratification and its explicitly inherited root-code distance and root-spanned-hyperplane premises. In particular, writing r=rank X_(S-complement), r=8 gives rank(G+Delta)=8+|S|; r=7 gives rank at least |S|+6 and |S|>=53; r<=6 gives rank at least62. The geometric premises are not independently accepted by this package.

**Complete equality class.** Every rank-59 completion is one of the following:

1. The additive case: |S|=51. Every nonzero choice of the 51 diagonal entries has rank59.
2. The nonadditive case: choose a live root line alpha in P112, set c=X alpha and S={i:c_i!=0}. Then |S|=53, and the nonzero complex coefficients must satisfy

       1 + sum_(i in S) c_i^2/(8 delta_i) = 0.             (1)

There are no other cases. Choose the doubled representative alpha so alpha^T alpha=8. If i_alpha is its own row, then c_(i_alpha)^2=64 and the other52 nonzero squares are16. Thus (1) is equivalently

       8/delta_(i_alpha) + 2 sum_(i in S, i!=i_alpha) 1/delta_i = -1. (2)

This gives a parameterization by nonzero complex t_i with sum t_i=-1: set delta_i=c_i^2/(8t_i). In particular it includes nonreal coefficients. The common value -112 is the predecessor witness, not a new witness claim. For the G/2 convention, divide every delta_i by two.

**Proof of support completeness.** The retained stratification forces r=7 and |S|=53 in the nonadditive case. Thus the 59 unchanged rows span a real root-spanned hyperplane. The inherited classification says that a root-spanned hyperplane with more than42 E8 root lines is E7, with63 lines and a root normal alpha. An excluded root normal is orthogonal to seven of the eight removed lines: six from the other three coordinate pairs and its partner in the same pair. A live two-coordinate root uses two distinct pairs and is orthogonal to the four removed lines on the other two pairs. A half-integral root in doubled coordinates has all coordinates +/-1; in each pair it is orthogonal to exactly one removed line, again four in total. Hence an excluded normal leaves56 live zero rows, whereas each live normal leaves59. Only the112 live normals give the required support.

Each of these59-row zero sets has rank seven. This follows from the source's rank-six bound42, or from the independent eight-column elimination in the checker. Distinct root normals therefore give distinct supports. No minimum-codeword support is omitted: every eligible59-row set equals all live root lines of its E7 hyperplane.

**Proof of the coefficient equation.** Pivot on seven independent unchanged rows. Projection off their real span leaves the line of alpha, so the Schur block on S is

       diag(delta_i) + c_S c_S^T/8.

The diagonal is invertible. A rank-one update of an invertible |S|-square matrix has nullity at most one. It has nullity one exactly when (1) holds, by direct multiplication of the candidate kernel vector diag(delta)^-1 c_S, or by the determinant lemma. Thus rank59 is equivalent to (1); otherwise the rank is60. This argument is valid for all nonzero complex coefficients and does not replace squares by absolute squares.

**The stated symmetry and its equivalence relation.** The group here consists of orthogonal E8 root-set symmetries that preserve the removed eight-line frame as a set. It is not an unspecified larger equivalence on matrices. Write the removed doubled roots as a_0,...,a_7 in pair order, plus then minus, and use coordinates y_j=(v dot a_j)/4. The removed roots become the lines of 2e_j. Each live root has four entries +/-1, and its support is an affine plane in F2^3 when j is labelled by its three binary digits. There are14 such planes and eight sign choices modulo overall sign on each plane, giving112 live lines. In the original coordinates the plane list consists of six unions of two coordinate pairs and eight choices of one coordinate from each pair with even parity. These are exactly the14 affine planes.

Every independent coordinate sign change preserves this root set. Every affine permutation j -> Aj+b, A in GL3(F2), also preserves it. Conversely a frame-preserving orthogonal map is a signed permutation, and its permutation must preserve these planes. After a translation fixes zero, preservation of {0,a,b,a+b} forces additivity; hence it is in GL3(F2). The group is therefore the signed permutation group 2^8 semidirect AGL3(2), of order344064. Its central overall sign acts trivially on root lines.

AGL3(2) is transitive on affine planes, and coordinate signs are transitive on the eight root lines on each plane. All112 normal lines and all112 supports are consequently in one orbit. To compare two coefficient choices, apply the induced permutation of live root lines to their supports and diagonal values. They are equivalent under this group exactly when one of these finitely many actions matches every coefficient. After fixing one normal alpha, take the quotient of (1) by its line stabilizer. This is a complete parameter space with an explicit finite equivalence test; no canonical ordering of arbitrary complex numbers or computation of an invariant ring is asserted. Row sign changes from the choice of root representatives leave diagonal values unchanged.

**Evidence and limits.** The checker independently generates all120 root normals, finds112 distinct equality supports and checks all their unchanged-row ranks. It verifies the affine-plane model, all1344 affine permutations and18816 plane actions, plus eight independent sign generators. Literal rational elimination of two112-row matrices distinguishes the predecessor nonadditive witness from an additive51-support rank59 completion. Six literal53-row Gaussian-rational Schur eliminations check three coefficient solutions, including a nonreal solution, and their three one-entry failures. These checks corroborate the written classification; they do not audit the inherited global root-flat premises. No physical decoder, diagonal repair bill, COPY optimum, odd-only-mask claim or supplier admission follows.

Credit Nick Petalas's [PR #5249](https://github.com/CrocSwap/integer-mult-bounds/pull/5249) supplies the exact model, rank stratification, rank-59 witness and equality question in its [pinned proof](https://github.com/CrocSwap/integer-mult-bounds/blob/1c8bf3f3dadd1f6fd14892630eb76e984a74738a/research/p112-diagonal-rank-boundary/README.md). It retains Arham-Tahir64's [PR #1313](https://github.com/CrocSwap/integer-mult-bounds/pull/1313) diagonal-mask question and pivot method, woklerx's [PR #1447](https://github.com/CrocSwap/integer-mult-bounds/pull/1447) code-distance premise, and themilkman216's [PR #968](https://github.com/CrocSwap/integer-mult-bounds/pull/968) root-flat classification. DreamingOfClouds and the retained E8/Hamming lineage keep their geometric credit. Rank-one determinant identities and the affine-plane model are classical. The new result is the complete first nonadditive coefficient/support class and its specified symmetry quotient.

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/p112-rank59-equality
```

Use Python 3.12 with the standard library. The normal and optimized commands must print `PASS_P112_RANK59_CLASSIFICATION`. The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The checker has no external runtime inputs.

## Open next questions

Test a specified diagonal-repair consumer and charge its full decoder bill before using this algebraic rank reduction. The source binding and physical cost model are not supplied by this package. See `TASK.json` for the structured scope.
