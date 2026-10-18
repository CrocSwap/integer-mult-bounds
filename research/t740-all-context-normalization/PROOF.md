# From every literal hosted context to the same twenty-site map

## Statement

Fix the canonical T740 base fill, 10-copy lifting, 145-row journal, dispatch,
provider widths, allocation plan, ordered data schedule and 112 port recipes in
SOURCES.json. For each owner `o` in `0..739` and port `p` in `0..111`, retain
that context's hosted phases at their literal times. Multiply each residual
phase at child `j` in `0..19` by an arbitrary `z_j` in `C*`.

For every character `x` in `F_2^73`, the normalized eight-stream operator equals
PR3297's retained polynomial matrix `F(z; g_p(x))`, where
`g_p(x)=i^(-parity(q_p & x))`. In particular the normal form does not depend on
`o` or on its hosted/residual split. This is a finite-source theorem quantified
over all characters and all nonzero complex multipliers, not an all-size caller
theorem.

## A sufficient transport condition

At a fixed character, a hosted axis list `H` on stream `r` acts by a diagonal
matrix with entry `f_H(x)=i^(sum_{a in H} parity(a & x))` at row `r` and unit
entries elsewhere. It commutes with every other diagonal phase, including
translations, unchanged residual factors and formal multipliers.

It also commutes with a shear `I+c E_ds` whenever `r` is neither `d` nor `s`.
Thus it may move forward to its own residual insertion if no intervening shear
has `r` as source or destination, and no intervening stream permutation occurs.
This condition is sufficient, not necessary. The proof never treats a
phase on a shear source as free to move merely because that source is read-only.

After moving all hosted factors of one child to that insertion, their product
with the unchanged residual factor is exactly the factor of the full child
basis. Each original axis occurs once because the source slices are disjoint
and the residual list is the complement of their union. The translation and
`z_j` remain at the original site. Diagonal factors commute with one another,
so transporting different children introduces no additional condition.

## Exhaustive source certificate for the transport premise

The global order consists of the 666 base calls, each lifted into ten consecutive
copies. The checker verifies that every owner executes local stages 0 through 8
exactly once in increasing order. For a hosted row at time `t`, its stage cut is

```text
k = number of that owner's local-stage times strictly less than t.
```

Hosting occurs before the caller's data events at the same global time, so
strict inequality is essential. A host at the same time as owner stage `k`
starts immediately before that stage, not after it. Calls of other owners have
no intervening data events on the eight streams of this context.

From the literal schedule, the checker marks both rows of every local shear
and all four rows of each paired bridge as touched. It then derives the
following sufficient cuts ending at each child's residual insertion:

| Children | Allowed stage cuts |
| --- | --- |
| 0, 2 | 0, 1 |
| 1, 3 | 2 |
| 4, 6 | 0, 1, 2, 3 |
| 5, 7 | 4 |
| 8, 10 | 0, 1, 2, 3, 4, 5 |
| 9, 11 | 6 |
| 12, 13 | 3, 4, 5, 6, 7, 8 |
| 14, 15 | 5, 6, 7, 8 |
| 16, 17 | 7, 8 |
| 18, 19 | none |

This table is derived, not hard-coded as the acceptance test. Each local stage
has its literal pair and direction. A terminal permutation is required to
follow every residual insertion. Other intervening events are diagonal or
checked bridge/local shears. No hosted row uses children 18 or 19.

For every one of the 2,717,280 expanded rows, the checker derives the width from
its actual caller's dispatch and provider helper. It checks the destination
owner, port and child, the plan's physical row against the residual site's row,
the allowed stage cut, the slice range, and disjointness from preceding slices.
It checks compact prefixes after processing every context. All 82,880 contexts
are visited, with no failed transport premise. The complete expanded payload
hash also matches the predecessor's canonical fill, so the certificate is not
merely a projection omitting inconvenient rows. Every exchange preimage and
unchanged call/helper identity is checked before expansion.

The elementary commutation argument therefore reduces every context to its
full-child word. The source-specific computation proves the premise for a
finite set of literal contexts. The matrix implication then holds for every
character and multiplier, not only for tested phase values.

## The port-dependent full-child word

After transport, only the port recipe remains variable. For every one of the
112 literal recipes, algebra.py executes the complete data word, including all
20 idle phases, local changes, bridges, terminal translations and signed terminal
exchange. It uses the exact Boolean-character identity

```text
parity(a & x) = sum_i a_i x_i - 2 sum_{i<j} a_i a_j x_i x_j mod 4.
```

Higher-degree terms have coefficients divisible by four. Two bitsets hold the
low and high linear coefficients; a third holds the even quadratic coefficients.
Formal monomials carry their exact integer coefficient and a 20-bit variable
mask. Source operations are additions, multiplication by character phases and
one insertion of each formal variable. Distinct formal terms are combined only
when their exact phase polynomials agree. No floating point or sampled-character
identity test is used.

After removing `i^(popcount(x))`, every term's remaining ambient phase is exactly
`1` or the port's own `g_p(x)`. The coefficient, row, column, variable mask and
ambient type of every term match the unchanged 72-term PR3297 receipt. All 112
port checks pass. The all-one assignment reduces coefficient by coefficient
to the identity. Therefore all actual contexts have the stated `F`.

The common final-cover convention and the omission of the bank-padding and
whole-family-translation bookkeeping from the eight-stream projection are the
same boundary used by the predecessor. This proof does not establish a new
native or whole-supplier interpretation of that projection.

## Inherited consequence, not a new inverse proof

PR3297's [retained proof](reference/PR3297-PROOF.md) gives a rational inverse
for `F` on `(C*)^20`, for every nonzero `g`, with nonzero monomial denominators.
The new normal-form equality makes that same inverse applicable to every actual
owner and port. This package inherits that algebraic implication; it does not
claim an independent verification of the inverse or depend on a peer audit.

Consequently, under that inverse, equality of two complete fixed-interface
operators at every character forces each child's residual phase function to
remain unchanged. For a linearly independent residual list of rank `r`,

```text
|E_x i^(sum_{a in R} parity(a & x))|^2 = 2^(-r).
```

Equality of phase functions fixes `r`. With the hosted basis fixed and a legal
independent combined basis, full child rank is fixed too. Literal bases need
not be unique. Dependent axis lists do not satisfy this rank conclusion.

## Boundary and credit

The theorem fixes the original source, hosting, charts, translations, data word
and insertion cuts. It does not normalize a proposal that changes those events,
prove arbitrary new hosting legal, price a new consumer, execute native gates,
or supply a multiplication theorem or new kappa. Different contexts can have
different original ranks; the claim fixes each context's own ranks under an
operator-preserving replacement, not equality of all original rank profiles.

The matrix, inverse and phase representation retain thakrarsagar/PR3297 and
PR3272 credit. Ross Richardson had publicly reported related local-only
normalization work. This proof does not claim method priority over it. It adds
a complete source-bound coverage certificate. Full provider, fill, journal,
physical-stream and geometry attribution is in README.md.
