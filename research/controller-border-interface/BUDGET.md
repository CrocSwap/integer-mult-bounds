# What deleting the idle stages can and cannot save

This is a bound for the stated changed controller model, not a bound for every
native word or multiplication algorithm. The local helper and paid inventories
are frozen to Cinna Davis's #4470 and the retained query-thinned BIT invoice.
Changing those inventories, the number or nature of the main outputs, or the
central-query alphabet changes this model.

## A determinant invariant survives a scalar border

Work over the commutative Laurent ring in independent `Q,D_0,...,D_(2p)`.
Every shear and bridge has determinant one. A full stage multiplies exactly
two main roles by its `D_s`; a thin query contributes no `D_s`. Signed swaps
have determinant one. Thus, for one port of the controller with no idles,

    det A = product(s full) D_s^2.

There are `p+2` full stages, also when `p=1`. This determinant is a formal
identity; no numerical specialization or field-character evaluation is used.

Allow any invertible scalar matrices `L(e),R(e)` over the rational-function
field in an auxiliary parameter e, independent of Q and the D variables.
Suppose `L(e) A R(e)` has a finite, full-rank limit which is diagonal with
monomial entries. Its determinant is

    det L(e) det R(e) product D_s^2.

The full-rank limiting determinant forces the scalar factor to have a finite
nonzero limit. Hence the product of the limiting monomials has exactly the
same D degrees. In the source-compatible target model, each of the `2p` main
outputs has one central rank-one factor `Q` or `Q^-1`, and a product of fresh
stage factors with nonnegative degrees. Its credited rank is
`1+b*(number of stage factors)`, where b is 8 for complex or 7 for BIT.
Consequently the total main rank at v ports is necessarily

    M_p = 2v[p+b(p+2)].

This argument does not allow canceled positive and negative D degrees to earn
extra rank. Nor does it cover mixing the helpers into a different target
family: helpers here remain the separately productive native outputs. Allowing
any distribution of this total mass is already more favorable than requiring
integer ranks, individual stage-degree feasibility, or the actual triangular
controller's diagonal. For BIT this is a formal Laurent invariant before
physical scalar-extension admission, not a claim that the native involutive
representation has unique Laurent exponents.

The actual diagonal in [DISCOVERY.md](DISCOVERY.md) has, for p>=2, four v-field
groups of rank `1+2b` and `2(p-2)v` fields of rank `1+b`. At p=1 it has `2v`
fields of rank `1+3b`. At complex p16 the discarded idle mass is 141,568:
main output mass falls from 177,408 to 35,840. The same rank-mass surplus 752
remains. Deleting the bill while retaining the old targets is therefore invalid.

## An all-p optimistic ceiling, even with free extraction

Let `t=1-C`, with `0<=C<=1`. Write H(t) and P(t) for the *local* productive
helper and paid moments, and `h(t)=H(t)-P(t)`. The complete changed controller
has `p+2` copies of both inventories and `v(p-1)` paid rank-one thin queries.
Its optimistic surplus moment after any allowed redistribution of main ranks
is, by concavity of `x^t`, at most

    J_p(t) = (p+2)h(t) - v(p-1)
             + 2vp [1+b+2b/p]^t.

The tangent bound at `u=1+b` gives

    J_p(t) <= p A(t) + B_J(t),
    A(t)   = h(t) - v + 2v(1+b)^t,
    B_J(t) = 2h(t) + v + 4vbt(1+b)^(t-1).

The exact checker encloses the required rational powers by integer nth-root
comparisons on a 48-bit dyadic grid. It proves both A and B_J strictly negative
at C=.006 for complex and C=.007 for BIT. Approximate values are shown only
for readability; `RESULT.json` contains the exact rational enclosures.

| Inventory | C | A upper bound (rounded here) | B_J upper bound (rounded here) |
|---|---:|---:|---:|
| Complex #4470 | .006 | -2.6366097977 | -132.6282065737 |
| Retained BIT | .007 | -3.5731057048 | -133.1717283852 |

These inequalities exclude every positive integer p. The checker separately
rejects the declared target C=.01 and verifies the actual p=1 exception.

To extend the exclusion to every larger saving, combine equal-rank terms in
h. All its positive terms lie above rank 6 in complex, and above rank 15/2
in BIT; every negative term lies below that separator. The Jensen main base
`1+b+2b/p` also lies above it, while the paid thin query lies below it.
Dividing the *unlinearized* J_p(t) by separator^t makes every nonconstant
signed summand increasing in t. Thus J_p(t)<0 at the cutoff implies J_p(t)<0
for every smaller t in [0,1]. We do not require the tangent intercept to be
monotone. This proves the fixed-model necessary bounds

    C < .006 (complex),       C < .007 (BIT).

No positive supplier is admitted by this argument. Even a positive formal
moment must still pay for extraction, native scalar implementation, matching,
precision and all compiler/outer obligations.

The actual diagonal gives an affine surplus `p A(t)+B(t)` for p>=2, where

    B(t) = 2h(t)+v+4v[(1+2b)^t-(1+b)^t].

This independently agrees with explicit profiles at checked small and large p.
Positive controls at complex `(p,C)=(32,.005)` and BIT `(64,.006)` ensure that
the necessary moment checker is not simply rejecting every candidate. These
are formal invoices only. Omitting the paid thin queries incorrectly makes
the C=.01 test pass; the checker records that diagnostic undercharging fault.

## Repeated whole-controller extraction loses even with fresh helpers

Suppose a conversion evaluates the entire changed controller K>=2 times.
Grant each evaluation its own independent productive helper inputs and keep
all those helper outputs. Only the main inputs are copied and combined, so
their target inventory is credited once. The most favorable corresponding
surplus is

    main(t) + K[(p+2)h(t)-v(p-1)].

At t=1 and K=2 its rank-mass margin is exactly

    complex: -1920p-3616,       BIT: -1680p-3138.

For any redistribution of main ranks allowed above, Jensen bounds their moment
by `2vp(1+b+2b/p)^t`. Dividing this envelope by the same rank separator makes
it increasing in t. Its negativity at t=1 therefore implies negativity for
every t in [0,1]. Also h(1)=-1856 complex and -1617 BIT; the same normalized
monotonicity proves h(t)<0 throughout [0,1]. Each additional evaluation makes
the bill worse. Thus this repeated-whole-unit policy fails at every concave
moment, even granting free interpolation, routing and scalar operations.

Fresh helpers matter: they are legitimate independent productive inputs, not
copies. The checker retains their full credit. Its duplicate-main fault
instead credits the *same* main outputs twice: at p=2,t=1 that invalid bill
reports +160 complex or +162 BIT, while the correct bill is -7456 or -6498.
This is an ownership distinction, not a numerical interpolation estimate.

This obstruction does not cover exactification sharing paid calls between
evaluations, using extra independent main outputs, changing the native word,
or exploiting a different amplification theorem. [EXACTIFICATION.md](EXACTIFICATION.md)
states why a polynomial-overhead claim for the inherited chronological product
needs a new proof.

## Decision

The original symmetric C>.01 ambition is rejected for this fixed native
inventory and output contract, including the favorable redistribution above.
Increasing p or optimizing the same scalar filtration cannot meet it. The
explicit border remains a possible new interface, but a construction campaign
must first fund its recovery. A future target above .01 needs a changed native
paid/helper profile, a different output contract, or a different controller
query alphabet. This is a scoped stopping result, not a universal barrier.

Prepared by Dillon with substantial OpenAI Codex assistance. Apache-2.0.
Credit Cinna Davis, zxv, Jacob Alan Sussman and the source native/compiler
lineage; Matarener's #4602 identified the large idle bill that motivated this test.
