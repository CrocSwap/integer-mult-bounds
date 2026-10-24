# Four binary full-guard events lie below the product of their marginals

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and dependencies

Let m >= 4, and let U_1,...,U_4 be pairwise orthogonal rank-one idempotents
on F_2^m. Put P_t = I-U_t. Choose G uniformly from the complete group
GL_m(F_2). Event E_t means that every leading principal minor of
G P_t G^-1 of orders 1 through m-1 is nonzero.

Write n=m-1, X=2^m, and

```text
s_m = 3^n / [(X-1)2^n],
rho_m = Pr(E_1 intersect E_2 intersect E_3 intersect E_4) / s_m^4.
```

**Theorem.** For every m >= 4,

```text
Pr(E_1 intersect E_2 intersect E_3 intersect E_4) < s_m^4.
```

Moreover,

```text
1-rho_m = 12(7/9)^n + O((19/27)^n),
lim_(m->infinity) (1-rho_m)/(7/9)^n = 12.
```

This is a scoped counting proof with an exact finite component. It answers
k=4 of Open next question 2 in #4275. The theorem does not assert negative
association for arbitrary functions or arbitrary groups of events.

The marginal s_m is the corank-one law of Nick Petalas's #4227. The joint
character law is Theorem 2 of Nick Petalas's #4275, retained at canonical
main f626db5c3a3d781d8f7695038776c621651f75e1 in
`research/corankone-triple-header-law/PROOF.md`. These theorems are cited
steps, not new results or audit deliverables here. SOURCES.json binds the
exact predecessor proof. The new result is the four-event inequality and
the leading correlation deficit. The character calculation below is the
finite component needed for that new inequality.

## 1. Normalize the joint law

Let c run over the 4-by-4 binary matrices with zero diagonal. There are
2^12=4096 such characters. Define

```text
Z(c) = sum_(sigma in {0,1,2}^4)
       (-1)^(sum_(i,j: sigma_i=1, sigma_j=2) c_ij),
N_n = sum_c (-1)^|c| Z(c)^n.
```

The cited character law gives a numerator C_n=N_n/4096 and denominator

```text
D_m = (X-1)(X-2)(X-4)(X-8) 2^(4m-16).
```

Consequently, with all powers of two canceled exactly,

```text
rho_m = (N_n/81^n) H(X),
H(X) = (X-1)^3 / [(X-2)(X-4)(X-8)].                 (1)
```

The finite-GL factor H(X) is greater than one. It cannot be dropped when
proving the product inequality.

## 2. Exact finite character calculation

Grouping every character by Z(c) gives the following signed multiplicities
b_z, so that N_n=sum_z b_z z^n. Zero signed multiplicities are omitted.

```text
 z    b_z       z    b_z
81      1      37    228
63    -12      35   -336
57     24      33    399
55     -8      31   -444
51    -24      29    502
49     18      27   -548
47    -48      25    523
45    118      23   -332
43    -68      21    144
41     85      19    -48
39   -180      17      6
```

The finite calculation is independently executable in two forms in
verify.py. `literal_characters` evaluates the definition of Z(c) on all
4096 characters, each over all 81 ternary assignments. `step_weights`
enumerates all 256 pairs x,y in F_2^4, retains disjoint supports, and counts
their zero-diagonal rectangles y x^T. Its XOR-convolution transform,
computed by twelve exact Hadamard stages, agrees character by character.
The signed table then follows by weighting each character by (-1)^|c|.
A direct integer walk without diagonalization corroborates C_n for
0 <= n <= 12. No sampled character or floating-point arithmetic is used.

In particular,

```text
N_n = 81^n - 12*63^n + R_n,
|R_n| <= 4083*57^n,                               (2)
```

because the absolute signed multiplicities below 63 sum to 4083 and their
largest base is 57. The signed spectrum itself is predecessor counting
data; its use to settle the four-event inequality is the contribution.

## 3. All large dimensions

Put x=(7/9)^n. The exact integer inequality

```text
4083*57^84 < 63^84
```

and monotonicity of (57/63)^n show, for every n >= 84, that

```text
N_n/81^n <= 1-11x.                                (3)
```

For X >= 32 the denominator of H(X) is at least

```text
(15/16)(7/8)(3/4) X^3 = (315/512) X^3.
```

Its numerator minus its denominator is 11X^2-53X+63 <= 11X^2.
Since 11*512 < 18*315,

```text
H(X)-1 < 18/X = 9/2^n.                            (4)
```

The exact inequality 9*9^84 < 14^84 and monotonicity show that
9/2^n < x for every n >= 84. Also 11*7^84 < 9^84, so 1-11x is
positive there. Combining (1), (3), and (4) gives

```text
rho_m < (1-11x)(1+x) = 1-10x-11x^2 < 1.
```

This proves the theorem for m >= 85. All constants in this argument are
checked with exact integers by `proof_checks`.

## 4. Remaining finite dimensions

For every integer 4 <= m <= 84, `proof_checks` evaluates the character
count and the fractions in (1), then checks the strict rational inequality
Pr(intersection E_t)<s_m^4. This is 81 separate exact comparisons. The
verifier's generated JSON enumerates every dimension, joint fraction and
ratio. The normal and optimized modes both execute explicit checks.

At m=4 the joint fraction is zero. At m=5 it is 1/208320, whereas each
marginal is 81/496. The finite calculation and the uniform argument cover
every m>=4, with no unchecked interval. This is a computer-assisted finite
component of a written proof, without a proof-kernel certificate.

## 5. Leading deficit

Equation (2) gives

```text
N_n/81^n = 1-12(7/9)^n + O((19/27)^n).
```

Equation (4) gives H(X)=1+O(2^-n). Since 1/2<19/27<7/9, multiplying these
expressions in (1) proves the asserted deficit and limit. The limit is an
analytic consequence of the bounds, rather than a numerical extrapolation.

## Scope

The theorem requires exactly four fixed, pairwise orthogonal rank-one
kernel projectors over F_2 and uniform weighting of complete GL headers.
It does not settle k>=5, odd characteristic, restricted header covers,
nonorthogonal kernels or general dependence properties. The minimal-dimension
classification reserved by another contributor is not a deliverable here.

Binary header arithmetic extends beyond the retained odd-prime normalizer's
executable domain. A producer, header selection/emission, dispatch, dirty
restoration, stock, precision and complete physical caller remain open.
Their costs are unknown. No supplier, new kappa or complete multiplication
theorem follows from this density inequality.
