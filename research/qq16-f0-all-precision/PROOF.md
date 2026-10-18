# Uniform precision for the credited F0 witness

## 1. Model and theorem

Use the literal 26,099-event F0 word and exact native conventions authenticated
by `SOURCES.json`. The model is PR3067's mixed arithmetic. Each scalar ADD
component rounds nearest-even to a normalized binary significand of p bits.
The exponent is unbounded. Completed native operators, native interiors,
endpoint/residual adapters, SCALEs and private CLEARs are exact. Source and
destination fields are distinct at every ADD. Private inputs are zero here.

For every integer `p >= 8`, let `D_p=2^(p+12)` and enter physical fields
`L112=ONE`, `L224=D_p ONE`, with every other field zero. The ideal exact word
returns the entry. The mixed rounded word has only the five errors stated in
the README. All helpers return exactly and all private fields are zero.

The exact word, the witness and this endpoint pattern are credited to
PR3036/PR3067/PR3017. The new assertion is their validity simultaneously for
all these p. Its proof uses the following rational predicate rather than
inferring a universal statement from finite runs.

## 2. A nearest-even lemma on a precision ray

Let a and b be real dyadic rationals. Write `x_p=a*2^(p+12)+b`. Fix an integer
`p0 >= 2`.

If `a=0` and b's reduced numerator needs at most p0 bits, b is exactly
representable at every `p >= p0`, so `RN_p(x_p)=b`.

Otherwise put `A=a*2^(p0+12)`, `z=A+b`, and
`e=floor(log2(abs(z)))`. Assume:

1. A and z have the same nonzero sign.
2. `2^e <= abs(A) <= 2^(e+1)`.
3. If `abs(A)=2^(e+1)`, then `a*b<0`.
4. With `q=2^(e-p0+1)`, the number `A/q` is an even integer.

Then, for every integer `p >= p0`,

```text
RN_p(x_p) = a*2^(p+12) + q*nearest_even_integer(b/q).       (1)
```

To prove this, put `t=2^(p-p0)`. Dividing `x_p` by t gives `A+b/t`, a convex
combination of z and A. Conditions 1 through 3 keep its sign fixed and its
absolute value in `[2^e,2^(e+1))` for every finite t. The possible upper endpoint
is only approached from below. Thus x_p's binary exponent is exactly
`e+p-p0`. Its p-bit grid spacing is the constant q, independent of p.

Condition 4 makes `t*A/q` an even integer. Adding that even integer commutes
with rounding `b/q` to the nearest integer, including tie parity. Multiplying
by q proves (1). If rounding reaches the upper binade boundary, that boundary
is itself representable and has the required even parity. Negative values
follow by sign symmetry. The classifier fails closed if any predicate is not
established. It makes no claim outside those predicates.

All comparisons and nearest-integer decisions in this lemma use integer or
Fraction arithmetic. No floating logarithm or finite precision calculation
establishes a predicate. The separate test oracle enumerates neighboring
normalized binary numbers and does not call the classifier.

## 3. Induction through the actual program

Maintain two exact Gaussian-dyadic vectors per field, u and v. Their meaning
is `D_p*u+v` for every `p >= 8`.

At entry u is ONE only in L224 and v is ONE only in L112. Every completed
native event is a fixed complex-linear operator, so applying the same exact
operator separately to u and v preserves this meaning. The event dispatcher
includes the actual child recipes, native lines, source/target endpoint
monomials and residual adapters. Phase events are control markers. No cover
sweep occurs in F0. Uniform-owner input and the inherited local tensor
convention are unchanged from the predecessor.

At a scalar ADD, the exact coefficient product is computed on both tracks.
For every real and imaginary component, the lemma certifies that this product
is already exactly representable for all p on the ray. The model's separate
coefficient multiplication therefore introduces no additional rounding here.
The destination sum is then treated by the lemma. Equation (1) leaves u
unchanged and supplies one exact new v. SCALE coefficients are nonzero signed
powers of two and remain exact in the stated model. Each CLEAR targets only
an owned private field and sets both tracks to zero.

The source-bound replay checks the lemma's predicates at every scalar product
and every ADD result. It checks every component whenever u is nonzero; for
zero u, every distinct constant coefficient suffices. The fixed word has
40,556 such vector obligations. All pass with p0=8. Thus ordinary finite
induction on 26,099 events establishes both symbolic tracks for every p>=8.

Exactly two ADDs change the constant track. At event 3887,
`L112 -= L224/2`, and event 4060, `L139 -= L224/2`, each rounded component is

```text
exact       -2^(p+11)+1/2
rounded     -2^(p+11)
error       -1/2.
```

The decisions are not ties. The symbolic replay compares all 712 returned
vectors with the claimed tracks, not just a final digest or the five named
fields. The ideal run independently follows both tracks without ADD rounding
and returns the entry. The rounded run returns the unchanged leading track
and the constant-track errors

```text
L112: -ONE; L114,L137,L190,L211: -ONE/2; all other fields: zero error.
```

This closes the finite certificate of the induction's source-specific
premises. The written lemma supplies its universal quantifier. It is not a
formal-kernel verification of that lemma, the primitive evaluator or a complete
multiplication theorem. The direct unchanged predecessor executor agrees at
p=8,127,256 as a separate implementation control, not the universal proof.

## 4. Consequences and limits

ONE has Euclidean norm `sqrt(512)`. The largest error therefore equals the
input data norm, giving relative error one. Every exact linear map and binary
nearest-even rounding commutes with multiplication by a signed power of two.
Scaling the entire input by `1/32` gives data norm `1/sqrt(2) <= 1` while
preserving relative error one. Arbitrary non-power-of-two scalings are not
asserted to commute with rounding.

The dirty input changes with p. Consequently the theorem rules out a
precision-only uniform data-relative accuracy claim over arbitrary dirty
magnitudes for this exact mixed model. It does not rule out increasing
precision for one fixed dirty input, an admitted dirty-range bound, exact-grid
arithmetic, changed operations or retained information. It is not an
injectivity theorem or a fully rounded native-program collision. No inference
about finite exponents, tensor powers, paid precision, recursive costs or the
F17 consumer follows without their separate contracts.
