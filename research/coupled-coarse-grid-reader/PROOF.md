# A coupled coarse-grid dirty reader: global error and precision

@CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.

This is a written mathematical proof in a specified integer word model. The
finite verifier is independent evidence for its identities and implementation;
it is not a formal proof assistant. No statement below grants productive
Gaussian target credit or changes a multiplication constant.

## 1. Scope and inherited mechanism

Fix

\[
 A=\begin{pmatrix}1&2\\-2&1\end{pmatrix},\qquad
 \operatorname{adj}A=\begin{pmatrix}1&-2\\2&1\end{pmatrix},\qquad \det A=5.
\]

This matrix is in the complete 625-matrix `[-2,2]` two-by-two census at
[Nick Petalas #6666](https://github.com/CrocSwap/integer-mult-bounds/pull/6666),
head `042b4ee85f64f4b3279426e2ed10191296448e6c`. It supplies a concrete retained
algebraic cut, not a literal cut of the native P104 caller. Its two rows and two
columns are genuinely coupled in this fixed coordinate chart.

[Ali Romman #1135](https://github.com/CrocSwap/integer-mult-bounds/pull/1135)
already supplies the rounded four-call dirty-borrowing endpoint and the generic
residue-image method. [Ali Romman #5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615)
supplies the exact dyadic Smith-factor capacity distinction. #6666 supplies
approximate dyadic algebraic response capacity and the four-shear restoration.
[ToikY #6685](https://github.com/CrocSwap/integer-mult-bounds/pull/6685), head
`9e6c76ebf56fcd968c1383f00688152114f9dc79`, supplies the sharp scalar coarse-grid
factor-three minimax. None of those mechanisms is claimed here as new.

The added result is a global optimization over **all** integer two-by-two lifts
for this retained cut, together with sharp Euclidean precision thresholds and
an explicit reversible implementation in fixed grids. The distinction between
one active residual row and two active rows creates the optimum.

Let `b >= 0`, `M = 2^b`, and `B >= 0` be integers. In units of a fixed coarse
spacing `gamma`, source `x` and destination `Y` are integer pairs; the helper
pair has spacing `gamma/M` and integer code `H`. Assume `|x_j| <= B`. The
incoming helper and destination are arbitrary dirty integers. They need not be
zero and are not available as scratch.

For an arbitrary integer lift matrix `L`, put

\[
 c=\lfloor M/2\rfloor,\qquad
 O_M(H)=\left\lfloor\frac{AH+c\mathbf1}{M}\right\rfloor,
 \qquad D=AL-MI.
\]

Floors are componentwise. This implements nearest rounding with ties toward
positive infinity. At `M=1`, all reader numerators are integers and the choice
`c=0` is the same rounding function. We restrict to the inherited four blocks

\[
 H\gets H+Lx;\quad Y\gets Y+O_M(H);\quad
 H\gets H-Lx;\quad Y\gets Y-O_M(H).
\]

Their endpoint is exactly

\[
 (x,H,Y)\longmapsto(x,H,Y+x+e_L(H,x)),\quad
 e_L(H,x)=O_M(H+Lx)-O_M(H)-x.                 \tag{1}
\]

The source and helper are restored. The error budget below is Euclidean on the
**original two coarse output coordinates**, without unpriced basis changes.
We optimize over `L`, keeping `A`, the source box, the grids, the rounding rule,
and the four-block architecture fixed. L need not itself be invertible: the
whole update is reversible because the source is preserved. For example, the
balanced lift at b=0 is zero and makes no output update. The error criterion
alone does not certify independent useful channel contributions.

## 2. Exact attainable errors

Set `r = (AH + c 1) mod M`, with `0 <= r_i < M`. The inherited floor-residue
identity gives

\[
 e_i=\left\lfloor\frac{r_i+(Dx)_i}{M}\right\rfloor.                 \tag{2}
\]

Because `gcd(5,M)=1`, multiplication by `A` is bijective on
`(Z/MZ)^2`: multiply by `adj(A)` and by the inverse of 5 modulo `M`.
Thus **every** phase pair `r` is attained, once per helper period. This step
licenses independent phase choices; it must not be silently applied to even
determinants.

Write `(Dx)_i = q_i M+s_i`, `0 <= s_i < M`, using Euclidean division, also
for negative values. Then `e_i` is `q_i` on `M-s_i` phases and `q_i+1` on
`s_i` phases. The full joint error set is the product of the nonempty choices,
and their counts over `H mod M` are the products of those counts. In
particular,

\[
 \max_H\|e_L(H,x)\|_2^2
 =\sum_{i=1}^2\left\lceil\frac{|(Dx)_i|}{M}\right\rceil^2.        \tag{3}
\]

For a negative displacement `-k`, the most negative endpoint is
`-ceil(k/M)`; positive and negative cases therefore have the same absolute
maximum. The two coordinate maxima can be attained simultaneously because
all phase pairs occur.

This section specializes #1135's generic method. The optimization in the next
section is the added claim.

## 3. The global minimax theorem

**Theorem.** For every integer `B >= 0` and `b >= 0`,

\[
 \boxed{\min_{L\in\mathbb Z^{2\times2}}
   \max_{H\in\mathbb Z^2,\,x\in[-B,B]^2\cap\mathbb Z^2}
   \|e_L(H,x)\|_2^2
 =\min\left\{\left\lceil\frac{3B}{M}\right\rceil^2,
              2\left\lceil\frac{B}{M}\right\rceil^2\right\}.}    \tag{4}
\]

The physical squared error is `gamma^2` times this value.

### 3.1 The residual lattice

An integer matrix `D` is attainable exactly when
`adj(A)(MI+D)` has every entry divisible by 5. The second row of `adj(A)` is
twice its first row modulo 5, so the complete condition is

\[
 d_{11}-2d_{21}\equiv-M\pmod5,\qquad
 d_{12}-2d_{22}\equiv2M\pmod5.                                  \tag{5}
\]

When it holds, `L=adj(A)(MI+D)/5` is an integer matrix realizing `D`.
`D=0` cannot satisfy (5), since 5 does not divide a power of two.

### 3.2 Lower bound when one residual row is nonzero

If only the top row `(u,v)` is nonzero, (5) forces
`u=-M mod 5`, `v=2M mod 5`. As `M mod 5` runs through `1,2,4,3`, the
least absolute representatives have magnitudes 1 and 2 in some order.
Thus `|u|+|v| >= 3`.

If only the bottom row `(u,v)` is nonzero, (5) instead forces
`u=3M mod 5`, `v=-M mod 5`; the same lower bound holds. Choose a source
corner with signs matching the nonzero row. Its residual displacement has
magnitude at least `3B`. Equation (3) gives worst squared error at least
`ceil(3B/M)^2`.

### 3.3 Lower bound when both residual rows are nonzero

For any two nonzero integer row vectors in two dimensions, some
`z in {-1,0,1}^2` has nonzero dot product with both rows. Indeed, if some column
has two nonzero entries, take its standard basis vector. Otherwise the two
nonzero row supports are disjoint, and their two standard basis vectors may
be added. Both products are nonzero integers and hence have absolute value
at least 1. Taking `x=Bz` in (3) gives worst squared error at least
`2 ceil(B/M)^2`.

The zero-row, one-row, and two-row cases exhaust the possibilities, proving
the lower bound in (4). For `B=0`, (1) has zero error directly.

### 3.4 Attaining both branches

Put `J=[[0,-1],[1,0]]`. A balanced residual is

| `b mod 4` | `M mod 5` | `D_bal` |
|---|---:|---|
| 0 | 1 | `-I` |
| 1 | 2 | `J` |
| 2 | 4 | `I` |
| 3 | 3 | `-J` |

Each satisfies (5). It is a signed permutation, so (3) gives exactly
`2 ceil(B/M)^2`, attained at a source corner and a suitable phase pair.

For a concentrated residual, let `u` and `v` be the unique representatives in
`{-2,-1,0,1,2}` of `-M` and `2M` modulo 5, and set

\[
 D_{\rm conc}=\begin{pmatrix}u&v\\0&0\end{pmatrix}.
\]

It satisfies (5), and `|u|+|v|=3`. The second output is exact for every dirty
helper. The first has worst residual displacement `3B`, so its squared error
is exactly `ceil(3B/M)^2`. Both residuals give integer lifts by Section 3.1.
Choosing the better one proves attainment in (4). No bounded search over `L`
is used in this proof.

For example at `M=8`, the balanced and concentrated lifts are respectively

\[
 L_{\rm bal}=\begin{pmatrix}2&-3\\3&2\end{pmatrix},\qquad
 L_{\rm conc}=\begin{pmatrix}2&-3\\4&2\end{pmatrix}.
\]

Their residuals are `-J` and `[[2,1],[0,0]]`. At `B=2`, both approximations
use the same grids; the first has worst squared error 2 and the second has 1.
The latter improves the global output budget by deliberately concentrating
coefficient residuals, not by reducing every coordinatewise coefficient error.

## 4. What shared precision buys

For `B >= 1`, the optimum is at least one coarse cell: every residual is
nonzero, a source in the box produces a nonzero integer displacement, and an
adversarial helper phase rounds it to a nonzero integer error. No finite
refinement makes the worst error strictly smaller than `gamma`.

The exact thresholds following from (4) are:

| Required worst Euclidean error | Necessary and sufficient precision |
|---|---|
| `< gamma` | impossible at finite `b` |
| `<= gamma` | `2^b >= 3B` |
| `<= sqrt(2) gamma` | `2^b >= B` |

In particular the least precisions are `ceil(log2(3B))` and
`ceil(log2(B))` for the last two rows. In integer code these are
`(3B-1).bit_length()` and `(B-1).bit_length()`.

For the middle row, the balanced branch is always at least 2 and the
concentrated branch is at most 1 exactly when `3B<=M`. For the last row, the
balanced branch is at most 2 exactly when `B<=M`; if `B>M`, it is at least 8
and the concentrated branch at least 16. These arguments include `B=1`.

Both helpers use the same precision and may have arbitrary, independent dirty
values. No selected phase correlation is assumed. This theorem optimizes a
shared precision `b` and `L`; it does **not** optimize unequal helper precisions,
the number of helper words, arbitrary nonlinear encodings, other rounding
rules, or unrestricted reversible circuits.

For the infinity norm, the same lattice and nonzero-row argument gives the
simpler optimum `ceil(B/M)`, attained by the balanced family. The Euclidean
law retains additional information lost by a coordinatewise maximum.

**Complex-linear lift corollary.** If the lift is additionally required to
commute with `J=[[0,-1],[1,0]]`, the sharp squared error is always
`2 ceil(B/M)^2`. Indeed `A` commutes with `J`, so `D=AL-MI` commutes with
`J` and has the form `[[a,-d],[d,a]]`. A nonzero such matrix has two nonzero
rows, giving the Section 3.3 lower bound. Every balanced residual and its
constructed lift commute with `J`, proving attainment. The concentrated
residual has one zero row and cannot commute with `J`. Consequently an
unrestricted one-cell improvement is unavailable under this extra lift
constraint for any finite precision and `B>=1`.

This corollary constrains the lift alone. It does not assert that ties-up
coordinate rounding, or the complete rounded word, has quarter-turn covariance.
A physical caller requiring such covariance needs a separate audit.

## 5. Smith factors alone do not determine fixed-chart error

Let

\[
 U=\begin{pmatrix}1&0\\2&1\end{pmatrix},\quad
 V=\begin{pmatrix}1&-2\\0&1\end{pmatrix}.
\]

Both are unimodular and `UAV=diag(1,5)`. For the diagonal reader
`S=diag(1,5)` with the **same coordinate box and Euclidean metric**, the
minimum worst error is

\[
 \left\lceil\frac{s_bB}{M}\right\rceil,\quad
 s_b=\operatorname{dist}(M,5\mathbb Z)
 =\begin{cases}1&b\text{ even},\\2&b\text{ odd}.\end{cases}      \tag{6}
\]

For every integer lift the `(2,2)` residual is `5L_22-M`, of absolute value
at least `s_b`; choose `x=B e_2` and an extremal helper phase for the lower
bound. The diagonal lift `diag(M, nearest(M/5))` attains it, with the first
output exact. This includes all off-diagonal lifts in the lower bound.

Thus at `M=2,B=2`, the coupled reader has squared optimum 2 while the
Smith diagonal has 4; at `M=4,B=2`, those values are 2 and 1. Neither fixed
chart uniformly dominates the other. Smith factors describe exact algebraic
capacity but do not preserve this source box and output geometry. Transporting
a result through `U,V` requires transporting the source domain, norm, rounding
boundary and the paid implementation of the basis changes as well.

## 6. Why the phase-image hypothesis is substantive

Take another member of the same census,
`C=[[1,1],[1,-1]]`, with `M=2`, `L=[[1,0],[2,0]]` and `x=(1,0)`.
Its residual displacement is `(1,-1)`, but its phase image is only
`{(0,0),(1,1)}`. Formula (2) gives exactly errors `(0,-1)` and `(1,0)`,
with squared norm 1. Replacing the actual image by independent coordinates
would falsely allow `(1,-1)`, with squared norm 2. The checker treats this
as a negative control, not an application of (4). The generic residue-image
principle remains #1135's contribution.

## 7. A reversible, fixed-grid logical lowering

The runtime roles are exactly `(x0,x1,h0,h1,y0,y1)`. A gate translates one
integer destination by a signed, non-mutating shifted view of a **different**
source word. A left shift is integer multiplication in the view; a right
shift is arithmetic floor division in the view. It never discards bits from
the source register. Constant translations are also allowed. Every such gate
is inverted by negating its translation, because its source remains unchanged.
All finite-word statements require the headroom below; wraparound is excluded
on the declared execution domain. If implemented with modular finite-word
translations, each gate is a permutation on the full word space and agrees
with the integer operation on that guarded domain.

For one positive reader call, first execute

```
h0 += 2*h1
h0 += c
y0 += floor(h0/M)
h0 -= c
h0 -= 2*h1
```

then

```
h1 -= 2*h0
h1 += c
y1 += floor(h1/M)
h1 -= c
h1 += 2*h0
```

The quotient additions read the arithmetic-right-shift view by `b` bits.
Each five-gate section restores the temporarily changed helper. Consequently
this reader implements exactly `Y += O_M(H)` and restores `H`. The negative
reader is the reverse gate list with opposite signs; it subtracts the
**same** rounded function, rather than evaluating rounding at a negated
argument. This distinction matters at half ties.

An integer lift coefficient is compiled from the binary expansion of its
absolute value. A set bit `k` generates the translation
`h_i += sign(L_ij) * (x_j << k)`. The source has coarse-grid code and the
helper fine-grid code; this realizes a physical helper displacement
`gamma Lx/M`. The inverse lift reverses the list and signs. No source scaling,
destructive shift, odd division, measurement, clean word or saved residue is
used at runtime. The division by 5 constructs compile-time integer constants
only.

Writing `P(L)=sum_ij popcount(|L_ij|)`, the whole four-block word uses:

| Resource | Exact logical bill |
|---|---:|
| Runtime integer roles | 6 |
| Clean scratch words | 0 |
| Source/helper words restored | 4 |
| Signed word ADDs, including quotient-view ADDs | `2P(L)+12` |
| Nonzero constant translations | `8` when `b>=1`, otherwise `0` |
| Quotient-view ADDs included above | 4 |
| Nonzero lift-bit ADDs included above | `2P(L)` |
| Reader helper shear ADDs included above | 8 |

A fixed shifted/sign-extended view is an explicit capability of this logical
word model. This bill does not assign zero physical price to arbitrary bit
access, interconnect, carries, sign extension or Boolean arithmetic. An actual
native implementation must supply and price these operations, as well as any
ownership or scheduling constraints. No Boolean-size optimum is claimed.

## 8. Uniform headroom for a declared input box

Let incoming bounds be `|H_i|<=h_i`, `|Y_i|<=y_i`, and `|x_j|<=B`. Define

\[
 F_i=h_i+B\sum_j|L_{ij}|,\quad
 W_i=\sum_j|A_{ij}|F_j,\quad G_i=W_i+c.
\]

Every lift prefix and completed inverse-lift prefix is bounded by `F_i`:
for each coefficient the binary terms have its sign, and a prefix/inverse
prefix is a subset of those terms added to incoming `H`. Reader temporary
helper values are bounded by `G_i`, while the other helper stays within `F`.
Thus helper guards `G_i` cover all stages and the quotient-view operands.

The first completed positive reader changes `Y_i` by at most
`R_i=floor((W_i+c)/M)`. Since each reader translates each output only once,
the only other possible changed output state is the final endpoint. Equation
(2) bounds its error by
`E_i=ceil(B sum_j |D_ij|/M)`, hence its absolute value by `y_i+B+E_i`.
Therefore a valid output guard is

\[
 T_{Y_i}=y_i+\max\{R_i,\ B+E_i\}.                              \tag{7}
\]

These bounds are sufficient rather than advertised as minimal widths.
The source guard is `B`; signed two's-complement width
`1+T.bit_length()` suffices for every register with absolute guard `T`.
The same guards cover the literal inverse circuit from a reached endpoint,
because it visits the forward states in reverse order.

No finite width covers unbounded dirty integers simultaneously. The arbitrary
integer theorem and the finite input-box headroom contract are distinct.

## 9. Evidence and remaining physical boundary

`verify.py` exhausts finite phase/source boxes, compares a separately coded
literal reader with the compiled reversible gates, verifies full error
histograms, enumerates all residuals capable of beating a known upper bound
in declared finite optimization cases, checks headroom, and runs failure
controls. The universal quantifiers in (4) are justified by Section 3, not
by extrapolating those finite cases. Source snapshots and replay receipts
have separate integrity checks; neither is mathematical proof.

The exact dyadic channel capacity of this Smith type is one, while its
approximate algebraic response rank is two. This result describes precisely
one rounded boundary at which those two approximate responses can have error
at most one coarse Euclidean cell, at shared precision `2^b>=3B`.
It does not show that the two responses are independent productive target
contributions in a multiplication schedule. Native availability, complete
producer/consumer ownership, actual caller tolerance, Boolean/movement cost,
and the whole signed paid-versus-productive invoice remain unproved. The
selected #6030 result and all five assumptions are unchanged.
