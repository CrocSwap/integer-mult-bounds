# Paid-fusion moment ceiling

A legal rewrite that fuses paid child jobs keeps the productive multiset `T`
fixed and replaces paid ranks `b_1,...,b_m` by their sum. This package proves
what such a rewrite can and cannot buy at a crossing exponent `c` with
`0 < c < 1`, and gives the exact ceiling. Nothing here is source-bound: it is a
statement about the moment model the signed invoice uses, not about a word.

## Definitions

For a finite multiset `H` of positive integers (ranks) and real `c`, write

  `M_H(c) = sum_{h in H} h^c`.

The gate compares `M_T(c)` with `M_P(c)`; a rewrite is favourable at `c` when it
increases `M_T(c) - M_P(c)`. The crossing exponent is the root of that
difference on the relevant interval.

## Results

Throughout `0 < c < 1` and all ranks are integers `>= 1`.

1. **Strict subadditivity.** `(a+b)^c < a^c + b^c` for all `a,b >= 1`.
   Consequently every paid fusion strictly lowers the paid moment at every
   exponent in `(0,1)`, and every productive split strictly raises the
   productive moment at every such exponent. The sign is exactly reversed for
   `c > 1` and everything is an equality at `c = 1`.

2. **m-block form.** For `m >= 2` and `b_i >= 1`,
   `(b_1+...+b_m)^c < b_1^c + ... + b_m^c`.

3. **Sharp single-fusion cap.** With `D(a,b) = a^c + b^c - (a+b)^c`,

   `0 < D(a,b) < min(a,b)^c`,

   and the constant one is sharp: for fixed `a`, `D(a,b)/a^c -> 1` as
   `b/a -> infinity`. It is never attained. For a fixed total rank `r = a+b`,
   `D(a,r-a)` is instead maximized by the balanced split and minimized by the
   unbalanced ones. So no single fusion is worth one full copy of its smaller
   job's moment; very unequal pairs approach that cap when the smaller rank is
   held fixed, while at a fixed total paid mass a balanced merge buys most.

4. **Global fusion ceiling.** Let `P` be a paid multiset and let any partition
   of `P` into blocks be replaced by the block sums. The paid moment falls, and
   it stays at least the single-job moment of the whole paid mass:

   `M_{P'}(c) >= (sum_{p in P} p)^c`,  so  `M_P(c) - M_{P'}(c) <= G(c)`,

   where `G(c) = sum_{p in P} p^c - (sum_{p in P} p)^c`, with equality only for
   the one-block (full) fusion. `G` is therefore the total budget every
   paid-only fusion scheme shares.

5. **Crossing consequence.** If a rewrite fuses paid jobs and leaves `T` fixed,
   then at every `c` in `(0,1)`

   `M_T(c) - M_{P'}(c) <= M_T(c) - (sum_{p in P} p)^c`.

   Hence the crossing exponent after any paid-only fusion is at most the root
   of `M_T(c) = (sum_P p)^c`. No choice of which jobs to fuse, and no number of
   fusions, can pass that root. This is the stopping rule: a paid-fusion search
   that cannot reach the root against one collapsed paid job cannot reach the
   claim either.

## Proofs

1. `x -> x^c` is concave on `[0,inf)` for `0<c<1`, so its derivative is
   strictly decreasing and

   `(a+b)^c - a^c = int_a^{a+b} c x^{c-1} dx < int_0^b c x^{c-1} dx = b^c`.

   Concavity also gives `(a+b)^c > b^c` and `(a+b)^c > a^c`. For `c>1` the
   derivative is increasing and both inequalities reverse; at `c=1` the two
   sides are equal.

2. Induct on `m`, applying (1) to `(b_1+...+b_{m-1})` and `b_m`; the sum of the
   first `m-1` terms is itself strictly greater than their `c`-power sum.

3. Lower bound: `D > 0` is (1). Upper bound: assume `a <= b`; then
   `D = a^c + b^c - (a+b)^c < a^c` because `b^c < (a+b)^c`. Sharpness: put
   `s = b/a`; then `D/a^c = 1 + s^c - (1+s)^c`, and
   `(1+s)^c - s^c = s^c((1+1/s)^c - 1) -> 0`, so the ratio tends to one. The
   fixed-sum claim: `g(a) = a^c + (r-a)^c` has
   `g''(a) = c(c-1)(a^{c-2} + (r-a)^{c-2}) < 0`, so `g` is concave and
   symmetric; a concave symmetric function is maximized at its midpoint and
   minimized at an endpoint, so `D = g - r^c` has the same two extrema in the
   same order. Over integers `a >= 1` the endpoints are `a = 1` and `a = r-1`.

4. Apply (2) inside every block: the merged moment is strictly smaller than
   `M_P(c)` unless every block is a singleton. Apply (2) to the block sums
   themselves: `(sum_j s_j)^c < sum_j s_j^c` whenever there are at least two
   blocks, so `M_{P'}(c) > (sum_P p)^c` for every non-trivial partition. The
   one-block partition gives `M_{P'} = (sum_P p)^c` exactly, which is the
   smallest value any partition can reach and the ceiling `G(c)`.

5. Substitute (4) into the definition of the difference; both sides are
   monotone in `c`, so the root cannot move right of the root against the
   collapsed paid job.

## Verification

`verify.py` encloses every `a^c` in an exact rational interval and then checks
the statements above by exact rational comparison on finite grids:

- subadditivity and the sharp cap for all `1 <= a <= b <= 40` at five
  exponents, including `c = 363005817/100000000000` (the selected record's
  exponent) and `c = 1/279`, `1/1000` (`BIT`-scale and millesimal regimes);
- the `m`-block form for `m = 2,3,4` on five block shapes per exponent;
- the approach of `D(1,b)` to its cap for `b = 10^2..10^12` with exact integer
  square roots at `c = 1/2`, certifying `0.99 < D < 1` from `b = 10^4`;
- balanced-split optimality at fixed total rank against every other split of
  the same total for `3 <= r <= 60`;
- the global ceiling over five explicit multisets and every partition shape,
  with full collapse attaining the bound, plus a non-fusion control showing a
  paid split strictly raises the moment;
- rejection controls: `c = 1, 2, 3/2` (hypothesis fails), and non-positive
  ranks or `c = 0` (rejected).

The transcendental step is CPython `decimal` at 90 digits, correctly rounded
per its documentation, widened by one unit in the last place; all later
arithmetic is exact rational. A certified inequality is therefore a proof of
that finite case, not a floating-point observation.

## Limitations

- The result is a statement about the moment model. It does not certify that any
  word, caller, compiler, precision tape or outer row exists, and it does not
  bound the productive side, where #6651 already gives the balanced-split
  optimum for a concave tariff.
- Lemma 1 is classical. What is new here is the quantitative cap in (3), the
  total budget in (4) and the crossing consequence in (5), which turn the
  classical inequality into a search-stopping rule.
- No source-bound invoice is evaluated: the package proves a ceiling that any
  such invoice must respect.
