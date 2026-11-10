# Complete price consequence of the extra-query obstruction

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
This bounds the declared four-arm invoice below; it is not a new supplier.
The root/transport obstruction is proved separately in `PROOF.md`.

## 1. Frozen accounting and favorable relaxation

Use the 104-port native helper-minus-paid profile from CrocSwap/integer-mult-bounds#6833, exact source
`ad24ad966b857dbfed50d9121624db84b2eccc92`:

\[
D(t)=-2220-446\,2^t-485\,3^t-4^t-135\,5^t-4\,6^t
+7^t+39\,8^t+359\,9^t.
\]

`retained/CHAIN-RESULT.json` is authenticated byte for byte. The verifier
independently subtracts its native helper and paid histograms. Four positive
arm sizes sum to `m`; each size counts native leaves, not binary root groups.
The full-two-hub stage-support bill gives two hub targets of rank `8m+1`.
Each arm of length `g` contributes

\[
A_g(t)=\sum_{j=1}^g(8j+1)^t-\sum_{j=1}^{g-1}(8j)^t.
\]

The hub idle programs collectively cover `8m` fresh axes. Grant the most
favorable billing: **all** hub idles merge into a single rank-`8m` job, even
when the geometry would not permit it. This is more favorable than the two
proposed pair-merges. For positive ranks and `0<t<1`,
`sum r_i^t >= (sum r_i)^t`; any separately paid partition of this hub work
costs at least as much. Reuse that changes which work must be supplied is
outside this declared accounting.

When the root theorem's actual cross-arm hub-alignment hypothesis holds,
there are at least four thin queries after subtracting the rank-one target
credit of empty productive fields. For binary children this counts effective
root queries; child internal queries remain separately charged below.
Thus an optimistic complete direct-native margin is

\[
F_{\mathbf g}(t)=mD(t)+104\left[
2(8m+1)^t+\sum_{i=0}^3 A_{g_i}(t)-(8m)^t-4\right]. \tag{1}
\]

Extra queries, wrappers or restoration costs cannot improve (1). No extra
output credit is granted. Its rank-mass identity is `48m-208`, checked
independently. We do **not** assert four thin queries for an arbitrary
nonaligned root: the applicability conditions in `PROOF.md` are essential.

## 2. Binary child trees fit the upper bound

The retained `chain_root.py:outer_formula` charges each binary internal node
of `h>=2` native leaves two rank-`8h+1` targets, two rank-`8h` paid jobs and
one rank-one thin query. Put

\[
\delta_j=(8j+1)^t-(8j)^t,\qquad c=2\delta_2-1.
\]

An internal node contributes `2 delta_h-1<=c`. A partition into binary
children removes exactly as many all-one chain boundaries as it has binary
internal nodes. Its side bill is therefore at most

\[
U_g(t)=(8g+1)^t+\sum_{j=1}^{g-1}\max\{\delta_j,c\}. \tag{2}
\]

Each retained boundary contributes its delta; pair each missing boundary
with one internal node, whose contribution is at most c. Taking the larger
alternative at every boundary increases the bill. This includes arbitrary
ordered partitions and full binary tree shapes, a relaxation of the retained
balanced-child constructor. It is counting, not an operator-realizability
claim. The envelope was also established in the separate two-chain study;
its proof is repeated here to avoid a dependency on that submission.

The increments

\[
U_{g+1}-U_g=(8g+9)^t-(8g+1)^t+\max\{\delta_g,c\}
\]

strictly decrease with g. Balancing four side lengths therefore maximizes
fixed-total cost. Write `m=4q+r`, `0<=r<4`. Every declared grouped bill is
bounded by

\[
E_m(t)=mD(t)+104\left[2(8m+1)^t-(8m)^t+
(4-r)U_q(t)+rU_{q+1}(t)-4\right],\qquad m\ge4. \tag{3}
\]

## 3. The infinite envelope has a negative maximum

Let `h(x)=(x+8)^t-x^t`. The increment of (3) is

\[
E_{m+1}-E_m=D(t)+104\left[
2h(8m+1)-h(8m)+(U_{q+1}-U_q)\right],\quad q=\lfloor m/4\rfloor.
\]

The side increment is nonincreasing in m. The other term strictly decreases
for `m>=4`, since

\[
h'(x)=-t(1-t)\int_0^8(x+s)^{t-2}\,ds
\]

and pointwise

\[
\left(\frac{8m+1+s}{8m+s}\right)^{2-t}
\le\left(\frac{33}{32}\right)^2<2.
\]

Thus the derivative of `2h(8m+1)-h(8m)` is negative, so the increments of
E strictly decrease over its entire infinite integer domain.

At the exact rational saving `C=1/310`, `t=309/310`, integer-root bounds prove

\[
E_{38}-E_{37}>0.0406679361>0,\qquad
E_{39}-E_{38}<-0.0279991807<0,\qquad
E_{38}<-0.7500056424<0.
\]

The checker also proves `delta_9-c>0.0074927148`. The binary envelope equals
the ordinary A formula on all side lengths in these three values (at most
ten), justifying their coefficient evaluation. Strict discrete concavity
proves negativity for every m, including the unbounded tail. This is the
maximum of a relaxed envelope; no realizable all-hub merge is asserted.

## 4. Larger savings cannot recover a favorable margin

For each fixed arm-size tuple, divide its relaxed margin by `9^t`.
The native derivative has the positive rational lower bound

\[
\frac{d}{dt}\frac{D(t)}{9^t}
\ge\frac{2220}{9}\log9-\log(9/7)-39\log(9/8)
\ge\frac{323717}{1512}>0.
\]

Keep the positive rank-one derivative, discard the other positive low-rank
terms, and bound the negative terms of ranks seven and eight. The elementary
inequalities are `log x>=1-1/x` and `log x<=x-1`.
Each side endpoint divided by `9^t` is nondecreasing. Each normalized delta
increases: for j=1 it is `1-(8/9)^t`; for larger j it is `a^t-b^t` with
`a>b>=1`, whose derivative is positive because `x^t log x` increases on
`x>=1`. Normalized c is twice such a difference minus `9^(-t)`, also
increasing. The normalized maximum in (2) therefore increases.

The normalized hub term is an increasing difference
`((8m+1)/9)^t-(8m/9)^t`, plus `((8m+1)/9)^t`. Finally `-4/9^t` increases.
The relaxed margin divided by `9^t` strictly increases with t, and strictly
decreases with the saving C.

**Price consequence.** No invoice under these declared costs and the root
theorem's alignment hypothesis has positive margin for

\[
1/310\le C<1.
\]

The value `1/310=0.003225806...` is below the pending CrocSwap/integer-mult-bounds#6833 crossing near
`0.0033718004755`; it is **not** below the selected `0.003125804` frontier.
Thus this optimistic family cannot improve the strongest pinned pending
complex result. The attractive three-thin model omitted a mandatory cost.
Changed stage supports, coupling/chain mixing, different native profiles,
initialized ancillary input restrictions or a genuinely new interface can
escape this scoped result. **No new κ.**

## 5. Reproduction, independence and scope

```sh
python3 -B research/p104-coupling-root-obstructions/price_ceiling.py
```

Expected: `PASS_FOUR_ARM_PRICE_CEILING`. The same command with `-O` retains
all checks. For scale `S=2^40` and every required rank a, binary search finds
an integer z satisfying

\[
z^{310}\le a^{309}S^{310}<(z+1)^{310}.
\]

Then `[z/S,(z+1)/S]` encloses `a^(309/310)`. Signed integer coefficient sums
round outward. No floating point, predecessor pricing, or logarithm/exponential
implementation is used. `PRICE-RESULT.json` is deterministic.

The finite corroboration exhausts totals 4 through 96 (93 cases, no seed).
The infinite claim comes from the analytic concavity and monotonicity proofs.
Six controls reject omission of the mandatory fourth thin query, false maxima
37 and 39, fewer than four positive arms, a noninteger rank, and altered source
bytes. With the fourth charge removed the displayed optimistic bill is
positive, so the checker detects the disputed cost premise.

A separate research agent independently checked the integer-root bounds,
rounding, binary-envelope gap and infinite concavity argument. This is
mathematical/source review, not formal proof-kernel acceptance. The certificate
does not establish root realizability, full physical compiler admission, or
any of the five inherited framework assumptions.
