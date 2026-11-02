# Six orthogonal full-guard events lie below the product of their marginals

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
This answers the k=6 case of the open product inequality in
[discussion comment 19144831](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144831).
Nick Petalas's #4275 supplies the character law and the m=k threshold.
Ryanson Jonathan's #4599 and #4607 settle k=4 and k=5. The 19/21 remainder
gap is Nick Petalas's #5146. No new κ is claimed.

## Statement

Let m ≥ 6. Let U_1, …, U_6 be pairwise orthogonal rank-one idempotents on
F_2^m, and let G be uniform in GL_m(F_2). Event E_t says that every leading
principal minor of G(I−U_t)G^{−1}, of orders 1 through m−1, is nonzero.
Write n = m−1, X = 2^m and

```text
s_m = 3^n / ((X−1) 2^n).
```

**Theorem.** For every integer m ≥ 6,

```text
Pr(E_1 ∩ ⋯ ∩ E_6) < s_m^6.
```

At m = 6 the joint probability is 0. The ratio tends to 1 from below. The
proof is a scoped counting argument with one exhaustive 2^30-character
spectrum and an integer tail for every larger dimension. It is not a
negative-association theorem for other events, a supplier admission, or a
selected-frontier change.

## 1. Reduction

A basis change takes U_t to e_t e_tᵀ and only permutes complete headers.
#4275, Theorem 2, counts the headers whose first six diagonal guards all
pass. With N_n = Σ_c (−1)^{|c|} Z(c)^n and K = 30,

```text
Z(c) = Σ_{σ in {0,1,2}^6} (−1)^{Σ_{i≠j} c_ij [σ_i=1][σ_j=2]},
D_n = N_n / 2^{30},
Pr = D_n / (2^{6n−30} (X−1)(X−2)(X−4)(X−8)(X−16)(X−32))
   = N_n / (2^{6n} (X−1)(X−2)(X−4)(X−8)(X−16)(X−32)).
```

The same theorem gives the one-event count 3^n, hence the marginal s_m.
Dividing Pr by s_m^6 cancels 2^{6n} and one factor of X−1, and produces

```text
ρ_m = (N_n / 729^n) · H(X),
H(X) = (X−1)^5 / ((X−2)(X−4)(X−8)(X−16)(X−32)).
```

The subset form used by the enumerator,

```text
Z(c) = Σ_{S: every j∉S has even incoming parity from S} 2^{6−|S|},
```

is the closed form obtained by summing the label-2 coordinates in Z(c).
The verifier checks it against the literal three-state sum on every
zero-diagonal character at k=3 and k=4, and checks that the same enumerator
reproduces #4275's published k=3 coefficients and #4607's leading k=5
coefficients 243^n − 20·189^n + 60·171^n.

## 2. The signed spectrum

The enumerator walks all 2^30 edge masks by a Gray code. Each step flips
one arc and updates the incoming-parity mask of the 2^{4} source sets that
contain that arc. The resulting 176 nonzero coefficients begin

```text
N_n = 729^n − 30·567^n + 120·513^n + R_n.
```

Here 567 = 7·3^4 and 513 = 19·3^3. #5146 already separates these from
every matrix with two or more entries, whose character is at most 513.
The verifier evaluates the three-state sum on all 30 single arcs and on
all 120 two-arrow stars (six orientations on each triple of vertices,
every other entry zero). Each arc has Z = 567 and odd weight. Each star
has Z = 513 and weight 2. The absolute coefficients sum to 2^30, so no
character value contains both signs. Those two evaluations are therefore
the entire levels: coefficient −30 at 567 and +120 at 513.
Every other character has Z ≤ 495, and the absolute sum of those
coefficients is A = 1,073,741,673. Thus

```text
R_n ≤ A·495^n,    N_n ≤ 729^n − 30·567^n + 120·513^n + A·495^n.
```

Two direct counts fall out of the same table. N_n = 0 for 0 ≤ n ≤ 5, so
there is no positive walk of length less than 6 and the joint event is
empty at m = 6. At n = 6, N_6 / 2^30 = 23,040, an exact positive header
count at m = 7. Adding one to the single-arc coefficient makes N_5 nonzero,
so that vanishing is not a rounding accident.

## 3. Dimensions 7 ≤ m ≤ 130

For n from 6 through 129 the verifier compares the integers

```text
N_n · (X−1)^5 < 729^n · (X−2)(X−4)(X−8)(X−16)(X−32).
```

Each comparison is strict. Floating point already rounds ρ_m to 1 at these
dimensions; the sign is carried by the integer slack. Representative exact
ratios are about 0.000270 at m = 7, 0.00996 at m = 8, 0.3767 at m = 13 and
0.9988 at m = 41.

## 4. Every larger dimension

Let L(n) = 27·567^n − 120·513^n − A·495^n. The spectrum bound and L(n) ≥ 0
give

```text
N_n ≤ 729^n − 30·567^n + 120·513^n + A·495^n = 729^n − 3·567^n − L(n)
    ≤ 729^n − 3·567^n.
```

The verifier finds L(129) > 0, and also that 26·567^{129} does not cover
the same remainder, so three single-arc modes are what this cap leaves at
the threshold. Expanding the definition gives

```text
L(n+1) − 567 L(n) = 120·513^n·54 + A·495^n·72 > 0,
```

so L(n+1) > 567 L(n) and L stays positive.

It remains to show (729^n − 3·567^n) H(X) < 729^n. Expanding the
denominator gives the integer identity

```text
(X−1)^5 − (X−2)(X−4)(X−8)(X−16)(X−32)
  = 57X^4 − 1230X^3 + 9910X^2 − 31739X + 32767.
```

For X ≥ 128 the positive lower terms satisfy 9910X^2 ≤ X^4 and
32767 ≤ X^4, so the difference is at most 59X^4. Therefore it is enough
that

```text
3·567^n · (X−1)^5 > 59 · X^4 · 729^n,    X = 2^{n+1}.
```

The verifier checks this at n = 129, where X = 2^{130}. If P(n) and N(n)
are the two sides, the next order is 2X, so

```text
P(n+1)/P(n) = 567·((2X−1)/(X−1))^5 > 567·32 = 18144,
N(n+1)/N(n) = 16·729 = 11664.
```

The fifth-power ratio is strictly larger than 2 because
(2X−1)/(X−1) = 2 + 1/(X−1). A strict gap at n = 129 therefore stays
strict at every larger n. Also 729/567 = 9/7 > 1, and the verifier finds
729^{129} > 3·567^{129}, so 729^n > 3·567^n remains true and the
comparison upper bound stays nonnegative. The degree-four majorization
was checked at X = 128, the smallest integer in its hypothesis, and both
9910 ≤ X^2 and 32767 ≤ X^4 become looser as X grows. Hence ρ_m < 1 for
every n ≥ 129. Section 3 already includes that threshold, and sections 2
through 4 together cover every m ≥ 6.

## Scope

**Covered.** Exactly six fixed, pairwise orthogonal rank-one requests over
F_2, with complete headers weighted equally, at every m ≥ 6.

**Not settled.** k ≥ 7 inside the strip k+1 ≤ m ≤ 8(k(k−1)+1), odd
characteristic, restricted header families and nonorthogonal kernels.
#5146 already supplies a loose eventual bound past that strip; this package
does not rerun it and does not improve it for k ≥ 7.

**Not claimed.** A physical saving, a supplier, a new κ, or proof-kernel
review. Header probabilities are not an executed caller.
