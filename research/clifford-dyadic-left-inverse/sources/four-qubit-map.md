# Exact spectral endpoints at every odd width

This is a written algebraic proof with exact finite certificates. It
does not construct or price a physical decoder.

## Result

Use the full four-qubit Gaussian-dyadic Clifford group `G`, its natural
representation `V` of dimension 16, the Pauli subgroup `P`, and the
scalar subgroup `Z = <iI>`. Let `S = G/P = Sp(8,2)`. There are
`N = |G/Z| = 12,128,668,876,800` scalar cosets.

Choose a unitary representative `U_a` of each coset. At width `f`, let
`A_f` have columns `vec(U_a^(tensor f))/16^(f/2)`. Its normalized Gram
matrix is

```text
K_f(a,b) = (tr(U_a* U_b)/16)^f.
```

The star means conjugate transpose. A different choice of representatives
gives diagonal unitary conjugation and does not change the spectrum.

For an odd integer `f >= 13`, set

```text
p = (f-1)/2,
sigma = (-1)^floor((f+1)/4),
x = sigma 2^(-p).

P(x) = 1 + 255x + 32300x^2 + 2034900x^3 + 63083328x^4
       + 946249920x^5 + 6623744000x^6
       + 19871232000x^7 + 19871236096x^8.

Q(x) = 1 - 153x + 9860x^2 - 310284x^3 + 4806240x^4
       - 36044352x^5 + 126164480x^6
       - 189259776x^7 + 94633984x^8.
```

The following endpoints are exact and have the stated full eigenspaces.

| Width modulo 8 | Minimum | Minimum dimension | Maximum | Maximum dimension |
|---|---|---:|---|---:|
| 1 or 7 | `Q(x)` | 313,600 | `P(x)` | 256 |
| 3 or 5 | `P(x)` | 256 | `Q(x)` | 313,600 |

Both endpoints are positive. No other irreducible block attains either
endpoint at a finite width in this domain. The exact Gram condition
number is the maximum divided by the minimum. The condition number of
`A_f` is its square root. The norm of the least-squares coefficient
recovery map on the full span is the reciprocal square root of the
minimum. These are sharp constants for this normalized full alphabet.

All 81 spectral blocks are given by degree-eight polynomials in the
certificate. This extends the single-width spectrum in
[PR #7772](https://github.com/CrocSwap/integer-mult-bounds/pull/7772).
It does not change the threshold `T(4)=13` or any multiplication bound.

## 1. The phase at every odd width

We use the exact group and Pauli-sector identification from
[alephnan's proof](https://github.com/alephnan/integer-mult-bounds/blob/f7f32a18dde54e67624a9ed9cc7e1b266d9585c0/research/clifford-three-qubit-threshold/PROOF.md)
and the Gaussian trace argument in
[the four-qubit threshold proof](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/PROOF.md).
For a symplectic element with fixed-space dimension `d`, choose a Pauli
lift with nonzero trace `a`. Then

```text
|a|^2 = 2^d,
a^4 = (-1)^d 2^(2d).
```

The first statement follows from the signed permutation action on the
Hermitian Pauli basis. The signs on fixed labels form a character, and
Pauli translations supply all such characters. The second statement
follows from the Gaussian-dyadic sum-of-two-squares equation: after
removing the dyadic factor, an even exponent gives an axial Gaussian
integer and an odd exponent gives equal absolute real and imaginary
parts. Its fourth power has the displayed sign.

If `f = 1 mod 4`, the unique Pauli irreducible in the tensor power's
central sector is `V`. If `f = 3 mod 4`, it is the conjugate `Vbar`.
Therefore the honest quotient representation `W_f` satisfies

```text
V^(tensor f) = V    tensor W_f       when f = 1 mod 4,
V^(tensor f) = Vbar tensor W_f       when f = 3 mod 4.
```

Character division on the chosen lift gives, respectively,
`a^(f-1)` and `a^(f+1)/|a|^2`. In both cases,

```text
chi_(W_f)(s) = sigma^d 2^(p d),
dim(W_f) = 2^(8p).
```

In particular, the sign is positive at widths 15 and 17, and negative
at widths 13 and 19. Keeping the width-thirteen sign at every odd width
would give the wrong representation.

## 2. All spectral polynomials

The mathematical input is the ordinary `Sp(8,2)` character table through
[Nick Petalas's exact projection](https://github.com/petalas/integer-mult-bounds/blob/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine/PROJECTION.json).
Its retained source names the ATLAS and Thomas Breuer's CTblLib 1.3.11.
Let `e_j` be the degree of row `j`, and let `C_(j,d)` be the sum of
class size times that character over elements with fixed dimension `d`.
The projection supplies `d=1,...,7`. Identity gives `C_(j,8)=e_j`.
Character orthogonality gives

```text
C_(j,0) = |S| [j=1] - sum_(d=1)^8 C_(j,d),
|S| = 47,377,612,800.
```

These aggregate sums are real integers. The tensor multiplicity and
normalized projective Gram eigenvalue are

```text
m_j(f) = (1/|S|) sum_(d=0)^8 C_(j,d) sigma^d 2^(p d),
lambda_j(f) = |S| m_j(f) / (e_j 2^(8p)).
```

The projective regular block has dimension `(16 e_j)^2`. The eigenvalue
normalization is the same for `V` and `Vbar`. It follows either from
central convolution and the four scalar lifts, or from the retained
[width-thirteen normalization proof](https://github.com/aliromman/integer-mult-bounds/blob/1398fbdca3536389d8ac3c8b3aaa408f03e8f6c2/research/clifford-threshold-conditioning/PROOF.md).

Since `sigma^8=1`, define

```text
P_j(x) = sum_(r=0)^8 (C_(j,8-r)/e_j) x^r.
```

Then `lambda_j(f)=P_j(x)`. The first row has degree one and polynomial
`P`; the second row has degree 35 and polynomial `Q`.
The certificate records every coefficient of all 81 polynomials.

Two whole-polynomial checks verify the complete normalization. If `c_d`
is the number of symplectic elements with fixed dimension `d`, then

```text
sum_j e_j^2 P_j(x) = |S|,
sum_j e_j^2 P_j(x)^2 = |S| sum_(r=0)^8 c_(8-r) x^(2r).
```

The first is the normalized Gram trace. The second also follows directly
from Pauli lifts: each symplectic element has `2^(8-d)` nonzero projective
Pauli traces of squared modulus `2^d`. The checker compares every
coefficient, including the vanishing odd coefficients of the second
identity. This is stronger than checking these moments at a list of
widths.

## 3. Finite certificates for the infinite width range

For positive `x` in the actual domain, `0 < x <= 1/128`. For negative
`x`, `-1/64 <= x < 0`. The two finite interval statements are

```text
Q(x) < P_j(x) < P(x)       for 0 < x <= 1/128,
P(x) < P_j(x) < Q(x)       for -1/64 <= x < 0,
```

with only the designated endpoint row omitted from its own strict
inequality. Each pair of distinct endpoint rows occurs once. There
are 159 comparisons per interval, or 318 in total.

For each comparison `P_a < P_b`, substitute `x = sigma y/D`, where
`D=128` or `64`. All polynomials have constant term one. Hence

```text
P_b(sigma y/D) - P_a(sigma y/D) = y q(y),
degree(q) <= 7.
```

The certificate writes this quotient in the degree-seven Bernstein basis:

```text
q(y) = sum_(j=0)^7 b_j binom(7,j) y^j (1-y)^(7-j).
```

All 2,544 rational coefficients `b_j` are strictly positive. Their
minimum is `45984105/1073741824`. The basis terms are nonnegative and
sum to one on `0 <= y <= 1`. Therefore `q(y)>0`, and `y q(y)>0` for
`0<y<=1`. This proves every strict comparison on the complete intervals.
No subdivision, numerical roots or sampled sign checks are used.

Two further degree-eight Bernstein certificates prove positivity of
the lower endpoints themselves. Their least coefficients are
`470624175/4294967296` for `P(-y/64)` and
`75707742285/274877906944` for `Q(y/128)`. The checker expands every
deposited Bernstein expression back into the power basis and requires
exact coefficient equality. Merely supplying positive numbers does
not pass the check.

Since all other rows lie strictly between these two rows, their
regular dimensions give the exact endpoint eigenspace dimensions.
Equal eigenvalues among interior rows do not affect this conclusion.

## 4. Sharp stability contract and convergence

Write `alpha_f` and `beta_f` for the minimum and maximum in the result
table. For every complex coefficient vector `c`,

```text
alpha_f ||c||_2^2 <= ||A_f c||_2^2 <= beta_f ||c||_2^2.
cond_2(K_f) = beta_f/alpha_f.
cond_2(A_f) = sqrt(beta_f/alpha_f).
||A_f^+||_2 = 1/sqrt(alpha_f).
```

For observation `A_f c + e`, least-squares recovery has coefficient
error at most `||e||_2/sqrt(alpha_f)`, including errors outside the
column span. The endpoint eigenspaces show sharpness for the full
alphabet. Principal submatrices give the same valid bounds for every
subalphabet; sharpness for a proper subset is not claimed.

This result also determines the leading conditioning error. Put
`t=2^(-(f-1)/2)`. From `P(x)=1+255x+O(x^2)` and
`Q(x)=1-153x+O(x^2)`, either sign gives

```text
cond_2(K_f) = 1 + 408 t + O(t^2),
cond_2(A_f) = 1 + 204 t + O(t^2).
```

The limits hold along all odd widths, despite the change of endpoint
blocks. The constants are sharp asymptotic coefficients, not bounds
on the unspecified remainder at a fixed width.

## Evidence and limits

The unchanged threshold source checker runs in both registered modes.
It checks the retained projection, literal Bell/Pauli identities and
threshold certificate. This package also checks multiplicity
integrality, tensor dimensions and independent tuple-orbit norms at
all 35 odd widths from 13 through 81. Those finite evaluations check
the implementation; Sections 1--3 supply the infinite quantifier.

A separate literal calibration constructs all 24 one-qubit projective
Clifford operators and checks all 576 products. It checks the Pauli
quotient formula at 16 odd widths on every operator, or 384 complete
fibres. Four complete 24-by-24 Gram matrices at widths 13, 15, 17 and
19 have the predicted cubic annihilators and full spectral dimensions.
They cover all four odd residues modulo eight.

Controls reject a missing fixed-space term, wrong scalar normalization,
negative Bernstein coefficient, positive but incorrect certificate,
wrong endpoint row, even width and loss of the Gaussian phase.
All retained source bytes are authenticated. The full table archive is
not re-extracted here. No full four-qubit Gram matrix is materialized.
No full three-qubit or even-sector replay, Lean or Docker run is made.

These exact algebraic bounds do not supply native preparation, a
physical inverse, precision allocation, routing, owned-state recovery,
stock or a complete caller invoice. Those costs remain unknown. No
independent human or proof-kernel acceptance is claimed. All five
framework assumptions and the selected frontier remain unchanged.

## Open next questions

Construct and price a decoder that meets this exact stability contract.
Start with one specified caller, precision and owned-state interface.
The present result supplies no physical implementation cost.

The corresponding exact even-width endpoints remain open here.
Start with the quadratic-form stabilizer decomposition, rather than
substituting an even width into this odd-sector formula.
