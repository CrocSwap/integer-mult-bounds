# Clean helpers in the two-support flag case

This contribution was produced by Nick Petalas. The argument is a scoped written proof, not a formal proof-kernel result.

## Statement

Use PR6338's scalar-idempotent model. Fix `m >= 1`, `t >= 1` and `r >= 0`, and put `n=t+r`. Work in the group algebra `F_2[M_m(Q)]` of the additive group of rational matrices. A paid call is `I_n + ([A]-1)xy^T`, where `rank_Q(A)=1` and `y^T x=1` over `F_2`. The target is `diag([C_1],..., [C_t],1,...,1)` with `C_i` invertible. The last `r` registers are clean and return to identity. A word is an exact formal group-algebra identity; there are no interposed address maps.

Suppose the rational span of the paid `A` has dimension at most `m+1`, and the relative matrices `C_1^{-1}C_i` have a common complete rational invariant flag. Then the word has at least `mt` paid calls. In particular this applies to lower-triangular invertible data targets. The hypothesis is invariant under common invertible left and right address changes. For diagonal targets the direct coordinate word attains `mt` within span `m`, so the bound is sharp for the class. It does not claim that a direct word for every prescribed set of targets has span at most `m+1`.

## Two-dimensional lemma with zero helper blocks

Suppose all data target exponents in a two-dimensional block are invertible lower-triangular matrices, and all helper exponents in that block are zero. Let `U` denote calls whose frame has nonzero upper-right entry. Project every frame to that entry. The target becomes identity, including the helper entries. Write the associated scalar columns and rows as `X,Y`, with ranks `r_X,r_Y` over `F_2`. PR468's product factorization gives

    r_X + r_Y <= U.                                      (1)

For `i=1,2`, let `l_i` count the other calls whose `i`th diagonal entry is nonzero. Project onto that diagonal entry. Its target-minus-identity has rank exactly `t` over the fraction field of the Laurent group algebra: the data diagonal entries are nonzero and the helpers are zero. The factorization bounds its rank by both scalar spans. The upper calls span at most `r_X` columns and `r_Y` rows; the other relevant calls contribute at most `l_i` each. Therefore

    t <= r_X + l_i,       t <= r_Y + l_i.                (2)

A rank-one lower-triangular two-by-two frame has at most one nonzero diagonal entry. Thus `l_1+l_2 <= E-U`, where `E` is the number of calls assigned to this block. Adding (2) for both coordinates and using (1) gives

    4t <= 2(r_X+r_Y+l_1+l_2) <= 2E,

so `E >= 2t`. This is the new zero-helper adaptation of PR468's flag count. It does not assume that a clean helper's zero block is invertible.

## Apply the lemma

PR6338 proves the claimed lower bound for span at most `m`, and for span `m+1` with normalized support intersection `|K| != 2`. We cite those cases rather than re-prove them. For the remaining case, use the normalization in PR468 and PR5988: the span is block upper triangular after a common row and column permutation, with one two-dimensional diagonal block and `m-2` one-dimensional blocks. A rank-one frame has at most one nonzero diagonal block, so each call can be assigned to at most one block. This is an address-space fact, independent of the number of registers.

All data target diagonal blocks are invertible, while all clean helper blocks are zero. The common flag of the relative data targets passes to each invariant subquotient of the block filtration: intersect the common flag with each invariant subspace and pass to the quotient. It follows that common invertible left and right changes within the two-dimensional block make all data target blocks lower triangular. Those changes preserve rank, the formal identity, and zero helper blocks. The lemma above gives at least `2t` calls in that block. Each one-dimensional block needs at least `t` by its diagonal projection and scalar rank. The disjoint assignments sum to `2t + (m-2)t = mt`.

The exact finite checks in `verify.py` exercise the formal output identity, a nontrivial upper-entry cancellation, the scalar-span inequality on short words and a missing-cancellation control. They are corroboration, not a substitute for the argument.

## Dependencies and limits

Eumemic's PR288 supplies the model. Ali Romman's PR468 supplies normalization, projection and the original flag inequality. PR5988 supplies the all-dimensional support split. Unpaidmoon's PR6338 supplies the clean-helper question and all non-two-support cases. These are cited inputs, not results rechecked here.

Ali Romman's PR4961 already proves the stronger unrestricted-span nine-call bound for three lower-triangular `3 x 3` data targets with one returned register. It contains that particular case of the present statement. The contribution here is the all-dimension, arbitrary-data-count and arbitrary-clean-helper-count small-span flag bound, not the three-data one-helper instance. Unpaidmoon's PR4118 gives a partial bound for arbitrary dirty auxiliaries at the same three-dimensional span; its unresolved five-call block case does not assert this general common-target-flag result.

Targets without a common rational flag, nonzero dirty helper exponents in the two-block, span above `m+1`, free address maps, physical implementation, native and caller costs, and any complete multiplication theorem remain outside the statement. No new kappa is claimed.
