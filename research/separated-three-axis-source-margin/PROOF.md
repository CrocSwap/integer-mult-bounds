# A quantitative three-axis source margin with separated fine primes

## 1. Exact scope

Let `p >= 4096` be an integer and `t` a power of two. Let
`s_0,s_1,s_2` be distinct odd primes satisfying

```
s_l >= p^4,
(1 - 1/(2p^2)) t < s_l <= (1 - 1/(4p^2)) t,
|s_l-s_m| >= t/(32p^2)          for l != m.              (1)
```

All three axes have the **same dyadic target**. The separation in (1)
is an additional hypothesis; this theorem does not cover arbitrary
distinct source primes, including closely spaced triples.

Use the retained source parameters

```
L = ln(16p),   alpha = ceil(sqrt(4L/pi)),
a = pi alpha^2,             w = exp(-2a).
```

On every axis choose the extremal same-cell starting index from
CrocSwap/integer-mult-bounds#7599:
`i_l=(t-s_l)^(-1)(-(s_l-1)/2) mod s_l`.
The literal unrounded, alias-deleted source sections are

```
C_l = [[1,U_l],[V_l,1]],
U_l = exp(-a (2(t-s_l)+1)/s_l),
V_l = exp(-a (2s_l-1)/s_l),
C = C_0 tensor C_1 tensor C_2.                          (2)
```

Binary vertex `(x_0,x_1,x_2)` has index `4x_0+2x_1+x_2`.
Fix the order and its reverse

```
o = (0,1,2,4,6,5,3,7),     rev(o) = (7,3,5,6,4,2,1,0),
E(A) = A - Z A Z^T,
D = a^3 w^2/(2^16 p^6),                                (3)
```

where `Z` is the ordinary eight-by-eight lower one-step shift.

**Theorem.** In each of these two orders,

```
|det E(C)| >= D,
sigma_min(E(C)) >= 2^-21 D,
sigma_min(E(C^(-1))) >= 2^-49 D.                        (4)
```

Ordering is understood in each occurrence of `C` in (4).
If each factor entry has an arbitrary complex perturbation of
magnitude at most `2^-71 D`, the tensor of the perturbed factors
is invertible and the two corresponding displacements retain
singular-value lower bounds `2^-22 D` and `2^-50 D`.

Matched periodic aliases plus a further factor-table error at most
`2^-73 D` also meet this contract. A sufficient precision for the
further periodic-factor error is

```
b >= ceil(233 + 42 log2 p).                             (5)
```

In particular `b=p` suffices throughout the stated range.
The inverse is of the selected tensor, not a selected section of
the full source inverse. The theorem concerns **two explicit orders**,
not all 40,320 orders. It does not implement a table producer or
complete caller, discharge a foundational assumption, or improve kappa.

The order in (3) is singular for all repeated factors
`[[1,u],[v,1]] tensor 3`, even with strict positive decays. Its
displacement has equal column pairs (2,3) and (5,6). The new source
separation is what supplies a quantitative margin for this order.

## 2. An exact determinant decomposition

For independent variables write

```
H = [[1,u],[v,1]] tensor [[1,x],[y,1]]
                         tensor [[1,r],[z,1]],
F = det E(H[o,o]).
```

Give `v,y,z` degree one and `u,x,r` degree zero. Exact expansion
has no term of degree zero or one. Its degree-two part is

```
F_2 = (u-r)(ur+x^2)(xy-uv)(xy-rz).                      (6)
```

All other terms have total lower-entry degree at least three.
The complete coefficient counts and absolute coefficient masses are:

| Lower-entry degree | Nonzero terms | Absolute coefficient mass |
| --- | ---: | ---: |
| 2 | 16 | 16 |
| 3 | 165 | 224 |
| 4 | 580 | 1246 |
| 5 | 1029 | 3658 |
| 6 | 1425 | 7104 |
| 7 | 1532 | 8878 |
| 8 | 1313 | 7410 |
| 9 | 889 | 4070 |
| 10 | 437 | 1370 |
| 11 | 134 | 246 |
| 12 | 9 | 16 |

There are 7,529 nonzero terms. The exact weighted mass of degrees
at least three is

```
sum_(d>=3) 2^d sum_(degree(m)=d) |coefficient(m)|
    = 7,682,848 < 2^23.                                (7)
```

The primary verifier derives every coefficient by subset determinant
recursion. A separate checker uses literal Leibniz permutations and
packed monomial exponents: 16,687 nonzero permutation products expand
to 1,186,624 signed monomials before collection. The two complete
coefficient dictionaries agree. This is exhaustive fixed-dimensional
algebra, not interpolation from sampled parameter values.

To bound the whole polynomial, suppose

```
3/4 <= u,x,r <= 1,      w <= v,y,z <= 2w,       0<w<=1,
|u-r| >= h,
|xy-uv| >= wh,          |xy-rz| >= wh,
w <= h^3/2^24.                                         (8)
```

Then `ur+x^2 >= 2(3/4)^2 > 1`, so
`|F_2| >= h^3 w^2`. By (7), the remaining polynomial
has absolute value at most `2^23 w^3 <= h^3 w^2/2`.
Therefore

```
|F| >= h^3 w^2/2.                                      (9)
```

No sign of the prime ordering is assumed. The argument uses an
absolute lower bound for the leading factor and pays all possible
sign cancellation from the remainder.

## 3. Actual separated source factors satisfy the gap conditions

The source selector, finite-grid legality and coefficient identities
in (2) are exactly those in #7599; no similarity or physical
phase/chirp coefficient is discarded. Its elementary bounds give

```
4 ln(16p) <= a <= 9 ln(16p) <= 9p/8,
1023/1024 <= U_l <= 1,       w <= V_l <= 2w,
w <= (16p)^-8.                                         (10)
```

For completeness the upper-entry exponent is at most
`a(2/p^2+1/p^4) <= 27/(8p) < 2^-10`, and
`V_l=w exp(a/s_l)`. Thus `exp(-x)>=1-x` and
`exp(x)<=1/(1-x)` give the stated box. The alpha bound follows
from `ln(16p)>=pi` and
`a <= 4L+4sqrt(pi L)+pi <= 9L`.
Also `p/8-ln(16p)` is increasing for `p>=4096` and at
4096 exceeds `512-16>0`, since `ln2<1`. This proves the
uniform bound `L<=p/8` used in (10).

Put `rho_l=t/s_l` and `q_l=U_l V_l=exp(-2a rho_l)`.
Because all three targets equal `t`, (1) gives

```
|rho_l-rho_m| = t |s_l-s_m|/(s_l s_m)
              >= 1/(32p^2).                            (11)
```

Over the interval between any two source ratios,
`1<rho<=1+1/p^2`, and

```
U(rho)=exp(-a((2+1/t)rho-2)),
q(rho)=exp(-2a rho).
```

The first derivative has magnitude at least `a`, since
`U>=3/4` and `2+1/t>=2`. For the second,
`exp(-2a rho)>=w/2`: indeed
`2a/p^2<=9/(4p)<1/2` and `exp(-x)>=1-x`.
Its derivative therefore has magnitude at least `aw`.
The integral mean-value estimate and (11) show

```
|U_l-U_m| >= h,         |q_l-q_m| >= wh,
h = a/(32p^2).                                        (12)
```

Finally `a>=1` and (10) imply

```
w <= 2^-32 p^-8 <= a^3/(2^39 p^6) = h^3/2^24,
```

because `p^2 a^3 >= 2^7` in the stated range. All conditions
of (8) hold, and (9) gives the determinant bound `D`.

The reverse order satisfies the same bound. It equals the original
order after interchanging the first and third bit axes and complementing
all three bits. Complementing all bits transposes the tensor with
its directed factors; the determinant of its Stein displacement
equals that of the untransposed matrix. Hence the reverse-order
polynomial is obtained from `F` by exchanging the outer factor
pairs. This changes the sign of (6), but leaves all absolute
bounds and the remainder mass unchanged. The verifier checks the
full polynomial identity, not just the vertex relation.

## 4. Singular-value and inverse bills

Every tensor entry in (2) lies in `(0,1]`, and each displacement
entry has absolute value at most one. Thus `||E(C)||_2<=8`.
The product of the eight singular values is the determinant magnitude,
which proves the forward lower bound `D/8^7 = 2^-21 D`.

Every factor has `0<U_l V_l<=2w<1/2` and inverse

```
(1-U_l V_l)^(-1) [[1,-U_l],[-V_l,1]].
```

Its Euclidean norm is at most four, so
`||C^(-1)||_2<=64`, `||E(C^(-1))||_2<=128`, and
`0<det C=product_l(1-U_l V_l)^4<=1`.

For every invertible `A`, the two determinant Schur complements of
`[[A,Z],[Z^T,A^(-1)]]`, followed by the same identity with
`A` replaced by `A^(-1)`, give

```
det E(A^(-1)) = det E_rev(A)/(det A)^2,
E_rev(A)=A-Z^T A Z = J E(J A J) J,                      (13)
```

where `J` reverses order. Since both orders have the lower bound
`D`, the inverse determinant has magnitude at least `D`.
The inverse singular-value bound is therefore
`D/128^7 = 2^-49 D`. No arbitrary diagonal-similarity invariance
or symmetry premise is used.

## 5. Complete tensor and inverse perturbation allowance

If an eight-by-eight matrix perturbation has maximum entry magnitude
`epsilon`, its operator norm is at most `8epsilon`, and its
Stein displacement norm is at most `16epsilon`.
Take

```
epsilon <= 2^-68 D.                                    (14)
```

Here `D<1`, for example from `a<=9p/8`, `w<=1`
and the definition (3). Hence
`||C^(-1) F||<=512epsilon<1/2`. Neumann inversion gives

```
||(C+F)^(-1)-C^(-1)|| <= 2*64^2*8epsilon
                       = 2^16 epsilon.
```

Its inverse displacement changes by at most `2^17 epsilon`,
which is at most one quarter of `2^-49 D`. The forward change
is also less than half its proved margin. The more conservative
retained bounds are `2^-22 D` forward and `2^-50 D` inverse.

If instead each of the three factor tables has entry error at most
`zeta<=1`, exact tensor formation has entry error at most
`(1+zeta)^3-1<=7zeta`. Thus

```
zeta <= 2^-71 D                                        (15)
```

suffices for (14). Additional rounding while forming or inverting the
tensor needs its own error and cost account. The inverse in this
claim is the exact inverse of the tensor of the perturbed factors.

By (10),

```
D = a^3 exp(-4a)/(2^16 p^6)
  >= 2^-16 (16p)^-36 p^-6
  = 2^-160 p^-42.                                      (16)
```

Therefore factor-table error `2^-b` meets (15) whenever
`b>=ceil(231+42log2 p)`. Section 6 uses two additional bits
for aliases and further periodic-table error.

## 6. Matched periodic sections

The exact source periodization is
`N(j,k)=sum_(m in Z) G_(j,k+ms)`. At the selected adjacent pair,
`|rho k-q_j|<=3/2` and `|beta_k|<=1/2`. The direct alias
argument from #7599 therefore gives the factor entry bound

```
|N(j,k)-G(j,k)| <= 4 exp(-a t^2/8).                     (17)
```

The source-size guard here implies the stronger allowance

```
4 exp(-a t^2/8) <= 2^-73 D.                            (18)
```

Indeed the ratio of the left side to `D` is
`2^18 p^6 a^(-3) exp(-a(t^2/8-4))`. For `p>=4096`,
`t>=s_l>=p^4`, `a>=1`, and

```
a(t^2/8-4) >= p^8/8-4 >= p^2
           >= 91 ln 2 + 6 ln p - 3 ln a.
```

The last inequality follows from `ln2<1`, `ln p<=p`,
`ln a>=0` and `p^2>=91+6p` for `p>=16`.
This proves (18), including the powers of two.

A further periodic-factor error at most `2^-73 D` leaves total
factor error at most `2^-72 D < 2^-71 D`, so the same tensor
and inverse conclusions apply. Equation (16) yields (5).
At `p=4096`, its right side is 737. The difference
`p-233-42log2 p` is increasing thereafter, since
`ln2>1/2` gives derivative at least `1-84/p>0`.
Thus `p` bits suffice, and any fixed positive `Cp` bits
suffice eventually.

The periodic factors are the selected sections of the matched
periodized source; their tensor inverse is not a section of the
full periodized inverse. No existing production routine is silently
identified with this matrix or credited with the error allowance.

## 7. Feasibility and paid selection of separated source triples

The added source hypothesis is nonempty. For `p=4096`,
`t=2^64`, exact Proth-style certificates in the verifier establish

```
s_0 = 18446743751587004417 = 4294967221 * 2^32 + 1,
s_1 = 18446743674277593089 = 4294967203 * 2^32 + 1,
s_2 = 18446743541133606913 = 1073741793 * 2^34 + 1.
```

Witnesses 3,3,5 have `a^((s_l-1)/2)=-1 mod s_l`;
the odd multipliers are less than the corresponding powers of two.
Every prime divisor then exceeds `sqrt(s_l)`, proving primality.
The exact interval and separation guards also pass. These fixtures
establish the local family, not a complete outer production instance.

For the retained eventual scale
`log t=Theta(p^(1-epsilon))`, fixed `0<epsilon<1`,
apply the same classical prime-count estimate used by the source
to three subintervals:

```
I_0=((1-19/(64p^2))t, (1-17/(64p^2))t],
I_1=((1-25/(64p^2))t, (1-23/(64p^2))t],
I_2=((1-31/(64p^2))t, (1-29/(64p^2))t].
```

Each has length `t/(32p^2)`, lies inside the fine-prime interval,
and is separated from its neighbors by at least `t/(16p^2)`.
The logarithmic-integral main term is at least
`t/(32p^2 log t)`. The exact primary input is
[Trudgian, theorem 2](https://arxiv.org/html/1401.2689v2#S2):

```
|pi(x)-li(x)| <= 0.2795 x (ln x)^(-3/4)
                         exp(-sqrt(ln x/6.455)),   x>=229.
```

Let `ell=ln t`. All six endpoints lie in `[t/2,t]`.
For `t>=458`, `ln(t/2)>=ell/2`, so the sum of two endpoint
errors is at most

```
2 t ell^(-3/4) exp(-sqrt(ell/12.91)).
```

Here `2*0.2795*2^(3/4)<2` pays the constant.
The ratio to the main term is at most
`64 p^2 ell^(1/4) exp(-sqrt(ell/12.91))`.
If fixed positive `c_1,c_2` satisfy
`c_1 p^(1-epsilon)<=ell<=c_2 p^(1-epsilon)`, the logarithm
of this ratio is at most

```
O(ln p) - sqrt(c_1/12.91) p^((1-epsilon)/2),
```

which tends to minus infinity.
Each interval therefore contains a prime eventually; those primes
also satisfy `s_l>=p^4` eventually. This is an eventual statement
whose threshold can depend on `epsilon,c_1,c_2`. It does not assert
availability for every `p>=4096` or provide a practical threshold.
It applies the retained unconditional analytic theorem to smaller
fixed-fraction intervals.

Scanning the three intervals and using trial division costs at most
`O(t^(3/2) poly(log t))` bit operations with logarithmic local
arithmetic scratch and the inputs/outputs charged. At the retained
scale its logarithm is `o(p)`. Selecting the three extremal indices
adds fixed-many modular inverses and polynomial bit work in
`log t`. Coefficient construction, table transport, inversion,
storage histories and full-caller amortization remain separate.

## 8. Limitations and credit

This proves a quantitative source-specific result for a strict-box
singular order and its reverse under explicit prime separation.
The exact all-order companion theorem does not transfer these
two-order margins to every order. Close distinct primes, differing
dyadic targets, growing dimensions and full analytic recovery remain
open.

Credit #7599 for the extremal selector, two-axis source bounds,
alias estimate and inverse-error framework; #7598 for the separate
exact source specialization argument; #7600 for its local two-axis
coefficient adapter; Chafik Boukhalfa, Vlado Vojdanovski, IdeaOuter,
Jeremy Kothe and the retained bilateral/framework lineage.
The prime-count input is Tim Trudgian, *Updating the error term in
the prime number theorem*, arXiv:1401.2689v2, theorem 2.
The determinant, norm, Neumann and Schur facts are classical.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI
assistance. No new kappa, discharged foundational assumption,
human peer review or formal-kernel acceptance is asserted.
Apache-2.0.
