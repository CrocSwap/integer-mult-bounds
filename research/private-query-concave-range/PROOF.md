# Private scalar query cost for the full concave range

Result: the saved private scalar optimum extends to every `0<=b<=1`.
The minimum bill is `8*8^(1-b)`. This result gives no new construction
and no new integer kappa.

## Scope and proof inputs

Use the fixed retained 112-port E8 Gram correction `G=R R^T/4` and the
fixed binary source labels. In a factorization `G=sum_j u_j f_j`, each
nonzero scalar row has a private source frame of rank `1<=r_j<=9`.
The bill is `sum_j r_j^(1-b)`.

The saved independent proof supplies the following facts.

1. `rank(G)=8` and every nonzero row in its code has support at least 53.
2. A source frame of rank at most seven has capacity at most 36.
3. Every factorization has total private source rank at least 64.
4. At total rank 64, every profile that passes the necessary conditions
   has maximum rank at most eight.
5. Eight coordinate gathers of rank eight each factor `G`.

Facts 1, 2, 3 and 5 are in
`work/autonomous-kappa-run/framework/PRIVATE64-INDEPENDENT-REVIEW.md`.
Fact 4 is in
`work/autonomous-kappa-run/framework/private64-weighted/PROOF.md` and
has a separate rank-multiplicity check in `independent_max_rank.py` in
that directory. This new proof does not repeat those checks. The old
proof only bounds the weighted bill for `0<b<=1/32`.

Shared carriers, native blocks, productive ownership, and other source
encodings or controllers are outside this model. A binary invertible
change of all source labels preserves this result because it preserves
each source-frame rank. A nonzero diagonal scalar change of source
coordinates also preserves this result because it preserves every support.
No claim applies to an unproved change of the Gram code.

## A uniform scalar inequality

For `0<=a<=1`, put `F(a)=7*9^a+2-8*8^a`. Then

`F(a)>2/27`.

The ratio of the positive term to the negative term in `F'(a)` is

`(7*log(9)/(8*log(8)))*(9/8)^a`.

This ratio strictly increases. Thus `F` has a unique global minimum at

`a0=log(8*log(8)/(7*log(9)))/log(9/8)`.

The following five exact integer inequalities give all required bounds.

```text
9^7 < 8^8
8^96 < 9^91
13^10 * 8^7 < 12^10 * 9^7
9^17 < 8^18
8^7 * 3^10 < 13^10
```

The first gives `a0>0`. The second gives
`8*log(8)/(7*log(9))<13/12`. The third gives
`13/12<(9/8)^(7/10)`. Hence `a0<7/10`.
The fourth gives `8*log(9/8)/log(9)<4/9`.
The fifth gives `8^(7/10)<13/3`.

At the critical point, the derivative equation gives

`F(a0)=2-(8*log(9/8)/log(9))*8^a0`

`>2-(4/9)*(13/3)=2/27`.

This proves the inequality on the whole interval. Numerical samples
are not proof inputs.

## Complete weighted bound

Remove zero rows. Retain an independent basis of the query rows and
absorb each removed row into the decoder. This preserves `G` and removes
a positive charge. Let `N` be the number of retained rows, `q=sum r_j`,
and `a=1-b`. Then `N>=8` and `0<=a<=1`.

If `N=8`, the query space equals the eight-dimensional code. Each row
has support at least 53, so each frame has rank at least eight. Thus
`sum r_j^a>=8*8^a`.

If `q=64`, Fact 4 gives `r_j<=8`. Since `b>=0`,

`sum r_j^(1-b)=sum r_j*r_j^(-b)>=64*8^(-b)=8*8^a`.

In every other case, `N>=9` and `q>=65`. Concavity puts each value
`r^a`, for `1<=r<=9`, above its chord from rank one to rank nine:

`r^a >= A*r+C`,

where `A=(9^a-1)/8>=0` and `C=1-A>=0`.
Therefore

`sum r_j^a>=A*q+C*N>=65*A+9*C=7*9^a+2`

`>8*8^a+2/27`.

These cases cover every finite factorization in the stated model. The
eight coordinate gathers attain `8*8^a` for every `0<=b<=1`.
For `0<b<1`, equality forces exactly eight independent queries of rank
eight each. At `b=0`, other total-64 factorizations are not excluded.
At `b=1`, every eight-query factorization with frame ranks eight or nine
has the same bill of eight.

The upper endpoint is sharp for this cost law. If `b>1`, enlarge each
coordinate-gather frame to rank nine. This gives a valid private bill
`8*9^(1-b)<8*8^(1-b)`. This is an allowed source-frame change, not a new
physical circuit or global recurrence.

## Value and verification limit

The extension excludes a weighted-cost escape through redundant private
queries for the full concave range. It separates that obstruction from
the small current complex-saving interval. It does not improve the
current multiplier. The new proof needs five integer comparisons and
elementary calculus. The full submission also needs the substantial
finite geometry and sharp-rank dependencies of the unpublished proof.
The extension alone is small. Its prerequisite package is not small.

Run `verify_scalar_lemma.py` with a new output path. It checks each integer
inequality, the exact rational margin, and the endpoint algebra. It
imports no historical verifier and uses no floating-point arithmetic.
It verifies the new scalar lemma's finite premises. The hand proof
supplies the real-variable argument. It does not replay the Gram code,
profile screen, or final algebraic closures.

Prepared with OpenAI Codex assistance. New work is under Apache-2.0.
