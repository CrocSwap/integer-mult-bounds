# Full ordinary Stein rank at three extremal source phases

## 1. Claim, source and boundary

Fix an integer `p >= 4096`. For `l = 0,1,2`, let `s_l` be distinct odd
primes, `s_l >= p^4`, and let `t_l` be powers of two satisfying

```
(1 - 1/(2p^2)) t_l < s_l <= (1 - 1/(4p^2)) t_l.
```

Let `alpha` be any common positive integer and put `a = pi alpha^2`.
The usual `alpha = ceil(sqrt((4/pi) ln(16p)))` is included. Retain the
literal column-normalized, unrounded, alias-deleted source array

```
q_j = floor(tj/s + 1/2),       beta_j = tj/s - q_j,
G_jk = exp(-a ((tk/s - q_j)^2 - beta_k^2)).
```

For each axis set

```
delta_l = t_l - s_l,          n_l = -(s_l - 1)/2,
i_l = delta_l^(-1) n_l mod s_l,   0 <= i_l < s_l.
```

These are the deterministic extremal indices of
[CrocSwap/integer-mult-bounds#7599](https://github.com/CrocSwap/integer-mult-bounds/pull/7599).
Let `C_l` be the selected principal two-point section on `i_l,i_l+1`,
and `C = C_0 tensor C_1 tensor C_2`. If `Z` is the ordinary eight-by-eight
lower one-step nilpotent shift, write `E(A) = A - Z A Z^T`.

**Theorem.** For every simultaneous permutation `P` of the eight vertices,

```
rank E(P C P^T) = rank E(P C^(-1) P^T) = 8.
```

The inverse is the inverse of the selected tensor, not a principal section
of a larger inverse. The theorem supplies **exact source-specific avoidance**
of singularity. It supplies no uniform lower determinant or singular-value
bound, and therefore no rounded-table, alias or `Cp`-bit robustness result.
All five foundational assumptions remain. No new kappa is claimed.

The new finite-dimensional algebraic step is a full-determinant certificate
for all eight-vertex orders, followed by the existing source-prime
specialization argument at degree eight. The general matching theorem in
[CrocSwap/integer-mult-bounds#7598](https://github.com/CrocSwap/integer-mult-bounds/pull/7598)
gives rank at least `2 ceil((8+3)/5) = 6`; it does not supply this full rank.

## 2. Legal source indices and directed exponents

Suppress an axis subscript. The centered integer
`n_j = t j - s q_j` runs through the balanced residues
`[-(s-1)/2,(s-1)/2]`, because `delta` is coprime to odd prime `s`.
There are no nearest-integer ties. The extremal residue has a same-cell
next step: `n_(i+1) = n_i + delta`, so `q_(i+1) = q_i + 1`.
Indeed `delta < s-1` follows from the fine interval.

Direct substitution in the literal coefficient formula gives

```
C_l = [[1,U_l],[V_l,1]],
U_l = exp(-a A_l/s_l),       A_l = 2 delta_l + 1,
V_l = exp(-a B_l/s_l),       B_l = 2 s_l - 1,
A_l + B_l = 2 t_l.
```

No diagonal similarity or phase/chirp normalization has been silently
discarded. If the selected `i` were `s-1`, its same-cell next step to
`j=s` would give `n_i=-delta`. Extremality would then force
`2delta+1=s`, whereas the fine interval gives `2delta+1<s`.
Thus `0 <= i <= s-2`; both selected indices are in the finite source list.
The corresponding target indices are also in `[0,t)`.

The fine interval implies

```
s/(4p^2) < delta <= s/p^2.
```

Consequently `A > p^2/2 > 8`, and

```
8 A + 8 = 16 delta + 16
          <= 16s/p^2 + 16
          <= s (16/p^2 + 16/p^4) < s.
```

For `0 <= u,v <= 8`, the residue `uA+vB mod s` equals
`uA-v mod s`. All unreduced values lie in `[-8,8A]`, an interval
of length `8A+8<s`. Equality of two residues therefore gives equality
of their unreduced values. Since `A>8`, the equation
`(u-u')A=v-v'` forces `u=u'` and `v=v'`.

This proves the required degree-eight exponent-box injection for every
axis, not just for the finite source fixtures in the verifier.

## 3. A finite polynomial certificate for all 40,320 orders

Introduce six independent indeterminates and form

```
H(U,V) = tensor_(l=0)^2 [[1,U_l],[V_l,1]].
```

Vertices use binary order `4 x_0 + 2 x_1 + x_2`.
For each of the `8! = 40,320` permutations `o`, let
`F_o(U,V) = det E(H[o,o])`. Each tensor entry is squarefree in each
individual variable. Each displacement entry is a difference of at most
two such monomials. The determinant expansion therefore gives an integer
polynomial of individual degree at most eight.

The following single integer specialization certifies that **every**
`F_o` is a nonzero polynomial:

```
(U_0,V_0,U_1,V_1,U_2,V_2) = (2,3,5,7,11,13).
```

`verify.py` enumerates the entire permutation domain and evaluates all
40,320 determinants modulo the prime `1000000007`; none is zero.
Primality is checked by exhaustive trial division through its integer
square root. Gaussian elimination uses field inverses and accounts for
row-swap signs. Its running invariant is ordinary determinant-preserving
row elimination. A nonzero residue implies a nonzero integer determinant,
which implies that the corresponding polynomial is not identically zero.

`review/check_integer.py` independently assembles the Kronecker matrix
and uses fraction-free integer elimination to check the same complete
order domain. It imports no primary-verifier code. These are two exact
arithmetic algorithms, not a formal-kernel proof or independent human
review. A separate orchestration review is recorded when completed.

The integer witness is an algebraic test point, not a physical Gaussian
source. Its role is solely to certify polynomial nonidentity. The proof
of transfer to physical coefficients is the next section. A finite
enumeration is complete here because the only enumerated domain is the
fixed, finite set of eight-vertex orders.

## 4. Pointwise transfer to every admitted distinct-prime source triple

Set

```
S = s_0 s_1 s_2,              z = exp(-pi alpha^2/S),
U_l = z^(A_l S/s_l),          V_l = z^(B_l S/s_l).
```

Consider two monomials of one `F_o`. All their variable exponents lie
between zero and eight. If substitution gives the same total integer
exponent of `z`, reduce that equality modulo `s_l`. Every other axis
contributes a multiple of `s_l`, while `S/s_l` is a unit modulo
`s_l`. We obtain

```
A_l (u_l-u'_l) + B_l (v_l-v'_l) = 0 mod s_l.
```

The injection proved in section 2 forces equality of both exponents
on every axis. Thus different monomials remain different powers of
`z`: the specialized polynomial is a nonzero integer polynomial.

By the classical Gelfond-Schneider theorem, `z` is transcendental.
Take the algebraic base `-1`, the logarithm `i pi`, and algebraic
irrational exponent `i alpha^2/S`. This value of the power is exactly
`exp(-pi alpha^2/S)`. The base is neither zero nor one and the exponent
is nonreal and hence irrational. The exact same classical input and
branch choice are used in #7598; no quantitative transcendence measure
is being invoked.

The nonzero polynomial cannot vanish at `z`. Hence
`det E(P C P^T) != 0` for every order. The source selector is chosen
before, and works for, all orders.

## 5. Inverse transfer with reversal charged explicitly

Each factor is invertible because
`U_l V_l = exp(-2a t_l/s_l) < 1`. In fact
`det C = product_l (1-U_l V_l)^4 > 0`.

For any invertible square `A`, compare the two determinant Schur
complements of

```
[[A,Z],[Z^T,A^(-1)]].
```

They give

```
det E(A) = (det A)^2 det E_rev(A^(-1)),
E_rev(B) = B - Z^T B Z.
```

Applying this identity to `A^(-1)` yields

```
det E(A^(-1)) = det E_rev(A)/(det A)^2.
```

If `J` reverses the order, then
`E_rev(A) = J E(J A J) J`. Order reversal is included in the
40,320-order theorem. Therefore the numerator is nonzero for every
`A=P C P^T`, proving full inverse displacement rank.

This argument neither assumes that Stein rank is invariant under an
arbitrary diagonal similarity nor substitutes the inverse of a selected
section for a section of the full source inverse.

## 6. Strict interior box counterexample

The obstruction to a parameter-box proof is stronger than the
`U=1` boundary example in #7599. Let
`B=[[1,u],[v,1]]`, with any `0<u<1` and `0<v<1`, and put
`H=B tensor B tensor B`. In order

```
o = (0,1,2,4,6,5,3,7)
```

the ordinary Stein displacement has columns 2 and 3 equal, and
columns 5 and 6 equal (zero-based indexing). Equivalently its kernel
contains the two independent vectors `e_2-e_3` and `e_5-e_6`.
This follows by comparing the bivariate monomials in each of the eight
entries of each column pair. The verifier checks the symbolic
coefficient identities; the identities do not depend on numerical
sampling.

For example `u=2047/2048`, `w=1/4096`, `v=3/8192` lies strictly below
`U=1` and within the predecessor's asymmetric box. Its displacement
has rank at most six. Arbitrarily small unequal perturbations of these
equal factors can approach this singular point, so mere distinctness
of unrestricted real factors cannot yield a positive uniform margin
over that box either.

These equal factors are **not** an admitted triple of distinct-prime
source factors. In the actual family,
`V_l=exp(-a(2-1/s_l))` is a strictly monotone function of `s_l`,
so distinct source primes give distinct reverse coefficients.
The precise pointwise exclusion nevertheless uses all six-variable
exponent separation from section 4, rather than relying only on that
pairwise distinction.

## 7. Representation consequence and costs

For the exact ordinary representation
`A=sum_(j=1)^k L(g_j) U(h_j)`, using lower and upper triangular
Toeplitz matrices, `E(A)=sum_j g_j h_j^T`. Thus every order of
`C` and `C^(-1)` requires at least eight terms. Eight terms
also suffice for every eight-by-eight matrix by a rank decomposition
of `E(A)` and inversion of the finite Stein sum, so the exact
minimum here is eight.

A format storing all two length-eight generator vectors separately
therefore uses at least 128 scalar slots. This concerns that specific
dense generator format. It is not a lower bound for implicit tensor
descriptions, circuits, general algorithms, time or total memory.

The selector uses three modular inverses and fixed-many integer
operations on `O(log s_max)`-bit integers. Extended Euclid and
schoolbook arithmetic give a conservative
`O((log s_max)^3)` bit-operation bound and
`O(log s_max)` local scratch, plus explicitly charged inputs and
the three output indices. It does not produce any coefficient table,
inverse, generators or full caller.

## 8. Remaining quantitative question

Exact nonvanishing gives no usable lower margin by itself. The proof
does not show that aliases or coefficient errors smaller than
`2^(-Cp)` preserve rank. The strict interior counterexample explains
why the entire predecessor box cannot provide such a bound even after
excluding its `U=1` face.

A useful next task is to bound determinants along the actual
distinct-prime source curves near those singular equal-factor points,
including their prime-spacing and dyadic-target constraints. That task
must pay inverse conditioning, tensor entry errors, alias tails and any
coefficient production. The fixed three-axis exact result does not
extend automatically to growing dimension.

Credit #7598 for source-phase exponent separation and the classical
specialization method; #7599 for the extremal selector and the
quantitative two-axis source theorem; #7600 for its distinct local
coefficient-production result. Chafik Boukhalfa, Vlado Vojdanovski,
IdeaOuter, Jeremy Kothe and the retained bilateral/framework lineage
retain their credit. Prepared for Jerry Chen / @CubeJerry with
substantial OpenAI assistance. Apache-2.0.
