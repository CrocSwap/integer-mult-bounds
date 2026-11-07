# Price ceiling for any number of fully aligned arms

This strengthens the four-arm price consequence under a stronger geometric
hypothesis: **every** arm's complete pure coupling idle projector is identified
with one common projector by the actual ordinary coupling-only transport.
The independent proof in `all-aligned/PROOF.md` gives at least
`2+ceil(k/2)` net thin queries for `k>=3` arms, including the cancellation of
empty-field target credits. The root may have arbitrary binary children.

All costs and exclusions of `PRICE-CEILING.md` remain in force: a two-dimensional
coupling space, two full-support coupling targets, the frozen native profile,
the stated binary-node invoice, and no additional productive output credit.
We still grant one whole hub-idle job, even if a legal implementation cannot
realize it. This is not an assertion that pairwise alignment implies global
alignment, nor a restriction on arbitrary multi-coupling constructions.

## The all-arm envelope

Retain `D`, `U_g`, and `c` from `PRICE-CEILING.md`, and put

\[
H(m)=2(8m+1)^t-(8m)^t.
\]

For positive arm sizes summing to `m`, the complete relaxed margin is at most

\[
mD(t)+104\left[H(m)+\sum_{i=1}^k U_{g_i}(t)
-2-\lceil k/2\rceil\right]. \tag{1}
\]

We prove that (1) is negative for **all** `k>=3`, all lengths, and all saving
parameters `C>=1/310`, `C<1`. This is an upper bound for the declared family,
not an implemented supplier or a new multiplication exponent.

## Four or more arms: one affine support controls the unbounded family

First fix `t=309/310`. Strictly decreasing increments of `U_g` give the
global supporting line

\[
U_g\le U_9+(g-9)s,\qquad s=U_{10}-U_9.
\]

The previously certified `delta_9>c` shows `U_9=A_9` and
`s=81^t-72^t`. Exact integer-root bounds certify

\[
2U_9-18s-1<-0.4677774977<0.
\]

Consequently, using `ceil(k/2)>=k/2`, expression (1) is bounded above by

\[
mD+104\left[H(m)+ms+k(U_9-9s-1/2)-2\right]
\le B_m:=mD+104\left[H(m)+4U_9+(m-36)s-4\right]
\]

whenever `k>=4`. This eliminates the unbounded arm-count parameter without
enumerating it. The increments of `B_m` strictly decrease for `m>=4`, by the
same explicit derivative inequality for `H` proved in `PRICE-CEILING.md`.
For `m=37,38,39`, `B_m` equals that note's four-arm envelope exactly. Its
certified adjacent signs and negative maximum therefore prove

\[
B_m\le B_{38}<-0.7500056424<0\quad(m\ge4).
\]

## Three arms

Balancing the three lengths maximizes their `U` sum. Its total-length
increments strictly decrease for `m>=3`; the derivative estimate only needs
`(25/24)^2<2`. Exact certificates at the same rational exponent give

\[
E^{(3)}_{33}-E^{(3)}_{32}>0.1184894476,
\qquad E^{(3)}_{34}-E^{(3)}_{33}<-0.2291084915,
\qquad E^{(3)}_{33}<-30.2404991641.
\]

Here `delta_11>c` certifies that the binary envelope equals the all-one
formula on the side lengths used at totals 32, 33 and 34. Thus every
three-arm invoice is also negative.

## All larger savings and exact scope

For each fixed tuple and `k`, the normalized expression (1) divided by `9^t`
strictly increases with `t`: the native derivative is positive, normalized
`U_g` increases, normalized `H` increases, and the negative constant divided
by `9^t` increases. These component claims were proved explicitly in
`PRICE-CEILING.md`. Negativity at `C=1/310` therefore persists for every
`1/310<=C<1`. The supporting-line intercept need not be re-proved negative
at other exponents.

The original four-arm theorem requires only one actual cross-arm alignment.
This all-arm extension requires a common complete carrier for **all** arms.
Partial sharing graphs, chain/coupling mixing, altered supports or endpoints,
and different native profiles remain outside the conclusion. The threshold
is below the pending CrocSwap/integer-mult-bounds#6833 crossing but above the selected frontier.
**No new κ.**

## Reproduction and provenance

```sh
python3 -B research/p104-coupling-root-obstructions/all_arms_price.py
```

Expected: `PASS_ALL_ALIGNED_ARMS_PRICE`. Normal and optimized execution use
the exact integer 310th-root arithmetic already described in
`price_ceiling.py`; no floating point or external solver is used. The source
is authenticated again. Finite corroboration exhausts `3<=k<=24` and
`k<=m<=96`, with no random seed. The infinite claim comes from the supporting
line and concavity arguments, not this bounded domain. Four controls reject
false three-arm maxima, use of the theorem at two arms, and a constant
four-query charge at six arms; the latter optimistic model has positive
margin and would miss the growing query cost.

The query-rank extension and price argument were developed separately and
then cross-reviewed. Credit the source and concurrent predecessors recorded
in `README.md`. New proof and exact implementation prepared for @CubeJerry
with substantial OpenAI assistance. Apache-2.0.
