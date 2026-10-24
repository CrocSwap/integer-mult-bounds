# Accuracy of the actual five-stage expansion at computed inputs

This independently audits the accuracy handoff in JoyboyBrian's
[PR5056](../tensor-internal-contraction/README.md), head
`fe624453057b7f0cb42870a594d314a148b9fb84`. That result supplies the actual
staged norm invariant and coordinate binding, but explicitly leaves this
accuracy telescope open. The audited implementation is Jose Manuel's
[physical expansion](../physical-gaussian-expansion/PROOF.md), retained at
`1a86a8fb73bb7a0982fff99852a031832c191902`, as called by
`physical-gaussian-tensor/tensor_engine.py`.

The contribution is an exact five-residual identity, its independently
derived error bounds, and the computed-input tensor telescope. It retains
the source coefficient-enclosure and exact primitive contracts explicitly.
It stops at the expansion output before chirp. No precision change, new
supplier, physical speedup or selected-frontier change follows.

## 1. Local interface and retained premises

Consider one source-produced block with input precision `p`, work precision
`P`, scale `sigma`, source length `n`, target length `m`, and
`P>=p+2sigma`. Set `Q=2^P`, `eta=1/Q`, `h=2^-p`, and `lambda=2^(2sigma)`.
The input is a complex p-grid line `x_j=v_j/2^p`, `0<=j<n`, of norm at most
`R<=1`. Integer numerators below are complex pairs, with truncation applied
separately to their signed real and imaginary components.

The stored nonnegative integer factors are `A_j,K_l,B_z,C`. Write their
normalized values as `a_j=A_j/Q`, `k_l=K_l/Q`, `b_z=B_z/Q`, `c=C/Q`.
The source checks `a_j,k_l,b_z in [0,1]` and `0<c<=1/4`.
Retain exact promotion, signed products, packed convolution separation,
crop semantics and record ownership. PR5056 derives the actual internal
operand and work-record headroom from these premises; finite examples do
not replace the primitive's all-size correctness or cost contract.

For comparison with the true Gaussian, additional premises are necessary:
the page comes from the matching original-coordinate producer; its true
normalized factors `a*_j,k*_l,b*_z,c*` lie in the same ranges; the first
three factor errors are strictly below `4eta`, and `|c-c*|<eta`.
Here `c*=1/(2alpha)`. These are the retained directed-interval/reciprocal
contracts, not consequences of the page's syntax or positivity checks.
In the actual `prepare_page` path, the stored factors are the downward
enclosure endpoints (or exact unit factors). The certified `grid_interval` upper
endpoint is checked against `Q`; this supplies the **true** factor upper
bound, not just the stored-value bound. Its enclosure width is at most
three grid units, supporting the retained strict `4eta` allowance. The
normalization is the exact quotient `floor(Q/(2alpha))/Q`. The exact
stored-factor identity below does not require these analytic premises.

## 2. The five residuals and their exact transport

Let `T_q(v)=sign(v) floor(|v|/2^q)` for an integer component and `q>=0`.
The actual `Block.scalar` and convolution owner execute

```text
w_j = T_P(A_j 2^(P-p) v_j),
y_l = T_P(sum_j K_(l-j) w_j),
z_z = T_P(B_z y_(n-1+z)),
f_z = T_P(C z_z),
o_z = T_(P-p-2sigma)(f_z).
```

Only valid kernel indices participate in a convolution coefficient. In the
cropped coefficient `l=n-1+z`, every `j=0,...,n-1` has a valid index in
`[0,n+m-1)`. The complete convolution is rounded before cropping; no
earlier restriction of the source or its signed sum is assumed.

Define the dimensionless complex residuals at their actual computed operands:

```text
rho1_j = w_j - Q a_j x_j,
rho2_z = y_(n-1+z) - sum_j k_(n-1+z-j) w_j,
rho3_z = z_z - b_z y_(n-1+z),
rho4_z = f_z - c z_z,
rho5_z = o_z - 2^(-P+p+2sigma) f_z.
```

Every component of every residual has absolute value strictly below one;
if a shift is zero its residual is zero. This follows directly from signed
truncation toward zero and is valid for both signs. Thus each complex
residual has modulus strictly below `sqrt(2)`.

Let the exact stored-factor row be

```text
(W x)_z = lambda c b_z sum_j k_(n-1+z-j) a_j x_j.
```

Substituting the five defining equalities, without any approximation, gives

```text
o_z/2^p - (W x)_z
 = lambda eta [c b_z sum_j k_(n-1+z-j) rho1_j
               + c b_z rho2_z + c rho3_z + rho4_z]
   + h rho5_z.                                             (1)
```

This is an identity for the executed nonlinear arithmetic. In particular,
the fine-normalization residual `rho4` is amplified by `lambda eta`, whereas
the last extraction residual `rho5` is measured on the final p-grid.
Combining them into one unamplified rounding allowance is invalid.

The coefficients in the bracket are nonnegative and have total at most

```text
c b_z sum_j k_(n-1+z-j) + c b_z + c + 1 <= (n+6)/4.
```

Consequently the stored-map rounding error satisfies

```text
|o_z/2^p - (W x)_z|
 < sqrt(2) [h + lambda eta (n+6)/4].                         (2)
```

Equation (1), rather than a fitted bound, is the finite check's target.
It also separates all five local error sources when small final errors
or signed cancellation would conceal an omitted intermediate contribution.
No rounded-map linearity or Lipschitz statement is used.

## 3. Stored coefficients, original indices, and production tails

For one true/stored coefficient product, telescope the four factors:

```text
c b k a - c* b* k* a*
 = (c-c*) b* k* a*
   + c (b-b*) k* a* + c b (k-k*) a* + c b k (a-a*).
```

The range and interval premises in §1 give absolute value below
`eta + 3*(1/4)*4eta = 4eta`. Therefore, for a complex input of norm `R`,
the stored row differs from the exact retained-window Gaussian row by
at most `4n R lambda eta`, strictly less when `R>0`. At `R=0` both rows
vanish. There is no additional `sqrt(2)` in this
term: a real coefficient multiplies a complex input with `|x_j|<=R`.
Together with (2), the finite-window defect is strictly below

```text
sqrt(2) h + lambda eta [sqrt(2)(n+6)/4 + 4nR].                (3)
```

The original-coordinate identity is essential. For block target start `v0`,
put `kappa=s/t`, `j0=floor(kappa v0)`, `gamma=j0-kappa v0`,
and `h_j=hlo+j`. The borrowed source value is
`x((j0+h_j) mod s)`, including all retained windings. Kernel slot `r`
has difference argument `-hhi+r`. At slot `n-1+z-j` this becomes
`z-h_j`, because `n-1=hhi-hlo`. The three exact quadratic exponents
therefore sum to `(j0+h_j-kappa(v0+z))^2/alpha^2`. Their two normalized
diagonal factors contribute `2^(-2sigma)`, cancelled by exactly `lambda`.
Thus the true row in (3) is the declared window of `S/2`, not an arbitrary
positive matrix or a row with a shifted crop.

For the production case, take the original hypotheses
`p>100`, `2<=alpha<sqrt(p)`, `u=alpha^2`, `1<t/s<2`, and
`r=alpha ceil(sqrt(p))`. The source block has `1<=m<=r`,
`hlo=-r-1` and `hhi=ceil(kappa(m-1)-gamma)+r+1`.
Every omitted source index is farther than `r` from the target center.
For either tail, monotonicity bounds its discrete Gaussian sum by its
first term plus the corresponding integral. The elementary integral bound
`integral_r^infinity exp(-pi x^2/u) dx <= u exp(-pi r^2/u)/(2pi r)`
then gives the normalized two-tail defect at unit input at most

```text
(1/alpha + alpha/(2pi r)) exp(-pi r^2/u)
 < exp(-pi p) < 2^(-3p) < 2^(-p-12).                        (4)
```

Here `r^2/u>=p`, and the prefactor is below one since `alpha>=2` and
`ceil(sqrt(p))>=11`. Periodicity does not eliminate repeated residues:
their positive Gaussian weights all remain in this sum. For norm `R`,
the tail allowance is multiplied by `R`. This argument relies on the
production window and cannot be applied to the reduced-halo p48 fixture.

The actual `compile_frame` work-width guard requires

```text
P >= 2sigma+p+ceil(log2(32(n+1)))+12.
```

For `R<=1`, the bracket in (3) is less than `32(n+1)`. Hence the internal
term in (3) is strictly below `2^(-p-12)`. Production values
`P=32768p`, `sigma=4096p` satisfy this guard: the source geometry gives
`n<=2r+m+3<4p`, and `ceil(log2(32(n+1)))<=p` for integer `p>=101`.
The latter follows, for example, from `32(n+1)<=160p<=2^p`, with the
last inequality established at `p=16` and preserved by induction.
Combining (3) and (4) independently recovers the production local bound

```text
||computed block - (S/2) block||_infinity
 < (sqrt(2)+2^-11) 2^-p.                                   (5)
```

The normalization, interval and exact primitive premises remain explicit;
this does not independently validate the exponential or packed-word backend.

## 4. Complete axes and a telescope at computed inputs

Within an axis, the actual Tile checks successive target starts and lengths,
so its blocks partition the target interval exactly once. Taking the maximum
of their local defects gives an axis allowance `delta_i`; summing over the
number of blocks would overcharge a sup-norm error. The declared original
halo values, zero-padding checks, complete spectator lines and final natural
gather are the interfaces audited in PR5056. Exact copies and permutations
do not enlarge the norm or error. A halo repeats values rather than adding
them. Zero extension on another axis commutes with this zero-preserving
computed map by coordinate selection, not by additivity.

Let `A_i` be the exact original-coordinate `S_i/2` map, and let
`Etilde_i` be the actual computed axis map in the retained order
`i=0,...,D-1`. The shapes and parameters may differ by axis. Retain the
analytic all-center row bound

```text
||A_i||_(infinity->infinity) <= beta_i
 = 1/2 + 1/(20^(alpha_i^2)-1) <= 21/38 < 1.
```

PR5056's staged invariant gives `||Etilde_i z||<=beta_i ||z||` for each
admitted computed input. Thus starting with `||z_0||<=1/2`, all actual
inputs remain in the unit disk required for (3)–(5), without an accumulated
additive norm allowance.

For `z_(i+1)=Etilde_i z_i`, `y_(i+1)=A_i y_i`, and
`e_i=||z_i-y_i||`, evaluate the local defect at `z_i`:

```text
e_(i+1) <= ||Etilde_i z_i - A_i z_i|| + ||A_i(z_i-y_i)||
        <= delta_i + beta_i e_i.
```

For every finite `D>=1` and every positive complete-row multiplicity,

```text
e_D <= e_0 product_(j=0..D-1) beta_j
       + sum_(i=0..D-1) delta_i product_(j=i+1..D-1) beta_j.  (6)
```

The empty product is one. This allows nonuniform axis defects, block sizes
and parameters. For the actual common-p production policy, each
`delta_i<(sqrt(2)+2^-11)2^-p`, so (6) implies both the source's coarse
`D p^2 2^-p` allowance when `e_0=0` and the stronger retained-contraction
sum. For example, with `beta=21/38`, that sum is strictly below
`(sqrt(2)+2^-11)2^-p (1-beta^D)/(1-beta)`.

One may use (6) with differing precision budgets only when each next
computed input satisfies its stated p-grid interface. An extra precision
conversion contributes its own defect and norm admission; it is not supplied
for free by this formula. The physical Tensor under audit uses common `p`.
We never compare two rounded calls or assume a rounded map is nonexpansive:
even inward integer rounding sends `0.99` to zero and `1` to one.

Exact later restoration by `2^gamma` multiplies the error reaching that
restoration by `2^gamma`; it introduces no new rounding but removes no
earlier defect. Here `gamma=sum_i(2alpha_i^2+j_i+1)` in the retained Tensor.
The expansion error in (6) still needs transport through the actual chirp
and compression and addition of their defects before applying that scale.
This note supplies the expansion handoff, not the complete restored Fourier
or CRT integer-recovery guarantee.

## Evidence, attribution, and limits

Finite evidence distinguishes exact stored-page arithmetic from production
Gaussian accuracy. The reduced p48/P80 catalogue can test every term in (1),
signed residual bounds, crop/axis composition and actual-owner output. It
cannot validate (4) or a production Fourier error bound. Separate small
arithmetic cases can distinguish omission of each residual; they are not
claimed as production Gaussian pages. The receipt records the exact cases
actually run. The quantified argument above does not follow from sampling.

Credit Jose Manuel (`jmbarrancoml`) for the physical expansion/Tensor and
its original accuracy proposition; JoyboyBrian/#5056 for the internal norm
audit and this handoff; Dugongue for Gaussian row bounds; Hanson Sun/#1243
and Artus Krohn-Grimberghe/#371 for the coefficient/final-grid accounting
lineage; and the retained Chafik Boukhalfa, RaD/hipotures, word, Gaussian,
chirp and manuscript contributors. Sources and notices remain unchanged.
Prepared by Hiroki KUMAZAKI (@kumagi), with substantial OpenAI Codex
assistance, under Apache-2.0. No independent human or proof-kernel acceptance
is claimed. Primitive, interval, native, physical cost, chirp, compression,
full supplier and selected-frontier obligations remain outside this audit.
